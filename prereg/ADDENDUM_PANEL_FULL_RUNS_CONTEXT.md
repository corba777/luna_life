# Addendum — server context length for the local full runs

**Status:** locked 2026-10-24, after the dry build. Parent: `AMENDMENT_PANEL_FULL_RUNS.md` (locked).
Local and pre-approved. No local full-run call is made before this file is committed as locked.

## Why

W1-spark-none-all stopped at round 2 with HTTP 400. The rendered input was 4,334 tokens, and the
completion cap is 32,768. Their sum is 37,102, which exceeds the server's `--context-length 36864`.
That value is the wave-1 `CONTEXT` for every model. It is a serving limit, not a model limit:

- Spark-X2.6-4B: `max_position_embeddings` 1,048,576, no `rope_scaling`.
- gpt-oss-20b: 131,072, with static YaRN factor 32.

The finished Qwen world-1 `all` histories do not bound the input. Their largest rendered Spark input
is 4,145, but the failing call was 4,334. Each model's own history sets how many lines reach an
`all` inbox, so a bound has to come from the prompt builder, not from another model's run.

## Change

1. **Context length.** Both local full-run servers (Spark-none and gpt-oss-20b, `all` and lattice)
   start with `--context-length C`. C is the smallest of 40,960, 49,152 and 65,536 that satisfies
   C ≥ I_max + 32,768 + 512. The value is 40,960 for both models. Spark-none needs 38,219 and
   gpt-oss-20b needs 37,469.
2. **I_max** is the rendered input, in each model's own tokens, of the largest prompt the Stage 1
   builder can produce for world 1 under `all`: all 99 other cells publish, each with the longest
   rule description in the catalog and the longest signal field. Spark-none I_max is 4,939.
   gpt-oss-20b I_max is 4,189. Both counts are the round-20 prompt for cell 9. The published text
   is `rotate_left(3);shift_symbols(7)` (31 bytes, tied for the longest catalog description) and
   the signal is 7. Signals 0–7 all render as one digit.
3. **Runtime invariant.** Before every call, the runner checks that input_tokens + max_tokens ≤ C,
   using the server's own count. If the check fails, the run stops with `run.aborted`. Nothing is
   truncated, retried with a smaller cap, or skipped.
4. **Unchanged:** decoding (temperature, top_p, top_k, max_tokens 32,768, thinking or effort
   settings), the model revisions, the prompt builder, scoring, the locked predictions F4 and the
   W1-oss20 readout. `--context-length` sets how much fits. It does not change the output for a
   prompt that fits.

## The partial Spark-none-all run

The 100 round-1 calls in `runs/model_panel/full/W1-spark-none-all/cache_r1/` were made with the same
prompts and decoding, and with round-1 inputs of about 2,069 tokens. They fit at 36,864, and they
are kept. The rerun resumes from that cache: round 1 hits the cache, and round 2 onward is new. The
old `run.aborted` is kept beside the new run's files as `run.aborted.context36864` and named in the
readout.

## Cache key

`_cache_key` carries the panel id, effort, prompt, draw, catalog digest, structured flag and
temperature. It has no arm, topology or replicate field. Arms are kept apart because each arm writes
to `runs/model_panel/full/<arm>/cache_r<replicate>/`. That separation is a runtime invariant from
now on: the runner refuses to start if the cache directory path does not contain its own arm id and
replicate.

## Gates (live calls refused, before the lock)

- I_max and C for each model, with the worst-case prompt rendered and counted by the model's chat
  template: Spark-none 4,939 and 40,960; gpt-oss-20b 4,189 and 40,960. The template count matches
  `prompt_tokens` on stored calls; the prep check showed 24 of 24 for both models.
- The runtime check from item 3 refuses the 4,334 + 32,768 case at C = 36,864 and accepts it at the
  new C, shown on a fake client.
- The cache-directory invariant refuses a path from another arm, shown on a fake client.
- `--guard-check` and the launch gates: lock free, no model server or other GPU job up.

## Readout

Each full-run readout states C and I_max, and the largest input seen in the run against I_max.
