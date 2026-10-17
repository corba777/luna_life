# Task — The distributed world without forced publishers

**Status:** locked 2026-10-17, before any DRc run. Predictions are locked with this file, before any run. API: Luna
Responses (reasoning), same endpoint and settings as the original DR. Follows `DESIGN_CHECKLIST.md`
and the standing rules in `PLAN_NEXT.md`. Parents: the distributed-world task (DR, DR-noex),
CHAIN_HYGIENE §24, `runs/life_distributed/forced_publishers_j96.md`,
`runs/life_distributed/stats_for_correction.md`.

## Why

The distributed world was designed with no sources. Each cell holds one example that does not
identify the rule, and the rule is fixed only by the intersection of all examples. Because of a
runner fault (§24), cells 0, 5, 50 and 55 were forced to publish P_e in every generation. The
environment as run therefore modelled nothing that was intended.

Existing logs suggest the four cells mattered little:
- 3–14 non-forced cells per world already hold P_e at g1, before any message;
- adoptions where only forced cells sent P_e are 8–22% of DR adoptions.

That is indirect evidence. This task reruns the world as designed and measures run-to-run noise
for a reasoning arm, which the project does not have yet. Every threshold below is derived from
that noise.

## Arms

| arm | as | runs |
|---|---|---|
| **DRc** | DR, with all 100 cells calling the model | 2 independent replicates |
| **DRc-noex** | DR-noex, with all 100 cells calling the model | 2 independent replicates |

Everything else is byte-identical to DR / DR-noex: worlds 1–5, examples, catalog, prompt, schema,
parser, channel, 10 generations. The only change is that cells 0, 5, 50 and 55 are model cells.
Their examples are the ones already assigned to them by `draw_world`.

## Gate

- **Runner:** new script, committed before launch. The generation loop sits **inside**
  `source_ids_override(())`, as in `run_life_long_chain.py`.
- **Runtime assertions, every generation:** `source_mask` is all false; the live plus cached model
  decisions for that generation are exactly 100; no cell's rule is written by
  `source_raw_decision`. Any failure aborts the run.
- **Payload check:** for 3 non-forced cells at g1 of world 1, the request bytes equal the original
  DR request bytes for the same cell. For cell 0 at g1, the rendered prompt has the same template
  as any other cell.
- **Independent replicates:** each replicate uses its own fresh, empty cache directory. Replicate
  2 must make 1000 live requests per world. Any cache hit across replicates aborts the run (a hit
  would make the two runs identical and the noise estimate zero).
- Commit hash recorded per arm × replicate × world. Watchdog, nohup and manifest rules as in
  CHAIN_HYGIENE.

## Metrics

- J(g) and J@g10 per world, over all 100 cells (all are model cells now). Also over the 96 non-forced
  cells, for comparison with the as-run figures.
- g1 independent finds, witness cells holding P_e at g10, as in `stats_for_correction.md`.
- Cost per arm.

## Noise and the test (derived, locked)

Let x_w¹, x_w² be the two replicates' J@g10 in world w (96-cell count, so it is comparable with the
as-run DR), and a_w the as-run 96-cell J@g10.

- Replicate variance: σ̂² = (1/5)·Σ_w (x_w¹ − x_w²)² / 2, which has 5 degrees of freedom.
- Clean mean per world: m_w = (x_w¹ + x_w²)/2.
- D = (1/5)·Σ_w (a_w − m_w). If the four forced cells have no effect, a_w is a third draw from the
  same distribution, so Var(a_w − m_w) = 1.5σ², and SE(D) = σ̂·√(1.5/5).
- **Test:** t = D / SE(D), compared with t₅. One-sided, because forced publishers of the truth
  can only help: a large positive D means they mattered.

**Limitation, stated in advance:** J is bounded, and worlds at the ceiling (1.00) contribute
almost no variance. If σ̂ = 0, report that the test is undefined, and report the per-world
differences only.

## Predictions (locked)

- **C1 (the forced cells do not change the result):** for DRc, t < 2.015 (one-sided t₅, α = 0.05).
  The same test is reported for DRc-noex.
- **C2 (where it would show):** if any world drops, the largest drop a_w − m_w is in world 2. That
  is the world with the fewest g1 finds (3) and the only one where non-forced holders first
  outnumber the forced four at g2, not g1. Descriptive, with chance level 1/5.
- **C3 (population vs one agent, descriptive):** report m_w − DRo-iter_w per world, with σ̂·√1.5 as
  the per-world noise band. No threshold. The old "≥ 0.10" prediction is not reused.

## Readout

- **C1 holds:** the article's distributed-world figures are replaced by DRc (100 cells, clean
  design). The forced-publisher runs go into a dated correction note.
- **C1 fails:** the forced cells mattered. The article reports DRc as the result of the designed
  world and states the size of the difference.
- Either way, σ̂ is the project's first measured run-to-run noise for a reasoning arm, and later
  reasoning-arm thresholds use it.

## Cost

From the logged DR usage scaled to 100 cells: ≈ $2.08 per arm-replicate (five worlds). Four
arm-replicates ≈ $8.3. Alarm $15. Report the actual cost.

## Constraints

Closed-model outputs are not used as training data. No reasoning text is requested or stored.
Use a new runner and edit no running script. Commit this file before the gate. Amendments come
before numbers.