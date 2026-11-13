# Amendment — does the signal convention carry weight? A cell-level intervention (gpt-oss-20b)

**Status:** locked (Artem, 2026-11-12). This is v3, written after the agent's dry check (2026-11-12).
It runs on the GPU, and only after the Part A repro queue has finished and Artem has given a go.

## Background (post hoc, descriptive; not in the paper)

The population export (`population_calls_2026-11-12`, zip sha256 `41bdf8ae…`) shows two things.

- **Conventions on the complete graph.** In 6 of 8 gpt-oss-20b world-1 `all` runs, the population
  ties a signal to a rule. In five of those runs the true rule $P_e$ travels with one number $s^*$
  (4, or 3 in r5), while prefix messages carry another.
  - Witnesses start it.
  - It spreads by imitation, and from about round 6 it covers ≥ 0.9 of $P_e$ messages.
- **No visible effect on the outcome.** Runs with and without a convention reach similar
  $x(10\text{–}20)$.

**An important structural fact.** A cell's memory holds only its previous rule and publish flag, not
its signal. So the convention exists only in the inbox, and every cell reads it afresh each round.
Two consequences follow:

- Changing the inbox signals changes everything the cell can know about the convention.
- A relabelling that is consistent within one inbox cannot be detected by the cell. The cell can only
  respond to two things: the **contrast** (P_e and the prefix carry different numbers) and its
  **priors about particular numbers** (for example, "0 = unsure").

The arms below separate these two.

## Question

Holding the rule names fixed, does the signal on inbox messages change whether a cell adopts or keeps
$P_e$?

## Items (the stored prompts, re-asked)

- **Source runs.** gpt-oss-20b, world 1, `all`, runs r1, r2, r3, r5 and r6: the runs where $P_e$ is
  marked by $s^*$. r4 is left out because its convention marks the prefix instead; r7 and r8 have no
  convention. Rounds 6–20 are used, because by then the convention covers ≥ 0.9 of $P_e$ messages.
  - **$s^*$, defined operationally.** Take the run's published final calls, all rounds. The message's
    rule is the sender's `inferred_rule`. Then $s^*$ is the signal $s \in \{0,\dots,7\}$ that maximises
    $|P(s \mid P_e\ \text{messages}) - P(s \mid \text{prefix messages})|$. Ties go to the smaller $s$.
    This reproduces Artem's `a1.json` (in `signals_2026-11-12.zip`). The expected values are r1 4,
    r2 4, r3 4, r5 3 and r6 4, and the dry check must match them.
  - **$s_{\text{pre}}$.** The modal signal of prefix messages in rounds 6–20, per run. Ties go to the
    smaller $s$.
  - **If $s_{\text{pre}} = s^*$ in a run,** the run is refused for the `cross` arm and reported.
- **Strata.**
  - **ADOPT:** the cell does not hold $P_e$ (`rule_before ≠ P_e`). Outcome: the answer is $P_e$.
    In rounds 6–20 of these runs, every such cell has ≥ 1 $P_e$ message in its inbox (agent's count).
    This is kept as a check, not as a filter.
  - **KEEP:** the cell holds $P_e$ (`rule_before = P_e`). Outcome: the answer is $P_e$.
- **Sampling.** Per stratum, 400 items are drawn without replacement from the eligible
  (run, round, cell) triples. The draw is stratified by run (80 per run) and ranked by
  `sha256("sigint|run|round|cell")`.
  - **Eligible pool.** 2,570 ADOPT and 4,930 KEEP triples; every run has ≥ 329 in each stratum.
  - **Why 400.** Draws are independent across arms (see Calls). In a simulation at the stored ADOPT
    rates, with 99.17 % intervals, a change of 0.08 in adoption is detected with probability about
    0.60 at 200 items × 2 draws. At 400 items × 2 draws it is about 0.89; at 0.10 the figures are
    0.82 and 0.99.
  - **Fallback.** Artem may cut to 200 per stratum to halve the GPU time. The minimum detectable
    difference is then reported as worse.
- **Prompt.** Each prompt is rebuilt from the stored cache exactly as shown. Its sha256 must equal
  `prompt_sha256` in the export before any call; otherwise the item is refused.

## Arms (only `signal=` values in the inbox lines change; every other byte is identical)

| arm | edit to every inbox message | what it isolates |
|---|---|---|
| `orig` | none | baseline; also the fidelity gate |
| `zero` | signal ← 0 | removes the contrast |
| `perm` | signal ← π(signal), one random bijection of 0–7 per item, with π(s*) ≠ s*, seeded by `sha256("sigint-perm|item")` | keeps the contrast, randomises which numbers carry it: tests contrast vs specific numbers |
| `cross` | swap $s^*$ ↔ $s_{\text{pre}}$ | keeps the contrast, gives $P_e$ the number the prefix used: tests priors on particular numbers |

Before the lock, the dry check confirms that `life_cell_decision_v2` allows exactly the integers 0–7 for
the signal; if the range differs, `perm` uses the schema's range. After each edit, the runner checks two things. The edited prompt must differ from `orig` only inside
`signal=` fields. The number of messages and their says must be unchanged.

## Calls

- **Engine and request body.** SGLang 0.5.18 (image `223b675f…`), `openai/gpt-oss-20b` at revision
  `6cee5e81…`. The launch is the stored one: context 40,960, memory fraction 0.70, 16 concurrent
  requests, `enable_deterministic_inference=False`, `sampling_backend=flashinfer`. The request body is
  `run_life_panel_wave1.request_body("W1-oss20")`: temperature 1.0, top_p 1.0, max_tokens 32,768,
  reasoning_effort `medium`, strict schema `life_cell_decision_v2` (signal: integers 0–7, checked).
- **Date.** The date that the server template renders is pinned per item to the stored run's date:
  2026-10-25 for r1–r2, 2026-11-03 for r3, and 2026-11-04 for r5–r6. Each item takes its date from its
  own round's stored record, so the run uses three server launches, one per date.
  - *Erratum before any call (2026-11-12):* the locked text first said "2026-11-03 for r3–r8". The
    agent's check of the stored records found 2026-11-04 for r5 and r6. The rule ("the stored run's
    date") is unchanged; only the listed dates are corrected. The mechanism is the one the earlier per-run pinned-date
  runners used. As a result, `orig` reproduces the stored rendered input, not only the user prompt.
  The rendered date is recorded per call, and a mismatch stops the run.
- **Retries.** An unparsed answer is retried once, as in the stored runs. If the retry is unparsed too,
  it scores 0.
- **Draws.** Two draws per item and arm, **unseeded**. The stored engine ignores per-request seeds
  outside deterministic mode, and deterministic mode would not be the stored engine. So the arms are
  independent draws on the same prompts: the pairing is by item, not by random stream.
- **Total.** 800 items × 4 arms × 2 draws = 6,400 calls. At the stored 4.4–4.8 s per call this is
  about 9 GPU hours (about 4.5 at the 200-item fallback).
- **Storage.** Reasoning text is stored per call. This is an open model, and it is the standing rule.

## Gates

- **(i) Prompt identity.** As above, for every item and arm.
- **(ii) Fidelity.** In `orig`, the outcome rate minus the stored outcome of the same items (one stored
  draw each), per stratum. The rule is a two-sided 95 % cluster-bootstrap interval that must contain 0.
  - If this gate fails, the arm contrasts are still computed but read as engine-conditional, the same
    as in the Qwen repro.
- **(iii) Format.** Invalid or truncated answers (after the one retry) are counted and score 0.
  - **Early stop.** If they exceed 1 % of the first 400 calls, the run stops and reports. The stored
    runs had 2 unparsed answers in 48,000; 1 % is far above that, so a stop means a broken engine, not
    sampling noise.
- **Tokenize mismatches** are recorded and raise an alert, but do not stop the run.

## Measures and rule (locked)

- **Unit.** The cluster is (run, cell). The bootstrap resamples clusters: 4,000 resamples, numpy
  `default_rng(0)`, percentile intervals.
- **Contrast.** For each stratum and each arm $a \in \{$`zero`, `perm`, `cross`$\}$:
  $$\Delta_a = \overline{y}_a - \overline{y}_{\text{orig}},$$
  paired by item and draw.
- **Multiplicity.** There are six contrasts: three arms × two strata. Each uses a two-sided interval
  at $1 - 0.05/6$ = 99.17 % (Bonferroni, so the family-wise error is ≤ 5 %). The direction is not
  assumed.
- **Minimum detectable difference.** For each contrast it comes from a simulation at the observed
  `orig` rates, and it is reported beside the result.

## Pre-stated readings (per stratum)

| zero | perm | cross | reading |
|---|---|---|---|
| ≈ 0 | ≈ 0 | ≈ 0 | The signal carries nothing beyond the rule names; the convention is decorative. |
| ≠ 0 | ≈ 0 | ≈ 0 | The **contrast** matters (a marked group is read as such), not the particular numbers. |
| ≠ 0 | ≈ 0 | ≠ 0 | Contrast matters, and so does which side carries which number: the model has priors on numbers. |
| ≈ 0 | ≠ 0 | any | Particular numbers matter even though the contrast is kept: the model reads numbers by prior meaning. |
| ≈ 0 | ≈ 0 | ≠ 0 | Only putting the prefix's number on P_e matters: a prior on that particular number (for example, 0). |

In the table, "≈ 0" means the interval contains 0, and "≠ 0" means it excludes 0, with the sign
reported. Patterns not listed are reported as observed, without a reading.

**What follows.** If every arm reads "≈ 0", the population-level intervention (forced signals in live
runs, speed of spread, re-emergence after a reset) is not worth its cost. It is planned only if some
cell-level contrast is ≠ 0, and then under its own amendment.

**Optional follow-up: gpt-oss-120b (Artem, 2026-11-12).** Only if at least one ADOPT or KEEP contrast
for 20b is ≠ 0 does a smaller version of the same design run on gpt-oss-120b `all` r3. That is the only
120b run with a convention ($s^* = 3$). This runs under its own short amendment, with items, arms and
rule copied from this one and n set by a cost estimate. If no 20b contrast is ≠ 0, it does not run.

## Implementation choices (agent's dry check, accepted)

1. **Prefix.** `shift_symbols(1)`, the first operation of $P_e$.
2. **$s_{\text{pre}}$.** Counted over prefix messages published in rounds 6–20. It is 0 in all five
   runs, so `cross` swaps 4 ↔ 0, or 3 ↔ 0 in r5.
3. **`perm`.** The item id is `run|round|cell`. The generator is
   `numpy default_rng(int(sha256("sigint-perm|item")[:16], 16))`, redrawn until π(s\*) ≠ s\*.
4. **Call order.** Calls are sorted by `sha256("sigint-order|item|arm|draw")`.
5. **Bootstrap matrices.** There is one resample matrix per stratum, shared by gate (ii) and the three
   arms. The minimum detectable difference is simulated with `default_rng(1)`. Beside the nominal
   shift, it is also reported as the effective mean shift after clipping at 0 and 1.

## Outputs

`runs/signal_intervention/`:

- `items.json` (sampled items, $s^*$ and $s_{\text{pre}}$ per run, edited-prompt hashes);
- `calls_<arm>.jsonl`;
- `readout.json` / `readout.md`;
- a recheck package (prompts per arm, answers, stored outcomes, hashes) in the usual format.

## Limits

- Items come from five runs of one model, so "the convention" here means the 20b one.
- Re-asking a cell outside its run cuts the feedback loop. This measures the cell's response, not the
  population's.
- Two draws per item at one temperature. Small effects may sit below the minimum detectable
  difference, which is reported.