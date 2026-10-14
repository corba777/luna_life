# Task — One agent with all the evidence, given time (DRo-iter)

**Status:** **locked** 2026-10-14. Predictions locked with this file, before any run. API only (Luna
Responses, `effort=medium`). Follows `DESIGN_CHECKLIST.md` and the standing rules in `PLAN_NEXT.md`.
Parent: `TASK_LIFE_DISTRIBUTED.md` (Phase 1). Runs after Phase 1 closes (A1).

## Why

In the distributed world no single cell's example identifies P_e (|S_c| ≥ 3), but the
intersection over each Moore neighbourhood does (world audit). Phase 1 results (2-op, J@g10, all
100 cells):

| arm | what it is | result |
|---|---|---|
| DRs | one example per cell, no channel | 0.15 (below chance 0.25) |
| DR | one example per cell, rules-only channel, 10 generations | 0.85 (0.71–1.00) |
| DRo | one call per neighbourhood with all nine examples | 0.56 |

D2 (DRo ≥ 0.80) failed as registered. DRo differs from DR in two ways at once: it pools the
evidence in one prompt, and it gets one call instead of ten generations. This task gives the
pooled-evidence agent the same ten generations and memory of its own rule. If it then matches DR,
the population's advantage was time; if not, distributed checking beats one agent holding all the
evidence.

## Arm

| arm | cells | evidence | generations | memory | feedback | channel |
|---|---|---|---|---|---|---|
| **DRo-iter** | one agent per DRo neighbourhood | the same nine example pairs as DRo | 10 | `rule='…' published=no` | none | none |

- Same neighbourhoods, same nine examples per neighbourhood, same constitution and prompt as DRo
  (seeds 1–5). The only differences from DRo: generation number, the query of that generation
  (drawn as in DR), and the memory line value from g2 on.
- g1 is a fresh DRo-style call (memory `Previous step: none.`).
- Same model, effort, schema, parser and refusal policy as DR/DRo.

## Gate

- g1 payload: byte-identical to the logged DRo request for the same neighbourhood except fields
  listed above; compared on the runner's request builder output (raw bytes).
- g2 dry render for 3 neighbourhoods: expected differences only in memory value, generation number
  and query. Runtime masked check at g2 of seed 1, before any g3 request.
- Fresh empty cache dir `cache_DRo_iter`; no DRo cache reuse (assert 0 hits from other dirs).

## Metrics

- Accuracy at g10 and mean over generations: share of neighbourhood agents holding P_e (seed means
  and per seed). Comparable to DR J@g10 (share of cells holding P_e).
- g1 accuracy (should reproduce DRo within sampling noise).
- Switch rate per generation, share of switches to/from P_e, stickiness P(keep | prev ≠ P_e).
- What the agent holds when wrong: a 1-op member of the pooled candidates, another rule
  consistent with some but not all nine examples, or inconsistent with any.
- Cost: USD, prefill/output tokens per call.

## Predictions (lock)

- **I0 (sanity):** g1 accuracy within ±0.10 of DRo (0.56), seed mean.
- **I1:** DRo-iter accuracy at g10 < 0.80 (without feedback, more time does not fix one-shot pooling).
- **I2 (primary):** DRo-iter accuracy at g10 ≤ DR J@g10 − 0.10 (DR 0.85), seed mean.
- **I3 (descriptive):** switch rate and stickiness by generation vs DR.

## Readout

- **I2 PASS:** with the same time and memory, one agent holding all nine examples stays below a
  population in which each member holds one example and passes rule names. The collective's
  advantage is not only time. Report D5 alongside (DR adopts received rules that fit its own
  example).
- **I2 FAIL:** the gap between DR and DRo was time; one agent with pooled evidence and ten tries does
  as well. The population then matches, but does not beat, a single well-informed agent.
- **I0 FAIL:** DRo-iter g1 does not reproduce DRo; stop and report before interpreting.

## Cost

About 20 neighbourhoods × 10 generations × 5 seeds ≈ 1,000 calls with nine examples each; estimate
~$5, alarm $10. Report the actual cost.

## Artifacts

`prompts/dro_iter_gate.md`, `runs/life_distributed/DRo_iter/seed{n}/`,
`runs/life_distributed/dro_iter_summary.json` (I0–I3 with DR, DRo, DRs alongside),
`fig_dro_iter.png` (accuracy by generation: DRo-iter per seed; DR J(g) and DRo as references).