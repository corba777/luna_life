"""One board object. Substrate changes only the visibility mask and TTL."""

from __future__ import annotations

import hashlib
from collections import Counter
from dataclasses import dataclass
from typing import Literal

from constitutional_life.board.geometry import N_CELLS, chebyshev
from constitutional_life.v1a_constants import (
    MESSAGE_TTL_BY_SUBSTRATE,
    READ_BUDGET,
    REGION_RADIUS,
)

Substrate = Literal["none", "local", "regional", "global"]

RADIUS: dict[Substrate, int | None] = {
    "none": -1,
    "local": 1,
    "regional": REGION_RADIUS,
    "global": None,
}


@dataclass(frozen=True, slots=True)
class Message:
    sender_id: int
    generation: int
    signal: int
    say: str

    @property
    def message_id(self) -> str:
        return f"{self.sender_id}:{self.generation}"


def message_age(generation: int, message: Message) -> int:
    return generation - message.generation


def is_visible(
    reader_id: int,
    message: Message,
    generation: int,
    substrate: Substrate,
) -> bool:
    """Visibility after TTL. Readers never see their own writes (any substrate)."""
    if substrate == "none":
        return False
    age = message_age(generation, message)
    ttl = MESSAGE_TTL_BY_SUBSTRATE[substrate]
    if not 1 <= age <= ttl:
        return False
    dist = chebyshev(reader_id, message.sender_id)
    if dist == 0:
        return False
    radius = RADIUS[substrate]
    if radius is None:
        return True
    return dist <= radius


def selection_key(
    world_seed: int,
    generation: int,
    reader_id: int,
    message_id: str,
) -> str:
    payload = f"{world_seed}|{generation}|{reader_id}|{message_id}".encode()
    return hashlib.sha256(payload).hexdigest()


def select_messages(
    candidates: list[Message],
    reader_id: int,
    generation: int,
    world_seed: int,
    budget: int = READ_BUDGET,
) -> list[Message]:
    ranked = sorted(
        candidates,
        key=lambda msg: selection_key(world_seed, generation, reader_id, msg.message_id),
    )
    return ranked[:budget]


@dataclass
class Board:
    """Persistent message store. Writes at t become visible at t+1."""

    messages: list[Message]

    def __init__(self) -> None:
        self.messages = []

    def commit(self, writes: list[Message]) -> None:
        self.messages.extend(writes)

    def expire(self, generation: int, max_ttl: int = 3) -> None:
        self.messages = [
            msg for msg in self.messages if message_age(generation, msg) <= max_ttl
        ]

    def candidates(
        self,
        reader_id: int,
        generation: int,
        substrate: Substrate,
    ) -> list[Message]:
        return [
            msg
            for msg in self.messages
            if is_visible(reader_id, msg, generation, substrate)
        ]

    def deliver(
        self,
        reader_id: int,
        generation: int,
        substrate: Substrate,
        world_seed: int,
    ) -> list[Message]:
        return select_messages(
            self.candidates(reader_id, generation, substrate),
            reader_id,
            generation,
            world_seed,
        )


def all_cell_ids() -> list[int]:
    return list(range(N_CELLS))


def live_messages(
    board: Board,
    generation: int,
    substrate: Substrate,
) -> list[Message]:
    """Messages still inside the substrate TTL at `generation`."""
    if substrate == "none":
        return []
    ttl = MESSAGE_TTL_BY_SUBSTRATE[substrate]
    return [msg for msg in board.messages if 1 <= message_age(generation, msg) <= ttl]


def circulating_rules(
    board: Board,
    generation: int,
    substrate: Substrate,
    p_e: str,
) -> list[dict]:
    counts = Counter(msg.say for msg in live_messages(board, generation, substrate))
    return [
        {"say": say, "n": n, "correct": say == p_e}
        for say, n in counts.most_common()
    ]
