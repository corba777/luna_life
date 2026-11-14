# QX-2 plan — can a population discover a seeded error by experiment?

**Status:** plan, not a lock (2026-11-13; §8 added the same day). Each phase below gets its own
amendment, locked after a dry build and before any call. It runs after the current GPU queue: the
check nudge, then the 120b signal intervention.

**Origin.**

- Michal Valko's suggestion (2026-10-22): seed a shared wrong hypothesis, let the agents choose
  their own experiments, and ask whether they discover the error.
- His design advice (2026-11-13):
  1. Tell the agents they can run tests and use the results, without saying their belief is wrong.
  2. Let them revise and test again.
  3. Sweep the budget, against a single-agent baseline with the same total budget.
  4. Keep results private but allow them to be communicated.
  5. Make the wrong hypothesis hard to distinguish, so that the choice of experiment matters.
  6. Track the three outcomes separately, and check the recovered rule on unseen inputs.
  7. The real question: can one agent's counterexample overturn the group's consensus, or do the
     others explain it away?

## 1. Why the current world cannot answer it

In the current catalog every pair of the 101 rules disagrees on at least 7/8 of the 4,096 inputs.
$P_e$ and the prefix disagree on 7/8 as well. So a random test refutes the false rule with
probability 0.875, and choosing the experiment barely matters. This was checked by exhaustive
evaluation on 2026-11-13.

## 2. New world: a difficulty knob δ

**δ** is the share of inputs on which the true rule $H_T$ and the seeded false rule $H_F$ disagree.

**New primitive.** `subst(p, X, Y)` replaces symbol X with Y at position p, and leaves the input
unchanged otherwise. Composed with an existing rule, it changes the output on exactly the inputs
that have X at position p.

| level | $H_T$ = $H_F$ followed by | δ | random-test refutation in t tests |
|---|---|---:|---|
| hard | a two-position condition, e.g. subst at p=0 only if position 1 is Y | 1/64 | 1 − (63/64)^t |
| medium | `subst(p, X, Y)` | 1/8 | 1 − (7/8)^t |
| easy (current) | a swap, as in $P_e$ vs the prefix | 7/8 | 1 − (1/8)^t |

**Requirements, all checked in the dry build:**

- **Indistinguishable from the examples.** Every cell's private examples are drawn from inputs where
  $H_T$ and $H_F$ agree, so no cell can tell them apart without a test.
- **Catalog.** The catalog contains $H_T$, $H_F$ and distractors of the same form (other positions
  and symbols). Every catalog rule is a distinct function. An oracle checks this exhaustively on all
  4,096 inputs.
- **Hidden structure.** The catalog does not reveal which subst is true. It lists many subst
  variants consistent with the examples.

## 3. Protocol

- **Seeded consensus.** In generation 0, every cell's memory holds $H_F$, published. This is the
  constructed V2 start.
- **Tests.**
  - In each generation a cell may request the hidden rule's output on one input of its choice, up to
    a total budget B per cell over the run.
  - The result arrives in the next generation and only that cell sees it.
  - A cell keeps all its own results, in a "Your test results" block.
- **Channel.** A published message carries either a rule name or one of the sender's own results
  (`x -> y`), with the 0–7 signal as now. This is Valko's "private results that agents can
  communicate". A shared result is the sender's claim, and the receiver cannot verify it.
- **Prompt.** It says, neutrally: tests are available, here is the budget, results come back and
  only you see them, you may share a result. It says nothing about the current rule being wrong.
- **Run length.** G = 12 generations. The topology is the lattice first, then `all`.

## 4. Arms

| factor | levels |
|---|---|
| δ | 1/64, 1/8 (7/8 as the reference, cheap) |
| budget B per cell | 1, 2, 4 |
| population | 100 cells; a **single-agent baseline** with the same total budget (100·B tests over G generations, up to ⌈100·B/G⌉ per generation) |
| control | no tests, seeded consensus |

**Scripted agents in a simulator, before any model call:**

- random tester;
- perfect tester, which always picks an input where the two hypotheses disagree;
- "never revise".

These give the derived reference values for every outcome below. An LLM population is judged against
the random tester, not against intuition.

## 5. Outcomes (tracked separately, as Valko asks)

1. **First refutation:** the generation at which any cell first obtains a result that contradicts $H_F$.
2. **Abandonment:** the share of cells not holding $H_F$ at the end.
3. **Recovery:** the share holding a rule equal to $H_T$ as a function. Beside it, the accuracy of
   each cell's final rule on held-out inputs:
   - uniform inputs;
   - the δ-inputs where $H_T$ and $H_F$ disagree.

**Mechanism measures:**

- **Test quality.** The share of tests on δ-inputs. The random baseline is δ.
- **Overturn.** After the first counterexample, does it spread? Count the cells that abandon $H_F$
  within k generations of receiving it, directly or as a shared message. Also count the cells that
  receive it and keep $H_F$: "explained away".
- **Collective gain.** Population against the single agent at equal total budget, on all three
  outcomes.

## 6. Phases

1. **World build (CPU).** The DSL primitive, oracle, catalogs for δ = 1/64 and 1/8, example sampler,
   prompt, and dry build. Then the scripted-agent simulator and its reference values.
2. **Pilot (gpt-oss-20b, cheap and local).**
   - δ = 1/8, B ∈ {1, 4}, lattice, 2 replicates each, plus the single-agent baseline and the no-test
     control.
   - About 1,200 calls per run at about 4.6 s per call, so roughly 1.5 GPU hours per run and
     roughly 12 hours for the pilot.
   - The point is to check the mechanics and the outcome definitions, not to test hypotheses.
3. **Main (locked predictions; thresholds from the simulator).**
   - The full δ × B grid on local models only: 20b, then Qwen3-4B-Thinking (slow, about 30 s per
     call).
   - Luna, as the strong tester from QX-1, only under the budget rule in §7: δ = 1/64 with B = 1 and
     B = 4, one replicate each.
4. **Topology.** Repeat the best-informative cell of the grid on `all`.

## 7. Decisions (Artem, 2026-11-13)

- **Shared results carry no mark** that they were really observed. They are claims, so "explaining
  them away" is possible.
- **Memory keeps all own results.**
- **Model order.** gpt-oss-20b (pilot, then the grid), then Qwen3-4B-Thinking, then Luna. Luna goes
  ahead only after a cost estimate. The estimate is built from QX-1p's measured spend (Luna medium:
  $0.22 for 480 calls) scaled by the QX-2 prompt and answer token counts from the 20b pilot, and is
  compared with the Luna envelope before any call.

## 8. Phase-1 lock and Luna budget rule (Artem, 2026-11-13)

- **Phase 1 is locked:** `AMENDMENT_QX2_PHASE1.md`. Where it differs from this plan, the amendment
  holds:
  - a 117-rule catalog;
  - relay of received results;
  - two single-agent baselines;
  - six scripted agents;
  - δ = 1/64 as the main cell and δ = 1/8 as the control;
  - abandonment and recovery as the primary outcomes.
- **Luna budget rule.**
  - No Luna call in QX-2 unless the re-estimate from the 20b pilot's measured prompt and answer
    lengths is **at most $5 in total**.
  - Never above the **$13.20** left in the $100 envelope.
  - The full grid runs on local models only (20b, then Qwen).
  - Luna, if it runs, gets only **δ = 1/64 with B = 1 and B = 4, one replicate each**.

## 9. Known items for the grid amendment (Artem, 2026-11-14)

The locked pilot (`AMENDMENT_QX2_PILOT_20B.md`) runs as locked; these items change only the grid.

- **Pooled single-agent budget.** The per-call cap ⌈100·B/12⌉ (9 for B = 1, 34 for B = 4) with no test
  in generation 12 leaves 99 of 100 and 374 of 400 usable tests, below the nominal 100·B, while the
  prompt states the nominal total ("You have 100 tests for the whole run"). Fix in the grid amendment:
  either per = ⌈100·B/11⌉ (10 and 37, so 110 ≥ 100 and 407 ≥ 400), or state the usable number in the
  prompt. The simulator reference for the pooled baseline is recomputed under whichever rule is chosen.