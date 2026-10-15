# DR-noex gate (TASK_LIFE_DR_NOEX)

**Status:** PASS — 2026-10-15T01:42:38.282411+00:00  
0 API. Runner capture via `DistCompleter` (same builders as live).

## Locked replacement strings (g ≥ 2)

**Constitution sees-sentence (DR → DR-noex):**

```
You see your private examples, your current query, a one-step memory of the rule you held last generation (and whether you published it), and eight message slots from other cells. Unused slots are empty. You are not told whether your last rule was correct.
```

→

```
You saw your private example in the first generation; from now on you see your current query, a one-step memory of the rule you held last generation (and whether you published it), and eight message slots from other cells. Unused slots are empty. You are not told whether your last rule was correct.
```

**Examples block (DR → DR-noex):** the entire

```
Private examples:
  <IN> -> <OUT>
```

block is replaced by the single line:

```
Your private example is not shown this generation.
```

Nothing else may differ (memory, inbox, query, catalog, publish paragraph, JSON
tail, world sentence).

## g1

Payload byte-identical to DR for seed 1, cells [1, 2, 3]: **PASS**.

## g2 dry (3 cells)

Allowed differences only the two edits above: **PASS**.

| cell | g1 identical | g2 diff ok | DR_noex g2 sha16 |
|---:|---|---|---|
| 1 | True | True | `cff4fdb14dd84512` |
| 2 | True | True | `f59ac0a024c9117b` |
| 3 | True | True | `c50afc386f49b7ac` |

## Cache / runtime

- Fresh empty `runs/life_distributed/cache_DR_noex/`; no reuse of `cache_DR`.
- Dry g2 inputs: `runs/life_distributed/gate_dry/seed1_DR_noex_cell{1,2,3}_g2.input.txt`
  (for masked runtime gate at seed-1 after g2, before g3).
- Fail if any g≥2 has 0 live requests.

## Per-cell detail

```json
{
  "1": {
    "g1_byte_identical": true,
    "g1_sha_DR": "dbafe521c23c4c24",
    "g1_sha_DR_noex": "dbafe521c23c4c24",
    "g2_diff_ok": true,
    "g2_classify": {
      "ok": true,
      "ok_sees": true,
      "ok_examples": true,
      "n_opcodes": 2,
      "extras": []
    },
    "g2_sha_DR_noex": "cff4fdb14dd84512",
    "dry_input": "runs/life_distributed/gate_dry/seed1_DR_noex_cell1_g2.input.txt"
  },
  "2": {
    "g1_byte_identical": true,
    "g1_sha_DR": "c81d8bc90b8c2b6f",
    "g1_sha_DR_noex": "c81d8bc90b8c2b6f",
    "g2_diff_ok": true,
    "g2_classify": {
      "ok": true,
      "ok_sees": true,
      "ok_examples": true,
      "n_opcodes": 2,
      "extras": []
    },
    "g2_sha_DR_noex": "f59ac0a024c9117b",
    "dry_input": "runs/life_distributed/gate_dry/seed1_DR_noex_cell2_g2.input.txt"
  },
  "3": {
    "g1_byte_identical": true,
    "g1_sha_DR": "96fbdb1b8594a94d",
    "g1_sha_DR_noex": "96fbdb1b8594a94d",
    "g2_diff_ok": true,
    "g2_classify": {
      "ok": true,
      "ok_sees": true,
      "ok_examples": true,
      "n_opcodes": 2,
      "extras": []
    },
    "g2_sha_DR_noex": "c50afc386f49b7ac",
    "dry_input": "runs/life_distributed/gate_dry/seed1_DR_noex_cell3_g2.input.txt"
  }
}
```
