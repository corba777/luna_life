# Amendment — a third model: gpt-oss-120b on the redo Part 0b battery

**Status:** locked. Local and approved by Artem: the 120b first, and the 20b only after this
readout. No gpt-oss call outside the pilot below until this file is committed as locked. Values marked
**[dry build]** are filled in by the agent from existing logs or the pilot before the lock.
Parents: `runs/life_dr_qwen/qi1/readout.md`, `runs/life_dr_tipping/redo/redo_readout.md`, the Qwen
QI task (QI-1 definition), `DESIGN_AUDIT_CHECKLIST.md`.

## Why

The battery is the redo Part 0b prompts, the same strings as QI-1m. The top-block construction is not
a behavioural reference. QI-1 stays only as a model-against-model comparison on the original top-block
prompts, set against Luna's original top-block counts.

| class A, P_e / prefix | 2/6 | 3/5 | 4/4 | 5/3 | 6/2 | 1 P_e + 7 empty | 1/7 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Luna (redo; the reference) | 0/40 | 2/40 | 5/40 | 32/40 | 39/40 | 34/40 | 0/40 |
| Qwen QI-1m (redo; the reference) | 1/40 | 0/40 | 3/40 | 1/40 | 7/40 | 1/40 | 0/40 |
| Luna (original top block) | 2/40 | 5/40 | 17/40 | 40/40 | 40/40 | 35/40 | 0/40 |
| Qwen QI-1 (top block; not a reference) | 0/40 | 1/40 | 8/40 | 8/40 | 9/40 | 3/40 | 1/40 |

QI-1m rates, 2026-10-22: S = -0.050, L = 0.025, top = 0.675. The file stays a draft until its own lock.
On the top-block prompts, Luna has a sharp step at a strict majority and a single P_e line in an empty
inbox is enough (35/40). Qwen QI-1 has no step: from 4/4 upward it stays flat near 0.2, and a single
line does almost nothing (3/40). That comparison is not the reference for G1 or G2. Both models keep
the own-example filter on the class-B 0/8 inbox, which has no P_e line, so the two builders emit the
same prompt (Luna redo prefix 0/40, Qwen QI-1 prefix 1/40).

Two models give a contrast, not an explanation. gpt-oss-120b has open weights from the same developer
as Luna, and it is closer to Luna in strength than Qwen3-4B is. It asks whether the threshold response
goes with the developer family.

## Model and serving

- `openai/gpt-oss-120b`, Hugging Face revision `b5c939de8f754692c1647ca79fbf85e8c1e70f8a`
  (public, Apache-2.0, not gated), served by the same SGLang install as Qwen, on the same host,
  while no other job runs.
- The served weights are the 15 MXFP4 safetensors shards, 65,248,893,184 bytes (60.77 GiB). The
  original and metal copies in the same repository are not downloaded. The host has 127,600,528 kB
  (121.69 GiB) of unified memory. While the Qwen server is up at mem-fraction 0.6, about 38 GiB is
  available, which is less than the weights, so this model does not fit beside that server. With
  that server stopped, the first setting, mem-fraction-static 0.70, was an 85.2 GiB pool: 60.77 GiB of weights and about
  24 GiB for KV, leaving 36.5 GiB outside the pool, above the serve script's 15 GiB host reserve.
  Serving flags: context length 36864, `--reasoning-parser gpt-oss`, max-running-requests 4.
  The first load used mem-fraction-static 0.70 and was killed during weight initialization (exit -9).
  Serving configuration after that kill: mem-fraction-static 0.62, and drop the page cache before
  start when the host permits it. The drop was not permitted: `/proc/sys/vm/drop_caches` is not
  writable, and passwordless sudo is refused.
  Third attempt, 2026-10-22, after QI-2. Image `lmsysorg/sglang:latest-cu130`, index digest
  `sha256:e3a4f06001a29542fc4a8638536d9ffc5eb9c9942b08603c09b19a56eae4a1ae`, linux/arm64 manifest
  `sha256:06441be3de19a816ddbac917535e920cbfc7fc43171abc08417394f43634ffb6`, both re-checked at pull.
  SGLang in that image is 0.5.22. Flags: `--ipc=host`, `--ulimit memlock=-1`, `--ulimit stack=67108864`,
  `--mem-fraction-static 0.70`, context length 36864, the revision above, `--reasoning-parser gpt-oss`,
  `--attention-backend flashinfer`, no `--trust-remote-code`. Swap, from `swapon --show`: `/swap.img` 16G
  and `/swapfile2` 64G, about 80G, both in fstab. About 2.3G of `/swap.img` was already used.
  The process exited in about 16 seconds, before weight loading (docker status 1). The log selected the
  FlashInfer CUTLASS MXFP4 MoE kernel, then refused the attention backend: `GptOssForCausalLM` requires
  one of `triton`, `trtllm_mha`, `fa3`, `fa4`, `ascend`, `intel_amx`, `intel_xpu`, `aiter`, and got
  flashinfer. MemAvailable stayed near 122 GiB. Swap use did not rise. This image's own help names the
  MoE switch `--moe-runner-backend`, whose choices include `triton_kernel`. That switch was not tried.
  No fastsafetensors load and no vLLM. The tag `latest-cu130` was then pointed back at the previous
  image `sha256:223b675fee9ec3020a7b1479a6d1a3d24296f729f2eb6049f69f1e0423118e7e` (SGLang 0.5.18,
  repo digest `sha256:9e148f5ac788e856a06166bd6347a831831eb9fcfab4d1770874823a7c29a1a1`). The 0.5.22
  image is kept as `lmsysorg/sglang:cu130-20261022`.
  Fourth attempt, ordered after QI-1m and not started while that job holds the server. Same pinned
  image, the arm64 manifest above, SGLang 0.5.22, and the same settings, without
  `--attention-backend`, so the build picks its default for gpt-oss. The tag `latest-cu130` is not
  used for this launch, because that tag names the 0.5.18 image. The download of the 15 shards to the host Hugging Face cache was started
  with this draft. The runner does not stop the Qwen server until all 15 shards are present.
  Fourth attempt result, 2026-10-22: the 15 shards loaded in 354.90 s, using 79.97 GB. SGLang then stopped
  with "Loaded weights leave no GPU memory for the KV cache under --mem-fraction-static=0.7", minimum
  viable 0.7132. The model never answered. Report: `runs/life_dr_gptoss/qi1/load_attempt4_report.md`.
  Fifth attempt, Artem's go 2026-10-22: `--mem-fraction-static 0.82`, because of that error. Everything
  else as in the fourth attempt: the same arm64 manifest (SGLang 0.5.22), the revision, context length
  36864, `--reasoning-parser gpt-oss`, no `--attention-backend`, no `--trust-remote-code`, swap about
  80G. Queued after the wave-1 queue ends and before QI-G. If the KV pool is below 4 × 36864 = 147,456
  tokens, max-running-requests is lowered to the largest value that fits (pool // 36864), and the
  server is restarted once with that value. This changes throughput only, not outputs. A pool below
  36864 tokens is a serving failure. Swap affects throughput, not outputs. The pilot's mean seconds per
  call projects the battery's wall time as mean × 960 ÷ max-running-requests (880 battery calls plus
  80 QI-1b calls). The chain stops before the lock only if that projection exceeds 48 h. Otherwise the
  swap figures and the projection are recorded here, and the chain continues.
  KV pool: 195,574 tokens (5.31 contexts of 36,864). max-running-requests: 4, unchanged, because the pool holds at least 4 full contexts. Swap: 2.43 GiB used at the start, peak 32.48 GiB at 2026-10-22T23:23:03-04:00, 6.34 GiB when the server answered.
  Swap during the pilot: 6.24 GiB used at its start, 6.23 GiB at its end, 0.027 GiB swapped in. Projected battery wall time: 24.3 s mean per pilot call × 960 ÷ 4 = 1.6 h (within the 48 h limit).
- Reasoning effort `medium`, set by the model's own mechanism (the Harmony system line
  `Reasoning: medium`) and matching Luna's `effort="medium"`. OpenAI's gpt-oss repository, "Recommended
  Sampling Parameters": "We recommend sampling with `temperature=1.0` and `top_p=1.0`."
  https://github.com/openai/gpt-oss/blob/d21f34ec3c1ede813adfbd83f07d2ad2eec7ff02/README.md#recommended-sampling-parameters
  Qwen runs at its own recommendation (0.6 / 0.95 / 20).
  Each model therefore runs at its developer's recommended decoding, which is the comparison already
  made between Luna and Qwen. That choice is stated in the readout. max_tokens 32768. No seed.
- **Pinned template variable: the Harmony date.** The model's chat template (sha256
  `a4c9919cbbd4acdd51ccffe22da049264b1b73e59055fa58811a99efbd7c8146`, the same file in the 20b and 120b
  revisions) writes `{{- "Current date: " + strftime_now("%Y-%m-%d") + "\n\n" }}` into the system
  message. It has no date variable. Its only kwargs are `builtin_tools`, `model_identity` and
  `reasoning_effort`, so `chat_template_kwargs` cannot set the date. The date is pinned to 2026-10-22,
  the date the gpt-oss-20b battery saw (all its calls, pilot included, fell between 21:15 and 22:26 UTC
  on 2026-10-22, on a UTC container clock). The server gets a copy of the template,
  `runs/life_dr_gptoss/pinned/chat_template_date_20261022.jinja` (sha256
  `e6433aba3fb14f310cd55bd516dbbbaa5859f48e5b7a05f605916bb07a9a7387`), through `--chat-template`, mounted
  read-only at `/pinned`. It differs from the model's template in that one line only:
  `{{- "Current date: " + "2026-10-22" + "\n\n" }}`. This is a serving difference, and the readout states it.
  The reference system message, `runs/life_dr_gptoss/pinned/system_prompt_reference.txt` (sha256
  `2bf6cf4998b457b654066c55af37594ee634f179164dc36b57f9b14c0fee61e4`), is the 20b battery's rendered
  system message, byte for byte:
  `<|start|>system<|message|>You are ChatGPT, a large language model trained by OpenAI.\nKnowledge cutoff:
  2024-06\nCurrent date: 2026-10-22\n\nReasoning: medium\n\n# Valid channels: analysis, commentary, final.
  Channel must be included for every message.<|end|>`.
  Runtime invariants (`runs/gptoss_pinned_template.py`), for every gpt-oss run (gate, pilot, battery,
  QI-1b):
  - an offline render of the pinned template, with `reasoning_effort` medium, gives a system message
    equal to the reference byte for byte;
  - the pinned file differs from the model's template in the date line only;
  - the live container was launched with `--chat-template /pinned/chat_template_date_20261022.jinja`,
    and the mount comes from the pinned directory (`docker inspect`);
  - every response's `prompt_tokens` equals the token count of the offline pinned render. That check
    cannot see the date itself, but it does detect a server rendering a different template.

  SGLang 0.5.22 (source of the released wheel) loads a `.jinja` `--chat-template` with
  `"".join(f.readlines()).strip("\n")` and then `.replace("\\n", "\n")`. Unlike the model's built-in
  template, which the 20b battery used, this step changes the text. Rendered offline, that loaded
  text gives the same full prompt as the file on all 960 wave-1 battery prompts, and the invariant
  renders it both ways. Template feature detection (reasoning and tool parsers) runs on the loaded
  template in either case. The chat endpoint renders with `tokenizer.apply_chat_template` and passes
  `reasoning_effort` as a template kwarg.
  The cache key includes the pinned template's sha256. Any failure stops the run before or at that call.
- Scoring reads only the final channel. gpt-oss has open weights, so its reasoning text may be stored,
  but nothing is scored from it.

## Prompts

The 880 redo Part 0b prompts (22 class × condition cells, 20 source cells, 2 draws), the same strings
as QI-1m. The message content handed to the chat template is byte-identical to that redo content.
It is not the QI-1 top-block content. Only the template differs, as it does between any two models.
One call per prompt: 880 calls. The cache
is `runs/life_dr_gptoss/qi1/cache`, with its own lock, one launch, nohup, the watchdog and no
auto-relaunch. In the queue it goes after QI-T and before QI-2. The Qwen server is stopped before
it and restarted after it by the runner, under the launch gates.

## Pilot (before the lock, not scored)

The pilot needs the server, so it runs in this job's queue slot after QI-T ends, never next to another
job. The sequence: the offline gates (byte identity, the pinned revision, the recorded body, power)
are done now. When QI-T's readout is committed, the pilot runs. If the pilot and every other gate pass,
the agent commits this file as locked, records the lock commit, and launches the battery. If anything
fails, it stops and reports, and QI-2 goes next.

The pilot itself is 20 calls on round-1 prompts from the Qwen Stage 1 `all` world-1 history (empty
inbox), which are not part of the battery. The selection, fixed before those calls, is cells 0–19 of
replicate 1. The offline gate rebuilt those 20 prompts: each inbox is empty, and each prompt is in
the Stage 1 `all` replicate-1 cache. These prompts check only that the model loads, renders through
Harmony and returns a final answer the existing parser reads. **[dry build]**: parse failures,
truncations and time per call are filled from the 20 calls in the queue slot, before the lock. If
more than 1 of the 20 fails to parse or is truncated, stop and report. Do not change the prompt to
fix it.
Pilot result, filled from the 20 calls, 2026-10-22: n = 20, parse failures 0, truncations 0, failing calls 0, median time per call 26.6 s.

## Statistics (fixed now)

Unit: the source cell (20 cells, both draws pooled within a cell). Cluster bootstrap over cells, 2000
draws, `numpy` Generator seed 0, as in the QI-1 readout.

- **Step** S = P(adopt P_e | class A, 5/3) − P(adopt P_e | class A, 4/4). Luna's reference is the redo
  rate, 27/40 = 0.675. Qwen's reference is the QI-1m rate, -2/40 = -0.050. The QI-1 top-block difference is 0/40 and is not this reference.
- **Single line** L = P(adopt P_e | class A, 1 P_e + 7 empty) − P(adopt P_e | class A, 1/7). Luna's
  reference is the redo rate, 34/40 = 0.850. Qwen's reference is the QI-1m rate, 1/40 = 0.025. The QI-1 top-block
  difference is 2/40 and is not this reference.

Classification for each of S and L uses the hull of the Wilson 95% interval and the
cluster-bootstrap 95% interval, from the lower of the two lower bounds to the higher of the two
upper bounds. Reason: at a rate of 0 or 1 within a condition the percentile bootstrap collapses to a
point, for example [1, 1] at 40/40. Such an interval excludes a reference of 0.975 that is true by
construction. The hull is never degenerate and is never narrower than either interval.

S and L are differences. The Wilson interval of a difference is the first rate's Wilson lower bound
minus the second rate's Wilson upper bound, through the first rate's Wilson upper bound minus the
second rate's Wilson lower bound. Each rate uses z = 1.96 and its 40 prompts. The bootstrap is the
95% percentile interval of the 20 cell differences.

- **Luna-like:** the interval excludes the Qwen value and contains the Luna value.
- **Qwen-like:** the interval excludes the Luna value and contains the Qwen value.
- **Intermediate:** the interval excludes both.
- **Undecided:** the interval contains both.

## Predictions (locked)

- **G1 (family, step):** S is classified Luna-like.
- **G2 (family, single line):** L is classified Luna-like.
- **G3 (filter):** class B adopts the prefix under 0/8 in at most 0.08 of prompts, the same bound as
  I3 and I3q.
- **Descriptive:** the full class-A and class-B curve with Wilson intervals, beside Luna and Qwen.
  Class-A adoption at 8/0. Answers that are neither P_e nor the prefix, and whether they fit the
  cell's own example. Three-way per-prompt agreement against the independence baseline used in the
  QI-1 readout.

## Pre-stated readings

- **G1 and G2 pass:** the threshold response, and the single-line response, appear in the open model
  of Luna's developer. This is consistent with a family trait, though one model cannot separate family
  from strength. The 20b run is the next step: the same family at lower strength.
- **Both Qwen-like:** the threshold is not a family trait at this size and recipe. Luna's response is
  then specific to Luna (or to its closed serving and decoding), and the package says so.
- **Split, intermediate or undecided:** stated as it is. The two curves are the result, and no
  family claim is made.
- **G3 fails:** the own-example filter is not shared by all three models, and this is stated
  separately from G1 and G2.
- **Decoding:** gpt-oss runs at temperature 1.0 and Qwen at 0.6. If gpt-oss comes out Qwen-like,
  temperature cannot be the reason it looks less Luna-like, because QI-T is testing whether lower
  temperature makes Qwen more stable. If QI-T shows Qwen's behaviour is temperature-driven, the
  readout states how that bears on this comparison.
- **If the design is the cause:** Harmony rendering or parsing could turn real answers into parse
  failures. Parse failures and truncations are counted per cell, and if they exceed 5% of any cell,
  that cell is reported but not used in S, L or G3.

## Design audit

1. **Fidelity.** The message content is byte-identical to the redo Part 0b prompts, the QI-1m set.
   Asserted: 880 of 880 user contents equal those prompt strings, and each (content, draw) pair is
   the key of an existing file in the Luna redo cache `runs/life_dr_tipping/redo/cache_part0b_mix`.
   There are 440 distinct strings, two draws each. They are not the QI-1 top-block prompts. The
   schema object is the QI-1 schema
   (`sha256 8712e3df2171bd51ac6455e5caf8a1e22e4648e7f3525dbd6dcf886979545529`). The only
   differences are the chat template, the reasoning line (`Reasoning: medium`) and sampling, and
   each is listed and justified above.
2. **Coverage.** S and L use only conditions that are in the battery, at the counts that produced the
   Luna and Qwen reference values. Nothing is extrapolated.
3. **Controls.** 4/4 is the control for S, 1/7 is the control for L, and the 0/8 baseline is the
   control for G3. All are in the same battery.
4. **Observability.** The cell sees only its prompt: its example, the inbox lines and the memory line
   as built for the redo. No prediction relies on anything else.
5. **Gate consistency.** These pre-lock gates run together: the pilot passes; byte identity of the
   880 message contents; the pinned revision is recorded; the request body is recorded field by field.
   Byte identity, the revision and the body are recorded above and below. The pilot has not run, so
   this file stays a draft. The launch gates are checked by the runner at start: the lock is free,
   no other job runs, the Qwen server is stopped, and the gpt-oss server answers.

   Request body, one field per line. There is no `seed`, `top_k`, `min_p` or `presence_penalty`.
   The messages array is one user message, so the chat template writes the Harmony system line
   `Reasoning: medium` from `reasoning_effort`. The final channel is what the existing parser reads.

   - `model`: `openai/gpt-oss-120b`
   - `messages`: `[{"role": "user", "content": <the redo prompt>}]`
   - `temperature`: 1.0
   - `top_p`: 1.0
   - `max_tokens`: 32768
   - `reasoning_effort`: `medium`
   - `response_format.type`: `json_schema`
   - `response_format.json_schema.name`: `life_cell_decision_v2`
   - `response_format.json_schema.strict`: true
   - `response_format.json_schema.schema`: the QI-1 schema, hash above
6. **Statistical unit.** The source cell, with the bootstrap over 20 cells. The Fisher tests on prompts
   are reported beside it, as in the QI-1 readout.
7. **Pre-stated readings.** Above, including the decoding and design-as-cause readings.

## Power

Simulate the classification with 20 cells × 2 draws, under true rates equal to Luna's counts and
then to Qwen's counts for the four conditions involved, 2000 simulations each. Record how often S and L
land in the correct class under each. If either rate is below 0.8, the readout says so. The design is
not changed after that number is seen unless this amendment is re-locked.

True rates in this dry build are Luna's redo rates, 32/40, 5/40, 34/40 and 0/40, and the QI-1
top-block rates, 8/40, 8/40, 3/40 and 1/40, in the order 5/3, 4/4, 1 P_e + 7 empty, 1/7. The Qwen
reference inside the classifier is the QI-1m difference (S = -2/40, L = 1/40). Each simulation draws
Binomial(2, p) per cell,
forms the 20 cell differences, and classifies the hull defined above against the fixed reference
values. One `numpy` Generator with seed 0 is used per true-rate scenario; the binomial draws and the
inner bootstraps share that generator in sequence. The correct class is Luna-like under Luna's rates
and Qwen-like under Qwen's rates.

| true rates | S in the correct class | L in the correct class |
|---|---:|---:|
| Luna (redo) | 0.9945 | 0.9865 |
| Qwen QI-1m (redo) | 0.9985 | 1.0000 |

All four are above 0.8 against that top-block point. The design is unchanged. The file is not locked
until the QI-1m rates replace that point and this power row is recomputed.