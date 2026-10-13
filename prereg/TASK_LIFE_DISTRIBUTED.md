# Task — Life with distributed evidence: a task no single agent can solve

**Status:** locked. Predictions locked with this file, before any run. Follows
`DESIGN_CHECKLIST.md` (all items answered below) and `CONTEXT_MODELS.md`.
Phase 1: API only (Luna). Phase 2: local models, registered here, run when the GPU is free.

## Why

`TASK_LIFE_OWN_MEMORY.md` showed that in the current Life task a single reasoning agent with
memory of its own previous rule solves two-step rules alone (J@g10 0.89 vs 0.99 with messages).
Each cell's own example, plus "right/wrong" feedback over ten generations, identifies the rule. That
task cannot show a collective effect beyond spreading.

Here the evidence is split so that it **cannot** be identified alone:
- no individual correctness feedback;
- each cell's examples fit several catalog rules;
- only the examples of a neighbourhood together leave the true rule.

Question: does a population of agents that exchange rules (not examples) find a rule that none of
them can identify alone, and which agents can do it?

## World

- Same rule family and catalog as Life v1b (4-symbol strings over A–H, 101 rules, depth 1–2).
  True rule P_e is two-op in every seed.
- **Example assignment** (seeded, `DIST_WORLD_SEED = 20261013`, committed with this file). Each
  cell c gets k examples (k from the world audit, default 1) with consistent set S_c ⊆ catalog
  such that:
  1. P_e ∈ S_c for every cell;
  2. |S_c| ≥ 3 for every cell (no cell can identify the rule alone);
  3. for every cell, the intersection of S over its Moore neighbourhood (cell + 8 neighbours)
     is exactly {P_e};
  4. in at least 40% of cells, S_c contains a one-op rule. A simpler wrong rule is available, so a
     simplicity prior does not lead to P_e.
- **No sources.** Nobody is seeded with P_e.

### World generator

Naive iid draws from the `|S_c| ≥ 3` pool fail when the first operation of P_e sits in almost
every cofitting set (classic seed 1: `shift_symbols(1);swap(2,3)`): forcing the ≥40% one-op
quota then leaves that first-op in every neighbourhood intersection.

**Procedure** (`life_verify/distributed.py`, `DIST_WORLD_SEED`):
1. Build the pool of inputs with `|S| ≥ 3` and P_e ∈ S.
2. **Witness** inputs: those whose S excludes the first operation of P_e. Place witness examples
   on a **stride-3 lattice** of cells (`(r,c)` with `r,c ∈ {0,1,3,4,6,7,9}` on the two
   phase-offset grids — 25 cells) so every Moore neighbourhood contains at least one witness.
3. Fill remaining cells by random draw from the pool (biased toward one-op-bearing examples for
   condition 4).
4. Accept only if all four world conditions hold. Else redraw the fill (same witness lattice).
5. If a scheduled world seed cannot accept within the draw cap, advance the world-seed index and
   record every try in `draw_log`.

Assignment draws for accepted seeds 1–5: **1, 1, 1, 28, 1** (mean 6.4). Seed 4 needed 28 because
its first op is `reverse` and the witness pool is the entire `|S|≥3` set — the 1-op quota is the
binding constraint.

### World audit (committed, no API)

Artifact: `runs/life_distributed/world_audit.json`. Identifying radius = 1 (by construction).
Mean chance E[1/|S_c|] = **0.251**, so the D1 band is DRs J@g10 ≤ **0.40** (chance + 0.15).
The Phase 1 readout reports **D3 per seed** in a column beside these rows.

| seed | P_e | chance E[1/\|S_c\|] | share 1-op in S_c | witnesses / nbhd (min / mean) | n_draws |
|---:|---|---:|---:|---|---:|
| 1 | `shift_symbols(1);swap(2,3)` | 0.251 | 0.75 | 2 / 2.25 | 1 |
| 2 | `rotate_left(1);swap(0,3)` | 0.197 | 0.97 | 2 / 2.25 | 1 |
| 3 | `shift_symbols(6);swap(1,3)` | 0.250 | 0.76 | 2 / 2.25 | 1 |
| 4 | `reverse;shift_symbols(6)` | 0.295 | 0.42 | 9 / 9.00 | 28 |
| 5 | `shift_symbols(1);swap(0,3)` | 0.264 | 0.75 | 2 / 2.25 | 1 |

## Constitution (distributed)

v1b already states that one hidden transformation is shared and that private examples differ
(`constitutional_life.cell.prompt._WORLD`). Distributed keeps that sentence, drops any implication
of correctness feedback, and names rule-memory instead of answer-memory. **Final wording
(channel on, Responses / JSON rendering):**

```
You are one cell among 100 on a wrapping 10×10 grid.

Each cell has its own private task for this epoch: a hidden transformation of 4-symbol strings over A–H. Every cell in the epoch has the same hidden transformation, but different private examples and a different query each generation. There is no shared score.

You see your private examples, your current query, a one-step memory of the rule you held last generation (and whether you published it), and eight message slots from other cells. Unused slots are empty. You are not told whether your last rule was correct.

You may publish at most one message this generation, or stay silent. A message has an integer signal 0–7 and a short text (at most 96 UTF-8 bytes). Published messages become visible only from the next generation, and only to cells allowed to see them. Your task_answer and inferred_rule are not shown to other cells. Messages may name a transformation; they never carry private examples.

inferred_rule is required. Write the hidden transformation as you currently understand it.

Output a single JSON object and nothing else.
```

**Silent (DRs / DCs):** replace the “You see …” / publish paragraphs with the no-channel pair
(no inbox; “You cannot send or receive messages”), same world sentence and no-feedback memory.

**Typed (DC / DCs):** same world + see/publish text (publish paragraph unified with DR — see
`AMENDMENT_DISTRIBUTED_DR_DC_DIFF.md`); tail is the typed choose-from-options line
(no JSON output shape), still with no correctness feedback.

### Expected constitution diffs vs v1b (gate list)

| piece | v1b | distributed |
|---|---|---|
| shared transformation + different examples | present in `_WORLD` | **kept** (required) |
| “A correct answer is the hidden transformation applied to your query.” | present | **removed** (no individual grading) |
| memory in “You see …” | “one-step memory of your last answer” | “one-step memory of the rule you held last generation (and whether you published it)” |
| feedback | implied by memory `correct=` | explicit: “You are not told whether your last rule was correct.” |
| messages | may name a transformation | same + “they never carry private examples.” |

Arm-to-arm diffs (DR vs DRs, etc.) remain as in the Gate section below.

## Memory line (clean schema)

Every arm uses the same memory line, which separates the cell's state from its action:

```
Previous step: rule='<rule held at g−1>' published=<yes|no>.
```

- No `answer=`, no `correct=`: there is no individual feedback.
- At g1: `Previous step: none.`

## Channel

Same topology as Life v1b: a cell may publish one message (integer signal 0–7 + short text) or
stay silent; delivered messages reach the 8 Moore neighbours from the next generation.

**Rules-only enforcement (engine, not prompt-only).** A published text is delivered only if it
**parses** to a catalog rule after normalize (strip / lower-case / trailing `.` / whitespace
inside ops) → `parse_program` → `catalog.canonicalize`; the neighbour then sees the
**canonical** `description()`. Otherwise the slot is delivered **empty** (as if the sender
stayed silent for that text). Signal alone never carries a rule. Dropped (non-catalog)
publishes are counted per **arm × seed × generation** and reported in the readout
(`AMENDMENT_DISTRIBUTED_DR_DC_DIFF.md`). Constitution wording above is unchanged — the
engine is the hard constraint.

## Arms

### Phase 1 (API, `gpt-6-luna`)

| arm | cells | channel | role |
|---|---|---|---|
| **DR** | reasoning (Responses, medium) | on | main: population with messages |
| **DRs** | reasoning | off | single-agent baseline, equal memory and calls (checklist item 3) |
| **DRo** | reasoning, one call per neighbourhood | — | oracle: one agent sees all 9 examples of a neighbourhood; upper bound that the information suffices |
| **DC** | one-pass (Decisions, argmax, P=4) | on | one-pass population |
| **DCs** | one-pass | off | one-pass single-agent baseline |

- 5 world seeds, 10 generations, 10×10 torus, same decoding and P as the parent arms.
- Channel: see **Channel** above (rules-only engine filter; drop log per arm×seed).
- DRo: 20 neighbourhoods per seed (fixed sample, seeded), one reasoning call each, asked for the
  single rule consistent with all 9 examples.

### Phase 2 (local GPU, after `gpu_chain.ok`, Phase 0 (300) and the Unsloth hybrid)

Same world, prompts and arms with cells from `CONTEXT_MODELS.md`: Qwen3-4B-Instruct-2507 cot,
SPADE-4B cot, and, if the hybrid task produces them, the V1 and V2 decision models. Predictions for
Phase 2 are written as an amendment before its first run, using Phase 1 as the reference.

## Gate (before the first API call)

1. **World audit** committed (table above; `runs/life_distributed/world_audit.json`).
2. **Expected prompt diffs** (checklist item 1), g2, 3 cells, same seed and cell:
   - Distributed constitution vs v1b: exactly the rows in “Expected constitution diffs vs v1b”.
   - DR vs DRs: constitution channel lines (listed verbatim in the gate file); inbox block present
     vs absent; memory line `published=yes|no` value only. **Nothing else.**
   - DC vs DCs: same set of differences.
   - DR vs DC: pre-catalog state text identical; only the allowed diffs in
     `AMENDMENT_DISTRIBUTED_DR_DC_DIFF.md` (JSON/typed output-format instruction and option
     rendering — catalog in text vs Decisions choices). Publish paragraph unified.
   - All arms vs the world: the cell's examples render identically across arms.
3. Gate checks the request text actually sent (request hash in cache), not a logging
   reconstruction. Any unlisted difference fails. Commit `prompts/life_distributed_gate_diffs.md`.
4. Startup asserts: no sources; no `correct=` anywhere in any prompt; memory line matches the
   cell's rule at g−1 from the live run; channel off ⇒ no deliveries and memory always
   `published=no` (DRs/DCs cannot publish); constitution contains the
   shared-transformation / different-examples sentence; **no delivered message text outside the
   catalog** (every non-empty inbox `say` is a canonical catalog description after the
   canonicalize filter).

## Metrics

- J at g10 and mean J over 10 generations (all 100 cells); always name which.
- Correct / false locks (modal share ≥ 0.5); modal rule at g10.
- Chance level per seed: E[1/|S_c|], and the share of cells whose held rule is in S_c (validity of
  individual inference).
- **Intersection use (DR, DC):** at each switch, whether the new rule is (a) in the cell's own S_c,
  (b) received from at least one neighbour, (c) the most frequent rule in the inbox. Report the
  shares of switches to P_e explained by (a∧b) vs (c) alone.
- DRo accuracy (share of neighbourhoods answered with P_e).
- Validity: invalid / fallback counts; reasoning tokens per cell-generation; total USD per seed.
- **Dropped publishes (DR, DC):** share and count of published texts that failed the
  canonicalize filter and were delivered empty, per **arm × seed × generation** (and totals).

## Predictions (lock)

- **D1 (design validity):** DRs J@g10 ≤ chance + 0.15 (seed mean). With audited chance **0.251**,
  that threshold is **≤ 0.40**. If D1 fails, the world is solvable alone and D3–D4 are not
  interpreted. This is recorded as a design failure, not a finding.
- **D2 (information suffices):** DRo accuracy ≥ 0.80.
- **D3 (main, reasoning):** DR J@g10 ≥ DRs J@g10 + 0.30 in ≥ 4/5 seeds. Report per-seed Δ next to
  the world-audit row for that seed.
- **D4 (one-pass):** DC J@g10 − DCs J@g10 < 0.15 (seed mean). One-pass agents do not intersect
  hypotheses.
- **D5 (descriptive):** among DR switches to P_e, the share explained by (a∧b) (own consistency
  plus a received rule) vs majority copying (c) alone.

## Readout

- **D1, D2, D3 PASS:** a population of reasoning agents finds a rule no member can identify alone.
  This is the first collective effect in Life beyond spreading. D5 says whether it works by
  intersection or by copying the majority. Table: per-seed D3 Δ beside chance / share_1op /
  witnesses-per-nbhd from the audit; include dropped-publish counts per arm×seed.
- **D1, D2 PASS, D3 FAIL:** the information is there (oracle), but exchanging rules does not
  assemble it. Report where it stalls (D5, locks).
- **D2 FAIL:** the task is too hard even with pooled examples; redesign before interpreting.
- **D4:** if one-pass populations do gain, report it; it would contradict the one-pass results so
  far.

## Cost

Reporting rule (`DESIGN_CHECKLIST.md` item 7; `AMENDMENT_DIST_COST_COMPUTE.md`): every readout
gives (a) API USD at list price and (b) compute — prefill and decode tokens per cell-generation,
separately; for local runs also measured GPU-seconds per cell-generation.

Phase 1 (API): DR and DRs ≈ $0.45 per seed each (10 seeds total); DC and DCs ≈ $1.0 per seed
each at P=4 (10 seeds); DRo ≈ 100 calls. Estimate ≈ $16–20; alarm $25 (alarm, not a stop).
Report actual list-price USD per arm and prefill/decode tokens per cell-generation.

Phase 2 (local): same (b) with GPU-seconds per cell-generation; USD only if an API surface is
used. Predictions for Phase 2 remain in a separate amendment before its first run.

## Artifacts

- `runs/life_distributed/world_audit.json`, `prompts/life_distributed_gate_diffs.md`
- `runs/life_distributed/{DR,DRs,DRo,DC,DCs}/seed{n}/`
- `runs/life_distributed/summary.json` (D1–D5), `intersection_diag.md`
- `fig_distributed.png`: J(g) for all population arms, with chance level and DRo accuracy as
  horizontal lines.

## Constraints

Placement only for closed models: no training on outputs, no reasoning text requested or stored.
Same prompts for all models. New runner script; running scripts are never edited in place. Commit
this file before the gate. Amendments before numbers.