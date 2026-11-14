# Amendment — panel wave 2a: one-pass decision agents on open weights (AnyJev L0 and Tacit-4B)

**Status:** locked 2026-10-25, after the dry build in `runs/model_panel/wave2_gate.json`.
No call was made before this lock. The live gates (answer mass m, pilots) run before the local
arms. LM-dec-fact starts on the API after this lock, under its cap of $3.8934, and stops if that
cap is reached. The shared envelope stays below $20. Basis:
- `MODEL_PANEL_PLAN.md`;
- the class-B 0/8 section of `runs/model_panel/panel_summary.md`;
- the AnyJev technical report (Zhang et al., arXiv 2610.00831v1, read in full);
- the AnyJev README and `docs/limitations.md`;
- the Tacit-4B model card;
- `DESIGN_AUDIT_CHECKLIST.md`.

## Why

The project question is whether collective intelligence can arise among one-pass decision agents
only. So far every one-pass arm fails the individual capacity that the lattice win rests on: checking
the cell's own example against a unanimous contrary inbox. Class-B 0/8 fit is:

| arm | type | fit |
|---|---|---|
| LM-dec | one pass | 0.10 |
| LM-none | one pass | 0.225 |
| Qwen-Instruct | one pass | 0.30 |
| Qwen-Thinking | reasoning | 0.925 |
| Luna medium | reasoning | 1.00 |

That slice is world-3 cells. AnyJev offers two kinds of one-pass agent on open weights:
- **L0**, a training-free readout. Its report says it "cannot reason": the capability is the base
  model's.
- **Tacit-4B**, self-distilled from Qwen3-4B's own reasoning into one forward pass, according to its
  model card. The card does not give the training recipe, and the report covers L0 only.

If Tacit checks, it is the first one-pass agent with a witness veto. Its population run then answers
the project question directly.

## Arms (battery: the 960 panel prompts plus the 200 class-B 0/8 filter draws)

| arm | model, pinned revision | decision path |
|---|---|---|
| W2-q3-think | `Qwen/Qwen3-4B` @ `1cfa9a7208912126459214e8b04321603b3df60c`, thinking on | generation; the panel prompt and parser; thinking-mode decoding from the card: temperature 0.6, top_p 0.95, top_k 20, min_p 0 (https://huggingface.co/Qwen/Qwen3-4B) |
| W2-q3-L0 | same revision | AnyJev `Decider`, L0: all K rotations, prior `none`, options sorted by text before rotating |
| W2-tacit | `morriszjm/Tacit-4B` @ `af3fa1dc3cd98f937ab2ccedd4df8613fce5f1e5` | Tacit one pass, options in sorted order, no rotation, `adaptive=False` |
| W2-tacit-L0 | same revision | AnyJev L0 on the Tacit checkpoint: all K rotations, prior `none`, sorted |
| W2-tacit-adapt | same revision | Tacit with `adaptive=True` at the card defaults (tau 0.5, max_cot_share 0.2, cot window 1000, cot_max_tokens 8192) |
| LM-dec-fact | Luna Decisions | the factorized question below, P = 4 orderings, argmax of the average; the control for the factorization |

**AnyJev version.** PyPI package `anyjev` 0.3.0. Git tag `v0.3.0`, commit
`1ffa57b5287572cd173e1dc83d8a8f2e8dedca00`
(https://github.com/nokia-applied-research/AnyJev/commit/1ffa57b5287572cd173e1dc83d8a8f2e8dedca00).
The tag's `pyproject.toml` version is 0.3.0.

**Same base.** W2-q3-think is the reasoning reference with the same base weights as Tacit-4B. Tacit
counts under its Qwen base in the panel, as the panel plan states. Qwen3-4B is the hybrid model, not
Thinking-2507, so it is a new reference and is not merged with QI-1m. Both pinned configs are
`Qwen3ForCausalLM` with native context 40,960. The longest battery prompt under the Qwen3-4B
thinking template is 2,078 tokens, so 2,078 + 32,768 is 34,846 and fits that context.

**Prior.** The prior is `none` because the label prior in L0 is a running batch mean. The report
states that it lowers accuracy when one label dominates, and a population under consensus is that
case. With `none`, L0 is rotation averaging only, which matches LM-dec's ordering average. Content-free
prior arms are not run: the report says AnyJev offers that estimator but does not test it.

## The factorized rule question

The letter readout supports at most 26 options. The catalog has 101 rules. Every arm except
W2-q3-think therefore answers the rule question in two steps, with option sets fixed now from the
catalog. Q1 has 17 options and the largest Q2 has 12, both at most 26. Q1, in sorted
order, is `reverse`, `rotate_left(1)`, `rotate_left(2)`, `rotate_left(3)`, `shift_symbols(1)`
through `shift_symbols(7)`, and the six swaps `swap(0,1)`, `swap(0,2)`, `swap(0,3)`, `swap(1,2)`,
`swap(1,3)`, `swap(2,3)`. Each Q2 is the second operations paired with that first operation in the
catalog, plus "no second operation" when the first operation alone is a catalog rule. The sets
rebuild the 101 rules with nothing missing and nothing extra. Labels are the letters A onward in
that order. Each of those 17 letters is one distinct token in both the Qwen3-4B and the Tacit-4B
tokenizer. The option list is the full set. The full Q2 lists are in the gate JSON.

- **Q1:** "Which is the first operation of the hidden transformation?" The options are the distinct
  first operations of the catalog rules.
- **Q2, given the Q1 answer o1:** "Which second operation follows it?" The options are the second
  operations o2 for which `o1;o2` is in the catalog, plus "no second operation" if `o1` alone is in
  the catalog.

The decision is greedy: the argmax of Q1, then the argmax of Q2 given that answer. A tie in an
averaged distribution is broken by sorted option text. The named rule
is `o1;o2` or `o1`, and it is always a catalog rule.

**Factorization caveat, stated before any result.** Q1/Q2 name the structure "first operation, then
second", which is the prefix-plus-swap form of P_e. The factorization could itself help composition.
LM-dec-fact separates that effect: it is Luna Decisions with the same two questions, against the
existing one-question LM-dec. The state text is the LM-dec state, quoted from the code, and is the
same for every decision arm. On all 1,160 prompts the state is the byte prefix before
`\n\nRule catalog (choose by key):\n`. The first state is 1,770 characters. Publish and signal are not asked; the battery scores the
named rule only.

**Draws.** L0 and Tacit one pass are deterministic, so they run 1 draw per prompt, and the readout
states n per arm. W2-q3-think and W2-tacit-adapt (escalation is generation) run the panel's 2 draws.

## Gates (live calls refused unless stated)

- Answer mass m, as defined in the report, on 20 pilot states per decision arm: median m ≥ 0.99 per
  question. Below that, the arm is "not run", with m stated. The report found m = 0 on a template
  fault.
- The decision state is byte-identical to LM-dec's state text for the same prompt.
- The Q1/Q2 option sets reconstruct exactly the 101 catalog rules, with nothing missing and nothing
  extra.
- Tokens: every label is one token in each tokenizer, and the label set is read in full, not from a
  top-20 list.
- Pilot: 20 calls per arm outside the battery, with the panel rule (more than 1 failure stops the
  arm). For W2-q3-think, truncation at the cap counts as a failure.
- Cost: LM-dec-fact is 1160 × (P = 4) × 2 questions = 9,280 Decisions calls. The mean stored
  LM-dec input is 2,097.76 tokens, from the 1,920 cache bodies. At the list rate of $0.10 per
  million input tokens the cold estimate is $1.9467. The cap is twice that, $3.8934. Spent
  $9.8365, remaining $10.1635 of $20. The cap fits. Those stored questions offer 101 options, so
  the estimate is above the cost of Q1 and Q2.

## Measures (per arm)

- **Checking:** class-B 0/8 fit, with the panel hull. Also composition: P_e, prefix, other fitting,
  other non-fitting.
- **Conformity:** prefix / (prefix + other non-fitting), with its hull. A denominator under 5 is n/a.
- **The panel fingerprints:** S, L, ally, count, top and filter. Also U1 and U2.
- **Answer mass m** per question.
- **Escalation share** for W2-tacit-adapt, and fit split by route (one pass or escalated).
- **Order sensitivity** for W2-tacit: the share of answers that change when the option order is
  reversed, on 40 states. This is descriptive; the authors did not measure it.

## Predictions (locked)

The unit is the source cell (20 class-B cells at 0/8). One-sided cell-level sign-flip, α = 0.05.
Wilson and Fisher go beside it and are not scored.

- **T1 (self-distillation transfers checking):** fit(W2-tacit) > fit(W2-q3-L0) on class-B 0/8.
- **T2 (reasoning reference):** fit(W2-q3-think) > fit(W2-q3-L0). This is the manipulation check on
  the pair. If T2 fails, T1 is reported but not read.
- **T3 (factorization alone):** fit(LM-dec-fact) > fit(LM-dec) on the same 20 cells. LM-dec has 10
  ties at P = 4; they are resolved as in its readout.
- **Classification, not a test:** the hull of each one-pass arm's fit, against W2-q3-think and
  W2-q3-L0 as references, by the panel hull rule: matches reasoning, matches one pass, or neither.

## Full-run trigger (locked)

A one-pass arm (W2-q3-L0, W2-tacit, W2-tacit-L0 or W2-tacit-adapt) gets a lattice full run in world 1
if either holds:
- its fit hull excludes W2-q3-L0's fit;
- it fails U1.

The full run gets its own amendment. Its protocol needs publish and signal questions, which are not
designed here.

## Pre-stated readings

- **T2 passes, T1 passes:** Qwen3-4B's own reasoning, distilled into one pass, carries checking. If the
  hull matches the reasoning reference, a one-pass agent has the individual capacity the lattice win
  needs, and the full run tests the collective.
- **T2 passes, T1 fails:** the distillation does not carry checking on this task. One-pass checking
  stays absent across Luna and Qwen, and "intelligence in the protocol" becomes the remaining route.
- **T3 passes:** the factorized question raises Luna Decisions' fit by itself. Every factorized arm's
  fit is then read net of that, and the protocol change is a result in its own right.
- **W2-tacit-adapt:** the escalation share and the fit by route say whether reasoning on hard cases
  alone recovers checking. Class-B 0/8 is a hard case by construction.
- **If the design is the cause:**
  - Greedy Q1 → Q2 can lock in a wrong first operation. The readout reports Q1 accuracy, meaning the
    share whose o1 fits the example's first step, where defined.
  - The decision arms see the LM-dec state, not the generation prompt. They are compared on outcomes.
  - Tacit's training prompt differs from ours. It is the one-forward prompt in `tacit_decision.py`
    at the pinned revision `af3fa1dc3cd98f937ab2ccedd4df8613fce5f1e5`. The file calls it the prompt
    Tacit was trained on. System text, verbatim:

    `You are a decision function. You will be given a state and one question. Reply with the answer label only: no words, no punctuation, no explanation.`

    User text for a choice, verbatim in structure:

    ```
    State:
    <state>

    Question: <question>
    Options:
    A. <option>
    Answer with the letter only.
    ```

    The labels are `A`, `B`, `C`, ... and each option line is `"{label}. {option}"`.

## Design audit

1. **Fidelity.** The state text is identical to LM-dec's. The option sets are derived from the catalog
   by code and checked by a gate. The pinned revisions and the AnyJev version are recorded.
2. **Coverage.** The battery only, world-3 source cells, as in the rest of the panel. The world
   restriction of the 0/8 slice, stated in `panel_summary.md`, applies.
3. **Controls.** W2-q3-L0 is the untrained one-pass control for Tacit. W2-q3-think is the reasoning
   reference on the same base. LM-dec-fact is the factorization control.
4. **Observability.** Decisions are read from the label distribution only. m is reported before any
   accuracy.
5. **Gate consistency.** All gates above run together, with live calls refused, before the pilots.
6. **Statistical unit.** 20 class-B source cells for the scored tests, with paired sign-flips over the
   same cells. This is small, and stated. The power for T1 at fit 0.30 against 0.70 is 0.882,
   from 2000 simulations at the observed per-cell spread. The off arm uses the Instruct slice,
   where the two draws agree inside every cell (ICC 1.0). The on-rate arm uses the Thinking slice,
   whose ICC is −0.056, so those draws are independent. Both arms independent give 0.9545. Numpy
   Generator seed 1 for the ICC run and seed 3 for the independent run.
7. **Pre-stated readings.** Above.

## Queue

After the current local queue (W1-oss20 full, then moore). The arms run in the order W2-q3-L0,
W2-tacit, W2-tacit-L0, W2-tacit-adapt, W2-q3-think. LM-dec-fact runs on the API in parallel, after
the lock.

**Erratum (Artem, 2026-11-14; queue order only).** "After the current local queue" is superseded. Wave 2a
runs after wave 2b, 120b Stage 2 and Flint-NVFP4, by Artem's go of 2026-10-27 (`MODEL_PANEL_PLAN.md`,
entry "2026-10-27. Artem’s go. … Queue reorder: … → wave 2b Gemma/Nemotron off and on → 120b Stage 2 →
Flint-NVFP4 (CUDA hash gate) → wave 2a"; the same order in `RESEARCH_ROADMAP.md`). The arm order within
wave 2a is unchanged. No setting, prediction or analysis changes. The cited plan entry was committed on 2026-11-14 with a provenance line (corroborated by
`RESEARCH_ROADMAP.md` as committed on 2026-10-28; commit ids in the private provenance log).
