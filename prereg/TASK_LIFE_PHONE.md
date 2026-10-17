# Task — A phone to everyone: is reach the problem, or checking?

**Status:** **closed** 2026-10-17. Predictions were locked with this file before any number.
API only (Luna Decisions). Follows `DESIGN_CHECKLIST.md` and the standing rules in `PLAN_NEXT.md`.
No Alls arm.
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

**Descriptive (added before the summary was read; no change to P1–P4).** Non-source
cells, g≥2; Ca-r / Da-r from tech-lead logs alongside:

- **Switch to inbox modal:** P(chosen = unique inbox modal | own rule ≠ modal), binned by the
  modal rule's share of received messages (0–25 / 25–50 / 50–75 / 75–100%), per arm.
- **Retention r:** P(keep own rule) per arm and generation. Retention does not use the inbox.

Phone arms were recomputed after `rule_history.inbox_says` was found to be the Moore
delivery, not the inbox the cell was shown. Those rates use the phone inbox rebuilt from
the decision cache. Ca-r / Da-r are unchanged: their log is the Moore inbox they saw.
The earlier table (R8, two seeds, Moore inbox) is
`runs/life_phone/archive_switch_retention_moore_inbox/`.

Artifact: `runs/life_phone/switch_retention_descriptive.{json,md}`
(`runs/diag_life_phone_switch_retention.py`).

**Replicate noise (readout, after the summary; no prediction uses it).** R8 J@g10 per
world, fresh run versus the archived partial R8 run, for worlds 1–4 where both complete
reports exist, with the absolute differences. Label: run-to-run variation of the Decisions
API under identical payloads.

Artifact: `runs/life_phone/replicate_noise_descriptive.{json,md}`
(`runs/diag_life_phone_replicate_noise.py`).

**P_e versus false modal (readout, after All J@g10 was seen; no prediction uses it).**
All and R8, per world, non-source cells, g≥2. The phone inbox is rebuilt from the
decision cache (`rule_history.inbox_says` is the Moore delivery). Bins are the rule's
share of inbox messages, 0–25 / 25–50 / 50–75 / 75–100%:

- P(switch to P_e | P_e is in the inbox and the cell did not hold it).
- P(switch to the unique inbox modal | that modal is a false rule and the cell did not hold it). Ties excluded.
- P(keep P_e | held P_e at g−1).

Artifact: `runs/life_phone/pe_vs_false_modal_descriptive.{json,md}`
(`runs/diag_life_phone_pe_vs_false.py`).

## Predictions (lock)

- **P1 (reach without a filter does not help):** All seed-mean J@g10 ≤ Ca-r J@g10 (0.24), and All
  ends in a false lock in ≥ 3 of 5 seeds.
- **P2 (reach with a filter is fast):** Allc seed-mean J@g10 ≥ 0.95, and Allc reaches J ≥ 0.80 by
  g3 in ≥ 4 of 5 seeds.
- **P3:** Allc reaches J ≥ 0.80 earlier than Da-r in ≥ 4 of 5 seeds (Da-r "never" counts as later).
- **P4 (descriptive):** R8 vs Ca-r and R8c vs Da-r — does removing geometry at fixed bandwidth help,
  hurt, or do nothing.

## Readout

Pre-registered branches, kept as written:

- **P1 PASS, P2 PASS:** reach is not what one-pass populations lack. Direct contact with everyone
  spreads the majority, which is wrong; with a check at every cell it spreads the truth within a
  few rounds. The value lies in reach combined with a filter.
- **P1 FAIL:** global reach alone lifts one-pass populations; report J by generation and whether
  sources' messages dominate the inbox.
- **Beside P1 (verdicts unchanged):** Ca-r is a single run. Same-payload reruns differ by up to
  0.26 per world (`runs/life_phone/replicate_noise_descriptive.md`).
- **P2 FAIL:** even with a check and full reach the population does not converge quickly; report
  inbox diversity and how many rules survive the check per cell.

**Result (2026-10-17).** Full write-up: `runs/life_phone/readout.md`. Figure: `runs/life_phone/fig_phone.png`.

- **P1 FAIL.** All seed-mean J@g10 is 0.621, above Ca-r 0.240. False locks are 2 of 5, not ≥ 3.
  Worlds 1–2 lock on a false rule; worlds 3–5 end on P_e. An All inbox is about 85–91 messages, so
  the four sources are not a majority of it.
- **P2 FAIL on the speed clause; the level clause is met.** Allc seed-mean J@g10 is 1.000 (≥ 0.95).
  J reaches 0.80 by g3 in 2 of 5 worlds, not 4. By g10 every Allc world holds one rule, P_e.
- **P3 PASS.** Allc reaches 0.80 earlier than Da-r in 4 of 5 worlds. World 2 ties at g4. Da-r world 1
  never reaches 0.80.
- **P4 (descriptive).** R8 0.481 versus Ca-r 0.240. R8c 0.992 versus Da-r 0.923. Dropping geometry
  at fixed bandwidth raises the unchecked mean by about the size of the 0.26 same-payload world
  move, and leaves both checked arms near 1.
- **Caveat (filter form).** P3 and the P4 comparison of R8c against Da-r change the topology and
  the filter form together, so they cannot be read as topology alone. The verdicts stay as computed.
  Da-r showed an inconsistent rule with a mark. R8c and Allc removed it before the prompt.
- **Mechanism.** The first rule to a majority wins. Without the filter, which rule gets there
  first differs by world. The one-pass prior mass of P_e (probe A) does not order the worlds the
  same way as the low-share switch onto P_e (prior: 5, 1, 3, 4, 2; switch: 3, 4, 5, 1, 2); only
  world 2 is last on both. So the prior of P_e alone does not explain which worlds succeed. A
  post-hoc candidate, not tested here: P_e's prior relative to the main false competitor's. With
  the filter, a false rule is removed before the cell sees it, and the population reaches P_e; the
  speed still varies by world.

**Prior versus low-share switch (descriptive, n = 5; no prediction uses it).** Probe A prior mass
of P_e next to All's P(switch to P_e | share in [0, 25%)). Rank, highest first: prior 5, 1, 3, 4, 2;
switch 3, 4, 5, 1, 2. World 2 is last on both. The other four are not the same order.
`runs/life_phone/prior_vs_switch_descriptive.md`.

## Cost

Ca-r ≈ $1.09 and Da-r ≈ $1.19 per seed. R8 / R8c ≈ the same. All / Allc have longer inboxes (more
distinct rules); estimate ≈ $1.5–2 per seed. Total ≈ $25; alarm $40.

**Actual Phone cost (list rate).** R8 4.56, R8c 5.39, All 12.35, Allc 12.34. Total **$34.64**.
Prompt tokens across those four arms: 3.46×10^8.

## Artifacts

- `prompts/phone_gate.md` (dry renders, inbox blocks), `PHONE_SEED` (committed before the first call)
- `runs/life_phone/{R8,R8c,All,Allc}/seed{n}/`
- `runs/life_phone/readout.md` (P1–P4, mechanism, descriptive tables)
- `runs/life_phone/summary.json` (runner close, when the process finishes)
- `runs/life_phone/prior_vs_switch_descriptive.{json,md}` (descriptive; n = 5 worlds)
- `runs/life_phone/switch_retention_descriptive.{json,md}` (descriptive; phone inbox from the decision cache; Ca-r / Da-r unchanged)
- `runs/life_phone/archive_switch_retention_moore_inbox/` (earlier table; Moore inbox; wrong for phone arms)
- `runs/life_phone/replicate_noise_descriptive.{json,md}` (descriptive; after summary; no prediction uses it)
- `fig_phone.png`: J(g) for Ca-r, R8, All (left) and Da-r, R8c, Allc (right), seed means with
  per-seed lines

## Constraints

Closed model outputs are not used as training data. No reasoning text requested or stored. New
runner script; do not edit running scripts. Commit this file before the gate; amendments before
numbers.