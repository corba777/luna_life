# Amendment — Ca-sample fresh cache (INVALID first run)

**Status:** locked after cache audit (`runs/life_ca_sample/cache_audit.md`).
Amends `TASK_LIFE_CA_SAMPLE.md` / runner / gate. Predictions S1–S3 unchanged.

## Verdict on first run

**INVALID as a Ca-sample experiment** (wrong label / claim). Do not use the prior
readout for S1–S3. See also `runs/ARM_REGISTRY.md`.

### Evidence

- Trajectory is **bit-identical to arm C** every generation (100/100 cells), and
  diverges from Ca (~5–13/100). J@g10 seed-mean **0.008** = C, not Ca (0.254).
- Every Decisions `choose` was a **cache hit** on `runs/life_reasoning_cells/cache_C`
  (11520/11520 per seed); **0 live requests** at every generation including g≥2.
- Cache keys **do** hash the full request `input` (state). Hits are real content
  matches to arm C’s pre-filled entries — not a key-without-state bug.
- Cached outcomes include first / forced / uniform (uniform is C’s refusal path
  served from disk, not a live miss→uniform in this run).

### Wrong label, not wrong data

Arm **C** is already Decisions / P=4 / **`decode=sample`** / channel on / k=0 / 4
sources / `cache_C` / same `inference_seed` schedule
(`runs/run_life_reasoning_cells.py` `ARM_SPEC["C"]`). The first Ca-sample run is a
**valid replay of C**. It is invalid only as the registered task “Ca (argmax) with
sample readout”: that experiment must start from Ca’s π̄ at g1 and diverge, with
live g≥2 requests on a fresh cache.

### Bug (relative to the task claim)

Runner shared `cache_C` and used `decode=sample` + C’s seeds → free C replay /
$0 live, while the task text said parent **Ca**. Gate allows **g1** hits vs Ca;
**g≥2 must be live** when state diverges from Ca.

## Fix (rerun)

1. **Fresh cache dir only:** `runs/life_ca_sample/cache_Ca_sample` (never read
   `cache_C` / arm C).
2. g1 may still be cold (pay full) — do **not** warm from C. Optional later: warm
   **only** from Ca’s g1 keys if a separate copy tool is written; not required.
3. **Startup asserts (runner):**
   - cache path is `cache_Ca_sample` under this task’s out dir;
   - after each generation: log `live_requests`, `cache_hits`, `outcomes_*`;
   - **fail** if at any `g≥2`: `live_requests == 0` OR
     `outcomes_uniform / n_choose > 0.02`.
4. Quarantine: `runs/life_ca_sample/INVALID`, old `seed*/` →
   `runs/life_ca_sample/archive_invalid_cache_C/`.
5. Re-gate (`prompts/ca_sample_gate_diffs.md`) must mention fresh cache + g≥2 live
   assert; then `--allow-api` rerun.

## Distributed hold

`ALLOW_PHASE1` stays **not created** until this Ca-sample rerun closes. DC/DCs use
the same Decisions client; release requires the startup asserts in
`AMENDMENT_DISTRIBUTED_DR_DC_DIFF.md` § release (fresh per-arm cache dirs;
per-generation live/cached/fallback log; fail if Decisions arm at g≥2 has 0 live
or uniform share > 2%).
