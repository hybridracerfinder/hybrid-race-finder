#!/usr/bin/env python3
"""Daily update of the race database (data/races.json + data/races.js).

Run by GitHub Actions (.github/workflows/update.yml), or by hand:
    pip install requests beautifulsoup4
    python tools/update_races.py

What it does
  1. Reads the current database (data/races.json), which is the source of truth.
  2. Collects the announced races from the official sites:
       HYROX  hyrox.com/find-my-race (list) + each event page (ticket sales opening soon, venue)
       ATHX   athxgames.com/events
       DEKA   spartan.com "find a race" pages (US, UK, ES) filtered on DEKA
  3. Merges them into the database: dates, names, links and ticket status are refreshed;
     new races are added (their city is geocoded with OpenStreetMap Nominatim, results cached);
     races that disappeared from an official list are removed.
  4. Reconciles past races: a race that has taken place becomes "not announced" (expected) in its city
     unless a new edition of the same brand is already announced there; an expected race is dropped as
     soon as an edition of the same brand is announced in its city.
  5. Writes data/races.json, data/races.js and data/update_report.json.

Safety
  - If a site cannot be read, or returns far fewer races than before (layout change), that brand is left
    untouched and the problem is written to the report. The workflow then fails so GitHub e-mails you,
    but the data already on the site stays as it was.
  - Fields this script does not own (notes, tags, translations, coordinates, manual "expected" entries)
    are preserved.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
import time
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
RACES_JSON = DATA / "races.json"
RACES_JS = DATA / "races.js"
GEOCACHE = DATA / "geocache.json"
REPORT = DATA / "update_report.json"

USER_AGENT = "HybridRaceFinder/5 (personal, non-commercial race map; updates once a day)"
DELAY = 1.5           # seconds between two requests to the same site
MIN_RATIO = 0.6       # a source returning < 60 % of the previous number of upcoming races is treated as broken

BRAND_LABEL = {"hyrox": "HYROX", "athx": "ATHX", "deka": "DEKA"}
BRAND_PAGE = {
    "hyrox": "https://hyrox.com/find-my-race/",
    "athx": "https://athxgames.com/events",
    "deka": "https://www.spartan.com/en/deka",
}
ONE_OFF_TAGS = {"championnat-du-monde", "championnat", "finale"}
AUTO_TICKET_INFO = {
    "fr": "Ouverture de la billetterie prochainement (liste d'attente)",
    "en": "Ticket sales opening soon (waitlist)",
    "de": "Ticketverkauf startet bald (Warteliste)",
}

MONTHS = {m: i + 1 for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"])}
MONTHS.update({"sept": 9, "june": 6, "july": 7, "mai": 5, "okt": 10, "dez": 12, "mär": 3, "mrz": 3})

# Country (ISO code) -> continent used by the filters
CONTINENT = {}
for cc in ("AT BE BG CH CY CZ DE DK EE ES FI FR GB GR HR HU IE IS IT LT LU LV MT NL NO PL PT RO RS SE SI SK TR UA AD MC").split():
    CONTINENT[cc] = "europe"
for cc in ("US CA MX GT CR PA DO PR JM BS".split()):
    CONTINENT[cc] = "north-america"
for cc in ("BR AR CL CO PE UY EC VE BO PY".split()):
    CONTINENT[cc] = "south-america"
for cc in ("AU NZ CN HK JP KR TW SG MY TH VN ID PH IN AE SA QA KW BH OM IL JO LB".split()):
    CONTINENT[cc] = "asia-pacific"
for cc in ("ZA EG MA TN KE NG GH MU NA".split()):
    CONTINENT[cc] = "africa"

COUNTRY_EN = {  # names as written on the official sites -> ISO code
    "united states": "US", "usa": "US", "united kingdom": "GB", "uk": "GB", "great britain": "GB",
    "netherlands": "NL", "the netherlands": "NL", "portugal": "PT", "france": "FR", "spain": "ES",
    "italy": "IT", "belgium": "BE", "switzerland": "CH", "germany": "DE", "austria": "AT", "ireland": "IE",
    "sweden": "SE", "denmark": "DK", "norway": "NO", "finland": "FI", "poland": "PL", "canada": "CA",
    "mexico": "MX", "australia": "AU", "new zealand": "NZ", "united arab emirates": "AE", "uae": "AE",
    "south africa": "ZA", "brazil": "BR", "argentina": "AR", "japan": "JP", "south korea": "KR",
    "china": "CN", "hong kong": "HK", "singapore": "SG", "thailand": "TH", "malaysia": "MY",
    "india": "IN", "egypt": "EG", "greece": "GR", "hungary": "HU", "latvia": "LV", "turkey": "TR",
    "türkiye": "TR", "czech republic": "CZ", "czechia": "CZ",
}

# ---------------------------------------------------------------- helpers

def today_iso() -> str:
    return dt.date.today().isoformat()


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "", s)


def norm_url(u: str) -> str:
    u = (u or "").strip().split("#")[0].split("?")[0]
    u = re.sub(r"^https?://(www\.)?", "", u)
    return u.rstrip("/").lower()


def iso(y: int, m: int, d: int) -> str:
    return dt.date(y, m, d).isoformat()


def month_num(name: str) -> int | None:
    return MONTHS.get(name.strip(". ").lower()[:3]) or MONTHS.get(name.strip(". ").lower())


class Http:
    """Polite HTTP client: one request every DELAY seconds per host, a few retries."""

    def __init__(self):
        import requests  # imported here so the pure functions can be tested without it
        self.requests = requests
        self.s = requests.Session()
        self.s.headers["User-Agent"] = USER_AGENT
        self.s.headers["Accept-Language"] = "en"
        self.last = {}

    def get(self, url: str, **kw):
        host = re.sub(r"^https?://([^/]+).*", r"\1", url)
        wait = DELAY - (time.time() - self.last.get(host, 0))
        if wait > 0:
            time.sleep(wait)
        err = None
        for attempt in range(3):
            try:
                r = self.s.get(url, timeout=30, **kw)
                self.last[host] = time.time()
                if r.status_code == 200:
                    return r
                err = f"HTTP {r.status_code}"
            except self.requests.RequestException as e:  # network error
                err = str(e)
            time.sleep(3 * (attempt + 1))
        raise RuntimeError(f"{url}: {err}")


def soup_of(html: str):
    from bs4 import BeautifulSoup
    return BeautifulSoup(html, "html.parser")


def event_segments(soup, link_re, url_of):
    """Split the page into one text segment per event, in document order.

    Everything between the first link to an event and the first link to the next event belongs to that
    event (title, dates, venue, the "Buy tickets" / "Enter now" button...). This does not depend on how
    the site nests its HTML, which is what broke the first version (the button sat in another block
    than the date and was missed).
    Returns {key: {"url": ..., "titles": [anchor texts], "text": "..."}} in page order."""
    from bs4 import NavigableString, Tag
    segs, current = {}, None
    for node in soup.descendants:
        if isinstance(node, Tag) and node.name == "a" and node.get("href"):
            href = node["href"].split("?")[0].split("#")[0]
            if link_re.search(href):
                url = url_of(href)
                current = norm_url(url)
                seg = segs.setdefault(current, {"url": url, "titles": [], "text": []})
                t = node.get_text(" ", strip=True)
                if t:
                    seg["titles"].append(t)
        elif isinstance(node, NavigableString) and current and node.parent.name not in ("script", "style"):
            t = str(node).strip()
            if t:
                segs[current]["text"].append(t)
    for seg in segs.values():
        seg["text"] = " ".join(seg["text"])
    return segs


# ---------------------------------------------------------------- date parsers (one per site format)

def parse_hyrox_dates(text: str):
    """'15. Oct. 2026– 18. Oct. 2026', '17. Oct. 2026', 'Date coming soon!'"""
    found = re.findall(r"(\d{1,2})\.\s*([A-Za-zäé]{3,5})\.?\s*(\d{4})", text)
    dates = []
    for d, m, y in found:
        mn = month_num(m)
        if mn:
            dates.append(iso(int(y), mn, int(d)))
    if not dates:
        return None, None
    return dates[0], dates[1] if len(dates) > 1 else dates[0]


def parse_athx_dates(text: str):
    """'17 Oct 2026', '23 - 24 Jan 2027', '31 Jan - 01 Feb 2026', '27 - 29 Nov 2026'"""
    m = re.search(r"(\d{1,2})(?:\s+([A-Za-z]{3}))?(?:\s+(\d{4}))?\s*[-–]\s*(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})", text)
    if m:
        d1, m1, y1, d2, m2, y2 = m.groups()
        mo2, yr2 = month_num(m2), int(y2)
        mo1 = month_num(m1) if m1 else mo2
        yr1 = int(y1) if y1 else (yr2 - 1 if mo1 > mo2 else yr2)
        if mo1 and mo2:
            return iso(yr1, mo1, int(d1)), iso(yr2, mo2, int(d2))
    m = re.search(r"(\d{1,2})\s+([A-Za-z]{3})[a-z]*\s+(\d{4})", text)
    if m and month_num(m.group(2)):
        d = iso(int(m.group(3)), month_num(m.group(2)), int(m.group(1)))
        return d, d
    return None, None


def parse_deka_dates(text: str):
    """'Nov 07 - 08, 2026', 'Oct 31 - 01, 2026' (next month), 'Mar 27, 2027', 'Dec 30 - Jan 02, 2027'"""
    m = re.search(r"\b([A-Z][a-z]{2})\s+(\d{1,2})(?:\s*[-–]\s*(?:([A-Z][a-z]{2})\s+)?(\d{1,2}))?,\s*(\d{4})", text)
    if not m:
        return None, None
    m1, d1, m2, d2, y = m.groups()
    mo1 = month_num(m1)
    if not mo1:
        return None, None
    y = int(y)
    start = dt.date(y, mo1, int(d1))
    if not d2:
        return start.isoformat(), start.isoformat()
    mo2 = month_num(m2) if m2 else mo1
    if not m2 and int(d2) < int(d1):  # 'Oct 31 - 01' -> 1 November
        mo2 = mo1 % 12 + 1
    y2 = y + 1 if mo2 < mo1 else y
    if m2 and mo2 < mo1:  # 'Dec 30 - Jan 02, 2027': the year belongs to the end date
        start = dt.date(y - 1, mo1, int(d1))
        y2 = y
    return start.isoformat(), dt.date(y2, mo2, int(d2)).isoformat()


# ---------------------------------------------------------------- city names from event names

def hyrox_city(name: str) -> str:
    s = re.split(r"\bHYROX\b", name, flags=re.I)[-1]
    s = re.sub(r"\b(youngstars|world championships?|elite 15)\b", " ", s, flags=re.I)
    s = re.sub(r"[|\d]+", " ", s)
    return re.sub(r"\s+", " ", s).strip(" -–").title()


def athx_city(name: str) -> str:
    s = re.sub(r"^\s*ATHX\s+", "", name, flags=re.I)
    s = re.sub(r"\b(19|20)\d{2}\b", "", s)
    return re.sub(r"\s+", " ", s).strip(" -–").title()


def deka_city(name: str) -> str:
    if " - " in name:
        s = name.split(" - ")[-1]
        s = re.sub(r",\s*[A-Z]{2}$", "", s.strip())
    else:
        s = re.sub(r"\bDEKA\b|\b(FIT|MILE|STRONG|ULTRA)\b|&|\b(19|20)\d{2}\b", " ", name, flags=re.I)
        s = re.sub(r"\(.*?\)", " ", s)
    s = re.sub(r"\b(primavera|oto[nñ]o|spring|autumn|fall|trifecta weekend)\b", " ", s, flags=re.I)
    return re.sub(r"\s+", " ", s).strip(" -–").title()


# ---------------------------------------------------------------- scrapers
# Each returns a list of dicts: brand, url, name, start, end, date_confirmed, listing_cta (+ optional extras)

# Only explicit wording. "Athlete Ticket Notification List" and "waitlist" also appear on pages whose
# ticket sales are open, so they must not be used (this made every HYROX race blue in the first run).
SOON_RE = re.compile(r"ticket sales (?:will )?open soon|tickets? (?:will )?go(?:es)? (?:on sale|live) soon|"
                     r"registration (?:will )?opens? soon|sales open soon", re.I)


def scrape_hyrox(http: Http, check_event_pages=True, log=print):
    html = http.get(BRAND_PAGE["hyrox"]).text
    soup = soup_of(html)
    link_re = re.compile(r"hyrox\.com/event/[^/]+/?$|^/event/[^/]+/?$")
    segs = event_segments(soup, link_re, lambda h: (h if h.startswith("http") else "https://hyrox.com" + h))
    out = []
    for key, seg in segs.items():
        titles = [t for t in seg["titles"] if t.lower() not in ("buy tickets", "find out more")]
        if not titles:
            continue
        text = seg["text"]
        start, end = parse_hyrox_dates(text)
        out.append({
            "brand": "hyrox", "url": seg["url"].rstrip("/") + "/", "name": titles[0],
            "start": start, "end": end, "date_confirmed": start is not None,
            "listing_cta": "buy_tickets" if re.search(r"\bbuy tickets?\b", text, re.I) else "find_out_more",
            "slug": key.split("/")[-1],
        })
    if check_event_pages:
        for r in out:
            if r["start"] and r["end"] < today_iso():
                continue
            try:
                page = soup_of(http.get(r["url"]).text).get_text("\n", strip=True)
            except RuntimeError as e:
                log(f"  ! {r['url']}: {e}")
                continue
            r["_page_checked"] = True
            r["_soon"] = bool(SOON_RE.search(page))
            m = re.search(r"Event Location:\s*([^\n]{3,120})", page)
            if m:
                r["venue"] = m.group(1).strip()
    return out


def hyrox_meta(http: Http, slug: str):
    """Continent and adults/youngstars of a new HYROX event, from the WordPress API."""
    r = http.get("https://hyrox.com/wp-json/wp/v2/event", params={"slug": slug, "_fields": "slug,class_list"})
    items = r.json()
    classes = items[0].get("class_list", []) if items else []
    cont = next((c[len("continent-"):] for c in classes if c.startswith("continent-")), None)
    typ = "youngstars" if "type-youngstars" in classes else "adults"
    return cont, typ


def scrape_athx(http: Http, log=print):
    soup = soup_of(http.get(BRAND_PAGE["athx"]).text)
    link_re = re.compile(r"/events/[0-9a-z]{20,}$")
    segs = event_segments(soup, link_re, lambda h: (h if h.startswith("http") else "https://athxgames.com" + h))
    out = []
    for key, seg in segs.items():
        text = " ".join(seg["titles"]) + " " + seg["text"]
        m = re.search(r"\bATHX\s+[A-ZÀ-Ü][A-ZÀ-Ü .'\-]*?\s+(19|20)\d{2}\b", text, flags=re.I)
        if not m:
            continue
        start, end = parse_athx_dates(text)
        country = next((cc for name, cc in sorted(COUNTRY_EN.items(), key=lambda x: -len(x[0]))
                        if re.search(rf"\b{re.escape(name)}\b", text, flags=re.I)), None)
        out.append({
            "brand": "athx", "url": seg["url"], "name": m.group(0).strip().title().replace("Athx", "ATHX"),
            "start": start, "end": end, "date_confirmed": start is not None,
            "listing_cta": "buy_tickets" if re.search(r"enter now|register now|buy tickets?", text, re.I) else "find_out_more",
            "_cc": country,
        })
    return out


DEKA_PAGES = [
    ("https://www.spartan.com/en/race/find-race?race_type=DEKA", "US"),
    ("https://uk.spartan.com/en/race/find-race?race_type=DEKA", "GB"),
    ("https://es.spartan.com/en/race/find-race?race_type=DEKA", "ES"),
]


def scrape_deka(http: Http, log=print):
    out, seen, errors = [], set(), []
    link_re = re.compile(r"spartan\.com/[a-z]{2}/race/detail/\d+|spartan\.com/[a-z]{2}/races/[\w-]+|^/[a-z]{2}/race/detail/\d+|^/[a-z]{2}/races/[\w-]+")
    for page, cc in DEKA_PAGES:
        try:
            soup = soup_of(http.get(page).text)
        except RuntimeError as e:
            errors.append(str(e))
            continue
        base = re.match(r"https://[^/]+", page).group(0)
        segs = event_segments(soup, link_re, lambda h, base=base: (h if h.startswith("http") else base + h))
        for key, seg in segs.items():
            if key in seen:
                continue
            text = " ".join(seg["titles"]) + " " + seg["text"]
            # The DEKA filter page also lists Spartan obstacle races, whose description may mention DEKA.
            # Keep an event only if DEKA is in its own title: the text of its links, or, when its links have
            # no text (image only), the first words of its block.
            titles = [t for t in seg["titles"] if len(t) > 3 and not re.fullmatch(r"(register|sign up|book|more info|learn more)", t, re.I)]
            title = max(titles, key=len) if titles else seg["text"][:90]
            if not re.search(r"\bDEKA\b", title, re.I):
                continue
            start, end = parse_deka_dates(text)
            if not start:
                continue
            seen.add(key)
            name = title if re.search(r"\bDEKA\b", title, re.I) else None
            if not name:
                m = re.search(r"((?:19|20)\d{2}\s+)?[^|]*?DEKA[^|]*?(?=\s+[A-Z][a-z]{2}\s+\d{1,2}|$)", text)
                name = m.group(0).strip() if m else text[:80]
            out.append({
                "brand": "deka", "url": seg["url"], "name": re.sub(r"\s+", " ", name)[:90],
                "start": start, "end": end, "date_confirmed": True,
                "listing_cta": "find_out_more" if re.search(r"sold out|coming soon", text, re.I)
                               else ("buy_tickets" if re.search(r"register|sign up|book", text, re.I) else "find_out_more"),
                "_cc": cc,
            })
    if errors and not out:
        raise RuntimeError("; ".join(errors))
    return out


# ---------------------------------------------------------------- geocoding (new cities only)

class Geocoder:
    def __init__(self, http: Http | None):
        self.http = http
        try:
            self.cache = json.loads(GEOCACHE.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            self.cache = {}

    def save(self):
        GEOCACHE.write_text(json.dumps(self.cache, ensure_ascii=False, indent=1), encoding="utf-8")

    def lookup(self, city: str, cc: str | None):
        q = f"{city}|{cc or ''}"
        if q in self.cache:
            return self.cache[q]
        if not self.http:
            return None
        params = {"q": city, "format": "jsonv2", "limit": 1, "namedetails": 1, "addressdetails": 1,
                  "accept-language": "en"}
        if cc:
            params["countrycodes"] = cc.lower()
        try:
            res = self.http.get("https://nominatim.openstreetmap.org/search", params=params).json()
        except (RuntimeError, ValueError):
            return None
        if not res:
            self.cache[q] = None
            return None
        h = res[0]
        nd = h.get("namedetails") or {}
        en = nd.get("name:en") or h.get("name") or city
        found_cc = (h.get("address", {}).get("country_code") or cc or "").upper()
        val = {
            "city": {"fr": nd.get("name:fr") or en, "en": en, "de": nd.get("name:de") or en},
            "cc": found_cc, "lat": round(float(h["lat"]), 4), "lng": round(float(h["lon"]), 4),
            "continent": CONTINENT.get(found_cc),
        }
        self.cache[q] = val
        return val


def city_index(races):
    """Known cities (from the current database), by normalised name in fr / en / de."""
    idx = {}
    for r in races:
        rec = {"city": r["city"], "cc": r["cc"], "lat": r["lat"], "lng": r["lng"], "continent": r["continent"]}
        for name in r["city"].values():
            idx.setdefault(norm(name), []).append(rec)
    return idx


def resolve_city(name_city: str, cc: str | None, idx, geo: Geocoder):
    cands = idx.get(norm(name_city), [])
    if cc:
        cands = [c for c in cands if c["cc"] == cc] or ([] if cands else cands)
    uniq = {(c["cc"], c["city"]["fr"]): c for c in cands}
    if len(uniq) == 1:
        return next(iter(uniq.values()))
    return geo.lookup(name_city, cc)


# ---------------------------------------------------------------- merge + reconcile (pure functions, tested)

OWNED = ("name", "start", "end", "date_confirmed", "listing_cta", "url")


def on_sale(r):
    return r.get("listing_cta") == "buy_tickets" and not r.get("ticket_info")


def ticket_status_collapsed(prev, scraped):
    """True when the number of races on sale drops implausibly (the ticket button was not found)."""
    before = sum(1 for r in prev if on_sale(r))
    after = sum(1 for s in scraped if s.get("listing_cta") == "buy_tickets" and not s.get("_soon"))
    return before >= 10 and after < 0.3 * before


def merge_brand(races, brand, scraped, today, resolve, meta_lookup=None, log=print, keep_ticket_status=False):
    """Merge the races scraped for one brand into `races` (list, modified in place).
    With keep_ticket_status=True, the ticket status of known races is left as it was.
    Returns (added, updated, removed, skipped) lists of names."""
    prev = [r for r in races if r["brand"] == brand and r["status"] == "announced"]
    by_url = {norm_url(r["url"]): r for r in prev}
    added, updated, skipped = [], [], []
    seen = set()
    for s in scraped:
        key = norm_url(s["url"])
        seen.add(key)
        r = by_url.get(key)
        if r is None and brand == "hyrox":
            r = next((x for x in prev if x["id"] == s.get("slug")), None)
        if r is not None:
            before = {k: r.get(k) for k in OWNED + ("ticket_info",)}
            for k in OWNED:
                if keep_ticket_status and k == "listing_cta":
                    continue
                if s.get(k) is not None or k in ("start", "end"):
                    r[k] = s.get(k)
            if s.get("_page_checked") and not keep_ticket_status:
                if s.get("_soon"):
                    r["ticket_info"] = AUTO_TICKET_INFO
                else:
                    r.pop("ticket_info", None)
            if s.get("venue") and not r.get("venue"):
                r["venue"] = s["venue"]
            if before != {k: r.get(k) for k in OWNED + ("ticket_info",)}:
                updated.append(r["name"])
            continue
        # new race
        if s["start"] and s["end"] < today:
            continue
        city_name = {"hyrox": hyrox_city, "athx": athx_city, "deka": deka_city}[brand](s["name"])
        cont = typ = None
        if brand == "hyrox" and meta_lookup:
            try:
                cont, typ = meta_lookup(s["slug"])
            except Exception as e:  # noqa: BLE001 - the API is optional
                log(f"  ! HYROX API {s['slug']}: {e}")
        place = resolve(city_name, s.get("_cc")) if city_name else None
        if not place:
            skipped.append(f"{s['name']} ({s['url']})")
            continue
        new = {
            "id": s.get("slug") if brand == "hyrox" else f"{brand}-" + re.sub(r"[^a-z0-9]+", "-", key.split("/")[-1]),
            "name": s["name"], "brand": brand, "city": place["city"], "cc": place["cc"],
            "continent": cont or place.get("continent") or "europe", "type": typ or "adults",
            "start": s["start"], "end": s["end"], "date_confirmed": s["date_confirmed"], "status": "announced",
            "listing_cta": s["listing_cta"], "url": s["url"], "lat": place["lat"], "lng": place["lng"],
        }
        if s.get("venue"):
            new["venue"] = s["venue"]
        if s.get("_page_checked") and s.get("_soon"):
            new["ticket_info"] = AUTO_TICKET_INFO
        races.append(new)
        added.append(new["name"])
    removed = []
    for r in prev:
        if norm_url(r["url"]) in seen:
            continue
        upcoming = not r["date_confirmed"] or r["end"] >= today
        if upcoming:  # no longer listed -> cancelled or moved
            races.remove(r)
            removed.append(r["name"])
    return added, updated, removed, skipped


def plus_months(ym: str, n: int) -> str:
    y, m = map(int, ym.split("-"))
    m += n
    return f"{y + (m - 1) // 12}-{(m - 1) % 12 + 1:02d}"


def next_expected_month(usual, last_end: str, today: str) -> str:
    cur = today[:7]
    best = None
    for m in usual:
        for y in range(int(cur[:4]), int(cur[:4]) + 3):
            ym = f"{y}-{m:02d}"
            if ym > last_end[:7] and ym >= cur:
                best = ym if best is None or ym < best else best
                break
    return best or plus_months(last_end[:7], 12)


def reconcile(races, today):
    """Past races -> expected; expected dropped when announced. Same rule as reconcile() in assets/app.js."""
    def key(r):
        return (r["brand"], r["city"]["fr"], r["cc"])

    def upcoming(r):
        return r["status"] == "announced" and (not r["date_confirmed"] or r["end"] >= today)

    def past(r):
        return r["status"] == "announced" and r["date_confirmed"] and r["end"] < today

    upcoming_keys = {key(r) for r in races if upcoming(r) and r.get("type") != "youngstars"}
    expected, changes = {}, []
    for r in races:
        if r["status"] == "expected":
            if key(r) in upcoming_keys:
                changes.append(f"announced again, removed from 'not announced': {r['name']}")
            else:
                expected[key(r)] = r
    for r in sorted(filter(past, races), key=lambda x: x["start"]):
        if r.get("type") == "youngstars" or ONE_OFF_TAGS & set(r.get("tags", [])):
            changes.append(f"finished, removed: {r['name']}")
            continue
        k = key(r)
        if k in upcoming_keys:
            changes.append(f"finished, next edition already announced: {r['name']}")
            continue
        month = int(r["start"][5:7])
        last = {"start": r["start"], "end": r["end"], "venue": r.get("venue")}
        e = expected.get(k)
        if e:
            e["usual_months"] = sorted(set(e.get("usual_months", [])) | {month})
            if not e.get("last_edition") or r["start"] > e["last_edition"]["start"]:
                e["last_edition"] = last
            changes.append(f"finished, merged into 'not announced': {r['name']}")
        else:
            expected[k] = {
                "id": "expected-" + re.sub(r"[^a-z0-9]+", "-", f"{r['brand']}-{r['cc']}-{r['city']['en']}".lower()),
                "name": f"{BRAND_LABEL[r['brand']]} {r['city']['fr']}", "brand": r["brand"],
                "city": r["city"], "cc": r["cc"], "continent": r["continent"], "type": "adults",
                "start": None, "end": None, "date_confirmed": False, "status": "expected",
                "usual_months": [month], "last_edition": last,
                "url": BRAND_PAGE[r["brand"]], "lat": r["lat"], "lng": r["lng"],
            }
            changes.append(f"finished, now 'not announced': {r['name']}")
    for e in expected.values():
        e["expected_month"] = next_expected_month(e["usual_months"], e["last_edition"]["end"], today)
    return [r for r in races if upcoming(r)] + list(expected.values()), changes


# ---------------------------------------------------------------- output

def write_outputs(db):
    DATA.mkdir(exist_ok=True)
    RACES_JSON.write_text(json.dumps(db, ensure_ascii=False, indent=2), encoding="utf-8")
    RACES_JS.write_text("// Generated by tools/update_races.py - do not edit by hand\n"
                        "window.RACES_DATA = " + json.dumps(db, ensure_ascii=False) + ";\n", encoding="utf-8")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only", choices=list(BRAND_LABEL), action="append", help="update only these brands")
    ap.add_argument("--skip-event-pages", action="store_true", help="HYROX: do not open each event page")
    ap.add_argument("--dry-run", action="store_true", help="print the changes, write nothing")
    args = ap.parse_args(argv)

    db = json.loads(RACES_JSON.read_text(encoding="utf-8"))
    races = db["races"]
    today = today_iso()
    http = Http()
    geo = Geocoder(http)
    idx = city_index(races)
    report = {"date": today, "brands": {}, "errors": [], "warnings": []}

    def resolve(city, cc):
        return resolve_city(city, cc, idx, geo)

    scrapers = {
        "hyrox": lambda: scrape_hyrox(http, check_event_pages=not args.skip_event_pages),
        "athx": lambda: scrape_athx(http),
        "deka": lambda: scrape_deka(http),
    }
    any_ok = False
    for brand in args.only or list(BRAND_LABEL):
        print(f"== {BRAND_LABEL[brand]}")
        prev_upcoming = [r for r in races if r["brand"] == brand and r["status"] == "announced"
                         and (not r["date_confirmed"] or r["end"] >= today)]
        try:
            scraped = scrapers[brand]()
        except Exception as e:  # noqa: BLE001
            msg = f"{BRAND_LABEL[brand]}: site unreadable ({e}); data left unchanged"
            print("  ! " + msg)
            report["errors"].append(msg)
            report["brands"][brand] = {"ok": False}
            continue
        upcoming_scraped = [s for s in scraped if not s["start"] or s["end"] >= today]
        if len(prev_upcoming) >= 5 and len(upcoming_scraped) < MIN_RATIO * len(prev_upcoming):
            msg = (f"{BRAND_LABEL[brand]}: only {len(upcoming_scraped)} races found instead of about "
                   f"{len(prev_upcoming)} (the site layout has probably changed); data left unchanged")
            print("  ! " + msg)
            report["errors"].append(msg)
            report["brands"][brand] = {"ok": False, "found": len(upcoming_scraped)}
            continue
        meta = (lambda slug: hyrox_meta(http, slug)) if brand == "hyrox" else None
        prev_announced = [r for r in races if r["brand"] == brand and r["status"] == "announced"]
        keep = ticket_status_collapsed(prev_announced, scraped)
        if keep:
            msg = (f"{BRAND_LABEL[brand]}: almost no race found on sale (was {sum(map(on_sale, prev_announced))}); "
                   "the ticket button was probably not recognised, ticket status left unchanged")
            print("  ! " + msg)
            report["errors"].append(msg)
        added, updated, removed, skipped = merge_brand(races, brand, scraped, today, resolve, meta,
                                                       keep_ticket_status=keep)
        any_ok = True
        report["brands"][brand] = {"ok": True, "found": len(upcoming_scraped), "added": added,
                                   "updated": updated, "removed": removed, "skipped": skipped}
        db.setdefault("meta", {}).setdefault("sources", {})[brand] = {"checked_on": today, "races": len(upcoming_scraped)}
        print(f"  {len(upcoming_scraped)} races · +{len(added)} · ~{len(updated)} · -{len(removed)}"
              + (f" · {len(skipped)} new races skipped (city not found)" if skipped else ""))
        for s in skipped:
            report.setdefault("warnings", []).append(f"{BRAND_LABEL[brand]}: new race not added, city not found: {s}")

    races, changes = reconcile(races, today)
    report["reconcile"] = changes
    for c in changes:
        print("  · " + c)
    db["races"] = races
    db.setdefault("meta", {})
    db["meta"]["count"] = len(races)
    db["meta"]["generator"] = "update_races"
    if any_ok:
        db["meta"]["updated_at"] = today
    geo.save()
    if args.dry_run:
        print(json.dumps(report, ensure_ascii=False, indent=1))
        return 0
    write_outputs(db)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Done: {len(races)} races, {len(report['errors'])} problem(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
