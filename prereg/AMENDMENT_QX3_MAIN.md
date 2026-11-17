# Amendment — QX-3 main phase: rule alone against rule plus counterexample, across runs

**Status:** locked v3 (2026-11-17), written by the reviewer for Artem. v2 takes in an external
review of the design (Grok): Family S is now a run-level test, a run is started only when it can
finish under the stop, a family with a missing run is not decided, and the readings say what the
tests can show. v3 fixes four defects from the dry build of v2 (run counts, GPU hours, pilot
values). It is locked after the agent's dry build (no model call) and the reviewer's review. No call is made before the lock and
Artem's go, logged in the switch log with his words.

## Why

The QX-3 pilots (`AMENDMENT_QX3_PILOT.md`, `AMENDMENT_QX3_LUNA_R_DOSE.md`) ran one run per
condition. They point to evidence, not rule names, as what moves neighbours:

- Luna, δ = 1/64: 1 cell on H_T at generation 24 with rule names only, 99 and 100 with results.
- gpt-oss-20b, δ = 1/8: 32, 62 and 83.
- Luna, δ = 1/8, rule only: a cell without evidence left H_F in 0 of 141 cases with one to four
  naming neighbours, and in 37 of 41 with five or more. This split was made after the data.

With one run per condition the run-to-run spread is unknown. In QX-2 one Luna cell gave 32 and
55 cells on H_T at generation 12 in two runs. Michal Valko asked to repeat across seeds to see how
stable the gap is. This amendment repeats each pilot condition four times (the rule-only dose
condition five times), with tests fixed in advance.

## Runs

The world, catalog, examples, prompts, schemas, attach rule, decoding and G = 24 are those of the
pilots. Each run is an independent replicate of the model's sampling in world 0. A second world is
not part of this amendment.

| model | cell | arms | new runs per arm | calls |
|---|---|---|---:|---:|
| Luna | δ = 1/64, B = 1 | R, R+E, R+E forced | 4 (r2–r5) | 28,800 |
| Luna | δ = 1/8, B = 1 | R | 5 (r2–r6) | 12,000 |
| gpt-oss-20b | δ = 1/8, B = 1 | R, R+E, R+E forced | 4 (r2–r5) | 28,800 |

- The pilot runs (r1) are not part of any test. They are reported beside the new runs.
- **Run order:** by run, then by arm: r2 R, r2 R+E, r2 R+E forced, r3 R, … The Luna δ = 1/8 runs
  come after all Luna δ = 1/64 runs.
- **Missing runs.** If any arm of a family has fewer finished runs than the design gives it, that
  family is reported as not decided and no p-value is computed. A partial run is not a run.
- **Cache key:** includes the arm and the run, as in the pilots. No answer is shared between runs.
- **Runners:** new files. Nothing pinned by an earlier manifest is edited. Each runner's spend or
  progress ledger starts from the rows already in its `calls.jsonl`.

### Luna

- `gpt-6-luna`, effort medium, temperature and top_p not sent, `max_output_tokens` 8,192.
- **Cost at the measured rates** (per call: R $0.000422, R+E $0.000582, forced $0.000639; dose
  arm R $0.000442): δ = 1/64 arms about $15.77, dose arm about $5.30, together about **$21.1**.
- **Hard stop: $24.00** for the whole Luna part, summed from the non-cached rows of all its
  `calls.jsonl` files.
- **Start rule.** A run is started only if the spend so far plus 1.5 × that run's projected cost is
  at most $24.00. So the stop falls between runs, not inside one. A run that is not started is a
  missing run. Envelope left before this phase: **$25.00** (Artem, 2026-11-17: "$25
  согласен"). The stop is not the envelope.
- The measured rates were checked against the provider's bill: the ledger's November spend,
  $11.66, matches the provider's $11.67.

### gpt-oss-20b

- The pilot's revision, image and request body (`max_tokens` 32,768).
- **Server context 40,960 from the start.** The pilot's forced arm stopped at 36,864 (prompt
  4,120 + 32,768); its largest prompt after the resume was 4,682 tokens. 40,960 leaves 8,192.
- **Queue:** after the QX-2 ladder, before the QX-2 continuation and the Qwen temperature battery
  (Artem, 2026-11-17). About 12.5 GPU-hours per set of three arms, 50.0 hours in all, at the
  pilot's rates.

## Measures

**Primary measure, per run:** x̄ = the mean share of the 100 cells holding H_T over generations
13–24. It uses the second half of the run, so a single generation (as at generation 24 of the
20b R+E pilot, 72 → 62) does not decide it.

x̄ is the total effect of the message channel. It adds cells that found a counterexample themselves
to cells that were moved by neighbours, and it does not see when a run reached its level: two arms
at 1.00 from generation 13 look the same even if one got there at generation 4 and the other at 12.

**Secondary contrast, no α:** x̄_nf = the same mean, counting only cells that never had a
counterexample of their own in that run (out of 100). It is the part of x̄ that neighbours carried.
For L1, L2, B1, B3 the same permutation p is reported for x̄_nf, as a description. Pilot values:
Luna 0.0008 / 0.908 / 0.960 and gpt-oss-20b 0.010 / 0.333 / 0.531 (R, R+E, forced).

Pilot values (not used in any test): Luna δ = 1/64: R 0.0075, R+E 0.998, forced 1.000.
gpt-oss-20b δ = 1/8: R 0.274, R+E 0.614, forced 0.7425.

Also reported per run, descriptive: recovery and abandonment by generation; tests, δ-share and
finders (readout v2) with the rule each ends on; messages with a result, refuting or not, own or
relayed; the R+E sharing rate; non-finders on H_T and how many first saw a shared counterexample;
the two-generation response to a first received counterexample; the dose table of arm R; format,
calls, GPU time and Luna cost.

## Tests

Each test is a one-sided exact permutation test on the run values of x̄: four runs against four,
70 splits, ties counted against rejection (`THEORY.md` §8.2). The smallest possible p is
1/70 = 0.0143. A family of three tests is held at α = 0.05 by Bonferroni, so each test needs
p ≤ 0.0167 (§8.3). With four runs per arm, a test can therefore hold only when every run of the
higher arm is above every run of the lower arm.

**Family L (Luna, δ = 1/64), each at 0.0167:**
- L1: R+E above R.
- L2: R+E forced above R.
- L3: R+E forced above R+E.

**Family B (gpt-oss-20b, δ = 1/8), each at 0.0167:**
- B1: R+E above R.
- B2: R+E forced above R+E.
- B3: R+E forced above R.

**Family S (Luna, δ = 1/8, rule only), one test at α = 0.05.** The majority step found in the dose
pilot, tested with the run as the unit.

- In each run, take the cells that held H_F at g − 1 and have no counterexample of their own in
  memory at g. k is the number of their neighbours that named a rule other than H_F in generation
  g − 1.
- For each cell, take its first generation with 1 ≤ k ≤ 4 and its first generation with k ≥ 5 (a
  cell can have one, both or neither). A cell whose own counterexample arrives at that generation
  is left out of that group.
- p_low and p_high are the shares of those cells that hold another rule at that generation. One
  observation per cell in each group.
- d_r = p_high − p_low for run r. A run with fewer than 5 cells in either group counts as d_r ≤ 0.
- **S holds if d_r > 0 in all five runs.** Under the null hypothesis that each d_r is positive with
  probability at most 1/2, independently across runs, P(5 of 5) ≤ 1/32 = 0.031.
- The cut at five neighbours was found in the pilot and is fixed here before these runs.

The pooled counts and each run's shares are reported beside the test, with nominal intervals.

## Predictions stated in advance

"Holds" means complete separation: every run of the higher arm above every run of the lower one.
A difference of means alone does not make a test hold.

| test | prediction | basis |
|---|---|---|
| L1 | holds | pilot 0.0075 against 0.998; a gap of about 0.99 survives any spread seen so far |
| L2 | holds | pilot 0.0075 against 1.000 |
| L3 | does not hold | both pilot arms at the ceiling; most runs are expected to tie at 1.00 |
| B1 | uncertain | pilot 0.274 against 0.614; run-to-run spread of 0.2 or more would overlap |
| B2 | no prediction | pilot 0.614 against 0.7425 |
| B3 | uncertain | pilot 0.274 against 0.7425 |
| S | holds | pilot 0 of 141 against 37 of 41 |

The only spread measured so far is from another experiment: two Luna runs of one QX-2 cell gave 32
and 55 cells on H_T at generation 12, a difference of 0.23. With such a spread the B gaps may not
separate fully, which is why B1 and B3 are marked uncertain. For every test the difference of means
and the range of each arm are reported.

## Readings stated in advance

| pattern | reading |
|---|---|
| L1 and L2 hold | For Luna, the gap between rule only and rule plus evidence is complete across four runs at δ = 1/64. |
| B1 and B3 hold | For gpt-oss-20b, the same gap is complete across four runs at δ = 1/8. |
| B2 holds | For gpt-oss-20b, attached evidence beats the model's own sharing in every run: the sender is a limit. |
| any of L1, L2, B1, B2, B3 does not hold | The four runs of the two arms are not completely ordered. The difference of means and the ranges are the summary; no claim of "no difference" is made. |
| L3 holds | For Luna, attached evidence beats the model's own sharing in every run, against the prediction. |
| S holds | In all five runs, cells without evidence left H_F more often at five or more naming neighbours than at one to four. The size of the two shares is reported; the test does not say that no cell moves below a majority. |
| S does not hold | The step is not seen in every run; the run shares are the summary. |
| a family not decided | Reported as such, with the finished runs described. |

Each family is a separate claim at its own α. No reading joins the two models into one tested claim;
the page may say that each family held.

## Gates

- **Format:** as in the pilots; more than 4 fallbacks or truncations in the first 400 decisions
  stops that run.
- **Prompt identity:** for every run, the generation-1 prompts and schemas equal the pilot's for
  the same model, cell and arm. Only the run name in the cache key differs.
- **Engine:** the pilot's invariants (no result in arm R; results in memory with stored, true
  outputs; the attach rule; no test in generation 24) are asserted in every run.
- **20b:** the usual GPU precheck and monitor; manifest checked in precheck.
- **Luna:** the $24.00 stop and the start rule. A stopped Luna part is not restarted without a report of the spend
  and Artem's word.

## Dry build (CPU, no model call)

1. Stubs for every runner and arm, with every invariant asserted.
2. Prompt and schema identity against the pilots' pinned files.
3. 3 × 4 + 5 = 17 Luna run names and 12 gpt-oss-20b run names, with distinct cache keys.
4. The test code run on constructed run values: complete separation gives p = 1/70; one overlap
   gives p ≥ 2/70; ties give p = 1 for identical arms; a missing run gives "not decided".
5. Family S code run on the pilot dose trace: the per-cell groups, p_low, p_high and d, with the
   pooled 0 of 141 and 37 of 41 reproduced beside them; and on constructed runs with too few cells.
6. Cost of the Luna part at the measured rates, the start rule checked before each run, the stop and
   the envelope; 20b GPU hours at the pilot's rates, with the server context.

## Outputs

Calls (final text and usage; reasoning stored for gpt-oss-20b only), traces, the readout with all
tests, and one recheck package per model with SHA256SUMS. Nothing enters the QX page or the paper
before the reviewer's recheck from raw data.
