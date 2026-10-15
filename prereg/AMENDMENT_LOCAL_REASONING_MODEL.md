# Amendment — B3 model swap: SPADE → Qwen3-4B-Thinking-2507

**Parent:** `TASK_LIFE_LOCAL_REASONING.md`  
**Status:** **locked** 2026-10-15 (OK). No Step 0 until smoke PASS is reviewed.  
**Related finding:** `runs/life_local_reasoning/spade_shortcircuit.md`  
**Sizing:** `runs/life_local_reasoning/thinking_sizing_probe.json` / `.md`

## Why

SPADE-Qwen3-4B-Games short-circuits on the locked DR prompt (~25–30 completion
tokens) whenever JSON-format cues and/or `Rnnn` catalog presentation are present
(2×2 body×closer + ablations). It cannot run the locked Distributed prompt as a
reasoning cell. B3 therefore switches the **cell model**, not the prompt.

## Locked change

| | Was (task lock) | Becomes |
|---|---|---|
| Model | `spade-rl/SPADE-Qwen3-4B-Games` | **`Qwen/Qwen3-4B-Thinking-2507`** |
| Exact revision | (SPADE snapshot) | **`768f209d9ea81521153ed38c47d515654e938aea`** (HF `refs/main` at sizing) |
| Arm names | DR-S / DRs-S | **DR-T / DRs-T** |
| Sampling | SPADE card: T=0.7, top_p=0.8, top_k=20, min_p=0 | **Thinking card:** T=**0.6**, top_p=**0.95**, top_k=**20**, min_p=**0**, **presence_penalty=0** (card default) |
| SGLang reasoning parser | `--reasoning-parser qwen3` (SPADE) | **`--reasoning-parser qwen3`** — Thinking template opens `<think>` itself; only `</think>` appears in raw model output; the parser splits into `reasoning_content` + `content` |
| `max_tokens` | 16384 | **32768** (from sizing; context-length ≥ **36864**) |
| Concurrency | 64 | **64** (fallback 32 if memory requires; record which) |
| Prompt / gate hashes | locked | **unchanged** |
| Field / key parse | `AMENDMENT_LOCAL_REASONING_PARSE` | **unchanged** (bare `Rnnn` or `Rnnn: <canonical text>`) |

Prompt text, gate file (`prompts/life_local_reasoning_gate.md`), and
`luna_responses_prompt_to_local` edits stay as locked. Only the served model,
sampling, token budget, arm labels, and the Thinking-specific channel parse
below change.

## Parse channel (Thinking-2507 only)

The final JSON object is taken from **`content` only**.

| `content` | Action |
|---|---|
| Non-empty; last top-level JSON parses under `AMENDMENT_LOCAL_REASONING_PARSE` | accept |
| Empty (e.g. truncation left only reasoning) | **invalid/truncated** → one re-sample → unsolved |
| Non-empty but parse/map fail | invalid → one re-sample → unsolved |

**Never** parse JSON from `reasoning_content` for this model (even if it contains a
JSON-looking block). Reasoning text may be stored locally for diagnostics only.

### Smoke check (every smoke request)

1. `content` holds the final answer (non-empty; JSON parse succeeds under the rules above).
2. A parse of `reasoning_content` alone must **not** yield an accepted answer
   (either empty, or no valid top-level JSON under the same rules). Fail smoke if
   any request violates (1) or if `reasoning_content` alone would have been accepted.

Also: median completion tokens **≥ 200**; truncation @32768 **≤ 5%**; parse
**≥ 95%**; existing abort shares (first-draw trunc+invalid > 10%; fallback > 2%).

## Predictions

**L1–L4 text unchanged.** Readout names the model as:

> open 4B reasoning model (Qwen3-4B-Thinking-2507)

not “SPADE”. Luna DR / DRs remain the closed-model references.

## GPU-h budget (from sizing probe)

| | GPU-h |
|---|---:|
| Decisions/hour (sizing concurrency 64) | **65.85** |
| Step 0 (2 arms × 1×10×96 = 1920) | **29.16** |
| Step 1 total (2×5×10×96 = 9600) | **145.80** |
| Step 1 per arm (4800) | **72.90** |

Sizing snapshot: median=6812.0, p90=9904, max=19239, trunc@32k=0.000, would_trunc@16k=0.031, parse=1.000. Step1/arm>120? **False**.

**Stop rule:** if Step 1 projects **> 120 GPU-h per arm**, stop for a decision
before launching Step 1. Step 0 may still run after smoke PASS.

## Artifacts / paths

- Arms: `runs/life_local_reasoning/{DR_T,DRs_T}/seed{n}/`
- Summary / figure labels: DR-T, DRs-T alongside Luna DR / DRs
- Runner: `runs/run_life_local_reasoning.py` — model + sampling + arm names + content-only parse
- SPADE diagnosis (not a B3 run): `runs/life_local_reasoning/spade_shortcircuit.md`

## Constraints

- No prompt or gate hash change in this amendment.
- Mirror to `luna_life` prereg with this commit.
- Step 0 only after smoke review OK.
