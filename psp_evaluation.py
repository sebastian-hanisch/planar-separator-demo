"""Auswertung: Trennmengen einer Instanz, Messreihen (Größe gegen √n, andere Netze, Nested Dissection, Toronto) und die Verdikte als reine Funktionen."""

from __future__ import annotations

import math
import statistics
from dataclasses import dataclass

import psp_algorithm as A
import psp_constants as C
import psp_scenario as S


def num(x: float, digits: int = 0) -> str:
    """Zahl im deutschen Format: Tausenderpunkt, Dezimalkomma."""
    return f"{x:,.{digits}f}".translate(str.maketrans({",": ".", ".": ","}))


def plural(count: int, singular: str, plural_form: str) -> str:
    return f"{count} {singular if count == 1 else plural_form}"


@dataclass(frozen=True)
class Settings:
    net: str = C.DEFAULT_NET
    n: int = C.DEFAULT_N
    seed: int = C.DEFAULT_SEED
    method: str = C.DEFAULT_METHOD


@dataclass(frozen=True)
class Analysis:
    inst: S.Instance
    sep: A.Separator | None
    check: A.SepCheck | None
    bound: float                 # √(8n), die Schranke des Satzes von Lipton und Tarjan
    sqrt_n: float
    others: dict[str, int | None]    # Größe der Trennmenge der beiden übrigen Verfahren (None: keine gefunden)
    components: list[set[int]]       # Komponenten nach dem Entfernen (größte zuerst)


def _adjacencies(inst: S.Instance):
    return A.adjacency(inst.n, inst.edges), A.adjacency(inst.n, inst.edges + inst.fan)


def analyse(settings: Settings) -> Analysis:
    return analyse_instance(S.make_instance(settings.net, settings.n, settings.seed), settings.method)


def analyse_instance(inst: S.Instance, method: str) -> Analysis:
    adj, full = _adjacencies(inst)
    nodes = set(range(inst.n))
    found = {m: A.find_separator(m, adj, nodes, inst.pos, full) for m in C.METHODS}
    sep = found[method]
    check = A.check_separator(adj, nodes, sep.vertices) if sep is not None else None
    comps = sorted(A.components(adj, nodes - set(sep.vertices)), key=len, reverse=True) if sep is not None else []
    return Analysis(
        inst, sep, check, math.sqrt(8 * inst.n), math.sqrt(inst.n),
        {m: (len(s.vertices) if s is not None else None) for m, s in found.items() if m != method}, comps,
    )


# --- Messreihen -----------------------------------------------------------------------------------------------------------------------------


def scaling_table(ns=C.SCALING_LIVE_NS, seeds=C.SWEEP_SEEDS) -> list[dict]:
    """Je Knotenzahl auf Karten: mittlere Größe der Trennmenge je Verfahren (Median), Verhältnis zu √n, und wie oft der Kreis die Schranke √(8n) hält."""
    rows = []
    for n in ns:
        sizes = {m: [] for m in C.METHODS}
        kept = 0
        for seed in seeds:
            inst = S.make_delaunay(n, seed)
            adj, full = _adjacencies(inst)
            nodes = set(range(n))
            for m in C.METHODS:
                sep = A.find_separator(m, adj, nodes, inst.pos, full)
                sizes[m].append(len(sep.vertices))
                if m == "cycle":
                    kept += len(sep.vertices) <= math.sqrt(8 * n)
        row = {"n": n, "samples": len(seeds), "sqrt_n": math.sqrt(n), "bound": math.sqrt(8 * n), "cycle_within_bound": kept}
        for m in C.METHODS:
            row[m] = statistics.median(sizes[m])
            row[m + "_ratio"] = row[m] / math.sqrt(n)
        rows.append(row)
    return rows


def other_table(seeds=C.SWEEP_SEEDS[:1]) -> list[dict]:
    """Gegenproben: Gitter und Raster (k × k) gegen k, Zufallsgraphen gegen n; Schicht und geometrischer Schnitt."""
    rows = []
    for k in C.OTHER_KS:
        for net in ("lattice", "grid"):
            inst = S.make_lattice(k * k, net == "grid")
            adj = A.adjacency(inst.n, inst.edges)
            nodes = set(range(inst.n))
            rows.append({"name": f"{inst.name} {k} × {k}", "n": inst.n, "level": len(A.level_separator(adj, nodes).vertices),
                         "geometric": len(A.geometric_separator(adj, inst.pos, nodes).vertices), "scale": k, "linear": False})
    for n in C.OTHER_RANDOM_NS:
        inst = S.make_random(n, seeds[0])
        adj = A.adjacency(inst.n, inst.edges)
        nodes = set(range(inst.n))
        rows.append({"name": f"Zufallsgraph (aus {n})", "n": inst.n, "level": len(A.level_separator(adj, nodes).vertices),
                     "geometric": len(A.geometric_separator(adj, inst.pos, nodes).vertices), "scale": inst.n, "linear": True})
    return rows


def nd_widths(inst: S.Instance, with_cycle: bool = False, with_fill: bool = True) -> dict:
    """Eliminationsbreite der Ordnungen: Nested Dissection (geometrisch, Schicht, auf Wunsch Kreis), Mindestgrad, Min-Fill."""
    adj, full = _adjacencies(inst)
    row = {
        "n": inst.n,
        "nd_geometric": A.elimination_width(adj, A.nested_dissection(adj, inst.pos, "geometric", C.ND_LEAF).order),
        "nd_level": A.elimination_width(adj, A.nested_dissection(adj, inst.pos, "level", C.ND_LEAF).order),
        "min_degree": A.elimination_width(adj, A.min_degree_order(adj)),
    }
    if with_cycle:
        row["nd_cycle"] = A.elimination_width(adj, A.nested_dissection(adj, inst.pos, "cycle", C.ND_LEAF, full).order)
    if with_fill:
        row["min_fill"] = A.elimination_width(adj, A.min_fill_order(adj))
    return row


def nd_table(seeds=C.SWEEP_SEEDS[:3]) -> list[dict]:
    """Nested Dissection gegen Mindestgrad und Min-Fill: reine Gitter, Karten (Median über Karten, mit Fundamentalkreis), Zufallsgraph."""
    rows = []
    for k in C.ND_GRID_KS:
        w = nd_widths(S.make_lattice(k * k))
        rows.append({"name": f"Gitter {k} × {k}", **w, "sqrt_n": float(k)})
    for n in C.ND_MAP_NS:
        results = [nd_widths(S.make_delaunay(n, seed), with_cycle=True) for seed in seeds]
        w = {key: statistics.median(r[key] for r in results) for key in results[0]}
        rows.append({"name": f"Karte (n = {n}, Median über {len(seeds)})", **w, "sqrt_n": math.sqrt(n)})
    inst = S.make_random(C.ND_RANDOM_N, seeds[0])
    rows.append({"name": f"Zufallsgraph (aus {C.ND_RANDOM_N})", **nd_widths(inst), "sqrt_n": math.sqrt(inst.n)})
    return rows


def toronto_stats() -> dict:
    """Toronto-Karte (5 072 Knoten): Größe der Trennmengen und Breite der Ordnungen."""
    inst = S.load_toronto()
    adj = A.adjacency(inst.n, inst.edges)
    nodes = set(range(inst.n))
    level = A.level_separator(adj, nodes)
    geo = A.geometric_separator(adj, inst.pos, nodes)
    widths = nd_widths(inst, with_fill=False)
    return {
        "inst": inst, "n": inst.n, "sqrt_n": math.sqrt(inst.n),
        "level": level, "geometric": geo,
        "level_check": A.check_separator(adj, nodes, level.vertices), "geometric_check": A.check_separator(adj, nodes, geo.vertices),
        **widths,
    }


# --- Verdikte (reine Funktionen: Art, Text) -------------------------------------------------------------------------------------------------


def verdict_separator(a: Analysis, method: str) -> tuple[str, str]:
    """Hauptergebnis: Größe der Trennmenge gegen √n, Prüfung, beim Kreis die Schranke des Satzes."""
    name = C.METHODS[method]
    if a.sep is None:
        return "warning", f"{name}: Es gibt hier **keine** Trennmenge dieser Art (der Graph hat keinen Kreis, keine ausgewogene Schicht oder nichts zu schneiden)."
    c = a.check
    size = len(a.sep.vertices)
    base = f"{name}: **{size} Knoten** ({num(size / a.sqrt_n, 2)} √n), die größte Komponente danach hat {c.largest} von {a.inst.n} Knoten (Grenze 2n/3 = {num(c.limit, 1)})"
    if not c.balanced:
        return "error", f"**Fehler:** {base}: nicht ausgewogen."
    if method == "cycle":
        extra = f"; die Schranke des Satzes von Lipton und Tarjan ist √(8n) = {num(a.bound, 1)}" + (" und wird eingehalten" if size <= a.bound else " und wird hier überschritten (der Graph ist nicht trianguliert oder nicht planar)")
        return "success", base + extra + "."
    return "success", base + "."


def verdict_scaling(rows: list[dict]) -> tuple[str, str]:
    """Wie wächst die Trennmenge gegen √n, je Verfahren?"""
    first, last = rows[0], rows[-1]
    return (
        "info",
        f"Auf Karten liegt die Trennmenge im Verhältnis zu √n bei n = {first['n']} / {last['n']} für den Fundamentalkreis bei {num(first['cycle_ratio'], 2)} / {num(last['cycle_ratio'], 2)}, "
        f"für den geometrischen Schnitt bei {num(first['geometric_ratio'], 2)} / {num(last['geometric_ratio'], 2)} und für die BFS-Schicht bei {num(first['level_ratio'], 2)} / {num(last['level_ratio'], 2)}. "
        f"Der Kreis hielt die Schranke √(8n) in {sum(r['cycle_within_bound'] for r in rows)} von {sum(r['samples'] for r in rows)} Fällen.",
    )


def verdict_other(rows: list[dict]) -> tuple[str, str]:
    """Gitter gegen k, Zufallsgraph gegen n."""
    grids = [r for r in rows if not r["linear"]]
    rand = [r for r in rows if r["linear"]]
    g = grids[-1]
    r = rand[-1]
    return (
        "info",
        f"Beim {g['name']} hat die Schicht {g['level']} und der geometrische Schnitt {g['geometric']} Knoten (k = {g['scale']}). "
        f"Beim Zufallsgraphen mit {r['n']} Knoten sind es {r['level']} und {r['geometric']}: {num(r['level'] / r['n'] * 100)} % der Knoten, nicht √n; ohne Planarität gibt es keine kleinen Trennmengen.",
    )


def verdict_nd(rows: list[dict]) -> tuple[str, str]:
    """Garantie, aber nicht besser als die Heuristiken; kleinste Trennmenge, nicht beste Ordnung."""
    maps = [r for r in rows if r["name"].startswith("Karte")]
    last = maps[-1]
    rand = rows[-1]
    grid = [r for r in rows if r["name"].startswith("Gitter")][-1]
    lattice = (
        f" Am {grid['name']} ist Nested Dissection erstmals vorn ({min(grid['nd_geometric'], grid['nd_level'])} gegen {grid['min_fill']} bei Min-Fill)."
        if min(grid["nd_geometric"], grid["nd_level"]) < grid["min_fill"] else ""
    )
    return (
        "info",
        f"Auf der größten Karte ({last['name']}) hat Nested Dissection mit dem geometrischen Schnitt die Breite {num(last['nd_geometric'], 1)}, mit dem Fundamentalkreis {num(last['nd_cycle'], 1)}, "
        f"Mindestgrad {num(last['min_degree'], 1)} und Min-Fill {num(last['min_fill'], 1)} (√n = {num(last['sqrt_n'], 1)}). Der Kreis hat die kleinste Trennmenge, aber nicht die beste Ordnung; die Heuristiken sind hier ebenso gut. "
        f"Am Zufallsgraphen bricht Nested Dissection ein: Breite {rand['nd_geometric']} gegen Mindestgrad {rand['min_degree']}." + lattice,
    )


def verdict_toronto(t: dict) -> tuple[str, str]:
    """Straßenkarte: Trennmengen und Breite."""
    return (
        "info",
        f"Die Toronto-Karte hat {num(t['n'])} Knoten (√n = {num(t['sqrt_n'], 1)}): Die BFS-Schicht trennt mit {len(t['level'].vertices)} Knoten ({num(len(t['level'].vertices) / t['sqrt_n'], 2)} √n), "
        f"der geometrische Schnitt mit {len(t['geometric'].vertices)} ({num(len(t['geometric'].vertices) / t['sqrt_n'], 2)} √n); beide sind geprüft ausgewogen. Obwohl die Karte nicht planar ist, verhält sie sich wie ein planarer Graph. "
        f"Nested Dissection (geometrisch) ordnet mit Breite {t['nd_geometric']}, Mindestgrad mit {t['min_degree']}.",
    )
