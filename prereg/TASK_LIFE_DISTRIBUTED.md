# Task — Distributed evidence: when the collective is necessary

**Status:** locked 2026-10-13 (commit before Step 1 world audit; before any API).
Parents: `TASK_LIFE_OWN_MEMORY.md` (memory confound closed), `TASK_LIFE_REASONING_CELLS.md`,
`DESIGN_CHECKLIST.md`. Article pointer: Oct 13 update (“Where this leaves the question”).

**Queue:** Phase 1 after Ca0/Da0 close (`TASK_LIFE_ONEPASS_NO_SOURCE.md`). Phase 2 registered
only — no launch until Phase 1 readout. No GPU. Cap: alarm $25 (Phase 1).

## Why

Own-memory showed that with individual right/wrong feedback, a lone reasoning cell that keeps
its previous rule reaches J@g10 ≈ 0.89 without messages. The collective was mostly a delivery
system. That task cannot show emergence: each cell’s private example plus feedback already
identifies the rule over generations.

A collective is **necessary** only when no single agent’s information suffices. Two design
choices, locked here:

1. **No individual feedback.** Drop `correct=true/false` from the memory line. The lone agent
   has nothing to learn from except its private example and (if the channel is on) neighbour
   messages.
2. **Channel carries rules only** (as today — not examples). Collecting neighbours’ examples
   would collapse the task to “gather data and solve alone.” Crossing hypothesis sets over
   *named rules* is the collective inference.

Each cell gets one private example compatible with several catalog rules (`|S_c| ≥ 2`). The
true rule is uniquely determined only from the examples of several cells together (here: a
cell plus its Moore neighbours).

## World (Step 1 — no API)

- Grid 10×10 torus, Moore neighbourhood (Chebyshev radius 1), catalog of 101, 2-op world seeds
  **1–5** (same P_e schedule as other Life 2-op arms).
- **0 sources.** Sparse: one example per cell.
- Draw seed: `DISTRIBUTED_SEED = 20261013` (committed with this file).
- Per cell: `|S_c| = |H(E_c)| ≥ 2`, P_e ∈ H(E_c).
- **Neighbour-union uniqueness:** for every cell c,  
  `|H(E_c ∪_{n∈N(c)} E_n)| = 1` and that hypothesis is P_e.  
  (Oracle that sees all neighbour examples has a unique answer.)
- Rejection-sample full assignments until the uniqueness constraint holds; report draws per seed.
- **Chance level** (solo baseline expectation): mean over cells of `1/|S_c|`.
- Artifact: `runs/life_distributed/world_audit.json` (+ `.md` readout).

## Arms

| arm | cells | channel | feedback | memory of own rule | notes |
|---|---|---|---|---|---|
| **D-solo** | Luna Responses medium | off | none | `held_rule` kept | single-agent equal resources |
| **D-ch** | Luna Responses medium | on (rules only) | none | `held_rule` kept | primary collective |
| **D-oracle** | symbolic / Luna? | — | — | — | sees own + neighbour **examples**; ceiling |
| **D-dec** | Luna Decisions argmax P=4 | on | none | `held_rule` kept | one-pass reference |
| **D-dec-s** | Luna Decisions | off | none | `held_rule` kept | one-pass silent |

- Phase 1 = D-solo, D-ch, D-oracle (ceiling), D-dec / D-dec-s as space allows under cap.
- Phase 2 (registered only): same world with our decision models (OpenJev / Unsloth hybrid when
  available) beside Luna. Do not start Phase 2 from this lock.

**Oracle definition (locked):** for each cell, the unique rule in
`H(E_c ∪ neighbour examples)` if `|H|=1`, else abstain. Expected J ≈ 1.0 under the world
constraint. Implementation may be symbolic (no API) for the ceiling row.

## Design checklist

### Item 1 — expected prompt diffs (before gate)

**A. D-ch vs parent B (channel on, with feedback) — same seed/cell/g≥2:**

| line / block | B (parent) | D-ch |
|---|---|---|
| memory | `Previous step: answer=… correct=true\|false published … say='…'.` | `Previous step: answer=… published … say='…'.` (**no** `correct=…`) |
| constitution / inbox / catalog / examples / query | unchanged vs B | same |

**B. D-solo vs D-ch:**

| line / block | D-ch | D-solo |
|---|---|---|
| constitution | “You may publish…” | “You cannot send or receive…” |
| inbox block | present | **absent** |
| memory publish vs silence | `published … say='…'` | `silence held_rule='…'` |
| `correct=` | absent both | absent both |
| examples / catalog / query | same | same |

**C. D-dec vs D-ch:** decode path / Decisions vs Responses only (same world, same no-feedback
memory shape). List exact template diffs in the gate file when rendered.

**What else disappears with no feedback?** The word `correct=true/false` and any instruction
that says the environment told the cell whether it was right. Do **not** remove `held_rule` /
`say` — own-rule memory stays (own-memory lesson).

### Item 2 — gate

- Dry-render g1 and g2 for ≥3 cells, seeds 1, same cell ids, for D-solo vs D-ch and D-ch vs a
  feedback-on control render.
- PASS iff differing lines = item 1 lists. Commit `prompts/life_distributed_gate_diffs.md`
  before first API call.
- Check request payload / cache key text, not a logging reconstruction.

### Items 3–6

- **3:** D-solo is the single-agent equal-resources baseline (same memory, same calls, no
  neighbours). Oracle is the information ceiling, not a group.
- **4:** post-hoc splits labelled; Predictions below are registered.
- **5:** scope = 4-symbol A–H catalog-101, 2-op seeds 1–5, 10×10, no feedback, rules-only channel.
- **6:** always **J at g10** or **mean J over 10 generations**.

## Metrics

- J at g10 and mean J over 10 gens (all 100 cells; 0 sources).
- Per cell `|S_c|`; population chance = mean `1/|S_c|` (from world_audit).
- Share of cells whose g10 rule ∈ S_c (consistency with own example).
- Oracle J (ceiling).
- Cost USD; reasoning tokens if Responses.

## Predictions (lock before Phase 1 numbers)

- **P1:** D-solo mean J over gens is within **0.05** of the chance level from world_audit
  (seed-mean), or CI for (D-solo − chance) covers 0. Alone, no feedback → no climb.
- **P2 (primary):** D-ch J@g10 − D-solo J@g10 ≥ **+0.20**, CI excludes 0 (seed-level, 5 seeds).
- **P3:** D-oracle J@g10 ≥ **0.95** (world constraint holds in play).
- **P4 (descriptive):** D-dec J@g10 < D-ch J@g10 (one-pass weaker without feedback).

## Readout

- P1 PASS + P2 PASS → collective necessary under distributed evidence + no feedback.
- P1 FAIL (solo climbs) → residual signal still identifies (leak); inspect prompts.
- P2 FAIL + P3 PASS → information is there but Luna channel does not assemble it.
- P3 FAIL → world generator bug.

## Artifacts

- `runs/life_distributed/world_audit.json`, `world_audit.md`
- `prompts/life_distributed_gate_diffs.md`
- `runs/life_distributed/{arm}/seed{n}/`
- `runs/life_distributed/summary.json`

## Constraints

No eval leakage into later distill banks by content hash. Amendments before any change after
first Phase 1 number. Phase 2 not auto-started.
