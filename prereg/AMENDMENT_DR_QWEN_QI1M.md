# Amendment — Qwen QI-1m on the Part 0b redo prompts

**Status:** locked before any QI-1m call. Parents: `TASK_LIFE_DR_QWEN_INTERVENTIONS.md` and
`AMENDMENT_DR_TIPPING_REDO.md`. Local model, no API cost. Not launched with this lock.

## What is added

QI-1 stays the original 880 Part 0b prompts. That comparison is on identical inputs.

QI-1m uses the 880 Part 0b prompts from the intervention redo: the same cells, conditions and draws,
with which senders carry P_e reassigned by the redo's fixed hash. Own cache. A read of the QI-1 cache,
of a Stage 0 or Stage 1 cache, or of any Luna cache aborts.

## Predictions

I1q, I2q and I3q are re-locked on the QI-1m prompts. The tests, the bound and α = 0.05 are the ones in
the task. The descriptive curve is reported next to QI-1 and next to the Luna redo on the same prompts.

## Schedule

After Qwen Stage 1 `all` finishes, after QI-1, and before any moore run. It waits until the redo
prompts exist. The Stage 1 runner is not edited, and a running Stage 1 process is not touched.
