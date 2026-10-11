"""Identifiability, example sampling, and the two symbolic oracles."""

from __future__ import annotations

import random
from dataclasses import dataclass

from constitutional_life.task.catalog import CanonicalFunction, FunctionCatalog
from constitutional_life.task.dsl import (
    N_INPUTS,
    decode_seq,
    encode_seq,
    is_valid_task_answer,
    validate_seq,
)

MAX_EXAMPLE_RESAMPLES = 100
IDENTIFIABILITY_TARGET = 0.95
Example = tuple[str, str]


def score_answer(answer: object, expected: str) -> bool:
    """Invalid or missing answers count as incorrect."""
    return is_valid_task_answer(answer) and answer == expected


def privileged_oracle(fn: CanonicalFunction, query: str) -> str:
    """Sees P_e. Must score 100% if the scorer and tables agree."""
    return fn.apply(validate_seq(query))


def hypothesis_set(
    examples: list[Example],
    catalog: FunctionCatalog,
) -> list[CanonicalFunction]:
    encoded = _encode_examples(examples)
    return [fn for fn in catalog.functions if _table_agrees(fn.output_table, encoded)]


def observational_enumerator(
    examples: list[Example],
    query: str,
    catalog: FunctionCatalog,
) -> str | None:
    """Sees exactly the cell observation. Resolves iff |H(E)| = 1."""
    hyps = hypothesis_set(examples, catalog)
    if len(hyps) != 1:
        return None
    return hyps[0].apply(validate_seq(query))


def sample_example_set(
    fn: CanonicalFunction,
    n_examples: int,
    rng: random.Random,
) -> list[Example]:
    if not 1 <= n_examples <= N_INPUTS:
        raise ValueError(f"n_examples={n_examples} out of range")
    indices = rng.sample(range(N_INPUTS), n_examples)
    return [(decode_seq(i), decode_seq(fn.output_table[i])) for i in indices]


def sample_identifying_examples(
    fn: CanonicalFunction,
    n_examples: int,
    catalog: FunctionCatalog,
    rng: random.Random,
    max_attempts: int = MAX_EXAMPLE_RESAMPLES,
) -> tuple[list[Example] | None, int]:
    """Resample E until |H(E)| = 1, or give up after max_attempts.

    Returns (examples_or_none, attempts_used).
    """
    for attempt in range(1, max_attempts + 1):
        examples = sample_example_set(fn, n_examples, rng)
        if len(hypothesis_set(examples, catalog)) == 1:
            return examples, attempt
    return None, max_attempts


@dataclass(frozen=True, slots=True)
class IdentifiabilityPoint:
    n_examples: int
    n_trials_per_function: int
    identified_rate: float
    functions_usually_identified: float
    reject_rate_at_cap: float


def identifiability_curve(
    catalog: FunctionCatalog,
    n_values: range | list[int],
    rng: random.Random,
    trials_per_function: int = 100,
    usual_threshold: float = IDENTIFIABILITY_TARGET,
) -> list[IdentifiabilityPoint]:
    tables = [fn.output_table for fn in catalog.functions]
    points: list[IdentifiabilityPoint] = []
    for n in n_values:
        identified = 0
        total = 0
        usual = 0
        rejects = 0
        for table in tables:
            hits = 0
            for _ in range(trials_per_function):
                examples = _random_encoded_examples(table, n, rng)
                if _unique_hypothesis(tables, examples):
                    identified += 1
                    hits += 1
                total += 1
            if hits / trials_per_function >= usual_threshold:
                usual += 1
            # Approximate engine reject: 100 independent draws all fail.
            # Use the empirical per-draw miss rate rather than 100 extra draws.
            miss = 1.0 - (hits / trials_per_function)
            rejects += miss**MAX_EXAMPLE_RESAMPLES
        n_fn = len(tables)
        points.append(
            IdentifiabilityPoint(
                n_examples=n,
                n_trials_per_function=trials_per_function,
                identified_rate=identified / total,
                functions_usually_identified=usual / n_fn,
                reject_rate_at_cap=rejects / n_fn,
            )
        )
    return points


def recommend_n_examples(
    points: list[IdentifiabilityPoint],
    target: float = IDENTIFIABILITY_TARGET,
) -> int | None:
    for point in points:
        if point.identified_rate >= target:
            return point.n_examples
    return None


def _encode_examples(examples: list[Example]) -> list[tuple[int, int]]:
    encoded: list[tuple[int, int]] = []
    seen: set[int] = set()
    for inp, out in examples:
        i = encode_seq(validate_seq(inp))
        o = encode_seq(validate_seq(out))
        if i in seen:
            raise ValueError(f"duplicate example input {inp!r}")
        seen.add(i)
        encoded.append((i, o))
    return encoded


def _table_agrees(table: tuple[int, ...], examples: list[tuple[int, int]]) -> bool:
    return all(table[i] == o for i, o in examples)


def _random_encoded_examples(
    table: tuple[int, ...],
    n: int,
    rng: random.Random,
) -> list[tuple[int, int]]:
    indices = rng.sample(range(N_INPUTS), n)
    return [(i, table[i]) for i in indices]


def _unique_hypothesis(
    tables: list[tuple[int, ...]],
    examples: list[tuple[int, int]],
) -> bool:
    found = 0
    for table in tables:
        if _table_agrees(table, examples):
            found += 1
            if found > 1:
                return False
    return found == 1
