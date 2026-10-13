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

**Nothing else.** DC → DCs: same set. DR vs DC: identical prompt text (API/decoding only).

### Memory line (all arms)

```
# g1
Previous step: none.

# g≥2
Previous step: rule='<rule held at g−1>' published=<yes|no>.
```

No `answer=`, no `correct=` anywhere in any prompt.

## Channel filter (engine)

Published text is delivered only if it exactly matches a catalog rule description in the
canonical `say` format; otherwise the neighbour slot is empty. Startup assert: every non-empty
inbox `say` is in the catalog. Dropped publishes logged per arm×seed for the readout.

## Dry-render

**Pending** — append g2 line diffs for cells {1,2,3} seed 1 once
`runs/run_life_distributed.py` (or equivalent) can render. Gate PASS requires those diffs to
match the tables above. No Phase 1 API until that append lands.
