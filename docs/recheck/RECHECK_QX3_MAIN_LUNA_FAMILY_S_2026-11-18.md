# Recheck — QX-3 main phase, Luna, Family S (2026-11-18)

Package `qx3_luna_family_s_artem_recheck_2026-11-18.zip`, sha256 `674055a5…b2b8`; SHA256SUMS passes (8 files).
Amendment `AMENDMENT_QX3_MAIN.md` locked v3, sha256 `d1c61ebc…37a1`. Recomputed from the five traces with
`famS_check.py` (own code, written from the locked text). Every number in the agent's readout reproduces.

## Locked test

Luna, δ = 1/8, B = 1, rule only, runs r2–r6. Cells on H_F at g − 1 with no own counterexample in memory at g;
k = neighbours that named a rule other than H_F in g − 1; per cell, the first generation with 1 ≤ k ≤ 4 and the first
with k ≥ 5; the share holding another rule at that generation.

| run | p_low | p_high | d |
|---|---:|---:|---:|
| r2 | 0/65 | 32/32 | 1.000 |
| r3 | 0/69 | 32/36 | 0.889 |
| r4 | 0/73 | 37/42 | 0.881 |
| r5 | 1/69 | 36/38 | 0.933 |
| r6 | 0/54 | 29/35 | 0.829 |

d > 0 in 5 of 5 runs; every group has at least 5 cells. **S holds**, P ≤ 1/32 = 0.031, as predicted.

Pooled, one observation per cell per group: 1/330 (95 % CP [0.0001, 0.017]) against 166/183 ([0.855, 0.945]).
Nominal: cells within a run interact.

## Integrity

- Each run 24 generations × 100 cells, `partial = False`, 0 fallbacks, 0 retries; r6 format gate not tripped.
- Arm R: no received results in any trace.
- r6 resume: 28 cache hits, all generation 1, cells 0–27. calls.jsonl holds 2,428 r6 rows over 2,400 distinct
  (generation, cell, draw); each of the 28 duplicate pairs matches on text, `prompt_sha256` and `cache_key`.
- Spend: r6 $1.0579 from non-cached rows; Luna main phase $20.566 against the $24.00 stop; envelope left $4.434.
- Go phrase for the resume: logged in Artem's words (agent's report; Artem copied the phrase himself).
