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
