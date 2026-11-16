# Amendment — QX-3 pilot: rule only, rule + chosen evidence, rule + attached evidence

**Status:** locked v1 (2026-11-16), after the dry build and the reviewer's review. No call is made
before Artem's go, logged in the switch log with his words.

## Why

QX-2 found that cells which reach the true rule without a counterexample of their own had almost
always first seen one shared by a neighbour: 12 of 14 for gpt-oss-20b, and 264 of 268 for Luna.
That is a correlation found after the data were seen. It does not show that the evidence causes
the switch. Michal Valko proposed the test: compare sharing the rule alone with sharing the rule
plus a counterexample, under matched budgets.

This pilot runs three message conditions. Everything else is identical: world, test budget, one
message per generation, and run length.

| arm | what a message can carry |
|---|---|
| **R** | the key of the rule the cell holds |
| **R+E** | that key, and optionally one result from the cell's memory, chosen by the model |
| **R+E forced** | that key, and the engine attaches the cell's most recent result that refutes H_F, if it has one |

The three comparisons are:
- **R+E against R:** does the option to share evidence help?
- **R+E forced against R+E:** how much is lost because senders do not share?
- **R+E forced against R:** what is the effect of guaranteed sharing of available evidence?

This is a pilot, so it is descriptive. It checks the new message formats and measures run-to-run
spread. A main-phase amendment with locked tests follows, sized from the pilot.

## World and protocol

As locked in `AMENDMENT_QX2_PHASE1.md` (world seed 0, catalog of 117 rules, two examples per cell,
the 10 × 10 torus with Moore neighbours, tests, memory, the mapper and the retry rule), with the
changes below.

- **Run length: G = 24 in every arm,** stated in every prompt from generation 1. There is no splice.
  There is no test field in generation 24, as phase 1 has none in its last generation.
- **Message.** A cell publishes or stays silent. A published message always carries a signal 0–7
  and the key of the rule the cell names this generation.
  - **R:** nothing else. The schema has no result field.
  - **R+E:** an optional `result` field. It is an `enum` over the inputs in the cell's memory (own
    or received), or null. The schema has no output field. The engine fills in the output from
    memory, so no result can be invented, as in phase 1.
  - **R+E forced:** the sender's schema is the R schema. After the model answers, and only if the
    cell publishes, the engine attaches one result:
    - **Choice rule:** among the results in the cell's memory at the moment of sending (own or
      received), take those whose output differs from H_F(input). Attach the one that arrived most
      recently; ties go to the lower input string.
    - **If there is none,** nothing is attached.
    - **No oracle.** The rule uses only H_F, the shared starting rule that every cell holds at
      generation 0. It never reads H_T. This is checked in the dry build.
- **What receivers see.** In R+E and R+E forced, received messages render identically:
  `sender n: rule K, result x -> y` or `sender n: rule K`. A receiver cannot tell an attached result
  from a chosen one.
  - Received results enter the memory block "Results shared with you", as in phase 1, and can be
    relayed. In R+E the model chooses whether to relay; in R+E forced the rule above may attach a
    received result.
  - In R no result is ever received.
- **Prompt text.** The three arms share every sentence except the description of what a message can
  carry, and the R+E sender's description of the optional result. The forced sender's prompt equals
  the R prompt: the sender is not told that a result will be attached. The dry build lists the
  differing sentences.
- **Cache key.** It includes the arm and the run, so no answer is shared between arms.

## Cells, models, runs

| model | cell | arms | runs | calls |
|---|---|---|---:|---:|
| gpt-oss-20b | δ = 1/8, B = 1 | R, R+E, R+E forced | 1 each | 3 × 2,400 = 7,200 |
| Luna | δ = 1/64, B = 1 | R, R+E, R+E forced | 1 each | 3 × 2,400 = 7,200 |

The cells were chosen as follows:
- **gpt-oss-20b at δ = 1/8.** Its cells find counterexamples there but rarely share them. At
  δ = 1/64 it finds none, so the arms could not differ.
- **Luna at δ = 1/64, B = 1.** Few cells find the error there, so sharing decides the pace. At
  δ = 1/8 every arm would reach the ceiling within a few generations.

Models and decoding are pinned as in the QX-2 pilot (20b) and the QX-2 Luna runs:
- **gpt-oss-20b:** the pilot's revision, image and request body.
- **Luna:** `gpt-6-luna` at effort medium, with temperature and top_p not sent, `max_output_tokens`
  8,192 and corrected billing. The hard stop is at $5.00 for the three Luna arms together. Before
  the lock, the dry build states the envelope left: **$15.00** as of 2026-11-16. The stop is not
  the envelope.

The arm order within each model is R, R+E, R+E forced.

## Scripted references (computed before the lock)

The phase-1 simulator is run under the new message protocol at G = 24, 1,000 runs per row:
- **R:** the random agent, which tests uniformly and ignores messages.
- **R+E forced:** adopt_shared with the attach rule above.
- **R+E:** no scripted agent, because the choice to share is the model's.

Abandonment and recovery are reported at generations 12 and 24 for both cells. The R+E forced −
R gap gives the scale of effect the main phase is sized against.

## Readout (descriptive)

Per arm:
- abandonment and recovery by generation, 0–24;
- tests used and the δ-share;
- finders, and the rule each ends on;
- messages carrying a result, refuting or not, own or relayed; in R+E forced, the attached results;
- for R+E, the share of publishing cells holding a refuting result that attached it (the sharing
  rate);
- **non-finders** on H_T, and how many had first seen a shared counterexample;
- the **lag** from the first counterexample found in the run to the first switch to H_T by a cell
  without its own (descriptive; the causal estimate comes only from comparing arms);
- overturn within 2 generations of receiving a refuting result, against the rate without one;
- signals by message content;
- format, calls, GPU time and Luna cost.

There is no test and no p-value.

## Readings stated in advance (for the main phase, not tested here)

| pattern | reading |
|---|---|
| R < R+E < R+E forced for 20b; R+E ≈ R+E forced for Luna | Evidence moves neighbours. 20b's limit is on the sender's side, while Luna already shares enough on its own. |
| R+E forced ≈ R for 20b | Guaranteed evidence does not help 20b. The limit is in how receivers use evidence, not in sending it. |
| R ≈ R+E ≈ R+E forced for Luna | For Luna the rule name alone carries the population; the post hoc evidence line would not reflect a cause. |

## Gates

- **Format.** As locked for QX-2: more than 4 fallbacks or truncations in the first 400 decisions
  stops that arm.
- **Prompt identity.** The three arms' generation-1 prompts differ only in the listed sentences and
  the schema.
- **Attach rule.** It is tested on synthetic memories:
  - it never attaches a non-refuting result;
  - it never attaches an input outside memory;
  - it takes the most recent refuting result;
  - its output is unchanged when H_T is replaced by another subst rule (no oracle).
- **GPU.** The usual precheck and monitor.

## Dry build (CPU, no model call)

1. Prompt and schema for each arm at generation 1, and at a generation with own and received
   results; the list of differing sentences.
2. The attach-rule tests above.
3. The fake client runs all six arms through the engine, with every invariant asserted.
4. The cache key includes the arm and the run.
5. The scripted references under the new protocol.
6. Calls and time: 20b at the pilot's measured calendar rate, and Luna at the corrected cost per
   call, with the envelope left.

## Queue

1. **20b (GPU).** Order as of 2026-11-16, Artem: random-8 → **this pilot** → QX-2 ladder →
   QX-2 continuation → Qwen temperature. The earlier line put this pilot after the ladder. The
   live ladder waiter stays until this amendment is locked and the QX-3 20b waiter is ready; then
   the switch is logged and the ladder waits on this pilot's done marker.
2. **Luna (API):** after the lock and Artem's go, at any time. Stop $5.00 for the three arms.

## Outputs

- Calls (final text, reasoning for 20b and usage), traces, the readout and the references.
- A recheck package with SHA256SUMS.

Nothing enters the QX page before the reviewer's recheck from raw data.