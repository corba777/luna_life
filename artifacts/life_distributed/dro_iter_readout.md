# TASK_LIFE_DRO_ITER — readout

Generated: 2026-10-14T08:56:53.052189+00:00
**USD (list):** $0.6176 (estimate ~$5, alarm $10)

## Verdicts

- **I0** (|g1 − DRo| ≤ 0.10): **PASS** (g1 mean=0.570, DRo=0.560)
- **I1** (g10 < 0.80): **PASS** (g10 mean=0.750)
- **I2** (primary: g10 ≤ DR − 0.10): **PASS** (g10=0.750, DR J@g10=0.852, thresh=0.752)

## Readout (I2 PASS branch)

With the same ten generations and memory of its own rule, one agent holding all nine neighbourhood examples stays below the DR population (rules-only channel, one example each). The collective's advantage is **not only time**. Report alongside Phase-1 D5 (DR adopts received rules that fit its own example) and the D2 post-hoc (DRo one-shot pooling fails to assemble nine examples).

## Per seed

| seed | g1 | g10 | mean | USD | DRo (ref) |
|---:|---:|---:|---:|---:|---:|
| 1 | 0.15 | 0.3 | 0.235 | 0.0681 | 0.2 |
| 2 | 0.65 | 0.8 | 0.705 | 0.1564 | 0.5 |
| 3 | 0.55 | 0.8 | 0.830 | 0.0989 | 0.75 |
| 4 | 0.55 | 0.9 | 0.850 | 0.1974 | 0.5 |
| 5 | 0.95 | 0.95 | 0.960 | 0.0968 | 0.85 |

Figure: `fig_dro_iter.png`

