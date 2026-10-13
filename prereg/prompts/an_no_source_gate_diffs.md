# An0 (0-source) gate diffs

**Task:** `TASK_LIFE_AN_NO_SOURCE.md`. Seed 1, cells [1, 2, 3] (non-former-source). Allowed: inbox content only.

Startup: `SOURCE_IDS == ()` under override; An0 `reasoning.effort=none`; same Responses schema as An; no reasoning text requested or stored.

`catalog_digest=436f4301513fbb20` · model=`gpt-6-luna` · max_output_tokens=8192.

## An0 vs An (must PASS)

Compared: Responses `complete_structured` payload. Non-`input` fields must be byte-identical (`effort=none` both sides). `input` may differ only in inbox lines.

### cell 1

order_seed=2071566886 · An hash=`029a44379c24951b…` · An0 hash=`029a44379c24951b…`

**PASS** — only inbox-related diffs (or none); meta identical.

```diff
(identical)
```

### cell 2

order_seed=3927991992 · An hash=`e5d860cff992ad33…` · An0 hash=`e5d860cff992ad33…`

**PASS** — only inbox-related diffs (or none); meta identical.

```diff
(identical)
```

### cell 3

order_seed=3062914366 · An hash=`90a74a0ffdb59ff7…` · An0 hash=`90a74a0ffdb59ff7…`

**PASS** — only inbox-related diffs (or none); meta identical.

```diff
(identical)
```

## Verdict

**PASS**

