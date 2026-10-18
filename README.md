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

## Run it locally

Open `index.html` in a browser (an internet connection is needed for the map tiles and the Leaflet library).
During development, a local server is more convenient:

```bash
python -m http.server 8000
# then open http://localhost:8000
```

## Publish on GitHub Pages

1. Create a **public** repository on GitHub and upload the content of this folder (drag and drop the files and folders; `index.html` must be at the root).
2. **Settings → Pages → Branch: `main` / `/ (root)` → Save.**
3. The site is live a minute or two later at `https://<username>.github.io/<repository>/`.

## Automatic updates

The workflow `.github/workflows/update.yml` runs `tools/update_races.py` every night (04:23 UTC). The script:

1. reads the official race lists (hyrox.com, athxgames.com, spartan.com for DEKA) and, for HYROX, each event page (to detect "ticket sales open soon" and the venue);
2. refreshes dates, names, links and ticket status, adds new races (new cities are geocoded with OpenStreetMap Nominatim and cached in `data/geocache.json`) and removes races that are no longer listed;
3. turns every race that has taken place into a **not announced** entry for its city, unless a new edition of the same brand is already announced there, and removes a not announced entry as soon as a new edition appears (Youngstars and championships are not carried over);
4. writes `data/races.json`, `data/races.js` and `data/update_report.json`, then commits them; GitHub Pages republishes the site automatically.

The page applies the same past-race rule when it loads, so the display stays correct even between two updates.

**One-time setup**

- **Settings → Actions → General → Workflow permissions → "Read and write permissions" → Save** (lets the workflow save the new data).
- The `.github` folder starts with a dot, so it may be hidden on your computer and skipped by drag and drop. If it does not appear in the repository, create the file in GitHub instead: **Add file → Create new file**, name it `.github/workflows/update.yml` and paste the content of the file.
- To run an update immediately: **Actions → Update races → Run workflow**.

**If a site cannot be read** (site down or layout changed), that brand is left untouched, the other brands are still updated, and the run is marked as failed so GitHub sends you an e-mail. The details are in `data/update_report.json` and in the run log. New races whose city cannot be located are listed there too and can be added by hand.

**Please keep the crawl polite**: one run a day, one request every 1.5 seconds per site. Automated collection may be restricted by the terms of use of the official sites; check them before making the site public.

## Editing the data by hand

`data/races.json` is the source of truth. You can edit it directly (for example to add a note, fix coordinates or add a not announced city), then regenerate `data/races.js`:

```bash
python -c "import json,sys; sys.path.insert(0,'tools'); import update_races as u; u.write_outputs(json.load(open('data/races.json',encoding='utf-8')))"
```

The updater only rewrites the fields it collects (name, dates, ticket status, link) and keeps everything else (translations, coordinates, notes, tags).
`tools/build_races.py` rebuilds the initial v4 database from scratch; it refuses to overwrite the live database unless run with `--force`.

### Race fields

| Field | Description |
|---|---|
| `id` | unique identifier |
| `name` | official event name |
| `brand` | `hyrox`, `athx` or `deka` |
| `city` | city name in `fr`, `en`, `de` |
| `cc` | ISO country code (country names are translated by the browser) |
| `continent` | `europe`, `north-america`, `south-america`, `asia-pacific`, `africa` |
| `type` | `adults` or `youngstars` |
| `start`, `end` | ISO dates (`null` when the date is not announced) |
| `date_confirmed` | `false` when the official site says "date coming soon" |
| `status` | `announced` or `expected` (not announced yet) |
| `listing_cta` | `buy_tickets` or `find_out_more`, as shown on the official list |
| `ticket_info` | optional `{fr, en, de}` text, e.g. ticket sales opening soon (shown in blue) |
| `url` | official page |
| `lat`, `lng` | coordinates (city level) |
| `venue`, `tags`, `note`, `geo_note` | optional |
| `usual_months`, `last_edition`, `expected_month` | not announced races: usual month(s), last edition, estimated next month |

## Project structure

```
index.html                    page
assets/style.css              styles
assets/app.js                 map, filters, cards, list, past-race rule
assets/i18n.js                interface texts (fr, en, de)
assets/favicon*               tab icon
data/races.json               race database (source of truth)
data/races.js                 same data, loaded by the page (generated)
data/geocache.json            geocoding cache (generated)
data/update_report.json       report of the last update (generated)
data/world-110m.json          built-in world outline, used by the single-file version
tools/update_races.py         daily updater
tools/build_races.py          initial database builder (v4)
tools/build_artifact.py       single-file version of the page
tests/test_update.py          tests of the updater (no network needed)
.github/workflows/update.yml  daily schedule
```

Run the tests with `python tests/test_update.py` (requires `requests` and `beautifulsoup4`).

## Versions

- **v5**: daily automatic update (GitHub Actions); "updated on" date in the header; past races automatically become "not announced"; yellow colour scheme; English README; licence notice.
- **v4**: renamed Hybrid Race Finder; ATHX and DEKA races; category filter HYROX / ATHX / DEKA; track-lane logo; Barlow typeface.
- **v3**: French, English and German interface; "tickets on sale" filter; coloured clusters; limited vertical panning; rolling month buttons; collapsible filters on mobile.
- **v2**: not announced races; status filter; key-free map tiles; tab icon.
- **v1**: first version, 101 announced HYROX races.

## Licence

Copyright © 2026 Baptiste. **All rights reserved.**

The source code of this repository is published for viewing only. No licence is granted to copy, modify, distribute or use it, in whole or in part, without the author's prior written permission. See [LICENSE](LICENSE).

Race information belongs to the respective race organisers, and HYROX, ATHX and DEKA are trademarks of their owners.

## Credits

Map: [Leaflet](https://leafletjs.com) and Leaflet.markercluster. Map tiles © Esri, HERE, Garmin, © OpenStreetMap contributors. World outline: Natural Earth. Geocoding: OpenStreetMap Nominatim.
