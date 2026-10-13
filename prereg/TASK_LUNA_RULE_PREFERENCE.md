# Task — Do one-pass agents dislike some correct rules?

**Status:** locked. Predictions are locked with this file, before any run. API only (Luna
Decisions), single-agent probes, no grid. Follows `DESIGN_CHECKLIST.md`. Queue: after An closes,
gate diffs first (`prompts/rule_pref_gate_diffs.md` must PASS), then API, before Distributed
Phase 1.

## Why

In seed 2 (P_e = `rotate_left(1);swap(0,3)`), one-pass cells almost never adopt the true rule from a
neighbour: h(1) = 0.003 in Ca, vs 0.012–0.074 in the other seeds. They stay near zero in every
mixed arm, even with 50% reasoning neighbours (Ca 0.00, Mx10 0.00, Mx25 0.14, Mx50 0.33 at g10).
With engine checks the same seed reaches 0.90 (Da0). Two explanations:

1. **Prior aversion:** the model gives this rule little mass whatever the evidence.
2. **Evidence mismatch:** for this rule, the cells' examples make a competitor look as good or
   better in one pass.

This probe separates them on single agents, before any long grid runs.

## Probes (same model and estimator as Ca: Decisions, P=4 option orders, argmax and mean prob)

- **A. Prior, no evidence.** The cell prompt with the examples block replaced by "No examples
  are available." Full 101-rule catalog. Report the probability mass and rank of each seed's P_e,
  and of each seed's modal false rule in Ca at g10. One prompt per seed context, P=4.
- **B. Pair, own example.** For each 2-op seed, 100 cells sampled (seeded) from the world; each
  cell's own private example; two options: P_e vs the seed's modal false rule in Ca (g10). Report
  P(choose P_e), split by whether the false rule is consistent with that cell's example.
- **C. Adoption replay.** Re-ask, with the original prompt, every Ca cell-generation where k = 1
  (exactly one P_e message in the inbox) and the cell was told wrong. Report P(choose P_e) per seed.
  This is a determinism check against the logged h(1) and needs no new design.

## Gate

- A and B prompts: diff against the Ca g2 prompt for the same cell. Expected differences only:
  the examples block (A) or the option list (B). Listed verbatim in `prompts/rule_pref_gate_diffs.md`.
- C: request text byte-identical to the logged Ca request (request hash). Mismatches are reported,
  not dropped.

## Predictions (lock)

- **R1 (prior):** in A, seed 2's P_e has the lowest probability mass among the five seeds' P_e.
- **R2 (pair):** in B, P(choose P_e) for seed 2 is at least 0.15 below the mean of the other four
  seeds.
- **R3 (replay, descriptive):** C reproduces the logged per-seed h(1) within ±0.05.

## Readout

- **R1 PASS, R2 PASS:** the model has a prior against this rule that its single example does not
  overcome. One-pass populations without a check cannot adopt it whatever the neighbours say;
  checks override the prior. Long runs on seed 2 are expected to stay low without a check.
- **R1 FAIL, R2 PASS:** not a general prior but an evidence effect: this world's examples favour
  the competitor in one pass.
- **R2 FAIL:** the stall is a network effect, not an individual preference; look at local
  neighbourhood dynamics in seed 2.

## Cost

A: 5 × P=4 requests; B: 5 × 100 × P=4; C: ≈ 1,200 replayed decisions (P=4). Under $3 at observed
Decisions rates; alarm $5. Report API USD and prefill tokens.

## Artifacts

`prompts/rule_pref_gate_diffs.md`, `runs/luna_rule_pref/{A,B,C}.json`, `summary.json` (R1–R3).

## Constraints

Placement only; no reasoning text requested or stored. Same prompts as Ca except the listed
differences. Commit before the gate. Amendments before numbers.