# Witness direction, Stage 1a — descriptive add-on: attention mass by prompt block

Written 2026-11-09 (Artem), before any activation is read; the locked amendment
`AMENDMENT_WITNESS_DIRECTION.md` (sha256 `3cf91f25…`) is unchanged. Descriptive only: no prediction,
no test, and nothing in Stage 1 (layer, penalty, directions, σ, α_max, arms) is chosen from it. No
GPU step before `runs/oss120/continue80/queue_v21_done.json` exists; Stage 1a itself still waits for
`wait_go_witness_direction`.

## What is stored

- **Same passes.** In the 540 Stage 1a forward passes (adopt prompts, k ≥ 1), no extra pass.
- **Quantity.** For every layer (36) and every query head (32), the attention probabilities from the
  last prompt token (the token before generation) over all prompt positions, summed into four
  blocks. The four masses sum to 1 per head (checked to 1e-3).
- **Computation.** Residual capture is unchanged (same attention implementation as the locked
  Stage 1a). A hook on each self-attention module records its inputs, and the last-position
  probabilities are recomputed from the module's own q/k projections, q/k norms and rotary
  embeddings (8 key-value heads shared by the 32 query heads, scaled softmax over all prompt
  positions). CPU check before the GPU step: on a small random-weight config of the same model
  class, the recomputed last row equals eager `output_attentions` (max abs difference ≤ 1e-4 in
  float32).
- **Storage.** Per prompt, a float32 array [36, 32, 4] plus the token count of each block, hashed
  in the Stage 1a package.

## Blocks

Character spans in the user message, mapped to tokens by the tokenizer's offsets on the templated
text:

| Block | Span |
|---|---|
| inbox lines | every slot line of `Visible messages (…):` (filled and empty), first non-space character to end of line; the header line is in "rest" |
| own example | the example line(s) under `Private examples:`; the header is in "rest" |
| memory line | the `Previous step: rule=… published=….` line |
| rest | everything else: chat-template tokens, constitution, position, query, catalog, instructions, newlines and indentation, the last token itself |

A token belongs to a block only if its character span lies inside the block span. A token that
straddles a boundary goes to "rest", and the number of such tokens is reported (expected 0).

## What is reported before the Stage 1 readout

- **Cells.** Fold 1's 16 training cells only (`folds.json`, `f64dcb7f…`; the same cells as the scale
  pilot). Fold 1's 4 held-out cells (35, 52, 59, 91) are neither printed nor logged until the
  Stage 1 readout.
- **Unit.** The stored decision (draw), labelled as in Stage 1a (y = 1 if the stored decision is
  P_e).
- **Per layer and head, for each block:**
  - mean mass for adopting and for non-adopting draws, within condition. For each condition with
    both outcomes among these cells, the difference of means; then the unweighted mean over those
    conditions, as for d_f.
  - Beside it: the raw means, the number of conditions used, the number of draws per outcome, and
    the mass per token of the block.
- **Breakdown.** Reported per form (lattice, `all`) and pooled.

The 4 held-out cells' numbers are released with the Stage 1 readout, in the same table format.

## gpt-oss-20b (later, when the GPU allows)

- **Same measure, same blocks, same cells, same report.** Run on the same battery prompts as
  rendered for gpt-oss-20b's stored Part A battery (its own chat template; labels = its stored
  decisions).
- **Two architecture notes, fixed now:**
  - gpt-oss has a learned per-head sink logit. The sink is reported as a fifth share, so the five
    shares sum to 1.
  - Its sliding-window layers (window 128) cannot reach blocks outside the window. These layers are
    flagged; zeros there are by construction.
- **Timing.** Not before `queue_v21_done.json`; it is not part of the witness-direction waiter
  unless a later queue line adds it.

## Addendum 2026-11-09 — token rule and runner choices (before any activation is read)

Written while building the runner, from tokenization and stub runs only (tiny random-weight model
on CPU); no Qwen activation or generation has been read.

- **Token-to-block rule, refined.** Under "character span inside the block span", every token
  that joins a newline or indentation to a block's first character straddles a boundary: 18,760
  such tokens over the 540 prompts. Rule used instead: a token belongs to the block that owns all
  of its **non-whitespace** characters; a token with only whitespace goes to "rest"; a token whose
  non-whitespace characters fall in more than one block goes to "rest" and is counted. On the 540
  real prompts that count is **0**. Mean tokens per prompt: inbox 738, own example 5.35, memory 13,
  rest 1,910.
- **Eager check (done, CPU).** Recomputed last row vs eager `output_attentions` on the tiny
  config: max abs difference 0.0; block masses sum to 1 within 1e-3.
- **Constrained answer (gate 3).** The answer after `</think>` is constrained by a token-level
  automaton over the answer format, applied after the raw logits and before temperature, top-k,
  top-p and min-p (order checked against Hugging Face's own sampler on the stub). Whitespace runs
  between answer fields are capped at 32 tokens in the real run. CPU checks: the automaton accepts
  all 9,380 stored Qwen server answers; on the stub, 100/100 stub reasonings end in a valid answer.
- **Stub-only settings** (dry check only, never in the real run): whitespace cap 2, token cap 200,
  `</think>` forced after 6 tokens, because random weights never end their reasoning.
- **Budget stop.** A timed batch of 4 prompts before the pilot projects Stage 1b GPU hours. If the
  projection exceeds 96 h, the queue stops at `wait_go_witness_budget` for Artem's decision.
- **Scale pilot readout is blind.** It writes only invalid and truncated rates per α rung and the
  chosen α_max, never adoption.
