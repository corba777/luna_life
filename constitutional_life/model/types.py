from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

from constitutional_life.cell.observation import CellObservation


class Completer(Protocol):
    """Returns one raw completion per observation. Never retries."""

    def complete_batch(
        self,
        observations: Sequence[CellObservation],
        *,
        channel: bool,
        seeds: Sequence[int],
    ) -> list[str]: ...
