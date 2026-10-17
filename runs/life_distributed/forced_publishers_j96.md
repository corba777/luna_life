# Forced publishers — J over 96 cells

Descriptive. Closed reports are not changed.

`source_ids_override(())` covers construction only. During `sim.step()`, cells 0, 5, 50 and 55 publish P_e. In every saved generation their `source_mask` is true and their rule is P_e. The closed reports still say `n_sources: 0`, because that field is a constant in `run_population`.

**As reported** is the share of all 100 cells holding P_e at generation 10 (`j_g10_all_100`, or the last entry of `J_series` for the local arms). **96-cell** drops those four cells. Seed mean is the unweighted mean of the worlds that exist.

## Affected

| arm | worlds | affected | as reported (100) | 96-cell |
|---|---:|---|---:|---:|
| DR | 1–5 | yes | 0.852 (426/500) | 0.846 (406/480) |
| DRs | 1–5 | yes | 0.146 (73/500) | 0.110 (53/480) |
| DC | 1–5 | yes | 0.054 (27/500) | 0.015 (7/480) |
| DCs | 1–5 | yes | 0.040 (20/500) | 0.000 (0/480) |
| DR_noex | 1–5 | yes | 0.460 (230/500) | 0.438 (210/480) |
| DR_T | 1 | yes | 0.230 (23/100) | 0.198 (19/96) |
| DRs_T | 1 | yes | 0.170 (17/100) | 0.135 (13/96) |

### DR

| world | 100 | 96 |
|---:|---:|---:|
| 1 | 100/100 | 96/96 |
| 2 | 80/100 | 76/96 |
| 3 | 75/100 | 71/96 |
| 4 | 71/100 | 67/96 |
| 5 | 100/100 | 96/96 |
| mean | 0.852 | 0.846 |

### DRs

| world | 100 | 96 |
|---:|---:|---:|
| 1 | 21/100 | 17/96 |
| 2 | 7/100 | 3/96 |
| 3 | 12/100 | 8/96 |
| 4 | 11/100 | 7/96 |
| 5 | 22/100 | 18/96 |
| mean | 0.146 | 0.110 |

### DC

| world | 100 | 96 |
|---:|---:|---:|
| 1 | 4/100 | 0/96 |
| 2 | 4/100 | 0/96 |
| 3 | 4/100 | 0/96 |
| 4 | 10/100 | 6/96 |
| 5 | 5/100 | 1/96 |
| mean | 0.054 | 0.015 |

### DCs

Every world is 4/100 and 0/96. Mean 0.040 and 0.000.

### DR_noex

| world | 100 | 96 |
|---:|---:|---:|
| 1 | 96/100 | 92/96 |
| 2 | 17/100 | 13/96 |
| 3 | 45/100 | 41/96 |
| 4 | 46/100 | 42/96 |
| 5 | 26/100 | 22/96 |
| mean | 0.460 | 0.438 |

### DR_T and DRs_T (world 1 only)

| arm | 100 | 96 |
|---|---:|---:|
| DR_T | 23/100 | 19/96 |
| DRs_T | 17/100 | 13/96 |

## Not this loop

DRo (`run_dro`) and DRo-iter (`runs/run_life_dro_iter.py`) do not step `SimulationV1b`. Their numbers are not 100-cell shares and are not recomputed here.

## World 1 witness cells at generation 10

The 24 cells are the non-forced cells whose example excludes `shift_symbols(1)`. Cell 0 also excludes it and is a forced publisher, so it is not in the 24.

| arm | hold P_e |
|---|---:|
| DR (Luna) | 24/24 |
| DR_T | 17/24 |

Per-seed JSON: `runs/life_distributed/forced_publishers_j96.json`.
