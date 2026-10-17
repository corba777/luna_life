# Arm registry

New reports and figures use the name `{env}/{agent}/{channel}/{check}`. The old name is an alias. Directory names are unchanged.

`runs/ARM_REGISTRY.md` is an older J@g10 table. It is not this registry.

Env is taken from the logged `source_mask` and the per-seed request count, plus which runner built the world. A mask of `{0, 5, 50, 55}` with 960 Responses calls per seed (96 cells × 10 rounds) is `life1-src4` on the life-1 board and `dist-h4` when the run is a distributed world. An empty mask with 1000 Responses calls per seed is `life1-src0` or `dist`. The distributed worlds are the ones applied by `_apply_world_examples` in `runs/run_life_dr_clean.py` and `runs/run_life_distributed_phase1.py`. One logged source (`B1`, `Ca1`, `Da1`) and the neighbourhood arms (`DRo`, `DRo-iter`) are not in the env vocabulary; those env fields are unverified.

Agent and effort come from the cache row the client stored with the request (`model`, `effort`, and `temperature` when present). The raw HTTP body is not stored. Channel comes from inbox construction. Check comes from a rendered inbox or, where noted, from the renderer branch the logged `k` selects.

Stage-1 training arms are not in this vocabulary. They are not given a name here.

## Rows

| Old name | New name | Evidence |
|---|---|---|
| A | `life1-src4/luna.resp-medium/moore/none` | Mask `{0,5,50,55}`, `k=0` (`runs/life_reasoning_cells/arm_A`). Cache `cache_A`: `gpt-6-luna`, `effort=medium`. Channel on, 8-slot state (`runs/life_reasoning_cells/sample_prompt_review.md`). |
| B | `life1-src4/luna.resp-medium/moore/none` | Seed 1: 960 requests. Same mask and `k=0`. Cache `cache_B`: `effort=medium`. |
| Bs | `life1-src4/luna.resp-medium/none/none` | Seed 1: 864 requests + 96 hits. `ARM_SPEC` `channel: False` (`runs/run_life_reasoning_cells.py`). Cache `cache_Bs`: `effort=medium`. |
| C | `life1-src4/luna.dec/moore/none` | Mask and `k=0`. Decisions cache `cache_C`: `model=gpt-6-luna`, no `effort` (choice/probabilities row). |
| Ca | `life1-src4/luna.dec/moore/none` | Seed 1: 11520 questions = 96×10×12. Same mask, `k=0`. Shares `cache_C`. |
| Cas | `life1-src4/luna.dec/none/none` | Same mask, `k=0`. `channel: False`. Own Decisions cache `cache_Cas`. |
| D | `life1-src4/luna.dec/moore/mark` | Logged `k=1`. Rendered k=1 state has `check:` with ✓ (`runs/life_reasoning_cells/sample_prompt_review.md`, `runs/life_v1b/smoke_renders/state_k1.txt`). Cache `cache_D`. |
| Da | `life1-src4/luna.dec/moore/mark` | Logged `k=1`. Same renderer. Shares `cache_D`. |
| An | `life1-src4/luna.resp-none/moore/none` | Mask `{0,5,50,55}`, `k=0`. Cache `cache_An`: `effort=none`. |
| An-T0 | `life1-src4/luna.resp-none/moore/none` | Same mask, `k=0`. Cache `cache_AnT0`: `effort=none`, `temperature=0.0`. |
| An0 | `life1-src0/luna.resp-none/moore/none` | Empty mask, `k=0`. Seed 1: 1000 requests. Cache `cache_An0`: `effort=none`. |
| Ca0 | `life1-src0/luna.dec/moore/none` | Empty mask, `k=0`. Decisions cache `cache_Ca0`. |
| Da0 | `life1-src0/luna.dec/moore/mark` | Empty mask, logged `k=1`. Decisions cache `cache_Da0`. Same k=1 renderer as D. |
| Ca-sample | `life1-src4/luna.dec/moore/none` | Mask `{0,5,50,55}`, `k=0`. `SimulationV1b(..., channel=True)` in `runs/run_life_ca_sample.py`. Decisions cache `cache_Ca_sample`. |
| Bs-mem, Bs-r | `life1-src4/luna.resp-medium/none/none` | Mask `{0,5,50,55}`, `k=0`. `channel=False` (`runs/run_life_own_memory.py`). Caches `cache_Bs-mem`, `cache_Bs-r`: `effort=medium`. |
| Cas-mem, Cas-r | `life1-src4/luna.dec/none/none` | Same mask, `k=0`, `channel=False`. Decisions caches `cache_Cas-mem`, `cache_Cas-r`. |
| KHs-mem | `life1-src0/luna.resp-medium/none/none` | Empty mask, `k=0`, `channel=False`. Cache `cache_KHs-mem`: `effort=medium`. |
| K2, K4, KH | `life1-src0/luna.resp-medium/moore/none` | Empty mask, `k=0`. `channel: True` (`runs/run_life_critical_mass.py`). Caches `effort=medium`. |
| KHs | `life1-src0/luna.resp-medium/none/none` | Empty mask, `k=0`. `channel: False` in that spec. Cache `cache_KHs`: `effort=medium`. |
| KH-r | `life1-src0/luna.resp-medium/moore/none` | Empty mask, `k=0`. `live_channel` and `render_channel` true (`runs/run_life_discovery_echo.py`). Cache `effort=medium`. |
| KHs-r | `life1-src0/luna.resp-medium/none/none` | Empty mask. Both channel flags false. Cache `cache_KHs-r`: `effort=medium`. |
| KHp, KHe, KHc | `life1-src0/luna.resp-medium/unverified/none` | Empty mask, `k=0`, `effort=medium`. The prompt is an 8-slot inbox filled synthetically (`_synthetic_inbox`), not Moore delivery, not `r8`, not `all`. |
| KHe-pub, KHc-pub, KHv | `life1-src0/luna.resp-medium/unverified/none` | Empty mask, `k=0`, `effort=medium`. `live_channel` false and `render_channel` true (`runs/run_life_publish_void.py`); inbox is echo1, echo8, or eight empty slots. |
| R8 | `life1-src4/luna.dec/r8/none` | Mask `{0,5,50,55}`, `k=0`. Decisions cache `cache_R8/decisions`. Rendered inbox is 8 peer slots with no ✓/✗ (`runs/life_phone/gate_dry.json`, arm R8). |
| R8c | `life1-src4/luna.dec/r8/drop` | Same mask and client. Gate cell 1: R8 keeps `say='shift_symbols(1)'`; R8c renders that slot empty. No ✓/✗. Drop is `engine_ok` in `_build_inbox` (`runs/run_life_phone.v2.py`). |
| All | `life1-src4/luna.dec/all/none` | Same mask. Gate cell 1 renders `Visible messages (66 slots):` and no mark. |
| Allc | `life1-src4/luna.dec/all/drop` | Same mask. Gate cell 1 renders 4 slots, the messages `engine_ok` kept, and no mark. |
| DR, DR_noex | `dist-h4/luna.resp-medium/moore/none` | Mask `{0,5,50,55}` and seed-1 DR: 960 requests, while the report field `n_sources` is 0. Cache `effort=medium`. Replayed world-1 cell 6 round 2 inbox is eight unmarked slots; `shift_symbols(1)` is present. `k=0` (`runs/run_life_distributed_phase1.py`). |
| DRs | `dist-h4/luna.resp-medium/none/none` | Same mask. Seed 1: 942 requests + 18 hits. `channel: False`. Cache `effort=medium`. |
| DC | `dist-h4/luna.dec/moore/none` | Same mask, `k=0`. Decisions cache `cache_DC`. |
| DCs | `dist-h4/luna.dec/none/none` | Same mask, `k=0`, `channel: False`. Decisions cache `cache_DCs`. |
| DRc | `dist/luna.resp-medium/moore/none` | Empty mask, `k=0`. Replicate 1 seed 1: 1000 requests. Cache `effort=medium`. Runner passes `k=0` (`runs/run_life_dr_clean.py:234`). Replayed cell 6 round 2 keeps unmarked `shift_symbols(1)`. The 30-round continuation is this same arm. |
| DRc-noex | `dist/luna.resp-medium/moore/none` | Empty mask, `k=0`, 1000 requests on replicate 1 seed 1. Cache `effort=medium`. Own example is hidden from round 2; the inbox builder is the same unmarked Moore inbox. |
| DRo | `unverified/luna.resp-medium/none/none` | No `source_mask`. Report `n_nbhd=20`. Cache `cache_DRo`: 100 rows, `effort=medium`. `channel: False` in `run_dro`. |
| DRo-iter | `unverified/luna.resp-medium/none/none` | No `source_mask`. Cache `cache_DRo_iter`: 1000 rows, `effort=medium`. `runs/run_life_dro_iter.py` does not call `source_ids_override`. |
| DR_T | `dist-h4/qwen4bT.local/moore/none` | Mask `{0,5,50,55}`, `k=0`. Cache `cache_DR_T`: `served_model=Qwen/Qwen3-4B-Thinking-2507`, no `effort` field. Same distributed inbox builder as DR. |
| DRs_T | `dist-h4/qwen4bT.local/none/none` | Same mask and served model. Silent distributed channel (`DRs` constitution). Cache `cache_DRs_T`. |
| B0 | `life1-src0/luna.resp-medium/moore/none` | Empty mask, `k=0`. Seed 1: 1000 requests. `channel=True` (`runs/run_life_long_chain.py`). Cache `effort=medium`. |
| B1 | `unverified/luna.resp-medium/moore/none` | Mask `{0}` only, `k=0`. Seed 1: 990 requests (99×10). Not one of the four env tokens. |
| Ca1 | `unverified/luna.dec/moore/none` | Mask `{0}`, `k=0`. Decisions cache `cache_Ca1`. |
| Da1 | `unverified/luna.dec/moore/mark` | Mask `{0}`, logged `k=1`. Decisions cache `cache_Da1`. |
| Ca-r | `life1-src4/luna.dec/moore/none` | Mask `{0,5,50,55}`, `k=0`. Decisions cache only (`cache_Ca-r/decisions`, 43199 rows). `runs/run_life_tech_lead.py` sets `k=0`. |
| Da-r | `life1-src4/luna.dec/moore/mark` | Same mask, logged `k=1`. Decisions cache only. |
| Dr | `life1-src4/luna.dec/moore/review` | Same mask, cell `k=0`. Reviewer cache `cache_Dr/reviewer`: 2568 rows, `gpt-6-luna`, `effort=medium`. `ReviewerClient` sends an accept/reject prompt and can drop rules (`runs/run_life_tech_lead.py`). |
| Mx10, Mx25, Mx50 | `life1-src4/luna.resp-medium+luna.dec/moore/none` | Same mask, `k=0`. Both caches are nonempty: Mx10 has 500 Responses rows (`effort=medium`) and 38699 Decisions rows; Mx25 has 1250 and 31949; Mx50 has 2500 and 20699. |

## Same arm, not a new row

Aborted and archived runs use the parent row. They are `life_ca_sample/archive_invalid_cache_C`, `life_reasoning_cells/archive_bs_nochannel_bug_20261010`, `life_distributed/archive_cross_version_memory_fix`, `life_local_reasoning/step0_aborted_*`, and `life_phone/r8_partial_647c1ed`.

`life_verify/v1b_m0_pilot` has no Luna or local-Qwen request cache. Its agent is unverified. Logged `k` is 0 or 2 and the source mask is either empty or `{0,5,50,55}`.
