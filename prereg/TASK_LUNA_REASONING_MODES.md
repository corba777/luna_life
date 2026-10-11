# Task — `gpt-6-luna` modes: Decisions vs Responses (reasoning none / medium / high)

**Status:** closed 2026-10-09 (honest CIs). Placement only — outputs are never training data;
reasoning text is never requested, stored or used. API-only, no GPU.

**Close:** R0–R5 all PASS under paired cluster / instance-cluster CIs with Decisions
resampled (`runs/openai_decisions/luna_modes_cis_fixed.json`). Point estimates unchanged;
prior zero-width high−Decisions CI was a bug (constant Decisions mean). Dose plateau at
medium → Life arms A/B use medium. Appendix D in `PAPER_CLAIMS.md`.

Parent: `TASK_OPENAI_DECISIONS_BATTERY.md` (Decisions numbers already exist and are reused,
not re-run).

## Question

Same weights, four ways of answering. Is the two-op failure a missing **intermediate
computation** (compositionality gap: apply op₁, hold the result, apply op₂ — fixed by a
reasoning trace that can write that result down) or missing knowledge (not fixed)?
Not “looking ahead in time”; two serial compute steps in one pass.

| mode | endpoint | output |
|---|---|---|
| `decisions` | `POST /v1/decisions` | probabilities (existing artifacts) |
| `resp_none` | Responses API, `reasoning.effort = "none"` | one option key per sample |
| `resp_medium` | Responses API, `reasoning.effort = "medium"` | one option key per sample |
| `resp_high` | Responses API, `reasoning.effort = "high"` | one option key per sample |

Public descriptions place `gpt-6-luna` as the lowest tier of a GPT-6 reasoning family with
settable reasoning effort; how Decisions mode is built is not documented. We make no claim
about Decisions internals.

## Sets (priority order)

1. **L-VERIFY pairs**, nops-matched — `PAIR_EVAL_SEED=5401`, `nops_matched_v1`, canonical
   harness, `heldout_fn`, default render (no engine marks), n=200 (100 per n_ops). Same pairs
   as `lv_pairs` in the Decisions battery.
2. **Life Part-2, `false` arm**, same instances as `luna_part2_probe.json` (n=101; 17×1-op,
   84×2-op). Plus the `true` arm, needed for the named contrast.
3. **E1-P Part-B subset** (relabel, gen seed 13, L0≠L2 ∩ L2⊂L0; 46 instances, 153 words) —
   receiver only, `pragmatic_argmax_L2`.

Not in scope: E-HP, mixed arms, `engine_check_v1` (Decisions already at ceiling), torus.

## Estimator (Responses modes)

- **Prompt surface:** the same state and question text as Decisions. Options are rendered as
  a list `key: description`, using the same opaque keys (`opt_i`), and the instruction ends
  with "Answer with the key only." Structured output (JSON schema with `enum` of keys) if
  supported in that mode; otherwise plain text with a strict parse. This adapter difference
  is recorded in the artifact.
- **K = 8 samples per question**, spread over the P=4 option orderings (2 samples each).
  Default sampling settings; record whatever the API reports.
- **Choice:** empirical π from the 8 keys. `pair_pref_choice` = 1 if count(true) >
  count(false), 0.5 on ties (including both 0), else 0 — same rule as `LV.evaluate_lv`.
  Part-2 / E1-P argmax = modal key; ties broken uniformly at random with a fixed seed;
  report tie rate.
- **Invalid output** (not exactly one valid key): one re-sample; if still invalid, the
  sample is dropped. Report invalid rate per mode × set. A question with 0 valid samples is
  scored as a tie (pairs) or uniform (argmax) and counted.
- **Never request reasoning summaries.** Store only final key, usage (input / output /
  reasoning tokens / cache fields as returned), model id returned, latency.
- **Comparisons are on choice only.** Mass is reported for `decisions` and never compared
  with sampled π.

## Cost gate (smoke, before any full set)

**Budget (locked):** **$50**.

**How dollars are obtained.** Smoke records **measured** `usage` from each Responses
call (input / output / `reasoning_tokens` / cache fields). The Responses object has **no
billed-cost field** (verified 2026-10-09); the organization Costs API returned 403 on this
key. Therefore the gate’s `$` figure is **measured tokens × OpenAI published list rates**
for `gpt-6-luna` Responses (input $0.10/M, cached input $0.01/M, cache writes $0.125/M,
output incl. reasoning $0.50/M) — not a projection of token counts, and not Decisions’
input-only $0.10/M. If a future usage payload includes a cost field, that becomes primary
and list-rate conversion is demoted to beside.

Decisions artifacts are reused and **not** re-billed.

1. Smoke: 10 pairs from the n_ops=2 stratum, `resp_high`, K=8. The script prints **usage
   only** (measured tokens, list-rate $ from those tokens, invalid rate) — **no accuracy**
   is computed or printed.
2. Project total cost for sets 1–3 in all three Responses modes by scaling smoke
   $/sample (and a short `resp_none` / `resp_medium` token spot-check if high-only smoke
   understates those modes — optional; default scale high smoke ×3 modes as upper bound).
3. Proceed if projected ≤ **$50**. Otherwise, in this order: drop set 3; then K=4
   (1 per ordering); then n=50 per n_ops stratum in set 1. The chosen reduction is
   committed as an amendment **before** the full run. Smoke answers are cached and
   reused, so no smoke call is wasted.

$50 leaves headroom if `resp_high` runs to tens of thousands of reasoning tokens; the cut
order is a safety net and is not expected to fire at list rates with moderate reasoning.

## Predictions (lock with this file)

Pairs, n_ops=2 (primary). Statistic: paired by pair, cluster bootstrap by held-out function.

- **R1 (primary):** `resp_high` − `decisions` ≥ **+0.15** on `pair_pref_choice`, CI excludes 0.
- **R2:** |`resp_none` − `decisions`| < 0.10 — without reasoning the mode does not matter.
- **R3 (1-op, descriptive):** `decisions` and all Responses modes ≥ 0.85; reasoning gain
  smaller than on 2-op.
- **R0 (depth curve, descriptive, no threshold):** on 2-op `pair_pref_choice` point
  estimates, `resp_none` ≤ `resp_medium` ≤ `resp_high`. Strengthens the intermediate-step
  reading if the lift grows with effort; not a pass/fail gate.

Part-2 `false` arm, 2-op (n=84; descriptive CI by instance):

- **R4:** `resp_high` follows the named false rule ≤ 0.50 (Decisions 0.76) and recovers the
  true rule > 0.10 (Decisions 0.00).

E1-P Part-B subset (instance-cluster bootstrap, n=46):

- **R5:** `resp_high` − `decisions` on `pragmatic_argmax_L2` ≥ +0.08, CI excludes 0 — reasoning
  moves Luna toward GLiDE (0.817). If set 3 is dropped by the cost gate, R5 is not tested.

## Readout

| R1 | R2 | Reading |
|---|---|---|
| PASS | PASS | Two-op verification needs an intermediate step; the weights have the knowledge. Supports Part C (teach the decision model to make that step internally) and engine checks in Life as an external step. |
| FAIL | PASS | Even with reasoning Luna does not check compositions on this surface — knowledge or task framing, not just depth. Life relies on engine checks; Part C verification target is weakened. |
| PASS | FAIL | Mode matters even without reasoning (Responses ≠ Decisions); report both gaps separately; do not attribute the gain to reasoning alone. |
| FAIL | FAIL | Report as is; no further Luna modes. |

**R0 beside:** monotone none→medium→high supports depth-as-intermediate-step; flat or
inverted depth curve weakens that reading even if R1 passes.

## Constraints

- Placement only. No Luna output (answers or anything else) enters any training set.
- Same pairs / instances / harness as the existing Decisions artifacts; no edits after the
  first Responses accuracy number.
- Record model id returned by Responses; abort if it is not a `gpt-6-luna` variant, or if
  it changes mid-run.
- Refusals: same policy as the Decisions client (one forced retry, then counted as invalid).

## Artifacts

- `runs/openai_decisions/luna_modes_smoke_cost.json` (usage only)
- `runs/openai_decisions/luna_modes.json` (per-question rows: mode, keys sampled, tie/invalid
  flags, usage; summaries per set × n_ops × mode; paired contrasts with CIs)
- One paragraph in `PAPER_CLAIMS.md` appendix D after readout.
