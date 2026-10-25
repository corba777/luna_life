# Amendment — panel wave 2b: Gemma 4 E4B, Nemotron-3.5-Bolt-E4B, Flint-NVFP4 (battery)

**Status:** locked 2026-10-25, after the dry build in `runs/model_panel/wave2_gate.json`.
No call was made before this lock. The CUDA binary sha256 of llama.cpp b11803 is a pre-pilot gate
and is still pending; that build waits for the queue, and no Flint call is made before the hash is
recorded. The schema grammar check passed on a CPU-only build of the same commit. The basis is
`MODEL_PANEL_PLAN.md`, including the dated addition of 2026-10-25, the class-B 0/8 section of
`runs/model_panel/panel_summary.md`, and `DESIGN_AUDIT_CHECKLIST.md`. All model facts below are taken
from the model cards and registries named, as reported on 2026-10-25.

## Why

Wave 2b adds two axes the panel does not have yet. Each run is the standard battery: the 960 panel
prompts plus the 200 class-B 0/8 filter draws.

- **Same base, different post-training, and thinking on/off within the same weights.** Gemma-4-E4B-it
  and Nemotron-3.5-Bolt-E4B, which NVIDIA post-trained from Gemma-4-E4B-it. Both have
  `enable_thinking`. This gives two within-weights reasoning pairs. Spark's pair could not be run,
  because both of its reasoning arms failed their pilots.
- **Large total, small active, reasoning chosen by the model itself.** Flint, a 39.8B MoE with about
  2.5B active parameters and no reasoning switch: the model decides on each turn whether to reason.
  It pairs with gpt-oss-20b. It runs as **Flint-NVFP4**, the quantized GGUF. BF16 needs at least
  141 GB of GPU memory and does not fit this host. Flint-NVFP4 is a quantized model on another
  engine, and the panel table names it that way.

## Arms

| arm | model, revision | engine | reasoning |
|---|---|---|---|
| W2-gemma-off | `google/gemma-4-E4B-it` @ `ee0ef602…` | vLLM | `enable_thinking` false |
| W2-gemma-on | same | vLLM | `enable_thinking` true |
| W2-nemo-off | `nvidia/NVIDIA-Nemotron-3.5-Bolt-E4B-BF16` @ `49843eed…` | vLLM | `enable_thinking` false |
| W2-nemo-on | same | vLLM | `enable_thinking` true, no thinking budget |
| W2-flint | `RecursiveSI/flint-nvfp4-gguf` @ `6ec43e19…` | llama.cpp b11803 | the model's own choice |

**Engine.** The four Gemma-family arms use the card-pinned `vllm/vllm-openai:v0.31.0`, linux/arm64
`sha256:3f7dd5b7…`, with `--reasoning-parser gemma4`. The Nemotron card pins this engine, and
Nemotron's architecture is `Gemma4ForConditionalGeneration`. Serving both models of the pair on one
engine keeps the engine out of the post-training contrast. Flint uses llama.cpp release b11803
(commit `a37cc46104eb50900d5ab4a9ba02a0abdac039db`). The CUDA build is
`cmake -B build -DGGML_CUDA=ON` and `cmake --build build --config Release`. Its binary sha256 is a
pre-pilot gate and is still pending: that build waits for the queue. The schema check below uses a
separate CPU build (`-DGGML_CUDA=OFF`) of the same commit. The engines differ from the SGLang used so far. The protocol fixes the prompt and the
card decoding, not the server. The sampler gate below applies to every engine.

**Decoding, from the cards.**
- Gemma: temperature 1.0, top_p 0.95, top_k 64 (https://huggingface.co/google/gemma-4-E4B-it).
- Nemotron: temperature 1.0, top_p 0.95 (https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Bolt-E4B-BF16).
  The card does not name top_k. The pinned `generation_config.json`, which is the developer's shipped
  default, sets top_k 64. That value is used. It equals Gemma's, so the pair differs in post-training
  and not in sampling.
- Flint: temperature 1.0, top_p 0.95, top_k 20 (https://huggingface.co/RecursiveSI/flint).
- max_tokens 32,768 for every arm, as in the panel.
- Every engine sampler that the card does not name is set explicitly to neutral, and the request
  body quotes it. vLLM 0.31.0 defaults `watermarking` to true, `min_p` to 0, both penalties to 0
  and `repetition_penalty` to 1. Each body sets watermarking false and quotes those three at the
  neutral values. Gemma and Nemotron both set `top_k` 64. llama.cpp b11803 defaults `min_p` to
  0.05, temperature to 0.80 and `top_k` to 40. The Flint body sets `min_p` 0, temperature 1.0,
  `top_k` 20, `repeat_penalty` 1, `frequency_penalty` 0, `presence_penalty` 0, `dry_multiplier` 0,
  `xtc_probability` 0, `typical_p` 1, `top_n_sigma` -1, `dynatemp_range` 0 and `mirostat` 0. No
  body carries a seed or a thinking budget. The bodies are in `runs/model_panel/wave2_gate.json`.
  An engine default is never left implicit.
- Nemotron's thinking budget is not used. The card's budget is a two-call client procedure, which
  would make a different agent. With `enable_thinking` true, a normal request has no budget, which
  matches the panel protocol.

**Context.** The engine context is 40,960, the panel C. Every model's native context is larger: 64K,
128K and 256K. The configs say the same thing: Nemotron 65,536, Gemma 131,072, Flint 262,144.
The battery input maximum, in each model's chat template, is Gemma 2,332 with thinking and 2,325
without, Nemotron the same 2,332 and 2,325, and Flint 1,844. Each plus 32,768 is below 40,960.
Flint's count uses the tokenizer in `RecursiveSI/flint`. The
pre-call check counts locally with the model's chat template, loaded once before the pool, and logs
the count against the returned `prompt_tokens`, as for W1-oss20.

## Gates (live calls refused unless stated)

1. **Sampler gate** (the standard gate since 2026-10-25), live on each engine and model before its
   pilot. One round-1 lattice prompt is sent 64 times in one concurrent batch, three times. The same
   prompt is sent 64 times serially. The cutoff is the pooled batched collision against 20,000 draws
   from the serial answers, one-sided p < 0.001. Failing it stops that model.
2. **Reasoning before JSON**, live, on the 20 pilot calls. In every reasoning arm (`-on` arms; Flint
   where it reasons), the JSON constraint must not apply before the reasoning ends. The check: the
   `-on` arms return a non-empty reasoning field on at least 18 of 20 pilot calls, and the `-off` arms
   return an empty one on all 20. For Flint, the reasoning share is reported. A constraint that
   applies from the first token makes a reasoning arm one-pass. That stops the arm until it is fixed
   and re-gated.
3. **Schema enforcement** (Flint, llama.cpp). llama.cpp skips unsupported schema features silently.
   The panel schema (`life_cell_decision_v2`: the `R000`–`R100` enum, the silence/publish union, signal
   0–7) is converted to GBNF. The converter must keep the enum, the union and the signal range; this
   is shown on the generated grammar. On a fake sampler, the grammar must reject each of the
   following:
   - an out-of-enum key;
   - signal 8;
   - an extra property.
   CPU-only check, 2026-10-25, commit `a37cc46104eb50900d5ab4a9ba02a0abdac039db`, built with
   `-DGGML_CUDA=OFF` under `nice -n 19`. The grammar is `runs/model_panel/wave2_flint_grammar.gbnf`.
   It keeps `R000` through `R100` and does not contain `R101`. The union is
   `communication-0-kind ::= "\"silence\""` and `communication-1-kind ::= "\"publish\""`. The signal
   range is `("0" | "1" | "2" | "3" | "4" | "5" | "6" | "7")`. A silence object and a publish with
   signal 7 match. `R101`, signal 8, and an extra property do not. Report:
   `runs/model_panel/wave2_flint_schema_check.json`.
4. **Answer path.** The stored row carries the final text, the reasoning text (all three models are
   open, so this is allowed) and `finish_reason`. A truncation counts as a failure.
5. **Pilot:** 20 calls outside the battery, with the panel rule (more than 1 failure stops the model).
   The Flint card asks for at least 32,768 output tokens on hard problems. If its pilot truncates
   above the rule, Flint is "not run", as Spark-low was.
6. **Memory and order:** one model is served at a time, with nothing else on the GPU. The launcher
   traps exit and stops its server.

## Measures (per arm)

- The panel fingerprints (S, L, ally, count, top, filter), and U1 and U2.
- **Checking:** class-B 0/8 fit, with the panel hull, and its composition.
- **Conformity:** prefix / (prefix + other non-fitting).
- **Reasoning length:** the median and 95th percentile of reasoning tokens. For Flint, the share of
  calls with a reasoning span, and fit by whether a span was written.
- Truncations and parse failures per cell.

## Predictions (locked)

The unit is the class-B source cell (20 cells at 0/8, both draws pooled per cell). One-sided
cell-level sign-flip, α = 0.05. Wilson and Fisher go beside it and are not scored.

- **P1g:** fit(W2-gemma-on) > fit(W2-gemma-off).
- **P1n:** fit(W2-nemo-on) > fit(W2-nemo-off).

Basis: the two within-lineage reasoning contrasts already measured on this slice, Luna medium
against none (40/40 against 9/40) and Qwen Thinking against Instruct (37/40 against 12/40).

- **U1 and U2** for every arm, counted in the panel as for every model.
- **Not predicted:**
  - Nemotron against Gemma in the same mode, which is the post-training contrast. It is reported
    descriptively for fit, conformity and every fingerprint, with the hull classification.
  - Flint. Its fit by reasoning span is observational, because the model chooses the span, and is
    descriptive.

## Pre-stated readings

- **P1g and P1n pass:** the reasoning → checking link holds in a third and fourth lineage, within the
  same weights. With Luna and Qwen, it is then a panel-wide statement for world 3.
- **One of them fails:** the link is lineage-specific in that case. The readout says which model and
  gives its off-arm fit. A high off-arm fit means a one-pass checker, and that triggers its full run.
- **Nemotron differs from Gemma in conformity or fit, in the same mode:** post-training on the same
  base moves the trait. This is the first panel evidence that the trait is trained, not given by the
  architecture.
- **Flint:** a high fit with a low reasoning share would make Flint the first model to check without
  explicit reasoning. That is read against W2-tacit-adapt in wave 2a.
- **If the design is the cause:** the engines differ from the earlier SGLang arms, and the sampler and
  reasoning gates are there to catch engine effects. Flint-NVFP4 is quantized, and no claim is made
  about BF16 Flint.

## Full-run triggers

As in the panel plan: a U1 failure, S or ally classified "neither", or the reasoning-off member of a
pair whose two fingerprints differ in class. Each full run gets its own amendment.

## Design audit

1. **Fidelity.** The message content is byte-identical to the panel battery. Only each model's chat
   template differs. The thinking switch is the documented `enable_thinking`. The decoding is quoted
   from the cards. Every other sampler is set neutral explicitly.
2. **Coverage.** The battery (world-3 source cells). The world restriction in `panel_summary.md`
   applies.
3. **Controls.** Each off arm is the control for its on arm, on the same weights and engine. Gemma is
   the base control for Nemotron.
4. **Observability.** Final answer, reasoning text and finish reason are stored per call.
5. **Gate consistency.** Gate 3 ran with live calls refused, on the CPU build. Gate 4 is the stored
   answer path and is checked on the pilot. Gates 1, 2 and 5 are live and run before the battery.
   The CUDA binary hash is the remaining pre-pilot gate.
6. **Statistical unit.** 20 class-B source cells for P1. This is small, and stated. Power at an off
   fit of 0.30 and an on fit of 0.85 is 0.992, from 2000 simulations at the observed
   per-cell spread. On this slice the Instruct draws agree inside every cell (ICC 1.0), and the
   Thinking draws have ICC −0.056, so the on arm is drawn independently. The same rates with both
   arms independent give 1.000. Numpy Generator seed 0 for the ICC run and seed 2 for the
   independent run.
7. **Pre-stated readings.** Above.

## Queue

After wave 2a's AnyJev arms. The order is W2-gemma-off, W2-gemma-on, W2-nemo-off, W2-nemo-on, then
W2-flint. Image and binary pulls are logged, and none is removed without a log line.