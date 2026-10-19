"""Szenario: Generatoren (Eigenschaften, Determinismus), Fächer-Triangulierung, Toronto-Daten."""

import os
import subprocess
import sys
from pathlib import Path

import pytest

import psp_algorithm as A
import psp_constants as C
import psp_scenario as S

ROOT = Path(__file__).resolve().parent.parent


def test_same_inputs_give_the_same_instance_and_other_seeds_differ():
    for net in ("delaunay", "random"):
        a = S.make_instance(net, 60, 4)
        assert a == S.make_instance(net, 60, 4) and a != S.make_instance(net, 60, 5)
    assert S.make_instance("lattice", 64, 1) == S.make_instance("lattice", 64, 2)               # das Gitter hat keinen Zufall


@pytest.mark.parametrize("seed", [100, 101, 102, 7])
@pytest.mark.parametrize("n", [20, 100, 300])
def test_map_plus_fan_is_a_maximal_planar_graph(n, seed):
    """Delaunay-Kanten (3n − 3 − h) plus Fächer (h − 3) ergeben 3n − 6 Kanten: eine vollständige Triangulierung."""
    inst = S.make_delaunay(n, seed)
    assert inst.m + len(inst.fan) == 3 * n - 6 and set(inst.fan).isdisjoint(inst.edges) and inst.planar
    assert list(inst.edges) == sorted(set(inst.edges)) and all(0 <= u < v < n for u, v in inst.edges + inst.fan)


def test_the_fan_starts_at_one_hull_vertex():
    inst = S.make_delaunay(60, 5)
    centre = {v for e in inst.fan for v in e}
    hub = max(centre, key=lambda v: sum(v in e for e in inst.fan))
    assert all(hub in e for e in inst.fan)


def test_lattice_and_grid_edge_counts():
    k = 6
    assert S.make_lattice(k * k).m == 2 * k * (k - 1) and S.make_lattice(k * k, True).m == 2 * k * (k - 1) + (k - 1) ** 2
    assert S.make_lattice(k * k).name == "Gitter" and S.make_lattice(k * k, True).name == "Raster mit Diagonalen"


def test_the_random_graph_has_mean_degree_about_three():
    inst = S.make_random(400, 3)
    degree = 2 * inst.m / inst.n
    assert 2.0 < degree < 4.5 and not inst.planar


def test_unknown_net_is_rejected():
    with pytest.raises(ValueError):
        S.make_instance("kugel", 20, 1)


def test_the_instance_does_not_depend_on_the_hash_seed():
    code = (
        "import sys; sys.path.insert(0, %r); import psp_evaluation as ev; "
        "a = ev.analyse(ev.Settings('delaunay', 100, 101, 'cycle')); print(a.inst.edges, a.sep.vertices, a.others)" % str(ROOT)
    )
    outputs = []
    for hash_seed in ("1", "2"):
        env = dict(os.environ, PYTHONHASHSEED=hash_seed, PYTHONIOENCODING="utf-8")
        outputs.append(subprocess.run([sys.executable, "-c", code], env=env, capture_output=True, text=True, check=True).stdout)
    assert outputs[0] == outputs[1] and outputs[0].strip()


def test_toronto_data_and_license():
    inst = S.load_toronto()
    assert (inst.n, inst.m) == (5072, 7621) and not inst.planar
    assert len(A.components(A.adjacency(inst.n, inst.edges), set(range(inst.n)))) == 1
    assert (S.DATA / "LICENSE-ODbL.md").exists() and C.N_MAX == 300
