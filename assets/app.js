/* Race Finder v3 — carte des courses Hyrox (non officiel)
 * Données : data/races.js (window.RACES_DATA), généré par tools/build_races.py
 * Textes  : assets/i18n.js (window.I18N)
 */
(function () {
  "use strict";

  const LANGS = ["fr", "en", "de"];
  const CONTINENTS = ["europe", "north-america", "south-america", "asia-pacific", "africa"];
  const BRANDS = ["hyrox", "athx", "deka"];
  const BRAND_LABEL = { hyrox: "HYROX", athx: "ATHX", deka: "DEKA" };
  const STATUS_FILTERS = ["open", "announced", "expected"];
  // Priorité des couleurs (marqueurs et regroupements) : jaune > bleu > gris > pointillé
  const RANK = { buy: 4, info: 3, tbc: 2, exp: 1 };
  const TODAY = isoDate(new Date());
  const CURRENT_MONTH = TODAY.slice(0, 7);          // "2026-10"
  const WINDOW_MONTHS = 12;                          // boutons de mois : 12 mois glissants à partir du mois en cours

  // ---------- Langue ----------
  let lang = (() => {
    try {
      const saved = localStorage.getItem("raceFinder.lang");
      if (LANGS.includes(saved)) return saved;
    } catch (e) {}
    const nav = (navigator.language || "fr").slice(0, 2).toLowerCase();
    return LANGS.includes(nav) ? nav : "en";
  })();
  const T = () => window.I18N[lang];

  // Formats de date dépendant de la langue
  let fmt = {};
  function buildFormats() {
    fmt = {
      full: new Intl.DateTimeFormat(lang, { day: "numeric", month: "short", year: "numeric" }),
      monthShort: new Intl.DateTimeFormat(lang, { month: "short" }),
      monthLong: new Intl.DateTimeFormat(lang, { month: "long" }),
      monthYear: new Intl.DateTimeFormat(lang, { month: "long", year: "numeric" }),
      list: new Intl.ListFormat(lang, { style: "long", type: "conjunction" }),
      region: new Intl.DisplayNames([lang], { type: "region" }),
    };
  }

  // ---------- État des filtres (ensemble vide = tout afficher) ----------
  const state = { continent: new Set(), month: new Set(), status: new Set(), brand: new Set() };

  // ---------- Utilitaires ----------
  function isoDate(d) {
    const z = (n) => String(n).padStart(2, "0");
    return `${d.getFullYear()}-${z(d.getMonth() + 1)}-${z(d.getDate())}`;
  }
  function parseISO(s) {
    const [y, m, d] = s.split("-").map(Number);
    return new Date(y, m - 1, d);
  }
  function esc(s) {
    return String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  }
  const noDot = (s) => s.replace(/\.$/, "");
  const tr = (v) => (v && typeof v === "object" ? v[lang] || v.en || v.fr : v); // texte multilingue de la base

  const colon = () => (lang === "fr" ? "\u00a0:" : ":"); // typographie française : espace avant « : »

  function formatRange(start, end) {
    const a = parseISO(start), b = parseISO(end);
    return start === end ? fmt.full.format(a) : fmt.full.formatRange(a, b);
  }
  function cityName(r) { return tr(r.city); }
  function countryName(r) { return r.cc === "HK" ? "Hong Kong" : fmt.region.of(r.cc); }
  function raceName(r) { return r.status === "expected" ? `${BRAND_LABEL[r.brand]} ${cityName(r)}` : r.name; }
  const brandBadge = (r) => `<span class="badge badge-brand">${BRAND_LABEL[r.brand]}</span>`;
  function cityKey(r) { return `${r.city.fr}|${r.cc}`; }

  function statusOf(r) {
    if (r.status === "expected") return "exp";
    if (!r.date_confirmed) return "tbc";
    if (r.ticket_info) return "info"; // vérifié sur la fiche : pas encore en vente
    return r.listing_cta === "buy_tickets" ? "buy" : "info";
  }
  // Catégories du filtre « Statut » auxquelles appartient une course
  function statusKeys(r) {
    if (r.status === "expected") return ["expected"];
    return r._status === "buy" ? ["announced", "open"] : ["announced"];
  }
  function monthsOf(r) {
    if (r.status === "expected") return [r.expected_month];
    if (!r.date_confirmed) return ["tbc"];
    const out = [];
    const a = parseISO(r.start), b = parseISO(r.end);
    const cur = new Date(a.getFullYear(), a.getMonth(), 1);
    while (cur <= b) {
      out.push(`${cur.getFullYear()}-${String(cur.getMonth() + 1).padStart(2, "0")}`);
      cur.setMonth(cur.getMonth() + 1);
    }
    return out;
  }
  // Mois "AAAA-MM" décalé de n mois
  function addMonths(ym, n) {
    const [y, m] = ym.split("-").map(Number);
    const d = new Date(y, m - 1 + n, 1);
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;
  }

  // Prochaine édition estimée d'une course non annoncée, recalculée à chaque ouverture de la page :
  // premier mois habituel situé après la dernière édition et à partir du mois en cours.
  function nextExpectedMonth(r) {
    if (!r.usual_months || !r.last_edition) return r.expected_month;
    const lastYM = r.last_edition.end.slice(0, 7);
    const startYear = Number(CURRENT_MONTH.slice(0, 4));
    let best = null;
    r.usual_months.forEach((m) => {
      for (let y = startYear; y <= startYear + 2; y++) {
        const ym = `${y}-${String(m).padStart(2, "0")}`;
        if (ym > lastYM && ym >= CURRENT_MONTH) {
          if (!best || ym < best) best = ym;
          break;
        }
      }
    });
    return best || r.expected_month;
  }

  function usualMonths(r) {
    return fmt.list.format(r.usual_months.map((m) => fmt.monthLong.format(new Date(2027, m - 1, 1))));
  }

  // ---------- Courses passées → non annoncées ----------
  // Même règle que tools/update_races.py, appliquée aussi ici pour que l'affichage reste juste
  // entre deux mises à jour automatiques (ou si l'une d'elles échoue) :
  //  - une course terminée devient « non annoncée » dans sa ville, sauf si une nouvelle édition
  //    de la même marque y est déjà annoncée (les Youngstars et les championnats ne sont pas reconduits) ;
  //  - une course « non annoncée » disparaît dès qu'une édition de la même marque est annoncée dans sa ville.
  const ONE_OFF_TAGS = ["championnat-du-monde", "championnat", "finale"];
  const BRAND_PAGE = {
    hyrox: "https://hyrox.com/find-my-race/",
    athx: "https://athxgames.com/events",
    deka: "https://www.spartan.com/en/deka",
  };
  function reconcile(list, today) {
    const key = (r) => `${r.brand}|${r.city.fr}|${r.cc}`;
    const upcoming = (r) => r.status === "announced" && (!r.date_confirmed || r.end >= today);
    const past = (r) => r.status === "announced" && r.date_confirmed && r.end < today;
    const upcomingKeys = new Set(list.filter((r) => upcoming(r) && r.type !== "youngstars").map(key));
    const expected = new Map();
    list.forEach((r) => {
      if (r.status === "expected" && !upcomingKeys.has(key(r))) {
        expected.set(key(r), { ...r, usual_months: [...(r.usual_months || [])] });
      }
    });
    list.filter(past).sort((a, b) => a.start.localeCompare(b.start)).forEach((r) => {
      if (r.type === "youngstars" || (r.tags || []).some((t) => ONE_OFF_TAGS.includes(t))) return;
      const k = key(r);
      if (upcomingKeys.has(k)) return;
      const month = Number(r.start.slice(5, 7));
      const last = { start: r.start, end: r.end, venue: r.venue || null };
      const e = expected.get(k);
      if (e) {
        if (!e.usual_months.includes(month)) e.usual_months.push(month);
        e.usual_months.sort((a, b) => a - b);
        if (!e.last_edition || r.start > e.last_edition.start) e.last_edition = last;
      } else {
        expected.set(k, {
          id: `expected-${r.brand}-${r.cc}-${r.city.en}`.toLowerCase().replace(/[^a-z0-9-]+/g, "-"),
          name: `${BRAND_LABEL[r.brand]} ${r.city.fr}`,
          brand: r.brand, city: r.city, cc: r.cc, continent: r.continent, type: "adults",
          start: null, end: null, date_confirmed: false, status: "expected",
          usual_months: [month], last_edition: last, expected_month: r.start.slice(0, 7),
          url: BRAND_PAGE[r.brand], lat: r.lat, lng: r.lng,
        });
      }
    });
    return list.filter(upcoming).concat([...expected.values()]);
  }

  // ---------- Démarrage ----------
  const data = window.RACES_DATA;
  if (!data) {
    document.getElementById("list").innerHTML = `<li class="empty">${esc(window.I18N[lang].loadError)}</li>`;
    return;
  }
  buildFormats();

  const sortKey = (r) => r.start || (r.status === "expected" ? r.expected_month + "-15" : "9999");
  const races = reconcile(data.races, TODAY)
    .map((r) => {
      if (r.status === "expected") r = { ...r, expected_month: nextExpectedMonth(r) };
      const x = { ...r, _status: statusOf(r), _months: monthsOf(r) };
      x._statusKeys = statusKeys(x);
      return x;
    })
    .sort((x, y) => sortKey(x).localeCompare(sortKey(y)) || x.name.localeCompare(y.name));

  // Boutons de mois : 12 mois glissants à partir du mois en cours (ex. en novembre 2026 : nov 2026 → oct 2027),
  // complétés par les mois plus lointains qui contiennent des courses, pour qu'aucune ne soit inaccessible.
  const monthKeys = (() => {
    const keys = new Set();
    for (let i = 0; i < WINDOW_MONTHS; i++) keys.add(addMonths(CURRENT_MONTH, i));
    races.flatMap((r) => r._months).forEach((m) => { if (m !== "tbc" && m >= CURRENT_MONTH) keys.add(m); });
    return [...keys].sort();
  })();
  const hasTbc = races.some((r) => r._status === "tbc");

  // ---------- Carte ----------
  // Limite verticale : on ne peut pas sortir de la bande de latitudes utiles ;
  // horizontalement, la carte tourne librement autour du globe.
  const LAT_SOUTH = -60, LAT_NORTH = 80;
  const map = L.map("map", {
    worldCopyJump: true,
    zoomSnap: 0.25,
    maxBounds: L.latLngBounds([LAT_SOUTH, -540], [LAT_NORTH, 540]),
    maxBoundsViscosity: 1,
  });

  // Zoom minimum calculé pour que la bande de latitudes remplisse toujours la hauteur de la carte
  function updateMinZoom() {
    const span = (lat) => L.CRS.EPSG3857.latLngToPoint(L.latLng(lat, 0), 0).y;
    const worldPx = span(LAT_SOUTH) - span(LAT_NORTH); // hauteur de la bande au zoom 0
    const h = map.getSize().y;
    const z = Math.max(1, Math.ceil(Math.log2(h / worldPx) * 4) / 4);
    map.setMinZoom(z);
    if (map.getZoom() < z) map.setZoom(z);
  }
  map.setView([30, 10], 2);
  updateMinZoom();
  map.on("resize", updateMinZoom);

  const toast = document.createElement("div");
  toast.className = "map-toast";
  toast.hidden = true;
  document.querySelector(".map-wrap").appendChild(toast);

  if (window.WORLD_SHAPES) {
    // Fond vectoriel embarqué (version hébergée sur Claude, où les tuiles externes sont bloquées) :
    // terres + frontières, dupliquées de part et d'autre pour le tour du globe.
    const renderer = L.canvas({ padding: 0.5 });
    [-360, 0, 360].forEach((off) => {
      const toLL = (c) => L.latLng(c[1], c[0] + off);
      L.geoJSON(window.WORLD_SHAPES.land, {
        renderer, interactive: false, coordsToLatLng: toLL,
        style: { stroke: false, fillColor: "#2b2b30", fillOpacity: 1 },
      }).addTo(map);
      L.geoJSON(window.WORLD_SHAPES.borders, {
        renderer, interactive: false, coordsToLatLng: toLL,
        style: { color: "#45454c", weight: 0.7, opacity: 1, fill: false },
      }).addTo(map);
    });
    map.setMaxZoom(9);
    map.attributionControl.addAttribution("Natural Earth");
  } else {
    // Fond de carte sombre (Esri, gratuit, sans clé)
    const ESRI = "https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/";
    const base = L.tileLayer(ESRI + "World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}", {
      maxZoom: 16, attribution: "Tiles &copy; Esri &mdash; Esri, HERE, Garmin, &copy; OpenStreetMap contributors",
    }).addTo(map);
    L.tileLayer(ESRI + "World_Dark_Gray_Reference/MapServer/tile/{z}/{y}/{x}", { maxZoom: 16 }).addTo(map);
    map.setMaxZoom(16);
    let tilesLoaded = 0, tilesFailed = 0;
    base.on("tileload", () => tilesLoaded++);
    base.on("tileerror", () => {
      if (++tilesFailed >= 6 && !tilesLoaded) {
        toast.textContent = T().tileError;
        toast.hidden = false;
      }
    });
  }

  // Sélecteur de langue (en haut à droite de la carte) : drapeau de la langue active,
  // qui déroule les autres langues au survol ou au clic
  const FLAGS = {
    fr: '<svg viewBox="0 0 3 2"><rect width="1" height="2" fill="#002395"/><rect x="1" width="1" height="2" fill="#fff"/><rect x="2" width="1" height="2" fill="#ed2939"/></svg>',
    en: '<svg viewBox="0 0 60 30"><clipPath id="uk-t"><path d="M30,15h30v15zv15h-30zh-30v-15zv-15h30z"/></clipPath><path d="M0,0v30h60v-30z" fill="#012169"/><path d="M0,0 60,30M60,0 0,30" stroke="#fff" stroke-width="6"/><path d="M0,0 60,30M60,0 0,30" clip-path="url(#uk-t)" stroke="#c8102e" stroke-width="4"/><path d="M30,0v30M0,15h60" stroke="#fff" stroke-width="10"/><path d="M30,0v30M0,15h60" stroke="#c8102e" stroke-width="6"/></svg>',
    de: '<svg viewBox="0 0 5 3"><rect width="5" height="1" fill="#000"/><rect y="1" width="5" height="1" fill="#dd0000"/><rect y="2" width="5" height="1" fill="#ffce00"/></svg>',
  };
  const LANG_NAMES = { fr: "Français", en: "English", de: "Deutsch" };
  const flag = (l) => `<span class="flag">${FLAGS[l]}</span>`;

  const LangControl = L.Control.extend({
    options: { position: "topright" },
    onAdd() {
      const el = L.DomUtil.create("div", "lang-switch");
      el.innerHTML = `<button type="button" class="lang-current" aria-haspopup="true" aria-expanded="false"></button>
        <ul class="lang-menu" role="menu"></ul>`;
      const btn = el.querySelector(".lang-current");
      btn.addEventListener("click", () => {
        const open = !el.classList.contains("is-open");
        el.classList.toggle("is-open", open);
        btn.setAttribute("aria-expanded", String(open));
      });
      el.addEventListener("mouseleave", () => {
        el.classList.remove("is-open");
        btn.setAttribute("aria-expanded", "false");
      });
      L.DomEvent.disableClickPropagation(el);
      return el;
    },
  });
  // Met à jour le drapeau affiché et la liste des autres langues
  function renderLangSwitch() {
    const el = document.querySelector(".lang-switch");
    if (!el) return;
    const btn = el.querySelector(".lang-current");
    btn.innerHTML = flag(lang);
    btn.title = `${T().language}${colon()} ${LANG_NAMES[lang]}`;
    btn.setAttribute("aria-label", btn.title);
    const menu = el.querySelector(".lang-menu");
    menu.innerHTML = "";
    LANGS.filter((l) => l !== lang).forEach((l) => {
      const li = document.createElement("li");
      li.innerHTML = `<button type="button" role="menuitem" lang="${l}">${flag(l)}<span>${LANG_NAMES[l]}</span></button>`;
      li.firstChild.addEventListener("click", () => {
        el.classList.remove("is-open");
        btn.setAttribute("aria-expanded", "false");
        setLang(l);
      });
      menu.appendChild(li);
    });
  }
  new LangControl().addTo(map);

  // Regroupements : couleur de la course la plus « importante » du groupe
  const cluster = L.markerClusterGroup({
    showCoverageOnHover: false,
    maxClusterRadius: 45,
    spiderfyOnMaxZoom: true,
    iconCreateFunction(c) {
      const kids = c.getAllChildMarkers();
      const n = kids.reduce((s, m) => s + m.options.eventCount, 0);
      const best = kids.reduce((a, m) => (RANK[m.options.best] > RANK[a] ? m.options.best : a), "exp");
      return L.divIcon({ html: `<span>${n}</span>`, className: `cluster cluster-${best}`, iconSize: [40, 40] });
    },
  });
  map.addLayer(cluster);

  let markersByCity = new Map();
  let pinned = null;   // marqueur dont la fiche a été ouverte au clic
  let closeTimer = null;

  // ---------- Filtres ----------
  function chip(group, key, html, title) {
    const b = document.createElement("button");
    b.type = "button";
    b.className = "chip";
    b.dataset.group = group;
    b.dataset.key = key;
    b.dataset.title = title || "";
    b.setAttribute("aria-pressed", "false");
    b.innerHTML = html;
    b.addEventListener("click", () => {
      const set = state[group];
      set.has(key) ? set.delete(key) : set.add(key);
      render({ fit: group === "continent" });
    });
    return b;
  }

  function buildChips() {
    const t = T();
    const elCont = document.getElementById("f-continent");
    elCont.innerHTML = "";
    CONTINENTS.forEach((k) => elCont.appendChild(chip("continent", k, `${esc(t.continents[k])} <span class="n"></span>`)));

    const elMonth = document.getElementById("f-month");
    elMonth.innerHTML = "";
    monthKeys.forEach((k) => {
      const d = parseISO(k + "-01");
      elMonth.appendChild(chip("month", k,
        `<span>${esc(noDot(fmt.monthShort.format(d)))}</span><span class="y">${d.getFullYear()}</span>`,
        fmt.monthYear.format(d)));
    });
    if (hasTbc) {
      const b = chip("month", "tbc", esc(t.dateTbc));
      b.classList.add("wide");
      elMonth.appendChild(b);
    }

    const elStatus = document.getElementById("f-status");
    elStatus.innerHTML = "";
    STATUS_FILTERS.forEach((k) => elStatus.appendChild(chip("status", k, `${esc(t.statusFilter[k])} <span class="n"></span>`)));

    const elType = document.getElementById("f-brand");
    elType.innerHTML = "";
    BRANDS.forEach((k) => elType.appendChild(chip("brand", k, `${BRAND_LABEL[k]} <span class="n"></span>`)));
  }

  document.querySelectorAll("[data-reset]").forEach((b) =>
    b.addEventListener("click", () => {
      state[b.dataset.reset].clear();
      render({ fit: b.dataset.reset === "continent" });
    })
  );
  // Bouton « Filtres » (affiché sur mobile) : replie ou déplie les filtres
  const panel = document.getElementById("panel");
  const ftBtn = document.getElementById("filters-toggle");
  ftBtn.addEventListener("click", () => {
    const open = !panel.classList.contains("filters-open");
    panel.classList.toggle("filters-open", open);
    ftBtn.setAttribute("aria-expanded", String(open));
  });

  document.getElementById("reset-all").addEventListener("click", () => {
    Object.values(state).forEach((s) => s.clear());
    render({ fit: true });
  });

  function inGroup(r, group, key) {
    if (group === "month") return r._months.includes(key);
    if (group === "status") return r._statusKeys.includes(key);
    return r[group] === key;
  }
  function match(r, skip) {
    for (const g of Object.keys(state)) {
      if (g === skip || !state[g].size) continue;
      if (![...state[g]].some((k) => inGroup(r, g, k))) return false;
    }
    return true;
  }

  function updateChips() {
    document.querySelectorAll(".chip").forEach((b) => {
      const { group, key } = b.dataset;
      const on = state[group].has(key);
      b.setAttribute("aria-pressed", String(on));
      // Nombre de courses si ce choix était actif (avec les autres filtres)
      const n = races.filter((r) => match(r, group) && inGroup(r, group, key)).length;
      const nEl = b.querySelector(".n");
      if (nEl) nEl.textContent = n;
      b.disabled = n === 0 && !on;
      if (b.dataset.title) b.title = `${b.dataset.title} · ${n} ${T().races(n)}`;
    });
  }

  // ---------- Fiche ----------
  function eventHTML(r) {
    const t = T();
    if (r._status === "exp") {
      const le = r.last_edition;
      const est = fmt.monthYear.format(parseISO(r.expected_month + "-01"));
      return `<div class="card-event">
        <div class="title">${esc(raceName(r))}</div>
        <div class="dates">${esc(t.nextEstimate)}${colon()} ${esc(est)}</div>
        <div class="badges">${brandBadge(r)}<span class="badge badge-exp">${esc(t.st.exp)}</span></div>
        <p class="note"><b>${esc(t.lastEdition)}${colon()}</b> ${esc(formatRange(le.start, le.end))}${le.venue ? " · " + esc(le.venue) : ""}</p>
        ${r.note ? `<p class="note">${esc(tr(r.note))}</p>` : ""}
        <a class="card-link ghost" href="${esc(r.url)}" target="_blank" rel="noopener">${esc(t.checkOfficial)} ↗</a>
      </div>`;
    }
    const badges = [brandBadge(r), `<span class="badge badge-${r._status}">${esc(t.st[r._status])}</span>`];
    if (r.type === "youngstars") badges.push(`<span class="badge badge-ys">${esc(t.types.youngstars)}</span>`);
    (r.tags || []).forEach((tag) => { if (t.tags[tag]) badges.push(`<span class="badge badge-tag">${esc(t.tags[tag])}</span>`); });
    const notes = [];
    if (r.ticket_info) notes.push(`<p class="note"><b>${esc(t.tickets)}${colon()}</b> ${esc(tr(r.ticket_info))}</p>`);
    if (r.venue) notes.push(`<p class="note"><b>${esc(t.venue)}${colon()}</b> ${esc(r.venue)}</p>`);
    if (r.geo_note) notes.push(`<p class="note">${esc(tr(r.geo_note))}</p>`);
    if (r.note) notes.push(`<p class="note">${esc(tr(r.note))}</p>`);
    return `<div class="card-event">
      <div class="title">${esc(raceName(r))}</div>
      <div class="dates">${esc(r.date_confirmed ? formatRange(r.start, r.end) : t.dateTbc)}</div>
      <div class="badges">${badges.join("")}</div>
      ${notes.join("")}
      <a class="card-link" href="${esc(r.url)}" target="_blank" rel="noopener">${esc(t.officialPage)} ↗</a>
    </div>`;
  }

  function cardHTML(group) {
    const first = group[0];
    const n = group.length;
    return `<div class="card-head">
        <h3>${esc(cityName(first))}</h3>
        <p>${esc(countryName(first))} · ${n} ${esc(T().races(n))}</p>
      </div>
      <div class="card-events">${group.map(eventHTML).join("")}</div>`;
  }

  // ---------- Marqueurs ----------
  function buildMarkers(list) {
    cluster.clearLayers();
    markersByCity = new Map();
    pinned = null;

    const groups = new Map();
    list.forEach((r) => {
      const k = cityKey(r);
      if (!groups.has(k)) groups.set(k, []);
      groups.get(k).push(r);
    });

    groups.forEach((group, k) => {
      const best = group.reduce((a, r) => (RANK[r._status] > RANK[a] ? r._status : a), "exp");
      const icon = L.divIcon({
        className: "",
        html: `<div class="pin pin-${best}">${group.length}</div>`,
        iconSize: [30, 30], iconAnchor: [15, 15], popupAnchor: [0, -14],
      });
      const m = L.marker([group[0].lat, group[0].lng], { icon, eventCount: group.length, best, title: cityName(group[0]) });
      m.bindPopup(cardHTML(group), { autoPan: false, maxWidth: 300, minWidth: 290, closeOnClick: false });

      // Survol : la fiche s'ouvre et reste ouverte tant que la souris est sur le marqueur ou la fiche
      m.on("mouseover", () => {
        clearTimeout(closeTimer);
        if (pinned && pinned !== m) return;
        if (!m.isPopupOpen()) {
          m.getPopup().options.autoPan = false;
          m.openPopup();
        }
      });
      m.on("mouseout", () => scheduleClose(m));
      // Clic (ou tap sur mobile) : fiche épinglée jusqu'à sa fermeture
      m.on("click", () => {
        pinned = m;
        m.getPopup().options.autoPan = true;
        m.openPopup();
      });
      m.on("popupopen", (e) => {
        const el = e.popup.getElement();
        el.onmouseenter = () => clearTimeout(closeTimer);
        el.onmouseleave = () => scheduleClose(m);
        highlightList(k, true);
      });
      m.on("popupclose", () => {
        if (pinned === m) pinned = null;
        highlightList(k, false);
      });

      markersByCity.set(k, m);
      cluster.addLayer(m);
    });
  }

  function scheduleClose(m) {
    clearTimeout(closeTimer);
    closeTimer = setTimeout(() => {
      if (pinned !== m && m.isPopupOpen()) m.closePopup();
    }, 250);
  }

  function openFromList(r) {
    const m = markersByCity.get(cityKey(r));
    if (!m) return;
    cluster.zoomToShowLayer(m, () => {
      pinned = m;
      m.getPopup().options.autoPan = true;
      m.openPopup();
    });
  }

  // ---------- Liste ----------
  const elList = document.getElementById("list");
  function renderList(list) {
    const t = T();
    if (!list.length) {
      elList.innerHTML = `<li class="empty">${esc(t.noResults)}</li>`;
      return;
    }
    elList.innerHTML = "";
    list.forEach((r) => {
      const li = document.createElement("li");
      li.className = "race-item";
      li.dataset.city = cityKey(r);
      let dateBlock;
      if (r.date_confirmed) {
        const a = parseISO(r.start);
        dateBlock = `<div class="race-date"><div class="d">${a.getDate()}</div><div class="m">${esc(noDot(fmt.monthShort.format(a)))} ${String(a.getFullYear()).slice(2)}</div></div>`;
      } else if (r._status === "exp") {
        const a = parseISO(r.expected_month + "-01");
        dateBlock = `<div class="race-date exp"><div class="d">≈</div><div class="m">${esc(noDot(fmt.monthShort.format(a)))} ${String(a.getFullYear()).slice(2)}</div></div>`;
      } else {
        dateBlock = `<div class="race-date tbc"><div class="d">?</div><div class="m">${esc(t.tbcShort)}</div></div>`;
      }
      li.innerHTML = `${dateBlock}
        <div>
          <div class="race-brand">${BRAND_LABEL[r.brand]}</div>
          <div class="race-name">${esc(raceName(r))}</div>
          <div class="race-meta">
            <span>${esc(cityName(r))}, ${esc(countryName(r))}</span>
            <span class="badge badge-${r._status}">${esc(t.st[r._status])}</span>
            ${r.type === "youngstars" ? `<span class="badge badge-ys">${esc(t.types.youngstars)}</span>` : ""}
          </div>
          ${r.date_confirmed ? `<div class="race-meta">${esc(formatRange(r.start, r.end))}</div>` : ""}
          ${r._status === "exp" ? `<div class="race-meta">${esc(t.usuallyIn)} ${esc(usualMonths(r))}</div>` : ""}
        </div>`;
      li.addEventListener("click", () => openFromList(r));
      elList.appendChild(li);
    });
  }

  function highlightList(key, on) {
    elList.querySelectorAll(".race-item").forEach((li) => {
      if (li.dataset.city === key) li.classList.toggle("is-active", on);
    });
  }

  // ---------- Textes statiques ----------
  function applyStaticTexts() {
    const t = T();
    document.documentElement.lang = lang;
    document.title = t.htmlTitle;
    document.querySelector('meta[name="description"]').content = t.metaDesc;
    const get = (path) => path.split(".").reduce((o, k) => o[k], t);
    document.querySelectorAll("[data-i18n]").forEach((el) => (el.textContent = get(el.dataset.i18n)));
    document.querySelectorAll("[data-i18n-html]").forEach((el) => (el.innerHTML = get(el.dataset.i18nHtml)));
    document.querySelectorAll("[data-i18n-aria]").forEach((el) => el.setAttribute("aria-label", get(el.dataset.i18nAria)));
    document.getElementById("map").setAttribute("aria-label", t.mapLabel);
    renderLangSwitch();
    // Date de la dernière mise à jour de la base (écrite par tools/update_races.py)
    const upd = document.getElementById("updated");
    const updatedAt = data.meta && data.meta.updated_at;
    if (upd) {
      upd.hidden = !updatedAt;
      if (updatedAt) {
        upd.textContent = t.updatedOn(new Intl.DateTimeFormat(lang, { day: "2-digit", month: "2-digit", year: "numeric" }).format(parseISO(updatedAt)));
      }
    }
    if (!toast.hidden) toast.textContent = t.tileError;
  }

  function setLang(l) {
    if (l === lang) return;
    lang = l;
    try { localStorage.setItem("raceFinder.lang", l); } catch (e) {}
    buildFormats();
    map.closePopup();
    applyStaticTexts();
    buildChips();
    render();
  }

  // ---------- Rendu global ----------
  function render(opts = {}) {
    const t = T();
    const list = races.filter((r) => match(r));
    updateChips();
    buildMarkers(list);
    renderList(list);
    const cities = new Set(list.map(cityKey)).size;
    document.getElementById("count").textContent =
      `${list.length} ${t.races(list.length)} · ${cities} ${t.cities(cities)}`;
    // Nombre de choix actifs, rappelé sur le bouton « Filtres »
    const nActive = Object.values(state).reduce((s, set) => s + set.size, 0);
    const elActive = document.getElementById("filters-active");
    elActive.textContent = nActive ? t.activeFilters(nActive) : "";
    elActive.hidden = !nActive;

    if (opts.fit) {
      if (list.length && state.continent.size) {
        map.fitBounds(L.latLngBounds(list.map((r) => [r.lat, r.lng])), { padding: [40, 40], maxZoom: 6 });
      } else if (!state.continent.size) {
        map.setView([30, 10], Math.max(2, map.getMinZoom()));
      }
    }
  }

  applyStaticTexts();
  buildChips();
  render();
})();
