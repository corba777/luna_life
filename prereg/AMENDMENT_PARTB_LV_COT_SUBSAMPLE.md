# Amendment — Part B LV `reason` capped subsample (ETA > 12 h)

**Status:** locked 2026-10-13 **after** stopping the live `reason` arm;
**before** any continue / relaunch. Parent: `AMENDMENT_PARTB_LV_PAIRS.md`.
Queue slot: **after Unsloth hybrid** (`AMENDMENT_QUEUE_DEFER_PARTB_LV_COT.md`).
Does **not** change the locked pair set seed, `max_tokens`, prompts, or
`enable_thinking` contract (those need a separate amendment).

## Evidence (no accuracy / preference read)

Live job: `runs/eval_partb_lv_pairs.py --mode both` under
`runs/reasoning/queue_partb_lv_pairs.sh` (SGLang 35B-A3B-FP8).

| | |
|---|---|
| `direct_matched` | **200/200 done** (~10:53–11:21 local); cached |
| `reason` (cot / `enable_thinking=true`) | **5/200** at stop |
| Cot start (first thinking cache) | **2026-10-13T11:27:01** |
| Elapsed at audit | **~6.9 h** (not an ETA) |
| Rate | **≈ 0.72 pairs/h** (5 pairs / 6.9 h wall) |
| ETA remaining at that rate | **≈ 270 h** |
| Client concurrency | `max_concurrency=1`, `n_draw_inflight=1` |
| Server `max_running_requests` | **not 1** — see serve snapshot below |

**Interpret 0.72 pairs/h correctly:** bottleneck was **client** serial
scheduling (`eval_partb_lv_pairs.py` → `eval_pairs(client)` without
`--max-concurrency`), not a server cap of 1. Server was launched with
`REASONING=1` and `max_running_requests=None` → SGLang mamba state cache
capped running requests at **68**. Snapshot:
`runs/reasoning/partb_lv_serve_config_aborted_cot.json`.

### Serve config during aborted cot (35B-A3B-FP8)

From `runs/reasoning/sglang_partb.log` (first `ServerArgs` for
`Qwen/Qwen3.6-35B-A3B-FP8`, queue `REASONING=1`):

| Field | Value |
|---|---|
| `model` | `Qwen/Qwen3.6-35B-A3B-FP8` |
| `REASONING` / `--context-length` | **1** / **32768** |
| `--reasoning-parser` | **qwen3** |
| `--mem-fraction-static` | **0.7** |
| `--max-running-requests` (arg) | **None** (unset) |
| effective `max_running_requests` | **68** (mamba state-cache cap; log line) |

Contrast with Phase 0 v2 abort (`phase0_serve_config_diff.json`): that watcher
set `REASONING=0`, ctx **4096**, and `--max-running-requests=1`. Part B cot did
**not** use that pattern.

Serial CoT at `max_tokens=16384` with client concurrency 1 cannot finish n=200
inside a 12 h budget.

## Decision (stop rule)

If ETA at current rate exceeds **12 h** → **stop** and lock a capped subsample
before continuing. Triggered → process stopped;
`runs/spade_grid/resume_chain.aborted` written (Part B cot wall-clock).

## Locked subsample (committed RNG)

- **Pool:** locked `PAIR_EVAL_SEED=5401`, `nops_matched_v1`, `heldout_fn`,
  harness `canonical`, n=200 (100 per `n_ops`).
- **Subsample seed:** `20261013` (`numpy.random.default_rng(20261013)`).
- **Draw:** without replacement, **8** ids from `n_ops=2` and **8** from
  `n_ops=1` (16 total). Machine list:
  `runs/reasoning/partb_lv_cot_subsample_16.json`.

**Pair ids (n_ops=2 then n_ops=1):**

1. `lv-pair-nops_matched_v1-heldout_fn-s5401-op2-0008`
2. `lv-pair-nops_matched_v1-heldout_fn-s5401-op2-0010`
3. `lv-pair-nops_matched_v1-heldout_fn-s5401-op2-0022`
4. `lv-pair-nops_matched_v1-heldout_fn-s5401-op2-0033`
5. `lv-pair-nops_matched_v1-heldout_fn-s5401-op2-0039`
6. `lv-pair-nops_matched_v1-heldout_fn-s5401-op2-0051`
7. `lv-pair-nops_matched_v1-heldout_fn-s5401-op2-0066`
8. `lv-pair-nops_matched_v1-heldout_fn-s5401-op2-0087`
9. `lv-pair-nops_matched_v1-heldout_fn-s5401-op1-0006`
10. `lv-pair-nops_matched_v1-heldout_fn-s5401-op1-0007`
11. `lv-pair-nops_matched_v1-heldout_fn-s5401-op1-0008`
12. `lv-pair-nops_matched_v1-heldout_fn-s5401-op1-0017`
13. `lv-pair-nops_matched_v1-heldout_fn-s5401-op1-0045`
14. `lv-pair-nops_matched_v1-heldout_fn-s5401-op1-0083`
15. `lv-pair-nops_matched_v1-heldout_fn-s5401-op1-0084`
16. `lv-pair-nops_matched_v1-heldout_fn-s5401-op1-0099`

## Continue protocol (after Unsloth hybrid)

1. **Keep** finished `direct_matched` (full n=200); do not re-run direct.
2. **Serve-config diff gate (same checklist as Phase 0 §7 / `phase0_serve_config_diff.json`), before any relaunch:** write
   `runs/reasoning/partb_lv_serve_config_diff_pre_relaunch.json` comparing the
   live `ServerArgs` to the aborted-cot snapshot above. Required match
   (else abort, do not start pairs):
   - `REASONING=1`, `--context-length=32768`, `--reasoning-parser=qwen3`
   - `model=Qwen/Qwen3.6-35B-A3B-FP8`
   - `--mem-fraction-static` ≈ 0.7
   - `--max-running-requests` unset/None **or** ≥ client `n_draw_inflight`
     (do **not** silently adopt Phase 0 v2’s `max_running_requests=1`)
3. Run `reason` **only** on the 16 ids above.
4. Wire SPADE-grid concurrency: `max_concurrency=64`, `n_draw_inflight=64`
   (client scheduling only — **not** a change to `max_tokens` or prompts).
   Cache / work-unit keys are independent of the window (`eval_spade_grid.py`);
   SGLang posts are unseeded — see `CHAIN_HYGIENE.md` §8.
5. **Readout of the n=16 run (mandatory, before any full-set go):**
   - throughput **pairs/h** at concurrency 64 / inflight 64;
   - linear **ETA for n=200** at that measured rate;
   - then decide whether to launch the full set (separate explicit go).
6. **P-LV1 at n=16 is diagnostic only.** No preference claim, no Part C gate,
   no “reason beats direct” language from the subsample. Registered primary
   P-LV1 remains the full n=200 / cluster bootstrap under
   `AMENDMENT_PARTB_LV_PAIRS.md`.
7. Artifacts: `partb_lv_pairs_reason_sub16.json`; fields
   `subsample_n=16`, `subsample_seed=20261013`,
   `subsample_amendment=this file`, `p_lv1_status=diagnostic_only`.

## Out of scope (need a separate amendment)

- Changing `max_tokens`, prompts, sampling, K, or `enable_thinking`.
- Treating the aborted 5/200 running `mean_pref` as a Part B result.
- Auto-starting this arm before Unsloth hybrid finishes.
