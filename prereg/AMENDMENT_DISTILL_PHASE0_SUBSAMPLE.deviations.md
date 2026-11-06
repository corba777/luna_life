Written in the working copy of `AMENDMENT_DISTILL_PHASE0_SUBSAMPLE.md` (mtime 2026-10-19), committed 2026-11-06; the locked amendment is unchanged.

## Schedule deviation log (2026-10-13)

**Recorded deviation from §4 / commit `424afab`:** Phase 0 (300-subsample) runs after
`runs/spade_grid/gpu_chain.ok`, **not** right after SPADE-4B cot as `424afab` states.

**Reason:** the subsample step was never added to the live chain (`resume_chain_after_cot.sh`),
and the chain had already moved past cot (cells / Part B / 30B in flight). Waiting until
`gpu_chain.ok` is the hygiene-safe slot (no in-place edit of the running chain). Watcher:
`runs/spade_grid/watch_phase0_subsample_after_gpu_chain.sh` →
`runs/life_distill/queue_phase0_subsample_300.sh`.

**No other change to Phase 0** — eval size, strata, teacher/student, D0 threshold, abort rule,
and artifacts below are unchanged. Ideal “after cot / before cells” remains the locked design;
this entry only documents the live-run slip.
