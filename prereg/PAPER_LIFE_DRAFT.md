# Who Speaks First: response rules, topology and the limit of checking in populations of language-model agents

**Status:** arXiv text **v1.7**, 2026-10-27 (target cs.MA). Successor to `PAPER_CLAIMS_LIFE_DRAFT.md`,
which stays as the provenance record of the earlier world (several examples, feedback, seeded
sources). Source of truth for every number: the locked amendment and its readout named in the
prediction table. `[FILL: …]` marks a number still to paste from a readout; `[PENDING: …]` marks a
result still running. Post-hoc analyses are labelled where they appear.

**Two versions of one text.** This file is the arXiv version. A Medium version, in the style of
"What None of Them Knew", is written from it after this text is frozen: same claims and numbers,
narrative order, no proofs. Neither version contains a claim the other lacks.

**Style rule.** One idea per sentence. Each claim states what was measured, on what, how many, and
which locked prediction it tested. No intensifiers, no "notably", no "crucially". Arm codes only in
tables and the appendix.

---

## Abstract

A hundred language-model agents on a 10 × 10 torus each hold one input–output example of a hidden
two-step string rule. Each round, each agent names the rule it holds and may post that name to its
neighbours. The examples together identify the rule, so a simple set-intersection protocol reaches
it on any connected graph. A one-step rule, the first step of the true one, fits 75 of the 100
examples. Only the other 25 agents can see that it is wrong.

We report two results. First, checking. Without reasoning, a frontier model's populations end with
none of their witnesses on the true rule. When agents of that model are asked whether a given rule
fits their own example, the true two-step rule does not beat its one-step prefix by a margin that
100 examples can resolve, in any of three modes. With one-pass answers it loses to the prefix. The
checking error grows with rule complexity and is shared by all agents, so adding voters does not
remove it. Second, response. We
reduce each agent to three functions — the probability of adopting the true rule, of abandoning
it, and of publishing — measured in a controlled battery outside the population. Their shape
differs by model: a threshold rule for one model, a graded response for another. Without fitting
to any population outcome, these functions predict which topology each model does better on, and
the ranking reverses between models. On the complete graph the threshold model is bistable: in 20
runs, 8 converge to the true rule and 12 freeze. Constructing the first round of published messages
changes the convergence rate from 1/8 to 8/8 (Fisher exact p = 0.0007). Every prediction was locked
before the data.

---

## 1. Introduction

Multi-agent systems are now built from language models, and the question of when a group of them
computes something none of its members can is practical. It is also hard to measure. Identical
agents given similar inputs agree without communicating. In an earlier version of this testbed, a
false majority on the same simple rule appeared in the first round with and without a message
channel, because that rule fit most agents' evidence [ref: earlier report]. (A silent population
that kept the false rule for all rounds did so because its prompts omitted each agent's own
previous rule; with that memory restored the lock broke after one round.) Agreement is therefore
not evidence of collective computation, and a no-channel control must not remove anything except
the channel. We measure something else: whether a population reaches a true rule that
only a minority of its members can tell apart from a locally consistent false one.

The setting is designed so that no agent can solve the task alone and the population can. Each
agent holds one example. The true rule is a composition of two operations. Its first operation
alone fits three quarters of the examples. The agents who can see the error, the witnesses, are a
quarter of the population and are scattered on the grid. The only channel carries rule names.

We ask two questions. Does the population lose the answer because of what agents can check, or
because of how they respond to each other? And can the second be measured on the individual agent
and used to predict the population?

Contributions:

1. A small theory of the setting (Section 3). The task has a global answer on every connected
   graph (Theorem 1). The agent reduces to three functions. Propositions on the complete graph and
   the lattice take these functions as measured inputs and state what would refute them.
2. A negative result on checking (Section 4). Verification by vote cannot select the true rule:
   the margin is bounded by a complexity-dependent error that is the same for every voter
   (Proposition 5, measured for three modes of one model).
3. A micro-to-macro result on response (Section 5). Response functions measured in isolation
   predict the topology ranking for two models whose rankings are opposite [and for one held-out
   model: PENDING]. On the complete graph, a threshold responder's outcome is decided by the first
   published messages, and we confirm this by manipulating them.

All predictions, thresholds and readings were committed before the data. Thresholds were derived
from earlier measurements or from the theory. Failed predictions are reported in the same table as
the ones that held (Appendix C).

## 2. Setting

**World.** N = 100 cells on a 10 × 10 torus. A catalog ℛ of 101 rules on strings of four symbols
from A–H: 17 single operations (`reverse`, `rotate_left(k)`, `shift_symbols(k)`, `swap(i,j)`) and
84 compositions of two. In the main world the hidden rule is P_e = `shift_symbols(1);swap(2,3)` and
the prefix is E = `shift_symbols(1)`. Each cell c holds one example (u_c, v_c) with v_c = P_e(u_c).
Its consistent set is S_c = {r ∈ ℛ : r(u_c) = v_c}. The examples were drawn so that the intersection
of all S_c is {P_e} (world audit). E fits 75 examples (class A). The other 25 cells (class B, the
witnesses) can exclude E from their own example. Two further worlds with the same structure
(true rule = prefix plus one swap) are used for robustness.

**Cell.** Each round, each cell receives one prompt: a fixed constitution, its own example, a
one-line memory of its previous rule and whether it published it, and an inbox. It returns one
rule name and a publication bit. There is no feedback and no seeded holder of P_e. The prompt is
byte-identical across models for the same state.

**Topologies.** The Moore lattice: eight neighbours, and an unpublished neighbour appears as an
empty slot. The complete graph (`all`): the inbox holds every line published in the previous round.

**Models.** `gpt-6-luna` (OpenAI, through the Responses API at reasoning effort medium; the
Decisions API and effort none appear in Section 4); gpt-oss-20b; Qwen3-4B-Thinking-2507;
gpt-oss-120b [PENDING]. Local models are served with SGLang with pinned images, chat templates and
decoding (Appendix D). Every model gets the same prompt.

**Measures.** x(t), the share of all cells holding P_e at round t. The run outcome is the mean of
x(t) over rounds 10–20. A run "tips" if that mean exceeds 0.9. The unit of inference is the run for
population results and the cell for battery results.

## 3. Theory

The theory is written so that each statement names its measured inputs and the observation that
would refute it. No parameter is fitted to the population outcome a statement predicts. Proofs
longer than a few lines are in Appendix A.

### 3.1 The task has a global answer

Notation: r_c(t) is the rule held by cell c at round t and z_c(t) ∈ {0, 1} its publication bit.
The inbox of c at round t holds the rules of neighbours d with z_d(t − 1) = 1. We write k and m for
the numbers of inbox lines naming P_e and E.

**Theorem 1 (sufficiency).** If ⋂_c S_c = {P_e} and the graph G is connected, there is a protocol
with messages of O(|ℛ|) bits that brings every cell to P_e within diam(G) + 1 rounds.

*Proof.* Each cell publishes its current candidate set and replaces it by the intersection with
the sets it receives. The sets only shrink and always contain P_e. After diam(G) rounds every set
equals ⋂_c S_c. ∎

In sheaf terms (as in [TSI, arXiv 2610.26777]), the local sections S_c glue to a non-empty global
section, so there is no obstruction on any topology. Any failure to reach P_e is a property of the
agents or of the rule-naming protocol, not of the graph.

**Corollary 1.** E ∈ S_c for every c in class A. The false consensus "all cells hold E" agrees with
75 % of the evidence, and no class-A cell can detect it from its own example.

### 3.2 The agent as three functions

Class-A answers lie almost entirely in {P_e, E} (Luna 100 % in the battery of Section 5;
gpt-oss-20b own-example fit 0.99). A class-A cell is then a two-state chain with

- adopt: a(k, m) = P(r(t+1) = P_e | r(t) = E, inbox with k P_e lines and m E lines);
- abandon: b(k, m) = P(r(t+1) = E | r(t) = P_e, same inbox);
- publish: π_X^R(t) = P(z(t) = 1) for a cell of class X holding R at round t.

On `all` the inbox enters through the share s of P_e among visible lines, and we write α(s), β(s).
Witnesses are taken to keep P_e once they hold it (h_B = 1); Proposition 4b drops this.

**Assumption M.** a and b depend only on the current rule and the current inbox. *Test:* a
simulator driven by the empirical full-run hazards, binned by (k, m) or by s, reproduces all four
world-1 population outcomes (Luna lattice 0.972 against observed 0.865–0.967; Luna `all` 0.291
against 0.232–0.307; gpt-oss-20b lattice 0.448 against 0.374–0.445; gpt-oss-20b `all` 0.885 against
0.850–0.871). This checks the reduction, not the prediction; the prediction (Section 5.2) uses
functions measured outside the population.

### 3.3 The complete graph

Let w = 0.25 be the witness share and x_A(t) the share of class A holding P_e. The P_e share on the
board is

  s(t) = [w π_B + (1 − w) x_A π_A^P] / [w π_B + (1 − w)(x_A π_A^P + (1 − x_A) π_A^E)],

and the mean-field recursion is x_A(t+1) = x_A + (1 − x_A) α(s) − x_A β(s).

**Proposition 2 (threshold freezing).** If α(s) = 0 and β(s) = 1 for s < θ, x_A(t₀) = 0, and
s₀ = w π_B / (w π_B + (1 − w) π_A^E) < θ for all t ≥ t₀, then x_A stays 0 and x = w.

With Luna's θ ≈ 1/2 and the measured π_B ≈ 0.94–1.0, π_A^E ≈ 0.8–0.9, s₀ ≈ 0.28 and the
prediction is x ≈ 0.25. The condition s₀ < 1/2 fails only when π_A^E < π_B · w/(1 − w) ≈ π_B/3:
class A has to be mostly silent for the witnesses to carry the board.

**Proposition 3 (graded spread).** If α(s) ≥ ε > 0 and β(s) ≤ β̄ < 1 on the reachable range of s,
and π_A^P ≥ π_A^E, every fixed point satisfies x_A* ≥ ε/(ε + β̄). If α is non-decreasing and β
non-increasing in s, the recursion is monotone and converges from 0 to the smallest fixed point.

**Bistability.** For a threshold responder the recursion has two attractors, the witness plateau
and x = 1. Which one a run reaches depends on whether s crosses θ in the first rounds. When round-1
publication is sparse, s(2) is computed from a handful of lines and is a noisy draw. The prediction
is that fixing the early board fixes the outcome. Section 5.4 tests it.

### 3.4 The lattice

**Lemma 1.** If a(k, m) is non-decreasing in k and non-increasing in m and c's class-A neighbours
hold E, the probability that c adopts at the next round is non-increasing in π_A^E.

So silence of E-holders can only help early local adoption. In world 1 every class-A cell has two
or three witness neighbours and none has four or more (dry build).

**Proposition 4 (plurality on a filled lattice).** Under a = 1[k > m], b = 1[m > k], with all
class-A neighbours on E, c flips with probability P(Bin(n_B, π_B) > Bin(n_A, π_A^E)). For n_B ≤ 3
and n_A ≥ 5 this is small when π_A^E ≈ π_B.

A plurality responder therefore cannot start spread from the witnesses on a filled lattice. It
needs empty slots, earlier flips or ties broken toward P_e.

**Proposition 4b (witness flicker).** If a witness holding P_e moves off it with per-round hazard
h_out, and a witness not holding P_e moves onto P_e (not merely to another rule) with hazard h_in,
both constant over rounds, its stationary probability of holding P_e is h_in/(h_in + h_out), and
the witness plateau is w · h_in/(h_in + h_out). Hazards are pooled over witness-rounds; they are
descriptive inputs, and the check is against run-level outcomes.

### 3.5 Aggregating checks

Replace rule-naming by a vote: each cell answers whether a candidate R fits its own example. A rule
that fits a share f_R of examples gets yes answers at rate q_R = f_R TPR_j + (1 − f_R) FPR_j, where
j is the number of operations in R.

**Proposition 5.** With f = 1 for P_e (two operations) and f = 0.75 for E (one operation), the
expected vote ranks P_e above E if and only if

  Δ = TPR₂ − (0.75 TPR₁ + 0.25 FPR₁) > 0.

The rates TPR_j and FPR_j are properties of the agent and of rule complexity. They are the same for
every voter, and each voter has one example. The number of independent pieces of evidence is
therefore the number of examples (100), not the number of votes cast, and repeating rounds adds
nothing. If Δ ≤ 0 the vote selects the prefix for any number of examples. If Δ > 0 it selects P_e
reliably only when Δ exceeds the sampling noise of n examples. The locked criterion is the
one-sided normal bound

  Δ > 1.645 · √( q_P(1 − q_P)/n + q_E(1 − q_E)/n ),  with q_P = TPR₂, q_E = 0.75 TPR₁ + 0.25 FPR₁,

evaluated at n = 100 with the measured rates.

## 4. Result I: the population has the answer and loses it in checking

**The evidence suffices.** Theorem 1 applies to all three worlds (audit). The failures below are
not caused by topology or missing information.

**Witnesses hold the true rule only when the agent can check.** Table 1 gives, for each model and
mode, the number of witnesses holding P_e at round 20 of the world-1 runs, and a battery measure of
checking under social pressure: 20 witness cells (from world 3) are shown an inbox of eight prefix
lines and no P_e line, two draws each, and we count answers whose rule fits the cell's own example.
The prefix never fits a witness's example, so this counts how often a witness resists a unanimous
wrong inbox with a rule its evidence allows.

Table 1. Witnesses at round 20 (two runs per entry) and own-example fit under a unanimous prefix
inbox. The fit measure was defined after earlier battery results were seen and is descriptive.

| model | mode | lattice: B at round 20 (/25) | `all`: B at round 20 (/25) | own-example fit (/40) |
|---|---|---|---|---|
| Luna | Responses, medium | 25, 25 | 22, 23 | 40 |
| Luna | Responses, none | 0, 0 | 0, 0 | 9 |
| Luna | Decisions | — | — | 4 |
| gpt-oss-20b | default | 24, 25 | 25, 25 | 35 |
| Qwen3-4B-Thinking | thinking | 20, 22 | 11, 17 | 37 |
| Qwen3-4B-Instruct | no thinking | — (battery only) | — (battery only) | 12 |
| Spark-X2.6-4B | thinking off (only mode that passed the pilot) | 0, 0 | 0, 0 | 17 |
| gpt-oss-120b | default | [PENDING] | [PENDING] | 39 |

The same model with reasoning off never gets its witnesses onto P_e: Luna at effort none has 0 of
25 witnesses on P_e at round 1 and at round 20, on both topologies, against 22–25 at round 20 at
effort medium. In the battery, Luna at effort none and with the Decisions API answers the prefix to
most unanimous inboxes (24/40 and 34/40), which no witness's example allows. Non-reasoning failure
is not one thing: Qwen3-4B-Instruct almost never names the prefix (0/40) but names rules that do not
fit its example (28/40), and Spark at thinking off ends with its witnesses on neither P_e nor the
prefix (25 of 25 on other rules at round 20, all four runs).

Spark caveat. Two runs of the same round-1 prompts gave different rule distributions (swap test
p = 1/20001 in both topologies), and a batched-against-serial check on the Spark serving image
found more repeated answers when batched (collision 0.25 against 0.21, p = 0.024; the second image
in the check failed to start, so the diagnosis is incomplete). We use Spark's runs only for the
direction of their outcome (x ≤ 0.002 in every run, 0 witnesses on P_e) and not for which wrong
rule they converge on. Without its witnesses a population has no route to P_e, whatever
its response to messages. The rest of the paper concerns agents that keep them.

The battery split between reasoning and non-reasoning modes holds in world 3, where the battery
cells come from. In world 1 Luna medium's witnesses give the prefix in 17/40 under a constructed
prefix memory. The gap is specific to the world-1 rule. In a battery that keeps one round-1 prompt
and replaces only the example, Luna medium named the prefix `shift_symbols(1)` for 6 of 40 examples
of `shift_symbols(1);swap(2,3)` and for 0 of 40 examples of `shift_symbols(1);swap(0,3)` (paired
over 17 shared base examples: difference 0.147, sign-flip p = 0.031). Qwen3-4B-Thinking named it 0
times in both. The main world is the hardest of these rules for Luna to check, which works against
Luna in every world-1 result. We do not state the split as a general property.

Qwen's witnesses leave P_e and return. With the measured class-B hazards (rounds 2–20, both runs
pooled), Proposition 4b gives a stationary share of 0.84 on the lattice (onto P_e 72/209 = 0.344,
off P_e 50/741 = 0.067), or 21 of 25 witnesses; observed at round 20: 20 and 22. On `all`
(111/313 = 0.355 and 104/637 = 0.163) it gives 0.69, a plateau of 0.17; observed mean x(10–20):
0.16 and 0.20. Where a Qwen witness goes when it leaves differs from Luna: on the lattice 29 of 50
leaves go to another rule that fits the witness's own example, against 0 of 35 for Luna, all of
whose leaves go to the prefix (one-sided Fisher p = 1.5 × 10⁻⁹, locked prediction QM3). Qwen's
witnesses keep checking and lose the true rule among other rules their example allows; Luna's
witnesses, when they leave, conform.

**Voting on checks does not select P_e.** We measured TPR and FPR on 2,272 items: for each example
in three worlds, P_e, the prefix, other consistent rules and non-fitting one- and two-operation
rules, with truth computed by code (Table 2). The locked decision rule compared each arm's Δ with
the bound at n = 100.

Table 2. Checking a given rule against one's own example (Luna, 2,272 items per arm). Intervals:
Wilson 95 % united with an example-cluster bootstrap.

| mode | TPR₁ | FPR₁ | TPR₂ | FPR₂ | Δ [interval] | bound, n = 100 |
|---|---|---|---|---|---|---|
| Decisions | 0.800 | 0.196 | 0.522 | 0.319 | −0.127 [−0.205, −0.042] | 0.114 |
| Responses, none | 0.752 | 0.269 | 0.640 | 0.500 | +0.009 [−0.073, +0.096] | 0.112 |
| Responses, medium | 1.000 | 0.028 | 0.834 | 0.018 | +0.077 [+0.047, +0.117] | 0.093 |

The three modes fall in three places. With the Decisions API the vote prefers the prefix (Δ < 0,
interval below 0). At effort none P_e and the prefix are indistinguishable. At effort medium the
vote prefers P_e (interval above 0), but by less than 100 examples resolve. None of the three modes
lets a population of 100 select P_e by voting.

The binding term is the two-operation true-positive rate. At effort medium Luna accepts every
example that the prefix fits (210/210) and rejects 17 % of those that P_e fits (141/851). In the
one-pass modes, checking accuracy drops with complexity: Youden J is 0.604 for one operation and
0.203 for two with the Decisions API (paired difference over 210 examples −0.325, sign-flip
p = 0.00005; locked prediction V1 holds), and 0.483 and 0.140 at effort none. Reasoning raises
two-operation J from 0.203 to 0.817 (V2 holds). A complex true rule loses to its simple prefix
because the checking error is larger for complex rules, and the error is the same for every agent.

The stage-0 arms for local models were planned and not run; this result is for one model.

**Reading.** In this world the population does not fail for lack of information or of a channel.
It fails at checking, and checking does not aggregate. What remains is the dynamics of rule-naming,
which depend on how agents respond to the names they see.

## 5. Result II: the response function decides the population

### 5.1 Measuring the response

We measured a, b and α, β in a battery outside the population. Twenty class-A cells from world 1
received constructed states: a memory line holding E (adopt direction) or P_e (abandon direction),
and an inbox with exactly k P_e lines, m prefix lines and 8 − k − m empty slots (lattice form, 19
conditions), or 88 published lines at P_e shares from 0 to 1 (`all` form, 10 conditions). Line
positions and message signals were assigned by hash; prompts were identical across models except
for the manipulated block. Each model received 2,960 calls.

| measure | definition | Luna | gpt-oss-20b | Qwen | gpt-oss-120b |
|---|---|---|---|---|---|
| S88 | a(0.60) − a(0.40), n = 88 | 0.925 | 0.200 | [FILL] | [PENDING] |
| M88 | mean a at shares 0.10–0.30 | 0.008 | 0.064 | [FILL] | [PENDING] |
| R88 | b at share 0.30 | 0.95 | 0.617 | [FILL] | [PENDING] |
| E8 | a(1, 0) − a(1, 7), n = 8 | 0.90 | 0.40 | [FILL] | [PENDING] |

The four locked contrasts between Luna and gpt-oss-20b (A1–A4) hold. Luna follows the plurality of
visible lines: at n = 8, logit a = −0.27 + 1.47 k − 1.24 m, so a P_e line and a prefix line cancel
and an empty slot counts for nothing. At n = 88, logit α = −8.26 + 16.3 s, a threshold at s ≈ 1/2.
gpt-oss-20b responds to a P_e minority (M88 eight times Luna's) and resists a P_e majority less
sharply. We call these the threshold and graded classes.

[Figure 1: a(k, m) at n = 8 and α(s), β(s) at n = 88, per model, with cell-cluster intervals.]

### 5.2 The response predicts the topology ranking

A simulator (committed before the battery) places class-A cells on each topology, drives them with
the battery fits, and drives witnesses and publication with measured round-1 holding and
publication rates. It has no parameter tuned to the population outcome. Prediction B1: the sign of
x_lattice − x_all in simulation equals the observed sign, for each model.

| model | lattice: sim / observed | `all`: sim / observed | B1 |
|---|---|---|---|
| Luna (medium) | 1.00 / 0.86, 0.97 | 0.30 / 0.23, 0.31 | holds |
| gpt-oss-20b | 0.40 / 0.37, 0.45 | 0.67 / 0.85, 0.87 | holds |
| Qwen | [PENDING] | [PENDING] | [PENDING] |
| gpt-oss-120b | [PENDING: prediction record, hash] | [PENDING] | [PENDING] |

Observed values are mean x(10–20) for each of two runs. The ranking reverses between the two models
and the simulator reproduces both. The level for gpt-oss-20b on `all` is underpredicted (0.67
against 0.85–0.87). In the population gpt-oss-20b adopts more at intermediate shares than in the
battery (at share 0.5: 35/97 = 0.36 against 9/40 = 0.23), and its inboxes hold 79 lines on average
rather than the battery's 88. We claim the ranking, not the level.

Two counterfactual simulations separate the response from the other inputs (publication by round
and class, round-1 starts). Each model's response functions are run with the other model's inputs
(Table 3). The ranking follows the response functions in both cases.

Table 3. Simulated mean x(10–20), 200 runs each.

| response functions | other inputs | lattice | `all` | winner |
|---|---|---|---|---|
| Luna | Luna | 1.00 | 0.30 | lattice |
| Luna | gpt-oss-20b | 1.00 | 0.27 | lattice |
| gpt-oss-20b | gpt-oss-20b | 0.40 | 0.67 | `all` |
| gpt-oss-20b | Luna | 0.54 | 0.82 | `all` |

The inputs change the levels (gpt-oss-20b gains 0.14–0.15 on both topologies with Luna's
publication) but not the sign. A third simulation tests Corollary 2: setting Luna's class-A
round-1 publication to gpt-oss-20b's rate (0.06 → 0.91 on the lattice) halves the round-2 share of
P_e (0.51 → 0.25), as Lemma 1 requires, and leaves the final outcome at 1.00. Silence speeds Luna's
lattice spread; it does not decide it.

On the lattice Luna wins through empty slots. Its class A publishes rarely in round 1 (about 1 %),
so a witness's line is often the only line in a neighbour's inbox, and a(1, 0) = 0.95. gpt-oss-20b
class A publishes from round 1 and fills the inboxes with the prefix (Proposition 4). On `all` the
same threshold that helps Luna on the lattice holds it at the witness plateau (Proposition 2),
while gpt-oss-20b's minority response lets P_e grow from the 25 % witness share (Proposition 3).

[PENDING: gpt-oss-20b in worlds 3 and 5, C1 and C2.]

### 5.3 On the complete graph, the threshold responder is bistable

The simulation of Luna on `all` predicted occasional tipping: 15.0 % of simulated runs (Wilson 95 %
[10.7, 20.7]) crossed s = 1/2 early and went to x ≈ 1. The two earlier runs were both frozen. We ran
20 new runs with fresh caches. Locked predictions: at least one tip (T1), at most 8 (T2, the 97.5th
percentile of Binomial(20, 0.207)), and a non-tipper median within the simulated band [0.269,
0.753] (T3).

Eight runs tipped (0.40, Wilson [0.22, 0.61]). T1 holds. T2 holds at its limit. T3 fails: the
non-tipper median is 0.241, just below the band. The earlier statement "Luna loses on `all`" was a
statement about two draws from a bimodal distribution.

*Post hoc.* Round-1 publication was near zero (class A about 1 %, class B about 3 %), so the round-2
board held a few lines. Runs with s(2) ≥ 0.5 tipped in 6 of 8, runs with s(2) < 0.5 or an empty
board in 2 of 12. With round-1 inputs pooled over 22 runs the simulator gives a tip rate of 0.315
[0.255, 0.382].

### 5.4 Who speaks first decides it

If the outcome is set by the first published lines, constructing them should set it. Each run
played round 1 live. The round-2 board was then constructed from that run's own round-1 rules, in
one of two ways:

- F0: every cell is shown as having published its round-1 rule;
- F1: only the witnesses holding P_e are shown as having published.

Each cell's memory line was set to match. Rounds 3–20 ran live. Eight runs per arm, alternating.
Before any call, the simulator gave tip rates of 0.012 for F0 and 1.000 for F1, and the locked
predictions were: F1 tips more often than F0 (F-T1, one-sided Fisher), F1 tips at least 7 times
(F-T2), F0 at most once (F-T3).

All eight F1 runs tipped at round 2. One of eight F0 runs tipped; the other seven froze near 0.23.
Fisher exact p = 0.0007. All three predictions hold.

The F0 run that tipped started from s(2) = 0.16. Its class A adopted little at round 2 (5 of 75
cells), but only 29 of 75 class-A cells published, the fewest among the F0 runs (others 47–67). The
round-3 board was therefore mostly witnesses (s(3) = 0.491, others 0.207–0.333), and class-A
holders went to 28, 52 and 75 over the next three rounds (post hoc, one event). This is the
condition of Proposition 2: s crosses 1/2 when class-A publication of E falls to about a third of
the witnesses'. F1 imposes that silence; this run drew it.

[Figure 2: x(t) for the 16 runs, F0 and F1, with the 20 unmanipulated runs in grey.]

## 6. Discussion

**Collective computation with one-pass agents.** In this world a population reaches a rule that
75 % of its members cannot distinguish from a false one, but not by voting on evidence. It gets
there, when it does, through the way agents respond to the names they see. The same response that
reaches P_e on the lattice holds the population at the witness plateau on the complete graph.

**The agent is described by curves, not by a score.** Luna checks rules more accurately than
gpt-oss-20b, and loses to it on the complete graph. The difference is the shape of the response,
not competence. A model's position on single-agent benchmarks does not predict what a population
of it will do; its response functions do, at least for the ranking.

**Protocol levers.** Three follow from the theory and the experiments: who publishes first (5.4);
silence of the majority rule's holders (Lemma 1, Proposition 2); and matching the topology to the
response class (5.2). All three can be set by a system designer without changing the agents.

## 7. Limitations

- One task family and three worlds, all with a true rule equal to a prefix plus one swap. The
  world-1 swap (2,3) is the one Luna checks worst (Section 4).
- Population results rest on two runs per arm, except the Luna `all` tipping (20) and
  first-speaker (16) experiments.
- The threshold case is one closed model, accessed through an API whose model can change. Run
  dates and the model string are recorded (Appendix D).
- The battery underestimates in-population adoption for graded responders; level predictions are
  not claimed.
- The F0/F1 construction shows cells a memory line that may differ from what they did in round 1.
  This is the manipulation and is stated as such.
- gpt-oss-20b runs used a chat template that inserts the current date. [FILL: date-sensitivity
  check.]

## 8. Related work

[FILL, short: threshold and complex contagion (Granovetter 1978; Centola & Macy 2007); voter and
majority dynamics on graphs; correlated errors in jury aggregation (Ladha 1992); LLM populations
and consensus formation; LLM cellular automata (LOGOS-CA, LLMCA); multi-agent debate under
correlated errors; TSI (arXiv 2610.26777) for the sheaf formulation.]

## 9. Conclusion

[3–4 sentences, written last.]

## Appendix

- A. Proofs (Propositions 3, 4, Lemma 1; Computation 2, the heterogeneous mean field).
- B. Prompts: one full prompt per experiment, and the battery's constructed blocks.
- C. All locked predictions and outcomes (below, expanded with the earlier panel predictions).
- D. Models, serving, decoding, template pins, sampler gates, run dates. Includes the arms that
  were not run and why: Spark-X2.6-4B high and low reasoning failed the locked pilot rule (more
  than 1 truncation in 20 calls at 32,768 completion tokens: high 2 of the first 2, low 3);
  gpt-oss-120b's first four loads failed on memory before any call.
- E. Cost.

### C. Prediction table

| ID | prediction (locked) | source | result |
|---|---|---|---|
| Th. 1 | global answer exists (world audit) | `THEORY.md` | holds |
| V1 | one-pass J(two-op) < J(one-op) | `AMENDMENT_P1_STAGE0_VERIFY.md` | holds (Luna; local arm not run) |
| V2 | reasoning J(two-op) > one-pass J(two-op) | same | holds (Luna pair; Qwen pair not run) |
| D | decision class per arm by Δ vs bound | same | D-none for all three Luna arms |
| A1–A4 | Luna vs gpt-oss-20b response contrasts | `AMENDMENT_CONTAGION.md` | hold |
| B1 | simulated ranking sign = observed, Luna and gpt-oss-20b | same | holds |
| B1-Qwen | scored after the Moore runs | same | [PENDING] |
| C1, C2 | gpt-oss-20b `all` > 0.5 and > lattice, worlds 3 and 5 | same | [PENDING] |
| T1, T2, T3 | Luna `all` tips sometimes, not often; frozen level | `AMENDMENT_LUNA_ALL_TIPPING.md` | T1, T2 hold; T3 fails |
| F-T1–F-T3 | constructed first speakers set the outcome | `AMENDMENT_LUNA_FIRST_SPEAKER.md` | hold |
| O1–O3 | gpt-oss-120b ranking, level, class, out of sample | `AMENDMENT_OSS120_PREDICTION.md` | [PENDING] |