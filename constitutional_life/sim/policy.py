"""Symbolic stand-in for the LLM cell. Not the registered policy.

A cell answers from H(E) if that set is a singleton. Otherwise it tries
to parse a visible `say` as a DSL program and apply that map. If it
solves, it publishes the canonical description — that is how a rule
crosses more than one hop.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from constitutional_life.board.board import Message
from constitutional_life.cell.score import ExecutionLogV1a
from constitutional_life.task.catalog import CanonicalFunction, FunctionCatalog
from constitutional_life.task.dsl import parse_program
from constitutional_life.task.identify import Example, hypothesis_set

Source = Literal["examples", "message", "unsolved"]


@dataclass(frozen=True, slots=True)
class OracleDecision:
    answer: str | None
    inferred_rule: str | None
    publish_say: str | None
    signal: int | None
    source: Source
    n_hypotheses: int


@dataclass(frozen=True, slots=True)
class StepDecision:
    answer: str | None
    inferred_rule: str | None
    publish_say: str | None
    signal: int | None
    source: str
    n_hypotheses: int
    parse_valid: bool = True
    parse_error: str | None = None


def step_from_oracle(decision: OracleDecision) -> StepDecision:
    return StepDecision(
        answer=decision.answer,
        inferred_rule=decision.inferred_rule,
        publish_say=decision.publish_say,
        signal=decision.signal,
        source=decision.source,
        n_hypotheses=decision.n_hypotheses,
    )


def step_from_log(log: ExecutionLogV1a, n_hypotheses: int) -> StepDecision:
    published = log.publication_committed
    return StepDecision(
        answer=log.task_answer,
        inferred_rule=log.inferred_rule,
        publish_say=log.say if published else None,
        signal=log.signal if published else None,
        source="model" if log.parse_valid else "parse_error",
        n_hypotheses=n_hypotheses,
        parse_valid=log.parse_valid,
        parse_error=log.parse_error,
    )


def _signal_for(description: str) -> int:
    return sum(description.encode()) % 8


def _function_from_say(
    say: str,
    catalog: FunctionCatalog,
) -> CanonicalFunction | None:
    try:
        program = parse_program(say)
    except ValueError:
        return None
    return catalog.canonicalize(program)


def decide(
    examples: list[Example],
    query: str,
    inbox: list[Message],
    catalog: FunctionCatalog,
) -> OracleDecision:
    hyps = hypothesis_set(examples, catalog)
    if len(hyps) == 1:
        fn = hyps[0]
        desc = fn.description()
        return OracleDecision(
            answer=fn.apply(query),
            inferred_rule=desc,
            publish_say=desc,
            signal=_signal_for(desc),
            source="examples",
            n_hypotheses=1,
        )

    for msg in inbox:
        fn = _function_from_say(msg.say, catalog)
        if fn is None:
            continue
        desc = fn.description()
        return OracleDecision(
            answer=fn.apply(query),
            inferred_rule=desc,
            publish_say=desc,
            signal=_signal_for(desc),
            source="message",
            n_hypotheses=len(hyps),
        )

    return OracleDecision(
        answer=None,
        inferred_rule=None,
        publish_say=None,
        signal=None,
        source="unsolved",
        n_hypotheses=len(hyps),
    )
