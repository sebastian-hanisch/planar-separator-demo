"""Orakel-Test planar-separator-demo: Kern gegen unabhängige Rechenwege (DEMO-PLAYBOOK §12).

Orakel: (1) networkx (Komponenten nach dem Entfernen, Matching, BFS-Schichten, chordale Abschlüsse), (2) Brute Force (kleinste Knotenüberdeckung), (3) Sätze:
Satz von König, Fundamentalkreis höchstens 2 · Tiefe + 1 und höchstens √(8n) auf triangulierten Karten (Lipton–Tarjan, Miller), Baumweite des k × k Gitters ist k, jede
Eliminationsbreite liegt darüber. Der große Lauf (mindestens 200 Zufallsinstanzen) lief im Scratch-Ordner; hier die schnelle Fassung."""

import itertools
import math
import random

import pytest

import psp_algorithm as A
import psp_constants as C
import psp_scenario as S

nx = pytest.importorskip("networkx")


def _nxgraph(inst):
    g = nx.Graph()
    g.add_nodes_from(range(inst.n))
    g.add_edges_from(inst.edges)
    return g


def _instances(count, rng):
    nets = ("delaunay", "grid", "lattice", "random")
    for i in range(count):
        yield S.make_instance(nets[i % 4], rng.randint(20, 120), rng.randrange(10**6))


def test_every_separator_is_balanced_according_to_networkx():
    rng = random.Random(1)
    found = 0
    for inst in _instances(60, rng):
        adj = A.adjacency(inst.n, inst.edges)
        full = A.adjacency(inst.n, inst.edges + inst.fan)
        g = _nxgraph(inst)
        nodes = set(range(inst.n))
        for method in C.METHODS:
            sep = A.find_separator(method, adj, nodes, inst.pos, full)
            if sep is None:
                continue
            found += 1
            rest = g.subgraph(nodes - set(sep.vertices))
            largest = max((len(c) for c in nx.connected_components(rest)), default=0)
            assert largest <= 2 * inst.n / 3, (inst.name, method)
            check = A.check_separator(adj, nodes, sep.vertices)
            assert check.largest == largest and check.balanced
    assert found > 150


def test_koenig_cover_equals_the_matching_and_covers_every_edge():
    rng = random.Random(2)
    for _ in range(80):
        left, right = rng.randint(1, 7), rng.randint(1, 7)
        edges = sorted({(u, left + v) for u in range(left) for v in range(right) if rng.random() < 0.4})
        if not edges:
            continue
        match = A.max_matching(edges)
        cover = A.koenig_cover(edges, match)
        g = nx.Graph(edges)
        assert len(match) == len(nx.bipartite.hopcroft_karp_matching(g, top_nodes={u for u, _ in edges})) // 2
        assert len(cover) == len(match) and all(u in cover or v in cover for u, v in edges)


def test_koenig_cover_is_a_minimum_vertex_cover_by_brute_force():
    rng = random.Random(3)
    for _ in range(40):
        left, right = rng.randint(1, 4), rng.randint(1, 4)
        edges = sorted({(u, left + v) for u in range(left) for v in range(right) if rng.random() < 0.5})
        if not edges:
            continue
        nodes = sorted({x for e in edges for x in e})
        smallest = next(k for k in range(len(nodes) + 1) if any(all(u in s or v in s for u, v in edges) for s in map(set, itertools.combinations(nodes, k))))
        assert len(A.koenig_cover(edges, A.max_matching(edges))) == smallest


def test_bfs_levels_equal_networkx_layers():
    rng = random.Random(4)
    for inst in _instances(30, rng):
        adj = A.adjacency(inst.n, inst.edges)
        g = _nxgraph(inst)
        root = rng.randrange(inst.n)
        mine = A.bfs_levels(adj, root, set(range(inst.n)))
        theirs = [sorted(layer) for layer in nx.bfs_layers(g, root)]
        assert mine == theirs


def test_fundamental_cycles_are_cycles_of_bounded_length():
    """Aufeinanderfolgende Kreisknoten sind benachbart (auch die letzte und die erste), der Kreis ist höchstens 2 · Tiefe + 1 lang."""
    rng = random.Random(5)
    for _ in range(25):
        inst = S.make_delaunay(rng.randint(20, 150), rng.randrange(10**6))
        full = A.adjacency(inst.n, inst.edges + inst.fan)
        root = rng.randrange(inst.n)
        parent, depth = A.bfs_tree(full, root, set(range(inst.n)))
        height = max(depth.values())
        for length, u, v, cyc in A.cycle_candidates(full, set(range(inst.n)), root)[:40]:
            assert len(set(cyc)) == len(cyc) == length and length <= 2 * height + 1
            assert all(cyc[(i + 1) % length] in full[cyc[i]] for i in range(length))


def test_the_cycle_separator_keeps_the_lipton_tarjan_bound_on_triangulated_maps():
    """Eigenschaftstest für den Satz: auf jeder Karte (mit Fächer, also trianguliert) ist der gefundene Kreis höchstens √(8n) lang, und ausgewogen auch auf dem Originalgraphen."""
    rng = random.Random(6)
    for _ in range(60):
        n = rng.randint(20, 250)
        inst = S.make_delaunay(n, rng.randrange(10**6))
        adj = A.adjacency(n, inst.edges)
        full = A.adjacency(n, inst.edges + inst.fan)
        sep = A.cycle_separator(full, set(range(n)))
        assert sep is not None and len(sep.vertices) <= math.sqrt(8 * n), n
        assert A.check_separator(full, set(range(n)), sep.vertices).balanced and A.check_separator(adj, set(range(n)), sep.vertices).balanced


def test_elimination_width_equals_the_clique_number_of_the_chordal_completion():
    rng = random.Random(7)
    for _ in range(40):
        n = rng.randint(6, 25)
        edges = sorted(rng.sample([(u, v) for u in range(n) for v in range(u + 1, n)], rng.randint(n, 2 * n)))
        adj = A.adjacency(n, edges)
        order = list(range(n))
        rng.shuffle(order)
        completion = nx.Graph(edges)
        completion.add_nodes_from(range(n))
        h = {v: set(adj[v]) for v in range(n)}
        for v in order:
            nb = sorted(h[v])
            for i in range(len(nb)):
                for j in range(i + 1, len(nb)):
                    completion.add_edge(nb[i], nb[j])
            A._eliminate(h, v)
        assert A.elimination_width(adj, order) == max(len(c) for c in nx.chordal_graph_cliques(completion)) - 1


def test_every_order_has_at_least_the_treewidth_of_the_lattice():
    """Die Baumweite des k × k Gitters ist k: keine Ordnung darf darunter liegen; Nested Dissection und die Heuristiken liegen darüber."""
    for k in (4, 6, 8):
        inst = S.make_lattice(k * k)
        adj = A.adjacency(inst.n, inst.edges)
        widths = [
            A.elimination_width(adj, A.min_degree_order(adj)), A.elimination_width(adj, A.min_fill_order(adj)),
            A.elimination_width(adj, A.nested_dissection(adj, inst.pos, "geometric").order), A.elimination_width(adj, A.nested_dissection(adj, inst.pos, "level").order),
        ]
        assert all(w >= k for w in widths), (k, widths)


def test_nested_dissection_orders_are_permutations_for_every_method_and_net():
    rng = random.Random(8)
    for inst in _instances(24, rng):
        adj = A.adjacency(inst.n, inst.edges)
        full = A.adjacency(inst.n, inst.edges + inst.fan)
        for method in C.METHODS:
            r = A.nested_dissection(adj, inst.pos, method, adj_cycle=full)
            assert sorted(r.order) == list(range(inst.n)) and A.elimination_width(adj, r.order) <= inst.n - 1


def test_separators_are_much_larger_without_planarity():
    """Gegenprobe: im Zufallsgraphen (Grad 3) ist die Trennmenge ein Bruchteil von n, in der Karte nur etwa √n."""
    rng = random.Random(9)
    random_share, map_share = [], []
    for _ in range(6):
        r = S.make_random(300, rng.randrange(10**6))
        d = S.make_delaunay(280, rng.randrange(10**6))
        random_share.append(len(A.level_separator(A.adjacency(r.n, r.edges), set(range(r.n))).vertices) / r.n)
        map_share.append(len(A.level_separator(A.adjacency(d.n, d.edges), set(range(d.n))).vertices) / d.n)
    assert min(random_share) > 0.1 and max(map_share) < 0.15 and sum(random_share) > 1.5 * sum(map_share)
