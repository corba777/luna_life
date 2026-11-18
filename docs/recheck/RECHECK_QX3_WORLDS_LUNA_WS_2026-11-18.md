# Recheck — QX-3 across worlds, Luna, W-S (2026-11-18)

Package `qx3_luna_worlds_ws_artem_recheck_2026-11-18.zip`, sha256 `e90f28f8…cbc8`; SHA256SUMS passes.
Amendment `AMENDMENT_QX3_WORLDS.md` locked v2. Recomputed with `ws_check.py` (own code; keys read from each
trace, world 0 computed). H_T at δ = 1/8 rebuilt independently per world (after `shift_symbols(1)`: w0
`subst(0,E,F)`, w1 `subst(3,D,E)`, w2 `subst(0,F,B)`, w3 `subst(3,E,C)`, w4 `subst(0,D,E)`); every stored test
output equals it. Every number in the agent's readout reproduces.

| world | H_F / H_T | left H_F at 1–4 naming neighbours | at 5 or more | d |
|---:|---|---:|---:|---:|
| 0 (r2) | K026 / K047 | 0/65 | 32/32 | 1.000 |
| 1 | K035 / K034 | 0/73 | 41/45 | 0.911 |
| 2 | K114 / K015 | 0/74 | 41/49 | 0.837 |
| 3 | K028 / K043 | 2/61 | 25/28 | 0.860 |
| 4 | K005 / K060 | 0/83 | 48/54 | 0.889 |

**W-S holds:** d > 0 in all five worlds, every group ≥ 5 cells, P ≤ 1/32, as predicted.
Pooled (nominal): 2/356 [0.001, 0.020] against 187/208 [0.850, 0.936].

All runs 24 × 100, not partial, 0 fallbacks, no received results. Luna spend for the worlds amendment $11.7495;
with the main phase, $32.3155 of the $45.00 authorization.
