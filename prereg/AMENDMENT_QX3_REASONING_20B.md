# Amendment — QX-3: what gpt-oss-20b reasons when a neighbour names a rule or sends a counterexample

**Status:** locked v5 (2026-11-18), written by the reviewer for Artem. v2 took in the dry build of v1
(`runs/qx3_reasoning_why_dry_build.json`): E1 is defined per k bin, the sampler has one rule with
run quotas, E4 is one test per cell, the reason categories cover every decision, the outcome is the
decision the reasoning belongs to, and the coder cost is priced from token counts. v3 takes in the dry
build of v2: the run quota follows the runs of each set, each stratum has its own generator, the
start rule counts this study's own spend, and the token encoding is named. v4 replaces the coders:
Luna and gpt-oss-120b are both OpenAI models, so their agreement could come from shared training
rather than from the text. The two coders are now gpt-oss-120b and a Qwen3 model, from different
families and both open-weight, with Nemotron as a third coder on a subset. The study then makes no
paid call. v5 pins the Qwen3 checkpoint found by the dry build of v4. The amendment is locked after the reviewer's review of v5, and before any analysis-set
reasoning is coded. No model call is made before the lock and Artem's go, logged in the switch log
with his words.

## Why

The QX-3 runs show what cells do: a rule name rarely moves a cell, a shared counterexample often
does. They do not show why. gpt-oss-20b's reasoning is stored for every call, so the decision at the
moment of contact can be read. A first look at the pilot (three cells, not part of this study) gave
two different reasons for not switching: one cell read the neighbours' rule names and kept its own
because its data fit; another cell received a counterexample and its reasoning never mentions it.

Luna's reasoning is not stored (closed model), so this study covers gpt-oss-20b only. A separate
amendment (`AMENDMENT_QX3_WHY_PROBE.md`) asks both models for a short stated reason.

## Data

gpt-oss-20b, δ = 1/8, B = 1, arms R, R+E and R+E forced.

- **Calibration set:** the pilot runs (r1). Used to write and test the coding instructions. Not
  analysed.
- **Analysis set:** the main-phase runs r2–r5 (`AMENDMENT_QX3_MAIN.md`). Not read by anyone before the
  coding instructions are frozen.

**Sources and joins.** Traces and `calls.jsonl` as stored; nothing in the running queue is changed.
- The reasoning of a decision is the `reasoning` of the `calls.jsonl` row with the same run,
  generation, cell and draw 0.
- The world, and so H_F and its outputs, is `qx2_world.build_world(0)`. The dry build of v1 re-rendered
  all 7,200 pilot decisions through the engine with this world and matched every stored
  `prompt_sha256`. The same replay is run on r2–r5 before coding.
- Generation 0 is not stored. In this world every generation-0 message names H_F, so k = 0 at
  generation 1. The replay match is what confirms this.

## Events (one reasoning text each, draw 0 of the decision)

A cell is **without evidence** at generation g if no result in its memory at g (own or received,
visible from its stored arrival generation) contradicts H_F. A received result that agrees with H_F
is not evidence.

| event | arms | definition |
|---|---|---|
| E1 name contact | R | for a cell on H_F at g − 1 and without evidence at g, k is the number of its neighbours whose generation g − 1 message named a rule other than H_F. For each cell, E1 is taken **once per k bin** (1–2, 3–4, 5 or more): the first generation at which k falls in that bin, as in Family S of `AMENDMENT_QX3_MAIN.md`. A cell can have up to three E1 events. |
| E2 evidence contact | R+E, forced | the first generation g at which a cell on H_F at g − 1, with no own counterexample at g, holds a received result that contradicts H_F |
| E3 own discovery | all three | the first generation at which a counterexample from the cell's own test arrives, if the cell is on H_F at g − 1 |
| E4 test after contact | R+E, forced | the cell's **first** test made at or after its E2 generation. All tests after E2 are counted and reported, not coded. |

v1 took only the first E1 per cell. On the pilot all 90 such events had k in 1–2, because a cell's
first contact almost always comes from one or two neighbours. The per-bin definition is what makes the
k comparison possible.

**Outcome**, taken from the trace and not coded: the rule the cell holds **at g**, the generation whose
reasoning is coded (other than H_F, and H_T or not). The rule at g + 1 is reported beside it.

## Sample

One rule for every event type and arm.

- **Strata.** E1: each k bin is a stratum with a cap of 40. E2, E3, E4: the type is one stratum with a
  cap of 120. So at most 120 events per type and arm, 960 in all.
- **Run quota.** In each stratum, if the events number at most the cap, all are coded. Otherwise each
  run of the set gets ⌊cap / n⌋ events, where n is the number of runs in the set (n = 4 for the
  analysis set r2–r5, so 10 for a k bin and 30 otherwise; n = 1 for the calibration set r1, so a
  stratum over the cap is a sample of the cap from r1). A run with fewer events gives all of them,
  and the shortfall is handed out one event at a time to the other runs of the set in run order,
  repeated, skipping runs with nothing left. The remainder of cap / n, if any, is handed out the same
  way.
- **No refill across strata.** An empty or short k bin is not filled from another bin.
- **Draw.** Each stratum calls numpy `default_rng(0)` on its own, so the sample of one stratum does not
  depend on any other. Within the stratum, runs are taken in run order; within a run, events are
  sorted by (generation, cell) and the quota is chosen without replacement from that generator.

## Codes

Each code is yes or no, read from the reasoning text only. The coder does not see the arm, the run,
the outcome or the answer text.

| code | applies to | yes if the reasoning … |
|---|---|---|
| C1 notices | all | refers to at least one neighbour message (a sender, a rule key or a shared result) |
| C2 checks name | E1 | applies a neighbour's named rule to at least one of the cell's own examples or results |
| C3 notices result | E2, E4 | refers to a specific shared result (its input or output) |
| C4 checks result | E2, E4 | computes the current rule's output on a shared input, or states that a shared result does not fit it |
| C5 rejects current | all | concludes that the current rule (H_F) is wrong |
| C6 replacement | all | names or describes a rule to replace H_F |
| C7 counts | E1, E2 | refers to how many neighbours say something, or to a majority |
| C8 own evidence | E4 | gives as a reason for the test that the cell wants its own result, or wants to share or confirm a result |

**Reason for the decision** (E1 and E2, every event, whatever the outcome), one category, the main
reason the reasoning gives for the rule it chooses:

- (a) does not refer to the neighbour information;
- (b) refers to it and keeps the current rule because its own data fit;
- (c) refers to it and distrusts the neighbour or the message;
- (d) the number of neighbours, or a majority;
- (f) a shared result shows the current rule is wrong;
- (g) a neighbour's named rule fits the cell's own data;
- (e) other, or the reasoning ends before a decision.

(a)–(d) are the reasons expected for staying, (f) and (g) for leaving, but the coder does not see the
outcome, and every category is allowed for every event.

## Coders and agreement

- **Two coders, from two model families,** with the same frozen instructions and the same item bytes,
  both open-weight and run locally when the GPU is free, temperature 0. If a coder at temperature 0
  truncates or repeats itself on more than 2 of the calibration items, that coder switches to its
  model card's recommended sampling for the whole study, decided on the calibration set and logged
  before any analysis item is coded:
  - gpt-oss-120b (OpenAI);
  - `Qwen/Qwen3.6-35B-A3B` (Alibaba), revision `995ad96eacd98c81ed38be0c5b274b04031597b0`, BF16, with
    the chat template in its `tokenizer_config.json` (sha256 prefix `e84f32a23fdda276`): the largest
    Qwen checkpoint on disk that fits the GPU and has a serve path in our stack.

  Both coders' reasoning and answers are stored. gpt-oss-20b does not code its own reasoning. Each
  item is coded once by each coder. Neither coder is claimed to be deterministic. Their agreement is
  the reliability measure.
- **Third coder, for a check:** Nemotron 3.5 (NVIDIA), with the thinking budget of
  `AMENDMENT_QX2_NEMOTRON_BUDGET.md`, on a random 25 % of the analysis items (numpy `default_rng(3)`),
  only if its QX-2 smoke check has passed. Its agreement with each of the two coders is reported. It
  does not decide whether a code is interpreted.
- **Input to the coder:** the frozen instructions, the event type and the reasoning text. Engine labels
  and run names are removed if they occur. Ordinary words are not removed: the v1 dry build stripped
  the word "forced" from one reasoning text, and v2 does not do that. Any reasoning text that contains
  an arm name as a word is listed for the reviewer instead.
- **Answer format:** a JSON object with the eight codes (yes, no, or not applicable for codes that do
  not apply to the event type) and the reason category, under a strict schema. An answer that fails
  the schema after the client's retries is counted and left out. It is never filled in.
- **Calibration:** the instructions are written and revised on the calibration set only, with the
  reviewer coding the same items as a reference. They are then frozen, with their sha256 logged,
  before any analysis-set item is sent to a coder. Coder calls on the calibration set are model calls
  and need the same go.
- **Agreement:** Cohen's κ between the two coders, per code and for the reason category, on the
  analysis set, with a bootstrap interval over items. A code is interpreted only if κ ≥ 0.6. This
  threshold is the conventional "substantial agreement" level (Landis and Koch, 1977). It is a
  convention, not derived from our data, and is stated here before the coding so that it cannot be
  chosen afterwards.
- **Disagreements** on interpreted codes are resolved by the reviewer, blind to arm and outcome, and
  the number resolved is reported.

## Cost

No paid call. GPU time for gpt-oss-120b about 1.9 hours at the ladder's per-call rate; the Qwen3 and
Nemotron times are measured on the calibration set. Coding runs after the GPU queue fixed for
gpt-oss-20b (QX-3 main, Nemotron with budget, QX-2 continuation), unless Artem orders otherwise.

## Readout (descriptive; no test and no p-value)

1. For each event type and arm: the share of yes on each interpreted code, with Clopper–Pearson
   intervals. Each E2, E3 and E4 event is a different cell. An E1 cell can appear in up to three k
   bins, once in each. Cells within a run interact, so intervals are nominal.
2. E1: C2, C5, C7 and the reason category by k bin, beside the switching rate at g.
3. E2: switching rate when C3 is yes and when C3 is no; the reason category by outcome.
4. E2 R+E against E2 forced: the same table. In forced the sender was not told that a result would be
   attached; receivers see the same rendering in both arms.
5. E4: C8 in R+E against forced, the share of first tests whose input equals a received result, and
   the count of all tests after E2 per cell.
6. Ten example excerpts per event type, chosen by the sampler, not by hand.

## Readings stated in advance

| pattern | reading |
|---|---|
| E2 non-switchers mostly (a) | Evidence fails for this model mainly because it is not read. A change in how shared results are presented could matter more than what they say. |
| E2 non-switchers mostly (b) or (c) | The model reads the evidence and discounts it. |
| C5 yes but C6 no is common in E2 | The model accepts that H_F is wrong before it finds a replacement (as in the forced pilot, where many cells held a third rule). |
| E1 switchers at k ≥ 5 mostly (d), at k 1–4 mostly (g) | The majority step is a counting step, not a checking step. |
| C8 higher in R+E than in forced | Re-testing a shared input is tied to the option to share own results, as the Luna counts suggest. |
| any code or the category with κ < 0.6 | That code is not interpreted. |

## Dry build of v4 (CPU, no model call; done 2026-11-18)

1. The Qwen3 checkpoints on disk, with revision, size and whether each fits the GPU in our stack; the
   chosen one, and its chat template.
2. The coder prompt and strict answer schema rendered for gpt-oss-120b, the chosen Qwen3 and
   Nemotron, with identical instruction and item bytes.
3. The 25 % subset with `default_rng(3)` on the pilot, reproducible.

Result: `Qwen/Qwen3.6-35B-A3B` chosen; the coder item (user-content sha256 `eb83ae6a…4a77163`) and
schema (`b28eb3cb…f4570`) are identical for the three coders; 103 of 413 pilot items drawn.

## Dry build of v2 (CPU, no model call; done 2026-11-18)

1. The extractor with per-bin E1 and first-test E4, on constructed traces (a cell with E1 events in
   two bins; a cell with two tests after E2), and on the pilot traces, with counts per type, arm and k
   bin.
2. The sampler with run quotas on constructed strata (a run short of its quota; a cap that does not
   divide by four), reproducible with seed 0.
3. The coder prompt with the frozen-instruction placeholder; the list of reasoning texts that contain
   an arm name as a word, with nothing stripped from them.
4. Input token counts of the coder prompts on the pilot, and the priced projection.
5. A note of which pilot facts the analysis-set replay must check again (sha match, generation-0 k).

## Outputs

The frozen instructions with sha256, both coders' raw answers, the agreement table, the readout and a
recheck package with SHA256SUMS. Nothing enters the QX page before the reviewer's recheck.

**For later runs (not this study, and nothing pinned or running is edited):** store the draw-0
reasoning on the decision, the generation-0 messages, and the world seed and H_F key on the trace.
