# Amendment — reasoning traces v3: stated refutation, both-fit and majority, within Qwen

**Status:** locked (Artem, 2026-11-13), before any trace of the deterministic arm is read. It runs on
CPU only and does not touch the GPU queue.

## Why v3

v2's locked features (2026-11-13 readout) matched words that the prompt itself supplies: the rule
strings, "previous step", "messages", "published", and the cell's own example. So six of nine
features were present in every trace, and Q1 and Q2 were zero by construction. That was a design
error in v2, not a finding. Its readings table was correctly not applied.

After that readout, the reviewer did two things.

- **He read the tails of 7 traces from the repro standard arm** (cells 1, 2, 15 and 59). In these,
  non-adopters test $P_e$ on their own example and conclude that it does not fit, for example by
  counting swap positions from 1. Adopters say that both rules fit.
- **He locked two hypotheses in the changelog and then tested them.**
  - **H-IDX held.** In the 4 cells where $P_e$ fits the example under either position convention,
    adoption is higher. Stored battery: 0.171 against 0.075, exact p = 0.0006. Deterministic arm:
    0.169 against 0.067, exact p = 0.0017.
  - **H-IDX2 failed.** The literal 1-based output string occurs equally often in adopting and
    non-adopting traces, about 0.29 in each.

v3 tests the stated reasons directly, with features that cannot match the prompt.

## Data

- **Primary: the repro deterministic arm,** `arm_deterministic.jsonl` (sha256 `a58dc83e…`). Adopt
  prompts with $k \ge 1$, 1,480 traces. No trace text from this arm has been read.
- **Beside, descriptive only: the repro standard arm** (`88c3409b…`). This is where the hypotheses
  came from: 7 tails were read, and v2's descriptives were computed on it.
- **Unit:** the cell (20 cells). Intervals come from a cell bootstrap: 4,000 resamples, numpy
  `default_rng(0)`, percentile intervals.
- **Adopt:** the final answer is $P_e$.

## Text units

- **Sentence.** The trace is split into sentences at `.`, `!`, `?` or a line break, when followed by
  whitespace.
- **Tail.** The last 4,000 characters of the reasoning text. The decision is stated there; the whole
  trace has a median of about 22,000 characters.

## Features (locked; case-insensitive Python `re`)

| name | rule | scope |
|---|---|---|
| REFUTE | a sentence that contains `swap` and also matches `\b(not the same|doesn'?t match|does not match|not match\w*|doesn'?t fit|does not fit|not fit\w*|doesn'?t work|does not work|inconsistent|contradict\w*|mismatch\w*|not consistent|would give|but the output is|isn'?t|is not)\b` | tail |
| BOTHFIT | `\b(both (rules |of them )?(fit|work|match|are consistent)|also (fits|works|matches)|consistent with both|either (rule|one) (fits|works))\b` | whole trace |
| MAJORITY | a sentence that contains `swap` or `R064` and also matches `\b(majority|most (of )?(the )?(messages|cells|others|neighbou?rs)|(\d+|one|two|three|four|five|six|seven|eight)\s+(out\s+)?of\s+(the\s+)?(8|eight)|all (the )?(other )?(messages|cells|neighbou?rs)|many (other )?cells|others (are )?publish\w*)\b` | tail |

**Prompt-echo gate, before any trace is read.** Each feature is run on all 1,160 Part A prompt texts
in the primary source. A feature that matches any prompt is dropped and reported; it is not
re-specified.

**Degeneracy.** If a feature is present in every primary trace or in none, its contrasts are zero by
construction. They are reported as degenerate, not tested.

## Predictions (locked)

There are four contrasts. Each uses a two-sided interval at $1 - 0.05/4$ = 98.75 % (Bonferroni), and
reads "above 0", "below 0" or "contains 0".

- **R1 (refutation goes with not adopting).** Within condition: the share of non-adopting traces with
  REFUTE minus the share of adopting traces with REFUTE. Per cell, the conditions are weighted by the
  number of adopter × non-adopter pairs. The mean is taken over cells that have both groups.
- **R2 (seeing that both fit goes with adopting).** The same with BOTHFIT, adopting minus
  non-adopting.
- **R3 (adoption goes through the majority).** The same with MAJORITY, adopting minus non-adopting.
- **R4 (the cell effect runs through refutation).** Among non-adopting traces, the share with REFUTE
  in the 16 cells where $P_e$ fails the example under 1-based positions, minus the share in the 4
  cells {1, 32, 91, 97}. This uses group means of per-cell shares and an exact two-sided permutation
  over the C(20,4) = 4,845 assignments, at α = 0.0125.

Beside each contrast: the minimum detectable difference at 80 % power. It comes from a null that
permutes the outcome labels within (cell, condition); for R4, from the permutation distribution.

## Pre-stated readings

- **R1 and R2 above 0:** Qwen does not adopt mainly when it concludes, rightly or wrongly, that the
  neighbours' rule contradicts its own example. When it sees that both fit, it adopts. Stubbornness is
  then largely a checking outcome, not a preference for its own rule.
- **R3 above 0:** when Qwen adopts, the stated reason is the majority of messages.
- **R4 above 0:** the higher adoption in the 4 cells comes with fewer stated refutations. The cell
  effect runs through checking.
- **Any contrast containing 0:** not detected at this precision. This is not evidence of no
  difference. The minimum detectable difference is the guide.
- **Below 0 on R1 or R2:** reported as observed. The checking account is then not supported.

## Precision check (descriptive, not a gate)

Artem codes the existing blind sample (40 standard-arm traces, answers removed) for three things:
"concludes the neighbours' rule contradicts its example", "states that both fit", and "cites the
majority". The precision and recall of REFUTE, BOTHFIT and MAJORITY against his codes are reported
beside the results.

## Outputs

`runs/reasoning_traces_v3/`:

- the echo gate;
- `features.jsonl`, one row per trace with features only and no text;
- `readout.json` and `readout.md`;
- a recheck package in the usual format.

No trace text is printed or mirrored. luna_life receives the amendment and the readout counts only.

## Limits

- Regular expressions miss paraphrases and can match negations about other rules. REFUTE requires
  `swap` in the same sentence to limit this, but it is still a proxy.
- What the model states is not necessarily what drives its answer.
- Adopters are few, about 130 per arm, so R1 to R3 may lack power. The minimum detectable difference
  is reported for that reason.