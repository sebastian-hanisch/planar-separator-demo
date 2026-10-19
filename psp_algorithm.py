"""Kern: Trennmengen in planaren Graphen (BFS-Schicht, Fundamentalkreis, geometrischer Schnitt mit König-Überdeckung), Prüfer, Nested Dissection und Eliminationsbreite.

Eine Einheit ist eine Regel: Komponenten bestimmen, Trennmenge prüfen, Schichten bilden, eine Schicht wählen, einen BFS-Baum bauen, einen Fundamentalkreis bilden,
am Median schneiden, ein Matching suchen, die Überdeckung ableiten, rekursiv zerlegen, eliminieren. Kein Zufall, keine Modul-Globals; Gleichstand entscheidet die
kleinere Knotennummer. Graphen sind einfach und ungerichtet (Nachbarmengen), Knoten 0 bis n − 1; `nodes` ist die Menge, auf die sich eine Rechnung beschränkt.

Eine **Trennmenge** S eines Graphen mit n Knoten heißt hier ausgewogen, wenn nach ihrer Entfernung jede Komponente höchstens 2n/3 Knoten hat (Satz von Lipton und Tarjan)."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass


def adjacency(n: int, edges) -> list[set[int]]:
    adj: list[set[int]] = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    return adj


def components(adj, nodes) -> list[set[int]]:
    """Zusammenhangskomponenten des von `nodes` induzierten Teilgraphen, nach kleinster Knotennummer geordnet."""
    nodes = set(nodes)
    seen: set[int] = set()
    found = []
    for s in sorted(nodes):
        if s in seen:
            continue
        comp = {s}
        seen.add(s)
        queue = deque([s])
        while queue:
            x = queue.popleft()
            for y in adj[x]:
                if y in nodes and y not in seen:
                    seen.add(y)
                    comp.add(y)
                    queue.append(y)
        found.append(comp)
    return found


def largest_component_after(adj, nodes, sep) -> int:
    """Größe der größten Komponente nach Entfernen der Trennmenge (0, wenn nichts übrig bleibt)."""
    rest = set(nodes) - set(sep)
    return max((len(c) for c in components(adj, rest)), default=0)


@dataclass(frozen=True)
class SepCheck:
    size: int
    largest: int                 # größte Komponente nach der Entfernung
    limit: float                 # 2n/3
    balanced: bool
    sides: tuple[int, ...]       # Größen aller Komponenten, absteigend


def check_separator(adj, nodes, sep) -> SepCheck:
    """Unabhängiger Prüfer: hat nach dem Entfernen jede Komponente höchstens 2n/3 Knoten?"""
    nodes = set(nodes)
    sizes = sorted((len(c) for c in components(adj, nodes - set(sep))), reverse=True)
    limit = 2 * len(nodes) / 3
    largest = sizes[0] if sizes else 0
    return SepCheck(len(set(sep)), largest, limit, largest <= limit, tuple(sizes))


@dataclass(frozen=True)
class Separator:
    vertices: tuple[int, ...]
    method: str                  # "level", "cycle" oder "geometric"
    detail: str = ""             # kurze Beschreibung für die Anzeige (Wurzel und Schicht, Kante des Kreises, Achse)
    cycle: tuple[int, ...] = ()  # beim Fundamentalkreis die Knoten in Umlaufreihenfolge
    cut_edges: int = 0           # beim geometrischen Schnitt: Zahl der Schnittkanten
    matching: int = 0            # beim geometrischen Schnitt: Größe des größten Matchings (= Größe der Überdeckung nach König)
    root: int = -1               # bei Schicht und Fundamentalkreis: die Wurzel der Breitensuche


# --- BFS-Schicht ------------------------------------------------------------------------------------------------------------------------------


def bfs_levels(adj, root: int, nodes) -> list[list[int]]:
    """Schichten der Breitensuche ab `root` im induzierten Teilgraphen (Schicht d: Abstand d, sortiert); nur der erreichte Teil."""
    nodes = set(nodes)
    dist = {root: 0}
    queue = deque([root])
    while queue:
        x = queue.popleft()
        for y in adj[x]:
            if y in nodes and y not in dist:
                dist[y] = dist[x] + 1
                queue.append(y)
    depth = max(dist.values())
    return [sorted(v for v, d in dist.items() if d == k) for k in range(depth + 1)]


def default_roots(nodes, count: int = 6) -> list[int]:
    """Gleichmäßig über die Knotennummern verteilte Wurzeln (höchstens `count`)."""
    ordered = sorted(nodes)
    return ordered[:: max(1, len(ordered) // count)]


def level_profile(adj, nodes, root: int) -> list[dict]:
    """Je Schicht ab `root`: Größe, größte Komponente nach dem Entfernen, und ob sie ausgewogen ist (zum Anzeigen)."""
    nodes = set(nodes)
    limit = 2 * len(nodes) / 3
    rows = []
    for d, level in enumerate(bfs_levels(adj, root, nodes)):
        largest = largest_component_after(adj, nodes, level)
        rows.append({"level": d, "size": len(level), "largest": largest, "balanced": largest <= limit and len(level) < len(nodes)})
    return rows


def level_separator(adj, nodes, roots=None) -> Separator | None:
    """Kleinste ausgewogene BFS-Schicht über alle Wurzeln (Gleichstand: kleinere Wurzel, dann kleinere Schicht); None, wenn keine existiert."""
    nodes = set(nodes)
    n = len(nodes)
    best = None
    for root in roots if roots is not None else default_roots(nodes):
        levels = bfs_levels(adj, root, nodes)
        if sum(len(lv) for lv in levels) < n:
            continue                                            # nicht zusammenhängend ab dieser Wurzel
        for d, level in enumerate(levels):
            if len(level) >= n:
                continue
            if largest_component_after(adj, nodes, level) <= 2 * n / 3:
                key = (len(level), root, d)
                if best is None or key < best[0]:
                    best = (key, level)
    if best is None:
        return None
    (size, root, d), level = best
    return Separator(tuple(level), "level", f"Schicht {d} ab Wurzel {root}", root=root)


# --- Fundamentalkreis -------------------------------------------------------------------------------------------------------------------------


def bfs_tree(adj, root: int, nodes) -> tuple[dict[int, int | None], dict[int, int]]:
    """BFS-Baum ab `root` (Nachbarn aufsteigend): Elternknoten und Tiefe."""
    nodes = set(nodes)
    parent: dict[int, int | None] = {root: None}
    depth = {root: 0}
    queue = deque([root])
    while queue:
        x = queue.popleft()
        for y in sorted(adj[x]):
            if y in nodes and y not in parent:
                parent[y] = x
                depth[y] = depth[x] + 1
                queue.append(y)
    return parent, depth


def fundamental_cycle(parent, depth, u: int, v: int) -> list[int]:
    """Der Kreis aus der Nicht-Baumkante uv und den Baumwegen von u und v bis zum gemeinsamen Vorfahren, ab u in Umlaufreihenfolge."""
    a, b = u, v
    left, right = [a], [b]
    while a != b:
        if depth[a] >= depth[b]:
            a = parent[a]
            left.append(a)
        else:
            b = parent[b]
            right.append(b)
    # left endet im gemeinsamen Vorfahren, right ebenfalls: Umlauf u … Vorfahr … v
    return left + right[-2::-1]


def cycle_candidates(adj, nodes, root: int) -> list[tuple[int, int, int, list[int]]]:
    """Alle Fundamentalkreise zum BFS-Baum ab `root`, nach Länge, dann Kante geordnet: (Länge, u, v, Kreis)."""
    nodes = set(nodes)
    parent, depth = bfs_tree(adj, root, nodes)
    tree = {(min(v, p), max(v, p)) for v, p in parent.items() if p is not None}
    found = []
    for u in sorted(parent):
        for v in sorted(adj[u]):
            if v in parent and u < v and (u, v) not in tree:
                cyc = fundamental_cycle(parent, depth, u, v)
                found.append((len(cyc), u, v, cyc))
    found.sort(key=lambda c: (c[0], c[1], c[2]))
    return found


def cycle_profile(adj, nodes, root: int, limit: int = 6) -> list[dict]:
    """Die `limit` kürzesten Fundamentalkreise ab `root` mit der größten Komponente nach dem Entfernen und, falls der erste ausgewogene Kreis weiter hinten liegt,
    dieser als letzte Zeile (`rank` = Platz unter allen Kreisen nach Länge; zum Anzeigen)."""
    nodes = set(nodes)
    bound = 2 * len(nodes) / 3
    rows = []
    found_balanced = False
    for rank, (length, u, v, cyc) in enumerate(cycle_candidates(adj, nodes, root), start=1):
        largest = largest_component_after(adj, nodes, cyc)
        balanced = largest <= bound
        if rank <= limit or (balanced and not found_balanced):
            rows.append({"rank": rank, "edge": (u, v), "length": length, "largest": largest, "balanced": balanced})
        found_balanced = found_balanced or balanced
        if rank >= limit and found_balanced:
            break
    return rows


def cycle_separator(adj, nodes, roots=None) -> Separator | None:
    """Kürzester ausgewogener Fundamentalkreis über alle Wurzeln (Kandidaten nach Länge); None, wenn der Graph keinen Kreis hat oder keiner ausgewogen ist."""
    nodes = set(nodes)
    n = len(nodes)
    best = None
    for root in roots if roots is not None else default_roots(nodes, 4):
        for length, u, v, cyc in cycle_candidates(adj, nodes, root):
            if best is not None and length >= best[0][0]:
                break
            if largest_component_after(adj, nodes, cyc) <= 2 * n / 3:
                best = ((length, root, u, v), cyc)
                break
    if best is None:
        return None
    (length, root, u, v), cyc = best
    return Separator(tuple(sorted(cyc)), "cycle", f"Kante {u}–{v} ab Wurzel {root}", tuple(cyc), root=root)


# --- Geometrischer Schnitt und König -----------------------------------------------------------------------------------------------------------


def median_cut(pos, nodes) -> tuple[int, set[int]]:
    """Achse mit der größeren Ausdehnung (bei Gleichstand x), kleinere Hälfte nach (Koordinate, Nummer): gibt die Achse (0 oder 1) und die linke Hälfte zurück."""
    ordered = sorted(nodes)
    spans = [max(pos[v][a] for v in ordered) - min(pos[v][a] for v in ordered) for a in (0, 1)]
    axis = 0 if spans[0] >= spans[1] else 1
    by_axis = sorted(ordered, key=lambda v: (pos[v][axis], v))
    return axis, set(by_axis[: len(by_axis) // 2])


def cut_edges(adj, nodes, left) -> list[tuple[int, int]]:
    """Kanten zwischen der linken Hälfte und dem Rest: (links, rechts), sortiert."""
    nodes = set(nodes)
    return sorted((u, v) for u in left for v in adj[u] if v in nodes and v not in left)


def max_matching(edges) -> dict[int, int]:
    """Größtes Matching im bipartiten Graphen der Kanten (links, rechts) durch erweiternde Wege (Kuhn); gibt rechts → links zurück."""
    nbrs: dict[int, list[int]] = {}
    for u, v in edges:
        nbrs.setdefault(u, []).append(v)
    match_right: dict[int, int] = {}

    def augment(u: int, seen: set[int]) -> bool:
        for v in nbrs[u]:
            if v in seen:
                continue
            seen.add(v)
            if v not in match_right or augment(match_right[v], seen):
                match_right[v] = u
                return True
        return False

    for u in sorted(nbrs):
        augment(u, set())
    return match_right


def koenig_cover(edges, match_right: dict[int, int]) -> set[int]:
    """Kleinste Knotenüberdeckung der bipartiten Kanten aus einem größten Matching (Satz von König): von den ungematchten linken Knoten aus alternierend erreichbar = Z;
    Überdeckung = (links ohne Z) ∪ (rechts in Z)."""
    nbrs: dict[int, list[int]] = {}
    for u, v in edges:
        nbrs.setdefault(u, []).append(v)
    matched_left = set(match_right.values())
    reached_left = {u for u in nbrs if u not in matched_left}
    reached_right: set[int] = set()
    queue = deque(sorted(reached_left))
    while queue:
        u = queue.popleft()
        for v in nbrs[u]:
            if v not in reached_right:
                reached_right.add(v)
                w = match_right.get(v)
                if w is not None and w not in reached_left:
                    reached_left.add(w)
                    queue.append(w)
    return (set(nbrs) - reached_left) | reached_right


def geometric_separator(adj, pos, nodes) -> Separator | None:
    """Median-Schnitt entlang der längeren Achse; Trennmenge = kleinste Knotenüberdeckung der Schnittkanten (König). None, wenn nichts zu schneiden ist."""
    nodes = set(nodes)
    axis, left = median_cut(pos, nodes)
    edges = cut_edges(adj, nodes, left)
    if not edges:
        return None
    match = max_matching(edges)
    cover = koenig_cover(edges, match)
    return Separator(tuple(sorted(cover)), "geometric", f"Median auf Achse {'xy'[axis]}", (), len(edges), len(match))


def find_separator(method: str, adj, nodes, pos, adj_cycle=None) -> Separator | None:
    """Ein Verfahren nach Namen; der Fundamentalkreis kann auf einer ergänzten (triangulierten) Nachbarschaft `adj_cycle` suchen."""
    if method == "level":
        return level_separator(adj, nodes)
    if method == "cycle":
        return cycle_separator(adj_cycle if adj_cycle is not None else adj, nodes)
    if method == "geometric":
        return geometric_separator(adj, pos, nodes)
    raise ValueError(f"unbekanntes Verfahren: {method}")


# --- Nested Dissection und Eliminationsbreite ---------------------------------------------------------------------------------------------------


def min_degree_order(adj, nodes=None) -> list[int]:
    """Mindestgrad-Ordnung (Eliminationsspiel mit Auffüllen, Gleichstand: kleinste Nummer) auf dem induzierten Teilgraphen."""
    nodes = set(range(len(adj))) if nodes is None else set(nodes)
    h = {v: set(adj[v]) & nodes for v in nodes}
    order = []
    while h:
        v = min(h, key=lambda x: (len(h[x]), x))
        order.append(v)
        _eliminate(h, v)
    return order


def _fill(h: dict[int, set[int]], x: int) -> int:
    """Zahl der Sehnen, die das Eliminieren von x einfügen würde (fehlende Kanten zwischen seinen Nachbarn)."""
    nb = sorted(h[x])
    return sum(1 for i in range(len(nb)) for j in range(i + 1, len(nb)) if nb[j] not in h[nb[i]])


def min_fill_order(adj, nodes=None) -> list[int]:
    """Min-Fill-Ordnung: stets der Knoten, dessen Elimination die wenigsten Sehnen einfügt (Gleichstand: kleinster Grad, dann kleinste Nummer).
    Nach jedem Schritt werden nur die Knoten neu bewertet, deren Nachbarschaft sich geändert hat (die Nachbarn des entfernten Knotens und deren Nachbarn)."""
    nodes = set(range(len(adj))) if nodes is None else set(nodes)
    h = {v: set(adj[v]) & nodes for v in nodes}
    fills = {v: _fill(h, v) for v in h}
    order = []
    while h:
        v = min(h, key=lambda x: (fills[x], len(h[x]), x))
        order.append(v)
        nb = sorted(h[v])
        affected = set(nb)
        for w in nb:
            affected |= h[w]
        _eliminate(h, v)
        del fills[v]
        for x in affected:
            if x in h:
                fills[x] = _fill(h, x)
    return order


def _eliminate(h: dict[int, set[int]], v: int) -> int:
    """Eliminiert v im Wörterbuch h: Nachbarn werden zur Clique, v verschwindet; gibt den Grad von v zurück."""
    nb = sorted(h[v])
    for i in range(len(nb)):
        for j in range(i + 1, len(nb)):
            h[nb[i]].add(nb[j])
            h[nb[j]].add(nb[i])
    for w in nb:
        h[w].discard(v)
    del h[v]
    return len(nb)


def elimination_width(adj, order) -> int:
    """Breite einer Eliminationsordnung: größter Grad eines Knotens im Moment seiner Elimination (Eliminationsspiel mit Auffüllen)."""
    if sorted(order) != list(range(len(adj))):
        raise ValueError("die Ordnung muss jeden Knoten genau einmal enthalten")
    h = {v: set(adj[v]) for v in range(len(adj))}
    return max((_eliminate(h, v) for v in order), default=0)


@dataclass(frozen=True)
class NDResult:
    order: list[int]
    pieces: list[tuple[int, int, str]]   # (Knoten des Stücks, Größe der Trennmenge, Verfahren oder Rückfall) je Zerlegungsschritt
    fallbacks: int                       # wie oft das gewählte Verfahren keine Trennmenge fand und der Rückfall nötig war


def nested_dissection(adj, pos, method: str, leaf: int = 4, adj_cycle=None) -> NDResult:
    """Nested Dissection: ein zusammenhängendes Stück wird an einer Trennmenge geteilt, die Teile werden zuerst geordnet, die Trennmenge zuletzt; Stücke bis `leaf` Knoten
    nach Mindestgrad. Findet das Verfahren nichts, schneidet der geometrische Median (ersatzweise ein Knoten): `fallbacks` zählt das."""
    order: list[int] = []
    pieces: list[tuple[int, int, str]] = []
    fallbacks = 0

    def rec(nodes: set[int]) -> None:
        nonlocal fallbacks
        if len(nodes) <= leaf:
            order.extend(min_degree_order(adj, nodes))
            return
        comps = components(adj, nodes)
        if len(comps) > 1:
            for comp in comps:
                rec(comp)
            return
        sep = find_separator(method, adj, nodes, pos, adj_cycle)
        used = method
        if sep is None or not sep.vertices:
            fallbacks += 1
            sep = geometric_separator(adj, pos, nodes) or Separator((min(nodes),), "single")
            used = "Rückfall " + sep.method
        pieces.append((len(nodes), len(sep.vertices), used))
        for comp in components(adj, nodes - set(sep.vertices)):
            rec(comp)
        order.extend(sorted(sep.vertices))

    rec(set(range(len(adj))))
    return NDResult(order, pieces, fallbacks)
