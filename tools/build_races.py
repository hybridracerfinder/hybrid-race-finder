"""Base des courses : génère data/races.json et data/races.js à partir de la liste relevée sur hyrox.com/find-my-race (15/10/2026)."""
import json, os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

EU, AP, NA, SA, AF = "europe", "asia-pacific", "north-america", "south-america", "africa"

# slug | nom | ville | pays | continent | type | début | fin | cta | lat | lng
R = [
("hyrox-valencia","HYROX Valencia","Valencia","Espagne",EU,"adults","2026-10-15","2026-10-18","buy",39.4699,-0.3763),
("hyrox-sao-paulo-2","HYROX São Paulo","São Paulo","Brésil",SA,"adults","2026-10-17","2026-10-18","buy",-23.5505,-46.6333),
("hyrox-youngstars-valencia","HYROX Youngstars Valencia","Valencia","Espagne",EU,"youngstars","2026-10-17","2026-10-18","buy",39.4699,-0.3763),
("hyrox-budapest","HYROX Budapest","Budapest","Hongrie",EU,"adults","2026-10-17","2026-10-17","buy",47.4979,19.0402),
("hyrox-tampa","MyFitnessPal HYROX Tampa","Tampa","États-Unis",NA,"adults","2026-10-22","2026-10-25","buy",27.9506,-82.4572),
("hyrox-abu-dhabi","HYROX Abu Dhabi","Abu Dhabi","Émirats arabes unis",AP,"adults","2026-10-23","2026-10-25","buy",24.4539,54.3773),
("hyrox-birmingham","HYROX Birmingham","Birmingham","Royaume-Uni",EU,"adults","2026-10-27","2026-11-01","buy",52.4862,-1.8904),
("intersport-hyrox-hamburg","INTERSPORT HYROX Hamburg","Hambourg","Allemagne",EU,"adults","2026-10-28","2026-11-01","buy",53.5511,9.9937),
("hyrox-nice-s26-27","TRAINSWEATEAT HYROX Nice","Nice","France",EU,"adults","2026-10-29","2026-11-01","buy",43.7102,7.2620),
("hyrox-mexico-city","COMMANDO HYROX Mexico City","Mexico","Mexique",NA,"adults","2026-10-29","2026-11-01","buy",19.4326,-99.1332),
("hyrox-shanghai-1031","ZhongAn HYROX Shanghai","Shanghai","Chine",AP,"adults",None,None,"buy",31.2304,121.4737),
("hyrox-youngstars-birmingham","HYROX Youngstars Birmingham","Birmingham","Royaume-Uni",EU,"youngstars","2026-10-31","2026-11-01","buy",52.4862,-1.8904),
("hyrox-dublin","HYROX Dublin","Dublin","Irlande",EU,"adults","2026-11-11","2026-11-15","buy",53.3498,-6.2603),
("hyrox-dusseldorf","EDEKA HYROX Düsseldorf","Düsseldorf","Allemagne",EU,"adults","2026-11-11","2026-11-15","buy",51.2277,6.7735),
("hyrox-barcelona-2","Leapmotor HYROX Barcelona","Barcelone","Espagne",EU,"adults","2026-11-11","2026-11-15","buy",41.3874,2.1686),
("hyrox-denver","The Feed HYROX Denver","Denver","États-Unis",NA,"adults","2026-11-12","2026-11-15","buy",39.7392,-104.9903),
("hyrox-seoul","AirAsia HYROX Seoul","Séoul","Corée du Sud",AP,"adults","2026-11-13","2026-11-15","buy",37.5665,126.9780),
("hyrox-cairo","HYROX Cairo","Le Caire","Égypte",AF,"adults","2026-11-14","2026-11-15","buy",30.0444,31.2357),
("hyrox-dallas","HYROX Dallas","Dallas","États-Unis",NA,"adults","2026-11-18","2026-11-22","buy",32.7767,-96.7970),
("hyrox-poznan","HYROX Poznań","Poznań","Pologne",EU,"adults","2026-11-20","2026-11-22","buy",52.4064,16.9252),
("hyrox-guangzhou","HYROX Guangzhou","Canton","Chine",AP,"adults","2026-11-21","2026-11-22","info",23.1291,113.2644),
("hyrox-rio-de-janeiro","HYROX Rio de Janeiro","Rio de Janeiro","Brésil",SA,"adults","2026-11-21","2026-11-22","buy",-22.9068,-43.1729),
("aia-hyrox-singapore","AIA HYROX Singapore","Singapour","Singapour",AP,"adults","2026-11-26","2026-11-29","buy",1.3521,103.8198),
("virgin-active-hyrox-johannesburg-26-27","Virgin Active HYROX Johannesburg","Johannesburg","Afrique du Sud",AF,"adults","2026-11-26","2026-11-29","buy",-26.2041,28.0473),
("hyrox-utrecht","HYROX Utrecht","Utrecht","Pays-Bas",EU,"adults","2026-11-26","2026-11-30","buy",52.0907,5.1214),
("hyrox-gujarat","IndusInd Bank HYROX Gujarat","Gujarat","Inde",AP,"adults","2026-11-26","2026-11-28","buy",23.0225,72.5714),
("hyrox-dubai","HYROX Dubai","Dubaï","Émirats arabes unis",AP,"adults","2026-11-27","2026-11-28","buy",25.2048,55.2708),
("hyrox-youngstars-utrecht","HYROX Youngstars Utrecht","Utrecht","Pays-Bas",EU,"youngstars","2026-11-28","2026-11-29","buy",52.0907,5.1214),
("hyrox-youngstars-singapore","AIA HYROX Youngstars Singapore","Singapour","Singapour",AP,"youngstars","2026-11-28","2026-11-29","buy",1.3521,103.8198),
("hyrox-london-excel","Amazon HYROX London","Londres","Royaume-Uni",EU,"adults","2026-12-02","2026-12-06","buy",51.5074,-0.1278),
("hyrox-anaheim-26-27","Centr HYROX Anaheim","Anaheim","États-Unis",NA,"adults","2026-12-03","2026-12-06","buy",33.8366,-117.9143),
("hyrox-milan","HYROX Milan","Milan","Italie",EU,"adults","2026-12-04","2026-12-06","buy",45.4642,9.1900),
("hyrox-youngstars-london-excel","HYROX Youngstars London ExCeL","Londres","Royaume-Uni",EU,"youngstars","2026-12-05","2026-12-06","buy",51.5074,-0.1278),
("hyrox-youngstars-anaheim","HYROX Youngstars Anaheim","Anaheim","États-Unis",NA,"youngstars","2026-12-05","2026-12-06","buy",33.8366,-117.9143),
("30454","24/7 Fitness HYROX Sanya","Sanya","Chine",AP,"adults","2026-12-05","2026-12-06","buy",18.2528,109.5119),
("hyrox-melbourne","BYD HYROX Melbourne","Melbourne","Australie",AP,"adults","2026-12-09","2026-12-13","buy",-37.8136,144.9631),
("hyrox-nashville","HYROX Nashville","Nashville","États-Unis",NA,"adults","2026-12-09","2026-12-13","buy",36.1627,-86.7816),
("intersport-hyrox-stockholm-arena","INTERSPORT HYROX Stockholm","Stockholm","Suède",EU,"adults","2026-12-10","2026-12-13","buy",59.3293,18.0686),
("fitness-first-hyrox-frankfurt","Fitness First HYROX Frankfurt","Francfort","Allemagne",EU,"adults","2026-12-10","2026-12-13","buy",50.1109,8.6821),
("hyrox-kuala-lumpur","AirAsia HYROX Kuala Lumpur","Kuala Lumpur","Malaisie",AP,"adults","2026-12-10","2026-12-13","buy",3.1390,101.6869),
("hyrox-paris-s26-27","Fitness Park HYROX Paris","Paris","France",EU,"adults","2026-12-12","2026-12-20","buy",48.8566,2.3522),
("hyrox-gent","HYROX Gent","Gand","Belgique",EU,"adults","2026-12-17","2026-12-20","buy",51.0543,3.7174),
("hyrox-vancouver","HYROX Vancouver","Vancouver","Canada",NA,"adults","2026-12-17","2026-12-20","buy",49.2827,-123.1207),
("hyrox-helsinki-2","HYROX Helsinki","Helsinki","Finlande",EU,"adults","2026-12-18","2026-12-20","buy",60.1699,24.9384),
("hyrox-youngstars-paris","HYROX Youngstars Paris","Paris","France",EU,"youngstars","2026-12-19","2026-12-20","buy",48.8566,2.3522),
("hyrox-hong-kong","AIA HYROX Hong Kong","Hong Kong","Hong Kong",AP,"adults","2027-01-07","2027-01-10","buy",22.3193,114.1694),
("hyrox-noida","HYROX Noida","Noida","Inde",AP,"adults","2027-01-15","2027-01-17","info",28.5355,77.3910),
("hyrox-manchester","HYROX Manchester","Manchester","Royaume-Uni",EU,"adults","2027-01-20","2027-01-31","buy",53.4808,-2.2426),
("byd-hyrox-osaka","BYD HYROX Osaka","Osaka","Japon",AP,"adults","2027-01-21","2027-01-25","buy",34.6937,135.5023),
("hyrox-amsterdam","HYROX Amsterdam","Amsterdam","Pays-Bas",EU,"adults","2027-01-22","2027-01-31","buy",52.3676,4.9041),
("hyrox-youngstars-amsterdam","HYROX Youngstars Amsterdam","Amsterdam","Pays-Bas",EU,"youngstars","2027-01-23","2027-01-24","buy",52.3676,4.9041),
("hyrox-verona","HYROX Verona","Vérone","Italie",EU,"adults","2027-01-28","2027-01-31","buy",45.4384,10.9916),
("hyrox-toulouse-s26-27","LUCIS HYROX Toulouse","Toulouse","France",EU,"adults","2027-02-03","2027-02-07","buy",43.6047,1.4442),
("hyrox-auckland","BYD HYROX Auckland","Auckland","Nouvelle-Zélande",AP,"adults","2027-02-04","2027-02-07","buy",-36.8485,174.7633),
("hyrox-bilbao","HYROX Bilbao","Bilbao","Espagne",EU,"adults","2027-02-06","2027-02-07","buy",43.2630,-2.9350),
("hyrox-youngstars-toulouse","HYROX Youngstars Toulouse","Toulouse","France",EU,"youngstars","2027-02-06","2027-02-07","buy",43.6047,1.4442),
("hyrox-bangkok","BYD HYROX Bangkok","Bangkok","Thaïlande",AP,"adults","2027-02-11","2027-02-14","buy",13.7563,100.5018),
("hyrox-chicago-26-27","Creapure HYROX Chicago","Chicago","États-Unis",NA,"adults","2027-02-11","2027-02-15","buy",41.8781,-87.6298),
("hyrox-basel","HYROX Basel","Bâle","Suisse",EU,"adults","2027-02-12","2027-02-14","buy",47.5596,7.5886),
("hyrox-katowice","DAFI HYROX Katowice","Katowice","Pologne",EU,"adults","2027-02-19","2027-02-21","buy",50.2649,19.0238),
("hyrox-vienna","INTERSPORT HYROX Vienna","Vienne","Autriche",EU,"adults","2027-02-19","2027-02-21","buy",48.2082,16.3738),
("hyrox-cancun","HYROX Cancun","Cancún","Mexique",NA,"adults","2027-02-19","2027-02-21","buy",21.1619,-86.8515),
("inbody-hyrox-phoenix-26-27","InBody HYROX Phoenix","Phoenix","États-Unis",NA,"adults","2027-02-25","2027-02-28","buy",33.4484,-112.0740),
("hyrox-mechelen","HYROX Mechelen","Malines","Belgique",EU,"adults","2027-03-03","2027-03-07","info",51.0259,4.4776),
("hyrox-hanoi","HYROX Hanoi","Hanoï","Viêt Nam",AP,"adults","2027-03-06","2027-03-07","info",21.0278,105.8342),
("hyrox-glasgow-2","HYROX Glasgow","Glasgow","Royaume-Uni",EU,"adults","2027-03-10","2027-03-14","buy",55.8642,-4.2518),
("hyrox-taipei","HYROX Taipei","Taipei","Taïwan",AP,"adults","2027-03-12","2027-03-14","buy",25.0330,121.5654),
("hyrox-las-vegas-26-27","HYROX Las Vegas","Las Vegas","États-Unis",NA,"adults","2027-03-12","2027-03-14","info",36.1699,-115.1398),
("hyrox-madrid","Fitness Park HYROX Madrid","Madrid","Espagne",EU,"adults","2027-03-17","2027-03-21","buy",40.4168,-3.7038),
("hyrox-guadalajara","HYROX Guadalajara","Guadalajara","Mexique",NA,"adults","2027-03-19","2027-03-21","info",20.6597,-103.3496),
("hyrox-buenos-aires","HYROX Buenos Aires","Buenos Aires","Argentine",SA,"adults","2027-03-20","2027-03-21","info",-34.6037,-58.3816),
("hyrox-copenhagen","BIOTHERM HYROX Copenhagen","Copenhague","Danemark",EU,"adults","2027-03-25","2027-03-28","info",55.6761,12.5683),
("sweat-pals-hyrox-miami-beach-26-27","Sweatpals HYROX Miami Beach","Miami Beach","États-Unis",NA,"adults","2027-03-26","2027-03-28","info",25.7907,-80.1300),
("virgin-active-hyrox-cape-town","Virgin Active HYROX Cape Town","Le Cap","Afrique du Sud",AF,"adults","2027-03-26","2027-03-28","info",-33.9249,18.4241),
("hyrox-youngstars-miami-beach","HYROX Youngstars Miami Beach","Miami Beach","États-Unis",NA,"youngstars","2027-03-27","2027-03-28","info",25.7907,-80.1300),
("hyrox-brisbane","BYD HYROX Brisbane","Brisbane","Australie",AP,"adults","2027-03-31","2027-04-05","buy",-27.4698,153.0251),
("hyrox-rotterdam","HYROX Rotterdam","Rotterdam","Pays-Bas",EU,"adults","2027-04-01","2027-04-04","info",51.9244,4.4777),
("hyrox-houston-26-27","Academy HYROX Houston","Houston","États-Unis",NA,"adults","2027-04-01","2027-04-04","info",29.7604,-95.3698),
("hyrox-bari","HYROX Bari","Bari","Italie",EU,"adults","2027-04-02","2027-04-04","info",41.1171,16.8719),
("hyrox-youngstars-houston","HYROX Youngstars Houston","Houston","États-Unis",NA,"youngstars","2027-04-03","2027-04-04","info",29.7604,-95.3698),
("hyrox-warsaw-26-27","Medicover Sport HYROX Warsaw","Varsovie","Pologne",EU,"adults","2027-04-07","2027-04-11","buy",52.2297,21.0122),
("hyrox-paris-grand-palais-s26-27","Maybelline HYROX Paris Grand Palais","Paris","France",EU,"adults","2027-04-08","2027-04-12","info",48.8566,2.3522),
("all-inclusive-fitness-hyrox-cologne","all inclusive Fitness HYROX Cologne","Cologne","Allemagne",EU,"adults","2027-04-08","2027-04-11","info",50.9375,6.9603),
("hyrox-malaga","HYROX Málaga","Malaga","Espagne",EU,"adults","2027-04-14","2027-04-18","info",36.7213,-4.4214),
("hyrox-nagoya","HYROX Nagoya","Nagoya","Japon",AP,"adults","2027-04-16","2027-04-18","info",35.1815,136.9066),
("hyrox-helsinki","HYROX Helsinki","Helsinki","Finlande",EU,"adults","2027-04-16","2027-04-18","buy",60.1699,24.9384),
("hyrox-monterrey","HYROX Monterrey","Monterrey","Mexique",NA,"adults","2027-04-16","2027-04-18","info",25.6866,-100.3161),
("hyrox-ottawa-26-27","HYROX Ottawa","Ottawa","Canada",NA,"adults","2027-04-21","2027-04-25","info",45.4215,-75.6972),
("factor_-hyrox-atlanta","Factor_ HYROX Atlanta","Atlanta","États-Unis",NA,"adults","2027-04-23","2027-04-25","info",33.7490,-84.3880),
("hyrox-youngstars-atlanta","HYROX Youngstars Atlanta","Atlanta","États-Unis",NA,"youngstars","2027-04-24","2027-04-25","info",33.7490,-84.3880),
("hyrox-krakow-26-27","HYROX Kraków","Cracovie","Pologne",EU,"adults","2027-05-07","2027-05-09","info",50.0647,19.9450),
("hyrox-lyon-s26-27","HYROX Lyon","Lyon","France",EU,"adults","2027-05-12","2027-05-16","info",45.7640,4.8357),
("hyrox-bengaluru","HYROX Bengaluru","Bangalore","Inde",AP,"adults","2027-05-12","2027-05-16","info",12.9716,77.5946),
("hyrox-incheon","BYD HYROX Incheon","Incheon","Corée du Sud",AP,"adults","2027-05-13","2027-05-16","info",37.4563,126.7052),
("hyrox-san-diego-26-27","EōS Fitness HYROX San Diego","San Diego","États-Unis",NA,"adults","2027-05-13","2027-05-16","info",32.7157,-117.1611),
("hyrox-cardiff-2","HYROX Cardiff","Cardiff","Royaume-Uni",EU,"adults","2027-05-20","2027-05-29","info",51.4816,-3.1791),
("hyrox-portland-26-27","HYROX Portland","Portland","États-Unis",NA,"adults","2027-05-21","2027-05-23","info",45.5152,-122.6784),
("cisalfa-hyrox-rimini","Cisalfa HYROX Rimini","Rimini","Italie",EU,"adults","2027-05-27","2027-05-30","info",44.0678,12.5695),
("hyrox-riga","HYROX Riga","Riga","Lettonie",EU,"adults","2027-05-28","2027-05-30","info",56.9496,24.1052),
("puma-hyrox-world-championships-hong-kong","PUMA HYROX World Championships Hong Kong","Hong Kong","Hong Kong",AP,"adults","2027-06-10","2027-06-13","info",22.3193,114.1694),
("hyrox-new-york","HYROX New York","New York","États-Unis",NA,"adults",None,None,"info",40.7128,-74.0060),
]

NOTES = {
    "hyrox-toulouse-s26-27": {"venue": "MEETT Parc des Expositions, Av. Concorde, 31840 Toulouse",
                              "ticket_info": {"fr": "Ouverture de la billetterie prochainement (liste d'attente)",
                                              "en": "Ticket sales opening soon (waitlist)",
                                              "de": "Ticketverkauf startet bald (Warteliste)"}},
    "hyrox-gujarat": {"geo_note": {"fr": "Position approximative (État du Gujarat)",
                                   "en": "Approximate location (Gujarat state)",
                                   "de": "Ungefähre Position (Bundesstaat Gujarat)"}},
    "puma-hyrox-world-championships-hong-kong": {"tags": ["championnat-du-monde"]},
}

races = []
for slug, name, city, country, cont, typ, start, end, cta, lat, lng in R:
    r = {
        "id": slug, "name": name, "city": city, "country": country,
        "brand": "hyrox", "continent": cont, "type": typ,
        "start": start, "end": end, "date_confirmed": start is not None,
        "status": "announced",
        "listing_cta": "buy_tickets" if cta == "buy" else "find_out_more",
        "url": f"https://hyrox.com/event/{slug}/",
        "lat": lat, "lng": lng,
    }
    r.update(NOTES.get(slug, {}))
    races.append(r)

# ---------- Courses habituelles, pas encore annoncées ----------
# Villes ayant accueilli une course depuis janvier 2026 sans édition annoncée pour la saison 2026/27.
# Sources : hyroxvault.com/events/2026 ; redbull.com (calendrier Hyrox) — recoupées le 15/10/2026.
# slug | ville | pays | continent | lat | lng | éditions passées [(début, fin, lieu)] | note
E = [
("st-gallen","St-Gall","Suisse",EU,47.4245,9.3767,[("2026-01-16","2026-01-18","OLMA Messen St. Gallen")],{"fr":"Bâle est annoncée en février 2027","en":"Basel is announced for February 2027","de":"Basel ist für Februar 2027 angekündigt"}),
("turin","Turin","Italie",EU,45.0703,7.6869,[("2026-01-30","2026-02-01","Oval Lingotto")],{"fr":"Vérone est annoncée à la même période (fin janvier 2027)","en":"Verona is announced for the same period (late January 2027)","de":"Verona ist für denselben Zeitraum angekündigt (Ende Januar 2027)"}),
("istanbul","Istanbul","Turquie",EU,41.0082,28.9784,[("2026-02-13","2026-02-14","Yeşilköy Istanbul Fuar Merkezi"),("2026-08-01","2026-08-02","Yeşilköy Istanbul Fuar Merkezi")],None),
("fortaleza","Fortaleza","Brésil",SA,-3.7319,-38.5267,[("2026-02-28","2026-02-28","Centro de Eventos do Ceará")],None),
("washington-dc","Washington","États-Unis",NA,38.9072,-77.0369,[("2026-03-07","2026-03-08","Walter E. Washington Convention Center"),("2026-09-03","2026-09-07","Walter E. Washington Convention Center")],None),
("beijing","Pékin","Chine",AP,39.9042,116.4074,[("2026-03-21","2026-03-22","China National Convention Center"),("2026-09-12","2026-09-13","China National Convention Center")],None),
("bologna","Bologne","Italie",EU,44.4949,11.3426,[("2026-04-04","2026-04-06","BolognaFiere")],None),
("wuhan","Wuhan","Chine",AP,30.5928,114.3055,[("2026-04-11","2026-04-11","Wuhan International Expo Center")],None),
("lisbon","Lisbonne","Portugal",EU,38.7223,-9.1393,[("2026-05-01","2026-05-03","FIL Lisbon")],None),
("heerenveen","Heerenveen","Pays-Bas",EU,52.9600,5.9200,[("2026-05-14","2026-05-17","Thialf Heerenveen")],None),
("puebla","Puebla","Mexique",NA,19.0414,-98.2063,[("2026-05-16","2026-05-17","Centro Expositor Puebla")],None),
("berlin","Berlin","Allemagne",EU,52.4730,13.4030,[("2026-05-22","2026-05-31","Airport Berlin Tempelhof")],None),
("jakarta","Jakarta","Indonésie",AP,-6.2088,106.8456,[("2026-06-27","2026-06-28","Jakarta Convention Center")],None),
("sydney","Sydney","Australie",AP,-33.8688,151.2093,[("2026-07-01","2026-07-05","ICC Sydney")],None),
("hangzhou","Hangzhou","Chine",AP,30.2741,120.1551,[("2026-07-04","2026-07-05","Hangzhou International Expo Centre")],None),
("delhi","Delhi","Inde",AP,28.6139,77.2090,[("2026-07-24","2026-07-26",None)],None),
("chengdu","Chengdu","Chine",AP,30.5728,104.0668,[("2026-08-01","2026-08-02","Century City New International Exhibition Center")],None),
("chiba","Chiba","Japon",AP,35.6480,140.0346,[("2026-08-07","2026-08-09","Makuhari Messe")],None),
("shenzhen","Shenzhen","Chine",AP,22.5431,114.0579,[("2026-08-15","2026-08-16","Shenzhen World Exhibition & Convention Center")],None),
("perth","Perth","Australie",AP,-31.9505,115.8605,[("2026-08-21","2026-08-23",None)],None),
("tenerife","Tenerife","Espagne",EU,28.4636,-16.2518,[("2026-09-04","2026-09-06","Recinto Ferial de Tenerife")],None),
("acapulco","Acapulco","Mexique",NA,16.8531,-99.8237,[("2026-09-05","2026-09-06","Forum Mundo Imperial")],None),
("athens","Athènes","Grèce",EU,37.9838,23.7275,[("2026-09-05","2026-09-06",None)],None),
("maastricht","Maastricht","Pays-Bas",EU,50.8514,5.6910,[("2026-09-17","2026-09-20","MECC Maastricht")],None),
("mumbai","Bombay","Inde",AP,19.0760,72.8777,[("2026-09-18","2026-09-20",None)],None),
("salt-lake-city","Salt Lake City","États-Unis",NA,40.7608,-111.8910,[("2026-09-18","2026-09-20","Salt Palace Convention Center")],None),
("izmir","Izmir","Turquie",EU,38.4237,27.1428,[("2026-09-19","2026-09-20",None)],None),
("rome","Rome","Italie",EU,41.9028,12.4964,[("2026-09-24","2026-09-27","Fiera di Roma")],None),
("oslo","Oslo","Norvège",EU,59.9139,10.7522,[("2026-09-25","2026-09-27","NOVA Spektrum")],None),
("bordeaux","Bordeaux","France",EU,44.8378,-0.5792,[("2026-09-30","2026-10-04","Parc des Expositions de Bordeaux")],None),
("karlsruhe","Karlsruhe","Allemagne",EU,49.0069,8.4037,[("2026-10-01","2026-10-04","Messe Karlsruhe")],None),
("toronto","Toronto","Canada",NA,43.6532,-79.3832,[("2026-10-01","2026-10-04",None)],None),
("boston","Boston","États-Unis",NA,42.3601,-71.0589,[("2026-10-08","2026-10-11","Boston Convention & Exhibition Center")],None),
("geneva","Genève","Suisse",EU,46.2044,6.1432,[("2026-10-09","2026-10-11","Palexpo")],None),
("gdansk","Gdańsk","Pologne",EU,54.3520,18.6466,[("2026-10-10","2026-10-11","AmberExpo")],None),
]

TODAY = "2026-10-15"
MOIS = ["janvier","février","mars","avril","mai","juin","juillet","août","septembre","octobre","novembre","décembre"]

def plus_one_year(iso):
    y, m, d = iso.split("-")
    return f"{int(y)+1}-{m}-{d}"

for slug, city, country, cont, lat, lng, editions, note in E:
    last = max(editions, key=lambda e: e[0])
    # prochaine date anniversaire après aujourd'hui, parmi les éditions passées
    nexts = sorted(plus_one_year(e[0]) for e in editions)
    nexts = [n for n in nexts if n > TODAY] or nexts
    usual = sorted({int(e[0][5:7]) for e in editions})
    r = {
        "id": f"expected-{slug}", "name": f"HYROX {city}", "city": city, "country": country,
        "brand": "hyrox", "continent": cont, "type": "adults",
        "start": None, "end": None, "date_confirmed": False,
        "status": "expected",
        "expected_month": nexts[0][:7],
        "usual_months": usual,
        "last_edition": {"start": last[0], "end": last[1], "venue": last[2]},
        "url": "https://hyrox.com/find-my-race/",
        "lat": lat, "lng": lng,
    }
    if note: r["note"] = note
    races.append(r)

# ---------- ATHX Games ----------
# Source : athxgames.com/events et /past-events, relevés le 17/10/2026.
# « Enter now » affiché = inscriptions ouvertes ; pas de bouton = infos à venir.
ATHX = "https://athxgames.com/events/"
# id | nom | ville | pays | continent | début | fin | cta | lieu | lat | lng | extra
RA = [
("01km0bfarc0dcs952s4rmtgd47","ATHX Houston 2026","Houston","États-Unis",NA,"2026-10-17","2026-10-17","info","Reliant Park",29.7604,-95.3698,{}),
("01k8b7nxgwcr70a86vqf2y6ck4","ATHX Amsterdam 2026","Amsterdam","Pays-Bas",EU,"2026-11-07","2026-11-07","buy","RAI Amsterdam",52.3676,4.9041,{}),
("01kxmxwwhpb0jatysf8kb8gz5a","ATHX Los Angeles 2026","Los Angeles","États-Unis",NA,"2026-11-07","2026-11-07","buy","Long Beach Convention & Entertainment Center",33.7701,-118.1937,{}),
("01kk1b7p4a1pzebw5dd7q2z7wn","ATHX Finals 2026","Lisbonne","Portugal",EU,"2026-11-27","2026-11-29","info","Lisbon Exhibition and Congress Centre",38.7223,-9.1393,{"tags":["finale"]}),
("01krwxxbqkjzzbhpdj52356qkc","ATHX London 2027","Londres","Royaume-Uni",EU,"2027-01-23","2027-01-24","buy","ExCeL London",51.5074,-0.1278,{}),
("01m3q7jv27nmxge7qrghrkb0m4","ATHX San Diego 2027","San Diego","États-Unis",NA,"2027-01-23","2027-01-23","buy","San Diego Convention Center",32.7157,-117.1611,{}),
("01m3q8sdq1s3qr7fsjbf2rg18c","ATHX Las Vegas 2027","Las Vegas","États-Unis",NA,"2027-02-06","2027-02-06","buy","Expo at World Market Center",36.1699,-115.1398,{"tags":["founders"]}),
("01krwy3qs5q0357mrpx9b4qxtf","ATHX Paris 2027","Paris","France",EU,"2027-02-13","2027-02-14","buy","Paris Event Centre",48.8566,2.3522,{}),
("01krwy548m3x7bt4j8bvvmr8j8","ATHX Valencia 2027","Valencia","Espagne",EU,"2027-02-20","2027-02-20","buy","Feria Valencia",39.4699,-0.3763,{}),
("01ktkx9y8tf4a4g88n2jrprvxb","ATHX Milan 2027","Milan","Italie",EU,"2027-03-06","2027-03-07","buy","Fiera Milano",45.4642,9.1900,{}),
("01m3qb3fstj70qb6kgdxspt43f","ATHX Denver 2027","Denver","États-Unis",NA,"2027-03-13","2027-03-13","buy","National Western Complex",39.7392,-104.9903,{"tags":["founders"]}),
("01krwy5v1j0w519tw157rjf94m","ATHX Brussels 2027","Bruxelles","Belgique",EU,"2027-03-20","2027-03-20","buy","Brussels Expo",50.8503,4.3517,{}),
("01krwy682mdagrw81v49eryjfh","ATHX St Gallen 2027","St-Gall","Suisse",EU,"2027-04-10","2027-04-10","buy","Olma Messen St. Gallen",47.4245,9.3767,{}),
("01krwy6n4pfbcrvdntsnxx1ve5","ATHX Stuttgart 2027","Stuttgart","Allemagne",EU,"2027-04-17","2027-04-17","buy","Messe Stuttgart",48.7758,9.1829,{}),
("01m52cq7h7hmngw4w6v1ptbfd9","ATHX Houston 2027","Houston","États-Unis",NA,"2027-04-17","2027-04-17","buy","Reliant Park",29.7604,-95.3698,{}),
("01krwy752qn8epq15qbfn1kjnm","ATHX Vienna 2027","Vienne","Autriche",EU,"2027-04-24","2027-04-24","buy","Marx Halle",48.2082,16.3738,{}),
("01krwy7hrp6bp8ndj7p1487n0n","ATHX Madrid 2027","Madrid","Espagne",EU,"2027-05-08","2027-05-09","buy","IFEMA Madrid",40.4168,-3.7038,{}),
("01krwy8bb5rcgrnwpbcczzbray","ATHX Frankfurt 2027","Francfort","Allemagne",EU,"2027-05-22","2027-05-22","buy","Messe Frankfurt",50.1109,8.6821,{}),
("01ktkxbvzg4bf5b0xp1vr4rgc9","ATHX Montpellier 2027","Montpellier","France",EU,"2027-05-28","2027-05-29","buy","Parc des Expositions & Sud de France Arena",43.6108,3.8767,{}),
("01krwy8tkc67qrvhyxrkf7rr2a","ATHX Glasgow 2027","Glasgow","Royaume-Uni",EU,"2027-06-05","2027-06-06","buy","Scottish Event Campus",55.8642,-4.2518,{}),
("01krwy9mpydvy1btj6mg0n24d3","ATHX Dublin 2027","Dublin","Irlande",EU,"2027-06-12","2027-06-13","buy","RDS Dublin",53.3498,-6.2603,{}),
("01m49ena5z6exns2wbwhz0as69","ATHX Miami 2027","Miami Beach","États-Unis",NA,"2027-06-12","2027-06-12","buy","Miami Beach Convention Center",25.7907,-80.1300,{}),
("01krwyacecyw2jbmn851f35kkt","ATHX Lisbon 2027","Lisbonne","Portugal",EU,"2027-06-26","2027-06-27","buy","FIL Lisbon",38.7223,-9.1393,{}),
("01m4r73y2nbndczzrhkh09xccc","ATHX Malmö 2027","Malmö","Suède",EU,"2027-07-31","2027-07-31","buy","Malmömässan",55.6050,13.0038,{}),
("01krwybw82cd8h9reednq08rdy","ATHX Berlin 2027","Berlin","Allemagne",EU,"2027-08-14","2027-08-15","buy","Arena Halle Berlin",52.4970,13.4540,{}),
("01m3qe0s9k2yzb4grc3qs0149m","ATHX Nashville 2027","Nashville","États-Unis",NA,"2027-08-14","2027-08-14","buy","The Fairgrounds Nashville",36.1627,-86.7816,{"tags":["founders"]}),
("01krwycnfs1czxhzqvvsqtcjhh","ATHX Birmingham 2027","Birmingham","Royaume-Uni",EU,"2027-08-20","2027-08-22","buy","NEC Birmingham",52.4862,-1.8904,{}),
("01krwydvc664nvf2am0tdtkscp","ATHX Hamburg 2027","Hambourg","Allemagne",EU,"2027-08-28","2027-08-28","buy","Hamburg Messe",53.5511,9.9937,{}),
("01m32wkpzn6npbb75agmenytbe","ATHX New York 2027","New York","États-Unis",NA,"2027-08-28","2027-08-28","buy","Javits Center",40.7128,-74.0060,{}),
("01m4r799gbhp53p6zjz8sayapk","ATHX Rome 2027","Rome","Italie",EU,"2027-09-04","2027-09-04","buy","Fiera di Roma",41.9028,12.4964,{}),
("01krwye8tdjj9gscaw7xht2sme","ATHX Marseille 2027","Marseille","France",EU,"2027-09-10","2027-09-11","buy","Marseille Chanot",43.2965,5.3698,{}),
("01m3qf0k52z2eq2s87gjn3ea61","ATHX Chicago 2027","Chicago","États-Unis",NA,"2027-09-11","2027-09-11","buy","Donald E. Stephens Convention Center (Rosemont)",41.8781,-87.6298,{"tags":["founders"]}),
("01krwyezkbkvf4rdk2em6nj7z4","ATHX Turin 2027","Turin","Italie",EU,"2027-09-25","2027-09-25","buy","Lingotto Fiere",45.0703,7.6869,{}),
("01krwyg5j85v7nrbwh5eak1tb9","ATHX Amsterdam 2027","Amsterdam","Pays-Bas",EU,"2027-10-02","2027-10-03","buy","RAI Amsterdam",52.3676,4.9041,{}),
("01krwyfbxhpxxdyn42cas8bcd1","ATHX Liverpool 2027","Liverpool","Royaume-Uni",EU,"2027-10-09","2027-10-10","buy","ACC Liverpool",53.4084,-2.9916,{}),
("01krwygz93demx24426v8p3xr5","ATHX Bilbao 2027","Bilbao","Espagne",EU,"2027-11-06","2027-11-06","buy","Bilbao Exhibition Centre",43.2630,-2.9350,{}),
]
for eid, name, city, country, cont, start, end, cta, venue, lat, lng, extra in RA:
    races.append({
        "id": f"athx-{eid}", "name": name, "city": city, "country": country,
        "brand": "athx", "continent": cont, "type": "adults",
        "start": start, "end": end, "date_confirmed": True, "status": "announced",
        "listing_cta": "buy_tickets" if cta == "buy" else "find_out_more",
        "url": ATHX + eid, "venue": venue, "lat": lat, "lng": lng, **extra,
    })

# ---------- DEKA (Spartan) ----------
# Source : spartan.com (sites US, UK, ES) « Find a race » filtré sur DEKA, relevés le 17/10/2026.
# Les sites DE, IT, FR et NL n'annonçaient aucune course DEKA. Statut d'inscription non relevé → « infos à venir ».
# id | nom | ville | pays | continent | début | fin | url | lat | lng | extra
RD = [
("atlanta-2026","DEKA FIT & Ultra Atlanta","Atlanta","États-Unis",NA,"2026-11-07","2026-11-08","https://www.spartan.com/en/race/detail/10979/overview",33.7490,-84.3880,{}),
("wc-2026","DEKA World Championship 2026","Fort Worth","États-Unis",NA,"2026-12-10","2026-12-13","https://www.spartan.com/en/races/deka-wc",32.7555,-97.3308,{"venue":"Fort Worth Convention Center","tags":["championnat-du-monde"]}),
("new-york-2027","DEKA FIT & Ultra New York","New York","États-Unis",NA,"2027-01-01","2027-01-31","https://www.spartan.com/en/race/detail/11416/overview",40.7128,-74.0060,{"note":{"fr":"Dates affichées : tout le mois de janvier 2027, à préciser","en":"Listed as the whole of January 2027, to be confirmed","de":"Angegeben: ganzer Januar 2027, noch zu bestätigen"}}),
("denver-2027","DEKA FIT & Ultra Denver","Denver","États-Unis",NA,"2027-03-27","2027-03-27","https://www.spartan.com/en/race/detail/11427/overview",39.7392,-104.9903,{}),
("sacramento-2027","DEKA FIT & Ultra Sacramento","Sacramento","États-Unis",NA,"2027-04-24","2027-04-25","https://www.spartan.com/en/race/detail/11428/overview",38.5816,-121.4944,{}),
("anaheim-2027","DEKA FIT & Ultra Anaheim","Anaheim","États-Unis",NA,"2027-05-08","2027-05-09","https://www.spartan.com/en/race/detail/11429/overview",33.8366,-117.9143,{}),
("washington-2027","DEKA FIT & Ultra Washington DC","Washington","États-Unis",NA,"2027-10-01","2027-10-03","https://www.spartan.com/en/race/detail/10206/overview",38.9072,-77.0369,{}),
("london-west-2026","London West DEKA Trifecta Weekend","Farnborough","Royaume-Uni",EU,"2026-11-28","2026-11-29","https://uk.spartan.com/en/race/detail/10454/overview",51.2869,-0.7526,{}),
("emea-2027","DEKA EMEA Championship 2027","Liverpool","Royaume-Uni",EU,"2027-05-28","2027-05-30","https://uk.spartan.com/en/race/detail/11460/overview",53.4084,-2.9916,{"venue":"Liverpool Waterfront","tags":["championnat"]}),
("east-midlands-2027","DEKA FIT East Midlands","Derby","Royaume-Uni",EU,"2027-09-11","2027-09-12","https://uk.spartan.com/en/races/derby",52.9225,-1.4746,{}),
("guadalajara-2026","DEKA Guadalajara","Guadalajara (ES)","Espagne",EU,"2026-10-24","2026-10-25","https://es.spartan.com/en/races/deka-guadalajara",40.6332,-3.1669,{}),
("alicante-2026","DEKA Alicante","Alicante","Espagne",EU,"2026-10-31","2026-11-01","https://es.spartan.com/en/races/deka-alicante",38.3452,-0.4810,{}),
("tenerife-2026","DEKA Tenerife","Tenerife","Espagne",EU,"2026-11-21","2026-11-22","https://es.spartan.com/en/races/deka-tenerife",28.4636,-16.2518,{}),
("torremolinos-2027","DEKA Torremolinos (Málaga)","Torremolinos","Espagne",EU,"2027-02-27","2027-02-28","https://es.spartan.com/en/races/deka-torremolinos",36.6218,-4.4998,{}),
("toledo-2027","DEKA Toledo","Tolède","Espagne",EU,"2027-03-06","2027-03-07","https://es.spartan.com/en/races/deka-toledo-2027",39.8628,-4.0273,{"venue":"Universidad de Castilla-La Mancha"}),
("barcelona-spring-2027","DEKA Barcelona Primavera","Barcelone","Espagne",EU,"2027-03-20","2027-03-21","https://es.spartan.com/en/races/deka-barcelona-primavera",41.3874,2.1686,{}),
("valencia-2027","DEKA Valencia","Valencia","Espagne",EU,"2027-04-03","2027-04-04","https://es.spartan.com/en/races/deka-valencia-2027",39.4699,-0.3763,{}),
("ibiza-2027","DEKA Ibiza","Ibiza","Espagne",EU,"2027-04-17","2027-04-18","https://es.spartan.com/en/races/deka-ibiza-2027",38.9067,1.4206,{"venue":"Sant Agustí des Vedrà"}),
("vigo-2027","DEKA Vigo","Vigo","Espagne",EU,"2027-06-26","2027-06-27","https://es.spartan.com/en/races/deka-vigo-2027",42.2406,-8.7207,{}),
("madrid-2027","DEKA Madrid","Madrid","Espagne",EU,"2027-07-10","2027-07-11","https://es.spartan.com/en/races/deka-madrid-2027",40.4168,-3.7038,{}),
("barcelona-autumn-2027","DEKA Barcelona Otoño","Barcelone","Espagne",EU,"2027-09-25","2027-09-26","https://es.spartan.com/en/races/deka-barcelona-otono-2027",41.3874,2.1686,{}),
]
for rid, name, city, country, cont, start, end, url, lat, lng, extra in RD:
    races.append({
        "id": f"deka-{rid}", "name": name, "city": city, "country": country,
        "brand": "deka", "continent": cont, "type": "adults",
        "start": start, "end": end, "date_confirmed": True, "status": "announced",
        "listing_cta": "find_out_more", "url": url, "lat": lat, "lng": lng, **extra,
    })

# ---------- ATHX habituelles, pas encore annoncées ----------
# Villes ATHX de 2026 absentes du calendrier 2026/27 (athxgames.com/past-events, 17/10/2026).
EA = [
("munich","Munich","Allemagne",EU,48.1351,11.5820,[("2026-02-07","2026-02-07","Messe München")],None),
("barcelona","Barcelone","Espagne",EU,41.3874,2.1686,[("2026-09-05","2026-09-05","Fira Barcelona")],None),
("copenhagen","Copenhague","Danemark",EU,55.6761,12.5683,[("2026-08-15","2026-08-15","Bella Center")],
 {"fr":"Malmö est annoncée à la même période (fin juillet 2027)","en":"Malmö is announced for the same period (late July 2027)","de":"Malmö ist für denselben Zeitraum angekündigt (Ende Juli 2027)"}),
]
for slug, city, country, cont, lat, lng, editions, note in EA:
    last = max(editions, key=lambda e: e[0])
    nexts = sorted(plus_one_year(e[0]) for e in editions)
    nexts = [n for n in nexts if n > TODAY] or nexts
    r = {
        "id": f"expected-athx-{slug}", "name": f"ATHX {city}", "city": city, "country": country,
        "brand": "athx", "continent": cont, "type": "adults",
        "start": None, "end": None, "date_confirmed": False, "status": "expected",
        "expected_month": nexts[0][:7],
        "usual_months": sorted({int(e[0][5:7]) for e in editions}),
        "last_edition": {"start": last[0], "end": last[1], "venue": last[2]},
        "url": "https://athxgames.com/events", "lat": lat, "lng": lng,
    }
    if note: r["note"] = note
    races.append(r)

# ---------- Traductions : villes (fr -> en, de) et codes pays ISO ----------
CITY = {
 "Valencia":("Valencia","Valencia"),"São Paulo":("São Paulo","São Paulo"),"Budapest":("Budapest","Budapest"),
 "Tampa":("Tampa","Tampa"),"Abu Dhabi":("Abu Dhabi","Abu Dhabi"),"Birmingham":("Birmingham","Birmingham"),
 "Hambourg":("Hamburg","Hamburg"),"Nice":("Nice","Nizza"),"Mexico":("Mexico City","Mexiko-Stadt"),
 "Shanghai":("Shanghai","Shanghai"),"Dublin":("Dublin","Dublin"),"Düsseldorf":("Düsseldorf","Düsseldorf"),
 "Barcelone":("Barcelona","Barcelona"),"Denver":("Denver","Denver"),"Séoul":("Seoul","Seoul"),
 "Le Caire":("Cairo","Kairo"),"Dallas":("Dallas","Dallas"),"Poznań":("Poznań","Posen"),
 "Canton":("Guangzhou","Guangzhou"),"Rio de Janeiro":("Rio de Janeiro","Rio de Janeiro"),
 "Singapour":("Singapore","Singapur"),"Johannesburg":("Johannesburg","Johannesburg"),"Utrecht":("Utrecht","Utrecht"),
 "Gujarat":("Gujarat","Gujarat"),"Dubaï":("Dubai","Dubai"),"Londres":("London","London"),"Anaheim":("Anaheim","Anaheim"),
 "Milan":("Milan","Mailand"),"Sanya":("Sanya","Sanya"),"Melbourne":("Melbourne","Melbourne"),"Nashville":("Nashville","Nashville"),
 "Stockholm":("Stockholm","Stockholm"),"Francfort":("Frankfurt","Frankfurt"),"Kuala Lumpur":("Kuala Lumpur","Kuala Lumpur"),
 "Paris":("Paris","Paris"),"Gand":("Ghent","Gent"),"Vancouver":("Vancouver","Vancouver"),"Helsinki":("Helsinki","Helsinki"),
 "Hong Kong":("Hong Kong","Hongkong"),"Noida":("Noida","Noida"),"Manchester":("Manchester","Manchester"),"Osaka":("Osaka","Osaka"),
 "Amsterdam":("Amsterdam","Amsterdam"),"Vérone":("Verona","Verona"),"Toulouse":("Toulouse","Toulouse"),"Auckland":("Auckland","Auckland"),
 "Bilbao":("Bilbao","Bilbao"),"Bangkok":("Bangkok","Bangkok"),"Chicago":("Chicago","Chicago"),"Bâle":("Basel","Basel"),
 "Katowice":("Katowice","Kattowitz"),"Vienne":("Vienna","Wien"),"Cancún":("Cancún","Cancún"),"Phoenix":("Phoenix","Phoenix"),
 "Malines":("Mechelen","Mecheln"),"Hanoï":("Hanoi","Hanoi"),"Glasgow":("Glasgow","Glasgow"),"Taipei":("Taipei","Taipeh"),
 "Las Vegas":("Las Vegas","Las Vegas"),"Madrid":("Madrid","Madrid"),"Guadalajara":("Guadalajara","Guadalajara"),
 "Buenos Aires":("Buenos Aires","Buenos Aires"),"Copenhague":("Copenhagen","Kopenhagen"),"Miami Beach":("Miami Beach","Miami Beach"),
 "Le Cap":("Cape Town","Kapstadt"),"Brisbane":("Brisbane","Brisbane"),"Rotterdam":("Rotterdam","Rotterdam"),"Houston":("Houston","Houston"),
 "Bari":("Bari","Bari"),"Varsovie":("Warsaw","Warschau"),"Cologne":("Cologne","Köln"),"Malaga":("Málaga","Málaga"),
 "Nagoya":("Nagoya","Nagoya"),"Monterrey":("Monterrey","Monterrey"),"Ottawa":("Ottawa","Ottawa"),"Atlanta":("Atlanta","Atlanta"),
 "Cracovie":("Kraków","Krakau"),"Lyon":("Lyon","Lyon"),"Bangalore":("Bengaluru","Bengaluru"),"Incheon":("Incheon","Incheon"),
 "San Diego":("San Diego","San Diego"),"Cardiff":("Cardiff","Cardiff"),"Portland":("Portland","Portland"),"Rimini":("Rimini","Rimini"),
 "Riga":("Riga","Riga"),"New York":("New York","New York"),
 "St-Gall":("St. Gallen","St. Gallen"),"Turin":("Turin","Turin"),"Istanbul":("Istanbul","Istanbul"),"Fortaleza":("Fortaleza","Fortaleza"),
 "Washington":("Washington, D.C.","Washington, D.C."),"Pékin":("Beijing","Peking"),"Bologne":("Bologna","Bologna"),"Wuhan":("Wuhan","Wuhan"),
 "Lisbonne":("Lisbon","Lissabon"),"Heerenveen":("Heerenveen","Heerenveen"),"Puebla":("Puebla","Puebla"),"Berlin":("Berlin","Berlin"),
 "Jakarta":("Jakarta","Jakarta"),"Sydney":("Sydney","Sydney"),"Hangzhou":("Hangzhou","Hangzhou"),"Delhi":("Delhi","Delhi"),
 "Chengdu":("Chengdu","Chengdu"),"Chiba":("Chiba","Chiba"),"Shenzhen":("Shenzhen","Shenzhen"),"Perth":("Perth","Perth"),
 "Tenerife":("Tenerife","Teneriffa"),"Acapulco":("Acapulco","Acapulco"),"Athènes":("Athens","Athen"),"Maastricht":("Maastricht","Maastricht"),
 "Bombay":("Mumbai","Mumbai"),"Salt Lake City":("Salt Lake City","Salt Lake City"),"Izmir":("Izmir","Izmir"),"Rome":("Rome","Rom"),
 "Oslo":("Oslo","Oslo"),"Bordeaux":("Bordeaux","Bordeaux"),"Karlsruhe":("Karlsruhe","Karlsruhe"),"Toronto":("Toronto","Toronto"),
 "Boston":("Boston","Boston"),"Genève":("Geneva","Genf"),"Gdańsk":("Gdańsk","Danzig"),
}
CITY.update({
 "Los Angeles":("Los Angeles","Los Angeles"),"Bruxelles":("Brussels","Brüssel"),"Stuttgart":("Stuttgart","Stuttgart"),
 "Montpellier":("Montpellier","Montpellier"),"Malmö":("Malmö","Malmö"),"Marseille":("Marseille","Marseille"),
 "Liverpool":("Liverpool","Liverpool"),"Munich":("Munich","München"),"Fort Worth":("Fort Worth","Fort Worth"),
 "Sacramento":("Sacramento","Sacramento"),"Farnborough":("Farnborough","Farnborough"),"Derby":("Derby","Derby"),
 "Guadalajara (ES)":("Guadalajara (Spain)","Guadalajara (Spanien)"),"Alicante":("Alicante","Alicante"),
 "Torremolinos":("Torremolinos","Torremolinos"),"Tolède":("Toledo","Toledo"),"Ibiza":("Ibiza","Ibiza"),"Vigo":("Vigo","Vigo"),
})
CC = {
 "Espagne":"ES","Brésil":"BR","Hongrie":"HU","États-Unis":"US","Émirats arabes unis":"AE","Royaume-Uni":"GB","Allemagne":"DE",
 "France":"FR","Mexique":"MX","Chine":"CN","Irlande":"IE","Corée du Sud":"KR","Égypte":"EG","Pologne":"PL","Singapour":"SG",
 "Afrique du Sud":"ZA","Pays-Bas":"NL","Inde":"IN","Italie":"IT","Australie":"AU","Suède":"SE","Malaisie":"MY","Belgique":"BE",
 "Canada":"CA","Finlande":"FI","Hong Kong":"HK","Japon":"JP","Nouvelle-Zélande":"NZ","Thaïlande":"TH","Suisse":"CH","Autriche":"AT",
 "Viêt Nam":"VN","Taïwan":"TW","Argentine":"AR","Danemark":"DK","Lettonie":"LV","Turquie":"TR","Portugal":"PT","Indonésie":"ID",
 "Grèce":"GR","Norvège":"NO",
}
for r in races:
    fr = r["city"]
    en, de = CITY[fr]
    r["city"] = {"fr": fr, "en": en, "de": de}
    r["cc"] = CC[r.pop("country")]

ids = [r["id"] for r in races]
assert len(ids) == len(set(ids)), "doublon"

out = {
    "meta": {
        "source": "hyrox.com, athxgames.com, spartan.com",
        "collected_on": "2026-10-17",
        "version": 4,
        "brands": {"hyrox": "https://hyrox.com/find-my-race/", "athx": "https://athxgames.com/events", "deka": "https://www.spartan.com/en/deka"},
        "count": len(races),
        "notes": "status=announced : courses officiellement annoncées ; status=expected : villes ayant accueilli une course en 2026 sans édition annoncée. Coordonnées au niveau de la ville. "
                 "listing_cta = bouton affiché sur la liste officielle (indicatif, à vérifier sur la fiche).",
    },
    "races": races,
}
data_dir = os.path.join(ROOT, "data")
# Depuis la v5, data/races.json est tenu à jour par tools/update_races.py : ce script ne sert plus qu'à
# reconstruire la base initiale. On refuse d'écraser une base mise à jour sans --force.
import sys
_existing = os.path.join(data_dir, "races.json")
if os.path.exists(_existing) and "--force" not in sys.argv:
    try:
        if json.load(open(_existing, encoding="utf-8")).get("meta", {}).get("generator") == "update_races":
            sys.exit("data/races.json is maintained by tools/update_races.py; rerun with --force to rebuild it from scratch.")
    except ValueError:
        pass
os.makedirs(data_dir, exist_ok=True)
with open(os.path.join(data_dir, "races.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
# Copie JS : permet d'ouvrir index.html par double-clic (file://), où fetch() est bloqué
with open(os.path.join(data_dir, "races.js"), "w", encoding="utf-8") as f:
    f.write("// Fichier généré par tools/build_races.py — ne pas modifier à la main\n")
    f.write("window.RACES_DATA = " + json.dumps(out, ensure_ascii=False) + ";\n")
print(len(races), "courses")
from collections import Counter
print(Counter(r["continent"] for r in races), Counter(r["status"] for r in races))
