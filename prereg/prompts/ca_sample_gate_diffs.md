# Ca-sample gate diffs

**Task:** `TASK_LIFE_CA_SAMPLE.md`. Seed 1, cells [1, 2, 3].

Startup (runner): 4 sources; channel on; k=0; decode=`sample`; draws logged.

## An sampling parameters (from logged An / client)

Source: `openai_responses_luna.LunaResponsesClient.complete` request body and `runs/life_luna_none/cache_An` (20 rows inspected).

Request body fields actually sent:

```
model, input, reasoning: {effort}, max_output_tokens, text: {format: json_schema…}
```

- `temperature` in payload construction: **False**
- `top_p` in payload construction: **False**
- cache rows with `temperature` / `top_p` keys: **0** / **0**
- client `draw` argument: cache-key only; **not** passed to the API

When omitted, the Responses API applies defaults **temperature = 1.0**, **top_p = 1.0**. So An's Life readout is non-greedy sampling at the API default, not a temperature-0 decode. Ca is argmax of P=4-averaged π (zero-temperature readout).

```
payload: dict[str, Any] = {
            "model": self.model,
            "input": prompt,
            "reasoning": {"effort": effort},
            "max_output_tokens": self.max_output_tokens,
        }
        if text_format is not None:
            payload["text"] = text_format
        t0 = time.time()
        body = self._post(payload)
        el
```

## Readout code (only decision change)

Ca and Ca-sample share `LunaDecisionsCompleter` / P=4 averaging / `cache_C`. The only change is `decode='argmax'` → `decode='sample'` in `choose()`:

```python
def choose(dist: Distribution, rng: random.Random, decode: Decode) -> str:
    """One draw per call in both modes, so RNG consumption does not depend on decode."""
    keys = list(dist)
    u = rng.random()
    if decode == "argmax":
        return max(keys, key=lambda k: dist[k])
    total = sum(dist.values())
    acc = 0.0
    for key in keys:
        acc += dist[key] / total
        if u < acc:
            return key
    return keys[-1]
```

RNG: `random.Random(inference_seed(world_seed, generation, cell_id, kind='trajectory', draw=0))` — already committed in `constitutional_life` engine; one `rng.random()` per question so argmax and sample consume the same stream length. No temperature rescaling of π̄.

Historical note: arm `C` in `run_life_reasoning_cells.py` used `decode=sample` before the Ca argmax amendment; Ca-sample is the registered S1–S3 arm with draw diagnostics. Do not substitute C's numbers for this task's readout.

## Ca-sample vs Ca requests (forced identical history)

Dry-render g2 Decisions fingerprints with Ca's logged rule history replayed for both arms. Must be byte-identical (hash equal). Live g1 is expected to hit `cache_C` (same requests as Ca).

- cell 1: hash `1cfb2562b338ce97…` PASS
- cell 2: hash `5846446aba70f285…` PASS
- cell 3: hash `c74e398cb3bb458f…` PASS

## Verdict

**PASS**

```json
{
  "payload_includes_temperature": false,
  "payload_includes_top_p": false,
  "cache_rows_inspected": 20,
  "cache_rows_with_temperature": 0,
  "cache_rows_with_top_p": 0,
  "client_payload_fields": [
    "model",
    "input",
    "reasoning.effort",
    "max_output_tokens",
    "text (structured format)"
  ],
  "not_sent": [
    "temperature",
    "top_p",
    "seed"
  ],
  "api_default_when_omitted": {
    "temperature": 1.0,
    "top_p": 1.0,
    "note": "Responses API default when fields are omitted from the request body"
  },
  "draw_field": "cache-key disambiguator only; not sent to the API"
}
```

