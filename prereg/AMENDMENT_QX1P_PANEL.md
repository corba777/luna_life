# Amendment — QX-1p: test choice under a false consensus, across the panel

**Status:** locked 2026-10-27, after the dry build
(`runs/life_dr_qwen/qx1p/dry_build.json`), every design-audit item below passes. Local arms are
pre-approved; the Luna arms run inside the $100 envelope. No call before this file is committed as
locked. No server is loaded for QX alone. Basis:
- `AMENDMENT_DR_QWEN_QX1.md` (locked) and its readout and descriptives;
- `QX_TRACK_PLAN.md`;
- `MODEL_PANEL_PLAN.md` and `AMENDMENT_PANEL_WAVE2_MODELS.md` (serving and decoding of each model);
- `DESIGN_AUDIT_CHECKLIST.md`.

Origin: Michal Valko's question (seed a shared wrong hypothesis and let agents choose their own
experiments). This step, like QX-1, measures the choice only. No test output is returned.

## Why

QX-1 on Qwen3-4B-Thinking found a narrow consensus shift (confirming share C1 0.438 against C0
0.362, sign-flip p = 0.048) on top of a large individual bias (C0 far above 1/8). The descriptives
then showed that the "confirming" share is mostly the share of constant inputs such as `AAAA`,
which have x_i = x_j for every pair (i, j) and so confirm the prefix in every world. Constant and
`ABCD`-type inputs made 384 of 480 tests. A test that confirms because it is constant is not
aimed at the shared hypothesis. The measure has to separate aimed confirmation from inputs that
confirm everything.

The panel question is whether this pattern is a property of Qwen or of LLM agents, and whether
reasoning changes the individual bias, the social shift, or neither.

## Measures

For a test input x from a cell of world w with swap pair (i_w, j_w):

- **confirming:** x_{i_w} = x_{j_w} (as locked in QX-1);
- **cross-world null:** the mean, over the two other worlds' pairs (i_v, j_v), v ≠ w, of
  1[x_{i_v} = x_{j_v}]. It is the confirming rate the same input would have if it were not aimed at
  this world's pair;
- **aimed confirming:** confirming minus the cross-world null, per call. It is exactly 0 for
  constant inputs. For any input distribution that does not depend on the world, its mean over the
  three worlds (equal cell counts) is 0; within one world it need not be, because the three pairs
  share position 3. The arm-level measure therefore pools the three worlds;
- **pattern class** (from `runs/life_dr_qwen/qx1/readout.md`): letters are relabeled in order of
  first appearance. **AAAA** = any one-letter string (constant). **ABCD** = four distinct letters
  (the all-distinct class — not the literal string `ABCD` alone). **other** = the rest. On QX-1,
  AAAA 175 + ABCD 209 = 384 of 480;
- descriptive, as in QX-1: whether the test separates the prefix from another rule in S_c, against
  the per-cell random baseline over all 4,096 inputs; the named rule and whether it left the prefix.

## Design

Unchanged from QX-1 for every arm: the same 480 prompts (3 worlds × 20 class-A cells × C0/C1 × 4
draws), byte-identical to the QX-1 prompt set (sha256
`c58f90b5328776b450fc182ea1748c2bda33c30caf9c78467269eee2f78c0d8e`, matches
`runs/life_dr_qwen/qx1/MANIFEST.json` and `gate.json`), the same added sentence and `test=XXXX`
field, the same parser and exclusion rule (more than 5 % failures in a condition: reported, not
tested).

## Arms

| arm | model | mode | serving window |
|---|---|---|---|
| QXp-lmmed | Luna | Responses, effort medium | API, any time |
| QXp-lmnone | Luna | Responses, effort none | API, any time |
| QXp-oss120 | gpt-oss-120b | default, fixed-date template pin | after 120b Stage 1 calls finish, before the server stops |
| QXp-oss20 | gpt-oss-20b | default, fixed-date template pin | with the 20b date check, after its calls finish |
| QXp-gemma-off / -on | Gemma-4-E4B | thinking off / on | wave 2b, after each mode's locked calls |
| QXp-nemo-off / -on | Nemotron-3.5-Bolt-E4B | thinking off / on | same |
| QXp-flint | Flint-NVFP4 | model-chosen | after its locked calls |
| QXp-qi | Qwen3-4B-Instruct | no thinking | with QX-1r, wave 2a |

Qwen3-4B-Thinking is the QX-1 arm and is not re-run here; QX-1r is its replication.

Not run, with reasons fixed before any QX-1p result:
- Luna Decisions, AnyJev L0 and Tacit-4B: decision agents pick from listed options and cannot write
  a free test input.
- Spark: closed on 2026-10-27 (sampler diagnosis incomplete, no further Spark runs).

Every model uses the decoding, template and server settings locked in its own panel amendment.
QX calls never share a batch with another arm's calls: each QX arm starts after that server's locked
arm has written its `run.ok`, so batching cannot couple the two.

Cost (dry build, Part H Luna medium USD on round-4-derived prompts × QX char-ratio 1.035, list rates
including cache_write; none scaled by P1 S0-lmnone/S0-lmmed = 0.0448/0.1650):
- QXp-lmmed: **$0.259** / 480, cap 2× = **$0.518**;
- QXp-lmnone: **$0.070** / 480, cap 2× = **$0.141**;
- both arms estimate **$0.329**, at cap **$0.658**, under the $100 envelope.

Local wall time per arm (dry build):
- thinking-arm reference (QX-1 Thinking, 480-call cache mtime span): **2.64 h** (19.8 s/call);
- gpt-oss-120b estimate from battery 11.667 s/call: **1.56 h**;
- Instruct / thinking-off arms: shorter than the thinking reference; not separately measured.

## Predictions (locked)

The unit is the cell, 60 per arm, with draws pooled. One-sided paired sign-flip over cells,
20,000 flips, seed 0, α = 0.05, per arm.

- **X1 (consensus shift, as locked in QX-1):** P(confirming | C1) > P(confirming | C0). Scored per
  arm, reported as a count of arms passing.
- **X1a (aimed shift):** mean aimed confirming in C1 > in C0. This is the primary measure for the
  panel: X1 can pass through more constant inputs under consensus, X1a cannot.
- **R-pairs (does reasoning change the individual bias?):** for each same-weights pair (Luna
  medium/none, Gemma on/off, Nemotron on/off), the C0 confirming rate and the C0 aimed confirming
  rate differ between modes. Two-sided paired sign-flip over the same 60 cells, α = 0.05. No
  direction is predicted.

Not predicted: the level of any arm against 1/8, the pattern distribution, and which arms pass.
Those are the typology.

Reference for "same as Qwen": each arm's C0 confirming rate and X1a effect are classified against
QX-1 Qwen (and, once run, QX-1r) by the panel hull rule (Wilson 95 % ∪ cell-cluster bootstrap 95 %).

## Pre-stated readings

- **X1 passes and X1a fails in an arm:** the consensus shift in that arm is a shift toward
  constant-type inputs, not toward tests aimed at the shared hypothesis.
- **X1a passes:** that agent, under consensus, chooses inputs that specifically cannot refute the
  shared rule. Confirmation bias aimed at the hypothesis, induced socially.
- **Both fail, aimed confirming ≈ 0 in both conditions:** the agent's tests carry no information
  about the hypothesis either way; whether experiments would help a population then depends on the
  separation rate, not on bias.
- **R-pairs differ:** reasoning changes the individual test choice in that model. Reported per
  pair; no family claim from one pair.
- **If the design is the cause:** the added sentence and memory line are constructed and identical
  across conditions and models. The cross-world null removes any preference that does not depend on
  the world's pair. A model whose answers fall outside 4-letter strings is reported through the
  parse rule.

## Gates (live calls refused unless stated)

Dry build 2026-10-27 (`runs/life_dr_qwen/qx1p/dry_build.json`, `live: refused`,
`no_server_loaded: true`):

- Prompt identity: digest `c58f90b5…` matches the QX-1 set; only the chat template differs by model.
  **Pass.**
- Confirming and cross-world / aimed checks on all **4,096** inputs (12,288 world×input aimed
  evaluations): constant inputs give aimed confirming 0 in every world; the uniform distribution
  (and the exhaustive mean over all inputs) give 0 in every world; QX-1 Qwen tests reassigned to all
  three worlds give pooled mean aimed 0. **Pass.**
- Per-arm serving: the arm's own locked settings, template hash shown on one rendered prompt, the
  sampler gate as already passed for that server (at run time).
- Ordering: the QX arm's runner refuses to start while that server's locked arm has no `run.ok`.
- Luna cost cap and envelope projection (above).

## Design audit

1. **Fidelity.** Same 480 prompts as QX-1 (digest match). Scoring functions are pure functions of
   the test string and world; checked on the full 4,096-input cube. Pass.
2. **Coverage.** Worlds 1, 3, 5, class A; arms span size, developer, post-training and reasoning
   mode. Spark closed by prior go. Decision agents excluded with a fixed reason. Pass.
3. **Controls.** C0 against C1 within an arm; cross-world null within a call; same-weights pairs for
   reasoning. Pass.
4. **Observability.** The cell sees its prompt only; no test output is returned. Pass.
5. **Gate consistency.** Prompt identity, aimed checks on 4,096 inputs, cost and wall estimates run
   together in the dry build and pass. Pass.
6. **Statistical unit.** The cell, 60 per arm. Power for X1a at the QX-1 Qwen per-cell
   aimed-confirming rates (2,000 bootstrap sims, seed 0): **0.649**, below 0.8. Stated; design not
   changed after the number was seen. Observed aimed mean diff on QX-1: +0.0458 (MC sign-flip
   20,000 flips p ≈ 0.0016; 13 of 60 cell diffs nonzero). Pass.
7. **Pre-stated readings.** Above. Pass.
8. **Chat-template date/time.** gpt-oss arms use the locked fixed-date pin
   (`chat_template_date_20261022.jinja`). Other arms follow their panel amendments. Pass.

## Queue

As in the serving-window column: no server is loaded for QX alone. Luna arms after the lock.
QX-1r goes with wave 2a. QX-2 and QX-3 (DiG-bench) after wave 2, each with its own amendment.
