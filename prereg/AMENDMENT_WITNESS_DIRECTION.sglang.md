# Witness direction — clarification: Stage 1b, scale pilot and timed probe on SGLang 0.5.18

**Status:** accepted 2026-11-10 (Artem: "Clarification accepted with one edit to the canary rule"),
with that edit in the canary gate below. Written before any scale-pilot, probe or Stage 1b call on
SGLang. The locked amendment `AMENDMENT_WITNESS_DIRECTION.md` (sha256 `3cf91f25…`) is unchanged;
this clarification sits beside it, as `AMENDMENT_WITNESS_DIRECTION.attention.md` does, because the
runner refuses to start if the locked file's bytes change. Decisions are Artem's of 2026-11-10
("Plan approved, with these decisions", items 1–4, and the acceptance).

## Why

The timed HF probe of v22d projects Stage 1b at **516.6 GPU h** against the 96 h limit
(`runs/witness_direction/stage1/budget.json`); v22d waits in `wait_go_witness_budget`.

## What changes

- **Engine for the timed probe, the scale pilot and Stage 1b:** SGLang 0.5.18 in image
  `sha256:223b675f…`, the engine the stored battery ran on, with an external model package
  (`runs/wdir_sglang/jev_steer`, mounted read-only, loaded by `SGLANG_EXTERNAL_MODEL_PACKAGE`). No
  image change.
- **Unchanged:** Stage 1a and the fit (done on HF: L*_f = 5, 32, 5, 5, 5; `fit.npz` `0f10bc86…`),
  folds, directions, σ_f, layers, the α ladder and its rule, the blind pilot, the 96 h budget,
  arms, predictions, pre-stated readings, statistics, and the design audit except the engine.

## Steering in SGLang

- **Vector.** v = α·σ_f·d_f, the array `steer_vec` returns, saved bit for bit in its stored
  dtype: float64 for d and d_rand, float32 for d_k (as in `fit.npz`). It is cast once to bf16, the
  cast the HF engine uses.
- **Where it is added.** v is added to the residual that decoder layer L*_f returns, so the stream
  after that layer is hidden + residual + v. SGLang sums hidden and residual in the next layer's
  fused add-norm, so this is the HF hook "output of layer L + v", applied at every token: prompt,
  generated tokens and every chunk of a chunked prefill. The bf16 buffer is created when the model
  is built, before CUDA-graph capture, so captured decode and prefill graphs include the add.
- **Rounding (decision 3).** v goes to the residual, not to the summed stream. At α = 0 the server
  is bit-identical to the unpatched one. At α ≠ 0 it differs from HF by at most one bf16 rounding at
  that layer.
- **One launch per (fold, arm) and per pilot rung**, with v fixed for the launch. The α = 0 arm
  launches the patched server with its fold's zero vector, so the witness gate applies to every
  launch.
- **Requests: those of the stored battery.**
  - `/v1/chat/completions`, one user message, the model's own chat template;
  - temperature 0.6, top_p 0.95, top_k 20, min_p 0, presence_penalty 0, max_tokens 32,768;
  - `response_format` strict `json_schema` (`decision_json_schema`), reasoning parser qwen3;
  - mem-fraction 0.6, at most 64 running requests.
  
  The answer is constrained by the server's grammar, as in the battery; the HF answer automaton is
  not used. **Context 40,960 for every call:** 36,864 cannot hold the longest Stage 1b prompt plus
  max_tokens (4,308 + 32,768 = 37,076). The battery's 204 resumed calls used 40,960 for the same
  reason.

## Gates at every launch (decision 1)

1. **Witness.** The model process writes one witness file: class, layer, sha256 of the vector
   file, sha256 of its bf16 bytes, norm, pid. The launch passes only if exactly one witness exists
   and every field equals the expected value. This catches the silent fallback: if the package
   fails to import, SGLang only logs a warning and serves the built-in class.
2. **Canary (deterministic).** One fixed prompt, chosen by rule before any GPU output: the pilot
   prompt with the lowest `sha256("wdir-canary|<prompt id>")`, which is `A|n8-k3-m2-adopt|15`, 1,996
   chat tokens (its ids are HF `chat_ids`).
   - **The request:** after readiness and before any other request, alone, its prompt-token
     logprobs from `/generate`: `input_ids`, `logprob_start_len` 0, one greedy token.
   - **α = 0:** bit-identical to the unpatched server's canary in the same mode with the same flags.
     That reference is recorded once per mode, from an unpatched launch.
   - **α ≠ 0:** differs from that reference at one or more positions, **and** matches HF under the
     same vector. The HF reference is the HF engine (bf16, sdpa, the same hook) on the same ids.
     For every vector that can be launched (5 folds × {d, d_rand, d_k} × α ∈ {0, ±2, ±4, ±8, ±16}),
     it is computed in one HF GPU step before the first SGLang launch.
   - **Match rule (Artem, 2026-11-10).** Means are over prompt positions; SG_unpatched(0) is the
     unpatched reference above.
     - (a) mean |SG(α) − HF(α)| ≤ 1.5 × mean |SG_unpatched(0) − HF(0)| + 0.005 nats.
     - (b) mean |HF(α) − HF(0)| ≥ 3 × mean |SG_unpatched(0) − HF(0)|.
     - (c) Pearson correlation over prompt positions between SG(α) − SG_unpatched(0) and
       HF(α) − HF(0) ≥ 0.9.
     - The launch passes if it differs from the reference, (a) holds, and, when (b) holds, (c) holds.
       If (b) fails, the launch log says "steering effect below engine noise on the canary" and the
       launch passes on (a) and the witness.
     - All three numbers are reported per launch.
   - A failed gate stops the launch before any call is scored. The witness file is kept with the
     launch's records.

## Mode (decision 2), stated before the probe

- **Timed SGLang probe, deterministic mode first** (`--enable-deterministic-inference`).
  - **What runs:** one patched launch with fold 1's zero vector. Both gates, then the 40 pilot
    prompts at α = 0, sent together.
  - **What it records:** launch-to-ready time, wall time, and invalid and truncated counts only.
    Nothing about decisions is printed or logged, as for the pilot.
  - **Projection:** over the 25 Stage 1b launches, ⌈n_launch / 40⌉ × probe wall time plus 25 ×
    launch time. Each launch holds its fold's adopt prompts and own-example items, 116 calls.
- **≤ 96 h:** deterministic mode for the pilot and every arm. Each call sends `seed` =
  `int(sha256("wdir-seed|<prompt id>|<draw>")[:8], 16) & 0x7fffffff`, the same in every arm. SGLang
  then samples by Gumbel noise keyed on (seed, position, rank). That gives common random numbers
  across arms, not the HF `row_uniform` scheme; the analysis is unchanged (paired by prompt).
- **Sampling in deterministic mode (source, 2026-11-10; check `sampler`).**
  - SGLang forces the pytorch sampling backend in deterministic mode. Standard mode uses flashinfer.
  - Both modes take the same path in `Sampler.forward`: logits divided by the temperature, then
    softmax, then `_sample_from_probs`. The RL log-softmax branch is off without
    `rl_on_policy_target`.
  - The pytorch sampler zeros probabilities outside top-k and outside top-p (top-p on the
    cumulative mass of the original sorted probabilities, the same kept set as flashinfer's
    `joint` order), then takes the Gumbel argmax of their log. That is a draw from the renormalised
    kept set.
  - In-image CPU test of that function, with only the Triton hash replaced by uniform draws:
    200,000 draws, one case with top-p binding (4 tokens kept) and one with top-k binding (20 kept).
    No draw outside the kept set; largest frequency gap to the renormalised distribution 0.0019.
  - Consequences: every request sends its seed (without one SGLang uses 42); min_p stays 0 (with a
    seed, min_p > 0 raises an assertion).
- **Otherwise:** standard mode with independent draws (no seed sent; SGLang ignores it in that
  mode). Standard mode is then timed the same way. If it also projects above 96 h, the queue stops
  in a `wait_go_*` step and asks Artem.
- The budget limit and its stop are unchanged.

## Fidelity gates

- **(i) Token ids:** now SGLang's own chat path, and checked on CPU (below).
- **(ii) and (iii):** unchanged, on the α = 0 arm. (ii) now compares the battery's engine with
  itself under steering code at α = 0.
- **(iii)'s call classes on SGLang:**
  - finish_reason `length` → truncated;
  - finish_reason `stop` with the reasoning closed and a final answer → closed-and-stopped;
  - `stop` with no final answer → EOS inside reasoning.

## CPU checks (done 2026-11-10; `runs/witness_direction/sglang_cpu_checks.json`, all nine pass)

`runs/wdir_sglang_checks.py`, no GPU, no network; image checks run in CPU-only containers.

- **source:** the nine SGLang files the design relies on, hashed inside the image, equal the host
  copy used for the reading.
- **ast:** the decoder layer returns `(hidden_states, residual)` from `postprocess_layer`; Qwen3Model
  uses Qwen2Model's loop, `layer(positions, hidden_states, forward_batch, residual)`, and the final
  `norm(hidden_states, residual)`; the registry block overwrites by class name and swallows import
  errors; our module has one class, `EntryClass`, and no import-time side effects.
- **registry (in the image):** with the package, `Qwen3ForCausalLM` resolves to
  `jev_steer.qwen3_steer.Qwen3ForCausalLM`, a subclass of the built-in; without it, to the built-in.
- **wrapper (stub base class):**
  - refuses a missing variable, a sha mismatch, a layer out of range, a wrong shape and a wrong
    dtype;
  - writes a witness that passes the gate;
  - the buffer equals HF's bf16 cast and is outside `state_dict`;
  - only layer L's residual changes, by exactly + v; keyword arguments pass through; an empty
    batch works; the buffer address is constant;
  - a zero vector is bit-identical.
- **vectors:** for 5 folds × 3 kinds × 9 α (135 files), the file reloads bit for bit as
  `steer_vec`'s array, its bf16 cast equals HF's, its norm is |α|·σ_f and its layer is L*_f.
- **emulator (tiny random Qwen3, L = 0, 1, 2):** SGLang's residual bookkeeping with + v on the
  residual, built from HF submodules, against the HF hook.
  - **float32:** logits agree within 2.4e-7, and every layer's stream equals HF's capture.
  - **bf16:** max logit gap 0.0039 against a steering effect of 1.11–1.28.
  - **Zero vector:** bit-identical in both precisions.
- **tokens:** for the 580 Stage 1b items (540 adopt, 40 own-example) and the 40 pilot items, the
  image's tokenizer and default chat path (transformers 5.12.1) give exactly HF `chat_ids`: 620 /
  620, no mismatch, every tail `<|im_start|>assistant\n<think>\n`. Lengths 1,924–4,308.
- **launch:**
  - the argv lint passes for patched and unpatched launches in both modes and catches
    `--forward-hooks`;
  - seeds are distinct over the 580 items and below 2³¹;
  - the canary logic on synthetic data: α = 0 passes identical and fails one ulp; α ≠ 0 passes
    steered-and-matched with (c) checked, fails steered-identical, wrong scale and missing HF
    references; passes on (a) with the note when (b) fails; fails when (a) and (b) both fail; fails
    when (a) and (b) hold and (c) does not.
- **sampler:** as described under Mode; source files `overrides.py`, `protocol.py` and
  `server_args.py` added to the pinned set.

## GPU checks before the timed probe (each its own background step)

- **Reference:** unpatched canary per mode.
- **HF canary references:** all launchable vectors.
- **First patched launch, on top of both gates:**
  - CUDA graphs on vs off at α ≠ 0 (greedy canary agrees);
  - a repeated steered prompt through the prefix cache gives identical output;
  - `/server_info` saved.

## Queue

On acceptance (Artem, 2026-11-10): v22d, idle in `wait_go_witness_budget`, is stopped with
`runs/queue_stop.sh --guard`; `runs/witness_direction/stage1/` is kept as is for the new runner. A
new waiter is armed beside a v3 watcher. It has one step per GPU check above, then the probe, the
mode decision, the pilot, the α = 0 arm with the fidelity gates, the steered arms and the readout.
Its first GPU step waits in a `wait_go_*` step for Artem's go.
