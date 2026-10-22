# Amendment — model panel, wave 1: gpt-oss-20b, Qwen3-4B-Instruct-2507, Spark-X2.6-4B

**Status:** locked. Local and approved (`MODEL_PANEL_PLAN.md`). Each model
runs only after its own pilot passes. This file is locked before the first wave-1 call, and after the
gpt-oss-120b battery, so wave 1 does not depend on any wave-1 result. Values marked **[dry build]** are
filled in before the lock. Facts come from `runs/model_panel/wave1_facts.md`.

## Runs

Every run is the 960-prompt fingerprint battery (the redo Part 0b prompts, the same strings as QI-1m,
plus QI-1b) under the panel protocol: byte-identical
message content, the pinned revision, max_tokens 32768, no seed, the existing parser, and a 20-call
pilot outside the battery.

| run | model @ revision | reasoning | decoding | source of decoding |
|---|---|---|---|---|
| W1-oss20 | `openai/gpt-oss-20b` @ `6cee5e81` | `Reasoning: medium` | temperature 1.0, top_p 1.0 | OpenAI's gpt-oss repository, "Recommended Sampling Parameters": "We recommend sampling with `temperature=1.0` and `top_p=1.0`." https://github.com/openai/gpt-oss/blob/d21f34ec3c1ede813adfbd83f07d2ad2eec7ff02/README.md#recommended-sampling-parameters |
| W1-qi-nat | `Qwen/Qwen3-4B-Instruct-2507` @ `cdbee75f` | off (the model has no thinking mode) | 0.7 / 0.8 / top_k 20 / min_p 0 | card, Best Practices |
| W1-qi-match | same | off | 0.6 / 0.95 / top_k 20 / min_p 0 | the Qwen3-4B-Thinking-2507 Stage 1 settings, to match decoding within the pair |
| W1-spark-high | `XHToken/Spark-X2.6-4B` @ `66e3ae7b` | thinking on, effort `high` (the template default) | 1.0 / 0.95 / top_k −1 | card and `generation_config.json` |
| W1-spark-none | same | `enable_thinking: false` | same as W1-spark-high | same |

Spark's `low` level is not run.

## Serving

- **gpt-oss-20b and Qwen-Instruct:** the installed SGLang 0.5.18, which supports both natively.
- **Spark:** the installed SGLang has no Spark architecture. The model's own SGLang example uses a
  nightly image and no `--trust-remote-code`, which points to native support in that build. Spark
  runs in that container, pinned by image digest, never by tag. The tag
  `lmsysorg/sglang:nightly-dev-cu13-20260827-20621aa1` is the OCI index
  `sha256:9ca30410d6280c09c8e6804525b8ba0ef598c456044e758819046f8ef3037020`. That index has a
  `linux/arm64` manifest, `sha256:40b02a1d78982c85dda79ade7522b30d8152ee9487d5c075ea7f9134b197d25f`.
  This host is aarch64, so the pull is `--platform linux/arm64` and selects that manifest. The container
  is pinned to the arm64 digest, not to the tag. It uses the card's `--chat-template` and
  `--reasoning-parser qwen3`. The readout states that Spark was served by a different SGLang build.
  The fallback is the vLLM or Transformers path with `trust_remote_code`, which executes the two
  hashed files in the facts table. That path is **not** taken without Artem's explicit go. If the
  pinned container cannot run, Spark is reported as "not run" and the queue goes on.

## Queue order

1. W1-oss20, right after the gpt-oss-120b battery and QI-1b, on the same server with the weights
   swapped.
2. W1-qi-nat.
3. W1-qi-match. After its 960-prompt battery, class-B 0/8 draws 2–11.
4. W1-r1-think, `Qwen/Qwen3-4B-Thinking-2507` on the Stage 1 settings, class-B 0/8 only. Draws 0
   and 1 are the QI-1 records. It runs only the missing draws.
5. W1-spark-high. After its 960-prompt battery, class-B 0/8 draws 2–11.
6. W1-spark-none. After its 960-prompt battery, class-B 0/8 draws 2–11.

Then the Qwen queue resumes at QI-2. Every run has its own cache and lock, starts with the v2
watchdog, and never relaunches automatically.

## Predictions (locked)

Scored as in the panel plan: U1 and U2 for every wave-1 run, counted per model. Within each pair the
rest of the fingerprint is classified descriptively against the Luna redo references and the Qwen
QI-1m rates, using the hull rule. QI-1m rates, 2026-10-22: S = -0.050, L = 0.025, top = 0.675. The file stays a draft until its own lock. The class-A rates in `MODEL_PANEL_PLAN.md` were scored
on the QI-1 top-block prompts. They are not the reference. Ally and count stay the QI-1b rates, which
are already on the redo prompts. U1 and R1 use class-B 0/8, where the two builders emit the same prompt,
so the QI-1 prefix rate 1/40 is a comparison on identical inputs.

**R1 (reasoning helps the own-example filter).** Class-B prefix adoption under 0/8 is higher with
reasoning off than with reasoning on, within each pair:
- **Qwen pair:** W1-qi-match against Qwen3-4B-Thinking-2507 QI-1 (1/40). This is the primary
  comparison, because decoding is matched; W1-qi-nat is reported beside it.
- **Spark pair:** W1-spark-none against W1-spark-high.

The test is a one-sided Fisher at α = 0.05 for each pair. A cell-level paired sign-flip test sits
beside it, valid because both members use the same 20 source cells. Basis: Part I. Luna's filter
failures were errors in checking the rule against the example, and reasoning is extra computation
spent on exactly that check.

**Not predicted:** the direction of S, L, ally and count between reasoning on and off. Luna (reasoning,
threshold) and Qwen-Thinking (reasoning, no threshold) already show that reasoning does not by itself
fix the social rule. The pairs measure what it changes.

## Pre-stated readings

- **R1 passes in both pairs:** reasoning supports the filter in two lineages. The model-agnostic
  filter claim (U1) is then a claim about reasoning models. If the reasoning-off members fail U1, the
  package says so.
- **R1 passes in one pair:** the effect is specific to that lineage, and it is stated per pair.
- **R1 fails in both pairs:** the filter does not depend on reasoning at this size. It comes from the
  model, not from the extra computation.
- **Fingerprint shifts between pair members** (in class, by the hull rule) are reported as the effect
  of the reasoning mode on that fingerprint. They are descriptive.
- **Qwen native against matched:** if W1-qi-nat and W1-qi-match differ in class on any fingerprint,
  decoding alone moves that fingerprint at 4B, and that bears on QI-T. It is stated.
- **If the design is the cause:** a reasoning-off model might not produce the answer format the
  parser expects. Pilot parse failures above 1 in 20 stop that run (protocol). The prompt is never
  changed to fit a model. For Spark, a different SGLang build is a serving difference, stated in the
  readout. If a Spark fingerprint is extreme, the pilot outputs are compared with the card's own
  example to check the template.

## Design audit

1. **Fidelity.** Message content is the redo Part 0b set plus QI-1b for all 960 prompts in every
   run. The 880 redo contents match a cache file in `runs/life_dr_tipping/redo/cache_part0b_mix`
   (0 missing). They are not the QI-1 top-block prompts. The 80 QI-1b contents match a cache file in
   `runs/life_dr_qi1b/luna/cache` (0 missing); QI-1b already places P_e by the redo hash. The same 960
   strings are the user-message content of all five runs (0 mismatches). Concatenated sha256
   `1f02f68d0082b24e663a97daee47f18765bd6562afde863080187a35444fd6e6`. Request bodies, on one shared
   prompt, schema sha256 `8712e3df2171bd51ac6455e5caf8a1e22e4648e7f3525dbd6dcf886979545529`, name
   `life_cell_decision_v2`, strict. No body contains `seed`.
   - **W1-oss20:** `model` `openai/gpt-oss-20b`; one user message whose content is the prompt;
     `temperature` 1.0; `top_p` 1.0; `max_tokens` 32768; `reasoning_effort` `medium`; `response_format`
     as above. No `top_k`, `min_p`, or `presence_penalty`.
   - **W1-qi-nat and W1-qi-match:** `model` `Qwen/Qwen3-4B-Instruct-2507`; one user message;
     `top_k` 20; `min_p` 0; `presence_penalty` 0; `max_tokens` 32768; the same `response_format`.
     `temperature` / `top_p` are 0.7 / 0.8 and 0.6 / 0.95. Those two keys are the only difference.
   - **W1-spark-high and W1-spark-none:** `model` `spark2.6`; one user message; `temperature` 1.0;
     `top_p` 0.95; `top_k` −1; `repetition_penalty` 1; `presence_penalty` 0; `frequency_penalty` 0;
     `max_tokens` 32768; the same `response_format`. `chat_template_kwargs.enable_thinking` is true
     and false. That key is the only difference. Effort `high` is the template default when thinking
     is on, so it is not a second field.
   Within each pair the bodies differ only as the table says: decoding for the Qwen arms, and
   `enable_thinking` for the Spark arms. Asserted: the Qwen diff is exactly `{temperature, top_p}`
   and the Spark diff is exactly `{chat_template_kwargs}`.
2. **Coverage.** All fingerprints use battery conditions only.
3. **Controls.** The pairs are their own controls. For class A, the reasoning-on member of the Qwen
   pair is QI-1m, on the redo prompts, plus QI-1b. QI-1 is not that member. For class-B 0/8, QI-1 is
   the same prompt, so its prefix rate is the reasoning-on comparison. W1-qi-match isolates reasoning
   from decoding.
4. **Observability.** The cell sees only its prompt.
5. **Gate consistency.** These pre-lock gates run together: byte identity; the body diffs; the
   decoding source for gpt-oss; the Spark image digest and arm64 manifest; the weights pinned and
   hashed after download. The pilots and launch gates (lock free, no other job) run per run, at its
   queue slot.
6. **Statistical unit.** The source cell, with Fisher on prompts beside it, as in QI-1.
7. **Pre-stated readings.** Above.

## R1 filter set (revision before lock)

The first dry build gave R1 a power of 0.089 at an off-rate of 0.08 and 0.456 at 0.15, with 40
prompts per arm. Failure rates near 0.025 are too rare for 40 prompts. Before the lock, and with no
wave-1 data seen, R1 moves to an enlarged filter set:

- **Prompts:** the same class-B 0/8 prompts of the 20 source cells, at D draws per cell instead
  of 2. D is the smallest value in {8, 12, 16} that gives power ≥ 0.8 at an off-rate of 0.08, from
  the homogeneous run below. That value is **D = 12** (power 0.8350). This inbox has no P_e line, so
  the top-block builder and the redo builder emit the same prompt. Rebuilt prompts are
  byte-identical to QI-1 at draws 0 and 1: 20/20 cells, 0 mismatches, and those two cache files are
  present. The prompt bytes are the same at draws 2–11; only `draw` enters the cache key. Those ten
  draws are absent from the QI-1 cache. The manifest was not rebuilt. Concatenated prompt sha256
  `ab50cef429329e869e7237d1dc851e2bda2343d9e2e16e6aef836d09d93341e7`. Manifest:
  `runs/model_panel/w1_r1_b08_prompts.json`.
- **Arms:** every R1 arm runs the enlarged set: W1-qi-match, W1-spark-none and W1-spark-high, plus
  a fresh Qwen3-4B-Thinking-2507 arm on the Stage 1 settings. W1-qi-match, W1-spark-high and
  W1-spark-none each run draws 2–11 from `runs/model_panel/w1_r1_b08_prompts.json` after their
  960-prompt battery. Draws 0 and 1 of that set are the class-B 0/8 rows already in the battery.
  The Thinking arm is queued right after W1-qi-match, on the Qwen server. The 2 QI-1 draws per
  cell count toward its D, and it calls only draws 2–11. Runner: `runs/run_life_panel_wave1.py`.
- **Unit:** the test is the same one-sided Fisher on prompts, with the cell-level sign-flip beside it.
  The fingerprint battery itself stays at 2 draws per cell. The extra draws serve only R1 and U1, and
  U1 is also reported on the enlarged set.

## Power

For R1, 20 cells × D draws, D ∈ {2, 8, 12, 16}, reasoning-on rate 1/40, reasoning-off rate 0.08 and
0.15, 2000 simulations, `numpy` Generator seed 0, one-sided Fisher α = 0.05. Homogeneous cells, and a
second run whose cell rates are drawn from a beta with the same mean and intraclass correlation 0.1.
The homogeneous run sets D. The D = 2 homogeneous row reproduces the first dry build.

| D | homogeneous 0.08 | homogeneous 0.15 | ICC 0.1 at 0.08 | ICC 0.1 at 0.15 |
|---|---:|---:|---:|---:|
| 2 | 0.0890 | 0.4560 | 0.1055 | 0.4355 |
| 8 | 0.6340 | 0.9930 | 0.6170 | 0.9700 |
| 12 | 0.8350 | 0.9990 | 0.7375 | 0.9920 |
| 16 | 0.9175 | 1.0000 | 0.8090 | 0.9980 |

**D = 12.** It is the smallest value in {8, 12, 16} with homogeneous power at 0.08 at least 0.8.
The ICC 0.1 power at that D and rate is 0.7375, below 0.8, and is stated beside the choice. The
design is not changed further.
