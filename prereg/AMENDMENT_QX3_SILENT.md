# Amendment — QX-3 without messages: what rule names add, and what evidence adds

**Status:** locked v2 (2026-11-18), written by the reviewer for Artem. v2 takes in the dry build of v1
(the runner drops the inboxes; the queue). It is locked after the reviewer's review. No call is made before the lock and Artem's go,
logged in the switch log with his words.

## Why

QX-3 compares a channel that carries rule names with one that also carries results. It has no condition
where nothing is carried. Without it, two contributions are mixed:

- **names:** rule only minus no messages;
- **evidence:** rule + chosen result minus rule only.

The Multi Agent Coordination Bench (Bespoke Labs, 2026-11-18) splits a team's gain the same way, with a
team that cannot communicate (S∅8) between a single agent and a communicating team, and finds the gain
from coordination near zero for frontier models on long tasks. Our setting can say which content of a
message produces a gain, if any.

At δ = 1/8 the rule-only runs carry the rare-to-common error by a majority cascade for Luna (entries 5,
7, 8), and gpt-oss-20b showed no majority step in its one rule-only run looked at (entry 6, post hoc). A
silent condition at δ = 1/8 measures what that cascade adds for each model. At δ = 1/64 rule only already
stays near 0 (x̄ ≤ 0.012 in seven Luna runs), so a silent condition there would add little; it is not run.

## Condition

**Silent:** no message reaches any cell, in any generation, including generation 0. A new runner drops
every inbox before the prompt is rendered and stores each outgoing message; `qx3_engine.py` is not
changed while the gpt-oss-20b queue imports it.

- The prompt template, schema and decoding are those of rule only. Every neighbour's message is rendered
  exactly as a neighbour that sent nothing is rendered in rule only. Cells still answer the full schema,
  including a message; that message is stored and dropped.
- The prompt is not changed to tell cells that messages are not delivered. This keeps the prompt
  identical in form; the only difference is the content of the neighbour lines. This is stated on the page
  with the result.
- Tests, results and memory work as in rule only (B = 1, a result arrives the next generation, no test in
  generation 24).

## Runs

Every run is labelled **model · δ · B · message · world**.

| part | model | δ | B | message | worlds | new runs | compared with (existing or queued) |
|---|---|---|---:|---|---|---:|---|
| S-L | Luna | 1/8 | 1 | silent | 0, 1, 2, 3 | 4 | Luna · 1/8 · B 1 · rule only: world 0 r2 and worlds 1–3 of `AMENDMENT_QX3_WORLDS.md` |
| S-O | gpt-oss-20b | 1/8 | 1 | silent | 0, 1, 2, 3 | 4 | gpt-oss-20b · 1/8 · B 1 · rule only and rule + chosen result: main r2 and worlds 1–3 of `AMENDMENT_QX3_WORLDS.md` |

- Run names `qx3s_{model}_d8_B1_S_w{seed}`. Traces store the world seed, the H_F and H_T keys and the
  (empty) generation-0 messages. The cache key hashes the run name. Analyses read keys from the trace.
- The Luna runner reads its spend once at start and keeps it in memory (as `run_qx3_b4_luna_v2.py`).

### Luna

- Cost at the dose rule-only rate, $1.06 per run, about $4.24 for four runs.
- **Hard stop: $5.00.** Start rule: this amendment's spend so far plus 1.5 × the run's projected cost is at
  most $5.00, and all Luna spend stays within the $45.00 authorization (Artem, 2026-11-18: «ну давай $20
  сверху, но не больше») with the why-probe's $2.00 and the withhold probe's $0.60 still unspent. If that
  margin is not there, the run is not started and the part is reported as not decided.
- Order: w0, w1, w2, w3.

### gpt-oss-20b

- The QX-3 revision, image, request body and server context 40,960. About 2.8 GPU-hours per run, 11 hours
  in all. Queue: the live queue is not changed (QX-3 main 20b, Nemotron with budget, QX-2 continuation).
  These runs wait until a waiter for the gpt-oss-20b runs of `AMENDMENT_QX3_WORLDS.md` exists and that
  set finishes, unless Artem orders otherwise. Until its four rule-only comparison runs exist, T-SO is
  not decided.

## Measures

x̄ (mean share on H_T over generations 13–24) and x̄_nf (cells that never had a counterexample of their
own). In the silent condition no cell can learn from a neighbour, so x̄_nf is the rate at which cells reach
H_T by guessing; it is reported as a baseline for the other conditions. Also: finders (cells with an own
counterexample) and the rule each holds two generations later.

## Tests

**T-SL (Luna): rule only above silent at δ = 1/8.** One-sided exact permutation test on x̄, the four Luna
rule-only runs (worlds 0–3) against the four S-L runs, α = 0.05 (p ≤ 3/70; complete separation not
required). One claim.

**T-SO (gpt-oss-20b): rule only above silent at δ = 1/8.** The same test on the gpt-oss-20b runs, α = 0.05.
One claim. Read with T-M of `AMENDMENT_QX3_20B_MAJORITY.md`.

A missing or partial run leaves its test not decided.

## Predictions stated in advance

| test | prediction | basis |
|---|---|---|
| T-SL | holds | Luna rule-only runs at δ = 1/8 reach all cells through the majority step; without messages only finders (about 70 of 100 in entry 5) can reach H_T |
| T-SO | does not hold | gpt-oss-20b showed no majority step (0 of 11, pilot, post hoc); if names do not move its cells, rule only and silent should end alike |

## Readings stated in advance

| pattern | reading |
|---|---|
| T-SL holds | For Luna, rule names add the cells beyond the finders, through the majority step. |
| T-SO does not hold, the two x̄ ranges overlap | For gpt-oss-20b, rule names add nothing measurable over silence at this δ; its gain, if any, comes from evidence (rule + chosen result against silent, reported without a test). |
| T-SO holds | gpt-oss-20b's names do add something; read with T-M. |
| x̄_nf in silent clearly above 0 | Some cells reach H_T without any evidence or message; that rate is the floor for the other conditions. |

The decomposition (silent → rule only → rule + chosen result) is reported per model and world, with no
further test.

## Gates

World checks, the format gate, the engine invariants of QX-3 plus: no neighbour message is shown in any
prompt of the silent condition, and the generation-1 prompt equals the rule-only prompt of the same world
except for the neighbour lines. The Luna stop and start rule.

## Dry build (CPU, no model call)

1. The silent engine with a fake client: no message delivered in any generation; stored outgoing messages.
2. Generation-1 and a later-generation prompt for a cell, silent against rule only, same world: the diff
   is only in the neighbour lines, rendered as for a neighbour that sent nothing.
3. Run names, cache keys and trace fields.
4. The tests on constructed values, including a missing run.
5. Luna cost, the start rule against the envelope with the two probe reserves, GPU hours.

## Outputs

Calls (reasoning stored for gpt-oss-20b only), traces, the readout with both tests and the decomposition
table, and one recheck package per model with SHA256SUMS. Nothing enters the QX page before the reviewer's
recheck.
