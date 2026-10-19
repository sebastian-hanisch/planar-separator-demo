# Planare Separatoren – kleine Trennmengen und Nested Dissection – Streamlit-Demo

<!-- TODO nach dem Deploy: direkt hierher den Live-Link setzen (Leerzeile davor und danach):
**[→ Demo live ausprobieren](https://sebastianhanisch-planar-separator-demo.streamlit.app/)** -->

Drittes Stück der **Planarität-und-Zeichnen-Linie** (Graphentheorie) in der „Konzepte“-Reihe für die Website „Sebastian Hanisch – Operations Research und Machine Learning“. Es setzt auf die Karten des ersten Stücks [planaritaet-demo](https://github.com/sebastian-hanisch/planaritaet-demo) auf (Delaunay-Karten, Toronto-Daten) und erklärt, warum Gitter und Straßennetze in der Härte-Reihe ([treewidth-demo](https://github.com/sebastian-hanisch/treewidth-demo), [tree-decomposition-dp-demo](https://github.com/sebastian-hanisch/tree-decomposition-dp-demo)) eine kleine Baumweite haben. Verwandt: [customizable-ch-demo](https://github.com/sebastian-hanisch/customizable-ch-demo) nutzt verschachtelte Zerlegung nach Koordinaten als Ordnung; dort werden Trennmengen nicht gemessen, hier sind sie das Thema.

Jeder planare Graph mit n Knoten hat eine **Trennmenge** aus höchstens √(8n) Knoten, nach deren Entfernung jede Komponente höchstens 2n/3 Knoten hat (Lipton und Tarjan 1979). Die Demo findet Trennmengen mit drei Verfahren, **BFS-Schicht**, **Fundamentalkreis** (kürzester ausgewogener Kreis eines BFS-Baums in einer triangulierten Karte) und **geometrischem Schnitt** am Median mit der kleinsten Knotenüberdeckung der Schnittkanten (Satz von König), misst, wie nah sie an √n kommen, und fragt, was für die Eliminationsordnung **Nested Dissection** folgt. Eigene Löser in Python, `networkx` nur als Gegenprobe in den Tests.

## Warum dieses Problem

Karten, Straßennetze und Leiterplatten lassen sich an wenigen Stellen in zwei Hälften zerlegen; das macht Divide-and-Conquer und Eliminationsverfahren auf ihnen billig. Kernfrage: **wie klein sind die Trennmengen wirklich, welche Verfahren finden sie, und was folgt für die Baumweite?**

## Modell

Ein einfacher ungerichteter Graph. Eine Trennmenge S ist **ausgewogen**, wenn jede Komponente von G − S höchstens 2n/3 Knoten hat; ein unabhängiger Prüfer rechnet das nach. **BFS-Schicht:** die kleinste ausgewogene Schicht einer Breitensuche über sechs Wurzeln. **Fundamentalkreis:** zu einem BFS-Baum gehört für jede Kante außerhalb des Baums ein Kreis; gewählt wird der kürzeste ausgewogene über vier Wurzeln; die Karte ist durch einen Fächer von einer Hüllenecke aus zu einer vollständigen Triangulierung ergänzt (Schranke des Satzes), die Trennmenge gilt auch für den Originalgraphen. **Geometrisch:** Median der längeren Achse, Überdeckung der Schnittkanten nach König. **Nested Dissection:** ein Stück wird an einer Trennmenge geteilt, die Teile werden zuerst geordnet, die Trennmenge zuletzt (Blätter bis vier Knoten nach Mindestgrad); die **Breite** einer Ordnung ist der größte Grad eines Knotens im Eliminationsspiel, eine obere Schranke der Baumweite. Formeln und Literatur im Expander „📐 Mathematische Formulierung“.

Netztypen: **Karte** (Delaunay-Triangulierung zufälliger Standorte), **Raster mit Diagonalen** und **Gitter** (k × k), **Zufallsgraph** (mittlerer Grad 3, größte Komponente, nicht planar) und die **Toronto-Karte** (OpenStreetMap, ODbL, 5.072 Knoten, aus `bfs-demo`).

## Methodik

- **Eine Instanz:** alle drei Verfahren, Prüfer, Tabellen der Schichten, der kürzesten Kreise und der Schnittkanten.
- **Messreihen:** (1) Trennmenge gegen √n auf Karten (n = 100 und 300 live, n = 1.000 auf Klick; je 6 feste Karten, Median), (2) Gegenproben (Gitter, Raster, Zufallsgraphen), (3) Nested Dissection gegen Mindestgrad und Min-Fill (reine Gitter, Karten, Zufallsgraph), (4) Toronto.

## Befunde (gemessen, keine Behauptungen)

| Frage | Befund | Test |
|---|---|---|
| Wie groß sind Trennmengen auf Karten? | n = 100 / 300 / 1.000: **Fundamentalkreis 10 / 16 / 26 Knoten** (1,00 / 0,92 / 0,82 √n), **geometrisch 11 / 18,5 / 31,5** (1,10 / 1,07 / 1,00 √n), **BFS-Schicht 13 / 28 / 72** (1,30 / 1,62 / 2,28 √n). Die Schicht wächst schneller als √n, der Kreis bleibt darunter. | `test_separator_sizes_on_maps`, `test_ratios_to_sqrt_n_and_the_theorem_bound` |
| Hält der Kreis die Schranke des Satzes? | Ja: √(8n) in 6 von 6 Karten je Größe (n = 100, 300, 1.000) und in 60 Karten des Eigenschaftstests (n = 20 bis 250); der Kreis liegt bei etwa einem Drittel der Schranke. | `test_ratios_to_sqrt_n_and_the_theorem_bound`, `test_the_cycle_separator_keeps_the_lipton_tarjan_bound_on_triangulated_maps` |
| Gitter und Raster? | Die Trennmenge ist etwa k bei k × k Knoten: Gitter 10 / 20 / 30: Schicht 8 / 16 / 24, geometrisch 10 / 20 / 30; Raster mit Diagonalen: Schicht 8 / 20 / 24, geometrisch 10 / 20 / 30. | `test_lattice_raster_and_random_graph_separators` |
| Ohne Planarität? | Zufallsgraph (mittlerer Grad 3): bei 372 Knoten braucht die Schicht 70 (19 %), der geometrische Schnitt 132 (35 %): **ein fester Anteil**, nicht √n. | `test_lattice_raster_and_random_graph_separators` |
| Wie ist die Toronto-Karte? | 5.072 Knoten (√n = 71,2): Schicht **83** (1,17 √n), geometrisch **57** (0,80 √n), beide geprüft ausgewogen: die nicht exakt planare Karte verhält sich wie ein planarer Graph. | `test_toronto_separators_and_widths` |
| Gibt Nested Dissection eine bessere Breite? | **Nein, meist nicht:** reine Gitter 8 / 12 / 16 / 24: Nested Dissection (geometrisch) 11 / 17 / 23 / 35, Mindestgrad 10 / 16 / 23 / 37, Min-Fill 10 / 16 / 22 / 37; erst beim 24 × 24-Gitter ist Nested Dissection vorn (34 und 35 gegen 37). Karten n = 100 / 200 / 300: ND geometrisch 15 / 23 / 27, Min-Fill 13 / 19 / 24. Toronto: 73 gegen Mindestgrad 57. Der Gewinn ist die Garantie O(√n), nicht die Breite. | `test_nested_dissection_widths_on_lattices_maps_and_the_random_graph`, `test_toronto_separators_and_widths` |
| Gibt die kleinste Trennmenge die beste Ordnung? | **Nein:** Nested Dissection mit Fundamentalkreisen hat auf Karten n = 100 / 200 / 300 die Breite 20 / 27 / 35, mit dem geometrischen Schnitt 15 / 23 / 27. | `test_nested_dissection_widths_on_lattices_maps_and_the_random_graph` |
| Und ohne Planarität? | Am Zufallsgraphen (276 Knoten) bricht Nested Dissection ein: Breite 67 gegen Mindestgrad 34 und Min-Fill 30 (mehr als 4 √n). | `test_nested_dissection_widths_on_lattices_maps_and_the_random_graph` |

## Ehrliche Grenzen

- **Kein Linearzeit-Verfahren.** Lipton–Tarjan und Miller arbeiten in linearer Zeit; das Kreisverfahren hier probiert Kreise nach Länge und prüft jeden (bei n = 1.000 einige Sekunden je Karte, deshalb auf Klick). Verglichen werden Größen, keine Laufzeiten.
- **Die Triangulierung ist ergänzt.** Der Fächer ist kein Teil der Karte; die Trennmenge gilt auch für das Original, kann dort aber etwas größer sein als nötig. Auf Gittern, Rastern und Zufallsgraphen hat der Kreis keine Garantie.
- **Nested Dissection ist hier kein Sieger.** Mindestgrad und Min-Fill sind auf den gemessenen Gittern und Karten gleich oder besser; die Baumweite des k × k Gitters ist k, und keine Ordnung liegt darunter.
- **Min-Fill hängt vom Gleichstand ab** (kleinster Grad, dann kleinste Nummer); mit anderer Regel ändern sich einzelne Breiten um wenige Punkte.
- **Kleine Stichprobe:** 6 feste Karten je Größe in den Größenreihen, 3 in der Nested-Dissection-Reihe (Median); Bänder in den Tests.

## Befunde und Korrekturen gegenüber dem Plan

- **BFS-Schicht:** die Vormessung im Einzelplan lief auf der ergänzten Triangulierung (mit Fächerkanten) und fand 18 / 35 / 74,5 Knoten bei n = 100 / 300 / 1.000; die Demo sucht die Schicht auf dem Originalgraphen und findet 13 / 28 / 72 (1,30 bis 2,28 √n statt 1,8 bis 2,5 √n). Die Tendenz (wächst schneller als √n) bleibt.
- **Nested Dissection auf Karten:** die Vormessung nutzte die ergänzte Triangulierung und andere Karten; die Demo misst auf dem Originalgraphen (Breiten 15 / 23 / 27 gegen 14 bis 29 in der Vormessung). Min-Fill ist in der Demo eine eigene Umsetzung mit anderer Gleichstandsregel als in `treewidth-demo` (24 × 24-Gitter: 37 statt 35); der Befund „Nested Dissection gewinnt nicht“ gilt in beiden.
- **Zufallsgraph:** die Vormessung fand 19 % Schicht bei n = 959; die Demo (kleinere Zufallsgraphen, n = 93 bis 372) 15 bis 25 % (Schicht).

## Verifikation

- **Kern gegen Handrechnung:** Komponenten, Prüfer (2n/3 inklusive), BFS-Schichten, Schichttrennmenge an Pfad, Stern und 3 × 3 Gitter, Schichtprofil, BFS-Baum, Fundamentalkreise am Sechseck mit Sehne, Median-Schnitt, Matching mit erweiterndem Weg, König-Überdeckung, geometrische Trennmenge, Eliminationsbreiten, Nested Dissection am Pfad (`tests/test_algorithm.py`).
- **Orakel:** `tests/test_oracle_planar_separator.py`: jede Trennmenge ausgewogen nach `networkx`, König-Überdeckung gleich größtem Matching (`networkx`) und kleinste Überdeckung nach Brute Force, BFS-Schichten gleich `networkx.bfs_layers`, Fundamentalkreise sind Kreise von höchstens 2 · Tiefe + 1 Knoten, die Schranke √(8n) auf 60 triangulierten Karten, Eliminationsbreite gleich der Cliquenzahl des chordalen Abschlusses minus eins, keine Ordnung unter der Baumweite des Gitters, Nested-Dissection-Ordnungen sind Permutationen für jedes Verfahren und jeden Netztyp.
- **Mutationsprüfung** (`tools/mutate_demo.py`, Stand vor dem ersten Commit): 126 von 129 Stellen des Kerns gesichert (gefangen oder als äquivalent festgehalten, `tests/mutation_state.json`), keine offene Lücke; 3 Mutanten ergaben Endlosschleifen (Zeitüberschreitung, zählt nicht). Die äquivalenten sind Sortierreihenfolgen, Schleifengrenzen und unerreichbare Zweige, die das Ergebnis nicht ändern.
- **Randfälle:** leerer Graph, ein und zwei Knoten, Dreieck, gleiche Lagen, Reihenfolge der Kantenliste, großes Blatt, unzusammenhängender Graph, alle Ecken der Regler (`tests/test_edge_cases.py`).
- **Verdikte** als reine Funktionen, jede Zahl (`tests/test_verdicts.py`); **Claims:** jede Zahl dieser README (`tests/test_claims.py`).
- **Szenario:** Delaunay-Karte plus Fächer ist maximal planar (3n − 6 Kanten), Hash-Seed-Unabhängigkeit, Toronto-Daten (`tests/test_scenario.py`); Darstellung (`tests/test_visualization.py`); Presets halten, was ihre Hilfetexte sagen (`tests/test_presets.py`).
- **Oberfläche:** AppTest-Rauchtest (jeder Button, jeder Regler an beiden Enden, jede Kombination aus Netztyp und Verfahren), Layout, Footer, Laufzeit-Importe.

## Dateistruktur

| Datei | Zweck |
|---|---|
| `.github/workflows/tests.yml` | CI: Push, Pull Request, wöchentlicher Canary |
| `.gitignore` | venv, Caches, Streamlit-Secrets |
| `.streamlit/config.toml` | Streamlit-Einstellungen (keine Nutzungsstatistik) |
| `app.py` | Streamlit-App |
| `psp_algorithm.py` | Kern: Prüfer, BFS-Schicht, Fundamentalkreis, geometrischer Schnitt mit König, Nested Dissection, Eliminationsbreite |
| `psp_constants.py` | Regler-Grenzen, Rechengrenzen, Farben, Presets |
| `psp_evaluation.py` | Analyse einer Instanz, Messreihen, Toronto, Verdikte, deutsche Zahlenformate |
| `psp_layout.py` | Fester Kopf (Stylesheet) |
| `psp_presets.py` | Permalink (Begrenzen), Presets (Schnellstart in der Seitenleiste), Zufalls-Seed-Button |
| `psp_scenario.py` | Instanzen: Karte mit Fächer, Gitter, Raster, Zufallsgraph, Toronto |
| `psp_visualization.py` | Plotly-Abbildungen (Achsen gesperrt) |
| `data/toronto_campus.json`, `data/LICENSE-ODbL.md` | OpenStreetMap-Auszug (ODbL) aus `bfs-demo` |
| `requirements-dev.txt` | Laufzeit plus pytest und networkx (Gegenprobe) |
| `requirements.txt` | Laufzeit-Bibliotheken (ungepinnt) |
| `tests/` | Handrechnung, Orakel, Randfälle, Verdikte, Claims, Szenario, Darstellung, Presets, Layout, AppTest, Footer, Laufzeit-Importe |

## Bewusst nicht umgesetzt

- Die Linearzeit-Verfahren von Lipton und Tarjan und von Miller (Einordnung statt Nachbau).
- Eine Trennmenge, die die kleinste mögliche ist (das Minimum ist NP-schwer; die Demo findet die besten ihrer Verfahren).
- Flussbasierte Trennmengen und Mehrebenen-Verfahren wie METIS.
- Eine Anwendung der Zerlegung als Divide-and-Conquer-Rechnung (etwa für die unabhängige Menge).

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Gebaut mit Streamlit, Plotly, NumPy und SciPy (Delaunay-Triangulierung der Standorte).

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html).
