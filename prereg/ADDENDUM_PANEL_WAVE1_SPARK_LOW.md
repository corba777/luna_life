# Addendum to AMENDMENT_PANEL_WAVE1.md — W1-spark-low as the reasoning-on member of the Spark pair

**Status:** locked 2026-10-23, after the content review and after audit items 1 and 5 passed.
Not run. Written 2026-10-22, before the W1-spark-high pilot outcome. It applies only if
W1-spark-high fails its pilot. That pilot failed, so this addendum is in force.

W1-spark-high outcome: not run (pilot failed: 2 truncations at 32768 tokens), 2026-10-22. Failing calls: cell 0: 32768, cell 1: 32768.

## Why

The locked wave-1 amendment pairs W1-spark-none (`enable_thinking: false`) with W1-spark-high (thinking
on, effort `high`, the template default) for R1. It states: "Spark's `low` level is not run." In the
first, interrupted W1-spark-high pilot, 6 of 12 calls stopped at `max_tokens` 32768 (finish reason
`length`). The locked pilot rule stops a run at more than 1 failing call in 20. If W1-spark-high fails
that rule again, the Spark pair has no reasoning-on member, and R1 is scored only in the Qwen pair.
This addendum adds the template's other thinking level, `low`, as the reasoning-on member. It does not
raise `max_tokens` and does not change the prompt.

## The run

| run | model @ revision | reasoning | decoding | source of decoding |
|---|---|---|---|---|
| W1-spark-low | `XHToken/Spark-X2.6-4B` @ `66e3ae7b` | thinking on, effort `low` | 1.0 / 0.95 / top_k −1, as W1-spark-high | card and `generation_config.json` |

Everything else is as W1-spark-high: the same pinned arm64 container
(`sha256:40b02a1d78982c85dda79ade7522b30d8152ee9487d5c075ea7f9134b197d25f`), `--chat-template` from the
card, `--reasoning-parser qwen3`, `--served-model-name spark2.6`, no `--trust-remote-code`, no
`--attention-backend`, mem-fraction 0.6, concurrency 64, context 36864, `max_tokens` 32768. The same
960-prompt fingerprint battery, then class-B 0/8 draws 2–11 from
`runs/model_panel/w1_r1_b08_prompts.json` (1160 calls). Own directory `runs/model_panel/W1-spark-low/`,
own cache, lock, pidfile and watchdog, no auto-relaunch.

**Request body.** As W1-spark-high, except
`chat_template_kwargs` = `{"enable_thinking": true, "reasoning_effort": "low"}`. The pinned template
accepts `reasoning_effort` `high` or `low` when thinking is on and raises on any other value. Against
W1-spark-none (`{"enable_thinking": false}`) the bodies differ only in `chat_template_kwargs`.

**Pilot.** The same 20 round-1 prompts (cells 0–19, outside the battery), run one at a time before the
battery. More than 1 call that fails to parse or is truncated stops the run (locked rule). Under
Artem's go of 2026-10-22, the pilot stops as soon as the second failing call is recorded; the verdict
is the same. The prompt is never changed to fit the model.

**Runtime invariants** (`runs/call_invariants.py`, as for every wave-1 run): live calls equal the
expected prompt count, with no cache hit in a fresh run; each sent message equals its manifest entry
byte for byte at send time; on the first sent request, the body differs from W1-spark-none's first
sent body only in `chat_template_kwargs`. Any violation stops the run with a logged reason.

**Queue position (locked).** After QX-1 and before moore. The live after-panel chain is left as it
is. `runs/queue_w1_spark_low.sh` waits until that chain has exited and `runs/life_dr_qwen/qx1/run.ok`
exists, then starts this run. Moore stays unstarted until this run writes `run.ok` or `run.aborted`.

## R1 for Spark

The locked R1 text is unchanged except for the Spark member. It reads:

- **Spark pair:** W1-spark-none against W1-spark-low.

Same test: one-sided Fisher at α = 0.05 on the class-B 0/8 prefix adoption, reasoning off higher than
reasoning on, on the enlarged filter set (20 cells × 12 draws), with the cell-level sign-flip beside
it. Power is the locked D = 12 table (0.8350 homogeneous at 0.08). W1-spark-high is reported as not
run, with its pilot outcome, and is not part of R1, U1 or U2.

## Pre-stated readings

- **R1 passes for Spark with effort `low`:** reasoning at the lower level already supports the filter
  in this lineage. That the `high` level did not fit 32768 tokens is stated next to it.
- **R1 fails for Spark with effort `low`:** the filter does not depend on low-effort reasoning in this
  lineage. It does not say what `high` would do. The readout says so.
- **W1-spark-low fails its own pilot:** the Spark pair is "not run", and R1 is scored in the Qwen pair
  only, as the locked readings for one pair state.
- **If the design is the cause:** the effort level is a template instruction, not a decoding change.
  A shift between `low` and `high` cannot be read, because `high` has no data. Only none against low
  is read.

## Design audit

1. **Fidelity.** The message content is the same 960 + 200 strings as every wave-1 run (battery sha256
   `1f02f68d0082b24e663a97daee47f18765bd6562afde863080187a35444fd6e6`, filter sha256
   `ab50cef429329e869e7237d1dc851e2bda2343d9e2e16e6aef836d09d93341e7`). Only `chat_template_kwargs`
   differs from W1-spark-none. **Checked 2026-10-23, offline, no server.** One battery prompt
   (5359 bytes) rendered from `runs/model_panel/spark_chat_template.jinja`. The user span equals that
   prompt under `low`, under `high`, and with thinking off. `low` selects `thinking_effort=low`.
   `high` and the template default both select `thinking_effort=high`, and those two renders are
   identical. Thinking off carries no effort line. `reasoning_effort: medium` is rejected by the
   template. The low and high renders differ only by that effort value. Record:
   `runs/model_panel/W1-spark-low/offline_render.json`.
2. **Coverage.** The battery and filter conditions only, as in the locked amendment.
3. **Controls.** W1-spark-none is the reasoning-off control, on the same server build and decoding.
4. **Observability.** The cell sees only its prompt. The effort level is part of the rendered system
   text of the template, not of the prompt.
5. **Gate consistency.** **Checked 2026-10-23.** The spec and body are in
   `runs/run_life_panel_wave1.py`. The dry gate (`--gate`, live calls refused) passed: the body
   differs from W1-spark-none only in `chat_template_kwargs`, those kwargs are
   `{"enable_thinking": true, "reasoning_effort": "low"}`, the invariant self-check passed, and the
   job list is the shared 960-prompt battery plus the 200 filter draws. The runner starts this run
   only when this status line says locked.
6. **Statistical unit.** The source cell, with Fisher on prompts beside it, as in the locked R1.
7. **Pre-stated readings.** Above.
