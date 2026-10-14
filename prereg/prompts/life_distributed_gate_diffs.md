# Distributed-evidence gate diffs (before Phase 1 API)

Task: `TASK_LIFE_DISTRIBUTED.md`. World audit: `runs/life_distributed/world_audit.json` (5/5 ok).

This file locks **DESIGN_CHECKLIST item 1** (expected diffs). Full dry-render of request
payloads (item 2) runs once the no-feedback runner exists and **before the first API call**
of Phase 1; results append below under “Dry-render”.

## Constitution vs v1b (required)

Shared-transformation / different-examples sentence is **kept** from `_WORLD`. Exact diffs:

| piece | v1b | distributed |
|---|---|---|
| shared transformation + different examples | present in `_WORLD` | **kept** (required) |
| “A correct answer is the hidden transformation applied to your query.” | present | **removed** |
| memory in “You see …” | “one-step memory of your last answer” | “one-step memory of the rule you held last generation (and whether you published it)” |
| feedback | implied by memory `correct=` | “You are not told whether your last rule was correct.” |
| messages | may name a transformation | same + “they never carry private examples.” |

### Final constitution (channel on, Responses / JSON)

```
You are one cell among 100 on a wrapping 10×10 grid.

Each cell has its own private task for this epoch: a hidden transformation of 4-symbol strings over A–H. Every cell in the epoch has the same hidden transformation, but different private examples and a different query each generation. There is no shared score.

You see your private examples, your current query, a one-step memory of the rule you held last generation (and whether you published it), and eight message slots from other cells. Unused slots are empty. You are not told whether your last rule was correct.

You may publish at most one message this generation, or stay silent. A message has an integer signal 0–7 and a short text (at most 96 UTF-8 bytes). Published messages become visible only from the next generation, and only to cells allowed to see them. Your task_answer and inferred_rule are not shown to other cells. Messages may name a transformation; they never carry private examples.

inferred_rule is required. Write the hidden transformation as you currently understand it.

Output a single JSON object and nothing else.
```

Startup assert: constitution contains “same hidden transformation, but different private examples”.

## Arm diffs

### DR → DRs (channel on → off)

| block | DR | DRs |
|---|---|---|
| constitution “You see …” / publish | channel-on paragraphs above | no-channel pair (no inbox; “You cannot send or receive messages”); same world sentence; no-feedback memory |
| inbox | present | **absent** |
| memory | `Previous step: rule='…' published=yes\|no.` | same schema; value only |
| `correct=` | absent | absent |

**Nothing else.** DC → DCs: same set. DR vs DC: pre-catalog state identical; allowed diffs = JSON/typed output-format + option rendering (`AMENDMENT_DISTRIBUTED_DR_DC_DIFF.md`).

### Memory line (all arms)

```
# g1
Previous step: none.

# g≥2
Previous step: rule='<rule held at g−1>' published=<yes|no>.
```

No `answer=`, no `correct=` anywhere in any prompt.

## Channel filter (engine)

Published text is delivered if it **parses** to a catalog rule (normalize → `parse_program` → `canonicalize`); neighbour sees the canonical `description()`. Otherwise the slot is empty. See `AMENDMENT_DISTRIBUTED_DR_DC_DIFF.md`. Startup assert: every non-empty
inbox `say` is in the catalog. Dropped publishes logged per arm×seed for the readout.

## Dry-render

**Done** (no API) — seed 1, cells [1, 2, 3], arms ['DR', 'DRs', 'DRo', 'DC', 'DCs'].
Review bundle: `runs/life_distributed/gate_dry_review.md`; raw prompts under `runs/life_distributed/gate_dry/`.

- World audit regenerated: n_ok=5/5, chance=0.2514, n_draws={'1': 1, '2': 1, '3': 1, '4': 28, '5': 1}.
- S_c checks seed1: min≥3 / ∩={P_e} / 1-op≥40% all **PASS**.
- Channel drop log: dropped=9 / planted=21 (drop_share=0.429; see `gate_dry/drop_log.json`).
- Canonicalize filter selftest: **PASS** (`gate_dry/filter_selftest.json`).
- Constitution diffs: DR/DRs/DCs/DRo artifacts under `gate_dry/`.
- DR vs DC (amendment): **PASS** (`gate_dry/DR_vs_DC_pre_catalog.diff`).
- Silent arms: memory `published=no` assert **PASS**.

Prompt hashes:

| arm | cell1 | cell2 | cell3 |
|---|---|---|---|
| DR | `880091c043961b6f` | `9e438be15aec875e` | `deaf83c8ee8dd332` |
| DRs | `7b837973d2cdcf2c` | `9f9fae96a658ca0e` | `535e1c5b29af05a9` |
| DRo | `6412fa6f8c2e8832` | `d9a8fb9af4027267` | `94c5e206a6018b1d` |
| DC | `b8b896019b563bb2` | `72cab152a771ac86` | `e50c42ab17620f40` |
| DCs | `9fc9682fbb9421d7` | `0e4f730c1ec9c36c` | `4343da069f05f443` |

Dry-render accepted; `ALLOW_PHASE1` released after Ca-sample close. Phase 1 runner must
enforce §5 startup asserts before the first API call (no auto-launch from this file).

