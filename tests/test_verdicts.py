"""Verdikte an von Hand gesetzten Werten (DEMO-PLAYBOOK §12): jede Zahl im Text und jede Schwelle der Art steht hier."""

import dataclasses

import psp_algorithm as A
import psp_evaluation as ev
import psp_scenario as S


def _lattice3(method):
    return ev.analyse_instance(S.make_lattice(9), method)


def _hexagon(method):
    edges = S.normalize_edges([(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (0, 5), (0, 3)])
    return ev.analyse_instance(S.Instance(6, edges, S.circle_layout(6), "Sechseck"), method)


def test_num_and_plural():
    assert ev.num(1234567.891, 1) == "1.234.567,9" and ev.num(0.5, 2) == "0,50" and ev.num(1000) == "1.000"
    assert ev.plural(1, "Kette", "Ketten") == "1 Kette" and ev.plural(0, "Kette", "Ketten") == "0 Ketten"


def test_verdict_for_a_level_separator_names_size_ratio_and_balance():
    kind, text = ev.verdict_separator(_lattice3("level"), "level")
    assert kind == "success"
    assert text == "BFS-Schicht: **2 Knoten** (0,67 √n), die größte Komponente danach hat 6 von 9 Knoten (Grenze 2n/3 = 6,0)."


def test_verdict_for_a_geometric_separator():
    kind, text = ev.verdict_separator(_lattice3("geometric"), "geometric")
    assert kind == "success" and text == "Geometrischer Schnitt (Median + König): **3 Knoten** (1,00 √n), die größte Komponente danach hat 5 von 9 Knoten (Grenze 2n/3 = 6,0)."


def test_verdict_for_a_cycle_separator_names_the_bound_of_the_theorem():
    kind, text = ev.verdict_separator(_hexagon("cycle"), "cycle")
    assert kind == "success" and "Fundamentalkreis: **4 Knoten** (1,63 √n)" in text and "2 von 6 Knoten (Grenze 2n/3 = 4,0)" in text
    assert "√(8n) = 6,9 und wird eingehalten" in text


def test_verdict_for_a_cycle_above_the_bound_says_so():
    a = _hexagon("cycle")
    a = dataclasses.replace(a, bound=3.0)
    kind, text = ev.verdict_separator(a, "cycle")
    assert kind == "success" and "wird hier überschritten" in text and "√(8n) = 3,0" in text


def test_verdict_without_a_separator_is_a_warning():
    a = ev.analyse_instance(S.Instance(7, S.normalize_edges([(i, i + 1) for i in range(6)]), S.circle_layout(7), "Pfad"), "cycle")     # ein Baum hat keinen Kreis
    kind, text = ev.verdict_separator(a, "cycle")
    assert a.sep is None and kind == "warning" and "keine** Trennmenge" in text


def test_verdict_for_an_unbalanced_result_is_an_error():
    a = _lattice3("level")
    bad = dataclasses.replace(a, check=A.SepCheck(1, 8, 6.0, False, (8,)), sep=A.Separator((4,), "level"))
    kind, text = ev.verdict_separator(bad, "level")
    assert kind == "error" and "nicht ausgewogen" in text and "8 von 9" in text


def test_others_report_the_sizes_of_the_other_methods():
    a = _lattice3("level")
    assert set(a.others) == {"cycle", "geometric"} and a.others["geometric"] == 3


def _row(n, level, cycle, geometric, within=6):
    return {"n": n, "samples": 6, "sqrt_n": n ** 0.5, "bound": (8 * n) ** 0.5, "cycle_within_bound": within, "level_ratio": level, "cycle_ratio": cycle, "geometric_ratio": geometric}


def test_verdict_scaling_names_first_and_last_ratio_and_the_bound_count():
    kind, text = ev.verdict_scaling([_row(100, 1.3, 1.0, 1.1), _row(1000, 2.28, 0.82, 1.0, within=5)])
    assert kind == "info"
    assert "n = 100 / 1000 für den Fundamentalkreis bei 1,00 / 0,82" in text and "geometrischen Schnitt bei 1,10 / 1,00" in text and "BFS-Schicht bei 1,30 / 2,28" in text
    assert "in 11 von 12 Fällen" in text


def test_verdict_other_compares_grid_with_k_and_random_graph_with_n():
    rows = [
        {"name": "Gitter 30 × 30", "n": 900, "level": 24, "geometric": 30, "scale": 30, "linear": False},
        {"name": "Zufallsgraph (aus 400)", "n": 372, "level": 70, "geometric": 132, "scale": 372, "linear": True},
    ]
    kind, text = ev.verdict_other(rows)
    assert "Beim Gitter 30 × 30 hat die Schicht 24 und der geometrische Schnitt 30 Knoten (k = 30)" in text
    assert "mit 372 Knoten sind es 70 und 132: 19 % der Knoten" in text


def _nd_rows(grid_nd, grid_fill):
    return [
        {"name": "Gitter 24 × 24", "n": 576, "nd_geometric": grid_nd, "nd_level": grid_nd + 1, "min_degree": 37, "min_fill": grid_fill, "sqrt_n": 24.0},
        {"name": "Karte (n = 300, Median über 3)", "n": 300, "nd_geometric": 27, "nd_level": 42, "min_degree": 26, "nd_cycle": 35, "min_fill": 24, "sqrt_n": 17.3},
        {"name": "Zufallsgraph (aus 300)", "n": 276, "nd_geometric": 67, "nd_level": 47, "min_degree": 34, "min_fill": 30, "sqrt_n": 16.6},
    ]


def test_verdict_nd_reports_map_and_random_graph_and_the_lattice_only_when_nd_wins():
    kind, text = ev.verdict_nd(_nd_rows(35, 37))
    assert kind == "info" and "Breite 27,0, mit dem Fundamentalkreis 35,0, Mindestgrad 26,0 und Min-Fill 24,0 (√n = 17,3)" in text
    assert "Breite 67 gegen Mindestgrad 34" in text and "Am Gitter 24 × 24 ist Nested Dissection erstmals vorn (35 gegen 37 bei Min-Fill)" in text
    assert "erstmals vorn" not in ev.verdict_nd(_nd_rows(40, 37))[1]


def test_verdict_toronto_states_sizes_and_widths():
    inst = S.make_lattice(9)
    adj = A.adjacency(9, inst.edges)
    level, geo = A.level_separator(adj, set(range(9))), A.geometric_separator(adj, inst.pos, set(range(9)))
    t = {"n": 5072, "sqrt_n": 71.2, "level": level, "geometric": geo, "nd_geometric": 73, "min_degree": 57}
    kind, text = ev.verdict_toronto(t)
    assert kind == "info" and "5.072 Knoten (√n = 71,2)" in text and "mit 2 Knoten (0,03 √n)" in text and "mit 3 (0,04 √n)" in text
    assert "Breite 73, Mindestgrad mit 57" in text
