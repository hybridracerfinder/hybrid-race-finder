"""Tests for tools/update_races.py (no network needed).
Run:  python -m pytest tests/   or   python tests/test_update.py
"""
import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import update_races as u  # noqa: E402


# ------------------------------------------------------------ date formats of the three sites

def test_dates():
    assert u.parse_hyrox_dates("15. Oct. 2026– 18. Oct. 2026 Buy Tickets") == ("2026-10-15", "2026-10-18")
    assert u.parse_hyrox_dates("7. May. 2027– 9. May. 2027") == ("2027-05-07", "2027-05-09")
    assert u.parse_hyrox_dates("17. Oct. 2026") == ("2026-10-17", "2026-10-17")
    assert u.parse_hyrox_dates("Date coming soon!") == (None, None)
    assert u.parse_athx_dates("ATHX LONDON 2027 23 - 24 Jan 2027 Excel") == ("2027-01-23", "2027-01-24")
    assert u.parse_athx_dates("31 Jan - 01 Feb 2026") == ("2026-01-31", "2026-02-01")
    assert u.parse_athx_dates("ATHX HOUSTON 2026 17 Oct 2026 Reliant Park") == ("2026-10-17", "2026-10-17")
    assert u.parse_athx_dates("27 - 29 Nov 2026") == ("2026-11-27", "2026-11-29")
    assert u.parse_deka_dates("Nov 07 - 08, 2026") == ("2026-11-07", "2026-11-08")
    assert u.parse_deka_dates("Oct 31 - 01, 2026") == ("2026-10-31", "2026-11-01")
    assert u.parse_deka_dates("Mar 27, 2027") == ("2027-03-27", "2027-03-27")
    assert u.parse_deka_dates("Dec 30 - Jan 02, 2027") == ("2026-12-30", "2027-01-02")


def test_city_names():
    assert u.hyrox_city("FITNESS PARK HYROX PARIS") == "Paris"
    assert u.hyrox_city("HYROX Youngstars London ExCeL") == "London Excel"
    assert u.hyrox_city("PUMA HYROX World Championships Hong Kong") == "Hong Kong"
    assert u.athx_city("ATHX ST GALLEN 2027") == "St Gallen"
    assert u.deka_city("2027 DEKA FIT & Ultra - Sacramento, CA") == "Sacramento"
    assert u.deka_city("DEKA VIGO 2027") == "Vigo"
    assert u.deka_city("DEKA TORREMOLINOS (MÁLAGA) 2027") == "Torremolinos"


# ------------------------------------------------------------ HTML parsing (pages shaped like the real ones)

class FakeHttp:
    def __init__(self, pages):
        self.pages = pages

    def get(self, url, **kw):
        class R:
            pass
        r = R()
        r.text = self.pages[url]
        r.json = lambda: json.loads(r.text)
        return r


HYROX_LIST = """
<div class="event"><a href="https://hyrox.com/event/hyrox-toulouse-s26-27/"><img src="x.jpg"></a><span>TLS</span>
<h2><a href="https://hyrox.com/event/hyrox-toulouse-s26-27/">LUCIS HYROX TOULOUSE</a></h2>
<p>3. Feb. 2027– 7. Feb. 2027</p><a href="https://hyrox.com/event/hyrox-toulouse-s26-27/">Buy Tickets</a></div>
<div class="event"><span>NYC</span><h2><a href="https://hyrox.com/event/hyrox-new-york/">HYROX New York</a></h2>
<p>Date coming soon!</p><a href="https://hyrox.com/event/hyrox-new-york/">Find out more</a></div>
<div class="event"><h2><a href="https://hyrox.com/event/hyrox-strasbourg/">HYROX Strasbourg</a></h2>
<p>10. Jun. 2027– 13. Jun. 2027</p><a href="https://hyrox.com/event/hyrox-strasbourg/">Find out more</a></div>
"""


def test_scrape_hyrox():
    pages = {
        u.BRAND_PAGE["hyrox"]: HYROX_LIST,
        "https://hyrox.com/event/hyrox-toulouse-s26-27/": "<p>Buy Tickets here</p><p>Event Location: MEETT, Toulouse</p>",
        "https://hyrox.com/event/hyrox-new-york/": "<p>Coming soon</p>",
        "https://hyrox.com/event/hyrox-strasbourg/": "<p><b>Ticket sales open soon.</b> Join the waitlist</p>",
    }
    got = {r["slug"]: r for r in u.scrape_hyrox(FakeHttp(pages))}
    t = got["hyrox-toulouse-s26-27"]
    assert (t["start"], t["end"], t["listing_cta"]) == ("2027-02-03", "2027-02-07", "buy_tickets")
    assert t["_soon"] is False and t["venue"] == "MEETT, Toulouse"
    assert got["hyrox-new-york"]["date_confirmed"] is False
    assert got["hyrox-strasbourg"]["_soon"] is True


ATHX_LIST = """
<a href="/events/01krwxxbqkjzzbhpdj52356qkc"><div><h3>ATHX LONDON 2027</h3><p>23 - 24 Jan 2027</p>
<p>Excel London</p><p>United Kingdom</p><span>Enter now</span></div></a>
<a href="/events/01km0bfarc0dcs952s4rmtgd47"><div><h3>ATHX HOUSTON 2026</h3><p>17 Oct 2026</p><p>Reliant Park</p>
<p>United States</p></div></a>
"""


def test_scrape_athx():
    got = u.scrape_athx(FakeHttp({u.BRAND_PAGE["athx"]: ATHX_LIST}))
    assert [(r["name"], r["start"], r["listing_cta"], r["_cc"]) for r in got] == [
        ("ATHX London 2027", "2027-01-23", "buy_tickets", "GB"),
        ("ATHX Houston 2026", "2026-10-17", "find_out_more", "US"),
    ]


DEKA_LIST = """
<div class="card"><a href="/en/race/detail/10979/overview">2026 DEKA FIT &amp; Ultra - Atlanta</a>
<p>Atlanta, GA</p><p>Nov 07 - 08, 2026</p><a href="/en/race/detail/10979/overview">Register</a></div>
<div class="card"><a href="/en/race/detail/11111/overview">Spartan Sprint Boston</a><p>Nov 01, 2026</p></div>
"""


def test_scrape_deka():
    pages = {p: "<html></html>" for p, _ in u.DEKA_PAGES}
    pages[u.DEKA_PAGES[0][0]] = DEKA_LIST
    got = u.scrape_deka(FakeHttp(pages))
    assert len(got) == 1  # the Spartan race is ignored
    assert got[0]["url"] == "https://www.spartan.com/en/race/detail/10979/overview"
    assert (got[0]["start"], got[0]["end"], got[0]["listing_cta"]) == ("2026-11-07", "2026-11-08", "buy_tickets")


# ------------------------------------------------------------ merge + reconcile on the real database

def db():
    return copy.deepcopy(json.loads((ROOT / "data/races.json").read_text(encoding="utf-8"))["races"])


def find(races, rid):
    return next((r for r in races if r["id"] == rid), None)


def status(r):
    """Same rule as statusOf() in assets/app.js -> marker colour."""
    if r["status"] == "expected":
        return "exp (dashed)"
    if not r["date_confirmed"]:
        return "tbc (grey)"
    if r.get("ticket_info"):
        return "info (blue)"
    return "buy (yellow)" if r["listing_cta"] == "buy_tickets" else "info (blue)"


def hyrox_scraped(races, today):
    out = []
    for r in races:
        if r["brand"] == "hyrox" and r["status"] == "announced" and (not r["date_confirmed"] or r["end"] >= today):
            out.append({k: r[k] for k in ("url", "name", "start", "end", "date_confirmed", "listing_cta")}
                       | {"brand": "hyrox", "slug": r["id"], "_page_checked": True, "_soon": False})
    return out


def test_ticket_sales_open_changes_colour():
    races, today = db(), "2026-10-18"
    tls = find(races, "hyrox-toulouse-s26-27")
    assert status(tls) == "info (blue)"            # 'opening soon' today
    scraped = hyrox_scraped(races, today)          # next day: page no longer says 'open soon'
    u.merge_brand(races, "hyrox", scraped, today, resolve=lambda c, cc: None)
    assert status(find(races, "hyrox-toulouse-s26-27")) == "buy (yellow)"


def test_find_out_more_becomes_buy():
    races, today = db(), "2026-10-18"
    rot = find(races, "hyrox-rotterdam")
    assert status(rot) == "info (blue)"
    scraped = hyrox_scraped(races, today)
    next(s for s in scraped if s["slug"] == "hyrox-rotterdam")["listing_cta"] = "buy_tickets"
    u.merge_brand(races, "hyrox", scraped, today, resolve=lambda c, cc: None)
    assert status(find(races, "hyrox-rotterdam")) == "buy (yellow)"


def test_expected_city_gets_announced():
    races, today = db(), "2026-10-18"
    assert find(races, "expected-berlin")
    scraped = hyrox_scraped(races, today) + [{
        "brand": "hyrox", "url": "https://hyrox.com/event/hyrox-berlin-27/", "name": "HYROX Berlin", "slug": "hyrox-berlin-27",
        "start": "2027-05-20", "end": "2027-05-30", "date_confirmed": True, "listing_cta": "find_out_more"}]
    idx = u.city_index(races)
    added, *_ = u.merge_brand(races, "hyrox", scraped, today,
                              resolve=lambda c, cc: u.resolve_city(c, cc, idx, u.Geocoder(None)))
    assert added == ["HYROX Berlin"]
    races, _ = u.reconcile(races, today)
    assert find(races, "expected-berlin") is None          # no longer 'not announced'
    berlin = find(races, "hyrox-berlin-27")
    assert berlin["city"]["de"] == "Berlin" and status(berlin) == "info (blue)"


def test_past_race_becomes_expected():
    races = db()
    races, changes = u.reconcile(races, "2027-02-08")       # HYROX Toulouse ended on 7 Feb 2027
    assert find(races, "hyrox-toulouse-s26-27") is None
    exp = next(r for r in races if r["status"] == "expected" and r["brand"] == "hyrox" and r["city"]["fr"] == "Toulouse")
    assert exp["last_edition"]["start"] == "2027-02-03" and exp["usual_months"] == [2]
    assert exp["expected_month"] == "2028-02" and status(exp) == "exp (dashed)"
    # Youngstars Toulouse (6-7 Feb) is not turned into a 'not announced' entry
    assert not any(r["status"] == "expected" and "Youngstars" in r["name"] for r in races)


def test_past_race_with_next_edition_announced():
    races = db()
    races, _ = u.reconcile(races, "2026-12-21")            # Helsinki Dec 2026 over, Helsinki Apr 2027 announced
    hel = [r for r in races if r["brand"] == "hyrox" and r["city"]["fr"] == "Helsinki"]
    assert [r["id"] for r in hel] == ["hyrox-helsinki"]


def test_past_race_merges_into_existing_expected():
    races = db()
    # ATHX Berlin 2027 (14-15 Aug) is announced; HYROX Berlin is 'not announced' -> different brands, both kept
    races, _ = u.reconcile(races, "2027-08-16")
    athx = next(r for r in races if r["brand"] == "athx" and r["city"]["fr"] == "Berlin")
    hyrox = next(r for r in races if r["brand"] == "hyrox" and r["city"]["fr"] == "Berlin")
    assert athx["status"] == "expected" and athx["expected_month"] == "2028-08"
    assert hyrox["status"] == "expected"


def test_championships_are_not_reconducted():
    races, _ = u.reconcile(db(), "2026-12-14")             # DEKA World Championship Fort Worth over
    assert not any(r["city"]["fr"] == "Fort Worth" for r in races)


def test_source_removal_and_safety():
    races, today = db(), "2026-10-18"
    scraped = hyrox_scraped(races, today)
    scraped = [s for s in scraped if s["slug"] != "hyrox-bari"]
    _, _, removed, _ = u.merge_brand(races, "hyrox", scraped, today, resolve=lambda c, cc: None)
    assert removed == ["HYROX Bari"]


if __name__ == "__main__":
    fails = 0
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print("ok  ", name)
            except AssertionError as e:
                fails += 1
                import traceback
                print("FAIL", name)
                traceback.print_exc()
    sys.exit(1 if fails else 0)
