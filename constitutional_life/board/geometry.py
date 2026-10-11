"""GRID×GRID torus geometry. Visibility is Chebyshev distance (Moore)."""

from __future__ import annotations

from constitutional_life.v1a_constants import GRID

N_CELLS = GRID * GRID


def cell_id(row: int, col: int) -> int:
    return row * GRID + col


def coords(cid: int) -> tuple[int, int]:
    return divmod(cid, GRID)


def torus_delta(a: int, b: int, n: int = GRID) -> int:
    d = abs(a - b)
    return min(d, n - d)


def chebyshev(a: int, b: int) -> int:
    ra, ca = coords(a)
    rb, cb = coords(b)
    return max(torus_delta(ra, rb), torus_delta(ca, cb))


def neighbours(cid: int, radius: int) -> list[int]:
    """Cells at Chebyshev distance 1..radius, wrapping. Excludes self."""
    return [other for other in range(N_CELLS) if 1 <= chebyshev(cid, other) <= radius]
