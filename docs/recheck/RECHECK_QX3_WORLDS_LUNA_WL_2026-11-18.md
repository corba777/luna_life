# Recheck — QX-3 across worlds, Luna, W-L (2026-11-18)

Package `qx3_luna_worlds_wl_artem_recheck_2026-11-18.zip`, sha256 `2f7f98cb…32c3`; SHA256SUMS passes.
Amendment `AMENDMENT_QX3_WORLDS.md` locked v2, sha256 `4d81a0e0…e6ae`. Recomputed with `wl_check.py` (own code).
H_F and H_T keys are read from each trace (world 0: K026 / K014). H_T is rebuilt independently from the
substitutions reported for `build_world(seed)` (w0 `subst_if(0,E,F,1,H)`, w1 `subst_if(3,D,E,0,D)`,
w2 `subst_if(0,F,B,3,D)`, w3 `subst_if(3,E,C,1,F)`, applied after `shift_symbols(1)`): every stored test
output, own and received, in all eight traces equals this H_T. Every number in the agent's readout reproduces.

| world | arm | x̄ | x̄_nf | independent finders | following | tests on region |
|---:|---|---:|---:|---:|---:|---:|
| 0 (r2) | R | 0.0058 | 0 | 3 | 0 | 3/100 |
| 0 (r2) | R+E | 0.9992 | 0.919 | 2 | 6 | 8/100 |
| 1 | R | 0 | 0 | 2 | 0 | 2/100 |
| 1 | R+E | 0.9992 | 0.919 | 4 | 4 | 8/99 |
| 2 | R | 0 | 0 | 4 | 0 | 4/98 |
| 2 | R+E | 0.9958 | 0.766 | 5 | 18 | 23/100 |
| 3 | R | 0 | 0 | 0 | 0 | 0/97 |
| 3 | R+E | 0.9992 | 0.890 | 3 | 8 | 11/100 |

**W-L holds:** complete separation, p = 1/70 ≤ 0.05, as predicted. All runs 24 × 100, not partial, 0 fallbacks.

## Observations (post hoc, descriptive)

- Discovery: in the four R runs, 9 of 395 tests (2.3 %) fell on the H_T region, against 1/64 = 1.6 % for a
  random input; world 3 R spent no test on it. See the next section for where the tests go instead.
- In arm R, finders do not end on H_T. All 9 finders in the four R runs move to the unconditional sibling
  `U_t` (the δ = 1/8 substitution of that world: K047, K034, K015), which also fits a single counterexample and
  their two examples. Only one world-0 cell reached H_T for 7 generations. So in arm R the name neighbours hear
  from a finder is mostly not H_T. With shared results (R+E), the population collects several counterexamples
  and ends on H_T.

## Two pieces of evidence (post hoc, descriptive; added 2026-11-18)

Seven R+E runs at δ = 1/64 (worlds 0 r2, 1, 2, 3, and world 0 r3–r5) and the matching R runs. `u_check.py`,
`u_src.py` (own code). U is the unconditional sibling of H_T in each world (the δ = 1/8 substitution: K047,
K034, K015, K043). A result **refutes U** when its input is one where U changes the output and the stored
output equals H_F's.

**Independent finders in R+E (20):** 12 first move to U, 7 straight to H_T, 1 to another rule. All 20 end on
H_T, and each moves to H_T in or after the generation in which it first holds a received result that refutes
U. With B = 1 a finder's own test was the counterexample, so it cannot refute U itself.

**Cells that reach H_T in R+E (700):** 688 held both a counterexample to H_F and a result refuting U at the
generation they moved (567 straight from H_F, 121 via U); 12 moved without a U-refuting result.

**Where the U-refuting results come from.** Luna's tests are aimed at the catalog's substitution rules:

| arm | tests made with no counterexample in memory | on the U-only region (chance 7/64 = 10.9 %) | on the H_T region (chance 1.6 %) |
|---|---:|---:|---:|
| R | 689 | 283 (41.1 %) | 22 (3.2 %) |
| R+E | 583 | 205 (35.2 %) | 20 (3.4 %) |

After holding a counterexample, R+E cells put 63 of 115 tests (55 %) on the H_T region. Messages carrying a
U-only result: 117–209 per R+E run. So the result that refutes U is common and widely shared; the
counterexample to H_F is rare. In R the same U-refuting tests are made but never shared, and finders stay on U.

Reading (descriptive, one model, not tested): no single cell holds H_T's evidence at first. The rare
counterexample (against H_F) and a common negative result (against the simpler U) come from different cells,
and the population ends on H_T only when both can travel.

## First finders and names (post hoc; `heard.py`, `heard3.py`)

Cells that found a counterexample before receiving one, all Luna δ = 1/64 runs in world 0 QX-2 (B 1 and 4,
r1–r2), QX-3 world 0 (R and R+E, r2–r5) and worlds 1–3. "Heard" = a neighbour's message named H_T in an
earlier generation.

| | H_T | U | other |
|---|---:|---:|---:|
| not heard (first finders) | 11 | 34 | 4 |
| heard H_T named | 36 | 1 | 2 (H_F) |

QX-2 finders went mostly to H_T because most of them found their counterexample after H_T was being named
nearby; the QX-2 first finders behave like QX-3's (U 4, H_T 2, other 2 of 8). The budget does not change the
first choice; with B = 4 a finder can later rule U out with its own tests.
