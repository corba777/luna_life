# Task — Luna with reasoning off as Life cells (effort=none)

**Status:** locked. Predictions locked with this file, before any run. API only (Luna), no GPU.
Follows `DESIGN_CHECKLIST.md`. Parents: `TASK_LIFE_REASONING_CELLS.md` (B, Ca, Da),
`TASK_LUNA_REASONING_MODES.md` (the single-agent control `none − Decisions` = +0.01 on two-op
pairs). Gate: `prompts/luna_none_gate_diffs.md` (PASS).

## Why

On single-agent tests, Luna with reasoning off (`effort=none`) behaves like the Decisions API:
two-op pairs 0.60 vs 0.59, Δ +0.01 [−0.055, +0.077]. In Life, `effort=none` cells were never run.
One-pass Life results so far come from Decisions (P=4 option orders, probabilities, argmax). Two
things differ between Decisions cells and reasoning cells: the absence of reasoning, and the
Decisions estimator. This task separates them and gives the reference point for our own one-pass
decision models (Unsloth V1).

## Arm

| arm | cells | channel | check | sources | parent for prompt | parent for outcome |
|---|---|---|---|---|---|---|
| **An** | Luna Responses, `effort=none` | on | none | 4 | **B** (identical prompt) | **Ca** |

- World seeds: the frozen schedule, 2-op seeds (primary) and 1-op seeds (descriptive), 10
  generations. Everything else as B: sparse, k=0, same constitution, same memory line
  (`published … say=…` / `silence.`, as in B; this is a channel-on arm).
- One request per cell-generation (as B); same output schema and parser as B; same retry and
  fallback rule (one retry, then `unsolved`).
- **References (not rerun):** B (medium), Ca (Decisions argmax, P=4), Cas, Da.

## Gate (before the first call)

1. **An vs B:** dry-render the g2 request for 3 cells (same seed, cell, history). The request
   text must be **byte-identical**; the only allowed difference is the API parameter
   `reasoning.effort` (`none` vs `medium`). Check on the request payload / request hash, not a
   logging reconstruction.
2. **An vs Ca (listed, not a failure):** state text identical; differences limited to the output
   instruction and option rendering of Responses vs Decisions. List them verbatim in
   `prompts/luna_none_gate_diffs.md`.
3. Startup asserts: channel on; 4 sources; `effort=none` on every request; no reasoning text
   requested or stored.

## Metrics

- J at g10 and mean J over 10 generations (96 non-source cells); locks; modal rule at g10.
- Validity: invalid / `unsolved` fallback rate per generation (reasoning-off output may break the
  schema more often; report it, do not drop seeds).
- Check behaviour (as traced for B and Ca): among switches to a neighbour's rule, the share of
  rules consistent vs inconsistent with the cell's own example; switches after `correct=false` vs
  `correct=true`.
- Self-revision hazard and retention (same definitions as `m1_retention_hazard.md`).
- Cost: API USD per seed, plus prefill and decode tokens per cell-generation (checklist item 7).

## Predictions (lock)

- **A1 (no reasoning ≈ Decisions in Life too):** |An − Ca| J@g10 < 0.10 (2-op, seed mean, 96
  cells; Ca reference 0.25).
- **A2 (reasoning matters in Life):** An J@g10 ≤ B J@g10 − 0.50 (2-op, seed mean; B 0.99).
- **A3 (descriptive):** An's share of adopted neighbour rules that contradict the cell's own
  example, against B (≈ 2%) and Ca (no filter).

## Readout

- **A1 PASS, A2 PASS:** in Life, what separates reasoning cells from one-pass cells is the
  reasoning, not the Decisions API; `effort=none` is a valid reference for one-pass decision
  models (Unsloth V1).
- **A1 FAIL:** the Decisions estimator matters in Life (P=4 averaging or probability argmax vs a
  generated key); calibrate V1 against both An and Ca.
- **A2 FAIL:** reasoning-off cells do well in Life despite failing two-op pairs alone; look at
  the check behaviour (A3) and at sources.

## Cost

Reasoning off: one request per cell-generation, no reasoning tokens. Expected well below B's
$0.44 per seed; 10 seeds ≈ $2–4. Alarm $5 (alarm, not a stop). Report the actual cost.

## Artifacts

- `prompts/luna_none_gate_diffs.md`
- `runs/life_luna_none/An/{2op,1op}/seed{n}/`
- `runs/life_luna_none/summary.json` (A1–A3 with B, Ca, Cas, Da alongside)
- `fig_luna_none.png`: J(g) for B, An, Ca, Cas (2-op)

## Constraints

Placement only: no training on outputs, no reasoning text requested or stored. Same prompt as B.
New runner script; do not edit running scripts in place. Commit this file before the gate.
Amendments before numbers. Queue: API, after Da0 closes, before `TASK_LIFE_DISTRIBUTED.md` Phase 1.