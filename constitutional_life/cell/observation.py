"""What a cell is allowed to see. Built by the engine, identical across policies."""

from __future__ import annotations

from dataclasses import dataclass

from constitutional_life.board.board import Message
from constitutional_life.board.geometry import coords
from constitutional_life.cell.memory import PrivateCellMemory, empty_memory
from constitutional_life.task.identify import Example
from constitutional_life.v1a_constants import READ_BUDGET


@dataclass(frozen=True, slots=True)
class CellObservation:
    cell_id: int
    generation: int
    epoch: int
    epoch_generation: int
    examples: list[Example]
    query: str
    inbox: list[Message | None]
    memory: PrivateCellMemory

    @property
    def row(self) -> int:
        return coords(self.cell_id)[0]

    @property
    def col(self) -> int:
        return coords(self.cell_id)[1]

    def delivered(self) -> list[Message]:
        return [msg for msg in self.inbox if msg is not None]


def pad_inbox(
    messages: list[Message],
    budget: int = READ_BUDGET,
) -> list[Message | None]:
    """Selection already applied. Pad with explicit nulls so every reader sees 8 slots."""
    if len(messages) > budget:
        raise ValueError(f"inbox length {len(messages)} exceeds read budget {budget}")
    padded: list[Message | None] = list(messages)
    padded.extend([None] * (budget - len(messages)))
    return padded


def message_to_dict(message: Message | None) -> dict | None:
    if message is None:
        return None
    return {
        "sender_id": message.sender_id,
        "generation": message.generation,
        "signal": message.signal,
        "say": message.say,
    }


def message_from_dict(payload: dict | None) -> Message | None:
    if payload is None:
        return None
    return Message(
        sender_id=payload["sender_id"],
        generation=payload["generation"],
        signal=payload["signal"],
        say=payload["say"],
    )


def observation_to_dict(obs: CellObservation) -> dict:
    return {
        "cell_id": obs.cell_id,
        "generation": obs.generation,
        "epoch": obs.epoch,
        "epoch_generation": obs.epoch_generation,
        "examples": [{"x": x, "y": y} for x, y in obs.examples],
        "query": obs.query,
        "inbox": [message_to_dict(msg) for msg in obs.inbox],
        "memory": obs.memory.to_dict(),
    }


def observation_from_dict(payload: dict) -> CellObservation:
    examples = [(row["x"], row["y"]) for row in payload["examples"]]
    inbox = [message_from_dict(row) for row in payload["inbox"]]
    return CellObservation(
        cell_id=payload["cell_id"],
        generation=payload["generation"],
        epoch=payload["epoch"],
        epoch_generation=payload["epoch_generation"],
        examples=examples,
        query=payload["query"],
        inbox=inbox,
        memory=PrivateCellMemory.from_dict(payload["memory"]),
    )


def make_observation(
    *,
    cell_id: int,
    generation: int,
    epoch: int,
    epoch_length: int,
    examples: list[Example],
    query: str,
    delivered: list[Message] | None = None,
    inbox: list[Message | None] | None = None,
    memory: PrivateCellMemory | None = None,
) -> CellObservation:
    if inbox is not None:
        if len(inbox) != READ_BUDGET:
            raise ValueError(f"inbox must have {READ_BUDGET} slots, got {len(inbox)}")
        slots = list(inbox)
    else:
        slots = pad_inbox(delivered or [])
    return CellObservation(
        cell_id=cell_id,
        generation=generation,
        epoch=epoch,
        epoch_generation=(generation % epoch_length) + 1,
        examples=examples,
        query=query,
        inbox=slots,
        memory=memory if memory is not None else empty_memory(),
    )


def inboxes_to_json(
    recorded: dict[int, dict[int, list[Message | None]]],
) -> dict:
    return {
        str(generation): {
            str(cell_id): [message_to_dict(slot) for slot in slots]
            for cell_id, slots in cells.items()
        }
        for generation, cells in recorded.items()
    }


def inboxes_from_json(payload: dict) -> dict[int, dict[int, list[Message | None]]]:
    return {
        int(generation): {
            int(cell_id): [message_from_dict(slot) for slot in slots]
            for cell_id, slots in cells.items()
        }
        for generation, cells in payload.items()
    }
