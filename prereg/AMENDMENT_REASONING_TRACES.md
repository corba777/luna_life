# Amendment — what the reasoning says: why Qwen does not adopt (stored traces, within Qwen)

**Status:** locked (Artem, 2026-11-13), before any trace is read. This is v2. It runs on CPU only and
does not touch the GPU queue (the signal intervention, then QX-1r).

**Change from v1.** Step 0 (`runs/reasoning_traces/inventory.json`, 2026-11-12) found no stored
reasoning for any Part A battery: not for Qwen, gpt-oss-120b or gpt-oss-20b. Reasoning is stored only
for the Qwen repro standard arm and the v23b α = 0 arm. So v1's model contrasts C1 and C2 cannot run.
v2 replaces them with contrasts inside Qwen, each against a baseline derived from the data. A
comparison with gpt-oss needs new calls and is left to a separate amendment (Part 2, below). The
features are unchanged from v1.

## Why

Qwen3-4B-Thinking is "stubborn": it adopts little below unanimity. Stage 1 of the witness direction
found no linear trace of the decision at the last prompt token, so the decision probably forms during
reasoning. This amendment asks: **when Qwen does not adopt, does it ignore the inbox, or does it read
the inbox and give a reason to keep its own rule?**

No closed-model output is used. Coding is by fixed regular expressions written before any trace is
read. No model is used as a judge.

## Data

- **Primary:** `runs/contagion/qwen_parta_repro/arm_standard.jsonl` (sha256 `88c3409b…`). This is
  SGLang 0.5.18 unpatched in standard mode, the battery's own configuration. It has 1,480 adopt
  prompts with $k \ge 1$: 23 conditions, all draws, 0 truncated.
- **Beside, descriptive only:**
  - `runs/witness_direction/stage1b_sglang/arm_alpha0.jsonl` (sha256 `ced39bed…`). This is
    deterministic mode, with all 27 adopt conditions and one draw per cell.
  - `runs/contagion/qwen_parta_repro/arm_deterministic.jsonl` (sha256 `a58dc83e…`). This is the
    repro check's deterministic arm, on the same items as the primary source.

  The same analysis is reported for each.
- **Memory line:** in every adopt prompt it holds the prefix, published (Step 0).
- **Trace:** the `reasoning_text` field only.
- **Unit:** the cell (20 cells). Intervals come from a cell bootstrap: 4,000 resamples, numpy
  `default_rng(0)`, percentile intervals.

## Features (locked; unchanged from v1; case-insensitive Python `re`; computed per trace)

| name | pattern / rule | meaning |
|---|---|---|
| PE | `shift_symbols\(1\)\s*;\s*swap\(2,\s*3\)` or `\bR064\b` | names $P_e$ |
| PREFIX | `shift_symbols\(1\)(?!\s*;)` or `\bR004\b` | names the prefix |
| INBOX | `\b(messages?|senders?|slots?|neighbou?rs?|other cells?|board|published)\b` | refers to the messages |
| COUNT | `\b(majority|minority|unanimous|most of (them|the messages)|all (of )?(the )?messages)\b` or `\b(\d+|one|two|three|four|five|six|seven|eight)\s+(of|out of)\s+(the\s+)?(8|eight|88|messages|slots)\b` | counts or weighs the inbox |
| BOTHFIT | `\b(both (rules |of them )?(fit|work|match|are consistent)|also (fits|works|matches)|consistent with both|either (rule|one) (fits|works))\b` | sees that both rules fit |
| SIMPLER | `\b(simpl(er|est)|occam|parsimon\w*|fewer (steps|operations))\b` | prefers the simpler rule |
| MEMORY | `\b(previous (step|rule|generation)|last generation|my (previous|earlier|current) rule|stick with|keep (my|the) (rule|previous))\b` | appeals to its own previous rule |
| EXAMPLE | the cell's private example input string occurs in the trace | works with its own example |
| KEEP | BOTHFIT or SIMPLER or MEMORY | gives a reason to keep its rule |

**Adopt** means the final answer is $P_e$; anything else counts as non-adopt.

## Predictions (locked)

There are three contrasts. Each uses a two-sided percentile interval at level $1 - 0.05/3$ (98.33 %),
so the family-wise error over the three is at most 5 % (Bonferroni). The baseline in each case is a
second group of the same model's traces, so no threshold is assumed.

- **Q1 (does it read the inbox).** Among non-adopting traces, the share with PE where $k$ is high,
  minus the share where $k$ is low. "High" means $k$ is above the median $k$ of that form's
  conditions in the data; "low" means at or below it.
  - Per cell: the difference is taken within each form, then averaged over the forms where the cell
    has both groups.
  - Reasoning: if the model reads the messages, more $P_e$ lines should put $P_e$ into its reasoning
    more often. If it ignores them, the mentions come only from the catalog and are flat in $k$.
- **Q2 (are keep reasons tied to not adopting).** The share with KEEP among non-adopting traces,
  minus the share among adopting traces.
  - The difference is taken within condition, weighted by the number of adopter × non-adopter pairs,
    then averaged per cell.
- **Q3 (does adoption come through counting).** The same as Q2 with COUNT, and with the sign
  reversed: the share among adopting traces minus the share among non-adopting traces.

Cells without both groups are dropped and counted. The minimum detectable difference for each
contrast is reported beside it. It comes from a null simulation that permutes the group labels within
(cell, condition).

**Descriptive, beside.** For non-adopters and for adopters, by form and $k$: the share of each feature
and the median reasoning length. Also reported: the share of non-adopting traces that have both PE
and KEEP. This share answers "reads and rejects" directly, but it has no baseline, so it is
descriptive only.

## Pre-stated readings

| Q1 | Q2 | reading |
|---|---|---|
| above 0 | above 0 | **Reads and rejects:** more $P_e$ lines put $P_e$ into the reasoning, and not adopting goes with a stated reason to keep the prefix. Stubbornness is a decision rule, not inattention. |
| above 0 | contains 0 or below 0 | It reads the inbox, but the fixed keep phrases do not separate adopters from non-adopters. The reason, if any, is not in these features. |
| contains 0 or below 0 | any | No sign that the inbox reaches the reasoning: mentions of $P_e$ do not rise with $k$. Stubbornness is at least partly **not reading**. |

**Q3 above 0:** when Qwen does adopt, its trace counts or weighs the inbox more often than when it
does not. Adoption, when it happens, comes through counting.

**What follows.** If the reading is "reads and rejects", the weight-level step looks at the point in
the trace where the keep reason is stated, not at the end of the prompt. If it is "not reading", the
weight-level step is attention from the reasoning to the inbox span.

## Precision check (descriptive only)

Artem codes a blind sample of 40 traces from the primary source. The sample is stratified by adopt /
non-adopt and shown without the answer. The precision of KEEP, COUNT and PE against his codes is
reported beside the results. It does not gate anything.

## Outputs

`runs/reasoning_traces/`:

- `features.jsonl`, one row per trace with the features and no text;
- `readout.json` / `readout.md`;
- `blind_sample.jsonl` (trace text with the final answer removed) and `blind_codes.jsonl` (Artem's codes).

Reasoning text is never copied to luna_life. Only feature counts and the readout are mirrored.

## Part 2 (not covered here): a comparison with gpt-oss

Neither gpt-oss battery stored its reasoning: `run_oss120_part_a.py` keeps `message.content` only, and
`run_life_contagion_local.py` keeps the parsed rule only. A comparison with 120b needs new calls on
the adopt prompts, with reasoning stored, under its own amendment. It runs after the repro queue
finishes.

**Standing request, separate from this amendment.** Every future runner for an open model stores the
reasoning text per call, as the repro and witness-direction runners already do. Open-model reasoning
may be stored. Closed-model reasoning is still never stored.

## Limits

- Regular expressions miss paraphrases. A feature can be undercounted. The contrasts are within one
  model, so the undercount affects both groups alike unless the wording differs between them.
- Adoption is rare, at roughly 0.1–0.15 on the lattice, so the adopter groups are small. Q2 and Q3 may
  lack power, and the minimum detectable difference is reported for that reason.
- What a model writes in its reasoning need not be what drives its answer. This is evidence about
  stated reasons, not proof of mechanism.