"""Plotly-Figuren: Graph mit Trennmenge, Größenreihen, Nested-Dissection-Breiten und Toronto-Karte. Alle Achsen fest (fixedrange)."""

from __future__ import annotations

import plotly.graph_objects as go

import psp_constants as C


def _edge_trace(pos, edges, color, width, dash=None):
    xs, ys = [], []
    for u, v in edges:
        xs += [pos[u][0], pos[v][0], None]
        ys += [pos[u][1], pos[v][1], None]
    return go.Scatter(x=xs, y=ys, mode="lines", line=dict(color=color, width=width, dash=dash), hoverinfo="skip", showlegend=False)


def _layout(fig, title, height, legend=False):
    fig.update_layout(
        title=dict(text=title, x=0, font=dict(size=14)) if title else None,
        height=height, margin=dict(l=10, r=10, t=40 if title else 10, b=10), showlegend=legend, plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", y=-0.02, x=0),
    )
    fig.update_xaxes(visible=False, fixedrange=True)
    fig.update_yaxes(visible=False, fixedrange=True, scaleanchor="x", scaleratio=1)
    return fig


def node_colors(n, sep_vertices, components) -> list[str]:
    """Farbe je Knoten: Trennmenge rot, die größten Komponenten in eigenen Farben, kleine Reststücke hellblau-grau."""
    colors = ["#9fb3c8"] * n
    for i, comp in enumerate(components):
        for v in comp:
            colors[v] = C.COLOR_SIDES[i] if i < len(C.COLOR_SIDES) - 1 else "#9fb3c8"
    for v in sep_vertices:
        colors[v] = C.COLOR_SEP
    return colors


def build_separator(inst, sep, components, title=None, height=460, show_fan=False):
    """Der Graph mit der Trennmenge (rot) und den Komponenten danach (zwei Hauptfarben); beim Fundamentalkreis der Kreis als rote Linie."""
    fig = go.Figure()
    if show_fan and inst.fan:
        fig.add_trace(_edge_trace(inst.pos, inst.fan, C.COLOR_FAN, 1.5, dash="dot"))
    fig.add_trace(_edge_trace(inst.pos, inst.edges, C.COLOR_EDGE, 2 if inst.n <= 150 else 1))
    if sep is not None and sep.cycle:
        ring = list(sep.cycle) + [sep.cycle[0]]
        have = set(inst.edges) | set(inst.fan)
        links = [(min(a, b), max(a, b)) for a, b in zip(ring, ring[1:]) if (min(a, b), max(a, b)) in have]
        fig.add_trace(_edge_trace(inst.pos, links, C.COLOR_CYCLE, 5))
    vertices = sep.vertices if sep is not None else ()
    colors = node_colors(inst.n, vertices, components)
    sizes = [17 if v in set(vertices) else 11 for v in range(inst.n)] if inst.n <= 150 else [11 if v in set(vertices) else 7 for v in range(inst.n)]
    fig.add_trace(
        go.Scatter(
            x=[p[0] for p in inst.pos], y=[p[1] for p in inst.pos], mode="markers",
            marker=dict(color=colors, size=sizes, line=dict(color="white", width=1)),
            hovertext=[f"Knoten {v}" + (" (Trennmenge)" if v in set(vertices) else "") for v in range(inst.n)], hoverinfo="text",
        )
    )
    return _layout(fig, title, height)


def build_scaling(rows, title="Größe der Trennmenge durch √n"):
    """Verhältnis Trennmenge / √n je Verfahren über n, dazu die Schranke √8 des Satzes."""
    fig = go.Figure()
    xs = [r["n"] for r in rows]
    for key, name, color in (("level", "BFS-Schicht", C.COLOR_PALETTE[1]), ("cycle", "Fundamentalkreis", C.COLOR_PALETTE[2]), ("geometric", "Geometrischer Schnitt", C.COLOR_PALETTE[0])):
        fig.add_trace(go.Scatter(x=xs, y=[r[key + "_ratio"] for r in rows], mode="lines+markers", name=name, line=dict(color=color, width=3),
                                 hovertemplate="n = %{x}: %{y:.2f} √n<extra>" + name + "</extra>"))
    fig.add_hline(y=8 ** 0.5, line=dict(color="#888", dash="dot"), annotation_text="Schranke √8 ≈ 2,83", annotation_position="top left")
    fig.update_layout(title=dict(text=title, x=0, font=dict(size=14)), height=360, margin=dict(l=10, r=10, t=40, b=10), legend=dict(orientation="h", y=-0.25, x=0))
    fig.update_xaxes(title="Knoten n", fixedrange=True, type="log", tickmode="array", tickvals=xs, ticktext=[str(x) for x in xs])
    fig.update_yaxes(title="Trennmenge / √n", fixedrange=True, range=[0, 3.1])
    return fig


def build_nd(rows, title="Breite der Eliminationsordnung"):
    """Breite der Ordnungen je Graph (Gruppen: Nested Dissection geometrisch, Schicht, Kreis; Mindestgrad; Min-Fill)."""
    fig = go.Figure()
    names = [r["name"] for r in rows]
    for key, name, color in (
        ("nd_geometric", "Nested Dissection, geometrisch", C.COLOR_PALETTE[0]), ("nd_level", "Nested Dissection, Schicht", C.COLOR_PALETTE[1]),
        ("nd_cycle", "Nested Dissection, Fundamentalkreis", C.COLOR_PALETTE[2]), ("min_degree", "Mindestgrad", C.COLOR_PALETTE[4]), ("min_fill", "Min-Fill", C.COLOR_PALETTE[5]),
    ):
        fig.add_trace(go.Bar(x=names, y=[r.get(key) for r in rows], name=name, marker_color=color))
    fig.update_layout(title=dict(text=title, x=0, font=dict(size=14)), height=420, barmode="group", margin=dict(l=10, r=10, t=40, b=10), legend=dict(orientation="h", y=-0.45, x=0))
    fig.update_xaxes(fixedrange=True, tickangle=-20)
    fig.update_yaxes(title="Breite", fixedrange=True)
    return fig


def build_toronto(t, height=520):
    """Toronto-Karte mit den beiden Trennmengen (BFS-Schicht rot, geometrischer Schnitt orange)."""
    inst = t["inst"]
    fig = go.Figure()
    fig.add_trace(_edge_trace(inst.pos, inst.edges, "rgba(150,150,150,0.45)", 1))
    for sep, color, name in ((t["level"], C.COLOR_SEP, "BFS-Schicht"), (t["geometric"], C.COLOR_PALETTE[1], "Geometrischer Schnitt")):
        fig.add_trace(go.Scatter(x=[inst.pos[v][0] for v in sep.vertices], y=[inst.pos[v][1] for v in sep.vertices], mode="markers", name=f"{name} ({len(sep.vertices)} Knoten)",
                                 marker=dict(color=color, size=7, line=dict(color="white", width=1)), hoverinfo="skip"))
    return _layout(fig, None, height, legend=True)
