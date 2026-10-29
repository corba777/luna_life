# QX track — experiments under a false consensus (plan)

**Status:** plan, not a lock. Each step below gets its own amendment, locked after a dry build and
before any call. Separate from the model panel and from the false-consensus article. It has its own
readout and its own write-up.

## Origin

Michal Valko, LinkedIn comment on Artem's post (2026-10-22): "seed the grid with a shared wrong
hypothesis, then let the agents choose their own experiments. Can they discover the error?" He pointed
to DiG-bench (Battleday et al., arXiv 2608.12593) as a possible testbed.

Artem's public reply fixes two constraints this track keeps:
1. The experimentation budget stays tight enough that collective reasoning still matters.
2. The primary measure is whether agents under consensus choose experiments that could falsify the
   shared hypothesis or only confirm it.

## Ideas in scope

| id | idea | source |
|---|---|---|
| V1 | Agents choose their own experiments under a shared wrong hypothesis. Is the choice falsifying or confirming? | Valko; Artem's reply |
| V2 | Seed the grid with the shared wrong hypothesis, instead of waiting for it to emerge | Valko |
| V3 | Can the population discover the error once experiments return results? | Valko |
| V4 | DiG-bench games as an external testbed | Valko |

## Steps

**QX-1 (done, Qwen3-4B-Thinking).** This step covers V1 as choice only, and no output is returned.
X1 passes narrowly: confirming share C1 0.438 against C0 0.362, sign-flip p = 0.048, Fisher
p = 0.057. The C0 rate is far above chance (1/8), so there is an individual bias plus a small social
shift. Chosen tests separate the prefix from another S_c rule less often than random inputs (0.68
and 0.61 against 0.987). The per-world descriptives are in `runs/life_dr_qwen/qx1/readout.md`.

Null for “confirming” — checked. Example-structure retention is 14/240 in both conditions (paired
difference 0.000, sign-flip p = 0.637). Most confirming tests are at Hamming distance 4 from the own
example (58/87, 73/105). Mimicry of the own example does not explain the confirming share. C0 stays
the control for X1, and 1/8 stays the descriptive uniform baseline. QX-1r and QX-1p lock X1 as in
QX-1, and report retention and distance beside it.

What “confirming” measures on Qwen. 384/480 tests are AAAA (confirming at every pair) or ABCD (at none),
and each world’s tests are about equally confirming at the other worlds’ pairs. On Qwen, the confirming
share is the AAAA share, a model string preference, not a world-specific choice. X1’s pass stands. Its
content is mainly world 5 (27 → 41 of 80): under consensus, the test moves toward a position-blind
string that checks only the shared shift. QX-1r and QX-1p report, beside X1: the test-pattern
distribution (AAAA, ABCD, other) per condition, and the cross-world confirming rate as the null.
Pre-stated: on a model whose choice is bimodal between canonical strings, an X1 pass is read as a
shift between those strings, named.

**QX-1r (Qwen replication).** The same 480 prompts with fresh draws. X1 is locked as in QX-1. Beside it,
not scored: the test-pattern distribution (AAAA, ABCD, other) per condition, and the cross-world
confirming rate as the null. Retention and Hamming distance stay beside it. The prediction direction
and α are unchanged. This decides whether X1 is a finding or a borderline draw. It runs locally.

**QX-1p (panel).** The same prompt for every model:
- Luna medium and Luna none, the same weights with and without reasoning;
- gpt-oss-120b and gpt-oss-20b;
- Qwen3-4B-Instruct;
- Spark (none and low).

Luna Decisions is excluded, with the reason: it picks from listed options and cannot write a free
test input. X1 is locked as in QX-1. Beside it, not scored: the test-pattern distribution (AAAA, ABCD,
other) per condition, and the cross-world confirming rate as the null. Retention and Hamming distance
stay beside it. Two locked measures per arm are planned:
- X1, the consensus shift;
- the C0 confirming rate, the individual bias.

Thresholds come from QX-1 and QX-1r, for example the replicate difference as noise. They are not set
by intuition. Cross-model question: does reasoning reduce the individual bias, the social shift, or
neither? The Luna arms run inside the $20 envelope. The local arms queue after the current panel
chain.

**QX-2 (experiments return results).** This step covers V3, with V2 as the start state. Each cell
may request the hidden rule's output on inputs of its choice, under a budget. The design problem is
stated before any choice is made. One free test refutes the prefix with probability 7/8, so an
unrestricted test makes the task solvable alone and removes the collective part. These design options
are to be compared in the amendment:
- a budget of one test per cell over the whole run;
- a per-test cost against the publish budget;
- results that are private and must be communicated to count.

Start state (V2): every cell's memory holds the prefix, as a constructed state. The unseeded
spontaneous consensus already exists in the Stage 1 runs and is the control.

Measures:
- the falsifying share of tests;
- the time to first refutation;
- whether a refutation spreads;
- x(g) against the no-experiment runs.

**QX-3 (DiG-bench, V4).** First read the paper and the 21 public games: their format, license, and
whether a multi-agent wrapper with a seeded wrong hypothesis is possible without changing the game.
Nothing is designed before that reading. If it fits, the step is a small external replication of
QX-1's measure on one or two public games.

## Order

QX-1 descriptives → QX-1r → QX-1p → QX-2 design → QX-2 runs → QX-3 reading → QX-3. Nothing runs
before its amendment is locked. No step is rushed to meet a date.

**2026-10-28 — informativeness primary.** Locked addendum `AMENDMENT_QX_INFORMATIVENESS.md`: for
every arm with no call yet (QX-1r and the remaining QX-1p arms), **S1** (consensus lowers
informativeness) is the primary scored measure; **S2** (C0 vs the cell’s 4,096-input baseline) is
descriptive beside it. Informative ≡ the historical `separates` predicate (agent-centred). X1 and
X1a stay as locked where already registered (QX-1r keeps both; panel keeps X1/X1a). Already-run arms
(QX-1 Qwen, QXp-lmmed, QXp-lmnone, QXp-oss20) keep their locked verdicts; informativeness on those
is post-hoc descriptive only.