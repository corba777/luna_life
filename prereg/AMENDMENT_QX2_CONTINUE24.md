# Amendment — QX-2 extended runs: from generation 12 to generation 24

**Status:** locked v3 (2026-11-15; v2 = Artem's horizon decision: restore gens 1–12 under G = 12,
re-announce G = 24 from generation 13; v3 = references follow the same splice, and dry item 3 is made exact).
Dry build (items 1–5 + G = 24 splice references) passed with 0 model calls; generation 12 of the
splice references reproduces the locked phase-1 values. No continuation call is made before Artem's
go, logged in the switch log with his words.

## Why

QX-2 runs last 12 generations (`AMENDMENT_QX2_PHASE1.md`). In several runs the population was still
moving at generation 12:
- all four gpt-oss-20b population runs at δ = 1/8: the share on H_T rose by 0.04–0.11 between
  generations 9 and 12;
- Luna at δ = 1/64, B = 1: from 0.21 to 0.32 over the same generations.

At generation 12 we cannot tell a slow population from a stuck one. The question is whether the
population reaches the true rule given time, or stops short of it. This amendment continues the
moving runs to generation 24 as **extended runs**.

**Order of knowledge, stated plainly:**
- **Post hoc.** The five runs in group A were chosen after their data were seen. Their extended
  runs are descriptive and are labelled post hoc.
- **Fixed in advance.** The rule for group B was locked before any group B data were seen. At this
  writing, Luna r2 is running and the ladder has not started.

## What is continued

**Group A (post hoc, named now) — extended runs:**

| run | model | δ | B | H_T at g9 → g12 |
|---|---|---|---:|---|
| `pop_d8_B1_r1` | gpt-oss-20b | 1/8 | 1 | 0.20 → 0.26 |
| `pop_d8_B1_r2` | gpt-oss-20b | 1/8 | 1 | 0.04 → 0.15 |
| `pop_d8_B4_r1` | gpt-oss-20b | 1/8 | 4 | 0.03 → 0.10 |
| `pop_d8_B4_r2` | gpt-oss-20b | 1/8 | 4 | 0.13 → 0.17 |
| `luna_d64_B1_r1` | Luna | 1/64 | 1 | 0.21 → 0.32 |

**Group B (rule fixed now) — extended runs:** every population arm of `AMENDMENT_QX2_LUNA_R2.md`
and `AMENDMENT_QX2_LADDER.md` is extended if both conditions hold:
- **(i)** 1 to 99 cells hold H_T at generation 12;
- **(ii)** more cells hold H_T at generation 12 than at generation 9.

An arm that fails either condition is not extended. The rule is applied by the readout script to
the stored traces, and its decision is logged before any continuation call.

## How

1. **Restore.** The engine is deterministic given the answers. Each run's state at generation 12 is
   rebuilt by replaying generations 1–12 through the same build, with every answer served from that
   run's own stored calls, keyed as in the original run.
   - A missing answer aborts the replay.
   - No model call is made in generations 1–12.
   - The replayed rules, tests, arrivals and messages of generations 1–12 must equal the stored trace
     before generation 13 is played.
   - Prompts for generations 1–12 use **G = 12** (byte-identical to the stored prompts).
2. **Horizon (re-announced; Artem, 2026-11-15).** Continuation does **not** keep a single G for the
   whole 1–24 path. Instead:
   - Generations 1–12 stay as stored under a horizon of 12.
   - Generations 13–24 are rendered with **G = 24** ("The run lasts 24 generations",
     "Generation g of 24").
   - Every call is stateless, so no agent sees both horizon values in one prompt.

   Phrases such as "last generation" (previous-turn rule) and "Tests left" (remaining budget) are
   **not** horizon words for this gate.
3. **The splice.** Generations 11–12 were played under a horizon of 12. In particular, generation 12
   shows **0 tests in every population run examined** (pilot and Luna). That is caused by the
   **engine**, not the model: `CellView.can_test` is false when `generation < G` fails, so the last
   generation of a run omits the test field (a result could never arrive). Generation 11 can still
   offer tests; any drop there, when the field is present, is the model's choice or a spent budget.
4. **Continue.** Generations 13–24 are played live with the same model, engine image, launch spec,
   chat template and request body as the original run, except that the prompt horizon is 24. The
   calls go to a fresh cache, keyed by run and arm.
   - The test budget B is unchanged and counts tests over the whole extended run. A cell that used
     its budget in generations 1–12 cannot test again.
   - At generation 13, `can_test` uses G = 24, so tests are allowed again for cells with budget left
     (the gen-12 engine ban does not carry forward).
   - Everything else is as locked in `AMENDMENT_QX2_PHASE1.md`.
5. **Models.**
   - gpt-oss-20b uses the pilot's pins (revision `6cee5e81…`, its SGLang image and launch spec).
   - Luna uses the first run's client and settings, with the corrected billing. The hard stop is at
     $2.00 for all Luna extended-run calls together, with the same rules as before.
   - 120b and Nemotron use the ladder's pins.

## Scripted references

The phase-1 simulator is rerun to generation 24 with the same splice as the extended runs:
- generations 1–12 run as locked, with no test in generation 12;
- tests are allowed again from generation 13, within each cell's budget;
- no tests are allowed in generation 24.

It uses 1,000 runs per cell, with the same agents and seeds as before. Abandonment and recovery are
reported at generations 12 and 24. Generation 12 must reproduce the locked phase-1 values exactly.

## Readout (descriptive)

- **Outcomes.** The locked outcomes at generation 12 are not changed. Abandonment and recovery at
  generation 24 are new descriptive outcomes for the extended runs, beside the G = 24 references.
- **Per run:**
  - the H_T trajectory for generations 0–24;
  - tests used, and δ-tests, in generations 13–24;
  - refuting results shared, own and relayed, in generations 13–24;
  - new finders;
  - the post hoc evidence line from the QX page, for cells that switch in generations 13–24.
- **Group A** is labelled post hoc throughout. Group A and group B continuations are labelled
  **extended runs**.

There is no test and no p-value.

## Gates

- **Restore.** It is exact, as in step 1 (G = 12 prompts for gens 1–12).
- **Horizon.** As in step 2: gens 13–24 render G = 24; gens 1–12 match the stored G = 12 prompts.
- **Format.** As locked for QX-2, applied to the continuation calls of each run.
- **GPU.** The usual precheck and monitor.

## Dry build (CPU, no model call)

1. **Restore of all group A runs.** Generations 1–12 replay byte-identically from the stored calls,
   with zero live calls.
2. **Horizon (re-announce).** Generations 1–12 prompts equal the stored G = 12 prompts. Generations
   13–24 prompts, for both B values, render G = 24 ("lasts 24", "of 24"). "last generation" and
   "Tests left" are not treated as horizon words.
3. **Continuation identity on a stub.** Two paths are run with the same stub answers.
   - **Uninterrupted path:** generations 1–15 in one process. Generations 1–12 are rendered with
     G = 12 and generations 13–15 with G = 24.
   - **Restored path:** generations 1–12 are played and stored, then restored in a fresh process and
     continued to generation 15.

   The prompts of generations 13–15 and the full state at generations 12 and 15 must be identical
   between the two paths.
4. **Group B rule.** It is coded and tested on group A, where it must select all five runs and
   reject `pop_d64_B4_r1` and the three Luna r1 arms at the ceiling.
5. **Calls and time.** Group A 20b: 4 runs × 12 generations × 100 cells = 4,800 calls, timed at the
   pilot's measured calendar rate. Luna r1: 1,200 calls, priced at the first run's corrected cost per
   call.

## Queue

1. **Luna parts (API).** Luna r1 extended run starts after the lock and Artem's go. Luna r2 starts
   after its own readout and the group B decision.
2. **GPU parts:** random-8 → QX-2 ladder → this continuation (group A 20b, then the group B 120b
   and Nemotron arms that qualify) → Qwen temperature battery. This is a queue switch, logged with
   Artem's words.

## Outputs

- Extended traces (generations 1–24) and the calls of generations 13–24.
- The readout.
- A recheck package with SHA256SUMS.

Nothing enters the QX page before the reviewer's recheck from raw data.
