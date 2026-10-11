"""Per-cell inference seeds. Same temperature everywhere; the seed is the split.

Trajectory cell i at generation t in world_seed W uses one seed. A system-level
permutation keeps W and therefore the seed, and only replaces the delivered 8.
Replay draws use kind='replay' and draw=k so they are not the trajectory sample.

Option order is a separate axis under the same hash scheme (`kind='order'`). True
and permuted inboxes for the same (W, t, i) share that order seed, as do both
exact-replay calls on a snapshot cell.
"""

from __future__ import annotations

import hashlib

ORDER_KIND = "order"


def inference_seed(
    world_seed: int,
    generation: int,
    cell_id: int,
    *,
    kind: str,
    draw: int = 0,
) -> int:
    payload = f"{world_seed}|{generation}|{cell_id}|{kind}|{draw}".encode()
    return int.from_bytes(hashlib.sha256(payload).digest()[:4], "big")


def option_order_seed(
    world_seed: int,
    generation: int,
    cell_id: int,
    *,
    draw: int = 0,
) -> int:
    """Presentation order for choice criteria. Independent of inbox content."""
    return inference_seed(world_seed, generation, cell_id, kind=ORDER_KIND, draw=draw)
