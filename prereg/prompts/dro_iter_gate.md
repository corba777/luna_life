# DRo-iter gate (TASK_LIFE_DRO_ITER)

Lock surface vs Phase-1 DRo oracle prompts (`runs/run_life_distributed_phase1.py::run_dro`).

## g1 vs DRo

Same constitution (`_constitution("DRo")`), same 20 neighbourhood centres
(`_dro_nbhd_ids`), same nine `(input, output)` pairs, same centre query
(= centre cell input), same memory line `Previous step: none.`, same
schema / effort / parser.

**Allowed difference:** the probe line includes `, generation 1` after
`of 20`. Catalog `order_seed` at g1 matches DRo (`100_000 + world_seed * 200 + i`).
`catalog_digest` is `distributed-DRo-iter` (separate cache namespace).

## g2+

Additional differences only:
- generation number in the probe line
- query redrawn as 4 symbols from A–H (seeded per world/centre/gen)
- memory line `Previous step: rule='…' published=no.` from the agent's own
  previous inferred rule (no feedback, no channel)

## Cache

Fresh empty `runs/life_distributed/cache_DRo_iter/`; resume only via
`--resume` + this arm's manifest. No reuse of `cache_DRo`.

## Runtime

Seed 1 writes `runtime_gate_dro_iter_g2.json` before g3 (note pointer; dry
renders live next to DRo dry if needed).
