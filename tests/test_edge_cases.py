"""Randfälle, an denen Kernroutinen erfahrungsgemäß brechen (DEMO-PLAYBOOK §12): leere und winzige Graphen, Entartungen, Gleichstände, alle Ecken der Regler."""

import pytest

import psp_algorithm as A
import psp_constants as C
import psp_evaluation as ev
import psp_scenario as S


def test_empty_graph_has_no_separator_and_a_trivially_balanced_check():
    adj = A.adjacency(0, [])
    assert A.components(adj, set()) == [] and A.level_separator(adj, set()) is None and A.cycle_separator(adj, set()) is None
    check = A.check_separator(adj, set(), ())
    assert check.largest == 0 and check.balanced and check.sides == ()
    assert A.nested_dissection(adj, [], "level").order == [] and A.elimination_width(adj, []) == 0


def test_a_single_vertex_cannot_be_separated():
    adj = A.adjacency(1, [])
    assert A.level_separator(adj, {0}) is None and A.geometric_separator(adj, [(0.0, 0.0)], {0}) is None
    assert A.nested_dissection(adj, [(0.0, 0.0)], "geometric").order == [0]


def test_exactly_two_vertices_one_edge():
    """n = 2: Grenze 2n/3 = 1,33: das Entfernen eines Knotens lässt einen (ausgewogen); die Schicht ab Wurzel 0 ist {0}."""
    adj = A.adjacency(2, [(0, 1)])
    s = A.level_separator(adj, {0, 1})
    assert s.vertices == (0,) and A.check_separator(adj, {0, 1}, s.vertices).balanced
    g = A.geometric_separator(adj, [(0.0, 0.0), (1.0, 0.0)], {0, 1})
    assert g.vertices == (0,) and g.cut_edges == 1


def test_a_triangle_is_its_own_fundamental_cycle():
    adj = A.adjacency(3, [(0, 1), (1, 2), (0, 2)])
    s = A.cycle_separator(adj, {0, 1, 2}, roots=[0])
    assert s.vertices == (0, 1, 2) and s.cycle == (1, 0, 2)                                 # alles entfernt: nichts übrig, ausgewogen
    assert A.check_separator(adj, {0, 1, 2}, s.vertices).largest == 0


def test_equal_positions_are_split_by_vertex_number():
    adj = A.adjacency(4, [(0, 1), (1, 2), (2, 3)])
    axis, left = A.median_cut([(0.0, 0.0)] * 4, {0, 1, 2, 3})
    assert axis == 0 and left == {0, 1}


def test_results_do_not_depend_on_the_order_of_the_edge_list():
    edges = [(0, 1), (1, 2), (2, 3), (3, 4), (0, 4), (1, 3)]
    a, b = A.adjacency(5, edges), A.adjacency(5, list(reversed(edges)))
    pos = [(float(i), 0.0) for i in range(5)]
    for method in C.METHODS:
        assert A.find_separator(method, a, set(range(5)), pos) == A.find_separator(method, b, set(range(5)), pos)


def test_nested_dissection_with_a_large_leaf_just_orders_by_minimum_degree():
    adj = A.adjacency(5, [(i, i + 1) for i in range(4)])
    r = A.nested_dissection(adj, [(float(i), 0.0) for i in range(5)], "level", leaf=10)
    assert r.order == A.min_degree_order(adj) and r.pieces == [] and r.fallbacks == 0


def test_nested_dissection_of_a_disconnected_graph_handles_each_part():
    adj = A.adjacency(8, [(0, 1), (1, 2), (2, 3), (4, 5), (5, 6), (6, 7)])
    r = A.nested_dissection(adj, [(float(i), 0.0) for i in range(8)], "level", leaf=2)
    assert sorted(r.order) == list(range(8))


def test_lattice_sizes_are_rounded_to_a_square():
    assert S.lattice_side(16) == 4 and S.lattice_side(150) == 12 and S.lattice_side(1) == 3
    assert S.make_lattice(150).n == 144 and S.make_lattice(100, True).m == 180 + 81


@pytest.mark.parametrize("net", list(C.NET_TYPES))
@pytest.mark.parametrize("n", [C.N_MIN, C.N_MAX])
@pytest.mark.parametrize("method", list(C.METHODS))
def test_every_corner_of_the_controls_gives_a_consistent_analysis(net, n, method):
    a = ev.analyse(ev.Settings(net, n, 100, method))
    assert a.inst.n >= 3
    kind, text = ev.verdict_separator(a, method)
    assert kind in ("success", "warning", "error") and text
    if a.sep is not None:
        assert a.check.balanced and a.sep.method == method
    else:
        assert kind == "warning"


def test_the_random_graph_is_connected_and_relabelled():
    inst = S.make_random(200, 5)
    adj = A.adjacency(inst.n, inst.edges)
    assert len(A.components(adj, set(range(inst.n)))) == 1 and inst.n <= 200 and not inst.planar and len(inst.pos) == inst.n
