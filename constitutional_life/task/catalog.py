"""Enumerate distinct maps and pick a canonical representative each."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from functools import lru_cache

from constitutional_life.task.dsl import (
    N_INPUTS,
    SAY_BYTE_LIMIT,
    Program,
    all_syntactic_programs,
    decode_seq,
    encode_seq,
    validate_seq,
)


def function_id(output_table: tuple[int, ...]) -> str:
    payload = b"".join(value.to_bytes(2, "little") for value in output_table)
    return hashlib.sha256(payload).hexdigest()[:16]


def _canonical_key(program: Program) -> tuple[int, str]:
    return (len(program.ops), program.description())


@dataclass(frozen=True, slots=True)
class CanonicalFunction:
    program_id: str
    canonical: Program
    output_table: tuple[int, ...]
    n_spellings: int

    def apply(self, seq: str) -> str:
        return decode_seq(self.output_table[encode_seq(validate_seq(seq))])

    def description(self) -> str:
        return self.canonical.description()

    def description_bytes(self) -> int:
        return len(self.description().encode("utf-8"))

    @property
    def transmissible(self) -> bool:
        return self.description_bytes() <= SAY_BYTE_LIMIT

    @property
    def n_ops(self) -> int:
        return len(self.canonical.ops)

    @property
    def is_identity(self) -> bool:
        return all(self.output_table[i] == i for i in range(N_INPUTS))


@dataclass(frozen=True, slots=True)
class FunctionCatalog:
    functions: tuple[CanonicalFunction, ...]
    n_syntactic_programs: int

    def __iter__(self):
        return iter(self.functions)

    def __len__(self) -> int:
        return len(self.functions)

    def by_id(self, program_id: str) -> CanonicalFunction:
        for fn in self.functions:
            if fn.program_id == program_id:
                return fn
        raise KeyError(program_id)

    def by_table(self, output_table: tuple[int, ...]) -> CanonicalFunction | None:
        pid = function_id(output_table)
        try:
            return self.by_id(pid)
        except KeyError:
            return None

    def canonicalize(self, program: Program) -> CanonicalFunction | None:
        return self.by_table(program.output_table())


@lru_cache(maxsize=1)
def build_catalog() -> FunctionCatalog:
    best: dict[str, tuple[tuple[int, str], Program, tuple[int, ...], int]] = {}
    n_programs = 0
    for program in all_syntactic_programs():
        n_programs += 1
        table = program.output_table()
        pid = function_id(table)
        key = _canonical_key(program)
        current = best.get(pid)
        if current is None:
            best[pid] = (key, program, table, 1)
        else:
            old_key, old_program, old_table, count = current
            winner = program if key < old_key else old_program
            winner_key = key if key < old_key else old_key
            best[pid] = (winner_key, winner, old_table, count + 1)

    functions = tuple(
        sorted(
            (
                CanonicalFunction(
                    program_id=pid,
                    canonical=program,
                    output_table=table,
                    n_spellings=count,
                )
                for pid, (_key, program, table, count) in best.items()
            ),
            key=lambda fn: (fn.n_ops, fn.description()),
        )
    )
    return FunctionCatalog(functions=functions, n_syntactic_programs=n_programs)
