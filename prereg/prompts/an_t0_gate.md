# An-T0 gate (`TASK_LIFE_AN_T0.md`)

**Status:** locked before spend. Runtime Step 0 / Step 1 fill the result sections below
after the Decisions repeat check (`runs/life_decisions_repeat/repeat.ok`).

## 1. Expected payload diff (An-T0 vs An)

Comparison arm: An (`LunaResponsesClient.complete_structured`, `effort=none`).

Allowed difference in the request body: **only** the presence of

```json
"temperature": 0
```

Everything else byte-identical: `model`, `input`, `reasoning.effort`, `max_output_tokens`,
`text` (json_schema format). `top_p` remains omitted in both arms.

Dry-render (seed 1, cell 1, g2): shared fields identical = **True**;
temperature-only diff = **True**. An sha `d8adee9b660f4951…`;
T0 sha `1a20593a646074cf…`.

## 2. Startup asserts

- model request string starts with `gpt-6-luna`
- `reasoning.effort = "none"` on every call
- no reasoning text requested or stored
- cache key includes `temperature` (null when omitted)

## 3. Responses API reference — `temperature` (verbatim)

> optional number or null. What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic. We generally recommend altering this or top_p but not both.

- min 0, max 2
- **No default stated** in the API reference
- **No note** on reasoning models or `effort`

Fact for An (when fields are omitted): **no temperature/top_p sent; default not stated in
the API reference.**

## Payload dry-render

```json
{
  "seed": 1,
  "cell": 1,
  "order_seed": 2071566886,
  "prompt_chars": 5296,
  "prompt_sha256": "6928547d835e9132240873df4b55b7674d4088137a5501502931d6ca0f008879",
  "an_request_sha256": "d8adee9b660f4951ae61d650c064b93141b972d1b449ad2aa36d16b74b730b2c",
  "t0_request_sha256": "1a20593a646074cf035967074c8bae812003d9021841da2279792bd7b9fc0d8a",
  "only_in_t0": [
    "temperature"
  ],
  "only_in_an": [],
  "shared_fields_identical": true,
  "temperature_only_diff": true
}
```

**Gate verdict: PASS**

## Step 0 — Feasibility (runtime)

_Pending._

## Step 1 — Honour 5× repeats (runtime)

_Pending._
