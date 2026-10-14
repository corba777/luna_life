# Distill Phase 0 — D0 readout

**D0 FAIL** as registered: T stage1 = **0.863454**, 95% Wilson CI **[0.8152, 0.9006]** (n=249, k=215; threshold 0.9).

**Stop:** no SD labelling / training (`STOP_SD_NO_TRAIN.ok`). SO-only (oracle, no teacher) = later amendment only — not now.

## S0
| metric | value |
|---|---:|
| stage1 | 0.096386 |
| stage2 | 0.028571 |
| stubborn | 0.189189 |
| validity frac_invalid | 0.1800 |

## T cost / projected hours
| | |
|---|---:|
| tokens / situation (live) | 6456.0 |
| Phase 0 wall T (h) | 5.26 |
| projected GPU h @ mean tok/s (live) | 5.47 |
| train-bank 3k label proj h (PASS branch only) | 54.7 |

Canonical: `runs/life_distill/phase0_gate.json`.

## Post-hoc (descriptive — no D0 change)

Registered stage1 counts still-truncated answers as fails in the stage1
denominator. Below: same situations, **completed answers only** (exclude
still-truncated from the denom). Offline from existing caches; no new run.
Detail: `phase0_completed_only_posthoc.json`.

### T

| | n | k | stage1 | 95% Wilson CI |
|---|---:|---:|---:|---|
| registered (incl. trunc as fail) | 249 | 215 | 0.863 | [0.815, 0.901] |
| **completed only** | **234** | **215** | **0.919** | **[0.877, 0.947]** |

**Are the 20 T invalids inside the stage1 denom (n=249)?** **No — not all.**
15/20 still-truncated rows fall in the stage1 denom; **5/20** are outside it
(situations with no inconsistent incoming). All 20 invalids are still-truncated
(0 unparseable).

Completed-only point estimate is above the 0.90 gate, but the CI still covers
values below 0.90. **D0 stays FAIL** as registered.

### S0

| | n | k | stage1 | 95% Wilson CI |
|---|---:|---:|---:|---|
| registered (incl. trunc as fail) | 249 | 24 | 0.096 | [0.066, 0.139] |
| **completed only** | **203** | **24** | **0.118** | **[0.081, 0.170]** |

**Invalids vs stage1 denom:** 54 still-truncated of 300 eval; **46/54** sit inside
the stage1 denom (n=249); 8/54 are outside. Not “54/249” — **46/249** of the
stage1 denom are still-truncated.

**Cap-limited baseline:** S0 ran `mode=direct`, `max_tokens=32`. That alone
truncates **54/300** answers (all of S0’s invalids). The registered S0 stage1
(0.096) is therefore **cap-limited**, not a pure competence floor under an
adequate completion budget.
