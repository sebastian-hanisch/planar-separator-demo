"""Konstanten: Regler-Grenzen, Rechengrenzen, feste Annahmen, Farben und Presets."""

N_MIN, N_MAX, DEFAULT_N = 16, 300, 100                   # Knoten; der Fundamentalkreis ist O(Kandidaten · n), bei n = 300 etwa 0,3 s
SEED_MAX, DEFAULT_SEED = 999999, 100
SWEEP_SEEDS = tuple(range(100, 106))                     # feste Karten für alle Messreihen (6): nie ein einzelner Seed als Befund

NET_TYPES = {
    "delaunay": "Karte (Delaunay-Triangulierung)",
    "grid": "Raster mit Diagonalen",
    "lattice": "Gitter (ohne Diagonalen)",
    "random": "Zufallsgraph (nicht planar)",
}
DEFAULT_NET = "delaunay"
NET_HELP = (
    "Karte: zufällige Standorte mit allen Kanten ihrer Delaunay-Triangulierung (planar); für den Fundamentalkreis ist sie durch einen Fächer von einer Hüllenecke aus zu einer vollständigen Triangulierung ergänzt. "
    "Raster mit Diagonalen und Gitter ohne: k × k Knoten (n wird auf ein Quadrat gerundet). "
    "Zufallsgraph: jeder Knoten hat im Mittel Grad 3, ohne Rücksicht auf die Lage; es zählt die größte Komponente. Er ist nicht planar und hat keine kleinen Trennmengen."
)

METHODS = {
    "level": "BFS-Schicht",
    "cycle": "Fundamentalkreis",
    "geometric": "Geometrischer Schnitt (Median + König)",
}
DEFAULT_METHOD = "cycle"
METHOD_HELP = (
    "BFS-Schicht: die kleinste Schicht einer Breitensuche, deren Entfernung den Graphen ausgewogen teilt. "
    "Fundamentalkreis: der kürzeste Kreis aus einer Kante außerhalb eines BFS-Baums und den Baumwegen, der ausgewogen teilt (die Konstruktion hinter dem Satz von Lipton und Tarjan). "
    "Geometrischer Schnitt: am Median der längeren Achse teilen, Trennmenge = kleinste Überdeckung der Schnittkanten (Satz von König)."
)

# Rechengrenzen und Messreihen
SCALING_NS = (100, 300, 1000)        # n der Größenreihe (n = 1000 nur auf Klick, der Kreis braucht dort rund 4 Sekunden je Karte)
SCALING_LIVE_NS = (100, 300)
ND_GRID_KS = (8, 12, 16, 24)          # reine Gitter der Nested-Dissection-Reihe
ND_MAP_NS = (100, 200, 300)           # Karten der Nested-Dissection-Reihe
ND_RANDOM_N = 300
ND_LEAF = 4                           # Stücke bis zu so vielen Knoten werden nach Mindestgrad geordnet
OTHER_KS = (10, 20, 30)               # Gitter und Raster der Gegenprobe
OTHER_RANDOM_NS = (100, 200, 400)
TORONTO_CROSS = None

COLOR_SEP = "#c0504d"        # Trennmenge
COLOR_SIDES = ("#4c78a8", "#e0a030", "#2F6B65", "#8c6bb1", "#6baed6")
COLOR_EDGE = "rgba(150,150,150,0.45)"
COLOR_CYCLE = "#c0504d"
COLOR_FAN = "rgba(150,150,150,0.25)"
COLOR_PALETTE = ("#4c78a8", "#e0a030", "#2F6B65", "#c0504d", "#8c6bb1", "#6baed6")

PRESETS = {
    "Lehrbeispiel: eine Karte": {"net": "delaunay", "n": 100, "seed": 100, "method": "cycle"},
    "Die Schicht ist größer": {"net": "delaunay", "n": 300, "seed": 101, "method": "level"},
    "Der Schnitt am Median": {"net": "delaunay", "n": 300, "seed": 101, "method": "geometric"},
    "Gitter: Trennmenge gleich k": {"net": "lattice", "n": 144, "seed": 100, "method": "geometric"},
    "Zufallsgraph: keine kleine Trennmenge": {"net": "random", "n": 300, "seed": 100, "method": "level"},
}
PRESET_HELP = {
    "Lehrbeispiel: eine Karte": "100 Standorte, ein Fundamentalkreis als Trennmenge: etwa √n Knoten, nach dem Entfernen ist jede Komponente höchstens zwei Drittel groß.",
    "Die Schicht ist größer": "Dieselbe Art Karte mit 300 Standorten und der BFS-Schicht: größer als der Fundamentalkreis, und das Verhältnis zu √n wächst mit n.",
    "Der Schnitt am Median": "Dieselbe Karte, geteilt am Median der längeren Achse; die Trennmenge ist etwa so groß wie √n.",
    "Gitter: Trennmenge gleich k": "Ein reines 12 × 12-Gitter: Eine Reihe von Knoten trennt es, die Trennmenge hat k = 12 Knoten.",
    "Zufallsgraph: keine kleine Trennmenge": "Ein Zufallsgraph mit Grad 3 hat keine kleine Trennmenge: ein fester Anteil der Knoten wird gebraucht, nicht √n; es fehlt die Planarität.",
}
