"""Planare Separatoren – kleine Trennmengen und Nested Dissection - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Lauffähig mit: streamlit run app.py
"""

import streamlit as st

import psp_algorithm as A
import psp_constants as C
import psp_evaluation as ev
import psp_scenario as S
from psp_layout import dunkles_design, kopf_css
from psp_presets import (
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    randomize_seed,
    sidebar_presets,
    sync_query_params,
)
from psp_visualization import build_nd, build_scaling, build_separator, build_toronto

st.set_page_config(page_title="Planare Separatoren – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner=False)
def _analysis(settings):
    return ev.analyse(settings)


@st.cache_data(show_spinner=False)
def _scaling(ns):
    return ev.scaling_table(ns)


@st.cache_data(show_spinner=False)
def _other():
    return ev.other_table()


@st.cache_data(show_spinner=False)
def _nd():
    return ev.nd_table()


@st.cache_data(show_spinner=False)
def _toronto():
    return ev.toronto_stats()


def _details(a, inst, method):
    """Tabelle zum gewählten Verfahren: Schichten, die kürzesten Kreise oder die Schnittkanten."""
    adj = A.adjacency(inst.n, inst.edges)
    full = A.adjacency(inst.n, inst.edges + inst.fan)
    nodes = set(range(inst.n))
    if a.sep is None:
        return
    if method == "level":
        rows = A.level_profile(adj, nodes, a.sep.root)
        st.markdown(f"**Schichten der Breitensuche ab Knoten {a.sep.root}** (gewählt wird die kleinste ausgewogene Schicht über sechs Wurzeln)")
        st.dataframe(
            [{"Schicht": str(r["level"]), "Knoten": str(r["size"]), "Größte Komponente danach": str(r["largest"]), "Ausgewogen": "ja" if r["balanced"] else "nein"} for r in rows],
            hide_index=True, width="stretch",
        )
    elif method == "cycle":
        rows = A.cycle_profile(full, nodes, a.sep.root, 6)
        st.markdown(
            f"**Die kürzesten Fundamentalkreise des BFS-Baums ab Knoten {a.sep.root}** (auf der ergänzten Triangulierung; die letzte Zeile ist der kürzeste ausgewogene Kreis dieser Wurzel; "
            "gewählt wird der kürzeste ausgewogene Kreis über vier Wurzeln)"
        )
        st.dataframe(
            [{"Platz nach Länge": str(r["rank"]), "Kante außerhalb des Baums": f"{r['edge'][0]}–{r['edge'][1]}", "Länge des Kreises": str(r["length"]), "Größte Komponente danach": str(r["largest"]),
              "Ausgewogen": "ja" if r["balanced"] else "nein"} for r in rows],
            hide_index=True, width="stretch",
        )
    else:
        st.markdown(
            f"**Geometrischer Schnitt:** {a.sep.detail}; {a.sep.cut_edges} Kanten zwischen den Hälften, größtes Matching {a.sep.matching}, "
            f"kleinste Überdeckung dieser Kanten = {len(a.sep.vertices)} Knoten (Satz von König: Überdeckung = Matching)."
        )


# Fester Kopf: nur der Titel bleibt beim Scrollen oben (Stylesheet in psp_layout.py).
st.html(kopf_css(dunkles_design()))
with st.container(key="kopf"):
    st.title("✂️ Planare Separatoren – kleine Trennmengen und Nested Dissection")
st.markdown(
    """
Jeder planare Graph mit n Knoten lässt sich durch Entfernen von höchstens **√(8n)** Knoten so zerlegen, dass jede Komponente höchstens **2n/3** Knoten hat (**Lipton und Tarjan 1979**). Straßennetze und Karten haben also kleine **Trennmengen**, Zufallsgraphen nicht.
Die Demo findet sie auf Karten, Gittern, Zufallsgraphen und einer echten Straßenkarte (Toronto) mit drei Verfahren, **BFS-Schicht**, **Fundamentalkreis** und **geometrischem Schnitt mit König-Überdeckung**, misst, wie nah sie an √n kommen, und fragt, was daraus für Eliminationsordnungen folgt (**Nested Dissection**, Baumweite).
Drittes Stück der Linie *Planarität und Zeichnen*; es setzt auf die Karten des ersten Stücks (`planaritaet-demo`) auf und erklärt, warum Gitter und Straßennetze in der Härte-Reihe (`treewidth-demo`) eine kleine Baumweite haben.

Weiter unten: **🔬 Wächst die Trennmenge mit √n?**, **🔬 Gegenproben**, **🔬 Nested Dissection**, **🔬 Straßenkarte Toronto**, **🚧 Wo die Annahmen enden** und der Expander **📐 Mathematische Formulierung**.
"""
)

with st.expander("So funktionieren die Verfahren", expanded=True):
    st.markdown(
        """
Eine **ausgewogene Trennmenge** ist eine Knotenmenge, nach deren Entfernung jede Komponente höchstens 2n/3 Knoten hat.
1. **BFS-Schicht:** Eine Breitensuche teilt den Graphen in Schichten nach dem Abstand von der Wurzel; eine einzelne Schicht trennt innen von außen. Gewählt wird die kleinste ausgewogene Schicht.
2. **Fundamentalkreis:** Zu einem BFS-Baum gehört für jede Kante außerhalb des Baums ein Kreis (die Kante plus die Baumwege bis zum gemeinsamen Vorfahren). In einer **triangulierten** planaren Karte hat jeder Kreis eine Innen- und eine Außenseite; es gibt immer einen kurzen Kreis, der beide ausgewogen teilt (Miller 1986, die Konstruktion hinter Lipton und Tarjan). Gewählt wird der kürzeste ausgewogene.
3. **Geometrischer Schnitt:** Die Knoten werden am Median der längeren Achse in zwei Hälften geteilt. Die Kanten zwischen den Hälften müssen getroffen werden: die kleinste Knotenmenge dafür ist nach dem **Satz von König** so groß wie ein größtes Matching zwischen den Hälften.
4. **Nested Dissection:** Ein Stück wird an einer Trennmenge geteilt, die Teile werden zuerst geordnet, die Trennmenge zuletzt. Die Eliminationsbreite der Ordnung begrenzt die Baumweite.
        """
    )

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    sidebar_presets()  # Schnellstart oben, das aktive Preset ist hervorgehoben
    st.header("⚙️ Einstellungen")
    st.markdown("**Graph**")
    net = st.selectbox("Netztyp", list(C.NET_TYPES), key="net_select", format_func=C.NET_TYPES.get, help=C.NET_HELP)
    n = st.slider("Knoten n", *bounds("n_slider"), key="n_slider", help="Zahl der Knoten (Gitter und Raster werden auf ein Quadrat gerundet, beim Zufallsgraphen zählt die größte Komponente).")
    seed = st.number_input("Zufalls-Seed der Instanz", *bounds("seed_input"), key="seed_input", step=1)
    st.button("🎲 Neue Instanz generieren", width="stretch", on_click=randomize_seed)
    st.markdown("**Verfahren**")
    method = st.selectbox("Verfahren", list(C.METHODS), key="method_select", format_func=C.METHODS.get, help=C.METHOD_HELP)

sync_query_params({"net_select": net, "n_slider": int(n), "seed_input": int(seed), "method_select": method})

settings = ev.Settings(net, int(n), int(seed), method)
a = _analysis(settings)
inst = a.inst

# --- Ergebnis ------------------------------------------------------------------------------------------------------------------------------

st.markdown("## 🎯 Ergebnis")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Knoten n", f"{inst.n}", delta=f"√n = {ev.num(a.sqrt_n, 1)}", delta_color="off")
m2.metric("Kanten m", f"{inst.m}", delta="planar" if inst.planar else "nicht planar", delta_color="off")
m3.metric("Trennmenge", f"{len(a.sep.vertices)}" if a.sep else "-", delta=f"{ev.num(len(a.sep.vertices) / a.sqrt_n, 2)} √n" if a.sep else None, delta_color="off", help="Größe der Trennmenge und ihr Verhältnis zu √n.")
m4.metric("Größter Teil", f"{a.check.largest}" if a.check else "-", delta=f"Grenze {ev.num(a.check.limit, 1)}" if a.check else None, delta_color="off", help="Größe der größten Komponente nach dem Entfernen; höchstens 2n/3.")
kind, text = ev.verdict_separator(a, method)
getattr(st, kind)(text)
st.plotly_chart(
    build_separator(inst, a.sep, a.components, title=f"{inst.name}: {inst.n} Knoten, {inst.m} Kanten", show_fan=method == "cycle"), width="stretch", key="main_graph",
)
st.caption(
    "Rot: die Trennmenge; blau und gelb: die beiden größten Komponenten danach; hellblau: kleine Reststücke."
    + (" Gepunktet: die Kanten, die die Karte für den Fundamentalkreis zu einer Triangulierung ergänzen; sie gehören nicht zum Graphen." if method == "cycle" and inst.fan else "")
)

# --- Kernfrage -----------------------------------------------------------------------------------------------------------------------------

st.markdown("## ❓ Kernfrage: Wie klein sind Trennmengen planarer Graphen, und was folgt daraus?")
_details(a, inst, method)
st.markdown("### Alle Verfahren auf derselben Instanz")
rows = [{"Verfahren": C.METHODS[method], "Trennmenge": str(len(a.sep.vertices)) if a.sep else "-", "Verhältnis zu √n": ev.num(len(a.sep.vertices) / a.sqrt_n, 2) if a.sep else "-"}]
rows += [{"Verfahren": C.METHODS[m], "Trennmenge": str(v) if v is not None else "-", "Verhältnis zu √n": ev.num(v / a.sqrt_n, 2) if v is not None else "-"} for m, v in a.others.items()]
st.dataframe(rows, hide_index=True, width="stretch")

st.markdown("---")

# --- Experiment 1 --------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Wächst die Trennmenge mit √n?")
st.caption(f"Delaunay-Karten, je Größe {len(C.SWEEP_SEEDS)} feste Karten (Median). Die Schranke des Satzes ist √8 ≈ 2,83 mal √n.")
with st.spinner("Rechne die Messreihe …"):
    scaling = _scaling(C.SCALING_LIVE_NS)
st.plotly_chart(build_scaling(scaling), width="stretch", key="scaling_chart")
kind, text = ev.verdict_scaling(scaling)
getattr(st, kind)(text)
if st.button("📊 Größere Reihe mit n = 1000 rechnen", key="run_scaling"):
    with st.spinner("Rechne die größere Reihe (der Fundamentalkreis braucht bei n = 1000 einige Sekunden je Karte) …"):
        st.session_state["scaling_big"] = _scaling(C.SCALING_NS)
if "scaling_big" in st.session_state:
    big = st.session_state["scaling_big"]
    st.plotly_chart(build_scaling(big, title="Größe der Trennmenge durch √n (bis n = 1000)"), width="stretch", key="scaling_big_chart")
    kind, text = ev.verdict_scaling(big)
    getattr(st, kind)(text)

st.markdown("---")

# --- Experiment 2 --------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Gegenproben: Gitter, Raster und Zufallsgraphen")
st.caption("Gitter und Raster haben k × k Knoten, ihre Trennmenge sollte etwa k sein; ein Zufallsgraph mit Grad 3 ist nicht planar.")
other = _other()
st.dataframe(
    [{"Graph": r["name"], "Knoten": str(r["n"]), "BFS-Schicht": str(r["level"]), "Geometrisch": str(r["geometric"]), "Vergleichswert": f"n = {r['n']}" if r["linear"] else f"k = {r['scale']}"} for r in other],
    hide_index=True, width="stretch",
)
kind, text = ev.verdict_other(other)
getattr(st, kind)(text)

st.markdown("---")

# --- Experiment 3 --------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Nested Dissection: Breite der Ordnung")
st.caption(
    "Nested Dissection zerlegt rekursiv und ordnet die Trennmenge zuletzt; die Breite der Ordnung (Eliminationsspiel mit Auffüllen) ist eine obere Schranke der Baumweite. "
    "Verglichen mit den Heuristiken Mindestgrad und Min-Fill auf reinen Gittern, Karten (Median über drei) und einem Zufallsgraphen. Das Rechnen dauert einen Moment und läuft nur auf Klick."
)
if st.button("📊 Breiten rechnen", key="run_nd"):
    with st.spinner("Rechne die Ordnungen …"):
        st.session_state["nd_rows"] = _nd()
if "nd_rows" in st.session_state:
    nd = st.session_state["nd_rows"]
    st.plotly_chart(build_nd(nd), width="stretch", key="nd_chart")
    st.dataframe(
        [{"Graph": r["name"], "ND geometrisch": ev.num(r["nd_geometric"]), "ND Schicht": ev.num(r["nd_level"]), "ND Kreis": ev.num(r["nd_cycle"]) if "nd_cycle" in r else "-",
          "Mindestgrad": ev.num(r["min_degree"]), "Min-Fill": ev.num(r["min_fill"]), "√n": ev.num(r["sqrt_n"], 1)} for r in nd],
        hide_index=True, width="stretch",
    )
    kind, text = ev.verdict_nd(nd)
    getattr(st, kind)(text)

st.markdown("---")

# --- Experiment 4 --------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Straßenkarte Toronto")
st.markdown(
    "Ein Auszug aus OpenStreetMap (Umkreis von 1 000 m um den St. George Campus, Daten unter ODbL; derselbe wie in der Härte-Reihe): 5 072 Knoten, nicht exakt planar. "
    "Wie klein sind die Trennmengen, und wie breit ist die Nested-Dissection-Ordnung? Das Rechnen dauert einige Sekunden und läuft nur auf Klick."
)
if st.button("🗺️ Toronto-Karte zerlegen", key="run_toronto"):
    with st.spinner("Zerlege die Karte …"):
        st.session_state["toronto"] = _toronto()
t = st.session_state.get("toronto")
if t:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Knoten", ev.num(t["n"]), delta=f"√n = {ev.num(t['sqrt_n'], 1)}", delta_color="off")
    c2.metric("BFS-Schicht", f"{len(t['level'].vertices)}", delta=f"{ev.num(len(t['level'].vertices) / t['sqrt_n'], 2)} √n", delta_color="off")
    c3.metric("Geometrisch", f"{len(t['geometric'].vertices)}", delta=f"{ev.num(len(t['geometric'].vertices) / t['sqrt_n'], 2)} √n", delta_color="off")
    c4.metric("Breite (ND)", f"{t['nd_geometric']}", delta=f"Mindestgrad {t['min_degree']}", delta_color="off")
    kind, text = ev.verdict_toronto(t)
    getattr(st, kind)(text)
    st.plotly_chart(build_toronto(t), width="stretch", key="toronto_chart")
    st.caption("Rot: die kleinste ausgewogene BFS-Schicht; orange: die Trennmenge des geometrischen Schnitts (Median der längeren Achse).")

st.markdown("---")

# --- Grenzen -------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    """
| Annahme | Was passiert, wenn sie verletzt ist | Wer setzt an |
|---|---|---|
| **Der Graph ist planar** | Der Satz braucht es. Beim Zufallsgraphen mit Grad 3 ist die Trennmenge ein Teil der Knoten (rund jeder fünfte bis dritte), nicht √n. Die Toronto-Karte ist nicht exakt planar und verhält sich trotzdem wie ein planarer Graph. | - |
| **Die Karte ist trianguliert** | Die Schranke √(8n) für den Fundamentalkreis gilt nur dort; die Demo ergänzt die Karte durch einen Fächer von einer Hüllenecke und sucht auf dem ergänzten Graphen. Die Trennmenge gilt auch für den Originalgraphen, kann dort aber etwas über dem Optimum liegen. Auf Gittern und Zufallsgraphen gibt es keine Garantie. | - |
| **Die Knoten haben eine Lage** | Der geometrische Schnitt braucht Koordinaten. Beim Zufallsgraphen liegen die Knoten auf einem Kreis, die Lage sagt nichts über die Struktur. | - |
| **Kleine Trennmenge heißt gute Ordnung** | Nein: Nested Dissection mit dem kürzesten Kreis hat auf Karten eine größere Breite als mit dem geometrischen Schnitt, und die Heuristiken Mindestgrad und Min-Fill sind meist ebenso gut. Der Gewinn von Nested Dissection ist die Garantie O(√n). | - |
| **Das Kreisverfahren ist schnell** | Nein: Es probiert Kreise nach Länge und prüft jeden durch Entfernen und Zählen; bei n = 1000 dauert das einige Sekunden je Karte. Die Verfahren von Lipton–Tarjan und Miller laufen in linearer Zeit und sind hier nicht nachgebaut. | - |
"""
)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Gegeben** ein ungerichteter Graph $G=(V,E)$ mit $n=|V|$ Knoten; **gesucht** eine Menge $S\subseteq V$, nach deren Entfernung jede Komponente von $G-S$ höchstens $\tfrac{2}{3}n$ Knoten hat, und möglichst klein.

| Symbol | Bedeutung |
|---|---|
| $S$ | Trennmenge (Separator) |
| $G-S$ | Graph ohne die Knoten von $S$ |
| BFS-Baum $T$ | Baum der Breitensuche ab einer Wurzel $r$, Tiefe $h$ |
| Fundamentalkreis $C_e$ | zur Kante $e=uv\notin T$ der Kreis aus $e$ und den Baumwegen $u\to \mathrm{lca}$, $v\to \mathrm{lca}$; Länge $\le 2h+1$ |
| $M$, $\tau$ | größtes Matching bzw. kleinste Knotenüberdeckung des bipartiten Schnittgraphen |

**Satz (Lipton und Tarjan 1979).** Jeder planare Graph mit $n$ Knoten hat eine Trennmenge mit $|S|\le 2\sqrt{2}\sqrt{n}=\sqrt{8n}$, nach deren Entfernung jede Komponente höchstens $\tfrac23 n$ Knoten hat.

**Fundamentalkreis (Miller 1986).** In einer 2-fach zusammenhängenden triangulierten planaren Karte gibt es eine Kante $e\notin T$, deren Kreis $C_e$ Innen- und Außenseite je höchstens $\tfrac23 n$ Knoten gibt und höchstens $2\sqrt2\sqrt n$ Knoten hat. Gesucht wird in der Demo der kürzeste Kreis mit dieser Eigenschaft, per Aufzählung der Kreise und Zählen der Komponenten.

**Satz von König.** In einem bipartiten Graphen ist $\tau=\nu$, die Größe der kleinsten Knotenüberdeckung ist die des größten Matchings. Der geometrische Schnitt ($L$ = erste Hälfte nach der Koordinate) trifft alle Schnittkanten $E(L,V\setminus L)$ mit einer Überdeckung der Größe $\nu$; die Komponenten danach haben höchstens $\lceil n/2\rceil$ Knoten.

**Nested Dissection (George 1973).** $\mathrm{ND}(G)$: ist $G$ klein, ordne nach Mindestgrad; sonst finde $S$, ordne $\mathrm{ND}$ jeder Komponente von $G-S$, danach $S$. Die Breite einer Ordnung $\sigma$ ist der größte Grad eines Knotens im Moment seiner Elimination im Eliminationsspiel (Nachbarn werden zur Clique); sie ist eine obere Schranke der Baumweite. Mit Trennmengen der Größe $O(\sqrt{n})$ in allen Teilgraphen ist die Breite $O(\sqrt n)$.

**Literatur.** R. J. Lipton, R. E. Tarjan, *A separator theorem for planar graphs*, SIAM Journal on Applied Mathematics 36(2) (1979), 177–189 (Konstante $2\sqrt2\sqrt n$; Djidjev verbesserte sie auf $\sqrt6\sqrt n$, nach einer Zusammenfassung mit einer Untergrenze von etwa $0{,}8\sqrt n$). G. L. Miller, *Finding small simple cycle separators for 2-connected planar graphs*, Journal of Computer and System Sciences 32(3) (1986), 265–279. A. George, *Nested dissection of a regular finite element mesh*, SIAM Journal on Numerical Analysis 10(2) (1973), 345–363. Die Angaben wurden per Suche gegen Bibliografie-Einträge und Zusammenfassungen geprüft, die Originalarbeiten nicht gelesen.
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html)."
)
