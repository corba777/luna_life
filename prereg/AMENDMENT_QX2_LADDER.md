# Amendment — QX-2 model ladder: gpt-oss-120b and Nemotron 3.5 Lightning on the four cells

**Status:** locked v1 (2026-11-15), written by the reviewer for Artem. Dry build passed (items 1–5;
wall estimate corrected to calendar time; Nemotron engine fixed by Artem). No call is made before
Artem's go, logged in the switch log with his words. It runs locally on the GPU after random-8 and
before the Qwen temperature battery.

## Why

Two models have now run QX-2 in the same world, and they differ at two steps of the process:
- **gpt-oss-20b** (pilot) mostly stays wrong. At δ = 1/64 its tests never hit the difference. At
  δ = 1/8 its agents find counterexamples but almost never share them.
- **Luna** (`AMENDMENT_QX2_LUNA.md`) corrects the error in three of four cells. It picks tests that
  separate the catalog's candidates, and it shares and relays the evidence.

This amendment adds two local models, to tell size from family:
- **gpt-oss-120b,** the same family as 20b at a larger size, which is also the paper's graded model;
- **NVIDIA Nemotron 3.5 Lightning 30B-A3B,** a recent open-weight reasoning model from another family.

## Scope

| order | arm | model | δ | B | replicates | calls |
|---:|---|---|---|---:|---:|---:|
| 1 | `oss120_d64_B4_r1` | gpt-oss-120b | 1/64 | 4 | 1 | 1,200 |
| 2 | `oss120_d8_B4_r1` | gpt-oss-120b | 1/8 | 4 | 1 | 1,200 |
| 3 | `oss120_d8_B1_r1` | gpt-oss-120b | 1/8 | 1 | 1 | 1,200 |
| 4 | `oss120_d64_B1_r1` | gpt-oss-120b | 1/64 | 1 | 1 | 1,200 |
| 5–8 | `nemo_*` | Nemotron 3.5 Lightning | same four cells, same order | | 1 | 4,800 |
| | **total** | | | | | **9,600** (+ retries) |

## Unchanged from the pilot and the Luna run

The following are as locked in `AMENDMENT_QX2_PHASE1.md`:
- the world (seed 0, G = 12), catalog, prompt bytes and schema;
- the mapper, retry and fallback rules;
- the protocol, the engine invariants and the format gate.

The same prompt goes to every model. The arm order within each model is the Luna order, most
informative first.

**Cache key.** It includes the arm name, as in the pilot, so no answer is shared between arms.
This avoids the cross-arm reuse found in the Luna run.

## Models and decoding (locked)

### gpt-oss-120b
- **Model and engine.** The pinned revision, SGLang image, launch spec and chat template of the
  paper's 120b runs (`openai/gpt-oss-120b` @ `b5c939de…`;
  `lmsysorg/sglang@sha256:06441be3de19a816ddbac917535e920cbfc7fc43171abc08417394f43634ffb6`,
  v0.5.22 / cu130-20261022; chat template `chat_template_date_20261022.jinja`, sha256 `e6433aba…`).
- **Request body.** As in `run_oss120_stage2.body_for`: temperature 1.0, top_p 1.0, reasoning
  effort medium, max_tokens 32,768.
- **Response format.** The QX-2 strict schema `qx2_cell_decision_v1`.
- **Reasoning.** The model is open, so its reasoning is stored for every call.

### Nemotron 3.5 Lightning 30B-A3B

Pins (Artem, 2026-11-15; smoke check decides):
- **Weights.** `nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-NVFP4` at revision
  `bee7596271d1495f6992ae224aefde4410e816b8`.
- **Engine.** The project's pinned SGLang image
  `lmsysorg/sglang@sha256:06441be3de19a816ddbac917535e920cbfc7fc43171abc08417394f43634ffb6`
  (v0.5.22), launched with `--reasoning-parser nemotron_3`. The model card's Day-0 tag
  `lmsysorg/sglang:dev-nemotron3-5-lightning` is **not** used on the first attempt.
- **Fallback (only if smoke fails).** The Day-0 image, pinned by digest for this machine
  (linux/arm64):
  `lmsysorg/sglang@sha256:ee63304703432429d55cf2e4579b70c5a334ed4cc49194fb5290c077fcbbd4a0`
  (index `sha256:a04d9a1a7ffe371b05230aecab001d4ba2bfa0e5c137bc56409ecc4cbc3ac864`). Switching to it
  needs a **new Artem decision**; the run stops and reports until then.
- **Decoding.** Model card reasoning ON: temperature 1.0, top_p 0.95,
  `chat_template_kwargs.enable_thinking = True`; max_tokens 16,000 as in the card examples.
- **Chat template.** `runs/qx2_ladder/pinned/nemotron35_lightning_chat_template.jinja`, sha256
  `58933db77d3099b4f78c55a38347a72e1ea05b97d6bd8f38775303dc0194e0a9` (from the NVFP4 revision
  above; date fixed 2026-11-15).
- **Reasoning.** It is stored for every call.
- **Response format.** The same QX-2 strict schema `qx2_cell_decision_v1`.

## Gates

- **Format.** As locked for QX-2: more than 4 fallbacks or truncations in the first 400 decisions
  stops that model's arms.
- **Smoke check (Nemotron only, the first live step after the go).** Twenty generation-1 prompts:
  10 from each B, the cells listed in the dry build. They are run before the arms and count against
  the format gate. If more than 2 of 20 answers fail the schema, the run **stops and is reported**;
  the Day-0 digest above is the fallback and needs a new Artem decision. The 20 answers are kept,
  and they are not part of any arm. The smoke check also measures calendar s/call for the Nemotron
  wall estimate.
- **GPU.** The usual precheck: manifest sha, free GPU, no foreign SGLang. The monitor runs beside it.

## Readout (descriptive)

For each arm, the same items as the completed Luna readout:
- abandonment and recovery, beside the scripted references;
- first refutation;
- test descriptives and the δ-share;
- the message mix, with own and relayed results;
- refuting results shared, with senders;
- the finder breakdown;
- signal use by message content;
- calls and GPU time.

One table puts all four models side by side per cell. The readout has no contrast and no p-value.
Each arm is one replicate.

## Dry build (CPU, no model call)

1. **Prompt identity.** The generation-1 prompts for B = 1 and B = 4 equal `gen1_B1.txt` and
   `gen1_B4.txt`.
2. **Request bodies.** For each model, they match the decoding stated above.
3. **Cache key.** It includes the arm. Two arms with the same prompt get different keys.
4. **Fake client.** It runs the eight arms through the engine, with every invariant asserted.
5. **Wall time.** Calendar time = per-request latency / concurrency 4. For 120b: from the measured
   QX-2 prompt and answer lengths and the 120b batch rate → about **18 h** as a lower bound. For
   Nemotron: unknown until the smoke check measures s/call.
6. **Nemotron pins.** Repository, revision, template sha, engine (pinned image + parser) and card
   settings, each with its source.

## Outputs

- Calls (final text, reasoning and usage), traces and the readout.
- A recheck package with SHA256SUMS.

Nothing enters the QX page before the reviewer's recheck from raw data.

## Queue

1. `wait_topology_random8_done`.
2. `wait_go_qx2_ladder`, which needs a go file and a switch-log line with Artem's words.
3. Precheck.
4. 120b: arms 1–4, with its own server start and stop.
5. Nemotron: smoke check on the pinned image, then arms 5–8 (or stop if smoke fails).
6. Readout.
7. Package.

The Qwen temperature battery (`AMENDMENT_QWEN_TEMPERATURE.md`) moves after this amendment.
