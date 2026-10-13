# Task — Reasoning-off Luna without sources (An0): are the sources the engine?

**Status:** locked. Predictions are locked with this file, before any run and before any
new analysis of the An logs. API only (Luna Responses, `effort=none`), no GPU. Follows
`DESIGN_CHECKLIST.md`. Parents: `TASK_LIFE_LUNA_NONE.md` (An), `TASK_LIFE_AN_FILTER.md`
(F1–F4 FAIL), `TASK_LIFE_ONEPASS_NO_SOURCE.md` (Ca0, Da0 conventions).

**Design checklist:** Gate covers items 1–2 (An0 vs An: inbox content only; commit
`prompts/an_no_source_gate_diffs.md` before spend). Item 3: Z1–Z2 are group vs group
(0-source An0 vs 4-source An / Ca0), not “group vs individuals”. Items 4–6 apply. Item 7:
report API USD + prefill/output tokens per cell-generation.

## Why

2-op, J@g10: An 0.47, Ca 0.25, B 0.99. `TASK_LIFE_AN_FILTER` ruled out an own-example filter:
in matched inboxes An adopts the neighbours' majority rule more often than Ca, whether or not it
fits its example, and keeps P_e less well (r 0.71 vs 0.97). An's raw h(1) advantage (0.28 vs 0.03)
comes mostly from inboxes with no competing rule (n_m = 0).

Hypothesis (voter model with zealots): the four sources publish P_e every generation and never
change. In a mobile population (An) they recruit clean P_e neighbourhoods around themselves, which
then spread; in a sticky population (Ca) wrong clusters freeze. If so, An's advantage needs the
sources. Without them An should fall to the level of Ca0 (0.04).

Alternative: An discovers P_e by itself (its own example plus memory of its own rule and the
correct flag) and spreads it by mobility; then An0 stays well above Ca0.

## Arm

| arm | cells | sources | channel | check | parent |
|---|---|---|---|---|---|
| **An0** | Luna Responses, `effort=none` | **0** | on | none | An (4 sources) |

- 2-op seeds 1–5 of the frozen schedule, 10 generations. 1-op not run.
- Sources off with `source_ids_override(())`, as in B0, Ca0, Da0; the four former source cells
  become ordinary cells.
- Everything else as An: same prompt, schema, parser, `effort=none`, memory line, constitution.
  Refusal policy from the An amendment (HTTP 400 `invalid_prompt`: retry once, then `unsolved`;
  log every refusal; > 2% triggers a caveat).
- **References (not rerun):** An, Ca, Ca0, Da0, B, B0.

## Gate (before the first call)

1. Dry-render the g2 request for 3 non-former-source cells (same seed, cell, previous answer) for
   An0 vs An. The request text may differ **only in inbox content**. Constitution, memory line
   format, catalog, example, query and API parameters (`effort=none`) must be byte-identical.
   Checked on the request payload, not a logging reconstruction.
2. Startup asserts: `SOURCE_IDS == ()`; no cell holds P_e at g1 by seeding; `effort=none` on every
   request; no reasoning text requested or stored.
3. Commit `prompts/an_no_source_gate_diffs.md` before the first call.

## Metrics

- J@g10 and mean J over 10 generations, on all 100 cells and on the parents' 96 non-source ids.
  Always label which J.
- First P_e holder per seed (generation, cell); number of P_e holders at g1 (solo discovery, empty
  inbox).
- h(0) (P_e chosen with no P_e in the inbox, prev ≠ P_e), h(1), r, per seed, same definitions as
  `TASK_LIFE_AN_FILTER`.
- Locks and modal rule at g10; invalid / `unsolved` / refusal counts.
- Cost: API USD, prefill and output tokens per cell-generation.

## Descriptive analyses from existing logs (0 API; computed after the lock, reported with An0)

- **D-a. Wave from sources.** For An and Ca (4 sources): J by torus distance to the nearest source
  (1, 2, 3, 4+), per generation g1–g10, per seed. A wave predicts J decreasing with distance and a
  front moving outward over generations.
- **D-b. Stickiness on wrong rules.** P(keep rule | prev ≠ P_e) for An, Ca, B, overall and after
  `correct=false`.
- **D-c. Solo discovery in An.** h(0) in the An logs, per seed.

## Predictions (lock)

- **Z1 (sources are the engine):** An0 seed-mean J@g10 (100 cells) ≤ 0.10.
- **Z2 (the drop is large):** An0 J@g10 (96-cell) ≤ An J@g10 − 0.30 (An 0.469, so ≤ 0.17).
- **Z3 (descriptive):** per seed, first P_e holder and An0 J@g10; D-a, D-b, D-c tables.

## Readout

- **Z1 PASS, Z2 PASS:** An's advantage over Ca is mobility around permanent sources (voter model
  with zealots), not discovery. One-pass and reasoning-off populations need a teacher or a check;
  only reasoning populations (B0) and checked ones (Da0) do without.
- **Z1 FAIL, Z2 PASS:** sources carry most of it, but An also discovers some rules itself;
  report N3-style first holders.
- **Z2 FAIL:** An finds and spreads the rule without a teacher, at least as well as with one;
  mobility plus its own memory is enough. Compare with Da0 (0.79) and B0.

## Cost

One arm × 5 seeds at An rates (~$0.22 per seed): about $1.1. Alarm $3 (not a stop). Report the
actual cost.

## Artifacts

`prompts/an_no_source_gate_diffs.md`, `runs/life_an_no_source/An0/seed{n}/`,
`runs/life_an_no_source/summary.json` (Z1–Z3, with An, Ca, Ca0, Da0, B0 alongside),
`fig_an_no_source.png` (J(g) per seed: An, An0, Ca, Ca0), D-a/D-b/D-c tables in `readout.md`.

## Constraints

Placement only: no training on outputs; no reasoning text requested or stored. New runner script;
do not edit running scripts in place. Commit this file before the gate; amendments before numbers.

## Not in this task (candidate, unregistered)

Extending An and Ca from g10 to g30 to test whether the sticky population catches up (Ca's
steady-share estimate is far above its g10 value; An is already near its own). Ca costs ~$1 per
seed per 10 generations; decide after Z1–Z3.