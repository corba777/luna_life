# Amendment — QX-1: which experiment does an agent choose under a false consensus (Qwen)

**Status:** locked 2026-10-22, after the dry build, before any QX-1 call; every design-audit item
passes. Local, pre-approved. No call before this file is committed as locked
after a dry build that fills every **[dry build]** value. Origin: Michal Valko's suggestion (seed a
shared wrong hypothesis and let agents choose their own experiments; LinkedIn, 2026-10-22). This
first step measures the choice only and does not run the experiment.

## Why

In worlds 1, 3 and 5 the true rule P_e is the prefix followed by one swap of positions (i, j). Once
the shift is applied, the prefix and P_e give the same output on an input exactly when that input
has equal symbols at i and j:

- world 1: `shift_symbols(1);swap(2,3)` (i, j) = (2, 3)
- world 3: `shift_symbols(6);swap(1,3)` (i, j) = (1, 3)
- world 5: `shift_symbols(1);swap(0,3)` (i, j) = (0, 3)

The shift is a bijection on symbols, so "equal after the shift" is the same as "equal in the
input". A test input is **confirming** when x_i = x_j: it cannot tell the shared false rule from
the truth. A uniformly random input is confirming with probability 1/8. The examples were selected
so that the prefix fits 75 of 100. Free inputs are not, so a single free test refutes the prefix
with probability 7/8. That is why this step measures only the choice. Giving agents real
experiments on the grid would make the task solvable alone, and needs a separate design.

## Design

- **Cells:** class A only, meaning the cell's own example fits the prefix. Per world, 20 cells
  chosen by the ascending hash `sha256("qx1|{world}|{cell}")`. Worlds 1, 3 and 5.
- **Source prompt:** the cell's logged round-4 prompt from the pinned DRc replicate-1 lattice
  history, as in Part H. The cell keeps its own example and query.
- **Memory line:** `Previous step: rule='<prefix>' published=no` in both conditions. The cell holds
  the shared hypothesis. This is a constructed state, and the readout says so.
- **Conditions:**
  - **C0:** all 8 inbox slots empty.
  - **C1:** 8 prefix lines from its real Moore neighbours, in redo order, with signals drawn by the
    Part D hash from that world's prefix-signal pool.
- **Added text:** fixed now, identical in both conditions. A single sentence is inserted directly
  before the answer-format instruction: "You may also request the hidden rule's output on one
  4-letter input of your choice (letters A–H)." The answer format gets one extra field,
  `test=XXXX`. No output is ever returned. **Dry build (2026-10-22):** the sentence is its own
  paragraph between `Decide for this cell now.` and `Return a single JSON object and nothing else
  with:`. The format line is added as the last field, directly after
  `  If you publish, the named rule on the board is your inferred_rule.`, and reads
  `- test: the 4-letter input you request (letters A–H), as "test": "XXXX".` The decision schema
  gets one added required property `test`, a string constrained to the 4096 inputs over A–H (an
  enum, as `inferred_rule` already is). All other schema properties are unchanged (schema sha256
  `63d17bb7…`). The prompt end, as built:

  ```
  Decide for this cell now.

  You may also request the hidden rule's output on one 4-letter input of your choice (letters A–H).

  Return a single JSON object and nothing else with:
  - inferred_rule: exactly one catalog key (R000…) for the hidden transformation.
  - communication: either {"kind":"silence"} or
    {"kind":"publish","signal":<integer 0-7>}.
    If you publish, the named rule on the board is your inferred_rule.
  - test: the 4-letter input you request (letters A–H), as "test": "XXXX".

  Choose a catalog key even if unsure. Do not invent keys. Do not return reasoning text.
  ```

  Because `test` is schema-constrained, parse failures can come only from truncation or a broken
  JSON object. The memory line keeps the logged format, with its final period:
  `Previous step: rule='<prefix>' published=no.`
- **Draws:** 4 per cell per condition. 3 worlds × 20 cells × 2 conditions × 4 draws = 480 calls.
- **Model and settings:** Qwen3-4B-Thinking-2507 with the Stage 1 settings. Own cache, own lock,
  v2 watchdog, runtime invariants on, no auto-relaunch. Queue: after QI-I, before moore.

## Scoring

- **Parsing:** `test` must be 4 letters from A–H. Parse failures and truncations are counted per
  condition and excluded. If more than 5% of a condition fails, it is reported but not tested.
- **Confirming:** x_i = x_j, using the (i, j) of the cell's world.
- **Descriptive, per call:**
  - whether the test separates the prefix from at least one other rule in the cell's S_c;
  - the per-cell random baseline of that property, computed over all 4096 inputs;
  - the share of inputs with any repeated letter;
  - the rule the cell names, and whether it changed from the prefix.

## Predictions (locked)

The unit is the cell. Per-cell rates pool the 4 draws. The primary test is a one-sided paired
sign-flip test over the 60 cells, at α = 0.05. Beside it, reported and not scored, is a one-sided
Fisher test on calls.

- **X1 (consensus shifts the choice toward confirmation):** P(confirming | C1) > P(confirming | C0).
- **Descriptive against chance:** P(confirming) in each condition, against 1/8, with Wilson
  intervals. This is not scored, because a model's preference for simple strings is not a uniform
  draw. C0 is the control for that.

## Pre-stated readings

- **X1 passes:** a shared false hypothesis in the inbox makes the agent choose tests that cannot
  refute it. This is confirmation bias, induced socially and measured against a matched control.
- **X1 fails, both rates near or below 1/8:** the agent picks informative tests under consensus
  too. An experimenting population could escape the false consensus. The grid design is then
  worth building.
- **X1 fails, both rates well above 1/8:** the agent prefers confirming inputs regardless of the
  messages. That is an individual bias, not a social one.
- **If the design is the cause:** the added sentence might itself push toward discriminating tests.
  It is neutral by construction: it says nothing about informativeness, and it is identical in
  both conditions. The memory line is constructed. A simple-string preference shows up equally in
  both conditions and is reported through the repeated-letter share.
- **Not claimed:** anything about running the experiments, or about other models. Luna and the
  panel are possible later steps, each with its own amendment.

## Design audit

1. **Fidelity.** The base prompt is the logged DRc lattice prompt, as in Part H. The differences
   are the memory line, the inbox block, the added sentence and the format field, and all are
   listed above. **Dry build:** outside these, all 480 prompts (120 distinct × 4 draws) are
   byte-identical to the source. Gate: 0 of 120 prompts differ outside the declared blocks. An
   independent line diff against each source finds only memory lines (76; the other 44 sources
   already held the prefix), inbox slot lines, the sentence with its following blank line, and the
   format line, with 0 undeclared lines. Each prompt is exactly 3 lines longer than its source.
   **Pass.**
2. **Coverage.** Class A in worlds 1, 3 and 5, where a single swap separates the prefix from P_e,
   so the confirming condition is exact. Worlds 2 and 4 are excluded: world 2's P_e is not a
   prefix plus one swap, and world 4's prefix fits no example. **Dry build:** class A holds 75
   cells in each of worlds 1, 3 and 5. The first 20 by hash are world 1: 4, 20, 21, 27, 28, 35,
   46, 49, 50, 52, 54, 55, 58, 59, 65, 73, 79, 81, 85, 94; world 3: 10, 19, 25, 26, 40, 43, 51, 52,
   53, 59, 61, 79, 80, 84, 85, 86, 88, 92, 95, 98; world 5: 10, 13, 19, 20, 24, 25, 27, 32, 35, 37,
   48, 50, 55, 61, 68, 70, 79, 83, 92, 97. **Pass.**
3. **Controls.** C0 differs from C1 only in the inbox. **Dry build:** for all 60 cells, the C0 and C1
   prompts have the same line count and differ in exactly 8 lines, all inbox slots. **Pass.**
4. **Observability.** The cell sees its example, the catalog, the memory line, the inbox and the
   sentence. The confirming property is a function of the input it writes. **Pass.** Noted at the
   dry build: in a class-A cell, the example fits both the prefix and P_e, so the cell's own
   example input is always confirming (60 of 60). The cell's query is confirming in 5 of 60. A
   test that repeats the own example input is therefore confirming by construction. It does so
   equally in C0 and C1. The readout reports the share of such tests per condition, beside the
   repeated-letter share.
5. **Gate consistency.** The pre-lock gates run together, with live calls refused:
   - byte identity outside the declared blocks;
   - every C1 inbox has 8 prefix lines and every C0 inbox has 8 empty slots;
   - every selected cell's example fits the prefix;
   - the confirming function, checked on the world's own example inputs against the catalog
     functions.

   **Dry build:** `python runs/run_life_dr_qwen_qx1.py --gate` runs them together, with live calls
   refused and the runtime-invariant self-check run first. Every gate passes. Results:
   - identity: 0 bad;
   - inboxes: 60 C1 inboxes with 8 prefix lines, 60 C0 inboxes with 8 empty slots, 0 bad;
   - C0 against C1 outside the inbox: 0 bad;
   - class-A fit: 0 of 60 bad;
   - confirming function: in each of worlds 1, 3 and 5, prefix(x) = P_e(x) exactly when
     x_i = x_j, on all 100 example inputs (75 of which are confirming) and on all 4096 inputs
     (512 of which are confirming, 1/8);
   - schema: exactly one added property.

   Prompt digest `c58f90b5…`. The runner refuses to call if its rebuilt prompts or schema differ
   from the gated build. **Pass.**
6. **Statistical unit.** The cell, with a paired sign-flip test over 60 cells. **Pass.**
7. **Pre-stated readings.** Above. **Pass.**

## Power

Simulate 60 cells × 4 draws per condition. Set P(C0) = 0.125 and P(C1) at 0.25 and at 0.35, with
cell heterogeneity at an ICC of 0.1. Run 2000 simulations each, and record the power of the paired
sign-flip test. If it is below 0.8 at 0.25, state that. The design is not changed after the number
is seen unless the amendment is re-locked.

**Dry build (2026-10-22; `runs/run_life_dr_qwen_qx1.py --power`, seed 0, file
`runs/life_dr_qwen/qx1/power.json`).** Each cell's rate is drawn from a Beta distribution with the
condition's mean and a + b = (1 − ICC)/ICC = 9. With ICC = 0.1, the primary model draws one uniform
per cell and maps it to both conditions' rates, so the cell effect is shared across C0 and C1. The
exact one-sided sign-flip test is run at α = 0.05.

| P(C1) | power, shared cell effect | power, independent (beside) |
|---|---:|---:|
| 0.25 | 0.973 | 0.918 |
| 0.35 | 1.000 | 1.000 |

Power at 0.25 is above 0.8.