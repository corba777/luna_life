# Task — Controls from the external review: sampling noise, graph realization, base rate

**Status:** locked. Budget confirmed: alarm at $45, stop at $55. Predictions are locked with this
file, before any API call. Luna Responses,
`reasoning.effort = medium`, the same settings as DRc and the topology runs. Parents:
`TASK_LIFE_DR_TOPOLOGY.md` and amendments, `runs/life_dr_topology/readout_final.md`,
`runs/life_dr_topology/adopt_by_share.md`, `runs/life_dr_topology/review_checks.md`, the external
review (Google Deep Review), `ARM_REGISTRY.md`.

## Why

Three claims in the review package rest on contrasts that the review showed to be confounded:

1. "all plateaus because it removes sampling noise". `all` also has a ten times longer inbox.
2. "r8 is almost deterministic". The two r8 replicates shared one sender schedule.
3. "the plateau level is set by the design (1 − 75/100)". It was found on one design value only.

The share analysis (`adopt_by_share.md`) gives the micro-rule these predictions use. Adoption is a step
at a strict majority of visible lines: (0.5, 0.75] → about 0.80, (0.25, 0.5) → 0.04–0.09, (0, 0.25] →
about 0.02–0.03. The step is nearly the same under moore, r8 and all.

## Part 0 — free analyses, existing logs only (high priority, run first)

All four are descriptive and post hoc. Each is defined here once and is not tuned after the numbers.

**0.1 Rule agent as a null model.** A programmed agent with no LLM, run on the same worlds, the same
examples, the same topologies (moore, r8 with the logged sender schedule, all) and 20 rounds:
- S_c is the set of catalog rules consistent with the cell's own example.
- Round 1 state: the LLM's logged round-1 rule for each cell, taken from the matching run. This isolates
  the social dynamics from discovery.
- Each round, the visible lines are the inbox the topology delivers.
- **Update rule:** if some rule in S_c has a strict majority among the visible lines, adopt it.
  Otherwise keep the current rule if it is in S_c. Otherwise take the most frequent visible rule in
  S_c, and if there is none, keep the current rule.
- **Publishing:** two variants. (a) Every cell publishes every round. (b) Each cell publishes with the
  LLM's logged probability for its state, conditioned on holding P_e or not and on the round, taken
  from the same topology. 100 runs of (b) per logged run, seed 0.

Report per world, run and topology: x(10) and x(20), the modal wrong rule and its share, the
prefix-rejection agreement, the number of false domains of size ≥ 5 living ≥ 10 rounds (moore), and the
replicate-style variance across runs of (b). Put each next to the LLM value. The question is which
LLM outcomes the rule agent reproduces and which it does not.

**0.2 Switching hazard by holding time.** For every cell-round on every topology, d is the number of
consecutive rounds the cell has held its current rule. Report P(switch at t+1 | d, rule is P_e or not)
for d = 1…10 and d > 10, with n and cluster-bootstrap intervals (2000 draws, seed 0). Cells are not
grouped by their final rule.

**0.3 Avalanches, comparable definitions.** For all three topologies compute (i) **synchrony**: all
cells that switch to the same new rule in the same round, whatever their position; and (ii) **spatial
avalanches**: the 8-connected components of those cells on the 10×10 torus. Two nulls, 1000
permutations each, seed 0: the windowed null already used, and a **position null** that keeps the
number of switches to each rule in each round but places them on random cells among the cells that did
not already hold that rule. Report p-values as (b + 1)/(B + 1).

**0.4 Domain boundaries at the level of exposures (moore).** For every cell-round in which a boundary
cell of a false domain (size ≥ 5, alive ≥ 10 rounds) has at least one P_e line in its inbox, record:
the number of P_e lines, the number and identity of the other lines, the cell's own rule, and whether it
switched at the next round. Report the switch rate by P_e share bin (as in `adopt_by_share.md`) and set
it next to the population curve. This shows whether those domains survive because their boundary
cells rarely see a P_e majority, or because they refuse a P_e majority.

## Part 0b — Inbox intervention at a fixed cell state (≈ $1)

This is the causal version of the share curve. A cell's own example, query and memory stay fixed. Only
the inbox is set by us.

- **Source prompts.** From the pinned DRc logs of worlds 1 and 3, rounds 3–8, take real round prompts of
  cells not holding P_e. Class A: 20 cells whose example fits the prefix and that hold the prefix.
  Class B: 20 cells whose example rules the prefix out and that hold neither P_e nor the prefix.
  Selection is by a fixed hash, before any call.
- **Inbox conditions.** The 8-slot block is rebuilt in the same format, with real neighbour ids in a
  shuffled order, generation = round − 1, and signal values copied from the original lines.
  P_e/prefix counts with all 8 slots filled: 0/8, 2/6, 3/5, 4/4, 5/3, 6/2, 8/0. Share against count
  conditions: 1 P_e line and 7 empty; 1 P_e line and 1 prefix line and 6 empty; 2 P_e lines and 2
  prefix lines and 4 empty.
- 10 conditions × 40 cells × 2 draws = 800 calls. Draws use a separate cache namespace from every run.

**Predictions (locked):**
- **I1 (the step is causal).** In class A, P(adopt P_e | 5/3) > P(adopt P_e | 3/5). One-sided Fisher
  exact test, α = 0.05.
- **I2 (share, not count).** In class A, P(adopt P_e | 1 P_e line, 7 empty) > P(adopt P_e | 1 P_e line,
  7 prefix lines). One-sided Fisher exact test, α = 0.05.
- **I3 (the filter holds under pressure).** In class B under 0/8, which is 8 prefix lines, the share of
  answers that adopt the prefix is ≤ 0.08. The bound is 1 − 0.92, the lowest Luna prefix-rejection
  agreement.
- **Descriptive:** the full curve by class, set against the observational curve in
  `adopt_by_share.md` for the same share bins.

## Part 1 — `all-8-exact` (noise against context length)

Arm `dist/luna.resp-medium/all8exact/none`. Each cell sees at most 8 inbox lines. When the other 99
cells have more than 8 publishers, the counts per rule follow the global publisher proportions,
rounded with largest remainders (ties are broken by a fixed hash of world, round and cell). The
publishers shown inside each rule are drawn at random, with a fixed hash. The line order is shuffled
with a fixed hash. When there are 8 or fewer publishers, all of them are shown, as in `all`. The slot
sentence and the header say 8. Everything else is byte-identical to `all`.

Worlds 1, 3 and 5. 2 replicates. 20 rounds. Each replicate has its own hash salt, its own cache, and
its own calls.

**Predictions (locked):**
- **C1 (plateau).** For each replicate where P_e is **not** the plurality among the round-2 messages
  and the modal wrong rule at g20 is the prefix: x(20) ∈ [0.21, 0.29], and the prefix-rejection
  agreement is ≥ 0.92. These are the same band and floor as Q1 and Q2' (the Luna `all` plateau runs).
  Reason: with P_e at about 25% of publishers, a cell sees 2 of 8 P_e lines, in the (0, 0.25] bin.
- **C2 (tipping).** If P_e **is** the plurality among the round-2 messages: x(20) ≥ 0.90.
- **Reading.** If C1 holds, the `all` plateau does not need a long inbox: removing sampling noise is
  enough. If the `all8exact` replicates instead reach ≥ 0.90 the way r8 did, the long inbox, and not
  the absence of noise, is the better explanation. Anything else is reported as mixed.

## Part 2 — r8 graph realization

Two arms, 5 worlds each:
- `dist/luna.resp-medium/r8/none`, **new replicate r3**. Senders are redrawn every round as before,
  but the hash includes a replicate salt. Its sender schedule differs from r1 and r2. It is compared
  with r1, which used a different schedule, so the r1–r3 pair carries graph-realization variance.
- `dist/luna.resp-medium/r8q/none`, a **quenched** random graph. Each cell gets 8 fixed senders, drawn
  once per replicate (uniform without replacement from the other 99, with a replicate salt) and held
  for all 20 rounds. 2 replicates with independent graphs.

**Predictions (locked):**
- **C3 (realization variance).** Descriptive only. Report the r1–r3 replicate variance at g20 next to
  the r1–r2 value (0.00006) and the lattice value (0.040). No threshold: there is no derived
  expectation for its size.
- **C4 (quenched against lattice, the clustering contrast).** Descriptive with one sign test. In each
  of worlds 1, 3 and 5, the first round with x ≥ 0.90 under r8q is compared with the lattice mean of
  the same world. Reported as counts. Theory (Centola and Macy 2007; Montanari and Saberi 2010)
  predicts that clustering helps majority-type contagion, so r8q should be no faster than the lattice.
  It is reported, not scored, because two replicates per world cannot separate the two.

## Part 3 — Base rate of the prefix

New worlds built from world 1's rule P_e = `shift_symbols(1);swap(2,3)` and its prefix
`shift_symbols(1)`. The 100 examples are resampled so that the prefix fits exactly **M** of them, with
M = 60 and M = 85. Constraints, checked by the world audit before any call:
- every example fits P_e;
- every cell has |S_c| ≥ 3;
- the intersection of all S_c is exactly {P_e};
- no wrong catalog rule fits more examples than the prefix;
- the examples that rule the prefix out are placed by the same spatial procedure as in world 1.

The worlds are named `dist-m60` and `dist-m85` in the registry. Arm `all`. 2 replicates each. 20 rounds.

**Predictions (locked):**
- **C5 (the plateau moves with M).** For each replicate where P_e is not the plurality at round 2 and
  the modal wrong rule at g20 is the prefix: x(20) ∈ [1 − M/100 − 0.04, 1 − M/100 + 0.04]. That is
  [0.36, 0.44] for M = 60 and [0.11, 0.19] for M = 85. The tolerance 0.04 is the largest Luna
  deviation from 0.25. Prefix-rejection agreement is ≥ 0.92 as in C1.
- **Stated risk.** At M = 60, P_e holders are about 40% of publishers. Many cells then see 3 of 8 or
  more, and the (0.25, 0.5) bin adopts at 0.04–0.09 per round, against 0.02–0.03 at 25%. A slow
  upward drift could carry M = 60 runs across one half and into tipping. If so, C5 fails at M = 60
  for a reason the share curve already shows. This is written down now, so a failure there is not
  explained away later.

## Gates (all parts)

- New runner, committed before launch. EPOCH_LENGTH ≥ 21. P_e and the example hash checked every round.
- The first-prompt diff against `all` (Part 1) or r8 (Part 2) round 1, before launch. The only allowed
  differences are the inbox block and the slot sentence.
- For Part 3: the world audit for the two new worlds is committed before any call. It reports the fit
  count of every catalog rule, |S_c| for every cell, and the intersection.
- Replicates have separate caches and salts. A read of another replicate's cache aborts.
- Cost is checked after every round. **Order:** Part 0, which is free; then Part 0b; then a report to
  Artem. Then Part 1, Part 3 and Part 2, so that a stop cuts the descriptive part first.

## Cost

Estimates from the topology run: about $1.4 per 8-line run, about $2.0 per `all` run, and about
$0.0007 per call for a single intervention prompt.
- Part 0: free.
- Part 0b: 800 calls, about $0.6–1.
- Part 1: 6 runs, about $9.
- Part 2: 5 + 10 = 15 runs of 8 lines, about $21.
- Part 3: 4 `all` runs, about $8.

Total about $39. **Alarm at $45, stop at $55.** Confirmed.

## Constraints

No reasoning text is requested or stored. Closed-model outputs are not used as training data. Same
prompt as all earlier arms except the inbox block. Edit no running script. Amendments come before
numbers.

## Closing note

After r8q finishes, no further API calls in this project without a new explicit approval from Artem.
Pid 3541299 is the last allowed writer. Remaining work is local (Qwen) and analysis only.

Spend at this note (2026-10-19), while r8q replicate 1 world 3 is still running: **$31.51**. The
sum is the controls caches, and it includes the $5.16 duplicate inside `cache_r8_r3` ($11.90 for
17668 files). It is not the final total. The final total is that same sum once pid 3541299 has
exited, and it is written in this note then.
