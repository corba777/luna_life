# Amendment — QX-3: why gpt-oss-20b keeps its counterexample, and why its cells go silent

**Status:** locked v2 (2026-11-18), written by the reviewer for Artem. v2 takes in the dry build of v1:
named probe sets, GPU time at a stated worker count, the queue, and the Luna stop outside the why-probe's. It adds two event types to the
locked study `AMENDMENT_QX3_REASONING_20B.md` (locked v5) and one condition to the why-probe
(`AMENDMENT_QX3_WHY_PROBE.md`). It changes neither: the locked texts, codes, samples and coders stay
as they are. It is locked after the agent's dry build (no model call) and the reviewer's review. No
call is made before the lock and Artem's go, logged in the switch log with his words.

## Why

Two behaviours separate gpt-oss-20b from Luna in every run so far (counts from the stored traces):

- **It rarely shares a result.** With the rule always sent and a result optional (QX-3, rule + chosen
  result, δ = 1/8, B = 1), gpt-oss-20b attached a result to 46 of 2,154 messages (2.1 %). Luna, in the
  same condition at δ = 1/64, attached one to 43–53 % of its messages. In QX-2, where a message carries
  the rule or a result, gpt-oss-20b sent a result in 0.1–0.9 % of its messages, Luna in 3–7 %.
- **It is often silent, and evenly so.** gpt-oss-20b sent nothing in 21–24 % of its turns in QX-2 and
  about 14 % in QX-3, at a similar rate in every generation. Luna was silent in 12–17 % (QX-2) and
  about 1 % (QX-3) of its turns, most of them in the last generation, when no one can read the message.

gpt-oss-20b's reasoning is stored for every call, so we can read why. This amendment asks two
questions in the cell's own words: when a cell holds a counterexample and sends its rule without it,
does it consider attaching it? When a cell sends nothing, what does it say about that?

## Data

gpt-oss-20b, δ = 1/8, B = 1, QX-3. Calibration set: the pilot (r1). Analysis set: the main phase,
r2–r5. Draw 0 of each decision. As in the locked study, the analysis set is not read before the coding
instructions for these events are frozen.

## Events

A cell **holds a counterexample** at generation g if a result in its memory at g (own or received)
contradicts H_F.

| event | arms | definition |
|---|---|---|
| E5 withheld | R+E | the first generation g at which a cell holds a counterexample and sends a message with no result |
| E5s shared | R+E | the first generation g at which a cell holds a counterexample and sends a message with a counterexample attached |
| E6 silent | R, R+E | the first generation g ≤ 23 at which a cell sends nothing; recorded with whether it holds a counterexample at g |

The forced arm has no E5: there the engine attaches the result. Generation 24 is left out of E6,
because a message sent then is never read.

**Sample.** The rule of the locked study (`AMENDMENT_QX3_REASONING_20B.md`, "Sample"): a cap of 120
per event type and arm, run quota ⌊cap / n⌋ over the runs of the set with the shortfall handed out in
run order, each stratum drawn with its own numpy `default_rng(4)`. E6 is stratified by whether the cell
holds a counterexample (cap 60 each, no refill). E5s is expected to be small (19 counterexamples were
attached in the pilot) and is coded whole.

## Codes

Read from the reasoning only. The coder does not see the arm, the run, the outcome or the answer.

| code | applies to | yes if the reasoning … |
|---|---|---|
| M1 considers message | E5, E5s, E6 | refers to what the cell will send to its neighbours |
| M2 considers result | E5, E5s | refers to the option of including a result in the message |
| M3 names the counterexample | E5, E5s | refers to the specific result that contradicts H_F |

**Reason for the message choice**, one category, the main reason the reasoning gives:

- (q) does not refer to the message at all;
- (r) nothing new to tell, or neighbours already know;
- (s) doubts the result or its own rule;
- (t) keeps the message short or simple, or reads the schema or instructions as discouraging a result or
  a message;
- (u) a deliberate choice to keep the information, for any stated reason other than (r)–(t);
- (v) shares because it helps neighbours, or because the evidence matters (for E5s);
- (e) other, or the reasoning ends before a decision.

## Coders

The coders, agreement rule and calibration procedure of the locked study: gpt-oss-120b and
`Qwen/Qwen3.6-35B-A3B` (rev `995ad96e…`), temperature 0 with the locked switch rule, Nemotron on 25 %
of items when available, Cohen's κ ≥ 0.6 for a code to be interpreted (a convention, stated in advance).
The instructions for M1–M3 and (q)–(v) are written and frozen on the calibration set, with their own
sha256 logged, before any analysis item is coded. No paid call.

## Asking directly: a third why-probe condition

The why-probe asks for a reason for the rule chosen. Here a third condition asks about the message.

- **Prompts:** set `M-20b`, 60 E5 prompts from gpt-oss-20b (δ = 1/8, R+E, r2–r5), and set `M-luna`, 60
  from Luna (δ = 1/64, R+E, r2–r5, the same event definition), sampled with the rule above and `default_rng(5)`, re-rendered and
  matched to their stored `prompt_sha256`.
- **Condition C:** the stored prompt plus one paragraph at the end, after a blank line, exactly:

  `Give a brief reason for what you put in your message.`

  and one required string field `message_reason`, `maxLength` 300. Condition A is the stored prompt.
- Both models on all 120 prompts, A and C, two draws each: 960 calls, 480 per model.
- **Cost:** Luna at the measured R+E rate, $0.288 for 480 calls; hard stop $0.60, separate from and in
  addition to the why-probe's $2.00, all within the $45.00 authorization. gpt-oss-20b about 0.6
  GPU-hours at 16 workers.
- **Queue:** the live queue is not changed. The gpt-oss-20b calls wait until the locked reasoning study
  has a waiter and finishes. The Luna calls can run after the lock and Artem's go.
- **Measures:** whether C changes the share of draws that attach a result, against the within-prompt
  permutation reference of the why-probe; the stated reasons coded into (q)–(v); for gpt-oss-20b, the
  agreement between the stated reason and the reasoning of the same call (share and κ).

## Readout (descriptive; no test except the C-against-A reference)

1. For E5, E5s and E6 (with and without a counterexample held): the share of yes on each interpreted
   code, with nominal Clopper–Pearson intervals, and the distribution of the reason categories.
2. E5 against E5s: M2 and M3.
3. E6 by generation: the share in each third of the run.
4. Condition C: attach rate in A and C per model, the reference, and the stated reasons.

## Readings stated in advance

| pattern | reading |
|---|---|
| E5 mostly M2 = no, category (q) | gpt-oss-20b does not weigh sharing at all; the option is there but not considered. A prompt that asks for the choice explicitly might change it. |
| E5 mostly M2 = yes, categories (r), (s) or (t) | It weighs sharing and decides against it, for the stated reason. |
| E5 mostly (u) | It keeps evidence on purpose. |
| E6 mostly (q) | Silence is not a decision about the message; it is the message field left out. |
| E6 mostly (r) | Silence means "nothing new". |
| C raises the attach rate beyond the reference | Asking for a reason about the message changes the choice; reported only with this caveat. |
| stated reason agrees with the reasoning (κ ≥ 0.6) | For this question, gpt-oss-20b's stated reasons can be read as its reasons. |

## Dry build (CPU, no model call)

1. The extractor for E5, E5s and E6 on the pilot traces and on constructed traces (a cell that holds a
   received counterexample and withholds it; a cell silent in generation 24 only), with counts per arm.
2. The draw-0 reasoning found for each sampled pilot event, with the share missing or empty.
3. The coder prompt and schema for the new codes, identical bytes for the three coders.
4. The condition-C prompt and schema against A: exactly one paragraph and one field differ.
5. Probe cache keys distinct from the why-probe's (the condition name `C` and the set name enter the
   key), the sample with `default_rng(5)`, the sha match on the pilot as a stand-in.
6. Luna cost at the locked R+E rate, GPU hours, queue position after the locked reasoning study.

## Outputs

The frozen instructions with sha256, the coders' raw answers, the probe calls (reasoning stored for
gpt-oss-20b only), the readout and a recheck package with SHA256SUMS. Nothing enters the QX page before
the reviewer's recheck.
