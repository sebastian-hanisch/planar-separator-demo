"""Gemeinsame Fixtures: Mini-Graphen, an denen jede Einheit von Hand geprüft wird (DEMO-PLAYBOOK §1b)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import psp_algorithm as A  # noqa: E402


@pytest.fixture
def path7():
    """Pfad 0-1-2-3-4-5-6 (n = 7, Grenze 2n/3 = 4,67)."""
    return A.adjacency(7, [(i, i + 1) for i in range(6)])


@pytest.fixture
def star7():
    """Stern mit Mitte 0 und sechs Blättern."""
    return A.adjacency(7, [(0, k) for k in range(1, 7)])


@pytest.fixture
def grid3():
    """3 × 3 Gitter, Knoten zeilenweise 0 bis 8 (Grenze 2n/3 = 6)."""
    edges = [(r * 3 + c, r * 3 + c + 1) for r in range(3) for c in range(2)] + [(r * 3 + c, (r + 1) * 3 + c) for r in range(2) for c in range(3)]
    return A.adjacency(9, edges)


@pytest.fixture
def hexagon_chord():
    """Sechseck 0-1-2-3-4-5 mit der Sehne 0-3."""
    return A.adjacency(6, [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (0, 5), (0, 3)])
