# Task — OpenAI Decisions API (`gpt-6-luna`) zero-shot battery

**Locked 2026-10-08 before any Stage-1 / Life metric on this model** (smoke + 101-choice probe only). Third closed decision vendor next to TypeSafe and GLiDE. Outputs are **placement only** — never train our models on them.

**Gate:** after Life v1b M_0 pilot frees attention (`QUEUE_ORDER` §2b). API-only — does **not** need the Spark GPU. **Deviation (2026-10-08):** ran API-parallel to the live v1b GPU pilot — preds were already locked; no Spark / no pilot attention steal. Recorded in `QUEUE_ORDER` §2b.

Docs: [Decisions guide](https://developers.openai.com/api/docs/guides/decisions). Endpoint `POST /v1/decisions`, model `gpt-6-luna` (public beta). Pricing (as of smoke): **$0.10 / 1M input tokens**; no output / cache charges.

## Questions

1. On **choice listening** (E1-P), is `gpt-6-luna` nearer TypeSafe (~0.55 `pragmatic_argmax_L2` on the Part-B subset ladder) or GLiDE (~0.80)?
2. On **content listening** (E-HP v2.1), does it match the TypeSafe / trained openjev band (high value, low FA_sat)?
3. Does it **read partner choice / omission** on E-HP (`other − none`)? Prediction: no.
4. On Life / engine-check surfaces: does it read ready ✓/✗ like M_0 under `engine_check_v1` (ceiling), and how credulous is it on Part-2 arms?

## Predictions (do not edit after first battery number)

Analogous to TypeSafe; written before any eval artifact under `runs/eval_openai_decisions*`.

1. **Speaker informative** on E1-P / E-HP: `speaker_index` (soft and/or argmax) and `requirement_share` in the TypeSafe / trained-sender band, not M_0-soft.
2. **Content listening good** on E-HP v2.1: `value_discrimination` (`viol−sat`) high; FA_sat near 0; `P_anti_none` low under Variant B + `goal_explicit`.
3. **Choice pragmatics between TypeSafe and GLiDE:** E1-P relabel `pragmatic_index` (soft) and especially **`pragmatic_argmax_L2` / choice ladder** sit **strictly between** TypeSafe (~0.55 choice) and GLiDE (~0.80) on the same Part-B subset when recomputed; if outside, say so — do not force the band.
4. **No E-HP choice-from-omission:** `override_other_dim − P_anti_none` ≈ 0 or slightly **positive** (same as TypeSafe / GLiDE on v2.1) — not a calm toward consensus.
5. **Engine-check:** on nops-matched pairs under `engine_check_v1`, catalog / named-pref near ceiling (like M_0’s valid probe: choice → 1.0). On **default** Life render (no marks), pair pref near M_0 / TypeSafe, not trained verify.
6. **Speak-easy / listen-hard** still holds in the TypeSafe sense: speaker climb available from prompt+model; choice listening not unlocked by strength alone.

## Environments (priority order)

| # | Env | Metrics | Skip if |
|---|---|---|---|
| 1 | **E1-P** val + relabel (n=100, seeds 12/13) | `R_team`, soft + argmax `speaker_index`, soft `pragmatic_index`, choice/`pragmatic_argmax_L2` on Part-B subset beside, `protocol_fidelity_p` | — |
| 2 | **E-HP v2.1** val + relabel (Variant B + `goal_explicit`, n=100) | `R_team`, req-share, value / hit / FA_sat, `P_anti_none`, `other−none` | — |
| 3 | **Life Part-2 probe** arms + **engine_check_v1** on nops-matched pairs | `delta_named[_choice]`, mixed 1T7F / 1F7T, follow_false descriptive; engine Δ vs default | 101-choice probe fails |
| 4 | **L-VERIFY pairs** nops-matched (`PAIR_VER=nops_matched_v1`, n=200) | `pair_pref_choice`, `pair_pref_mass`, vs M_0 0.625 | — |
| — | E-HP v1, grounded E1 | — | **Do not run** (v1 prompt-distorted; E1 uninformative) |

## Adapter rules

- **Same prompt surface** as TypeSafe / GLiDE: render → `state` mapped to Decisions `input`; question → `instructions`; option text → `choices[].description`. Machine `value` is opaque (`opt_0`…) — Luna can refuse when `value==description` on off-support words; descriptions carry the readable text.
- **One choice question per request.** Docs: related decisions separately. No bundling sender+receiver.
- **P = 4** option-order permutations; mean π in canonical order; report order sensitivity (max |Δp| across perms) on a small sample.
- **Refusal** (`type: refusal`): opaque `opt_*` values → force appendix → letter values; if still refused → **uniform** π (count `refusal_uniform`; do not skip the instance). Missing probabilities on a non-refusal answer → abort. Report `refusals` / `forced_choice_retries` / `refusal_uniform` / `outcomes_{first,forced,uniform}`. **Cache hits must restore those counters from `forced_choice` / `refusal_uniform` flags** (else recount undercounts after a resume).
- **Report beside primary:** (1) outcome fraction per metric step (R_team / speaker / listener / fidelity); (2) soft `pragmatic_index` and `pragmatic_argmax_L2` on **first-try-only** words (all P perms `outcome=first`) — descriptive, not a substitute. If `outcomes_uniform` is more than a few % of relabel receiver calls, read choice-listening with that caveat.
- **Prediction 3 primary:** `pragmatic_argmax_L2` on the **Part-B subset** (E1-P relabel, gen seed 13, first n=50, L0≠L2 filter; same ids as `runs/reasoning/diag_e1p_partb_subset_ladder_5seed.json`), vs TypeSafe 0.549 / GLiDE 0.817. Soft prg alone does not decide pred 3.
- **Record** wall date, requested model id, API-returned `model`, usage totals, SDK/HTTP path. Public beta — model may change before GA. Include `e1p_noise` L1 (draw=0 vs draw=1) as a determinism fact.
- Disk cache content-keyed like TypeSafe (`runs/openai_decisions/cache/`).
- Key: `OPENAI_API_KEY` from `.env` (never commit).

### Choice-count probe (done before battery — 2026-10-08)

Smoke: **101 choices OK** (`HTTP 200`, 101 probabilities, ~0.16 s, ~1325 input tokens). Life catalog head is unblocked. Re-check if API errors mid-battery with a smaller catalog.

## Implementation pointers

| Piece | Path |
|---|---|
| Client (`choose` duck-types `TypeSafeClient`) | `openai_decisions_client.py` |
| Policy | wrap with `typesafe_policy.TypeSafePolicy(client)` (P=4) |
| Battery entry | `runs/eval_openai_decisions_battery.py` |
| Smoke / preflight | `runs/smoke_openai_decisions.py` |
| Artifacts | `runs/eval_openai_decisions_battery.json`, per-env shards if needed |
| Predictions (this file) | do not edit after first number |

Reuse `runs/eval_glide_battery.py` structure and `E.evaluate_hp` / `speaker_index_p` / `pragmatic_index_p`. For Part-2 / engine-check, mirror `runs/eval_life_verify_part2_probe.py` and `runs/diag_lv_engine_check_m0.py` but call the Decisions client (no GPU).

## Cost (order of magnitude)

- E1-P n=100 × 2 splits × P=4 × (1 sender + ~K receiver probes): same ballpark as GLiDE ~**$0.5** if ~5M input tokens.
- Full registered Life torus: **hundreds of $** — **out of scope**. Part-2 probe + engine-check pairs only (~few $).
- Decide any torus arm only after v1b M_0 pilot + this battery’s Life-probe readout.

## Deliverables

1. Green smoke: auth, choice, predicate optional, 101-choice, refusal path unit-tested with a mock.
2. Battery JSON with all primary metrics + usage + model stamp.
3. One paragraph for `PAPER_CLAIMS.md`: where `gpt-6-luna` sits vs TypeSafe / GLiDE / M_0 on choice vs content; predictions 1–6 pass/fail.
4. Do **not** start SPADE or touch `runs/ALLOW_SPADE` from this task.
