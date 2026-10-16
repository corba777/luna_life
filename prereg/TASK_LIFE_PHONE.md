# Task — A phone to everyone: is reach the problem, or checking?

**Status:** **cleared to run** 2026-10-15 (Self-Check Part B read; **no Alls arm**). Predictions
locked with this file before any number. API only (Luna Decisions). Follows `DESIGN_CHECKLIST.md`
and the standing rules in `PLAN_NEXT.md`. Gate dry-renders before the first live call.
Parents: `TASK_LIFE_TECH_LEAD.md` (Ca-r, Da-r), `TASK_LIFE_SELF_CHECK.md` (Part A-src / Part B).

## Why

One-pass populations on 2-op worlds with four sources: without a check 0.24 (Ca-r), with the engine
check 0.92 (Da-r). Alone, without a channel, one-pass cells never find the 2-op rule (0.00), so every
cell that ends up with P_e got it, directly or through others, from the four sources. With the
sources at [0, 5, 50, 55], only 32 of 96 cells are their direct neighbours.

On the grid, the channel changes two things at once:
1. **geometry:** information moves ring by ring, so far cells hear it late;
2. **bandwidth:** a cell hears 8 others per round.

"A phone to everyone" removes the geometry and raises the bandwidth. This task separates the two,
with and without a check, to ask whether one-pass populations fail because the truth cannot reach
them, or because nothing filters what does.

## Arms

All arms: Luna Decisions (argmax, P = 4), 2-op world seeds 1–5, four sources (`SOURCE_IDS`
[0, 5, 50, 55], holding P_e and publishing every round), 10 generations, memory and feedback, cell
prompt, catalog, schema and parser exactly as Ca-r / Da-r. Only the set of cells a cell hears from
changes.

| arm | a cell hears from | check of incoming rules |
|---|---|---|
| Ca-r (reference, not rerun) | its 8 Moore neighbours | none |
| Da-r (reference, not rerun) | its 8 Moore neighbours | engine |
| **R8** | 8 cells drawn at random each round | none |
| **R8c** | 8 cells drawn at random each round | engine |
| **All** | all 99 other cells | none |
| **Allc** | all 99 other cells | engine |

- **R8 draws:** for each (world seed, generation, cell), 8 distinct cells other than itself, uniform
  over the 99 (sources included), drawn with a committed `PHONE_SEED` via sha256 of
  (PHONE_SEED, world, generation, cell). Directed: a cell hears its 8; they need not hear it.
  Fresh draw every generation.
- **All:** every other cell that published this round.
- **Inbox format unchanged:** each distinct received rule with the number of cells that sent it,
  as in Ca. Only the set of senders differs. The cell-prompt template is byte-identical to Ca-r /
  Da-r; under R8 and All the word "neighbours" in the prompt refers to the cells heard that round.
- **Engine check (R8c, Allc):** as in Da-r. Before the cell sees its inbox, any rule that
  contradicts the cell's own example is removed; accepted rules keep their sender counts.

Not in this task: removing memory and feedback (one factor at a time; a later amendment if
needed), cells choosing whom to call (needs information about who knows what — a separate
question).

**Possible extra arm (amendment only):** if `TASK_LIFE_SELF_CHECK.md` Part B passes its go
criterion, an **Alls** arm (all 99, each cell checks with its own one-pass yes/no call) may be added
by amendment before any number of this task is read.

## Gate

- Cell-choice payload: template byte-identical to Ca-r (no check) / Da-r (check) for the same seed,
  cell and forced history; only the inbox block differs. Dry render for 3 cells per arm at g2,
  listing the inbox blocks.
- Assertions at startup and per generation: R8 draws are 8 distinct cells, never self, reproducible
  across two processes (same sha256 seeds); All inboxes count exactly the publishing others; source
  positions and P_e unchanged.
- Runtime masked check at g2 of seed 1 before any g3 request; fresh empty per-arm caches; per-
  generation live / cached / fallback log; fail if g ≥ 2 has 0 live requests; uniform fallback ≤ 2%.
- Commit hash recorded per arm × seed; no resume across code versions.

## Metrics

- J(g) and J@g10 per seed and seed mean (non-source cells, as Ca-r / Da-r).
- Generation at which J first reaches 0.50 and 0.80 (or "never"), per seed.
- False lock at g10: a non-P_e rule held by ≥ 50% of non-source cells. Modal rule at g10.
- Number of distinct rules held at g10 (diversity), per seed.
- Inbox size: mean distinct rules received per cell per generation; prompt tokens per call.
- Cost per arm.

**Descriptive (added before the summary was read; no change to P1–P4).** Offline from
`rule_history.json`, non-source cells, g≥2; Ca-r / Da-r from tech-lead logs alongside:

- **Switch to inbox modal:** P(chosen = unique inbox modal | own rule ≠ modal), binned by the
  modal rule's share of received messages (0–25 / 25–50 / 50–75 / 75–100%), per arm.
- **Retention r:** P(keep own rule) per arm and generation.

Artifact: `runs/life_phone/switch_retention_descriptive.{json,md}`
(`runs/diag_life_phone_switch_retention.py`).

## Predictions (lock)

- **P1 (reach without a filter does not help):** All seed-mean J@g10 ≤ Ca-r J@g10 (0.24), and All
  ends in a false lock in ≥ 3 of 5 seeds.
- **P2 (reach with a filter is fast):** Allc seed-mean J@g10 ≥ 0.95, and Allc reaches J ≥ 0.80 by
  g3 in ≥ 4 of 5 seeds.
- **P3:** Allc reaches J ≥ 0.80 earlier than Da-r in ≥ 4 of 5 seeds (Da-r "never" counts as later).
- **P4 (descriptive):** R8 vs Ca-r and R8c vs Da-r — does removing geometry at fixed bandwidth help,
  hurt, or do nothing.

## Readout

- **P1 PASS, P2 PASS:** reach is not what one-pass populations lack. Direct contact with everyone
  spreads the majority, which is wrong; with a check at every cell it spreads the truth within a
  few rounds. The value lies in reach combined with a filter.
- **P1 FAIL:** global reach alone lifts one-pass populations; report J by generation and whether
  sources' messages dominate the inbox.
- **P2 FAIL:** even with a check and full reach the population does not converge quickly; report
  inbox diversity and how many rules survive the check per cell.

## Cost

Ca-r ≈ $1.09 and Da-r ≈ $1.19 per seed. R8 / R8c ≈ the same. All / Allc have longer inboxes (more
distinct rules); estimate ≈ $1.5–2 per seed. Total ≈ $25; alarm $40. Report actual cost and prompt
tokens.

## Artifacts

- `prompts/phone_gate.md` (dry renders, inbox blocks), `PHONE_SEED` (committed before the first call)
- `runs/life_phone/{R8,R8c,All,Allc}/seed{n}/`
- `runs/life_phone/summary.json` (P1–P4 with Ca-r, Da-r alongside)
- `runs/life_phone/switch_retention_descriptive.{json,md}` (descriptive; before summary read)
- `fig_phone.png`: J(g) for Ca-r, R8, All (left) and Da-r, R8c, Allc (right), seed means with
  per-seed lines

## Constraints

Closed model outputs are not used as training data. No reasoning text requested or stored. New
runner script; do not edit running scripts. Commit this file before the gate; amendments before
numbers.