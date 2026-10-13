# Task — Life run of reasoning-off Luna at temperature 0 (An-T0 run): is An's mobility sampling noise?

**Status:** locked. Predictions are locked with this file, before any Life run. API only
(Luna Responses, `effort=none`), no GPU. Follows `DESIGN_CHECKLIST.md`. Parents:
`TASK_LIFE_LUNA_NONE.md` (An), `TASK_LIFE_AN_FILTER.md`, `TASK_LIFE_AN_NO_SOURCE.md` (Z1/Z2 PASS),
`TASK_LIFE_CA_SAMPLE.md` (S1 PASS, S2/S3 FAIL), `TASK_LIFE_AN_T0.md` (feasibility probe: T0 PASS,
T1 PASS; one Life-shaped prompt, omit n_unique = 2, temperature=0 n_unique = 1).

The predictions below (G1–G3) were drafted before the probe and are unchanged by it. They are named
G1–G3 to avoid a clash with T0–T2 of the probe task.

## Why

2-op, J@g10, 4 sources:

| arm | decision | r (keep P_e after correct=true) | J@g10 |
|---|---|---|---|
| Ca | Decisions, argmax of P=4 mean | 0.97 | 0.25 |
| An | Responses `effort=none`, no temperature sent | 0.71 | 0.47 |
| Ca-sample | Decisions, draw from P=4 mean | 0.09 | 0.01 |

An's advantage needs the sources (An0 0.01). An is more mobile than Ca. Two readings:

1. **Noise:** An's mobility is sampling noise of a non-greedy generation.
2. **Responsiveness:** An's choice actually depends on its input (inbox, memory) more than Ca's
   does; it would move even when greedy.

An-T0 removes sampling noise from An and changes nothing else. It also avoids comparing
temperatures across two APIs whose decision readouts are not comparable.

## Arm

| arm | cells | temperature | sources | channel | check | parent |
|---|---|---|---|---|---|---|
| **An-T0** | Luna Responses, `effort=none` | **0** | 4 | on | none | An |

2-op seeds 1–5, 10 generations. Everything else as An: prompt, schema, parser, memory line,
constitution, refusal policy.

## Gate (before the first run)

Feasibility, determinism and the API-reference facts are closed by `TASK_LIFE_AN_T0.md`.

1. **An-T0 vs An:** dry-render the g2 request for 3 cells with a forced identical history;
   payloads must be byte-identical except the added `temperature: 0`.
2. Startup asserts: 4 sources; `effort=none` and `temperature=0` on every request; no reasoning
   text requested or stored. Cache keys include the temperature; no reuse of An's cache (assert 0
   An-cache hits).
3. Commit `prompts/an_t0_run_gate.md` before the first call.

## Metrics

J@g10 and mean J (96 non-source cells), labelled; h(0), h(1), r, P(keep rule | prev ≠ P_e), same
definitions as `TASK_LIFE_AN_FILTER`; locks; modal rule at g10; refusals and invalid outputs; cost
(USD, prefill and output tokens per cell-generation).

## Predictions (lock)

- **G1 (greedy An is sticky):** An-T0 r ≥ 0.90.
- **G2 (and does no better than Ca):** An-T0 seed-mean J@g10 ≤ 0.35 (Ca 0.25, An 0.47).
- **G3 (descriptive):** P(keep rule | prev ≠ P_e) for An-T0 vs An (0.18) and Ca (0.67); h(0), h(1).

## Readout

- **G1 PASS, G2 PASS:** An's mobility is sampling noise; with permanent sources, a moderate amount
  of noise helps a population converge; reasoning off and Decisions differ in Life mainly by the
  readout.
- **G1 FAIL:** greedy An still changes its rule; its mobility is responsiveness to input, not
  noise. Compare h(1) by inbox stratum with Ca.
- **G1 PASS, G2 FAIL:** greedy An is sticky yet still beats Ca; the difference lies in what it
  chooses, not how often it changes.

## Cost

About $1.1 (An rates), alarm $3 (not a stop).

## Artifacts

`prompts/an_t0_run_gate.md`, `runs/life_an_t0_run/seed{n}/`, `runs/life_an_t0_run/summary.json`
(G1–G3 with An, An0, Ca, Ca-sample alongside), `fig_an_t0.png` (J(g) per seed: Ca, An, An-T0).

## Constraints

Placement only: no training on outputs; no reasoning text requested or stored. New runner script;
do not edit running scripts in place. Commit this file before the gate; amendments before numbers.

## Not in this task (candidate, unregistered)

Ca-temp: Decisions with sharpened sampling π̄^(1/τ), τ fitted offline on Ca caches so that r ≈ 0.71.
Decide after G1–G3.