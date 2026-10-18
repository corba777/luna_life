# Amendment — TASK_LIFE_DR_TOPOLOGY: T1 world list

**Status:** written after Part A and before any API call. Parents:
`TASK_LIFE_DR_TOPOLOGY.md`, `AMENDMENT_DR_TOPOLOGY_CHANNEL.md`,
`AMENDMENT_DR_TOPOLOGY_R8_DRAW.md`. Counts:
`runs/life_dr_topology/partA_predictions.json` (1000 runs, seed 20261018).

## In-sample gate

The real x falls inside the simulated central 90% interval in 7 of 10 runs at round 10
and in 8 of 10 runs at round 20. The rule is at least 8 of 10 at each round. The gate
fails. The automaton gives no prediction. The r8 and all arms are descriptive only.
T1, T2 and T3 are not tests.

Outside the interval: world 2 replicate 1 at rounds 10 and 20 (real 0.23 and 0.53),
world 3 replicate 1 at round 10 (real 0.39), world 4 replicate 1 at rounds 10 and 20
(real 0.26 and 0.40).

## List from the P > 0.5 rule

The rule keeps a world when the simulated r8 replicate mean lies on the stated side of
the moore replicate mean with P > 0.5. All five worlds meet it. Because the gate failed,
this list is not locked as a test.

| world | round | direction | P(direction) |
|---:|---:|---|---:|
| 1 | 10 | r8 above moore | 1.000 |
| 2 | 20 | r8 below moore | 0.992 |
| 3 | 10 | r8 above moore | 0.997 |
| 4 | 20 | r8 below moore | 1.000 |
| 5 | 10 | r8 above moore | 0.983 |
