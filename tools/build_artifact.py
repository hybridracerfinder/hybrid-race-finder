"""Assemble une version en un seul fichier de la page (pour l'héberger comme page Claude).
Les CSS de Leaflet sont intégrées, le fond de carte est vectoriel (data/world-110m.json)
car les pages hébergées ne peuvent pas charger d'images externes.
Usage : python tools/build_artifact.py <leaflet_dist> <markercluster_dist> <sortie.html>"""
import pathlib, sys

P = pathlib.Path(__file__).resolve().parent.parent
leaflet_dist, cluster_dist, out_path = map(pathlib.Path, sys.argv[1:4])
html = (P / "index.html").read_text(encoding="utf-8")
body = html[html.index("<header"):html.index("<script")]
css = "\n".join([
    (leaflet_dist / "leaflet.css").read_text(),
    (cluster_dist / "MarkerCluster.css").read_text(),
    (P / "assets/style.css").read_text(encoding="utf-8"),
    ":root { color-scheme: dark; } body { background: var(--bg); }",
])
out = f'''<title>Hybrid Race Finder</title>
<meta name="description" content="Carte non officielle des courses hybrides HYROX, ATHX et DEKA.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700&family=Barlow:wght@400;500;600&display=swap" rel="stylesheet">
<style>
{css}
</style>
{body}
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script src="https://unpkg.com/leaflet.markercluster@1.5.3/dist/leaflet.markercluster.js"></script>
<script>
{(P / "data/races.js").read_text(encoding="utf-8")}
window.WORLD_SHAPES = {(P / "data/world-110m.json").read_text()};
</script>
<script>
{(P / "assets/i18n.js").read_text(encoding="utf-8")}
</script>
<script>
{(P / "assets/app.js").read_text(encoding="utf-8")}
</script>
'''
out_path.write_text(out, encoding="utf-8")
print(f"{out_path} : {len(out.encode()) // 1024} KB")
