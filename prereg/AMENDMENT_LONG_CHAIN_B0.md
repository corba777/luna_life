# Amendment — Long chain: zero-source arm B0 and a lineage fix

**Status:** locked (`636f063e2f`, before first B0 call).
Parent: `TASK_LIFE_LONG_CHAIN.md` (`b659a6f`). W1–W5 and their thresholds are unchanged.

## Why

In B1, about 30% of reasoning cells find P_e alone in the first generation, as in Bs (no channel,
J ≈ 0.25). Every such cell becomes an extra source scattered over the grid. The real chain is
therefore short, and the single seeded source may matter little. B0 asks the sharper question:
**does a population of reasoning cells reach the truth with no seeded source at all, only from
scattered solo finds, the channel and feedback?**

## 1. New arm B0

| arm | cells | sources | channel | check |
|---|---|---|---|---|
| **B0** | Luna Responses, medium | **0** | on | own reasoning |

- World seeds 2-op 1–5, the same as B, Bs and B1 (same P_e, examples and order seeds).
- Everything else as B1. With no sources, J is computed over all 100 cells. The first generation
  is the same situation as Bs and B1 at g1 (no messages yet); report g1 J for B0, Bs and B1 side by
  side as a check.
- Invariant checks as in the parent. Add one more: no cell is marked as a source in any
  generation.
- Cost: about B1's (~$0.45 per seed); cap $5 for this arm, inside the parent's $40.

## 2. Predictions (lock)

- **W6:** B0 J at g10 ≥ 0.70 in ≥ 3 of 5 seeds. The population converges on the truth without any
  seeded source.
- **W7 (descriptive):** B0 on seed 1 (`shift_symbols(1);swap(2,3)`, where the simpler first
  operation fits ~97% of examples) ends in a false lock on `shift_symbols(1)` at g10. Report the
  modal rule and share at g10 for every seed.
- **W8 (descriptive, paired by seed):** J at g10 for B0, B1 and B (4 sources), and Bs at g10. The
  readout is about whether seeded sources add anything beyond solo finds.

## 3. Lineage fix (descriptive; no prediction depends on it)

The strict `source-lineage` label (every P_e-holding parent must be source-lineage) is degenerate
when ~30% of cells are solo finds: with 8 neighbours, P(no solo neighbour) ≈ 0.7^8 ≈ 0.06. Keep it,
mark it as degenerate, and add:
- `source_ancestry`: at least one P_e-holding parent is of source or mixed lineage
  (= source-lineage ∪ mixed);
- `solo_only`: every P_e-holding parent is of solo lineage.
Report both at g10 and by distance, for B1, Ca1 and Da1. B0 has only solo lineage by construction.

## Readout

- W6 PASS → collective inference without a teacher. Scattered solo discoveries, a channel and
  "you were wrong" are enough; for reasoning cells the seeded sources mostly speed things up.
- W6 FAIL with false locks → without a source, the population can settle on the simpler false rule.
  A seeded truth matters exactly where the prior misleads (compare W7 with B1 and B on seed 1).
- W6 FAIL without false locks → solo finds are too sparse to spread without a seeded source;
  report J(g) to see whether this is slow or stalled.

## Artifacts

- `runs/life_long_chain/B0/seed{n}/`
- B0 rows, W6–W8 and the lineage fields in `runs/life_long_chain/summary.json`
- `fig_wave.png`: add B0 to the J(g) panel

## Close — W7 (seed 1; before remaining B0 seeds)

| prediction | verdict | note |
|---|---|---|
| **W7** | **FAIL** | Best possible fail. Seed 1 does **not** false-lock on `shift_symbols(1)` at g10. |

At g1, ~75% hold the simpler false rule and ~23% find P_e alone (same solo rate as Bs). Without a channel (Bs) that majority lasts all 10 generations. With a channel and **zero** seeded sources, the minority overturns it by ~g3; by g6 J ≈ 0.98 (g10 J = 0.98). Mechanism: majority keeps getting “wrong”; at ~23% solo finds almost every cell has ≥1 P_e neighbour; Part 0 ≈ 77%/gen switch given one check-passing neighbour and no compatible competitor. The forecast assumed a seeded teacher was needed to break a false consensus; what breaks it is **self-found truth + channel + negative feedback**. Paper line: *a quarter of the population that found the truth on its own overturned a three-quarter false majority within two generations, with no seeded source, because the majority kept being told it was wrong and the minority's answer survived each agent's own check.* Artifact: `runs/life_long_chain/w7_seed1_close.json`.

## Close — W6 / W8 (all five B0 seeds)

| prediction | verdict | note |
|---|---|---|
| **W6** | **PASS** | J@g10 ≥ 0.70 in **5/5** seeds (0.98 / 0.99 / 1.00 / 1.00 / 1.00). |
| **W7** | **FAIL** | See above (seed 1). |
| **W8** | descriptive | B0 ≈ B1 ≈ B(4src) ≫ Bs at g10 — seeded sources add little beyond solo finds + channel. |

Mean B0 J(g): 0.29 → 0.50 → 0.66 → 0.84 → 0.94 → **0.99** by g6. Full table: `runs/life_long_chain/summary.json` → `predictions.W6` / `W8`.