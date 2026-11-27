# Amendment — Who Speaks First, Claude Haiku 5.5 without the channel (world 1)

**Status:** draft v4, 2026-11-27 (v1 166ceeb2…; v2 fc634cc7… added the source guard; v3 a9a8336d… kept the Stage-3 schema and closing paragraph, as gpt-6-luna DRs did; v4 takes the Stage-3 epoch pin, 41, instead of 21). Not locked. No call before lock and Artem's go.
**Parent:** `AMENDMENT_LIFE_HAIKU55.md` (locked v1 `7e7611c6…`), Stage 3 runs `runs/life_haiku55/stage3/{lattice,all}/r{1–4}`.
**Label:** Claude Haiku 5.5 · world 1 (P_e `shift_symbols(1);swap(2,3)`, 25 witnesses) · **no channel** (nothing delivered, no publishing) · 100 cells · 20 rounds · replicates 1–4 · no reasoning stored.

## Why

Every Who Speaks First population of every model had the channel. Without a no-channel arm the topology results say how a model uses the channel, not whether it helps. Haiku is the case where this is open. In Stage 3 class-A cells almost never named P_e, so x is the witness share. On the lattice a witness off P_e moved to P_e at about the same rate with no P_e line in its inbox (31 of 198, 0.157) as with 1–2 (0.13) or 3+ (0.10). That alone, with the leaving rate 17 of 351 (0.048), gives a level close to the lattice level (0.189). On `all` the level was higher (0.245). The arm tells whether the lattice level needs the channel at all, and whether the `all` level is the channel's effect.

## Arm

One arm, **NC**: the Stage-3 lattice request with the channel off. Topology does not matter without messages, so there is no lattice/`all` split.

- Builder: the Stage-3 builder (`DistCompleter`) with the no-channel constitution used by gpt-6-luna DRs and Qwen3-4B-Thinking DRs_T (`run_life_distributed_phase1.py`: `_WORLD_DIST`, `_SEES_NO`, `_TAIL_JSON_NO`; no `_PUBLISH`) and `SimulationV1b(channel=False)`.
- Same world record (`world_audit.json` by_seed["1"], example sha256 `6d8792a6…`), epoch pin 41 as in Stage 3 (builder `stage2`, pinned on the engine, v1a and `PINNED_EPOCH`; all 20 rounds are epoch 0, as in Stage 3), k = 0. **No seeded sources in any round:** as in Stage 3, the source list stays empty (`source_ids_override(())`) around every step, not only while the grid is built, and `source_raw_decision` is replaced by a function that raises. Every round must have 100 completer calls (cached or live) and an all-false `source_mask`. (The Qwen3-4B-Thinking no-channel pair of 2026-10-16/17 ran with cells 0, 5, 50 and 55 fixed on P_e because the override covered only the build.)
- Model, decoding and request envelope: those of Stage 3 (model id, thinking and output_config as locked in the parent). Output schema and closing instruction paragraph: those of Stage 3, unchanged. Both name the `communication` field, as they did for gpt-6-luna DRs (stored DRs requests: same paragraph, schema `life_cell_decision_v2` requiring `communication`). A published `communication` is accepted by the parser and dropped by the channel-off encoder: nothing is delivered and the memory line says `published=no`. A reply without `communication` is invalid, as in Stage 3.
- Memory line from round 2: `Previous step: rule='…' published=no.`
- Replicates r1–r4, fresh empty cache per run, no resume. Stored per call: final text, stop reason, usage, request fields actually sent. Never reasoning. `cell_states.jsonl` per round in the Stage-3 format (inbox_lines must be 0 everywhere).

## Prediction (locked with this file)

Derivation: `nc_predict.py`, 20,000 bootstrap draws. Each witness is a two-state chain with the Stage-3 lattice rates measured with **no P_e line in the inbox**: off→on p = 31/198, on→off q = 17/351 (Beta(k+1, n−k+1) for each draw). The round-1 count is drawn from the eight Stage-3 round-1 counts (7, 9, 14, 13, 13, 9, 13, 13). Class-A cells are held off P_e. x(10–20) is the mean share on P_e over rounds 10–20.

- **NC1 (main):** the mean x(10–20) of the four NC runs lies in **[0.159, 0.209]** (5–95 % of the chain). Single-run band, descriptive: [0.150, 0.216].
- **NC2:** every NC run has x(10–20) below every Stage-3 `all` run (minimum 0.2427). Exact one-sided permutation over the 4 + 4 runs: complete separation is p = 1/70.

The band covers parameter and sampling uncertainty only. It excludes structural error: transitions pooled over cells and rounds, witnesses treated as alike, and a constitution that differs from Stage 3. The record must say so.

## Readout

- **NC1 held:** the Haiku lattice level is reached without the channel. Witnesses arrive at P_e from their own example over rounds. The measurable channel effect for Haiku is the `all` level only (NC2).
- **NC1 below 0.159:** the lattice channel adds to the witness share, or the no-channel constitution lowers re-derivation. The NC3 rates separate the two.
- **NC1 above 0.209:** without the channel witnesses do better than the chain from lattice rates.
- **NC2 not held:** the `all` gain is not shown to be a channel effect.

**NC3 (descriptive):**
- witness off→on and on→off rates in NC against the Stage-3 zero-line rates;
- round-1 witness count on P_e against the Stage-3 round-1 counts (effect of the constitution text alone);
- class-A cell-rounds on P_e;
- the rules named by witnesses off P_e.

## Dry build (CPU, before lock)

1. Round-1 prompts of all 100 cells against Stage-3 lattice r1 round-1 prompts. The diff may contain only the constitution strings named above and the absent message-slot block. Examples, query, memory line, catalog (as a multiset) and cell header must be equal.
2. Request body against Stage 3: equal, schema included.
3. Stub run of 20 rounds: `source_mask` all false and 100 completer calls in every round, `source_raw_decision` never called, inbox_lines 0 in every cell-round, a published `communication` accepted and ignored (nothing delivered), memory line `published=no`, the readout code computes NC1, NC2 and NC3.
4. Projection at no-inbox prompt length, and the start rule below.

## Money

Ceiling **$20** (Artem, 2026-11-27), hard stop on this amendment's own spend. Start rule: projection × 1.5 ≤ ceiling. Upper bound before the dry build: 8,000 calls at the Stage-3 rate (16,000 calls, full inboxes) ≈ $5.8.

## Constraints

New runner file, no edit of a running script. No closed-model output used for training. Predictions above are not changed after any NC call. Page entry only after the reviewer's recheck, with the runs in the viewer.