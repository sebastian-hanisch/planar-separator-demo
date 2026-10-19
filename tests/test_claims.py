"""Jede Zahl der README wird hier nachgerechnet (DEMO-PLAYBOOK §4): über dieselben Auswertungsfunktionen wie in der App.

Zufallsabhängige Werte (6 feste Karten je Größe) mit Band, weil die Bibliotheksversionen der CI die Ziehungen verschieben dürfen; Handrechnungen und Daten exakt."""

import math

import pytest

import psp_constants as C
import psp_evaluation as ev
import psp_scenario as S


@pytest.fixture(scope="module")
def scaling():
    return {r["n"]: r for r in ev.scaling_table(C.SCALING_NS)}


@pytest.fixture(scope="module")
def other():
    return {r["name"]: r for r in ev.other_table()}


@pytest.fixture(scope="module")
def nd():
    return {r["name"]: r for r in ev.nd_table()}


@pytest.fixture(scope="module")
def toronto():
    return ev.toronto_stats()


def test_separator_sizes_on_maps(scaling):
    expected = {100: (13.0, 10.0, 11.0), 300: (28.0, 16.0, 18.5), 1000: (72.0, 26.0, 31.5)}
    for n, (level, cycle, geometric) in expected.items():
        row = scaling[n]
        assert row["level"] == pytest.approx(level, rel=0.15), n
        assert row["cycle"] == pytest.approx(cycle, rel=0.15), n
        assert row["geometric"] == pytest.approx(geometric, rel=0.15), n
    assert C.SCALING_NS == (100, 300, 1000) and len(C.SWEEP_SEEDS) == 6


def test_ratios_to_sqrt_n_and_the_theorem_bound(scaling):
    assert [round(scaling[n]["cycle_ratio"], 1) for n in (100, 300, 1000)] == [1.0, 0.9, 0.8]
    assert scaling[100]["level_ratio"] < scaling[300]["level_ratio"] < scaling[1000]["level_ratio"] and scaling[1000]["level_ratio"] > 2.0
    assert all(0.9 <= scaling[n]["geometric_ratio"] <= 1.2 for n in scaling)
    assert all(scaling[n]["cycle_within_bound"] == 6 for n in scaling)                    # Kreis ≤ √(8n) in 6 von 6 Karten je Größe
    assert all(scaling[n]["cycle"] < scaling[n]["bound"] / 2 for n in scaling)           # die Schranke ist reichlich locker


def test_lattice_raster_and_random_graph_separators(other):
    for k, level, geometric in ((10, 8, 10), (20, 16, 20), (30, 24, 30)):
        assert other[f"Gitter {k} × {k}"]["level"] == level and other[f"Gitter {k} × {k}"]["geometric"] == geometric
        assert other[f"Raster mit Diagonalen {k} × {k}"]["geometric"] == geometric
    assert other["Raster mit Diagonalen 20 × 20"]["level"] == 20 and other["Raster mit Diagonalen 10 × 10"]["level"] == 8
    assert other["Raster mit Diagonalen 30 × 30"]["level"] == 24
    big = other["Zufallsgraph (aus 400)"]
    assert big["n"] == 372 and big["level"] == pytest.approx(70, rel=0.1) and big["geometric"] == pytest.approx(132, rel=0.1)
    assert 0.15 <= big["level"] / big["n"] <= 0.25 and 0.3 <= big["geometric"] / big["n"] <= 0.4
    shares = [other[f"Zufallsgraph (aus {k})"]["level"] / other[f"Zufallsgraph (aus {k})"]["n"] for k in C.OTHER_RANDOM_NS]
    assert min(shares) >= 0.13 and max(shares) <= 0.27


def test_nested_dissection_widths_on_lattices_maps_and_the_random_graph(nd):
    expected = {"Gitter 8 × 8": (11, 10, 10, 10), "Gitter 12 × 12": (17, 16, 16, 16), "Gitter 16 × 16": (23, 23, 23, 22), "Gitter 24 × 24": (35, 34, 37, 37)}
    for name, (geo, level, mindeg, fill) in expected.items():
        r = nd[name]
        assert (r["nd_geometric"], r["nd_level"], r["min_degree"], r["min_fill"]) == (geo, level, mindeg, fill), name
    maps = {n: nd[f"Karte (n = {n}, Median über 3)"] for n in C.ND_MAP_NS}
    assert [maps[n]["nd_geometric"] for n in C.ND_MAP_NS] == pytest.approx([15, 23, 27], abs=3)
    assert [maps[n]["nd_cycle"] for n in C.ND_MAP_NS] == pytest.approx([20, 27, 35], abs=4)
    assert [maps[n]["min_fill"] for n in C.ND_MAP_NS] == pytest.approx([13, 19, 24], abs=3)
    for n in C.ND_MAP_NS:
        assert maps[n]["nd_cycle"] > maps[n]["nd_geometric"] >= maps[n]["min_fill"] - 1      # kleinster Kreis, aber nicht die beste Ordnung
    rand = nd["Zufallsgraph (aus 300)"]
    assert rand["nd_geometric"] > 1.5 * rand["min_degree"] and rand["nd_geometric"] > 3 * rand["sqrt_n"]


def test_lattice_widths_are_not_below_the_treewidth(nd):
    for k in C.ND_GRID_KS:
        r = nd[f"Gitter {k} × {k}"]
        assert min(r["nd_geometric"], r["nd_level"], r["min_degree"], r["min_fill"]) >= k


def test_toronto_separators_and_widths(toronto):
    assert toronto["n"] == 5072 and round(toronto["sqrt_n"], 1) == 71.2
    assert len(toronto["level"].vertices) == 83 and len(toronto["geometric"].vertices) == 57
    assert toronto["level_check"].balanced and toronto["geometric_check"].balanced
    assert (toronto["nd_geometric"], toronto["nd_level"], toronto["min_degree"]) == (73, 137, 57)
    assert round(len(toronto["level"].vertices) / toronto["sqrt_n"], 2) == 1.17 and round(len(toronto["geometric"].vertices) / toronto["sqrt_n"], 2) == 0.80


def test_the_theorem_constant_and_the_gap():
    assert round(math.sqrt(8), 2) == 2.83 and round(math.sqrt(8 * 100), 1) == 28.3
    assert S.make_delaunay(100, 100).planar
