# Local reasoning gate (TASK_LIFE_LOCAL_REASONING)

**Status:** PASS — 2026-10-15T02:55:48.045892+00:00
0 API / 0 GPU. Luna DR/DRs via `DistCompleter`; DR-S/DRs-S = locked text edits only.

## Locked replacement strings

**Constitution / state output line (DR and DRs):**

```
Output a single JSON object and nothing else.
```

→

```
Think step by step, then end with a single JSON object with the same fields.
```

**Decision instructions block** (`life_verify.v1b.luna_cells.RESPONSES_DECISION_INSTRUCTIONS`):

```
Decide for this cell now.

Return a single JSON object and nothing else with:
- inferred_rule: exactly one catalog key (R000…) for the hidden transformation.
- communication: either {"kind":"silence"} or
  {"kind":"publish","signal":<integer 0-7>}.
  If you publish, the named rule on the board is your inferred_rule.

Choose a catalog key even if unsure. Do not invent keys. Do not return reasoning text.
```

→

```
Decide for this cell now.

Think step by step, then end with a single JSON object with the same fields:
- inferred_rule: exactly one catalog key (R000…) for the hidden transformation.
- communication: either {"kind":"silence"} or
  {"kind":"publish","signal":<integer 0-7>}.
  If you publish, the named rule on the board is your inferred_rule.

Choose a catalog key even if unsure. Do not invent keys.
```

Nothing else may differ in the text payload (world, sees, publish, examples,
memory, inbox, query, catalog multiset, generation numbers).

## Request parameters (not in text)

- Luna: Responses API with `json_schema` / structured output.
- Local (SPADE-4B): no schema constraint from the first token; parse the final
  JSON object strictly; one re-sample on parse failure, then `unsolved`.

## Dry render (seed 1, cells 1–3, g1 and g2)

Transform-only diffs: **PASS**.

| arm | cell | g1 ok | g2 ok | local g2 sha16 |
|---|---:|---|---|---|
| DR_S | 1 | True | True | `0c78717bd06550b7` |
| DR_S | 2 | True | True | `ed71f904fcc6f078` |
| DR_S | 3 | True | True | `9f4f58e492fec5bd` |
| DRs_S | 1 | True | True | `1ee9481c409a58cd` |
| DRs_S | 2 | True | True | `afc21a82969b4ecd` |
| DRs_S | 3 | True | True | `6c4dfc4a7df53959` |

## Cache / runtime (at launch)

- Fresh empty `runs/life_local_reasoning/cache_{DR_S,DRs_S}/`.
- Runtime masked check at g2 of world 1 before any g3 request.
- Fail if invalid + truncated > 10% in any generation.

Artifact: `runs/life_local_reasoning/local_reasoning_gate.json` (`pass=true`).

