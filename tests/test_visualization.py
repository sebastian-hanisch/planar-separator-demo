"""Darstellung: Knotenfarben (reine Funktion) und dass jede Figur ohne Fehler entsteht, mit festen Achsen."""

import plotly.graph_objects as go
import pytest

import psp_constants as C
import psp_evaluation as ev
import psp_scenario as S
import psp_visualization as V


def test_node_colours_mark_the_separator_and_the_largest_components():
    colors = V.node_colors(8, (3,), [{0, 1, 2}, {4, 5}, {6}, {7}])
    assert colors[3] == C.COLOR_SEP
    assert colors[0] == colors[1] == colors[2] == C.COLOR_SIDES[0] and colors[4] == colors[5] == C.COLOR_SIDES[1] and colors[6] == C.COLOR_SIDES[2] and colors[7] == C.COLOR_SIDES[3]


def test_node_colours_after_the_fourth_component_are_grey():
    comps = [{i} for i in range(6)]
    colors = V.node_colors(7, (6,), comps)
    assert colors[4] == colors[5] == "#9fb3c8" and colors[6] == C.COLOR_SEP


def _fixed(fig):
    return fig.layout.xaxis.fixedrange and fig.layout.yaxis.fixedrange


@pytest.mark.parametrize("net", list(C.NET_TYPES))
@pytest.mark.parametrize("method", list(C.METHODS))
def test_every_net_and_method_draws(net, method):
    a = ev.analyse(ev.Settings(net, 60, 100, method))
    fig = V.build_separator(a.inst, a.sep, a.components, title="t", show_fan=method == "cycle")
    assert isinstance(fig, go.Figure) and _fixed(fig)


def test_the_cycle_is_drawn_as_a_thick_line_and_the_fan_dotted():
    a = ev.analyse(ev.Settings("delaunay", 60, 100, "cycle"))
    fig = V.build_separator(a.inst, a.sep, a.components, show_fan=True)
    widths = [t.line.width for t in fig.data if t.mode == "lines"]
    dashes = [t.line.dash for t in fig.data if t.mode == "lines"]
    assert 5 in widths and "dot" in dashes
    no_fan = V.build_separator(a.inst, a.sep, a.components, show_fan=False)
    assert "dot" not in [t.line.dash for t in no_fan.data if t.mode == "lines"]


def test_no_separator_draws_the_plain_graph():
    inst = S.make_lattice(16)
    fig = V.build_separator(inst, None, [])
    assert list(fig.data[-1].marker.color) == ["#9fb3c8"] * 16


def test_measure_figures_have_fixed_axes():
    rows = [{"n": n, "level_ratio": 1.3, "cycle_ratio": 1.0, "geometric_ratio": 1.1} for n in (100, 300)]
    nd = [{"name": "Gitter", "nd_geometric": 11, "nd_level": 10, "min_degree": 10, "min_fill": 10}, {"name": "Karte", "nd_geometric": 15, "nd_level": 21, "nd_cycle": 20, "min_degree": 14, "min_fill": 13}]
    for fig in (V.build_scaling(rows), V.build_nd(nd)):
        assert fig.layout.xaxis.fixedrange and fig.layout.yaxis.fixedrange


def test_toronto_figure_builds():
    t = ev.toronto_stats()
    fig = V.build_toronto(t)
    assert isinstance(fig, go.Figure) and _fixed(fig) and len(fig.data) == 3
