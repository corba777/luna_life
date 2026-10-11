"""Task DSL: alphabet A..H, length 4, 1–2 op programs.

Canonical description is the shortest program denoting a function,
ties broken lexicographically on the description string. Composition
`op1;op2` means apply op1 first, then op2.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterator

ALPHABET = "ABCDEFGH"
ALPHABET_SET = frozenset(ALPHABET)
ALPHABET_INDEX = {ch: i for i, ch in enumerate(ALPHABET)}
L = 4
RADIX = len(ALPHABET)
N_INPUTS = RADIX**L  # 4096
SAY_BYTE_LIMIT = 96

_ROTATE_K = range(1, L)  # 1 .. L-1
_SHIFT_K = range(1, RADIX)  # 1 .. 7


class InvalidSequence(ValueError):
    """Sequence is not a legal task string (length or alphabet)."""


def is_valid_seq(seq: object) -> bool:
    return (
        isinstance(seq, str)
        and len(seq) == L
        and all(ch in ALPHABET_SET for ch in seq)
    )


def validate_seq(seq: object) -> str:
    if not isinstance(seq, str):
        raise InvalidSequence("sequence is missing or not a string")
    if len(seq) != L:
        raise InvalidSequence(f"sequence length {len(seq)} != {L}")
    if any(ch not in ALPHABET_SET for ch in seq):
        raise InvalidSequence(f"sequence {seq!r} has symbols outside {ALPHABET}")
    return seq


def is_valid_task_answer(answer: object) -> bool:
    """Invalid answers are scored incorrect under the fixed denominator."""
    return is_valid_seq(answer)


def encode_seq(seq: str) -> int:
    n = 0
    for ch in seq:
        n = n * RADIX + ALPHABET_INDEX[ch]
    return n


def decode_seq(idx: int) -> str:
    if not 0 <= idx < N_INPUTS:
        raise ValueError(f"input index {idx} out of range")
    chars = ["A"] * L
    for pos in range(L - 1, -1, -1):
        chars[pos] = ALPHABET[idx % RADIX]
        idx //= RADIX
    return "".join(chars)


def all_inputs() -> list[str]:
    return [decode_seq(i) for i in range(N_INPUTS)]


@dataclass(frozen=True, slots=True)
class Reverse:
    def description(self) -> str:
        return "reverse"

    def apply(self, seq: str) -> str:
        return seq[::-1]


@dataclass(frozen=True, slots=True)
class RotateLeft:
    k: int

    def description(self) -> str:
        return f"rotate_left({self.k})"

    def apply(self, seq: str) -> str:
        k = self.k % L
        return seq[k:] + seq[:k]


@dataclass(frozen=True, slots=True)
class RotateRight:
    k: int

    def description(self) -> str:
        return f"rotate_right({self.k})"

    def apply(self, seq: str) -> str:
        k = self.k % L
        return seq[-k:] + seq[:-k] if k else seq


@dataclass(frozen=True, slots=True)
class ShiftSymbols:
    k: int

    def description(self) -> str:
        return f"shift_symbols({self.k})"

    def apply(self, seq: str) -> str:
        return "".join(
            ALPHABET[(ALPHABET_INDEX[ch] + self.k) % RADIX] for ch in seq
        )


@dataclass(frozen=True, slots=True)
class Swap:
    i: int
    j: int

    def __post_init__(self) -> None:
        if not (0 <= self.i < self.j < L):
            raise ValueError(f"swap indices must satisfy 0 <= i < j < {L}")

    def description(self) -> str:
        return f"swap({self.i},{self.j})"

    def apply(self, seq: str) -> str:
        xs = list(seq)
        xs[self.i], xs[self.j] = xs[self.j], xs[self.i]
        return "".join(xs)


Op = Reverse | RotateLeft | RotateRight | ShiftSymbols | Swap


def atomic_ops() -> tuple[Op, ...]:
    ops: list[Op] = [Reverse()]
    for k in _ROTATE_K:
        ops.append(RotateLeft(k))
        ops.append(RotateRight(k))
    for k in _SHIFT_K:
        ops.append(ShiftSymbols(k))
    for i in range(L):
        for j in range(i + 1, L):
            ops.append(Swap(i, j))
    return tuple(ops)


@dataclass(frozen=True, slots=True)
class Program:
    ops: tuple[Op, ...]

    def __post_init__(self) -> None:
        if not 1 <= len(self.ops) <= 2:
            raise ValueError("v1 programs are compositions of 1–2 ops")

    def description(self) -> str:
        return ";".join(op.description() for op in self.ops)

    def apply(self, seq: str) -> str:
        out = validate_seq(seq)
        for op in self.ops:
            out = op.apply(out)
        return out

    def output_table(self) -> tuple[int, ...]:
        """Outputs over all inputs, encoded as base-8 integers."""
        return tuple(encode_seq(self.apply(decode_seq(i))) for i in range(N_INPUTS))


def all_syntactic_programs() -> Iterator[Program]:
    atoms = atomic_ops()
    for op in atoms:
        yield Program((op,))
    for first in atoms:
        for second in atoms:
            yield Program((first, second))


_OP_PATTERNS = (
    (re.compile(r"^reverse$"), lambda _m: Reverse()),
    (re.compile(r"^rotate_left\((\d+)\)$"), lambda m: RotateLeft(int(m.group(1)))),
    (re.compile(r"^rotate_right\((\d+)\)$"), lambda m: RotateRight(int(m.group(1)))),
    (re.compile(r"^shift_symbols\((\d+)\)$"), lambda m: ShiftSymbols(int(m.group(1)))),
    (re.compile(r"^swap\((\d+),(\d+)\)$"), lambda m: Swap(int(m.group(1)), int(m.group(2)))),
)


def parse_op(text: str) -> Op:
    for pattern, factory in _OP_PATTERNS:
        match = pattern.fullmatch(text)
        if match is None:
            continue
        op = factory(match)
        _validate_parsed_op(op)
        return op
    raise ValueError(f"unrecognized op: {text!r}")


def _validate_parsed_op(op: Op) -> None:
    if isinstance(op, (RotateLeft, RotateRight)) and op.k not in _ROTATE_K:
        raise ValueError(f"rotate k={op.k} not in 1..{L - 1}")
    if isinstance(op, ShiftSymbols) and op.k not in _SHIFT_K:
        raise ValueError(f"shift k={op.k} not in 1..{RADIX - 1}")
    if isinstance(op, Swap) and not (0 <= op.i < op.j < L):
        raise ValueError(f"swap({op.i},{op.j}) is not a v1 swap")


def parse_program(text: str) -> Program:
    parts = text.split(";")
    if not 1 <= len(parts) <= 2:
        raise ValueError(f"expected 1–2 ops, got {len(parts)} in {text!r}")
    return Program(tuple(parse_op(part) for part in parts))
