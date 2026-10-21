# Hybrid Race Finder

An interactive map of hybrid fitness races (**HYROX**, **ATHX** and **DEKA**) built to answer one question quickly: *where and when can I race next?*

Official race calendars are spread across several sites and are hard to browse. Hybrid Race Finder puts every race on a single world map, with filters and a short info card per city linking back to the official event page.

> **Unofficial project.** Hybrid Race Finder is a personal project and is not affiliated with, endorsed by or connected to the organisers of the races listed. Race names and brands belong to their respective owners. Information may be incomplete or out of date: always check the official event page before booking.

## Features

- **World map** with zoom and pan, and markers grouped by city; clusters take the colour of their most relevant race.
- **Info card** on hover (or tap on mobile): dates, venue, ticket status, Youngstars / championship badges and a link to the official page.
- **Filters**:
  - region: Europe, North America, South America, Asia-Pacific, Africa;
  - period: one button per month over a rolling 12-month window;
  - status: tickets on sale, announced, not announced yet;
  - category: HYROX, ATHX, DEKA.
- **Ticket status colours**: yellow = tickets on sale, blue = info coming soon, grey = date to be announced, dashed = not announced yet.
- **"Not announced" races**: cities that hosted a race recently but have no new edition announced yet, with the last edition and an estimated month for the next one.
- **Daily automatic update** of the race data through GitHub Actions, with the date of the last update shown in the header.
- **Three languages** (French, English, German) with a flag switcher; dates and country names are localised.
- **Responsive**: map and list side by side on desktop; map on top and collapsible filters on mobile.

## Licence

Copyright © 2026 HybridRaceFinder. **All rights reserved.**

The source code of this repository is published for viewing only. No licence is granted to copy, modify, distribute or use it, in whole or in part, without the author's prior written permission. See [LICENSE](LICENSE).

Race information belongs to the respective race organisers, and HYROX, ATHX and DEKA are trademarks of their owners.

## Credits

Map: [Leaflet](https://leafletjs.com) and Leaflet.markercluster. Map tiles © Esri, HERE, Garmin, © OpenStreetMap contributors. World outline: Natural Earth. Geocoding: OpenStreetMap Nominatim.

## Method
This project was designed by Hybrid Race Finder Creator and written with the help of an AI assistant (Claude, by Anthropic), through an iterative conversation: the author defined the features, tested each version and asked for changes; the assistant wrote the code, the data collection and the tests. The author is not a professional developer, so the code is provided as is and probably does not follow industry standards and best practices.
The prompt below summarises the full specification. Given to an AI coding assistant, it should produce an equivalent project. It will not produce identical code, as AI output differs from one run to the next.

<details>
<summary>Prompt to rebuild the project</summary>

```text
Build "Hybrid Race Finder", a static website (HTML, CSS, vanilla JavaScript, no build step) hosted on GitHub Pages, showing HYROX, ATHX and DEKA fitness races on an interactive world map.

DATA
- One JSON database (data/races.json) plus a JS copy (data/races.js, `window.RACES_DATA = …`) so the page also works when opened by double-click.
- Each race: id, name, brand (hyrox | athx | deka), city {fr, en, de}, cc (ISO country code), continent (europe, north-america, south-america, asia-pacific, africa), type (adults | youngstars), start, end (ISO dates, null if "date coming soon"), date_confirmed, status (announced | expected), listing_cta (buy_tickets | find_out_more), optional ticket_info {fr, en, de} (e.g. "ticket sales opening soon"), url (official page), lat, lng (city level), optional venue, tags (championnat-du-monde, championnat, finale, founders), note.
- "expected" races = cities that hosted a race recently with no new edition announced yet: usual_months, last_edition {start, end, venue}, expected_month.
- Seed it from the official lists: hyrox.com/find-my-race, athxgames.com/events (and /past-events), spartan.com DEKA "find a race" pages (US, UK, ES).

MAP AND INTERFACE
- Leaflet 1.9.4 + Leaflet.markercluster 1.5.3. Dark basemap only: Esri "World Dark Gray Base" + "Reference" tiles (free, no API key); show a message if tiles fail.
- Limit vertical panning to latitudes -60/80 (maxBounds + viscosity 1); compute the minimum zoom so this band always fills the map height; horizontal wrapping allowed.
- One marker per city showing the number of races. Status colours: yellow #ffe500 = tickets on sale, blue #5ec2ff = info coming soon (or ticket_info set), grey = date to be announced, dashed white outline = not announced. A marker and a cluster take the colour of their most important race, priority yellow > blue > grey > dashed.
- Info card on hover (stays open while hovering the card), pinned on click/tap: city, country, then each race with brand badge, dates, status badge, Youngstars / championship badges, venue, notes and an "Official page" button. For expected races: estimated next edition, last edition (dates and venue), note, link to the brand's race list.
- Side list sorted by date, synced with the filters; clicking an item zooms to the city and opens its card.
- Filters (empty = show all), each chip showing how many races it would give, chips with 0 disabled:
  region (5 continents, on two lines); period (one button per month over a rolling 12-month window from the current month, plus later months that contain races, plus "date to be announced"; a multi-month race appears in each month); status ("on sale", "announced", "not announced"); category (HYROX, ATHX, DEKA). "All" reset per group and a global reset.
- Header: logo (three yellow running-track lanes), title "Hybrid Race Finder", "Updated on <date>" read from meta.updated_at, short notice "Unofficial site. Always check the official sites: HYROX, ATHX, DEKA" with links.
- Three languages (French, English, German) with a flag dropdown (current flag only, other languages with flag and name on hover/click) in the top-right corner of the map; default to the browser language, remember the choice in localStorage; translate the interface, city names, country names (Intl.DisplayNames) and dates (Intl.DateTimeFormat).
- Dark theme, yellow accent, fonts Barlow Condensed (headings) and Barlow (text). Custom scrollbar (track = panel colour, thumb and arrows = text colour). Zoom buttons must not stay highlighted after a click. Favicon = the logo.
- Responsive: map left/list right on desktop; on mobile map on top, list below, filters collapsed behind a "Filters" button showing the number of active filters.

PAST RACES (same rule in the page and in the updater)
- A finished race becomes "not announced" in its city unless a new edition of the same brand is already announced there; it then shows its last edition and the estimated next month (first usual month after the last edition, from the current month).
- A "not announced" entry disappears as soon as an edition of the same brand is announced in its city.
- Youngstars races and championships/finals are not carried over; they simply disappear once finished.

DAILY AUTOMATIC UPDATE
- tools/update_races.py (Python, requests + BeautifulSoup), run every night by .github/workflows/update.yml (GitHub Actions, also runnable by hand), which commits data/races.json, data/races.js, data/geocache.json and data/update_report.json.
- Parse each listing page by splitting it into one text segment per event in document order (everything between an event link and the next event link), so dates and "Buy tickets" / "Enter now" buttons are found whatever the HTML nesting.
- HYROX: list page for dates and button; each event page to detect explicit wording only ("ticket sales open soon"…; never "ticket notification list" or "waitlist", which also appear when sales are open) and the venue; WordPress API (/wp-json/wp/v2/event?slug=) for the continent and Youngstars type of new events.
- DEKA: keep an event only if DEKA is in its own title (the pages also list Spartan obstacle races).
- Update only the collected fields (name, dates, button, link, ticket info); keep translations, coordinates, notes and tags. Add new races (reuse known cities, otherwise geocode with OpenStreetMap Nominatim and cache), remove upcoming races no longer listed, then apply the past-race rule.
- Safeguards: polite crawling (identified User-Agent, 1.5 s between requests, retries); if a site is unreadable or returns < 60 % of the previous number of races, leave that brand unchanged; if the number of races on sale collapses (< 30 % of before), keep the previous ticket status. Unreadable sites make the run fail (e-mail alert); new races that cannot be located are only reported.
- Tests without network (tests/test_update.py): date formats of the three sites, parsing of sample pages, ticket status changing colour, expected/announced transitions, safeguards.

DOCUMENTATION
- README in English, licence "All rights reserved" with a LICENSE file.
```
