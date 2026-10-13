# Distributed world audit (TASK_LIFE_DISTRIBUTED draft)

`DIST_WORLD_SEED=20261013`, `|S_c|≥3`, 1-op share ≥0.4, ∩ neighbourhood S = {P_e}.

- seeds ok: **4** / 5
- accepted world seeds: `[2, 2, 3, 4, 5]`
- chance E[1/|S_c|] mean: **0.2510**
- mean assignment draws: **260.5**

## Per accepted seed

| seed | |S_c| hist | chance | share_1op | n_draws | P_e |
|---:|---|---:|---:|---:|---|
| 2 | `{'3': 2, '4': 30, '5': 2, '6': 63, '24': 3}` | 0.1919 | 0.98 | 3 | `rotate_left(1);swap(0,3)` |
| 2 | `{'3': 2, '4': 30, '5': 2, '6': 63, '24': 3}` | 0.1919 | 0.98 | 3 | `rotate_left(1);swap(0,3)` |
| 3 | `{'3': 18, '4': 79, '7': 2, '11': 1}` | 0.2613 | 0.73 | 1030 | `shift_symbols(6);swap(1,3)` |
| 4 | `{'3': 55, '4': 27, '5': 8, '7': 8, '11': 2}` | 0.2801 | 0.65 | 2 | `reverse;shift_symbols(6)` |
| 5 | `{'3': 30, '4': 66, '5': 2, '11': 2}` | 0.2708 | 0.70 | 7 | `shift_symbols(1);swap(0,3)` |

Pooled |S_c|: `{'3': 105, '4': 202, '5': 12, '6': 63, '7': 10, '11': 5, '24': 3}`

Draw log (including failed tries): see `draw_log` in JSON.
