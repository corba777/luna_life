# Task — One-pass populations without a teacher (0 sources)

**Status:** locked (predictions N1–N3 with this file, before any run / before gate). API only (Luna
Decisions), no GPU. Parents: `TASK_LIFE_REASONING_CELLS.md` (Ca, Da, Cas),
`AMENDMENT_LONG_CHAIN_B0.md` (B0, the 0-source reasoning arm).

**Design checklist** (`DESIGN_CHECKLIST.md`, next to `runs/spade_grid/CHAIN_HYGIENE.md`): this
task’s gate already covers **items 1–2** (expected prompt diff written before the gate; gate
fails on any unlisted difference — see Gate and `prompts/onepass_no_source_gate_diffs.md`).
**Item 3 is not covered:** there is no single-agent arm; N1–N2 are worded as group vs. group
(0-source population vs 4-source parent / Cas), not as “the group does what individuals cannot”.
Items 4–6 apply as usual to post-hoc / claim scope / metric naming. Predictions N1–N3 unchanged.

## Why

"No teacher needed" (B0/B1: reasoning populations with 0 or 1 source reach the same J as with 4) was
shown for reasoning cells only. The own-memory runs suggest why: a reasoning cell that remembers its
own rule solves two-op rules alone (Bs-mem J@g10 0.89), so the population does not need a source.

One-pass cells do not solve two-op rules alone (Cas 0.00). With the channel and 4 sources they reach
mean J 0.14 (Ca); with engine checks on incoming rules, 0.67 (Da). Whether these numbers come from
spreading the sources' rule or from discovery inside the population has not been tested.

## Arms

| arm | cells | sources | channel | check on incoming rules | parent (4 sources) |
|---|---|---|---|---|---|
| **Ca0** | one-pass (Decisions, argmax) | **0** | on | none | Ca |
| **Da0** | one-pass (Decisions, argmax) | **0** | on | engine ✓/✗ (k=1) | Da |

- World seeds: 2-op seeds of the frozen schedule (same as Ca, Da, B0), 10 generations.
- Everything else identical to the parent arm. As in B0, sources are switched off with
  `source_ids_override(())`; the four former source cells become ordinary cells.
- **J is computed over all 100 cells** (there are no sources). For the comparison with the parents,
  also report J over the parents' 96 non-source cell ids.
- **References (not rerun):** Ca, Da (4 sources), Cas (silent), B0 (reasoning, 0 sources).

## Gate (before the first call)

- Dry-render g2 prompts for 3 non-former-source cells per arm and diff against the parent arm (same
  seed, cell, previous answer). Expected differences: inbox content only (no sources means
  different neighbours' rules). Constitution, memory line format, catalog, examples and query must
  be identical. Any other differing line fails the gate.
- Assert at startup: `SOURCE_IDS == ()`, no cell is seeded with P_e at g1, decode argmax, Da0 k=1.
- Commit diffs as `prompts/onepass_no_source_gate_diffs.md`.

## Metrics

- J at g10 and mean J over 10 generations (100 cells; and 96-cell for comparison); correct and
  false locks; modal rule at g10.
- **First appearance of P_e:** generation and cell of the first cell holding P_e per seed; number of
  cells holding P_e at g1 (solo discovery rate of one-pass cells, no inbox at g1).
- For Da0: share of P_e holders at g10 that descend from a check-accepted P_e in their inbox
  (spread) vs held P_e with P_e absent from inbox (unreceived).
- Validity: invalid / fallback counts.

## Predictions (lock)

- **N1 (one-pass Ca needs the teacher):** Ca0 seed-mean J@g10 ≤ 0.05.
- **N2 (the check spreads, but cannot replace the teacher):** Da0 seed-mean J@g10 ≤ Da seed-mean
  J@g10 − 0.20.
- **N3 (descriptive):** per seed, generation of the first P_e holder in Da0, and Da0 J@g10 in
  seeds where at least one cell holds P_e by g3.

## Readout

- **N1 PASS:** Ca's 0.14 is spreading from the sources; one-pass populations without a check do not
  discover two-op rules. "No teacher needed" holds for reasoning cells only.
- **N1 FAIL:** one-pass populations discover some two-op rules through the channel without a
  source; report how (first holders, inboxes).
- **N2 PASS:** with engine checks, one-pass populations still depend on a teacher; the check filters
  and spreads, it does not discover.
- **N2 FAIL:** a few chance discoveries plus an external check are enough without a teacher;
  report N3 per seed.

## Cost

Two Decisions arms × 5 seeds, same as Ca/Da per seed. Estimate a few dollars; cap $8 as an alarm,
not a stop. Runs after own-memory closes, before or in parallel with Dr-cat (separate process,
combined cost tracked). Report the actual cost.

## Artifacts

- `prompts/onepass_no_source_gate_diffs.md`
- `runs/life_onepass_no_source/{Ca0,Da0}/seed{n}/`
- `runs/life_onepass_no_source/summary.json` (N1–N3, with Ca, Da, Cas, B0 alongside)
- `fig_onepass_no_source.png`: J(g) for Ca, Ca0, Da, Da0, Cas (2-op)

## Constraints

Placement only: no training on outputs, no reasoning text requested or stored. Same prompts as the
parent arms except the absence of sources. New runner script; do not edit running scripts in place.
Commit this file before the gate. Amendments before numbers.