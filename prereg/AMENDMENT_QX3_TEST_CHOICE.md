# Amendment — QX-3: do cells choose informative tests? (information-directed test selection)

**Status:** draft v2 (2026-11-20), written by the reviewer for Artem, after an outside review of the idea
(points 1–5 taken in; see "Review taken in"). v2 takes in the dry build of v1 (`runs/dry_build_qx3_test_choice.md`):
the IG rank becomes the primary test, because almost every admissible input splits V early in a run
(q 0.85–0.98 on pilot S0 states); the unassigned states get their own stratum and enter the pooled
tests; the U/H_T question is restricted to δ 1/64, where U and H_T differ. CPU only, stored traces, no model call. It is locked
after the agent's dry build and the reviewer's review, and **before anyone computes any measure of
this amendment on any gpt-oss-20b run.** If such a measure is computed first, for that model, by
anyone, the tests below are void and reported as post hoc. Computing starts only on Artem's go,
logged in the switch log with his words.

## Why

QX so far measures whether evidence and rule names spread and whether cells change their rule. It
does not measure whether a cell, given what it knows, picks a test that can tell its live hypotheses
apart. Amayuelas et al. ("Sampling Is Not Curiosity", arXiv 2611.10501) state this as commitment C3,
"act to learn": among actions of similar task value the agent prefers the more informative one. They
give the behavioural test but do not run it, and name multi-agent curiosity (one agent's progress
directing what others investigate) as open (§6.1). QX has what the test needs: a finite catalog of
deterministic rules, the observations each cell has in its prompt, and every test it chose.

**What this amendment can and cannot show.** It measures *information-directed test selection*: the
chosen test against the tests the cell could have chosen. It cannot show C3 in the authors' full
sense, which needs the preference to disappear when an intrinsic signal is ablated; QX cells have no
such signal to ablate, and task value is not held equal by design. The result is named accordingly.

## Data

- **Analysis set (tests): gpt-oss-20b.** Every test in these runs, none yet read for test choice:
  - QX-3 main, world 0: δ 1/8 · B 1 · R, R+E, R+E forced, r2–r5 (12 runs);
  - `AMENDMENT_QX3_WORLDS.md`: δ 1/8 · B 1 · R and R+E, worlds 1–3 (6 runs), with world 0 r2;
  - `AMENDMENT_QX3_B4.md` O4: δ 1/64 · B 4 · R and R+E, worlds 0–3 (8 runs).
  A queued set that has not finished is not decided.
- **Descriptive only: Luna**, the same measures on its QX-3 runs (main, worlds, L4, silent). Its
  test-region shares are already known (B4 recheck), so nothing on Luna is a test.
- The pilot r1 of gpt-oss-20b is the calibration run for the code (dry build); not in any test.

## Definitions

**State of a cell at a test.** Everything shown in that cell's prompt in the generation it chose the
test: its two examples, its own results so far, results received from neighbours (R+E arms), and
nothing else — no later message, no result that reached another cell only, no engine knowledge of
H_T. The rendered prompt is the source; the extractor reads the observations from it, and the dry
build checks them against the trace.

**Version space V.** The catalog rules (all keys in that cell's prompt catalog, executed with
`build_world(seed)`; the reviewer's recheck rebuilds them independently) that map every observation
in the state to its stated output.

**Admissible tests A.** The inputs the engine would have accepted from that cell in that generation.
From the dry build: every string matching `^[A-H]{4}$` (4,096), repeats, example inputs and inputs
already in memory included, while the cell has budget and the generation is not the last; null is not
a test. An input already observed by the cell has IG 0 by construction.

**Partition of a test x.** The rules in V grouped by their output on x. With a uniform weight on V,
IG(x) = entropy of the group sizes (bits). Uniform weight is an analysis convention, not a claim
about the model's beliefs. The secondary measure (split) does not depend on it.

**Real choice.** A state has real choice if some x in A splits V (more than one group). States
without it are counted and reported apart; they enter no test.

**Strata,** fixed before computing:
- **S0** — no counterexample to H_F in the state, and no neighbour has named a rule other than H_F
  in any earlier generation;
- **S1** — no counterexample, but a neighbour named H_T (this run's key) in some earlier generation;
- **S2** — a counterexample to H_F in the state (own or received);
- **S3** — no counterexample, a neighbour named some rule other than H_F in an earlier generation,
  but never H_T (the dry build's 25 "unassigned" pilot states).

S0–S3 partition the tests. The pooled tests use every test with real choice, whatever its stratum;
the strata are reported, not tested.

## Measures, per test with real choice

- **IG rank** (primary): the mid-rank percentile of IG(x) among all x in A, (number below + half the
  number equal) / |A|; its mean under a uniform choice from A is exactly 0.5.
- **split** (secondary, prior-free): 1 if the chosen x splits V. Its null value is the share of
  admissible tests that split V, q = |{x ∈ A : x splits V}| / |A|. With q near 1 it has little room.
- **IG / max IG** and IG against the median over A, descriptive.

Per run: the mean of (split − q) and the mean of (rank − 0.5) over its tests with real choice, by
stratum and pooled. Reported beside: the number of tests, of states without real choice, and the
share of tests on the H_T region (as on the page).

## Tests (gpt-oss-20b; run = unit)

Cells in a run interact, so tests are not independent units; the run is the unit. Within a run, the
null of "choice independent of state" is a conditional randomization (each test redrawn uniformly
from its own A), which gives per-run reference values; across runs, a sign test.

- **T-C1: chosen tests are more informative than a uniform choice.** Per run, d = mean(rank − 0.5)
  over tests with real choice, pooled over strata. Over the runs of the analysis
  set with at least 10 such tests: one-sided exact sign test on d > 0, α = 0.05. With n runs, holds
  when the number of runs with d > 0 gives p ≤ 0.05 (n = 26: at least 18; the dry build tabulates n
  as it falls). One claim.
- **T-C2: chosen tests split the version space more often than a uniform choice** (d = mean(split −
  q)), the same test. Second claim, reported separately with the mean q per run; no correction (two
  questions: how informative the test is, and whether it can refute any live rule at all).
- **T-C3 (S1 against S0): having heard H_T named moves the choice toward the H_T region more than
  being informative would.** Not a test; descriptive, because S1 is rare at B 1 for this model.

## The U / H_T question (descriptive, stated in advance)

At δ 1/64 only (at δ 1/8, U and H_T are the same rule), so on O4 and on the Luna δ 1/64 runs.
States where V contains both U (the unconditional sibling) and H_T and the cell holds one of them:
the share of chosen tests where U and H_T differ, against that region's share of A. Reported per
model and run. If gpt-oss-20b has no such state (no finder at δ 1/64), it is reported so.

**Readings stated in advance:**

| pattern | reading |
|---|---|
| T-C1 holds | Given what it knows, gpt-oss-20b picks tests more informative than chance about its live rules. |
| T-C1 fails | Its tests are no more informative than a uniform pick from A. |
| T-C2 fails, mean q near 1 | Almost any test splits V; split cannot separate choice from chance here. |
| T-C2 holds, T-C1 fails | Its tests can refute something, but are not the more informative ones. |
| U/H_T share near the region's share of A | The cell does not aim at the difference between its two live rules; test guidance (S1) would then be following a pointed region, not discriminating. |
| U/H_T share well above it | Epistemic agency: the cell designs the test that separates its rivals. |

## Gates

- The extracted state equals the trace (examples, own and received results) for every test of the
  pilot r1 and of 5 random tests per analysis run (dry build on pilot only; analysis runs at compute).
- Catalog execution: every catalog rule reproduces the outputs the engine produced for its own key
  on 200 random inputs per world; H_F, U and H_T keys read from the trace.
- A run with an assertion failure is reported, not silently dropped.

## Dry build (CPU, pilot r1 only; no analysis run read)

1. The admissible-test rule from the engine, and |A| per world and δ.
2. The extractor on pilot r1: states, strata counts, V sizes, share of states with real choice.
3. q and the IG distribution over A for a few pilot states (no chosen test compared).
4. The sign-test table for the n that will occur; a constructed run where every test splits V
   (d > 0), one where none does, one with no real-choice states.
5. A statement that no measure of this amendment has been computed on any gpt-oss-20b analysis run.

## Review taken in (2026-11-20, outside review forwarded by Artem)

1. State only from the cell's own prompt — taken in. Results received from neighbours are in the
   prompt and so are part of the state.
2. Baseline from the same admissible set, plus max and median — taken in.
3. Strata: not heard / heard H_T / holds a counterexample — taken in (S0–S2).
4. Run as the unit, not tests — taken in.
5. States without real choice defined in advance and set apart — taken in.
Also: the uniform prior is a convention — the primary measure (split) is prior-free; the name
"information-directed test selection", not "curiosity" — taken in.

## Outputs

`readout.json` / `.md` with both tests, the strata tables and the U/H_T table; the extractor and code;
a recheck package with SHA256SUMS. Nothing enters the QX page before the reviewer's recheck.
