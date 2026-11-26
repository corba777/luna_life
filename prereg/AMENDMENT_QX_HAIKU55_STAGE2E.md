# Amendment — Claude Haiku 5.5, Stage 2E: δ 1/64, rule plus a chosen result, worlds 0–3

**Status:** draft v1 (2026-11-25), written by the reviewer for Artem. Artem, 2026-11-25 07:58: «По Haiku, из общих
экспериментов не хватает delta 1/64 R vs R+E + chosen result по мирам. Для Haiku, который опирается больше на
эксперимент, это важно». Money ceiling for Haiku: $72 in all (Artem, 2026-11-24). Locked after the agent's dry build and
the reviewer's review; no call before the lock and Artem's go, logged verbatim.

## Why

The Core experiments table has a row "δ 1/64 · B 1 · rule only vs + chosen result · worlds 0–3". Luna has both arms
(entry 8, test W-L held, p = 1/70). Claude Haiku 5.5 has only the rule-only arm (Stage 2B, entry 20: x̄ = 0 in all four
worlds). Haiku changes its rule almost only on a contradicting result (entries 16, 19–22), so the arm with shared results
is the one that can move it.

## Design (only the model changes; the rule-only arm is reused)

**Claude Haiku 5.5 · δ 1/64 · B 1 · rule plus a chosen result · 24 generations · worlds 0–3 · one run per world.**
4 runs, 9,600 calls. Engine, prompts, schemas and world files exactly as the Stage 2B rule-only runs
`qx3w_haiku55_d64_B1_R_w{0..3}` (the worlds engine of entries 8, 13, 19, 20) with the message switched to rule plus a
chosen result, as in Luna's entry 8 and Haiku's entry 19. Run names `qx3w_haiku55_d64_B1_RE_w{0..3}`. The rule-only arm is
those four Stage 2B runs, compared by file hash (sha256 of each trace listed in the dry build), not rerun. Decoding as in
Haiku Stage 0. No reasoning text stored.

## Measures and test

x̄ per run (share on H_T, generations 13–24) primary; x̄_nf, finders, rules held at 24 (H_T, the unconditional
substitution, H_F), messages with a counterexample, own or relayed, descriptive.

**Test W-LH:** x̄ with a chosen result above x̄ with rule only, four worlds against four, one-sided exact permutation,
70 splits, ties against rejection; holds at p ≤ 3/70.

## Prediction stated in advance, derived from measured data

The rule-only arm is fixed: x̄ = 0 in all four worlds. So W-LH holds exactly when every world's run with results has
x̄ > 0 (p = 1/70); one run at 0 gives p ≥ 5/70. Inputs, all measured on Haiku at δ 1/64, B 1: finders per run 15 in 16
runs (Stage 2B worlds 0–3: 1 in 4; Stage 2C world 0: 14 in 12) → Poisson(0.94), P(at least one finder) ≈ 0.61; a run with
results and a finder had x̄ > 0 in 3 of 3 (Stage 2C). Chance that all four worlds have x̄ > 0 ≈ 0.61⁴ ≈ 0.14.
**Prediction: does not hold** (derived chance 0.14). Stated risk: the finder rate in worlds 1–3 rests on 3 runs.

## Readings stated in advance

| pattern | reading |
|---|---|
| holds | In every world a finder appeared and shared results moved Haiku cells off H_F, against the prediction. |
| does not hold; a world with x̄ = 0 had no finder | With one test per cell the rare error is often not found; finding, not sharing, is the limit (as in entry 22). |
| does not hold; a world with a finder still has x̄ = 0 | A finder found the error but no cell reached H_T (e.g. all on the unconditional substitution). |

## Money

Projection: 9,600 × $0.000738 (mean cost per call of Haiku's δ 1/64 B 1 rule-plus-result runs in Stage 2C) ≈ **$7.08**;
**stop $10.62** (1.5 ×). Haiku spent before this stage: $14.19 + $18.90 (2B) + $6.26 (2D) + $20.58 (2C) = $59.93; left
$12.07; the stop fits. Start rule as before (spend so far + 1.5 × that run's projection ≤ stop). The page carries no
dollar figures.

## Gates, dry build, outputs

Format gate as in Stage 2B. Dry build (CPU): four run names and cache keys; generation-1 prompts byte-equal to Haiku's
entry-19 rule-plus-result prompts of the same world with δ 1/64 rendered as in the Stage 2B runs (mismatch counts); the
sha256 of the four reused rule-only traces; token counts and the start rule; the test code on constructed values
(all four > 0 → 1/70; one at 0 → 5/70). Outputs: calls (usage, no reasoning), traces, readout with W-LH, a package with
SHA256SUMS in the same message as the finish. Nothing enters the page before the reviewer's recheck; the page entry comes
with the four runs in the run viewer (Core experiments, δ 1/64 · R vs R+E, Claude Haiku 5.5).
