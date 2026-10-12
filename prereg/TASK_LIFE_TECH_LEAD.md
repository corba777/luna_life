# Task — Tech lead: does the checker need to be able to solve the task?

**Status:** locked (`a515d7937dad`). Predictions are locked with this
file, before any run. API only (Luna), no GPU. Parents: Life arms Ca, Da, B (2-op),
`TASK_LIFE_DISTILL_CHECK.md` (the third way to place the check). Reviewer prompt:
`prompts/tech_lead_reviewer.txt` (committed with this file).

**Pre-run correction (before first call; no numbers yet).** Cell prompts have **no**
operation-definition prose (no explanations of `shift_symbols` / `swap` / `rotate_left` /
`reverse`, `;` composition, indices, or wrap-around). Cells see bare rule names only (Responses
catalog / Decisions criteria) — names without definitions, and the Responses header is a chooser
instruction (`choose by key`). **v3:** drop the Rule catalog block from the reviewer; `{OPS_SPEC}`
is one line cells do have — `The rules transform 4-symbol strings over the alphabet A–H.` — nothing
more (no `;` order or index conventions). Proposed-rule labels are **P1..Pn** (not R1..Rn) to avoid
a clash with catalog keys. Cell-identity framing (`You are one cell among 100…`) is dropped. T1 is
read against this information. Dry example: `prompts/tech_lead_reviewer_example.txt`. Reviewer
accuracy splits false accept/reject by whether the rule’s two ops **commute** (order-sensitive vs
not).

## Why

One-pass Decisions cells on two-op rules:
- without a channel (Cas): J at g10 ≈ 0;
- with a channel, no check (Ca): crowding onto false rules, J at g10 ≈ 0.14;
- with a deterministic check of incoming rules against the cell's own example (Da): J ≈ 0.67
  (0.92 with one source).

The deterministic check is not an oracle. It does not know P_e; it only rejects incoming rules that
contradict the cell's example. Reasoning cells have two very different abilities here:
- **solve** a two-op rule alone from one example: ≈ 0.25 (Bs);
- **check** an incoming rule against their example: 0.98 (stage 1).

**Question:** can a reasoning model that solves the task only a quarter of the time replace the
deterministic check (a tech lead as reviewer)? And can a minority of reasoning cells embedded among
one-pass cells do the same job (tech leads in the team)?

## Arms

World seeds 2-op 1–5, 4 sources, 10 generations, memory and feedback as in Ca/Da. Same prompts as
Ca/Da/B for the cell decisions.

| arm | cells | check of incoming rules |
|---|---|---|
| **Ca-r** | one-pass (Decisions) | none (replicate of Ca) |
| **Da-r** | one-pass | deterministic engine (replicate of Da) |
| **Dr** | one-pass | **reasoning reviewer** (Luna Responses, medium) |
| **Mx10 / Mx25 / Mx50** | 10% / 25% / 50% reasoning cells (as B), the rest one-pass | none for one-pass cells; reasoning cells check by their own reasoning |

References from earlier runs (not rerun): B (100% reasoning cells), Cas, Bs.

**Dr reviewer.**
- Input: the cell's own example and the distinct rules in its inbox. **No neighbour counts**: the
  engine in Da ignores them, so the reviewer does too. Not P_e, not feedback, not other cells'
  examples.
- Output: for each incoming rule, accept or reject. Only accepted rules reach the one-pass cell,
  with their neighbour counts, exactly where the engine filter sits in Da.
- Fixed reviewer prompt, committed with this file (`prompts/tech_lead_reviewer.txt`) before the
  first call. Placeholders:
  - `{OPS_SPEC}`: `The rules transform 4-symbol strings over the alphabet A–H.` (v3; see pre-run);
  - `{EXAMPLE_INPUT}`, `{EXAMPLE_OUTPUT}`: rendered exactly as in the cell prompt;
  - `{RULE_LIST}`: one line per distinct inbox rule, `P1: <rule>`, ordered by catalog index.
- Unparseable or incomplete answer → one retry. If it still fails, **no filtering** for that cell
  and generation (the whole inbox passes, as in Ca), and the event is counted. This fallback can
  only hurt Dr, so it cannot flatter T2.
- Dr check accuracy is computed only over parsed decisions; fallbacks are reported separately.
- One reviewer call per cell per generation (from g2).
- No reasoning text requested or stored; only the accept/reject list.

**Mx placement.**
- Reasoning cells are placed at random non-source positions, drawn per world seed with `LEAD_SEED`
  (committed).
- The same positions are used across Mx levels where possible: Mx10 ⊂ Mx25 ⊂ Mx50.
- Report the positions and how many reasoning neighbours each one-pass cell has.

## Metrics

- J at g10 and J averaged over 10 generations; false locks at g10; modal rule at g10.
- For Mx: J separately among one-pass cells and among reasoning cells.
- **Dr check accuracy.** Per incoming rule, the reviewer's decision against the engine's
  consistency verdict:
  - false accept (inconsistent rule accepted);
  - false reject (consistent rule rejected);
  - by rule ops and by neighbour count;
  - false accept / false reject split by whether the rule’s two ops **commute**
    (order-insensitive vs order-sensitive; 1-op separate).
- **Cost:** reasoning calls and tokens per run, as a share of B's. Plot J at g10 against this share
  for Ca-r, Mx10/25/50, Dr, Da-r, B.

## Predictions (lock)

- **T1 (reviewer accuracy):** Dr pooled per-rule accuracy against the engine ≥ 0.95.
- **T2 (reviewer ≈ engine):** seed-mean J at g10, Dr ≥ Da-r − 0.10.
- **T3 (more leads help):** seed-mean J at g10 among one-pass cells increases
  Mx10 < Mx25 < Mx50.
- **T4 (embedded leads help juniors less than a reviewer):** J at g10 among one-pass cells, Mx50 <
  Dr in ≥ 4/5 seeds.
- **T5 (descriptive):** J at g10 against the reasoning-cost share; whether any Mx level reaches Da-r.

## Readout

- T1 + T2 PASS → the checker does not need to solve the task. A model that finds the rule alone a
  quarter of the time works as a near-perfect reviewer, because checking consistency is much easier
  than finding the rule.
- T1 PASS, T2 FAIL → reviewer errors are rare but compound over the grid. Report where the false
  accepts happen (which rules, which generations) and whether they seed false locks.
- T1 FAIL → the reviewer framing changes the model's behaviour relative to its own stage 1; compare
  false accepts with B's stage-1 failures.
- T3 PASS, T4 PASS → placing the check at every junior beats mixing seniors into the team.
- T4 FAIL → embedded leads lift the juniors as much as a reviewer does, at a lower reasoning cost;
  report the cost curve.
- T3 FAIL → juniors swamp the leads; report the leads' own J against B's.

## Cost

Six arms × 5 seeds.
- Dr ≈ B-level reasoning cost per run plus Decisions.
- Mx scale with the lead share.
- Ca-r and Da-r are cheap.

Estimate ≈ $10–12; cap $20. Report the actual cost.

## Artifacts

- `prompts/tech_lead_reviewer.txt`, `LEAD_SEED` (committed before the first call)
- `runs/life_tech_lead/{Ca-r,Da-r,Dr,Mx10,Mx25,Mx50}/seed{n}/`
- `runs/life_tech_lead/reviewer_accuracy.json`
- `runs/life_tech_lead/summary.json` (T1–T5)
- `fig_tech_lead.png`:
  - (a) J(g) per arm;
  - (b) J at g10 against the reasoning-cost share, one point per run, B/Ca-r/Da-r as anchors.

## Constraints

Placement only: no training on outputs, no reasoning text requested or stored. The same cell
prompts as Ca/Da/B; only the reviewer prompt is new, and it is committed before the first call.
Amendments before numbers.