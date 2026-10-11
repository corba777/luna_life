"""Constitutional Life — v1a task layer (enumerator + oracles)."""

from constitutional_life.task.catalog import CanonicalFunction, FunctionCatalog
from constitutional_life.task.dsl import ALPHABET, L, SAY_BYTE_LIMIT, Program
from constitutional_life.task.identify import (
    MAX_EXAMPLE_RESAMPLES,
    hypothesis_set,
    observational_enumerator,
    privileged_oracle,
    sample_identifying_examples,
)

__all__ = [
    "ALPHABET",
    "L",
    "SAY_BYTE_LIMIT",
    "MAX_EXAMPLE_RESAMPLES",
    "CanonicalFunction",
    "FunctionCatalog",
    "Program",
    "hypothesis_set",
    "observational_enumerator",
    "privileged_oracle",
    "sample_identifying_examples",
]
