# Task — Open reasoning cells in Life (SPADE-4B): does the collective effect survive an open 4B model?

**Status:** draft for lock. Predictions are locked with this file, before any run. Local GPU (SGLang),
after the Unsloth hybrid queue closes. Follows `DESIGN_CHECKLIST.md` and the standing rules in
`PLAN_NEXT.md` (B3). Parents: `TASK_LIFE_DISTRIBUTED.md` (DR, DRs on `gpt-6-luna`),
`runs/local_reasoning_probe/b1_readout.md` (sizing), `AMENDMENT_SPADE_GRID.md` (G2: SPADE-4B cot 0.94 on
two-step pairs).

## Why

On `gpt-6-luna`, reasoning cells that pass only rule names reach 0.85 in the distributed world, against
0.15 without the channel; they filter incoming rules against their own example (post-hoc: majority rule
adopted 64.5% when consistent, 1.8% when not). All of it is on a closed model. This task asks whether an
open 4B reasoning model reproduces the effect.

Sizing (B1, c=64): SPADE-4B ≈ 16 GPU-h per 5×10×96 arm, truncation 2–5%, invalid 2–3%.
Instruct-4B ≈ 58 GPU-h, truncation 15.6%; Qwen3.6-35B (vendor settings) ≈ 167 GPU-h. SPADE-4B is the
only cell that fits a full design; the others are not run here.

## Cells

`spade-rl/SPADE-Qwen3-4B-Games` (exact revision recorded), SGLang, BF16, sampling from the SPADE card
(temperature 0.7, top_p 0.8, top_k 20), per-request seed `hash(world, generation, cell, draw)`,
`max_tokens` 16,384, concurrency 64. Version and launch flags logged; the server stops when each step
ends.

## Prompt

The DR / DRs request built by the same distributed prompt builder (constitution, examples, memory line
`rule='…' published=…`, inbox, catalog in text, query). The only allowed difference from the Luna DR
request: the output-format tail. Luna's `Output a single JSON object and nothing else.` (schema passed as
an API parameter) is replaced by `Think step by step, then end with a single JSON object with the same
fields.` followed by the field list in text. Decoding is not constrained from the first token; the final
JSON object is parsed strictly; one re-sample on parse failure, then `unsolved`. Listed verbatim in the
gate file.

## Steps and arms

- **Step 0 (sanity, one world):** DR-S and DRs-S on world 1 only. Descriptive. Stop and report if the
  invalid + truncated share exceeds 10% or if any gate fails.
- **Step 1 (full):** DR-S and DRs-S on worlds 1–5, 10 generations, 100 cells (world 1 reused from
  Step 0 if no code or prompt change in between; otherwise rerun).

| arm | cells | channel | Luna reference |
|---|---|---|---|
| **DR-S** | SPADE-4B | rules only | DR (0.85) |
| **DRs-S** | SPADE-4B | none | DRs (0.15) |

## Gate

- Raw payload from the runner's request builder vs the Luna DR request for the same seed, cell, history:
  only the output-format tail differs (masked check on memory values, inbox contents, query, generation
  numbers; catalog as a multiset).
- Runtime masked check at g2 of world 1 before any g3 request; fresh empty per-arm caches; per-generation
  log of requests, truncations, invalid, fallbacks; fail if invalid + truncated > 10% in any generation.

## Metrics

J(g) and J@g10 (all 100 cells), per world and mean; uniform baseline per world (0.25 mean);
P(adopt | consistent) vs P(adopt | inconsistent) with the majority split (definitions of
`adopt_consistency.md`); invalid, truncation, tokens per decision, measured GPU-hours.

## Predictions (lock)

- **L1 (design validity on the open model):** DRs-S mean J@g10 ≤ 0.40.
- **L2 (main):** DR-S J@g10 ≥ DRs-S J@g10 + 0.30 in at least 3 of 5 worlds.
- **L3:** DR-S mean J@g10 < Luna DR mean J@g10 (0.85) — the open 4B model is weaker, not stronger.
- **L4 (mechanism):** for DR-S, P(adopt | majority ∧ inconsistent) ≤ 0.10 and
  P(adopt | majority ∧ consistent) − P(adopt | majority ∧ inconsistent) ≥ 0.30 (pooled).

## Readout

- **L1, L2, L4 PASS:** the collective effect and its filtering mechanism reproduce on an open 4B
  reasoning model.
- **L1 PASS, L2 FAIL:** the open model does not assemble the evidence through the channel; use L4 to say
  whether it fails to filter or fails to spread.
- **L1 FAIL:** the world is solvable alone for this model (or its baseline differs); record as a design
  failure for this model.

## Cost

Step 0 ≈ 2 × 3.3 GPU-h; Step 1 ≈ 2 × 16 GPU-h in total (world 1 reused). Report measured GPU-hours
per arm.

## Artifacts

`prompts/life_local_reasoning_gate.md`, `runs/life_local_reasoning/{DR_S,DRs_S}/seed{n}/`,
`runs/life_local_reasoning/summary.json` (L1–L4 with Luna DR/DRs alongside),
`fig_local_reasoning.png` (J(g): DR-S, DRs-S, Luna DR, Luna DRs).

## Constraints

Open model only; no closed-model output used anywhere in training (none here). Reasoning text from the
open model may be stored locally for truncation/loop diagnostics. New runner script; do not edit running
scripts; commit this file before the gate; amendments before numbers.