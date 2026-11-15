# Amendment — Qwen3-4B-Thinking at temperature 1.0: signal prior, signal copying, adoption

**Status:** locked v2 (2026-11-15; v2 gives QT3 three calls per prompt per arm after the dry build's
power check, with a sign-flip test on per-prompt counts), before any call. Written by the reviewer
for Artem; dry build passed; locked on Artem's instruction. No call is made before Artem's go. It
runs locally on the GPU after random-8.

## Why

Every Qwen3-4B-Thinking result in the paper was sampled at temperature 0.6, top_p 0.95 and top_k 20.
These are the settings its model card recommends for thinking mode. The gpt-oss models run at
temperature 1.0 and top_p 1.0. Qwen differs from the other models in two ways:

- **Adoption.** It is the stubborn class: it rarely adopts P_e from its neighbours.
- **Signal.** It writes signal 0 in 5,698 of 5,716 published messages, and it forms no convention.
  - With an empty inbox (round 1), 14 of 348 messages carry a non-zero signal (4.0 %). Twelve of
    these encode the rule the cell publishes: 4 for R004, or 1 for the shift amount.
  - After round 1, a cell that saw a non-zero signal repeated it 3 times in 403.

In Okawa's spin-model account of LLM debate, low temperature strengthens lock-in. So part of both
differences may come from sampling rather than from the model. This amendment tests that on stored
prompts. Only the temperature is changed.

## Design

- **Model and engine.** Qwen3-4B-Thinking-2507, with the same revision, SGLang image, launch spec
  and chat template as the stored runs.
- **Arms.**
  - **T06:** temperature 0.6, a fresh control with no cache reuse.
  - **T10:** temperature 1.0.
  - Everything else is identical: top_p 0.95, top_k 20, min_p 0, max_tokens 32,768, the same prompt
    bytes and the same response schema.
  - QT1 and QT2 prompts get one call per arm. QT3 prompts get three calls per arm, with draws
    1–3. The arm order is randomised per prompt by `sha256("qtemp|<prompt_sha256>")`: an even
    first byte means all T06 calls of that prompt go first.
- **Reasoning.** It is stored for every call, as for every open model.

### QT1 — signal prior (empty inbox)
- **Prompts.** The 348 stored round-1 publishing prompts of the world-1 Qwen population runs (`all`
  r1–r2, lattice r1–r2), as in `population_calls_2026-11-12`.
- **Outcome.** The message is published with a non-zero signal. A silent or unparsed answer counts
  as "not non-zero"; both are reported.

### QT2 — signal copying (non-zero in inbox)
- **Prompts.** The 403 stored publishing prompts from rounds ≥ 2 whose inbox shows at least one
  non-zero signal.
- **Outcome.** The message is published with a non-zero signal. Descriptive beside it: the share of
  non-zero signals that equal a value seen in the inbox (a copy), against a value not seen (new).

### QT3 — adoption
- **Prompts.** The 400 adopt prompts of `AMENDMENT_QWEN_CHECK_NUDGE.md`: the battery's lattice and
  S88 conditions, without the nudge sentence.
- **Outcome.** Adoption as defined there: the inferred rule is P_e when the cell's previous rule was
  not P_e.

## Prediction and thresholds (derived before the lock)

**QT1.** A one-token model of the choice gives the reference value. Suppose the signal were one
sampled token with a fixed logit gap Δ between 0 and the non-zero values. Then the log-odds scale as
1/T.
- At T = 0.6, the observed 4.0 % gives log-odds −3.18, so Δ = 1.91.
- At T = 1.0, the log-odds are −1.91, which gives about 13 %.

A thinking model reaches the signal through a long chain, so 13 % is a reference point and not a
fitted prediction. The readings below are fixed against it.

**Tests.** All are exact one-sided McNemar tests on the prompt-paired binary outcome (T10 against
T06), at α = 0.025 each.
- **QT1 holds** if T10 has more non-zero signals than T06 at p < 0.025.
- **QT2 holds** if T10 has more non-zero signals than T06 at p < 0.025.
- **QT3 holds** if T10 has more adoptions than T06 at p < 0.025. QT3 has three calls per arm, so it
  does not use McNemar. The statistic is the sum over prompts of d = (T10 adoptions − T06
  adoptions), with d between −3 and 3. The null is an exact sign flip of d per prompt: Monte Carlo
  with 100,000 flips, seed 0, one-sided.

There is no correction across the three tests: they ask three separate questions and are reported
separately.

**Power, computed at the reference values.**
- **QT1.** T06 at 4 % and T10 at 13 %, with independent draws per prompt. The expected discordant
  pairs are about 43 against 12, so power is above 0.99.
- **QT3.** The dry build gave power 0.42 with one call per arm, for +0.05 on a base of 0.15 (the
  nudge study's control rate was 0.145). The reviewer's simulation of the sign-flip test reproduced
  0.42 at one call and gave 0.72 at two and 0.89 at three, under independent draws. Three calls are
  used. The +0.05 is a planning value, not a derived threshold. The test's threshold is α, and +0.05
  only sizes the run.

**Pre-stated readings for QT1, with the T10 rate r:**

| r at T10 | reading |
|---|---|
| QT1 fails | The 0 is not sampling noise. Qwen's signal choice is a stable decision. |
| holds, r ≤ 0.20 | Consistent with a plain temperature effect on the choice (reference about 0.13). |
| holds, r > 0.20 | Temperature changes the reasoning about the signal, not only the sampling of one choice. |

## Decision rule: a full Qwen rerun at T = 1.0

**Trigger.** If QT1 or QT3 holds, a separate amendment reruns the whole Qwen line at temperature
1.0, with nothing else changed:
- the battery and its response class;
- the population runs on `all` and the lattice (two each, world 1);
- the signal readouts.

The paper then reports Qwen under both temperatures and states which conclusions depend on it.

**If neither holds,** the Qwen results stand at T = 0.6. The Limitations sentence changes from
"untested" to the measured result.

**QT2 alone** does not trigger the rerun. It is reported as descriptive evidence on copying.

## Gates

- **Format.** If unparsed or truncated answers exceed 2 % in either arm of any block, the run stops
  and the result is reported. The retry rule is the same as for the stored runs.
- **Prompt identity.** The dry build re-renders 5 prompts per block from the stored records. The
  rendered bytes must equal the stored prompt sha256, and the request bodies must differ only in
  `temperature`.
- **Control reproduction (descriptive).** T06 rates are reported beside the stored values: 4.0 % for
  QT1, 3/403 for QT2 and 0.145 for QT3. A large departure is reported. It does not stop the run.

## Calls and time

(348 + 403) × 2 + 400 × 3 × 2 = 3,902 calls, about 31 GPU-hours at the nudge study's 28.7 s per call. The agent states the wall time from the
stored Qwen runs' measured time per call.

## Outputs

- Calls, with reasoning, in the usual format.
- `readout.json` / `.md`: QT1–QT3 rates per arm, McNemar counts and p, the copy/new split, and the
  format counts.
- A recheck package with SHA256SUMS.

Nothing enters the paper before the reviewer's recheck from raw data.

## Queue

1. `wait_topology_random8_done`.
2. `wait_go_qwen_temperature`, which needs a go file and a switch-log line with Artem's words.
3. Precheck: manifest sha, free GPU, no foreign SGLang.
4. QT1, QT2 and QT3, interleaved by prompt in the randomised arm order.
5. Readout.
6. Package.