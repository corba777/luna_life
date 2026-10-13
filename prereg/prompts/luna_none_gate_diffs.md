# Luna none (An) gate diffs

**Task:** `TASK_LIFE_LUNA_NONE.md`. Seed 1, cells [1, 2, 3] (non-source).

Startup asserts (dry): channel on; 4 sources; An `reasoning.effort=none`; B `reasoning.effort=medium`; no reasoning text in schema/instructions.

`catalog_digest=436f4301513fbb20` · model=`gpt-6-luna` · max_output_tokens=8192.

## An vs B (must PASS)

Request body = Responses `complete_structured` payload. Allowed difference: only `reasoning.effort` (`none` vs `medium`). Prompt `input` and `text` format must be byte-identical.

### cell 1

**PASS** — prompt_sha256=`17ab87ef7277239b94416738e45156f40d469318f48bff04f60b795609ba7407` · An_payload_sha256=`4b82bfa4b1d754ee84503be2f48946b6d923e80db50bc1884b3054b2bd29b82d` · B_payload_sha256=`c6b89aa388ebf2b449d03f71441d481806e0b4cf6b56aae9f81b0f017d2eeddf`.

```diff
# input / text / model / max_output_tokens: identical
-  "reasoning": {"effort": "medium"}
+  "reasoning": {"effort": "none"}
```

### cell 2

**PASS** — prompt_sha256=`ae0569600fd5c14eecb2a09ce9cfde8fa5beffc8323a6b402d457912be41e583` · An_payload_sha256=`00ab91ad167c223eb1b129a78ba280603df3ef3dba470f547b2d3b4211c35600` · B_payload_sha256=`12a731a889a0d9e1f6b4842335491f66d542ea209abe155b868ad7337316ef11`.

```diff
# input / text / model / max_output_tokens: identical
-  "reasoning": {"effort": "medium"}
+  "reasoning": {"effort": "none"}
```

### cell 3

**PASS** — prompt_sha256=`7d0b18a27c9c020da3a3601835f11a2ed6fa49e7f8f0d80a5f82270547a23f18` · An_payload_sha256=`806555ad0b2b6bebc0ae981eb4b0541759c124410ca9c81b6f78466ccc70857d` · B_payload_sha256=`56868a955ca82f68739cdc429b4d33c197b4a49033b1d47b3448734fecfea376`.

```diff
# input / text / model / max_output_tokens: identical
-  "reasoning": {"effort": "medium"}
+  "reasoning": {"effort": "none"}
```

## An vs Ca (listed, not a failure)

Same seed/cells/history as above. State text is identical; differences are Responses vs Decisions output instruction and option rendering only.

State text: identical (An Responses `input` prefix == Ca Decisions `state`).

Output instruction — Responses (An/B):
```
Decide for this cell now.

Return a single JSON object and nothing else with:
- inferred_rule: exactly one catalog key (R000…) for the hidden transformation.
- communication: either {"kind":"silence"} or
  {"kind":"publish","signal":<integer 0-7>}.
  If you publish, the named rule on the board is your inferred_rule.

Choose a catalog key even if unsure. Do not invent keys. Do not return reasoning text.
```

Output instruction — Decisions rule question (Ca):
```
Which is the hidden transformation for this epoch?
```

Option rendering — Responses: keyed catalog block in the prompt (`R000: <description>` …) + JSON-schema enum over catalog keys; one structured object `{inferred_rule, communication}`.

Option rendering — Decisions: catalog descriptions as choice `criteria` on three separate questions (rule / communication / signal); P=4 option-order average; decode=argmax for Ca; communication criteria={"silence": "stay silent this generation", "publish": "publish one message this generation"}; signal instructions=`If this cell publishes, which signal does the message carry?`; signal values=[0, 1, 2, 3, 4, 5, 6, 7].

Cell 1 sample: Decisions n_criteria(rule)=101; Responses prompt chars=5294; state chars=1712.

### Per-cell state equality

- cell 1: state identical = **True** (1712 chars)
- cell 2: state identical = **True** (1727 chars)
- cell 3: state identical = **True** (1718 chars)

## Verdict

**PASS**
