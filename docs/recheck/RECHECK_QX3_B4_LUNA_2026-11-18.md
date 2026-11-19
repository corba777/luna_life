# Recheck — QX-3 with four tests per cell, Luna, T-L4 (2026-11-18)

Package `qx3_luna_b4_artem_recheck_2026-11-18.zip`, sha256 `fa696f17…e799`; SHA256SUMS passes. Amendment
`AMENDMENT_QX3_B4.md` locked v2. Recomputed with `b4_check.py` (own code; keys from the traces, world 0
computed; H_T rebuilt independently per world; every stored test output equals it). Every number in the
agent's readout reproduces.

Luna · δ 1/64 · rule only · worlds 0–3.

| world | x̄ at B = 1 | x̄ at B = 4 | x̄_nf at B = 4 | finders at B = 4 |
|---:|---:|---:|---:|---:|
| 0 | 0.0058 | 0.8392 | 0.0400 | 94 |
| 1 | 0 | 0.3075 | 0.0208 | 60 |
| 2 | 0 | 0.9883 | 0.0183 | 98 |
| 3 | 0 | 0.4433 | 0.0442 | 76 |

**T-L4 holds:** p = 1/70, as predicted. At most four tests per cell, none in generation 24, no received
results; runs 24 × 100, not partial.

Finders (328): two generations after the counterexample, H_T 292, U 8, H_F or other 10, no g + 2: 18. Of
the 310 with g + 2, 233 then hold an own result ruling out U.

## Where the tests go (post hoc, descriptive)

Tests on the H_T region by the tester's state when it chose the test, all four worlds:

| state of the tester | on the H_T region |
|---|---:|
| no counterexample yet, no neighbour has named H_T | 26 / 710 (3.7 %) |
| no counterexample yet, a neighbour has named H_T | 302 / 361 (84 %) |
| already holds a counterexample | 135 / 248 (54 %) |

Reading (one model, not tested): a rule name moves a Luna cell's next test, not its rule. A cell that hears
H_T named tests where H_T and H_F differ, finds the counterexample itself, and only then switches; x̄_nf stays
at 0.02–0.04. With one test per cell this path is closed: the test is usually spent before any neighbour
names H_T, and the first finders take U (entry 8).

Resume of w0: 209 cache hits; logged go words `resume qx3b4_luna_d64_B4_R_w0 by cache replay, then w1-w3`.
