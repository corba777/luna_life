# Task — Can a one-pass cell learn the check? Distilling stage 1 from reasoning traces

**Status:** draft for lock. Predictions are locked with this file, before any teacher call. GPU task
(SGLang + Unsloth, local). Does not preempt the SPADE grid: start Phase 0 after `cot.ok`.
Related: Life C-L2/C-L3 (two-stage correction), arXiv 2610.12176 (MASS: multi-agent behaviour
internalized by SFT).

## Why

On the grid, collective correction has two stages:
- **Stage 1:** reject an incoming rule that is inconsistent with the cell's own example. Reasoning
  cells do this 98% of the time; one-pass cells lack it (70/70 one-pass adopters had first been told
  "wrong").
- **Stage 2:** switch when told "wrong" and P_e is in the inbox.

Without stage 1, a one-pass grid needs an external check (Da) or it crowds onto false rules (Ca).
MASS shows that coordination behaviour (delegation, handoffs) carries over from multi-agent traces
into a single model's weights. Here the behaviour to carry over is epistemic: the consistency check.

**Question:** does a one-pass student fine-tuned on a reasoning teacher's decisions acquire stage 1,
and does a grid of such students then reach the truth without an external check?

## Constraints

- **Teacher and student are open models only.** No Luna or other closed-model output enters
  training, including Life logs: their inbox contents are Luna choices. All training situations are
  generated from the environment (below).
- **Same prompt as the Life one-pass cell**, for teacher (thinking on) and student (thinking off).
- **Train on the teacher's final decision only** (the chosen catalog rule). The teacher's reasoning
  text is not a training target; it may be stored locally for the loop/length diagnostics.
- **No filtering of teacher decisions by correctness.** The student distils the teacher, errors
  included. Correct labels are a separate arm (SO).

## Part 0 — Situation bank (no model)

A situation = (world rule P, the cell's private example, held rule, feedback "right"/"wrong",
inbox = list of (rule, n_neighbours)). It is generated from the catalog and the engine, as Life
generation ≥ 2 would present it.

Strata (balanced):
- feedback ∈ {wrong, right}
- inbox contains P: yes / no
- number of incoming rules inconsistent with the example: 0, 1, 2+; their votes: 1, 3+
- consistent competitor (≠ P, fits the example): none / one
- P is 1-op / 2-op. Include situations where the consistent choice is 1-op and the popular
  inconsistent one is 2-op, so that "prefer 2-op" or "prefer 1-op" cannot pass for a check.

**Split by world rule.** The training P set and the evaluation P set are disjoint. Evaluation P =
the five Life 2-op world rules (seeds 1–5) plus a held-out 1-op set. A student cannot pass by
memorizing which rule is true.

Sizes: train bank 3,000 situations; held-out eval bank 1,000 (separate generator seed,
`DISTILL_SEED`, committed). Report the stratum counts.

Definitions (on the eval bank):
- **stage1** = among situations with ≥ 1 inconsistent incoming rule, the share where the student
  does **not** pick an inconsistent rule. Reported by votes (1 vs 3+) and by feedback.
- **stage2** = among situations with feedback "wrong" and P in the inbox, the share that picks P.
- **stubborn** = among situations with feedback "wrong" and a consistent incoming rule, the share
  that keeps the held rule (a student that rejects everything must show up here).
- **validity**: unparseable or off-catalog outputs are counted and reported, and scored as
  "not a check" in stage1.

## Arms

| arm | model | training labels | check at inference |
|---|---|---|---|
| **T** | teacher: Qwen3-4B, thinking on (16384 cap, one retry, as SPADE grid) | — | own reasoning |
| **S0** | student base: Qwen3-4B, thinking off | none | none |
| **SD** | S0 + LoRA | teacher T's decisions on the train bank | none |
| **SO** | S0 + LoRA | oracle labels on the train bank | none |

- **Oracle policy (SO):** candidates = held rule + incoming rules; keep only those consistent with
  the example. If feedback is "wrong", drop the held rule. Pick the candidate with most neighbours;
  ties go to the held rule, then to the lower catalog index. If none survive, keep the held rule.
- SD and SO use the same LoRA recipe, steps and train-bank situations. Only the labels differ.
  Checkpoint = final step, fixed in advance; **no checkpoint selection on eval-bank or grid
  metrics.**
- Optional, if Phase 0 says it is affordable: teacher T' = Qwen3.6-27B-FP8 thinking. Report it as a
  second teacher; it does not replace T in the predictions.

## Phase 0 — Teacher gate (before any training)

Run T and S0 on the eval bank. Report stage1, stage2, stubborn and validity for both, plus
tokens per situation and loop/long-reasoning truncations for T.

Gate: proceed to distillation only if **T stage1 ≥ 0.90**. Otherwise stop and report: the open
teacher does not have the check, so there is nothing to distil. Also report the T cost per
situation and the projected GPU hours for the 3,000-situation train bank before labelling.

## Phase 1 — Grid

Life, 2-op world seeds 1–5, channel on, **no external check**, everything else as Ca (the
same prompt, memory, feedback, 4 sources, 10 generations, invariant checks). Arms on the grid:
S0, SD, SO. Add **S0+check** (Da analogue: the environment rejects incoming rules inconsistent
with the cell's example) as the ceiling. Served model and LoRA adapter hash recorded on every
response.

## Predictions (lock)

- **D0 (gate):** T stage1 ≥ 0.90 on the eval bank.
- **D1:** SD stage1 ≥ 0.80 and ≥ S0 stage1 + 0.30 on the eval bank. If S0 stage1 is already ≥ 0.70,
  D1 is reported as untestable (no gap to close), not as pass or fail.
- **D2 (no stubbornness):** SD stage2 ≥ S0 stage2 − 0.05, and SD stubborn ≤ S0 stubborn + 0.10.
- **D3 (primary, grid):** SD J at g10 > S0 J at g10 in ≥ 4/5 seeds.
- **D4:** SD false locks at g10 ≤ S0 false locks at g10 (count over 5 seeds).
- **D5 (descriptive):** SD vs SO on the bank and grid, and both vs S0+check. No direction is
  predicted.

## Readout

- D1 + D3 PASS → the check distils. A one-pass cell trained on a reasoning teacher's decisions
  carries stage 1, and the grid no longer needs the environment to filter claims. This is the
  epistemic counterpart of MASS's internalized delegation.
- D1 PASS, D3 FAIL → the check is learned on the bank but does not carry to the grid (distribution
  shift between generated situations and live inboxes). Compare the bank strata with the grid
  inbox composition.
- D1 FAIL → one-pass capacity or label sparsity is the limit. Compare SD with SO: if SO passes and
  SD does not, the teacher's labels are the bottleneck, not the student.
- D2 FAIL → the student learned to ignore incoming rules, not to check them.

## Artifacts

- `runs/life_distill/bank/{train,eval}.jsonl` + `bank_strata.json`
- `runs/life_distill/phase0_gate.json` (T, S0 on eval bank; cost; projected hours)
- `runs/life_distill/adapters/{SD,SO}/` (+ hashes, training config)
- `runs/life_distill/eval_bank_{S0,SD,SO,T}.json`
- `runs/life_distill/grid/{S0,SD,SO,S0check}/seed{n}/`
- `runs/life_distill/summary.json` (D0–D5), `fig_distill_check.png` (stage1 by votes for
  S0/SD/SO/T; J(g) on the grid for the four grid arms)

## Constraints (repeat)

Open models only for teacher and labels. No closed-model outputs or reasoning in any training file.
Commit this file before the first teacher call. Amendments before numbers. No checkpoint selection
on evaluation metrics.