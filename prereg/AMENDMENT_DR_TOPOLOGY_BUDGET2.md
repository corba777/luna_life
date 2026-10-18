# Amendment — TASK_LIFE_DR_TOPOLOGY: budget, second

**Status:** written while the launch is running, before the cumulative cost reaches $35.
Parents: `TASK_LIFE_DR_TOPOLOGY.md`, `AMENDMENT_DR_TOPOLOGY_BUDGET.md`.

## Cap

Artem raises the hard stop for this task from $35 to **$40**. The alarm stays at **$28**.

The launch already running took its stop from a constant in the runner that was
committed before that launch. That constant is not re-read from a file or from
the environment. That process still stops at $35, before the next round.

A resume runner, committed before it is used, continues after that stop. Its
hard stop is $40. The alarm stays $28. Completed series are skipped. The
interrupted series replays from its own cache through the last completed round:
no live request, and any cache miss aborts. The rules of all 100 cells at that
round must match the saved history. Later rounds are live. The cumulative cost
includes everything already spent. The other gates are unchanged: epoch length
21, the true rule and the example hash checked every round, and a separate
cache for each replicate.
