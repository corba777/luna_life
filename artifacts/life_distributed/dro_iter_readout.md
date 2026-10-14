# TASK_LIFE_DRO_ITER — readout

Generated: 2026-10-14T08:56:53.052189+00:00 (updated seed-1 diag 2026-10-14)
**USD (list):** $0.6176 (estimate ~$5, alarm $10)

## Verdicts

- **I0** (|g1 − DRo| ≤ 0.10): **PASS** (g1 mean=0.570, DRo=0.560)
- **I1** (g10 < 0.80): **PASS** (g10 mean=0.750)
- **I2** (primary: g10 ≤ DR − 0.10): **PASS** (g10=0.750, DR J@g10=0.852, thresh=0.752) — **margin 0.002**

## Readout (I2 PASS branch)

With the same ten generations and memory of its own rule, one agent holding all nine
neighbourhood examples stays below the DR population (rules-only channel, one example
each). The collective's advantage is **not only time**. Report alongside Phase-1 D5
(DR adopts received rules that fit its own example) and the D2 post-hoc (DRo one-shot
pooling fails to assemble nine examples).

**Mean gap is driven by seed 1:** DR J@g10 = 1.00 vs DRo-iter g10 = 0.30 (Δ = 0.70).
Seeds 2–5 are near or above the DR seed means; without seed 1 the seed-mean g10 would
sit at ~0.86 and I2 would fail. I2 still PASSes on the registered seed mean by 0.002.

## Per seed (vs DR / DRo)

| seed | DRo-iter g1 | DRo-iter g10 | DRo (ref) | DR J@g10 | Δ(DR − iter g10) | USD |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.15 | **0.30** | 0.20 | **1.00** | **+0.70** | 0.0681 |
| 2 | 0.65 | 0.80 | 0.50 | 0.80 | 0.00 | 0.1564 |
| 3 | 0.55 | 0.80 | 0.75 | 0.75 | −0.05 | 0.0989 |
| 4 | 0.55 | 0.90 | 0.50 | 0.71 | −0.19 | 0.1974 |
| 5 | 0.95 | 0.95 | 0.85 | 1.00 | +0.05 | 0.0968 |
| **mean** | **0.57** | **0.75** | **0.56** | **0.852** | **+0.102** | **0.618** |

Figure: `fig_dro_iter.png`

## Seed 1 descriptive (g10 wrong holds)

P_e = `shift_symbols(1);swap(2,3)`. At g10: 6/20 correct, **14/20 wrong**.

All 14 wrong agents hold the **same 1-op rule** `shift_symbols(1)` (a proper prefix of
P_e; in some cell’s single-example S_c). Fit to the nine pooled examples:

| n_fit of 9 | n agents |
|---:|---:|
| 7 | 13 |
| 6 | 1 |

No wrong agent holds a rule that fits all nine. They lock onto the salient 1-op that
covers most of the neighbourhood and never recover the second op without feedback.
Detail: `dro_iter_seed1_wrong_diag.json`.

## Post-hoc — DR seed 1 vs `shift_symbols(1)` (descriptive)

Same world as DRo-iter seed 1 (`P_e = shift_symbols(1);swap(2,3)`). Of 100 cells,
**25** have an own example **inconsistent** with `shift_symbols(1)` (rule not in
`hypothesis_set`; share **0.25**). Detail: `dr_seed1_shift1_inconsistent.json`.

What those 25 held under **DR** at g1–g3:

| gen | `P_e` | `shift_symbols(1)` | other |
|---:|---:|---:|---:|
| g1 | 15 | 9 | 1 (`reverse;shift_symbols(7)`) |
| g2 | 21 | 4 | 0 |
| g3 | 21 | 4 | 0 |

Most witness cells are already on `P_e` by g2. A minority still hold the
inconsistent 1-op at g1 (9) and a few keep it through g3 (4) — DR’s check does
not instantly clear every local mismatch. Contrast DRo-iter seed 1, where the
14 wrong agents all stay on that same 1-op.
