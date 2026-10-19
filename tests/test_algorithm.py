"""Einheiten des Kerns an Mini-Graphen, von Hand gerechnet (DEMO-PLAYBOOK §1b): eine Regel = ein Test."""

import pytest

import psp_algorithm as A


def test_components_are_ordered_by_their_smallest_vertex():
    adj = A.adjacency(6, [(0, 1), (2, 3)])
    assert A.components(adj, range(6)) == [{0, 1}, {2, 3}, {4}, {5}]
    assert A.components(adj, {1, 2, 3}) == [{1}, {2, 3}]                  # induzierter Teilgraph


def test_largest_component_after_removal(path7):
    nodes = set(range(7))
    assert A.largest_component_after(path7, nodes, [3]) == 3 and A.largest_component_after(path7, nodes, [1]) == 5
    assert A.largest_component_after(path7, nodes, list(range(7))) == 0


def test_check_separator_uses_the_two_thirds_bound(path7):
    ok = A.check_separator(path7, set(range(7)), (3,))
    assert ok.size == 1 and ok.largest == 3 and ok.balanced and ok.sides == (3, 3) and ok.limit == pytest.approx(14 / 3)
    bad = A.check_separator(path7, set(range(7)), (1,))
    assert bad.largest == 5 and not bad.balanced and bad.sides == (5, 1)


def test_check_separator_bound_is_inclusive():
    """Pfad mit 6 Knoten, Grenze 4: der Knoten 1 lässt 4 und 1 übrig (genau an der Grenze, ausgewogen); der Endknoten 0 lässt 5."""
    adj = A.adjacency(6, [(i, i + 1) for i in range(5)])
    assert A.check_separator(adj, set(range(6)), (1,)).balanced and A.check_separator(adj, set(range(6)), (1,)).largest == 4
    assert not A.check_separator(adj, set(range(6)), (0,)).balanced


def test_bfs_levels(path7):
    assert A.bfs_levels(path7, 3, set(range(7))) == [[3], [2, 4], [1, 5], [0, 6]]
    assert A.bfs_levels(path7, 3, {2, 3, 4, 6}) == [[3], [2, 4]]            # nur der erreichte Teil


def test_default_roots_are_evenly_spread():
    assert A.default_roots(range(7)) == list(range(7)) and A.default_roots(range(12)) == [0, 2, 4, 6, 8, 10] and A.default_roots(range(30), 4) == [0, 7, 14, 21, 28]


def test_level_separator_of_a_path_is_the_first_balanced_vertex(path7):
    s = A.level_separator(path7, set(range(7)))
    assert s.vertices == (2,) and s.method == "level" and s.root == 0 and s.detail == "Schicht 2 ab Wurzel 0"


def test_level_separator_of_a_star_is_its_centre(star7):
    s = A.level_separator(star7, set(range(7)))
    assert s.vertices == (0,) and s.root == 0


def test_level_separator_of_a_3x3_grid_has_two_vertices(grid3):
    s = A.level_separator(grid3, set(range(9)))
    assert s.vertices == (1, 3) and s.detail == "Schicht 1 ab Wurzel 0"


def test_level_profile_of_a_3x3_grid(grid3):
    rows = A.level_profile(grid3, set(range(9)), 0)
    assert [(r["level"], r["size"], r["largest"], r["balanced"]) for r in rows] == [(0, 1, 8, False), (1, 2, 6, True), (2, 3, 3, True), (3, 2, 6, True), (4, 1, 8, False)]


def test_no_level_separator_when_the_graph_is_disconnected_from_every_root():
    adj = A.adjacency(4, [(0, 1), (2, 3)])
    assert A.level_separator(adj, set(range(4))) is None


def test_bfs_tree_and_fundamental_cycles_of_the_hexagon_with_chord(hexagon_chord):
    parent, depth = A.bfs_tree(hexagon_chord, 0, set(range(6)))
    assert parent == {0: None, 1: 0, 3: 0, 5: 0, 2: 1, 4: 3} and depth[2] == 2 and depth[4] == 2
    assert A.fundamental_cycle(parent, depth, 2, 3) == [2, 1, 0, 3] and A.fundamental_cycle(parent, depth, 4, 5) == [4, 3, 0, 5]
    cands = A.cycle_candidates(hexagon_chord, set(range(6)), 0)
    assert [(c[0], c[1], c[2]) for c in cands] == [(4, 2, 3), (4, 4, 5)]


def test_cycle_separator_takes_the_shortest_balanced_cycle(hexagon_chord):
    s = A.cycle_separator(hexagon_chord, set(range(6)), roots=[0])
    assert s.vertices == (0, 1, 2, 3) and s.cycle == (2, 1, 0, 3) and s.detail == "Kante 2–3 ab Wurzel 0" and s.root == 0


def test_cycle_profile_lists_candidates_with_their_balance(hexagon_chord):
    rows = A.cycle_profile(hexagon_chord, set(range(6)), 0)
    assert rows == [
        {"rank": 1, "edge": (2, 3), "length": 4, "largest": 2, "balanced": True}, {"rank": 2, "edge": (4, 5), "length": 4, "largest": 2, "balanced": True},
    ]


def test_a_tree_has_no_cycle_separator(path7):
    assert A.cycle_separator(path7, set(range(7))) is None


def test_median_cut_picks_the_longer_axis_and_breaks_ties_by_x():
    pos = [(0.0, 0.0), (1.0, 5.0), (2.0, 1.0), (3.0, 4.0)]
    assert A.median_cut(pos, {0, 1, 2, 3}) == (1, {0, 2})                  # y-Achse ist länger: kleinste y-Werte links
    square = [(0.0, 0.0), (1.0, 0.0), (0.0, 1.0), (1.0, 1.0)]
    assert A.median_cut(square, {0, 1, 2, 3}) == (0, {0, 2})               # gleiche Ausdehnung: x, dann nach (x, Nummer)


def test_cut_edges_of_a_path():
    adj = A.adjacency(4, [(0, 1), (1, 2), (2, 3)])
    assert A.cut_edges(adj, {0, 1, 2, 3}, {0, 1}) == [(1, 2)]


def test_max_matching_needs_an_augmenting_path():
    assert A.max_matching([(0, 2), (0, 3), (1, 2)]) == {2: 1, 3: 0}
    assert A.max_matching([(0, 2), (1, 2)]) == {2: 0}


def test_koenig_cover_has_the_size_of_the_matching():
    assert A.koenig_cover([(0, 2), (0, 3), (1, 2)], A.max_matching([(0, 2), (0, 3), (1, 2)])) == {0, 1}
    assert A.koenig_cover([(0, 2), (1, 2)], A.max_matching([(0, 2), (1, 2)])) == {2}              # ein Knoten überdeckt beide Kanten
    k22 = [(0, 2), (0, 3), (1, 2), (1, 3)]
    assert len(A.koenig_cover(k22, A.max_matching(k22))) == 2


def test_geometric_separator_of_a_path():
    adj = A.adjacency(6, [(i, i + 1) for i in range(5)])
    pos = [(float(i), 0.0) for i in range(6)]
    s = A.geometric_separator(adj, pos, set(range(6)))
    assert s.vertices == (2,) and s.cut_edges == 1 and s.matching == 1 and s.detail == "Median auf Achse x"
    assert A.geometric_separator(A.adjacency(2, []), [(0.0, 0.0), (1.0, 0.0)], {0, 1}) is None       # nichts zu schneiden


def test_find_separator_dispatches_and_rejects_unknown_methods(path7):
    pos = [(float(i), 0.0) for i in range(7)]
    assert A.find_separator("level", path7, set(range(7)), pos).method == "level"
    assert A.find_separator("geometric", path7, set(range(7)), pos).method == "geometric"
    with pytest.raises(ValueError):
        A.find_separator("zufall", path7, set(range(7)), pos)


def test_min_degree_and_min_fill_orders():
    path = A.adjacency(4, [(0, 1), (1, 2), (2, 3)])
    assert A.min_degree_order(path) == [0, 1, 2, 3]
    c4 = A.adjacency(4, [(0, 1), (1, 2), (2, 3), (0, 3)])
    assert A.min_fill_order(c4) == [0, 1, 2, 3] and A.elimination_width(c4, [0, 1, 2, 3]) == 2


def test_elimination_width_of_known_orders(grid3):
    path = A.adjacency(5, [(i, i + 1) for i in range(4)])
    assert A.elimination_width(path, [0, 1, 2, 3, 4]) == 1
    k4 = A.adjacency(4, [(u, v) for u in range(4) for v in range(u + 1, 4)])
    assert A.elimination_width(k4, [0, 1, 2, 3]) == 3
    assert A.elimination_width(grid3, list(range(9))) == 3                      # zeilenweise: Breite 3 (die Baumweite des 3 × 3 Gitters)
    with pytest.raises(ValueError):
        A.elimination_width(path, [0, 1, 2])


def test_nested_dissection_of_a_path_puts_separators_last(path7):
    r = A.nested_dissection(path7, [(float(i), 0.0) for i in range(7)], "level", leaf=2)
    assert r.order == [0, 1, 3, 5, 6, 4, 2] and r.pieces == [(7, 1, "level"), (4, 1, "level")] and r.fallbacks == 0
    assert A.elimination_width(path7, r.order) == 2                            # Knoten 3 hat beim Eliminieren die Nachbarn 2 und 4 (die Baumweite des Pfads ist 1: die Ordnung ist nicht optimal)


def test_nested_dissection_falls_back_to_the_median_when_the_method_finds_nothing(path7):
    r = A.nested_dissection(path7, [(float(i), 0.0) for i in range(7)], "cycle", leaf=2)       # ein Baum hat keinen Kreis
    assert r.fallbacks >= 1 and all(p[2].startswith("Rückfall") for p in r.pieces) and sorted(r.order) == list(range(7))


def _lattice(k):
    edges = [(r * k + c, r * k + c + 1) for r in range(k) for c in range(k - 1)] + [(r * k + c, (r + 1) * k + c) for r in range(k - 1) for c in range(k)]
    return A.adjacency(k * k, edges)


def test_cycle_profile_shows_the_first_balanced_cycle_even_when_it_is_far_down_the_list():
    """4 × 4 Gitter, Wurzel 0: die kürzesten Kreise (Zellen) lassen 12 Knoten übrig, mehr als 2n/3 = 10,67; der erste ausgewogene steht weiter hinten und wird als letzte Zeile angefügt."""
    adj = _lattice(4)
    rows = A.cycle_profile(adj, set(range(16)), 0, limit=2)
    assert [r["rank"] for r in rows[:2]] == [1, 2] and not rows[0]["balanced"] and rows[-1]["balanced"] and rows[-1]["rank"] > 2 and len(rows) == 3
    chosen = A.cycle_separator(adj, set(range(16)), roots=[0])
    assert rows[-1]["length"] == len(chosen.vertices) and rows[-1]["largest"] <= 2 * 16 / 3


def test_cycle_profile_flags_follow_the_two_thirds_bound_exactly():
    for k in (4, 5, 6, 7):
        adj = _lattice(k)
        n = k * k
        rows = A.cycle_profile(adj, set(range(n)), 0, limit=40)
        assert all(r["balanced"] == (r["largest"] <= 2 * n / 3) for r in rows)
    rows = A.cycle_profile(_lattice(4), set(range(16)), 0, limit=40)
    band = [r for r in rows if 16 / 2 < r["largest"] <= 2 * 16 / 3]
    assert any(r["balanced"] for r in rows) and any(not r["balanced"] for r in rows) and band and all(r["balanced"] for r in band)


def test_cycle_separator_accepts_a_component_of_exactly_two_thirds():
    """Dreieck 0-1-2 mit Pfad 2-3-…-8 (n = 9): der Dreieckskreis lässt genau 6 = 2n/3 Knoten übrig und ist ausgewogen (Grenze inklusive)."""
    adj = A.adjacency(9, [(0, 1), (0, 2), (1, 2)] + [(i, i + 1) for i in range(2, 8)])
    s = A.cycle_separator(adj, set(range(9)), roots=[0])
    assert s.vertices == (0, 1, 2) and A.check_separator(adj, set(range(9)), s.vertices).largest == 6


def test_cut_edges_and_the_geometric_separator_of_a_3x3_lattice_are_listed_in_order():
    adj = _lattice(3)
    pos = [(float(c), float(-r)) for r in range(3) for c in range(3)]
    axis, left = A.median_cut(pos, set(range(9)))
    assert axis == 0 and left == {0, 1, 3, 6}
    assert A.cut_edges(adj, set(range(9)), left) == [(1, 2), (1, 4), (3, 4), (6, 7)]
    s = A.geometric_separator(adj, pos, set(range(9)))
    assert s.vertices == (1, 3, 6) and s.cut_edges == 4 and s.matching == 3


def test_nested_dissection_of_two_components_handles_each_before_any_separator():
    adj = A.adjacency(8, [(0, 1), (1, 2), (2, 3), (4, 5), (5, 6), (6, 7)])
    r = A.nested_dissection(adj, [(float(i), 0.0) for i in range(8)], "level", leaf=2)
    assert r.order == [0, 2, 3, 1, 4, 6, 7, 5] and r.pieces == [(4, 1, "level"), (4, 1, "level")] and r.fallbacks == 0


def test_a_level_that_contains_every_vertex_is_not_a_separator():
    """Ein Einzelknoten: seine einzige Schicht ist der ganze Graph, das Entfernen lässt nichts übrig und zählt nicht als Trennmenge."""
    rows = A.level_profile(A.adjacency(1, []), {0}, 0)
    assert rows == [{"level": 0, "size": 1, "largest": 0, "balanced": False}]
