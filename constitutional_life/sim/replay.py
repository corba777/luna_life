"""Causal-replay snapshots. Do not advance engine state.

A snapshot stores the already-delivered inbox (padded to 8). Permutation
replaces that vector from a paired seed; hash selection is not re-run.
Replay J is mean task_correct over the K draws, not the N_CELLS×T trajectory
denominator.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable

from constitutional_life.board.board import Substrate
from constitutional_life.cell.observation import (
    CellObservation,
    observation_from_dict,
    observation_to_dict,
)
from constitutional_life.cell.prompt import render_prompt
from constitutional_life.cell.schema import DecisionMode, parse_decision
from constitutional_life.cell.score import ExecutionLogV1a, log_from_parse, replay_j
from constitutional_life.task.catalog import CanonicalFunction, FunctionCatalog, build_catalog
from constitutional_life.v1a_constants import EPOCH_LENGTH, REPLAY_K, SCHEMA_VERSION

Completer = Callable[[CellObservation], str]


@dataclass(frozen=True, slots=True)
class ReplayCell:
    observation: CellObservation
    expected: str


@dataclass
class ReplaySnapshot:
    world_seed: int
    generation: int
    epoch: int
    substrate: Substrate
    channel: bool
    program_id: str
    p_e: str
    cells: list[ReplayCell]
    schema_version: int = SCHEMA_VERSION

    @property
    def mode(self) -> DecisionMode:
        return "channel" if self.channel else "no_channel"

    def prompt_for(self, cell_id: int) -> str:
        return render_prompt(self.cell(cell_id).observation, channel=self.channel)

    def cell(self, cell_id: int) -> ReplayCell:
        for row in self.cells:
            if row.observation.cell_id == cell_id:
                return row
        raise KeyError(cell_id)


def is_replay_point(completed_generation: int, epoch_length: int = EPOCH_LENGTH) -> bool:
    if completed_generation <= 0:
        return False
    phase = ((completed_generation - 1) % epoch_length) + 1
    return phase == epoch_length // 2 or phase == epoch_length


def make_replay_snapshot(
    *,
    world_seed: int,
    generation: int,
    epoch: int,
    substrate: Substrate,
    channel: bool,
    fn: CanonicalFunction,
    observations: Iterable[CellObservation],
    queries: dict[int, str],
) -> ReplaySnapshot:
    cells = [
        ReplayCell(observation=obs, expected=fn.apply(queries[obs.cell_id]))
        for obs in observations
    ]
    return ReplaySnapshot(
        world_seed=world_seed,
        generation=generation,
        epoch=epoch,
        substrate=substrate,
        channel=channel,
        program_id=fn.program_id,
        p_e=fn.description(),
        cells=cells,
    )


def apply_delivered_permutation(
    target: ReplaySnapshot,
    donor: ReplaySnapshot,
) -> ReplaySnapshot:
    """Give cell i in target the already-delivered 8 from cell i in donor."""
    if target.generation != donor.generation:
        raise ValueError("permutation requires the same generation")
    if target.substrate != donor.substrate:
        raise ValueError("permutation requires the same substrate")
    if target.channel != donor.channel:
        raise ValueError("permutation requires the same channel flag")
    if target.world_seed == donor.world_seed:
        raise ValueError("permutation is across seeds")
    donor_inbox = {row.observation.cell_id: row.observation.inbox for row in donor.cells}
    cells = []
    for row in target.cells:
        inbox = donor_inbox.get(row.observation.cell_id)
        if inbox is None:
            raise KeyError(row.observation.cell_id)
        obs = row.observation
        swapped = CellObservation(
            cell_id=obs.cell_id,
            generation=obs.generation,
            epoch=obs.epoch,
            epoch_generation=obs.epoch_generation,
            examples=obs.examples,
            query=obs.query,
            inbox=list(inbox),
            memory=obs.memory,
        )
        cells.append(ReplayCell(observation=swapped, expected=row.expected))
    return ReplaySnapshot(
        world_seed=target.world_seed,
        generation=target.generation,
        epoch=target.epoch,
        substrate=target.substrate,
        channel=target.channel,
        program_id=target.program_id,
        p_e=target.p_e,
        cells=cells,
        schema_version=target.schema_version,
    )


def replay_once(
    snapshot: ReplaySnapshot,
    completer: Completer,
    catalog: FunctionCatalog | None = None,
) -> list[ExecutionLogV1a]:
    """K=1 pass over all cells. Does not write the board or step the world."""
    catalog = catalog or build_catalog()
    fn = catalog.by_id(snapshot.program_id)
    logs = []
    for row in snapshot.cells:
        raw = completer(row.observation)
        parsed = parse_decision(raw, mode=snapshot.mode)
        logs.append(log_from_parse(parsed, row.expected, fn, catalog))
    return logs


def replay_k(
    snapshot: ReplaySnapshot,
    completer: Completer,
    k: int = REPLAY_K,
    catalog: FunctionCatalog | None = None,
) -> tuple[float, list[list[ExecutionLogV1a]]]:
    draws = [replay_once(snapshot, completer, catalog) for _ in range(k)]
    flat = [log for draw in draws for log in draw]
    return replay_j(flat), draws


def snapshot_to_json(snapshot: ReplaySnapshot) -> dict:
    return {
        "schema_version": snapshot.schema_version,
        "world_seed": snapshot.world_seed,
        "generation": snapshot.generation,
        "epoch": snapshot.epoch,
        "substrate": snapshot.substrate,
        "channel": snapshot.channel,
        "program_id": snapshot.program_id,
        "p_e": snapshot.p_e,
        "cells": [
            {
                "observation": observation_to_dict(row.observation),
                "expected": row.expected,
            }
            for row in snapshot.cells
        ],
    }


def snapshot_from_json(payload: dict) -> ReplaySnapshot:
    cells = [
        ReplayCell(
            observation=observation_from_dict(row["observation"]),
            expected=row["expected"],
        )
        for row in payload["cells"]
    ]
    return ReplaySnapshot(
        world_seed=payload["world_seed"],
        generation=payload["generation"],
        epoch=payload["epoch"],
        substrate=payload["substrate"],
        channel=payload["channel"],
        program_id=payload["program_id"],
        p_e=payload["p_e"],
        cells=cells,
        schema_version=payload.get("schema_version", SCHEMA_VERSION),
    )


def save_snapshot(snapshot: ReplaySnapshot, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(snapshot_to_json(snapshot), indent=2) + "\n")


def load_snapshot(path: Path) -> ReplaySnapshot:
    return snapshot_from_json(json.loads(path.read_text()))
