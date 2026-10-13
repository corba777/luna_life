# An-T0 Life-run gate (`TASK_LIFE_AN_T0_RUN.md`)

Feasibility / honour closed by `TASK_LIFE_AN_T0.md` (T0 PASS, T1 PASS).

## 1. An-T0 vs An payloads (forced identical An history, g2)

Seed 1, cells [1, 2, 3]. Allowed difference: only `"temperature": 0`.

- cell 1: shared=True, temp-only=True, keys differ=True, An-cache hit=False → **PASS** (An `d8adee9b660f4951…` / T0 `1a20593a646074cf…`)
- cell 2: shared=True, temp-only=True, keys differ=True, An-cache hit=False → **PASS** (An `008354265516de57…` / T0 `850902607ac7250c…`)
- cell 3: shared=True, temp-only=True, keys differ=True, An-cache hit=False → **PASS** (An `0e4f89a4db0aa04b…` / T0 `944d282730e2161e…`)

## 2. Startup asserts

- 4 sources: **True** (`[0, 5, 50, 55]`)
- every request: `effort=none`, `temperature=0`
- no reasoning text requested or stored
- cache keys include `temperature`
- **0 An-cache hits** for T0 keys: **True** (hits=0 under `runs/life_luna_none/cache_An`)

## 3. Commit

This file committed before the first An-T0 Life API call.

## Verdict

**PASS**

```json
{
  "seed": 1,
  "cells": [
    1,
    2,
    3
  ],
  "n_sources": 4,
  "an_cache_hits_for_t0_keys": 0,
  "cells_detail": [
    {
      "cell_id": 1,
      "shared_fields_identical": true,
      "temperature_only_diff": true,
      "cache_keys_differ": true,
      "an_cache_hit_for_t0_key": false,
      "an_sha": "d8adee9b660f4951",
      "t0_sha": "1a20593a646074cf",
      "t0_cache_key": "c01882383ae7a9d0",
      "pass": true
    },
    {
      "cell_id": 2,
      "shared_fields_identical": true,
      "temperature_only_diff": true,
      "cache_keys_differ": true,
      "an_cache_hit_for_t0_key": false,
      "an_sha": "008354265516de57",
      "t0_sha": "850902607ac7250c",
      "t0_cache_key": "be00ad7d5f0fb630",
      "pass": true
    },
    {
      "cell_id": 3,
      "shared_fields_identical": true,
      "temperature_only_diff": true,
      "cache_keys_differ": true,
      "an_cache_hit_for_t0_key": false,
      "an_sha": "0e4f89a4db0aa04b",
      "t0_sha": "944d282730e2161e",
      "t0_cache_key": "07f4577577a38b61",
      "pass": true
    }
  ],
  "pass": true
}
```

