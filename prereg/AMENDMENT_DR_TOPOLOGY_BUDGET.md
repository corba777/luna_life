# Amendment — TASK_LIFE_DR_TOPOLOGY: budget

**Status:** written after the cost projection and before the full launch. Parent:
`TASK_LIFE_DR_TOPOLOGY.md`. This supersedes the alarm at $15 and the stop at $20
in that task.

## Cap

Artem raises the cap for this task. Alarm at **$28**. Hard stop at **$35**.

The runner checks the cumulative list-rate cost after every round. The total
includes the world-1 round-1 `all` probe. Crossing $28 is logged and the run
continues. Crossing $35 stops before the next round.

## Projection recorded before launch

The projection for both arms, 2 replicates × 5 worlds × 20 rounds, is **$24.01**
(`r8` $9.09, `all` $14.92). Output tokens are the pinned DRc tokens for the same
world, replicate, and round. Input tokens start from the measured round-1 cost
and grow with inbox length.

Measured round 1, world 1, per call:

| | input | output | reasoning | $ / call |
|---|---:|---:|---:|---:|
| `all` probe, replicate 1 | 2048.68 | 431.13 | 402.10 | 0.000676 |
| DRc, replicate 1 | 2095.68 | 432.64 | 403.49 | 0.000687 |
| DRc, replicate 2 | 2095.68 | 422.46 | 393.31 | 0.000682 |

Cached input was 0 on these calls. Nearly all input tokens were a cache write.

## Order

For each replicate, for each world, `r8` then `all`. An early stop then leaves
the same completed worlds on both arms.
