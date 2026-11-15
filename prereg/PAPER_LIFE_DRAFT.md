# Who Speaks First: response rules, topology and the limit of checking in populations of language-model agents

**Status:** arXiv text **v1.22**, 2026-11-15 (v1.21 plus decoding settings for every model in the Models paragraph and a limitation on unequal sampling temperature). v1.21, 2026-11-15 (v1.20 plus Chuang et al. 2024 and one sentence on Okawa's neighbour count in Section 8). v1.20, 2026-11-15 (v1.19 plus two related-work additions in Section 8: Okawa 2026 and Mallick, Thomo and Saxena 2026). v1.19, 2026-11-14 (v1.18 plus the Qwen check-nudge result in §6 and Appendix C, rechecked from raw data). v1.18, 2026-11-13 (v1.17 plus the Qwen battery reproducibility check in §5.1, §7 and Appendix C, and the steering result in §6, both rechecked from raw data). v1.17, 2026-11-09: the gpt-oss-120b continuation to round 80 in §5.5, the abstract and Appendix C, rechecked from raw data. Independent recheck from raw data done for Sections 4
and 5 (Qwen battery, B1, the gpt-oss-20b and gpt-oss-120b text reruns, the 120b prediction record
and O3 included) and QX-1/QX-1p (`QX_RECHECK_REPORT.md`, `RECHECK_REPORT_2.md`,
`PAPER_LIFE_CHANGELOG.md`). v1.11 applies `PAPER_LIFE_REVIEW_2026-10-30.md`; `[VERIFY]` marks a
number taken from the review that is not yet recomputed independently.
Target: cs.MA. Successor to `PAPER_CLAIMS_LIFE_DRAFT.md`,
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
100 examples can resolve, in any of three modes. With the Decisions API it loses to the prefix; at
effort none it ties. On the true rule itself, no mode accepts it more often than the prefix. The
checking error grows with rule complexity and is shared by all agents, so adding voters does not
remove it. Second, response. We
reduce each agent to three functions — the probability of adopting the true rule, of abandoning
it, and of publishing — measured in a controlled battery outside the population. Their shape
differs by model: a threshold rule for one model, a graded response for another. Without fitting
to any population outcome, these functions predict which topology each model does better on, and
the ranking reverses between models. For the graded model the ranking replicated in six new runs
per topology (exact permutation p = 0.001) and held in a second world; in a third world it failed, and
there, on the complete graph, the witnesses moved to a rival two-step rule that fits 21 of their 25
examples. For a third model, measured and predicted before any of its
population runs, the predicted ranking held on both locked windows up to round 40, but the margin
was small and the simulator overestimated how fast the population converges. Continued to round
80, the ranking reversed: the lattice runs did not converge, the two frozen complete-graph runs
escaped, and over rounds 70–80 the complete graph was ahead (0.87 against 0.80). All three locked
predictions for the continuation failed. Post hoc, both topologies settled near the same level, set by
agents that keep leaving the true rule at about 10 % per round even when nearly all their
messages name it. On the complete graph the
threshold model is bistable: in 20
runs, 8 converge to the true rule and 12 freeze. Constructing the first round of published messages
changes the convergence rate from 1/8 to 8/8 (one-sided Fisher exact p = 0.0007). Every prediction was locked
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
quarter of the population and are scattered on the grid. Messages carry rule names, never
examples.

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
   predict the topology ranking for two models whose rankings are opposite, and the sign, but not
   the size or speed, of the ranking for a third, held-out model. On the complete graph, a threshold responder's outcome is decided by the first
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
rule name, a publication bit and an integer signal from 0 to 7. A published line shows its sender's
cell number, the round, the signal and the rule name; nothing else a cell writes reaches another
cell. An audit of all 213,002 population prompts, re-rendered from the run caches, found only
catalog rule names in the inbox, no example string in any inbox, and no information about the
sender's example in its signal (at most 0.009 bits per input symbol; Appendix D). The constitution
still mentions a short text field that the output schema does not have. There is no feedback and no seeded holder of P_e. The prompt is
byte-identical across models for the same state.

**Topologies.** The Moore lattice: eight neighbours, and an unpublished neighbour appears as an
empty slot. The complete graph (`all`): the inbox holds every line published in the previous round.

**Models.** `gpt-6-luna` (OpenAI, through the Responses API at reasoning effort medium; the
Decisions API and effort none appear in Section 4); gpt-oss-20b; Qwen3-4B-Thinking-2507;
gpt-oss-120b, held out: its population runs were predicted before they were made. Local models are
served with SGLang with pinned images, chat templates and decoding (Appendix D); every gpt-oss-120b
call uses a chat template pinned to a fixed date. Every model gets the same prompt. Decoding differs
by model. Luna uses the Responses API defaults: temperature and top_p are not sent, and reasoning
effort is medium. gpt-oss-20b and gpt-oss-120b are sampled at temperature 1.0 and top_p 1.0, with
reasoning effort medium. Qwen3-4B-Thinking is sampled at temperature 0.6, top_p 0.95, top_k 20 and
min_p 0, with at most 32,768 tokens; these are the settings its model card recommends for thinking
mode.

**Measures.** x(t), the share of all cells holding P_e at round t. The run outcome is the mean of
x(t) over rounds 10–20. A run "tips" if that mean exceeds 0.9. The gpt-oss-120b runs last 80
rounds; their locked predictions use rounds 1–20 as for the other models, and two later, separately
locked sets use rounds 30–40 and 70–80 (Section 5.5). The unit of inference is the run for population results
and the cell for battery results.

## 3. Theory

The theory is written so that each statement names its measured inputs and the observation that
would refute it. No parameter is fitted to the population outcome a statement predicts. Proofs
longer than a few lines are in Appendix A.

### 3.1 The task has a global answer

Notation: r_c(t) is the rule held by cell c at round t and z_c(t) ∈ {0, 1} its publication bit.
The inbox of c at round t holds the rules of neighbours d with z_d(t − 1) = 1. We write k and m for
the numbers of inbox lines naming P_e and E.

**Theorem 1 (sufficiency).** If ⋂_c S_c = {P_e} and the graph G is connected, there is a protocol
with messages of O(|ℛ|) bits under which every cell holds P_e from round diam(G) + 1 on.

*Proof.* Each cell publishes its current candidate set and replaces it by the intersection with
the sets it receives. The sets only shrink and always contain P_e. After diam(G) exchanges every
set equals ⋂_c S_c. ∎

In sheaf terms, in the spirit of [TSI, arXiv 2610.26777], the local sections S_c glue to a
non-empty global section, so there is no obstruction on any connected topology. Any failure to reach P_e is a property of the
agents or of the rule-naming protocol, not of the graph.

**Corollary 1.** E ∈ S_c for every c in class A. The false consensus "all cells hold E" agrees with
75 % of the evidence, and no class-A cell can detect it from its own example.

### 3.2 The agent as three functions

Class-A answers lie almost entirely in {P_e, E}: in the battery of Section 5, Luna 100 %,
gpt-oss-20b 2,954 of 2,960, gpt-oss-120b 2,959 of 2,960. A class-A cell is then a two-state chain with

- adopt: a(k, m) = P(r(t+1) = P_e | r(t) = E, inbox with k P_e lines and m E lines);
- abandon: b(k, m) = P(r(t+1) = E | r(t) = P_e, same inbox);
- publish: π_X^R(t) = P(z(t) = 1) for a cell of class X holding R at round t.

On `all` the inbox enters through the share s of P_e among visible lines, and we write α(s), β(s).
Witnesses are taken to keep P_e once they hold it (h_B = 1); Proposition 4b drops this.

**Assumption M.** a and b depend only on the current rule and the current inbox. *Test:* a
simulator driven by the empirical full-run hazards, binned by (k, m) or by s, reproduces all four
world-1 population outcomes under the locked criterion, which widens the observed two-run range by
its own width on each side (Luna lattice 0.972 against observed 0.865–0.967; Luna `all` 0.291
against 0.232–0.307; gpt-oss-20b lattice 0.448 against 0.374–0.445; gpt-oss-20b `all` 0.885 against
0.850–0.871). Three of the four simulated values lie just outside the bare two-run range. This checks the reduction, not the prediction; the prediction (Section 5.2) uses
functions measured outside the population.

### 3.3 The complete graph

Let w = 0.25 be the witness share and x_A(t) the share of class A holding P_e. The P_e share on the
board is

  s(t) = [w π_B + (1 − w) x_A π_A^P] / [w π_B + (1 − w)(x_A π_A^P + (1 − x_A) π_A^E)],

and the mean-field recursion is x_A(t+1) = x_A + (1 − x_A) α(s) − x_A β(s). Here s counts P_e lines
among lines naming P_e or E; lines naming other rules (rare except for Qwen) are left out, and an
empty board counts as s = 0.

**Proposition 2 (threshold freezing).** If α(s) = 0 and β(s) = 1 for s < θ, all witnesses hold P_e
from t₀ on, x_A(t₀) = 0, and s₀ = w π_B / (w π_B + (1 − w) π_A^E) < θ for all t ≥ t₀, then x_A
stays 0 and x = w.

With Luna's θ ≈ 1/2 and the measured rates on Luna `all` — π_B ≈ 0.94–1.0 from round 4, class-A
publication 0.79–0.89 from round 5 (0.71 at its lowest, round 4), which is close to π_A^E because
x_A is small — s₀ ≈ 0.28, and at most
0.31 at the lowest rate, so the prediction is x ≈ 0.25. The condition s₀ < 1/2 fails only when π_A^E ≤ π_B · w/(1 − w) ≈ π_B/3:
class A has to be mostly silent for the witnesses to carry the board.

**Proposition 3 (graded spread).** If α(s) ≥ ε > 0 and β(s) ≤ β̄ < 1 on the reachable range of s,
every fixed point satisfies x_A* ≥ ε/(ε + β̄). If, in addition, the publication rates do not depend
on t, α and β are continuous, α is non-decreasing and β non-increasing in s, and α + β ≤ 1 on the
reachable range, then the map x ↦ x + (1 − x) α(s(x)) − x β(s(x)) is non-decreasing (s is
non-decreasing in x_A for any publication rates), and the recursion converges monotonically from 0
to the smallest fixed point. Without α + β ≤ 1 the iterates can oscillate (α = β = 0.6 is an
example).

**Bistability.** For a threshold responder there are two attractors, the witness plateau and
x = 1 (the upper one requires β(1) = 0). In the deterministic recursion x_A = 0 never leaves 0; a
finite population leaves it through noise in the early board. Which attractor a run reaches depends
on whether s crosses θ in the first rounds. When round-1
publication is sparse, s(2) is computed from a handful of lines and is a noisy draw. The prediction
is that fixing the early board fixes the outcome. Section 5.4 tests it.

### 3.4 The lattice

**Lemma 1.** If a(k, m) is non-decreasing in k and non-increasing in m and c's class-A neighbours
hold E, the probability that c adopts at the next round is non-increasing in π_A^E.

So silence of E-holders can only help early local adoption. In world 1 every class-A cell has two
or three witness neighbours and none has four or more (dry build).

**Proposition 4 (plurality on a filled lattice).** Under a = 1[k > m], b = 1[m > k], with all
class-A neighbours on E, c flips with probability P(Bin(n_B, π_B) > Bin(n_A, π_A^E)). For n_B ≤ 3
and n_A ≥ 5 this is small only when both rates are high: with n_B = 3, n_A = 5 and π_A^E = π_B = π
it is 0.17, 0.20, 0.14, 0.03 and 0.006 at π = 0.1, 0.3, 0.5, 0.8 and 0.9.

A plurality responder therefore cannot start spread from the witnesses on a filled lattice. It
needs empty slots, earlier flips or ties broken toward P_e.

**Proposition 4b (witness flicker).** If a witness holding P_e moves off it with per-round hazard
h_out, and a witness not holding P_e moves onto P_e (not merely to another rule) with hazard h_in,
both constant over rounds and h_in the same whichever other rule the witness holds, its stationary
probability of holding P_e is h_in/(h_in + h_out), and
the witness plateau is w · h_in/(h_in + h_out). Hazards are pooled over witness-rounds; they are
descriptive inputs, and the check is against run-level outcomes.

### 3.5 Aggregating checks

Replace rule-naming by a vote: each cell answers whether a candidate R fits its own example. A rule
that fits a share f_R of examples gets yes answers at rate q_R = f_R TPR_j + (1 − f_R) FPR_j, where
j is the number of operations in R.

**Proposition 5.** With f = 1 for P_e (two operations) and f = 0.75 for E (one operation), and
writing TPR₂ for the yes rate on P_e itself, the expected vote ranks P_e above E if and only if

  Δ = TPR₂ − (0.75 TPR₁ + 0.25 FPR₁) > 0.

The rates TPR_j and FPR_j are properties of the agent and of rule complexity. They are the same for
every voter, and each voter has one example. The number of independent pieces of evidence is
therefore the number of examples (100), not the number of votes cast. With one fixed answer per
prompt, as with our cached calls, repeating rounds adds nothing; with sampled answers, repetition
reduces each example's noise but cannot change the sign of the expected margin. If Δ < 0 the vote
selects the prefix with probability tending to 1 as examples are added; Δ = 0 is a tie. If Δ > 0 it selects P_e
reliably only when Δ exceeds the sampling noise of n examples. The locked criterion is the
one-sided normal bound

  Δ > 1.645 · √( q_P(1 − q_P)/n + q_E(1 − q_E)/n ),  with q_P = TPR₂, q_E = 0.75 TPR₁ + 0.25 FPR₁,

evaluated at n = 100 with the measured rates. The locked bound treats the two yes rates as
independent; each example answers both items, so the paired variance Var(Y_P − Y_E)/n is the exact
form. The locked rule pools TPR₂ over all fitting two-operation rules; Table 2 also gives the rate
on P_e itself.

## 4. Result I: the population has the answer and loses it in checking

**The evidence suffices.** Theorem 1 applies to all three worlds (audit). The failures below are
not caused by topology or missing information.

**Witnesses hold the true rule only when the agent can check.** Table 1 gives, for each model and
mode, the number of witnesses holding P_e at round 20 of the world-1 runs, and a battery measure of
checking under social pressure: 20 witness prompts from world 3 (taken from different rounds and
runs, covering 13 distinct witness cells) are shown an inbox of eight prefix lines and no P_e line,
two draws each, and we count answers whose rule fits the cell's own example. Because some cells
appear more than once, the 40 answers rest on 13 private examples.
The prefix never fits a witness's example, so this counts how often a witness resists a unanimous
wrong inbox with a rule its evidence allows.

Table 1. Witnesses at round 20 (two runs per entry; four for gpt-oss-120b) and own-example fit under a unanimous prefix
inbox. The fit measure was defined after earlier battery results were seen and is descriptive.

| model | mode | lattice: B at round 20 (/25) | `all`: B at round 20 (/25) | own-example fit (/40) |
|---|---|---|---|---|
| Luna | Responses, medium | 25, 25 | 22, 23 | 40 |
| Luna | Responses, none | 0, 0 | 0, 0 | 9 |
| Luna | Decisions | 0, 0 | not run | 4 |
| gpt-oss-20b | default | 24, 25 | 25, 25 | 35 |
| Qwen3-4B-Thinking | thinking | 20, 22 | 11, 17 | 37 |
| Qwen3-4B-Instruct | no thinking | — (battery only) | — (battery only) | 12 |
| Spark-X2.6-4B | thinking off (only mode that passed the pilot) | 0, 0 | 0, 0 | 17 |
| gpt-oss-120b | default, date pinned | 21, 19, 22, 25 | 24, 22, 25, 25 | 39 (earlier battery, context 36,864) |

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
cells come from. In world 1 Luna medium's witnesses give the prefix in 17/40 answers when their
memory holds another fitting rule and the inbox holds eight prefix lines. The gap is specific to
the world-1 rule. In a battery that keeps one round-1 prompt and replaces only the example, Luna
medium named the prefix `shift_symbols(1)` in 6 of 40 answers (20 examples, two draws) for
`shift_symbols(1);swap(2,3)` and in 0 of 40 for `shift_symbols(1);swap(0,3)` (locked test I2,
one-sided Fisher p = 0.013; paired over 17 shared base examples, reported beside it: difference
0.147, sign-flip p = 0.031). Qwen3-4B-Thinking named it 0
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

**Voting on checks does not select P_e.** We measured TPR and FPR on 2,272 items from 284
examples: all 100 examples of worlds 3 and 5 and 84 of world 1, eight candidate rules each (P_e,
the prefix, other consistent rules and non-fitting one- and two-operation rules), with truth
computed by code (Table 2). Sixteen world-1 class-A cells with too few consistent rules to fill the
design were left out of the item set. Items with identical prompts share one cached answer, so each
arm used 2,045 distinct prompts (the Decisions arm asked each in two orderings); intervals are
clustered by example. The 284 examples hold 228 distinct input–output pairs (63 among the 84 of world 1),
so the clustering treats some duplicates as independent. The locked decision rule compared each arm's Δ with
the bound at n = 100.

Table 2. Checking a given rule against one's own example (Luna, 2,272 items per arm). Intervals:
Wilson 95 % united with an example-cluster bootstrap.

| mode | TPR₁ | FPR₁ | TPR₂ | FPR₂ | Δ [interval] | bound, n = 100 |
|---|---|---|---|---|---|---|
| Decisions | 0.800 | 0.196 | 0.522 | 0.319 | −0.127 [−0.205, −0.042] | 0.114 |
| Responses, none | 0.752 | 0.269 | 0.642 | 0.500 | +0.010 [−0.072, +0.097] | 0.112 |
| Responses, medium | 1.000 | 0.028 | 0.834 | 0.018 | +0.077 [+0.047, +0.117] | 0.093 |

*Post hoc, on P_e and its prefix only* (the estimand of Proposition 5; q for the prefix uses the
locked 0.75/0.25 weights on the prefix's own yes rates):

| mode | P_e accepted | prefix accepted (fits / does not) | Δ on P_e |
|---|---|---|---|
| Decisions | 149/284 = 0.525 | 167/209, 18/75 | −0.134 |
| Responses, none | 179/284 = 0.630 | 157/209, 28/75 | −0.026 |
| Responses, medium | 220/284 = 0.775 | 209/209, 16/75 | −0.029 |

With q for the prefix taken from all one-operation items instead, the three values are −0.124,
−0.001 and +0.018. At effort medium P_e is accepted for 44 of 84 world-1 examples, 76 of 100 in
world 3 and 100 of 100 in world 5.

On the locked pooled rates the three modes fall in three places. With the Decisions API the vote
prefers the prefix (Δ < 0, interval below 0). At effort none P_e and the prefix are
indistinguishable. At effort medium the pooled vote prefers two-operation rules over the prefix
(interval above 0), but by less than 100 examples resolve. On P_e itself the medium margin is
near zero: the pooled advantage comes from the other fitting two-operation rules, which Luna
accepts more often than P_e. None of the three modes lets a population of 100 select P_e by voting.

The binding term is the two-operation true-positive rate. At effort medium Luna accepts the prefix
on every example it fits (209/209) and rejects P_e on 64 of 284 examples (22.5 %), most of them in
world 1. In the
one-pass modes, checking accuracy drops with complexity: Youden J is 0.604 for one operation and
0.203 for two with the Decisions API (paired difference over 210 examples −0.325, sign-flip
p = 0.00005; locked prediction V1 holds), and 0.483 and 0.142 at effort none. Reasoning raises
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
| S88 | a(0.60) − a(0.40), n = 88 | 0.925 | 0.200 (0.300) | 0.025 (0.075) | 0.175 (0.300) |
| M88 | mean a at shares 0.10–0.30 | 0.008 | 0.064 (0.050) | 0.017 (0.017) | 0.039 (0.044) |
| R88 | b at share 0.30 | 0.95 | 0.617 (0.517) | 0.758 (0.733) | 0.717 (0.658) |
| E8 | a(1, 0) − a(1, 7), n = 8 | 0.90 | 0.40 (0.325) | 0.025 (0.108) | 0.400 (0.525) |

In parentheses: a second run of the battery with the model's text stored (Section 7). For both
gpt-oss models it was a full run: it reproduced the stored labels' parse on every call, and each of
the four differences between the runs has a cell-paired 95 % interval that covers 0. For Qwen it was
a reproducibility check on the conditions behind the four measures and the lattice mean (below).

The four locked contrasts between Luna and gpt-oss-20b (A1–A4) hold. Luna follows the plurality of
visible lines: at n = 8, logit a = −0.27 + 1.47 k − 1.24 m, so a P_e line and a prefix line cancel
and an empty slot counts for nothing. At n = 88, logit α = −8.26 + 16.3 s, a threshold at s ≈ 1/2.
gpt-oss-20b responds to a P_e minority (M88 eight times Luna's) and resists a P_e majority less
sharply. We call these the threshold and graded classes.

gpt-oss-120b was measured before any of its population runs. Its S88 and E8 lie inside the
intervals of gpt-oss-20b and outside Luna's (locked prediction O3 holds; it also holds against the
second 20b run): by its battery it is a graded responder.

Qwen, which the locked contrasts do not cover, is a third type. It almost never adopts P_e short of
unanimity (a ≤ 0.10 at every `all` share below 1, a = 0.625 at share 1; a(1, 0) ≈ 0.09 at n = 8)
and abandons P_e for the prefix in 76 % of calls at a P_e share of 0.30. We call it stubborn. Its
battery stopped at a server context limit and was resumed on a second server with the full
40,960-token context: 204 of 2,960 calls ran there, the 0.75 and 1.0 `all` conditions come only
from the resumed part, and a(0.60) includes 4 resumed calls of 40. A sampler gate on the second
server configuration (64 serial against 64 concurrent calls, top serial answer 0.73) found no
difference (p = 0.46), with no truncated answer in either half.

Because the stubborn label rests on small numbers, we checked that Qwen's battery reproduces
(`AMENDMENT_QWEN_PARTA_REPRO.md`, locked before any call). The battery's own prompts and draws were
run again on its own server configuration (standard sampling, as the battery) and, separately, in
the engine's deterministic mode, 1,600 calls per arm with text stored; the S88 and E8 conditions had
six draws per cell instead of two. The locked rule compared run and battery per cell, with a 99 %
cell-bootstrap interval per measure (Bonferroni over five). Lattice mean, S88, M88 and R88
reproduce in both arms (lattice 0.146 and 0.148 against 0.125). E8 does not, in either arm: the run
is higher (+0.083, 99 % CI [+0.008, +0.167]; deterministic +0.067 [+0.008, +0.142]). The whole
difference is in one condition, a single P_e line with seven empty slots: 13/120 and 11/120 in the
runs against 1/40 in the battery, with 0 adoptions against seven prefix lines in all three. Pooled
over battery and runs, a(1, 0) = 25/280 = 0.089 and E8 = 0.089, which we use. The two arms agree with
each other on every measure, so the engine mode does not move Qwen's answers. The pre-stated reading
of the check is that the battery does not reproduce; the condition it fails on does not enter the
stubborn label, and that label stands.

[Figure 1: response functions; spec in `PAPER_FIGURES_SPEC.md`.]

### 5.2 The response predicts the topology ranking

A simulator (committed before the battery) places class-A cells on each topology, drives them with
the battery fits, and drives witnesses and publication with measured round-1 holding and
publication rates. It has no parameter tuned to the population outcome. Two conventions are part
of it: every witness holds P_e from round 2 on (observed for Luna and gpt-oss-20b: 15–20 of 25 at round 2,
22–25 at round 20), and on the complete graph an empty board counts as a P_e share of 0. Prediction B1: the
sign of x_lattice − x_all in simulation equals the observed sign, for each model.

| model | lattice: sim / observed | `all`: sim / observed | B1 |
|---|---|---|---|
| Luna (medium) | 1.00 / 0.86, 0.97 | 0.30 / 0.23, 0.31 | holds |
| gpt-oss-20b | 0.40 / 0.37, 0.44 | 0.67 / 0.85, 0.87 | holds |
| gpt-oss-20b, 6 new runs (R1) | 0.40 / 0.46, 0.32, 0.32, 0.33, 0.29, 0.38 | 0.67 / 0.48, 0.60, 0.81, 0.86, 0.75, 0.76 | holds (R1, p = 1/924) |
| Qwen | 0.27 / 0.24, 0.25 | 0.27 / 0.16, 0.20 | holds (weak) |
| gpt-oss-120b (held out) | 0.48 / 0.31, 0.28, 0.40, 0.41 | 0.35 / 0.29, 0.22, 0.54, 0.29 | holds (O1; gap +0.016) |

Observed values are mean x(10–20) for each run (two per topology, plus six new gpt-oss-20b runs
per topology; four for gpt-oss-120b). The ranking reverses between the two models
and the simulator reproduces both. The level for gpt-oss-20b on `all` was underpredicted in the
first two runs (0.67 against 0.85–0.87); the six new runs spread from 0.48 to 0.86 (mean 0.71). In the population gpt-oss-20b adopts more at intermediate shares than in the
battery (at share 0.5: 35/97 = 0.36 against 9/40 = 0.23), and its inboxes hold 79 lines on average
rather than the battery's 88. We claim the ranking, not the level.

*How much the ranking rests on battery noise (post hoc).* With the fits from the second 20b battery
run the simulated gap shrinks from −0.31 to −0.04 (2,000 runs; `all` 0.40 instead of 0.70); its
sign is kept. Refitting on cell-bootstrap resamples of both runs pooled (5,920 calls, 100 refits)
keeps the sign in 97 % of refits, while the simulated `all` level ranges from 0.39 to 0.76. On the
complete graph gpt-oss-20b sits near the point where small changes in its response switch the
population between stalling and spreading; the ranking is robust to this, the level is not.

*Six more runs per topology (locked test).* The gpt-oss-20b ranking rested on two runs per topology.
We ran six new runs per topology in the same configuration, alternating topologies under one
waiter, and locked the test before the first call (`AMENDMENT_REPLICATES.md`, R1): the six `all`
runs have a higher mean x(10–20) than the six lattice runs, one-sided exact permutation over the
924 splits, α = 0.05. The new lattice runs give 0.29–0.46 (mean 0.35), the new `all` runs 0.48–0.86
(mean 0.71); the difference is +0.36 and no split of the twelve runs gives a larger one, p = 1/924 =
0.001. R1 holds. In all 36 (lattice, `all`) pairs the `all` run is higher, though the lowest `all`
run (0.48) lies only 0.02 above the highest lattice run (0.46). Eleven of the twelve runs lie inside
the simulated 5–95 % band of their topology (2,000 runs: lattice [0.31, 0.54], `all` [0.42, 0.88]);
one lattice run (0.29) lies below it. The spread of the `all` runs is twice that of the lattice
runs (SD 0.14 against 0.06), as expected for a population near its switching point. The first two
`all` runs (0.85, 0.87) were at the top of this spread.

*gpt-oss-120b, predicted before its runs.* The prediction record (sha256 `6a0561cb…`, committed
before any population call) gives lattice 0.48 and `all` 0.35 (200 runs; 2,000 runs: 0.48 and
0.35), a median gap of +0.13: the lattice wins, as for Luna, although by its battery 120b is a
graded responder like 20b. Publication for rounds 2–20 was taken from the second battery run,
because the first did not store the communication field (dated deviation, logged before the
build). Computed before any population result, cell-bootstrap refits put the predicted sign at
0.83 (first battery) to 0.95 (both runs pooled), and a gap of at least 0.10, the locked floor of
O1, at 0.57–0.61. The four runs per topology test the sign; whether the gap clears 0.10 was close
to even odds before the data.

The sign held, narrowly: mean x(10–20) 0.350 on the lattice against 0.335 on `all`, a gap of
+0.016 against the predicted +0.13 (O1 holds). The level did not: four of the eight runs lie
below their simulated 5–95 % band and one above it (O2 fails). Section 5.5 follows the same runs to
round 80.

For Qwen the simulated gap is small: lattice 0.2745 against `all` 0.2655 (+0.009; 2,000 runs give
+0.008 to +0.009 by seed), and the two 5–95 % bands of the 200-run simulation overlap ([0.264,
0.288] and [0.256, 0.275]). The
observed gap is +0.064, with both lattice runs above both `all` runs. B1 holds under its locked
sign rule, but the simulator overpredicts both levels (all four runs lie below their band), and a
responder that barely moves gives the topology little to act on. We count Qwen as consistent with
the ranking claim, not as support for it.

Two counterfactual simulations separate the response from the other inputs (publication by round
and class, round-1 starts). Each model's response functions are run with the other model's inputs
(Table 3). The ranking follows the response functions in both cases.

Table 3. Simulated median of x(10–20), 200 runs each.

| response functions | other inputs | lattice | `all` | winner |
|---|---|---|---|---|
| Luna | Luna | 1.00 | 0.30 | lattice |
| Luna | gpt-oss-20b | 1.00 | 0.27 | lattice |
| gpt-oss-20b | gpt-oss-20b | 0.40 | 0.67 | `all` |
| gpt-oss-20b | Luna | 0.54 | 0.84 | `all` |

The inputs change the levels (gpt-oss-20b gains 0.14–0.17 on both topologies with Luna's
publication) but not the sign. Luna on `all` is bimodal (median 0.29, mean about 0.44): the
occasional tipping of Section 5.3. A third simulation sets Luna's class-A round-1 publication to
gpt-oss-20b's rate (0.06 → 0.91 on the lattice): the round-2 share of P_e halves (0.51 → 0.25),
consistent with Lemma 1, and the final outcome stays at 1.00. Silence speeds Luna's
lattice spread; it does not decide it.

*Post hoc sensitivity to the witness convention.* Drawing each witness's rule every round at the
observed per-round witness share instead of fixing it at P_e (1,000 runs): Luna lattice 0.99,
`all` 0.26; gpt-oss-20b lattice 0.34, `all` 0.48. Both signs survive; the gpt-oss-20b level on `all`
moves further below the observed one. With witnesses frozen at their round-1 rule, an extreme that
the observed runs contradict, the gpt-oss-20b gap nearly vanishes (0.18 against 0.19). The ranking
for the graded model therefore depends on its witnesses reaching P_e, which they do in the
population (24–25 of 25 at round 20).

On the lattice Luna wins through empty slots. Its class A publishes rarely in round 1 (6 %),
so a witness's line is often the only line in a neighbour's inbox, and a(1, 0) = 0.95. gpt-oss-20b
class A publishes from round 1 and fills the inboxes with the prefix (Proposition 4). On `all` the
same threshold that helps Luna on the lattice holds it at the witness plateau (Proposition 2),
while gpt-oss-20b's minority response lets P_e grow from the 25 % witness share (Proposition 3).

*Two other worlds (Part C).* We ran gpt-oss-20b in worlds 3 and 5 with the same builder and
settings, two runs per topology, and locked two predictions, each required in both runs of a world:
C1, every `all` run has x(10–20) > 0.5; C2, every `all` run exceeds every lattice run. In world 3
both hold: `all` 0.843 and 0.844, lattice 0.311 and 0.321. In world 5 both fail, and the ranking is
reversed in every pair: `all` 0.030 and 0.049, lattice 0.260 and 0.142. The reversal between the
models is therefore not a world-1 property, and it is not a property of every world.

What differs in world 5 is the witnesses. On `all` they leave P_e: at round 20, 1 of 25 holds it
in each run, and 20 and 21 hold `reverse;shift_symbols(1)`, a two-step rule with the same first
step as P_e (`shift_symbols(1);swap(0,3)`). At round 1 this rule was already ahead of P_e among
witnesses (10 against 6, 7 against 6). On the lattice the witnesses keep P_e in part (17 and 11 of 25
at round 20). In world 1 no rival rule reaches more than 2 witnesses at round 20 in any of the 12
new runs, and in world 3 none reaches more than 2. This is the case the witness-convention
sensitivity above isolates: the graded model's advantage on `all` depends on its witnesses reaching
P_e, and in world 5 the complete graph carries them to a rival rule instead. The rival is not a checking error. Computed by code, it fits the
own example of 21 of the 25 witnesses (and 23 of the 75 class-A cells): `reverse` and `swap(0,3)` give
the same output whenever the two middle symbols are equal, so only witnesses 9, 11, 93 and 96 can
tell the two rules apart. Every witness that held the rival at round 1 on `all` (10 and 7 cells) held
a rule its own example allows. In worlds 1 and 3 the most-held non-P_e witness rule at round 20 is
the prefix, which fits no witness example. World 5 therefore tests a different situation: P_e is
singled out by four cells, and a population can settle on a rule that almost every witness accepts.
On the complete graph gpt-oss-20b settles there; on the lattice the four separating witnesses keep
P_e alive locally. Luna medium on `all` in world 5, beside: 0.999 and 0.250, with all 25 witnesses
on P_e at round 20 in both runs. (Post hoc description; the witness counts and fits were not
predicted.)

### 5.3 On the complete graph, the threshold responder is bistable

The simulation of Luna on `all` predicted occasional tipping: 15.0 % of simulated runs (Wilson 95 %
[10.7, 20.6]) crossed s = 1/2 early and went to x ≈ 1. The two earlier runs were both frozen. We ran
20 new runs with fresh caches. Locked predictions: at least one tip (T1), at most 8 (T2, the 97.5th
percentile of Binomial(20, 0.207)), and a non-tipper median within the simulated band [0.269,
0.753] (T3).

Eight runs tipped (0.40, Wilson [0.22, 0.61]). T1 holds. T2 holds at its limit. T3 fails: the
non-tipper median is 0.241, just below the band. The earlier statement "Luna loses on `all`" was a
statement about two draws from a bimodal distribution.

The locked reference rate came from one 200-run simulation at seed 0. The same simulator, unchanged,
gives 0.27 and 0.225 at seeds 1 and 2 and 0.234 over 1,000 runs (seed 7); an independent implementation
gives 0.220 ± 0.007 over 4,000 runs. The simulator's long-run tip rate is therefore about 0.22,
and the 200-run interval used for T2 was too narrow. The verdicts stand as locked. The observed
interval [0.22, 0.61] contains that rate, so we do not claim that the population tips more often
than its response functions imply.

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
One-sided Fisher exact p = 0.0007 (two-sided 0.0014). All three predictions hold.

The F0 run that tipped started from s(2) = 0.16. Its class A adopted little at round 2 (5 of 75
cells), but only 29 of 75 class-A cells published, the fewest among the F0 runs (others 47–67). The
round-3 board was therefore mostly witnesses (s(3) = 0.491, others 0.207–0.333), and class-A
holders went to 28, 52 and 75 over the next three rounds (post hoc, one event). This is the
condition of Proposition 2: s reaches about 1/2 when class-A publication of E falls to about a third of
the witnesses'. F1 imposes that silence; this run drew it.

### 5.5 Eighty rounds: the held-out model's ranking does not last

**To round 40.** The simulator, run with the record's inputs past round 20, predicted that the
gpt-oss-120b lattice population reaches P_e almost everywhere by round 40 through the merging of P_e
clusters, while `all` mostly stays stuck. We extended the eight runs to 40 rounds, with the prompts
of rounds 1–20 identical to a 20-round run, and locked three predictions before any call.

| | lattice | `all` |
|---|---|---|
| mean x(30–40), predicted median | 0.95 | 0.35 |
| mean x(30–40), observed, per run | 0.60, 0.37, 0.73, 0.83 | 0.29, 0.37, 0.88, 0.43 |
| x at round 40, per run | 0.67, 0.53, 0.81, 0.96 | 0.24, 0.36, 0.92, 0.52 |
| runs with x(30–40) ≥ 0.8, predicted per run / observed | 0.84 / 1 of 4 | 0.08 / 1 of 4 |

The lattice is ahead on this window (0.633 against 0.494; E1 holds by sign, exact permutation
p = 0.20 with four runs per topology). P_e clusters merge on the lattice: the number of
Moore-connected P_e components falls between rounds 5 and 20 in three of four runs (E2 holds; 5 → 4,
6 → 6, 8 → 2, 9 → 2), and by round 40 two runs hold a single cluster, one of 96 cells. On `all`, one
run tipped to P_e at round 23 and one rose to 0.48 at round 20 and fell back to 0.24.

*Post hoc: the witnesses.* The simulator holds every witness on P_e from round 2. In the population,
witnesses on P_e averaged 55 % at round 2, 78 % at round 10, 87 % at round 20 and 98 % at round 40 on
the lattice (70, 87, 96 and 96 % on `all`). With the observed per-round witness share in place of the
convention, the simulated lattice mean is 0.24, 0.30, 0.44 and 0.64 at rounds 10, 20, 30 and 40,
against 0.28, 0.40, 0.59 and 0.74 observed and 0.39, 0.61, 0.83 and 0.94 under the convention. The
slow uptake by witnesses accounts for most of the gap between predicted and observed speed on the
lattice. The `all` tip lies outside both versions.

**To round 80.** Every lattice run was still rising at round 40. We continued the same eight
populations from their own round-40 state to round 80 (32,000 further calls; rounds 1–40 restored by
replaying each run's stored answers, which reproduced every stored cell state). The simulator was
re-run from each run's round-40 state with witness uptake measured in rounds 2–40 (in-hazard 0.23
per round on the lattice, 0.38 on `all`; out-hazard 0.02 and 0.03), and three predictions were
locked: at least three of four lattice runs reach mean x(70–80) ≥ 0.8 (K1, predicted probability
0.997); the two frozen `all` runs, r1 and r2, both stay below 0.5 (K2, 0.978); the lattice mean
exceeds the `all` mean (K3).

| run | x(40) | predicted median x(70–80) | observed x(70–80) | x(80) | first round with x ≥ 0.9 |
|---|---:|---:|---:|---:|---:|
| lattice r1 | 0.67 | 0.93 | 0.725 | 0.71 | 67 |
| lattice r2 | 0.53 | 0.93 | 0.765 | 0.78 | — |
| lattice r3 | 0.81 | 0.93 | 0.854 | 0.88 | 52 |
| lattice r4 | 0.96 | 0.93 | 0.845 | 0.77 | 38 |
| `all` r1 | 0.24 | 0.31 | 0.852 | 0.87 | 74 |
| `all` r2 | 0.36 | 0.31 | 0.861 | 0.88 | 47 |
| `all` r3 | 0.92 | 0.95 | 0.897 | 0.93 | 23 |
| `all` r4 | 0.52 | 0.93 (bimodal) | 0.875 | 0.87 | 46 |

All three predictions fail. Two of four lattice runs reach 0.8 (K1 fails). Both frozen `all` runs
tipped: r2 crossed x = 0.5 at round 41 and r1 at round 69, each after more than 20 rounds near
0.3 (K2 fails). The `all` mean is higher, 0.871 against 0.797 (K3 fails; exact permutation p for
lattice > `all` is 0.986). At rounds 70 and 80 the lattice P_e region is one Moore-connected
cluster in every run (lattice r2 had two in 12 of rounds 51–67), but its size moves: lattice r4 fell from 96 cells at round 40 to
77 at round 80, and lattice r1 from 87 at round 60 to 71.

*Post hoc: what sets the level.* The witnesses are not the limit: from round 40 on, 80–100 % of them
hold P_e in every run. Class A is. Per round, a class-A cell holding P_e leaves it with probability
about 0.10 when 5 of its 8 lattice neighbours publish P_e, 0.05–0.07 when 7 or 8 do, and 0.09–0.11
on `all` when 60–89 of its inbox lines name P_e. A class-A cell off P_e takes it up with probability
0.55–0.83 at those inboxes on the lattice and 0.51–0.64 on `all`. These hazards are about the same in
rounds 2–40 and 41–80, so the cells did not change; the populations reached a level the agents keep
churning around. On `all`, an in-hazard near 0.6 and an out-hazard near 0.1 put class A at about
0.86 and x at about 0.89, which is where the four `all` runs sit. On the lattice, cells next to
cells off P_e see fewer P_e lines and leave more often (out-hazard 0.17–0.33 at 3–4 P_e
neighbours), so a pocket off P_e can grow from a few cells: lattice r4 went from 4 cells off P_e at
rounds 40 and 50 to 19 at round 60. The pockets are not fixed places. In rounds 60–80, 63–73
different class-A cells were off P_e at some round, and only one cell in lattice r1, none in r3 and
r4, and 14 in lattice r2 were off P_e in at least 15 of those 21 rounds. The dips are such pockets, not a
shared shock: lattice r1 fell from 0.82 to 0.60 over rounds 72–75 as one region off P_e grew from 7 to
38 cells, its border cells leaving with 1–6 P_e neighbours. Given each cell's own inbox, the number
of cells leaving P_e per round is what independent cells would give (dispersion index 1.02 over the
160 lattice rounds 41–80; 95th percentile under binomial noise 1.20); one round lies far out
(lattice r3, round 73: 15 left where 6.4 were expected).

*Post hoc: how the level moves.* The two topologies differ in how x moves at its late level as
much as in the level itself. After the plateau, x on `all` jitters: SD 2.1–4.0 points per run,
the worst three-round fall 6–8 points, and lag-1 autocorrelation 0.25–0.38 in the three runs that
had stopped rising (0.74 in `all` r4, which was still rising in rounds 50–63). A fall is undone
the next round, because every cell reads the same inbox and the same rates pull it back. On the
lattice, over rounds 50–80, SD is 4.8–10.1 points, the worst three-round fall 10–22 points, and
lag-1 autocorrelation 0.79–0.92: a fall builds over several rounds and lasts for about ten, the
time a region off P_e takes to grow and close. One consequence is that a lattice run's mean over
an eleven-round window depends on where in such a wave the window falls; lattice r1's window
(0.725) contains the dip of rounds 73–80.

*Post hoc: how the frozen `all` runs escaped.* Neither escape followed a fall in what the prefix's
holders published: in both runs they published in about 85 % of cell-rounds before and during the
transition, as did P_e holders. Both runs drifted, with the share of class A on P_e moving between
0 and about a third.
`all` r2 rose to x = 0.48 at round 35, fell back to 0.29, and tipped at round 41. `all` r1 crept
from 0.28 at round 58 to 0.53 at round 69. Once P_e reached about half of the inbox lines, the
remaining class-A cells followed within five rounds. This is the escape the pre-stated reading of a
K2 failure names: on the complete graph, the graded responder's witness plateau is not absorbing
over 80 rounds.

**What the 120b runs show.** The topology ranking of the graded held-out model is a statement about
a window, not about the long run. Up to round 40 the lattice led, as predicted. By rounds 70–80 both
topologies were near the same level, set by class-A churn, and every `all` run ended above 0.85.
*Post hoc: where the simulator went wrong.* We applied the record's class-A fits (logistic in k
and m on the lattice, in the P_e share of the inbox on `all`; `sim_inputs.json`, sha256
`a6771107…`) to every class-A cell-round of the population, with the inbox each cell actually saw.
In the middle of the range the fits are calibrated: on the lattice, adoption at 2–5 P_e neighbours
is 0.05–0.55 observed against 0.04–0.58 fitted, and abandonment at 3–5 is 0.10–0.48 against
0.09–0.41. They fail at the top. With 7 or 8 P_e neighbours the fitted abandonment is 0.01–0.03;
the population abandons at 0.05–0.07. On `all`, with 80–100 % of the inbox naming P_e, the fit gives
0.03–0.05 and the population 0.09–0.11; over rounds 41–80 the `all` cells left P_e 1,011 times
where the fits expected 620. Adoption at the top is also lower than fitted (0.74 against 0.90 at 7
lattice neighbours). A logistic fit to the battery sends abandonment to zero as the inbox fills; the
agents keep a floor of about one exit in ten. With the fitted rates at a 90 % share (adopt 0.68,
abandon 0.04) class A settles near 0.94 and x near 0.95, the simulator's prediction; with the
observed rates (0.63, 0.11) it settles near 0.85 and x near 0.89, the observed level. Near the
switching point on `all` (share 0.5–0.6) the population adopted more often than fitted in rounds
41–80 (0.41 against 0.20, 138 cell-rounds), which is where both frozen runs crossed.

[Figure 3: bistability and the first speaker; spec in `PAPER_FIGURES_SPEC.md`. Figure 2 (slope graph of Table 3 and B1) goes at the end of 5.2.]

## 6. Discussion

**Collective computation with one-pass agents.** In this world a population reaches a rule that
75 % of its members cannot distinguish from a false one, but not by voting on evidence. It gets
there, when it does, through the way agents respond to the names they see. The same response that
reaches P_e on the lattice holds the population at the witness plateau on the complete graph.

**The agent is described by curves, not by a score.** Luna checks rules more accurately than
gpt-oss-20b, and loses to it on the complete graph. The difference is the shape of the response,
not competence. A model's position on single-agent benchmarks does not predict what a population
of it will do; its response functions do, at least for the ranking.

**Topology sets the dynamics, not only the level.** For gpt-oss-120b both topologies end near the
answer, but in different ways. On the complete graph a departure from the level is corrected
within a round. On the lattice, departures are local regions off the answer that grow and close
over about ten rounds, so the population spends long stretches well below its level (Section 5.5).
A designer who needs the population near the answer at every round, not on average, has a reason
to prefer global reading for a graded responder.

**The stubborn response is not a direction we found.** Because Qwen's weights are open, we looked
for a direction in its residual stream that carries the decision to adopt a neighbour's rule
(`AMENDMENT_WITNESS_DIRECTION.md`, locked). A probe on the last prompt token, cross-fitted by cell,
reads little beyond the inbox itself: within one condition, its out-of-fold AUC is 0.634 (one-sided
95 % lower bound 0.493). Adding the mean adopter-minus-non-adopter direction at 16 standard deviations
did not raise adoption: it lowered it slightly, from 0.154 to 0.120 (−0.033 paired, one-sided upper
bound −0.006). A random direction and the direction of "more P_e lines seen" moved it less (0.135 and
0.143), and the opposite dose did not lower it beyond noise. The decision of a reasoning model is
probably made during its reasoning, not at the end of the prompt. Where it forms is open.

**Asking Qwen to check does not move it either.** A prompt-level intervention fails in the same way
(`AMENDMENT_QWEN_CHECK_NUDGE.md`, locked). On 400 adopt prompts from the battery's lattice and S88
conditions, we inserted one sentence before the decision: "Before you answer, check each rule named
in the visible messages against your private examples." Adoption was 0.110, against 0.145 with no
sentence and 0.160 with a placebo sentence of the same length that asks the model to reread
everything slowly (differences −0.035 [−0.088, +0.015] and −0.050 [−0.103, +0.003], 98.33 %
cell-bootstrap intervals). The check itself did happen: the share of reasoning traces stating that
both rules fit the cell's example rose from 0.40 to 0.61 (+0.21 [+0.12, +0.31]). Reasoning did not
get longer, and a decoy rule that fits no example was adopted in 0 of 40 prompts in every arm. So
the barrier is not a missing check. Post hoc, a "both fit" statement that names the neighbours' rule
was followed by adoption about half as often under the sentence as without it (0.16 against 0.33).
Qwen seems to stop at choosing between two rules that both fit its example, not at establishing
that they do. This last reading rests on pattern-matched traces and was not registered.

**Protocol levers.** Three follow from the theory and the experiments: who publishes first (5.4);
silence of the majority rule's holders (Lemma 1, Proposition 2); and matching the topology to the
response class (5.2). All three can be set by a system designer without changing the agents.

## 7. Limitations

- One task family and three worlds, all with a true rule equal to a prefix plus one swap. The
  world-1 swap (2,3) is the one Luna checks worst (Section 4).
- Population results rest on two runs per arm, except the Luna `all` tipping (20) and
  first-speaker (16) experiments, gpt-oss-20b in world 1 (eight runs per topology, the six new ones
  as the locked test) and gpt-oss-120b (four 80-round runs per topology). With four
  runs against four the smallest one-sided permutation p is 0.014; the 120b ranking on rounds
  30–40 has p = 0.20, and on rounds 70–80 it reversed.
- gpt-oss-20b (worlds 1, 3 and 5) and Qwen were run for 20 rounds. The gpt-oss-120b continuation
  shows that a ranking in a 20- or 40-round window need not hold later; continuations of the other
  local models to round 80 are [PENDING].
- The simulator's witness convention (all witnesses on P_e from round 2) is faster than the
  populations; it is adequate for the sign, not for the speed.
- The models are not sampled at a common temperature (Section 2, Models). Qwen runs at 0.6 and the
  gpt-oss models at 1.0. Whether part of Qwen's stubborn response comes from its lower temperature is
  untested; a battery arm at temperature 1.0 is planned.
- The threshold case is one closed model, accessed through an API whose model can change. Run
  dates and the model string are recorded (Appendix D).
- The battery underestimates in-population adoption for graded responders; level predictions are
  not claimed.
- The first response batteries of gpt-oss-20b, Qwen and gpt-oss-120b stored only the parsed rule,
  not the model's text. Both gpt-oss batteries were run again in full with text stored: the parse
  agreed on all 2,960 calls of each, and the four measures moved by up to 0.13 between runs, within
  their paired intervals. Qwen's battery was checked by a partial rerun with text stored, in two
engine modes (Section 5.1): four of five measures reproduce, and E8 is reported pooled. Luna's battery and every population
  run stored the final text.
- Luna's published runs contain no truncated reply (counted directly in the battery, QX, stage 0
  and the lattice runs; inferred from complete caches elsewhere). Two runs were interrupted and
  resumed (tipping r7 round 1; lattice r2 round 11), and a truncated reply in the lost fragment,
  at most about 100 calls each, would have been re-called without a record.
- The F0/F1 construction shows cells a memory line that may differ from what they did in round 1.
  This is the manipulation and is stated as such.
- gpt-oss-20b runs used a chat template that inserts the current date. A paired check on 400
  battery calls, default template against a pinned date (the default arm run a second time, with
  output stored), gave adoption 0.2225 and 0.2300 (difference +0.008, 95 % CI [−0.038, +0.048],
  exact two-sided p = 0.83; 0 truncations). We see no date effect at this resolution. The check
  used the battery's configuration (context 36,864; population runs used 40,960, with no truncation
  in either). The second 20b battery ran on a later live date and replicated the first. The six
  new 20b population runs per topology rendered 2026-11-03 or 2026-11-04 (one run crossed midnight).
  Of their 24,000 calls, one returned an empty final text after spending its budget on reasoning;
  it was re-called once with the same prompt plus one fixed sentence asking for valid JSON (the
  runner's retry rule), and both calls are stored. gpt-oss-120b
  ran every call with the date pinned; O3 therefore compares pinned 120b with live-date 20b.

## 8. Related work

**Thresholds and contagion.** Threshold models of collective behaviour [Granovetter 1978] and
cascades on networks [Watts 2002] describe how an individual adoption rule produces a population
outcome. Centola and Macy [2007] distinguish simple contagion, which spreads fastest with long
ties, from complex contagion, which needs reinforcement from several contacts and spreads better
in clustered networks; Centola [2010] confirmed the clustering advantage for behaviour in an online
experiment. Our response classes map onto this distinction, with one difference that matters on the
lattice: an empty slot is neither support nor opposition, so a threshold responder in a sparse
inbox behaves like a simple-contagion agent (Section 5.2). We measure the adoption rule of each
agent directly instead of assuming it.

**Opinion dynamics and social learning.** Voter and majority models on graphs [Castellano,
Fortunato and Loreto 2009], information cascades [Bikhchandani, Hirshleifer and Welch 1992] and
naive learning on networks [Golub and Jackson 2010] study when a population converges and whether
it converges to the truth. Work on the communication structure of epistemic communities [Zollman
2007] and simulations of organisational problem solving [Lazer and Friedman 2007] found that less
connected groups can do better in the long run, at a cost in the short run, because they keep
alternatives alive longer. Mallick, Thomo and Saxena [2026] survey language-model agents in models
of opinion dynamics, information diffusion and rumour spreading. Networks of language-model agents
converge to a consensus that matches the facts unless confirmation bias is induced by the prompt
[Chuang et al. 2024]; in our world the population starts from a simpler false rule and the facts
are held by a minority. Our lattice result for the threshold model has the same
direction; the graded model reverses it, so the advantage of sparse connection depends on the
agent's response, not on the network alone.

**Aggregation with shared errors.** The Condorcet jury theorem was stated for independent votes;
correlation weakens the gain from more voters but under fairly general conditions does not remove
it [Ladha 1992]. Language models of different developers make the same mistakes more often than
independence predicts [Kim et al. 2025], and swarms of agents built on one model make the same
choices, and the same mistakes [Anthropic Frontier Red Team 2026]. The failure in Proposition 5 is different in kind: a
shared bias, not correlation. Every voter checks with the same agent, the error depends on the
complexity of the rule being checked, and it favours the simpler false rule; independent voters
with the same bias would not remove it either. Chang and Zhang [2026] prove the general form for
agents that screen items through a shared representation: every aggregation rule keeps an error
floor at any number of agents, no statistic of the agents' outputs tells a right consensus from a
wrong one, and only judgments of items outside the consensus pin the error down. In our populations
the witnesses hold such evidence: their examples rule out the prefix. Whether the population uses
it is set by the response function (Section 5).

**Distributed information.** In HiddenBench [Li, Naito and Shirado 2026], groups of language-model
agents split the evidence for a decision; they reach 30 % where one agent with all the evidence
reaches 81 %, because agents converge on shared evidence and do not surface what only they hold.
On a hidden-profile task, groups of one frontier model reach about 85 % and groups of other models
17–36 % [Anthropic Frontier Red Team 2026], so the failure depends on the model as well as on the
protocol.
Our agents cannot share evidence at all, only rule names, and each one's evidence fits several
rules; the population has to reach the answer through how agents respond to the names they see.

**Multi-agent debate.** Debate between language-model agents has been reported to improve
reasoning and factuality [Du et al. 2024]. Later analyses find that much of the gain comes from
majority voting over answers rather than from the exchange [Choi, Zhu and Li 2025], and that
debate can converge to a shared wrong answer [Estornell and Liu 2024]. Our setting differs in that
the truth is held by a quarter of the agents and is locally verifiable by them only; debate
corresponds to the complete graph, and Section 5 shows that its outcome depends on the response
class of the agents and on who speaks first.

**Populations of language-model agents.** Populations of language-model agents form shared
conventions and collective biases that no single agent holds, and a committed minority can
overturn an established convention [Ashery, Aiello and Baronchelli 2025]. Our witnesses are such a
minority with evidence on their side; whether they prevail is decided by the majority's response
rule and by publication order. Okawa [2026] models debate among language-model agents with a spin
model from social dynamics: a biased consensus appears as a phase transition once conformity passes
a critical value set by the agents' initial bias and the sampling noise, and finite populations and
heterogeneous agents round the transition into a crossover. In that model topology enters only
through the number of observed neighbours, so it predicts that a well-mixed graph with eight
observed senders behaves like the lattice; a control of this kind is planned. The bistability of our threshold model
on the complete graph resembles this. Two things differ. Here a correct answer exists, it is spread
over a quarter of the agents and only they can check it; and the agents' update rule is not a
fitted conformity parameter but is measured in a battery outside the population and used to
predict the population before it is run.

**Cellular automata with language-model cells.** LOGOS-CA [Utimula 2026] and the LLMCA project
[pinsky-three, GitHub] use natural-language state and language-model updates in cellular
automata. Burtsev [2024] studies the inverse problem of learning elementary automaton rules with
transformers. Our cells solve a forward inference task from distributed evidence, and the
automaton is the measurement device rather than the object of study.

**Sheaf formulation.** Topological Sheaves of Irreducibility [Motta, Mambelli and Rozza 2026]
separate task-level obstructions to multi-agent solution from agent capability, using cohomology
of a capacity sheaf on the interaction complex. Theorem 1 concerns global sections only: our task
has a global solution, so every failure we observe is on the capability side. For cellular sheaves in
general see Hansen and Ghrist [2019].

### References (to format)

- Anthropic Frontier Red Team (2026). Patterns and problems in emerging multiagent systems.
  Anthropic research report, 13 August 2026. https://www.anthropic.com/research/multiagent-systems.
- Ashery, A. F., Aiello, L. M., Baronchelli, A. (2025). Emergent social conventions and collective
  bias in LLM populations. *Science Advances* 11(20), eadu9368. doi:10.1126/sciadv.adu9368.
- Bikhchandani, S., Hirshleifer, D., Welch, I. (1992). A theory of fads, fashion, custom, and
  cultural change as informational cascades. *Journal of Political Economy* 100(5), 992–1026.
- Burtsev, M. (2024). Learning elementary cellular automata with transformers. arXiv:2412.01417.
- Castellano, C., Fortunato, S., Loreto, V. (2009). Statistical physics of social dynamics.
  *Reviews of Modern Physics* 81(2), 591–646.
- Centola, D. (2010). The spread of behavior in an online social network experiment. *Science*
  329(5996), 1194–1197.
- Centola, D., Macy, M. (2007). Complex contagions and the weakness of long ties. *American Journal
  of Sociology* 113(3), 702–734.
- Chang, B., Zhang, D. (2026). Multi-agent screening: what agreement and acceptance cannot tell you.
  arXiv:2611.12705.
- Chuang, Y.-S., Goyal, A., Harlalka, N., Suresh, S., Hawkins, R., Yang, S., Shah, D., Hu, J.,
  Rogers, T. T. (2024). Simulating opinion dynamics with networks of LLM-based agents. *Findings of
  NAACL 2024*. arXiv:2311.09618.
- Choi, H. K., Zhu, X., Li, S. (2025). Debate or vote: Which yields better decisions in multi-agent
  large language models? NeurIPS 2025. arXiv:2508.17536.
- Du, Y., Li, S., Torralba, A., Tenenbaum, J. B., Mordatch, I. (2024). Improving factuality and
  reasoning in language models through multiagent debate. ICML 2024, PMLR 235, 11733–11763.
- Estornell, A., Liu, Y. (2024). Multi-LLM debate: Framework, principals, and interventions.
  NeurIPS 2024 (Advances in Neural Information Processing Systems 37), 28938–28964.
- Golub, B., Jackson, M. O. (2010). Naïve learning in social networks and the wisdom of crowds.
  *American Economic Journal: Microeconomics* 2(1), 112–149.
- Granovetter, M. (1978). Threshold models of collective behavior. *American Journal of Sociology*
  83(6), 1420–1443.
- Hansen, J., Ghrist, R. (2019). Toward a spectral theory of cellular sheaves. *Journal of Applied
  and Computational Topology* 3(4), 315–358.
- Kim, E. M., Garg, A., Peng, K., Garg, N. (2025). Correlated errors in large language models.
  ICML 2025, PMLR 267, 30038–30066.
- Li, Y., Naito, A., Shirado, H. (2026). Systematic failures in collective reasoning under
  distributed information in multi-agent LLMs. ICML 2026, PMLR 306, 69250–69268. arXiv:2505.11556.
- Ladha, K. K. (1992). The Condorcet jury theorem, free speech, and correlated votes. *American
  Journal of Political Science* 36(3), 617–634.
- Lazer, D., Friedman, A. (2007). The network structure of exploration and exploitation.
  *Administrative Science Quarterly* 52(4), 667–694.
- Mallick, S., Thomo, A., Saxena, A. (2026). LLMs for social network modeling: From network
  generation to dynamic processes. arXiv:2609.08049.
- Motta, S., Mambelli, D., Rozza, A. (2026). Topological sheaves of irreducibility: A theoretical
  framework for multi-agent task obstructions. arXiv:2610.26777.
- Okawa, M. (2026). Emergence of biased consensus in multi-agent LLM debates. *Proceedings of the
  43rd International Conference on Machine Learning*, PMLR 306, 94505–94527.
- pinsky-three. LLMCA: Language Model Cellular Automata. GitHub repository,
  github.com/pinsky-three/llmca [access date].
- Utimula, K. (2026). LOGOS-CA: A cellular automaton using natural language as state and rule.
  arXiv:2602.00036.
- Watts, D. J. (2002). A simple model of global cascades on random networks. *PNAS* 99(9),
  5766–5771.
- Zollman, K. J. S. (2007). The communication structure of epistemic communities. *Philosophy of
  Science* 74(5), 574–587.
- [Earlier report: "What None of Them Knew", luna_life site, 2026 — cite with URL.]

## 9. Conclusion

[3–4 sentences, written last.]

## Appendix

- A. Proofs (Propositions 3, 4, Lemma 1) and the heterogeneous mean field for the lattice.
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
| D | decision class per arm by Δ vs bound (class not predicted; medium is the reasoning reference) | same | result: D-none for the two one-pass arms; medium also below both cuts |
| A1–A4 | Luna vs gpt-oss-20b response contrasts | `AMENDMENT_CONTAGION.md` | hold |
| B1 | simulated ranking sign = observed, Luna and gpt-oss-20b | same | holds |
| B1-Qwen | scored after the Moore runs | same | holds (simulated gap +0.009, bands overlap) |
| C1, C2 | gpt-oss-20b `all` > 0.5 and > lattice, worlds 3 and 5, both runs | same; `AMENDMENT_CONTAGION_PARTC_RUN.md` | world 3: both hold (0.843, 0.844 vs 0.311, 0.321); world 5: both fail (0.030, 0.049 vs 0.260, 0.142) |
| T1, T2, T3 | Luna `all` tips sometimes, not often; frozen level | `AMENDMENT_LUNA_ALL_TIPPING.md` | T1, T2 hold; T3 fails |
| F-T1–F-T3 | constructed first speakers set the outcome | `AMENDMENT_LUNA_FIRST_SPEAKER.md` | hold |
| O1 | gpt-oss-120b ranking, rounds 10–20 (record: lattice > `all`) | `AMENDMENT_OSS120_PREDICTION.md`, `AMENDMENT_REPLICATES.md` | holds (gap +0.016) |
| O2 | each 120b run inside its simulated 5–95 % band | same | fails (5 of 8 outside) |
| O3 | gpt-oss-120b S88 and E8 inside 20b's intervals, outside Luna's | `AMENDMENT_OSS120_PREDICTION.md` | holds |
| E1 | gpt-oss-120b, rounds 30–40: lattice > `all` | `AMENDMENT_OSS120_EXTEND40.md` | holds (gap +0.139; permutation p 0.20) |
| E2 | fewer P_e components at round 20 than 5, ≥ 3 of 4 lattice runs | same | holds (3 of 4) |
| E3 | runs with x(30–40) ≥ 0.8 (descriptive) | same | lattice 1 of 4 (predicted 0.84 per run); `all` 1 of 4 (0.08) |
| K1 | gpt-oss-120b, ≥ 3 of 4 lattice runs with x(70–80) ≥ 0.8 (P = 0.997) | `AMENDMENT_OSS120_CONTINUE80.md` | fails (2 of 4: 0.725, 0.765, 0.854, 0.845) |
| K2 | `all` r1 and r2 both x(70–80) < 0.5 (P = 0.978) | same | fails (0.852, 0.861) |
| K3 | mean x(70–80) lattice > `all` | same | fails (0.797 vs 0.871; permutation p 0.986) |
| K4 | x(80), first round x ≥ 0.9, P_e components, witness share (descriptive) | same | §5.5 table; lattice one P_e cluster at rounds 70 and 80 in all runs; witnesses 80–100 % from round 40 |
| R1 (replicates) | gpt-oss-20b, 6 new runs per topology: `all` > lattice, x(10–20), exact permutation α = 0.05 | `AMENDMENT_REPLICATES.md` | holds (gap +0.361, p = 1/924); R2 36/36 pairs; R3 11/12 inside band |
| R1–R3 (text) | battery rerun with text: parse agrees; measures replicate; locked verdicts on the rerun | `AMENDMENT_PARTA_TEXT_REPLICATION.md` | 120b and 20b: R1 and R2 hold; R3 for 20b: B1 sign kept with rerun fits, A1–A4 on the rerun [PENDING]; Qwen: replaced by the reproducibility check (next row) |
| QR | Qwen battery reproduces on its own configuration (standard) and in deterministic mode: all five measures, 99 % per measure | `AMENDMENT_QWEN_PARTA_REPRO.md` | fails in both arms on E8 only (+0.083 [+0.008, +0.167]; +0.067 [+0.008, +0.142]); lattice, S88, M88, R88 reproduce |
| P1 | Qwen: a linear direction for adoption at the last prompt token (within-condition AUC, lower bound > 0.5) | `AMENDMENT_WITNESS_DIRECTION.md` | fails (0.634, lower bound 0.493) |
| N1–N3 | Qwen: a sentence asking to check each named rule raises adoption over no sentence (N1) and over a placebo sentence (N2); it raises the "both fit" statement in traces (N3); 98.33 % cell bootstrap | `AMENDMENT_QWEN_CHECK_NUDGE.md` | N1 fails (−0.035 [−0.088, +0.015]); N2 fails (−0.050 [−0.103, +0.003]); N3 holds (+0.210 [+0.116, +0.305]); fidelity gate passes; decoy 0/40 in every arm |
| D1–D3 | steering along it raises (+) or lowers (−) adoption, more than random and k directions, without hurting own-example fit | same | fail: D1+ −0.033 (opposite sign), D1− −0.015 (upper +0.017), D2 −0.015 and −0.022; D3 −0.125 |