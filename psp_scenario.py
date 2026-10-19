"""Szenario: Karten (Delaunay mit Fächer), Gitter, Raster mit Diagonalen, Zufallsgraphen und die Toronto-Karte.

Ein Graph ist eine Kantenliste über den Knoten 0 bis n − 1 (ungerichtet, einfach, jede Kante als (u, v) mit u < v) und eine Lage der Knoten. Die Lage braucht nur der
geometrische Schnitt und die Zeichnung."""

import json
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np

DATA = Path(__file__).resolve().parent / "data"


@dataclass(frozen=True)
class Instance:
    """n Knoten, Kanten, Lage, Name; `fan` sind zusätzliche Kanten, die eine Triangulierung vervollständigen (nur für die Suche des Fundamentalkreises)."""

    n: int
    edges: tuple[tuple[int, int], ...]
    pos: tuple[tuple[float, float], ...]
    name: str = ""
    fan: tuple[tuple[int, int], ...] = ()
    planar: bool = True

    @property
    def m(self) -> int:
        return len(self.edges)


def normalize_edges(edges) -> tuple[tuple[int, int], ...]:
    return tuple(sorted({(min(u, v), max(u, v)) for u, v in edges if u != v}))


def _delaunay(points: np.ndarray):
    from scipy.spatial import Delaunay

    tri = Delaunay(points)
    found = set()
    for simplex in tri.simplices:
        a, b, c = (int(x) for x in simplex)
        found.update({(min(a, b), max(a, b)), (min(b, c), max(b, c)), (min(a, c), max(a, c))})
    hull = list(dict.fromkeys(int(x) for x in tri.convex_hull.flatten()))
    centre = points.mean(axis=0)
    hull.sort(key=lambda i: (math.atan2(points[i][1] - centre[1], points[i][0] - centre[0]), i))
    return sorted(found), hull


def fan_edges(hull: list[int], edges) -> tuple[tuple[int, int], ...]:
    """Kanten von der ersten Hüllenecke zu allen weiteren Hüllenecken, die noch fehlen: machen die Außenfläche zu Dreiecken."""
    have = set(edges)
    extra = []
    for h in hull[2:-1]:
        e = (min(hull[0], h), max(hull[0], h))
        if e not in have:
            extra.append(e)
    return tuple(sorted(extra))


def make_delaunay(n: int, seed: int) -> Instance:
    """Zufällige Standorte im Einheitsquadrat, alle Kanten der Delaunay-Triangulierung; dazu der Fächer, der sie vollständig triangulierte."""
    rng = np.random.default_rng(seed)
    points = rng.random((n, 2))
    edges, hull = _delaunay(points)
    pos = tuple((round(float(x), 4), round(float(y), 4)) for x, y in points)
    return Instance(n, normalize_edges(edges), pos, "Karte", fan_edges(hull, edges))


def lattice_side(n: int) -> int:
    return max(3, round(math.sqrt(n)))


def make_lattice(n: int, diagonals: bool = False) -> Instance:
    """k × k Gitter (k = Wurzel aus n, gerundet), auf Wunsch mit einer Diagonale in jeder Zelle."""
    k = lattice_side(n)
    edges = [(r * k + c, r * k + c + 1) for r in range(k) for c in range(k - 1)] + [(r * k + c, (r + 1) * k + c) for r in range(k - 1) for c in range(k)]
    if diagonals:
        edges += [(r * k + c, (r + 1) * k + c + 1) for r in range(k - 1) for c in range(k - 1)]
    pos = tuple((float(c), float(-r)) for r in range(k) for c in range(k))
    return Instance(k * k, normalize_edges(edges), pos, "Raster mit Diagonalen" if diagonals else "Gitter")


def circle_layout(n: int) -> tuple[tuple[float, float], ...]:
    return tuple((round(math.cos(2 * math.pi * i / n), 4), round(math.sin(2 * math.pi * i / n), 4)) for i in range(n))


def make_random(n: int, seed: int) -> Instance:
    """Zufallsgraph mit mittlerem Grad 3 (jedes Paar mit Wahrscheinlichkeit 3/n); behalten wird die größte Komponente, die Knoten werden neu nummeriert; Kreis-Layout."""
    rng = np.random.default_rng(seed)
    upper = rng.random((n, n)) < 3 / n
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n) if upper[u, v]]
    adj = [set() for _ in range(n)]
    for u, v in pairs:
        adj[u].add(v)
        adj[v].add(u)
    seen: set[int] = set()
    best: list[int] = []
    for s in range(n):
        if s in seen:
            continue
        comp, stack = [s], [s]
        seen.add(s)
        while stack:
            x = stack.pop()
            for y in adj[x]:
                if y not in seen:
                    seen.add(y)
                    comp.append(y)
                    stack.append(y)
        if len(comp) > len(best):
            best = comp
    index = {v: i for i, v in enumerate(sorted(best))}
    kept = [(index[u], index[v]) for u, v in pairs if u in index and v in index]
    return Instance(len(best), normalize_edges(kept), circle_layout(len(best)), "Zufallsgraph", (), False)


def make_instance(net: str, n: int, seed: int) -> Instance:
    """Deterministisch aus den Reglern: gleiche Eingabe, gleiche Instanz."""
    if net == "delaunay":
        return make_delaunay(n, seed)
    if net == "grid":
        return make_lattice(n, True)
    if net == "lattice":
        return make_lattice(n, False)
    if net == "random":
        return make_random(n, seed)
    raise ValueError(f"unbekannter Netztyp: {net}")


def load_toronto() -> Instance:
    """Straßenkarte aus OpenStreetMap (ODbL, Auszug aus bfs-demo): Kanten ungerichtet vereinigt, die größte Komponente."""
    payload = json.loads((DATA / "toronto_campus.json").read_text(encoding="utf-8"))
    pos = [(float(x), float(y)) for x, y in payload["nodes_xy_m"]]
    edges = normalize_edges((u, v) for u, v, _ in payload["arcs"])
    adj = [set() for _ in pos]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    seen = {0}
    stack = [0]
    while stack:
        x = stack.pop()
        for y in adj[x]:
            if y not in seen:
                seen.add(y)
                stack.append(y)
    if len(seen) != len(pos):
        raise ValueError("Toronto-Auszug nicht zusammenhängend")
    return Instance(len(pos), edges, tuple(pos), "Toronto-Karte", (), False)
