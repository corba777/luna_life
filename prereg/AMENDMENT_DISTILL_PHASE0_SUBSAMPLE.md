# Amendment — Distill check Phase 0: stratified eval subsample

**Status:** locked 2026-10-13 (commit before any further Phase 0 teacher call).
Parents: `TASK_LIFE_DISTILL_CHECK.md`, `AMENDMENT_DISTILL_CHECK_TEACHER.md`,
`AMENDMENT_DISTILL_CHECK_THINKING.md` (option i: prompted CoT on Qwen3-4B-Instruct-2507).

## Why

The Phase 0 pilot (first 50 teacher situations, draw window 32) projected about 24 h for the full
1,000-situation eval bank and triggered the registered abort (> 12 h): `phase0.aborted`. Phase 0
is a gate (D0: teacher stage1 ≥ 0.90) plus the S0 baseline. A smaller stratified eval set is
enough for that gate. The pilot's 50 teacher answers were not read for any stage1 or accuracy
number; only token counts and wall pace were used.

## Changes

1. **Eval subsample.** Phase 0 runs on 300 eval situations drawn from the existing 1,000-situation
   eval bank with `PHASE0_SUBSAMPLE_SEED = 20261013` (committed with this file):
   - all 53 anti-shortcut situations are included;
   - the remaining 247 are drawn stratified over the bank strata (feedback wrong/right ×
     P in inbox × number of inconsistent incoming rules × consistent competitor × 1-op/2-op P),
     proportional to their counts in the 1,000-situation bank.
   - The 50 pilot situations are kept if they fall into the draw and are not re-queried (cache).
   - Report the stratum counts of the subsample and the stage1 denominator (situations with ≥ 1
     inconsistent incoming rule).
2. **Unchanged:** teacher and student setup (option i), the cap (16384 + one retry), the draw
   window (32), the definitions of stage1 / stage2 / stubborn / validity, the D0 threshold
   (stage1 ≥ 0.90), and the pilot abort rule (> 12 h projected → abort), now applied to the
   300-situation projection.
3. **Precision note.** With a stage1 denominator of about 240, a 95% interval around 0.90 is
   about ±0.04. D0 is read as registered (point estimate ≥ 0.90); the interval is reported next to
   it.
4. **Scheduling.** Phase 0 runs after SPADE-4B cot (the GPU queue is otherwise unchanged).
   The rest of the distill task (train-bank labelling, SD/SO training, grid) is unchanged and
   still waits on D0.

## Artifacts

- `runs/life_distill/bank/eval_phase0_300.jsonl`, `phase0_subsample_strata.json`
- `runs/life_distill/phase0_gate.json` (on the 300-situation subsample)