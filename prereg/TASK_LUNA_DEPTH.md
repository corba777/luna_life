# Task — Luna depth curve: does the one-pass gap grow with composition depth?

**Status:** locked 2026-10-09. Predictions below locked **before** any 3-op accuracy
number. Commit this file before the first generator check that produces the held-out set.
API-only, placement only. Parent: `TASK_LUNA_REASONING_MODES.md` (closed); its 1-op and
2-op numbers are reused, not re-run.

**Post gate:** do not publish `LUNA_DRAFT.md` until this curve is in (or D2 fails and the
failure is written into the post). Chart target = depth × mode, not three separate panels.

## Question

We have two points: Decisions 0.94 (1-op) → 0.59 (2-op); reasoning medium 1.00 → 0.995.
Two points cannot separate "two-step rules are specifically hard" from "accuracy falls with
computation depth". A third depth answers that, for both modes, and turns the post's chart
into a depth × mode curve.

## Set: 3-op pairs (new, outside the Life catalog)

Constants (frozen):

| knob | value |
|---|---|
| `DEPTH_SEED` | **5410** |
| `DEPTH_PAIR_VERSION` | `depth3_v1` |
| held-out 3-op functions | **25** |
| pairs | **100** (~4 per function) |
| modes | `decisions`, `resp_none`, `resp_medium` (skip `high`) |

1. **Generate 3-op functions** as compositions `a;b;c` of the 17 single operations, applied
   left to right (same `Program` / `CanonicalFunction` semantics and description format as
   the catalog, e.g. `reverse;shift_symbols(2);swap(0,3)`). Enumerate all 17³ candidates.
2. **Deduplicate by behaviour** over all 8^4 = 4096 input strings (`output_table`): drop any
   composition equal to the identity, to any 1-op or 2-op catalog function, or to another
   kept 3-op function. Report counts before/after in the generator-check artifact.
3. **Held-out sample:** 25 functions from the deduped pool, RNG seeded by `DEPTH_SEED`
   (committed). Report the 25 `program_id`s / descriptions.
4. **Pairs:** 100 pairs, ~4 per function, true 3-op vs a false 3-op from the **same 25-pool**
   (same-depth false — analogue of `nops_matched_v1`). Same canonical harness as
   `nops_matched_v1` (same `N_EXAMPLES`, same rendering). False rule must be inconsistent
   with the private examples. Ids:
   `lv-pair-depth3_v1-heldout_fn-s5410-op3-{k:04d}`.
5. **Options:** the 101-rule Life catalog **plus** that pair's two 3-op descriptions
   (103 options), shuffled by the same P=4 / K=8 ordering scheme as the parent. Adapter
   difference vs 1-op/2-op (101 options) is recorded; it adds two options, not a new format.
   Do **not** put 3-op rules into the Life catalog or into any Life / v1b run.

**Identifying examples (implementation note, locked):** parent
`sample_identifying_examples` / `hypothesis_set` are catalog-relative and will not see
out-of-catalog 3-op rules. The depth generator must:

- sample examples consistent with the true 3-op;
- reject any candidate example set on which the false 3-op also fits;
- optionally also reject sets that uniquely identify some ≤2-op catalog rule instead of
  the true 3-op (so the pair is not solvable by collapsing to a shorter equivalent — already
  prevented by behavioural dedupe against ≤2-op).

Do not silently fall back to the Life catalog sampler.

**Generator checks (no model, before any API call):** dedupe counts; zero behavioural
overlap with ≤2-op; every pair's false rule inconsistent with its examples; description
strings parse back to the same function; 25 functions × 100 pairs deterministic under
`DEPTH_SEED`. Artifact: `runs/openai_decisions/luna_depth_generator_check.json`.

## Modes

Same estimators and settings as the parent task:
- `decisions` (P=4, probabilities over the 103 option labels),
- `resp_none` (K=8),
- `resp_medium` (K=8; medium was already at plateau on 2-op, so high is skipped).
Same `max_output_tokens=8192` as the parent; truncation counted as invalid and reported.

Rough cost: 100 pairs × 8 × 2 Responses modes ≈ 1,600 Responses calls + ~400 Decisions
calls — same order as one parent stratum; a few dollars / a few hours.

## Metric and statistics

`pair_pref_choice` (ties 0.5). Paired by pair; cluster bootstrap by held-out function
(25 clusters). Depth curve = 1-op and 2-op from the parent task + 3-op from this one, per
mode. Also report mean / max reasoning tokens per depth for `resp_medium` (parent already
has 1-op ≈ 227, 2-op ≈ 689 — D5 continues that series).

## Predictions (lock — do not edit after first 3-op accuracy number)

- **D1:** `decisions` 3-op ≤ 0.65 (near chance, at or below its 2-op 0.59 + 0.06).
- **D2:** `resp_medium` 3-op ≥ 0.90.
- **D3 (primary):** `resp_medium` − `decisions` on 3-op ≥ **+0.25**, cluster CI excludes 0.
- **D4 (control):** |`resp_none` − `decisions`| on 3-op < 0.10.
- **D5 (descriptive):** mean reasoning tokens for `resp_medium` rise with depth
  (1-op < 2-op < 3-op).

## Readout

- D1 + D2 + D3 PASS → the one-pass gap opens at two steps and stays open; reasoning covers
  three steps too. Post chart becomes the depth curve.
- D2 FAIL (reasoning drops at 3-op) → a few hundred tokens are enough for two steps but not
  three: report the reasoning-token budget against depth; consider `resp_high` on 3-op as a
  follow-up (**amendment first**).
- D1 FAIL (Decisions above 0.65 at 3-op) → depth alone does not explain the 2-op failure;
  look at which operation types the 2-op failures concentrate on.

## Constraints

Placement only; no training on outputs; no reasoning text requested or stored. No changes
to generator, pairs or estimator after the first 3-op number. Life catalog and v1b
unchanged.

## Artifacts

- `runs/openai_decisions/luna_depth_generator_check.json`
- `runs/openai_decisions/luna_depth.json` (per-pair rows, per-mode summaries, contrasts
  with CIs, depth curve table 1/2/3-op × mode)
- Update `LUNA_DRAFT.md` Results figure to depth × mode; refresh "What it means" after
  readout (mode-limit wording already drafted; Part C bridge stays).
