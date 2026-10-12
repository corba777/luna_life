# Task — Why does the channel enable discovery? Echo controls at high ambiguity

**Status:** locked (`f07da76a3550`, v2; supersedes `39458205b497`). Predictions are
locked with this file, before any run. API only (Luna), no GPU. Parents:
`TASK_LIFE_CRITICAL_MASS.md`, `AMENDMENT_CRITMASS_LEVELS.md`; post-hoc source:
`runs/life_critical_mass/discovery_diag.json`.

## Why

Critical mass (K2 FAIL) showed populations in which no cell held P_e at g1, yet P_e became modal
by g10 (K4 s2/s5, KH s3/s5). The post-hoc diagnostics found:

- A few cells (4–23 per run) found P_e alone after being told "wrong" 1–5 times. They mostly jumped
  straight from their first wrong rule (1.0–1.3 distinct rules held before), not after trying
  neighbours' rules. The rest received it through the channel.
- At the KH level, the inbox at the moment of discovery held mostly rules the cell had already held
  and been told were wrong (91–100%). The channel did not supply the answer.
- In the silent control KHs, with the same feedback, one cell in five runs found P_e (at g10).

The cell's memory already records that its previous rule was wrong, in both KH and KHs. So the
channel's contribution is not the refutation itself. Three candidate explanations:

- **(b) Structure:** any non-empty inbox makes the cell reconsider; an empty one lets it keep its
  rule.
- **(e) Echo:** seeing its own refuted rule again in the inbox pushes the cell to drop it.
- **(c) Crowd:** seeing many neighbours hold the same refuted rule tells the cell that the shared
  answer is wrong, and pushes it to propose a new one.

Terminology: a cell that adopts P_e while P_e is absent from its inbox is said to **propose P_e
without having received it**. This is what the logs measure. It does not mean the proposal was free
of social influence: the inbox may still shape it.

These findings are post hoc. This task first replicates them with a locked prediction, then
separates (b) from (c) with synthetic inboxes.

## Pre-step (no model): fix the feedback count

In `discovery_diag`, cells that proposed P_e at g2 have `n_told_wrong_before = 0` (K4 s2, s4, s5;
KH s4, s5), although every cell was wrong at g1. Do not just add one. First establish the
semantics from the logged prompts: which feedback line the cell saw when choosing at generation g,
and which generation's rule it refers to. Recompute the count from what the cell actually saw,
regenerate `discovery_diag.json`, and record the convention in the file. The hazard below uses it.

## Arms

All at the KH level: the same world seeds 1–5, the same KH example draws (k_H = 11/24/11/11/11, 8
distinct inputs per seed), 0 sources, Luna Responses medium, 10 generations, memory and feedback as
in critical mass.

| arm | channel | inbox content |
|---|---|---|
| **KH-r** | on | real neighbours' rules (replicate of KH) |
| **KHs-r** | off | empty (replicate of KHs) |
| **KHp** | off | **placebo**: one rule inconsistent with the cell's example, not its g1 rule, count 1 |
| **KHe** | off | **self-echo**: the cell's g1 rule, count 1 |
| **KHc** | off | **crowd echo**: the cell's g1 rule, count 8 |

- The synthetic inboxes use the same format as a real inbox (rule + number of neighbours) and one
  entry each, so KHp, KHe and KHc differ only in content and count, not in length. Report the mean
  prompt length per arm. They start at g2.
- KHp's rule is drawn once per cell (with `ECHO_SEED`, committed) from catalog rules that fail the
  cell's example and differ from its g1 rule. A checking cell can discard it, so it carries neither
  the answer nor the consensus.
- No synthetic inbox contains P_e. If a cell's g1 rule is P_e (it never was at
  KH), record it and exclude that cell from the hazard.
- The synthetic inbox is fixed. It does not follow the cell's later rules, so it cannot carry a
  discovery. KHp, KHe and KHc measure proposals, not spread.
- The echoed messages are presented as neighbours' messages to LLM cells; there are no human
  participants. State this in the readout.
- Invariant checks as in the parent, plus: in KHp/KHe/KHc, the inbox at every g ≥ 2 equals the
  specified content; in KHs-r it is empty.

## Metrics

- **Proposal hazard (primary):** over cell-generations with g ≥ 2 where the cell did not hold P_e
  at g−1 and had been told "wrong" about its previous rule (per the pre-step convention), the share
  in which it holds P_e at g with P_e absent from its inbox. Pooled per arm, and per seed, with
  numerators and denominators.
- Number of unreceived P_e first-holds per run; first generation with any P_e holder.
- KH-r only: J at g10, whether P_e is modal at g10, received vs unreceived first-holds.
- Per arm: share of cells changing rule per generation (churn); distinct rules per generation.

## Predictions (lock)

- **E1 (replication):** unreceived P_e first-holds over g2–g10 are higher in KH-r than in KHs-r
  in ≥ 4/5 seeds, and the pooled proposal hazard of KH-r is ≥ 3× that of KHs-r.
- **E2 (crowd recovers discovery):** pooled hazard of KHc ≥ 0.5 × pooled hazard of KH-r.
- **E3 (count matters):** pooled hazard of KHc > pooled hazard of KHe.
- **E5 (content matters):** pooled hazard of KHp < pooled hazard of KHc. KHp vs KHs-r is
  descriptive.
- **E4 (descriptive):** KH-r J at g10 and P_e modal at g10 per seed, against KH from critical mass.

## Readout

- E1 FAIL → the post-hoc contrast does not replicate; the critical-mass discovery claim is reported
  as unreplicated, and E2, E3 and E5 are reported descriptively only.
- E1, E2, E3, E5 PASS → **crowd**: seeing a shared refuted answer drives new proposals; the
  channel helps discovery by showing that the consensus is wrong, not by supplying the answer.
- E2 PASS, E3 FAIL (KHe ≈ KHc), E5 PASS → **echo**: seeing the refuted rule again is enough; its
  count does not matter.
- E2 PASS, E5 FAIL (KHp ≈ KHc) → **structure**: any non-empty inbox triggers reconsideration,
  whatever it contains.
- E1 PASS, E2 FAIL (all synthetic inboxes low) → no fixed inbox reproduces the effect.
  Something in live inboxes matters (variation between neighbours, changing contents); next step
  is a shuffled-live-inbox control.

## Cost

5 arms × 5 seeds, as critical mass (~$0.5 per run): about $12.5. Cap $18. Report the actual cost.

## Artifacts

- corrected `runs/life_critical_mass/discovery_diag.json` (pre-step; answer-level told_wrong;
  frac of false-rule cell-generations with `correct=true`, by arm)
- `runs/life_discovery_echo/{KH-r,KHs-r,KHp,KHe,KHc}/seed{n}/` — `rule_history.json`,
  `report.json`, **`prompts.jsonl`** (rendered prompts; ours), `decision_log.json`
  (query / rule / answer / correct), `replay_verify.json` (dry-replay vs log), and for
  synthetic arms `synthetic_inbox.json`
- `runs/life_discovery_echo/summary.json` (E1–E5; hazard per arm and seed with numerators and
  denominators; mean prompt length; frac false-rule→`correct=true` by arm)
- `fig_discovery_echo.png`: proposal hazard by arm (pooled, with per-seed points); unreceived
  first-holds by generation per arm

## Constraints

Placement only: no training on outputs, no reasoning text requested or stored. Same prompt template
for all arms; only the inbox content differs. Commit this file before the first call. Amendments
before numbers.

## Encode-path bug (KHp; same for KHe/KHc) — cause and fix

**Cause.** KHp/KHe/KHc show a synthetic inbox in the prompt (`render_channel=True`) but keep the
board silent (`live_channel=False`). The Completer therefore encodes channel-shaped JSON (with
`communication`). The board parses `no_channel`, rejects that key, and writes
`inferred_rule=None` into the rule slot. The first KHp seed hit the non-source `None` assert at
g1. This is an **encode-mode mismatch on the Completer→board handoff for the placebo/echo arms**,
not a failure to handle an invalid cell answer, and not a bad placebo draw.

**Same path.** KHe and KHc use the same `ARM_SPEC` shape and the same `EchoCompleter` adapt. Without
the fix they would have the same silent `None` drop (rule never lands in the intended slot) even
if no assert fired.

**Fix.** `_adapt_encode_to_live` re-encodes to the live (`no_channel`) shape before the board
parse; invalid answers still fall back to `unsolved` as in the parent Life runner. Startup assert:
synthetic arms are exactly `{KHp, KHe, KHc}` with `render_channel≠live_channel`.