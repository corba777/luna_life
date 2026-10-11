"""Mechanical scoring of a parsed decision. Engine-side, not shown to the cell."""

from __future__ import annotations

from dataclasses import dataclass

from constitutional_life.cell.schema import ParseResult, publication_of
from constitutional_life.task.catalog import CanonicalFunction, FunctionCatalog
from constitutional_life.task.dsl import parse_program
from constitutional_life.task.identify import score_answer


@dataclass(frozen=True, slots=True)
class ExecutionLogV1a:
    parse_valid: bool
    parse_error: str | None
    task_answer: str | None
    task_correct: bool
    inferred_rule: str | None
    rule_correct: bool | None
    publication_committed: bool
    signal: int | None
    say: str | None


def score_inferred_rule(
    text: str,
    fn: CanonicalFunction,
    catalog: FunctionCatalog,
) -> bool:
    if text == fn.description():
        return True
    try:
        program = parse_program(text.strip())
    except ValueError:
        return False
    canonical = catalog.canonicalize(program)
    return canonical is not None and canonical.program_id == fn.program_id


def log_from_parse(
    result: ParseResult,
    expected: str,
    fn: CanonicalFunction,
    catalog: FunctionCatalog,
) -> ExecutionLogV1a:
    if not result.ok or result.decision is None:
        return ExecutionLogV1a(
            parse_valid=False,
            parse_error=result.error,
            task_answer=None,
            task_correct=False,
            inferred_rule=None,
            rule_correct=None,
            publication_committed=False,
            signal=None,
            say=None,
        )
    decision = result.decision
    pub = publication_of(decision)
    return ExecutionLogV1a(
        parse_valid=True,
        parse_error=None,
        task_answer=decision.task_answer,
        task_correct=score_answer(decision.task_answer, expected),
        inferred_rule=decision.inferred_rule,
        rule_correct=score_inferred_rule(decision.inferred_rule, fn, catalog),
        publication_committed=pub is not None,
        signal=None if pub is None else pub.signal,
        say=None if pub is None else pub.say,
    )


def replay_j(logs: list[ExecutionLogV1a]) -> float:
    """Mean task_correct over the replay sample. Not the N_CELLS×T denominator."""
    if not logs:
        return 0.0
    return sum(1.0 for log in logs if log.task_correct) / len(logs)
