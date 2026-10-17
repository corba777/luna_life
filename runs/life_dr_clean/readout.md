# DRc readout

Locked task: `TASK_LIFE_DR_CLEAN.md`. The article is not edited. Step 1 is not started.

J(g) below is the share of all 100 cells holding P_e. The C1 test uses the 96-cell share, which drops cells 0, 5, 50 and 55 so it matches the as-run count. g1 finds are non-forced cells holding P_e at g1, before any message. A witness cell is a non-forced cell whose cofitting set does not contain the shorter rule, the program before the first `;`.

## Verdicts

**C1 fails for DRc.** σ̂ = 0.1892. D = 0.3802. SE = 0.1036. t = 3.669, compared with t₅ = 2.015.

**C1 fails for DRc-noex.** σ̂ = 0.0929. D = 0.3802. SE = 0.0509. t = 7.474, compared with t₅ = 2.015.

The locked consequence of a C1 failure is that the article reports DRc as the result of the designed world and states the size of the difference. That edit is not applied in this file. The size on the 96-cell count is D = 0.3802 in both arms.

σ̂ is the first measured run-to-run noise for a reasoning arm. DRc σ̂ = 0.1892. DRc-noex σ̂ = 0.0929.

**C2 holds for DRc.** The largest drop a − m is world 2 (a − m = 0.6562). Chance level 1/5.

**C2 for DRc-noex.** The largest drop a − m is world 1 (a − m = 0.9583), not world 2.

**C3 is descriptive.** No threshold. The per-world noise band is σ̂·√1.5: 0.2317 for DRc and 0.1138 for DRc-noex.

| world | DRc m − DRo-iter | DRc-noex m − DRo-iter |
|---:|---:|---:|
| 1 | 0.4031 | -0.3000 |
| 2 | -0.6646 | -0.7427 |
| 3 | -0.1958 | -0.6073 |
| 4 | -0.7698 | -0.9000 |
| 5 | -0.1948 | -0.9135 |

## DRc-noex J@g10

| world | r1, 100 cells | r2, 100 cells | r1, 96 cells | r2, 96 cells |
|---:|---:|---:|---:|---:|
| 1 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| 2 | 0.1100 | 0.0000 | 0.1146 | 0.0000 |
| 3 | 0.0600 | 0.3200 | 0.0625 | 0.3229 |
| 4 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| 5 | 0.0700 | 0.0000 | 0.0729 | 0.0000 |

## DRc

### World 1 — `shift_symbols(1);swap(2,3)`

| replicate | J(g), 100 cells | at g10 | g1 finds | witness cells holding P_e at g10 |
|---:|---|---|---:|---|
| 1 | 0.18 0.19 0.24 0.28 0.35 0.37 0.45 0.51 0.56 0.61 | rising (Δ +0.05) | 17 (3, 9, 14, 17, 33, 36, 39, 41, 44, 60, 63, 66, 69, 71, 77, 93, 99) | 22 / 24 (`shift_symbols(1)`) |
| 2 | 0.17 0.20 0.26 0.31 0.33 0.39 0.46 0.57 0.69 0.80 | rising (Δ +0.11) | 17 (3, 6, 9, 11, 17, 39, 41, 60, 63, 69, 71, 74, 77, 90, 93, 96, 99) | 23 / 24 (`shift_symbols(1)`) |

### World 2 — `rotate_left(1);swap(0,3)`

| replicate | J(g), 100 cells | at g10 | g1 finds | witness cells holding P_e at g10 |
|---:|---|---|---:|---|
| 1 | 0.03 0.05 0.07 0.08 0.13 0.15 0.18 0.20 0.20 0.23 | rising (Δ +0.03) | 3 (9, 39, 60) | 8 / 24 (`rotate_left(1)`) |
| 2 | 0.03 0.03 0.03 0.03 0.05 0.05 0.05 0.06 0.04 0.04 | flat (Δ +0.00) | 3 (9, 39, 60) | 4 / 24 (`rotate_left(1)`) |

### World 3 — `shift_symbols(6);swap(1,3)`

| replicate | J(g), 100 cells | at g10 | g1 finds | witness cells holding P_e at g10 |
|---:|---|---|---:|---|
| 1 | 0.09 0.10 0.11 0.13 0.15 0.20 0.21 0.25 0.29 0.39 | rising (Δ +0.10) | 9 (6, 17, 30, 39, 41, 47, 71, 74, 90) | 22 / 24 (`shift_symbols(6)`) |
| 2 | 0.06 0.12 0.13 0.17 0.24 0.31 0.39 0.52 0.68 0.83 | rising (Δ +0.15) | 5 (30, 54, 66, 74, 90) | 22 / 24 (`shift_symbols(6)`) |

### World 4 — `reverse;shift_symbols(6)`

| replicate | J(g), 100 cells | at g10 | g1 finds | witness cells holding P_e at g10 |
|---:|---|---|---:|---|
| 1 | 0.11 0.11 0.08 0.10 0.14 0.16 0.20 0.22 0.23 0.26 | rising (Δ +0.03) | 11 (23, 39, 47, 54, 60, 63, 64, 65, 66, 68, 81) | 25 / 96 (`reverse`) |
| 2 | 0.09 0.06 0.07 0.02 0.01 0.02 0.02 0.02 0.02 0.00 | falling (Δ -0.02) | 8 (32, 37, 60, 64, 68, 70, 85, 91) | 0 / 96 (`reverse`) |

### World 5 — `shift_symbols(1);swap(0,3)`

| replicate | J(g), 100 cells | at g10 | g1 finds | witness cells holding P_e at g10 |
|---:|---|---|---:|---|
| 1 | 0.17 0.22 0.31 0.40 0.51 0.57 0.65 0.70 0.78 0.84 | rising (Δ +0.06) | 16 (9, 11, 17, 33, 36, 39, 41, 44, 60, 63, 69, 71, 74, 77, 93, 99) | 24 / 24 (`shift_symbols(1)`) |
| 2 | 0.15 0.22 0.29 0.35 0.36 0.40 0.43 0.51 0.60 0.68 | rising (Δ +0.08) | 14 (3, 6, 14, 30, 33, 36, 69, 71, 74, 77, 90, 93, 96, 99) | 22 / 24 (`shift_symbols(1)`) |

## DRc-noex

### World 1 — `shift_symbols(1);swap(2,3)`

| replicate | J(g), 100 cells | at g10 | g1 finds | witness cells holding P_e at g10 |
|---:|---|---|---:|---|
| 1 | 0.12 0.11 0.08 0.01 0.00 0.00 0.00 0.00 0.00 0.00 | flat (Δ +0.00) | 12 (30, 36, 39, 41, 44, 63, 66, 69, 74, 90, 93, 96) | 0 / 24 (`shift_symbols(1)`) |
| 2 | 0.14 0.13 0.09 0.00 0.00 0.00 0.00 0.00 0.00 0.00 | flat (Δ +0.00) | 14 (3, 6, 9, 17, 30, 36, 39, 41, 47, 66, 71, 74, 93, 99) | 0 / 24 (`shift_symbols(1)`) |

### World 2 — `rotate_left(1);swap(0,3)`

| replicate | J(g), 100 cells | at g10 | g1 finds | witness cells holding P_e at g10 |
|---:|---|---|---:|---|
| 1 | 0.03 0.06 0.10 0.12 0.14 0.13 0.14 0.12 0.13 0.11 | falling (Δ -0.02) | 3 (9, 39, 60) | 3 / 24 (`rotate_left(1)`) |
| 2 | 0.03 0.03 0.02 0.01 0.01 0.00 0.00 0.00 0.00 0.00 | flat (Δ +0.00) | 3 (9, 39, 60) | 0 / 24 (`rotate_left(1)`) |

### World 3 — `shift_symbols(6);swap(1,3)`

| replicate | J(g), 100 cells | at g10 | g1 finds | witness cells holding P_e at g10 |
|---:|---|---|---:|---|
| 1 | 0.06 0.09 0.08 0.07 0.06 0.08 0.08 0.07 0.08 0.06 | falling (Δ -0.02) | 6 (6, 30, 41, 47, 66, 74) | 1 / 24 (`shift_symbols(6)`) |
| 2 | 0.07 0.12 0.23 0.27 0.30 0.33 0.33 0.33 0.32 0.32 | flat (Δ +0.00) | 7 (6, 9, 39, 41, 66, 71, 90) | 8 / 24 (`shift_symbols(6)`) |

### World 4 — `reverse;shift_symbols(6)`

| replicate | J(g), 100 cells | at g10 | g1 finds | witness cells holding P_e at g10 |
|---:|---|---|---:|---|
| 1 | 0.09 0.09 0.12 0.09 0.03 0.00 0.00 0.00 0.00 0.00 | flat (Δ +0.00) | 9 (4, 6, 20, 43, 44, 65, 68, 70, 98) | 0 / 96 (`reverse`) |
| 2 | 0.10 0.10 0.09 0.07 0.05 0.05 0.04 0.00 0.00 0.00 | flat (Δ +0.00) | 10 (8, 21, 47, 60, 63, 65, 68, 70, 76, 81) | 0 / 96 (`reverse`) |

### World 5 — `shift_symbols(1);swap(0,3)`

| replicate | J(g), 100 cells | at g10 | g1 finds | witness cells holding P_e at g10 |
|---:|---|---|---:|---|
| 1 | 0.18 0.20 0.18 0.17 0.15 0.13 0.13 0.12 0.09 0.07 | falling (Δ -0.02) | 17 (6, 9, 11, 14, 17, 33, 36, 39, 44, 47, 63, 69, 71, 77, 90, 96, 99) | 1 / 24 (`shift_symbols(1)`) |
| 2 | 0.11 0.12 0.12 0.05 0.00 0.00 0.00 0.00 0.00 0.00 | flat (Δ +0.00) | 10 (6, 30, 33, 39, 41, 63, 71, 77, 90, 93) | 0 / 24 (`shift_symbols(1)`) |

## Cost

Actual total $7.6782. Alarm $15 was not hit.

