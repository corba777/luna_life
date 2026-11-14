# AMENDMENT — QX-2 phase 1: world, prompt, protocol and scripted references

**Status:** locked 2026-11-13 (Artem). This lock covers the world, catalog, prompt, schema, mapper,
protocol, simulator and reference values below. No model call was made under phase 1. The pilot
(phase 2) gets its own amendment; no call is made before that one is locked. Plan: `QX2_PLAN.md`.

**Lock record:**

- dry build `runs/qx2/dry_build.json` sha256 `981d340555267e64a580823b50cb6ef6250c2c27a607abd76a35f3e9a18ed50d`
- world digest `5151bc57d9bbf6081d470bfa2e7f6f5a7fc67851c70c1d58c8a48bc95031250f`

| file | sha256 |
|---|---|
| `runs/qx2_world.py` | `ebe9982f82b11c7a90d8229d05f2e49f7855d41c81c27743b943039f508075b9` |
| `runs/qx2_sim.py` | `89645df1f25ba7ed6255e483ae75e56d2447fab136e4cd4cf18901af8f29449a` |
| `runs/qx2_dry_build.py` | `ff71204c3d6d1ab0ee3c368715a2874d4b3df5053636b2e44d778d8564fa8133` |
| `runs/qx2/world.json` | `8c76ba911198ed138a59aa76c682e08daa5a81e6b14bfaacb958748aea52965d` |
| `runs/qx2/world_checks.json` | `e8d67cc1747106c0db3112e13491eab5d86996176336914f8cf525b4233abdfb` |
| `runs/qx2/sim_reference.json` | `8289693c7a8929acd18e94a2b9753f804cc3073d6fab18da5a2a48278ee67e9a` |
| `runs/qx2/readout.md` | `d48b16e2517440987ebcebfb8d1424dae0d467b1d8d183da171150aafa0ce915` |

**Decisions (Artem, 2026-11-13):**

- primary outcomes are abandonment and recovery;
- relay of received results is allowed;
- two single-agent baselines;
- shortest-rule agents, with "shortest" as defined in §5;
- a sixth agent that relays any result;
- δ = 1/64 is the main cell, δ = 1/8 the control;
- hash-drawn generation-0 signals;
- the glossary is kept;
- one retry, then keep the previous rule;
- the 100 base rules are in the catalog;
- no test field in generation 12;
- 9 / 17 / 34 tests per pooled single-agent call.

## 1. World

- **False rule.** $H_F$ = `shift_symbols(1)` (key K026).
- **True rule.** $H_T$ = $H_F$ followed by a subst, read on the output of $H_F$:
  - δ = 1/64 (**main**): `subst_if(p,X,Y,q,Z)`, which applies only when position q holds Z;
  - δ = 1/8 (**control**): `subst(p,X,Y)`, unconditional.
- Positions are 0-based from the left.

**Catalog: 117 rules, the same for both δ.**

- The 101 Life base rules (one-step and two-step compositions of reverse, rotate, `shift_symbols`
  and swap). $H_F$ is one of them.
- Four subst clusters, one anchored at each position k, each with the same shape:

| member | rule | differs from $H_F$ on |
|---|---|---|
| U_k | `H_F;subst(p_k,X_k,Y_k)` | 1/8 |
| C_k | `H_F;subst_if(p_k,X_k,Y_k,q_k,Z_k)` | 1/64 |
| Da_k | `H_F;subst(p_k,X_k,Y_k);subst(r_k,A_k,V_k)` | U_k plus one more symbol at r_k |
| Db_k | `H_F;subst(p_k,X_k,Y_k);subst(r_k,B_k,W_k)` | the same position r_k, another symbol |

- $H_T$ = U_t or C_t of one randomly drawn cluster t. The four Y_k are distinct.
- Keys K001–K117 come from a seeded permutation. Catalog order is shuffled per cell and generation.

**Ambiguity after a refutation.** Every counterexample is still fitted by at least one other subst
rule:

- C_t → U_t always fits;
- U_t → Da_t or Db_t fits.

So finding $H_T$ takes more tests or messages.

**Examples.**

- Two per cell, drawn from the inputs on which all 17 subst-family rules agree (625 of 4,096). These
  inputs are also where $H_T$ and $H_F$ agree.
- No input is repeated within a cell.

**Base rules left by the examples.**

- In 91 cells the two examples leave no base rule consistent besides $H_F$.
- In 9 cells they leave exactly one. It is one of `shift_symbols(1);swap(i,j)` for (i,j) = (0,1),
  (0,3), (1,3) or (2,3).
- None of these fits any counterexample.

**World seed 0, exhaustive checks** (all 4,096 inputs):

| check | δ = 1/64 (main) | δ = 1/8 (control) |
|---|---|---|
| $H_T$ | `shift_symbols(1);subst_if(0,E,F,1,H)` (K014) | `shift_symbols(1);subst(0,E,F)` (K047) |
| disagreement with $H_F$ | 64/4096 exactly | 512/4096 exactly |
| examples agree with $H_T$ and $H_F$ | yes | yes |
| rules fitting a cell's examples and one counterexample | min 3, max 4 | min 2, max 4 |
| base rules among them | 0 | 0 |

Also checked:

- 117 distinct functions;
- 15 subst variants besides $H_F$ and $H_T$, inside the 8–16 range;
- every subst rule fits every cell's examples;
- 200 examples, distinct within their cell.

## 2. Protocol

- **Population and run.** 100 cells on the 10×10 torus. Each cell's 8 Moore neighbours fill its 8
  message slots. G = 12 generations. Budgets B ∈ {1, 2, 4}, plus a B = 0 no-test control.
- **Generation 0 (constructed).** Every cell holds $H_F$ and publishes it. Each sender's signal is
  `sha256("qx2-seed-signal-{seed}-{cell}") mod 8`, uniform on 0–7 and listed in `world.json`.
- **Each generation g = 1…12:**
  1. Results of tests requested at g−1 arrive; only the requesting cell sees them.
  2. Messages published at g−1 become visible.
  3. The cell names a rule.
  4. It may request one test while its budget lasts and g < 12. Generation 12 has no test field,
     because the result could never arrive.
  5. It publishes or stays silent.
- **Messages and relay.**
  - A message carries a signal 0–7 and either the key of the rule held or one result from the cell's
    memory, own or received.
  - Received results go to their own memory block, "Results shared with you", with lines
    `generation g, from cell n: x -> y`. They are not marked as claims.
- **No result can be invented** (checked in the dry build on every sample schema):
  - A shared result is chosen **by input only**, from an `enum` that equals the cell's memory
    (own ∪ received).
  - The schema has **no output field**. The engine fills the output from memory.
  - A cell with empty memory has no result option at all.
  - The mapper rejects any input outside memory.
  - Every result in memory is a true output of $H_T$, so every shared or relayed result is true.
- **Memory.** The cell's previous rule and whether it published, all its own results, and all results
  shared with it.
- **Invalid answer.**
  1. One re-sample of the same prompt (draw + 1), as in the stored Life runs.
  2. If that is invalid too, the cell keeps its previous rule, uses no test and publishes nothing.
  3. Both attempts are logged; the fallback rate is reported per arm.
- **Single-agent baselines.** One agent with cell 0's two examples and no messages. No tests in
  generation 12. Two versions:
  - **pooled:** 100·B tests, at most ⌈100·B/12⌉ = 9 / 17 / 34 per generation. The upper bound for
    perfect central pooling.
  - **cell:** one cell's budget B, at most one per generation.

## 3. Prompt, schema, mapper

- **Samples.** `runs/qx2/prompts/`, with strict schemas:
  - generation 1 for each B;
  - generation 3 with only a received result;
  - generation 5 with own and received results;
  - budget spent;
  - generation 12;
  - single-agent pooled and cell for each B, and pooled generation 12.
- **Text.** Neutral:
  - tests are available, with budget B, at most one per generation;
  - a result arrives next generation and only the requesting cell sees it;
  - the cell keeps its own and its received results;
  - a message may carry the held rule's key or a result the cell has.
  
  Nothing says the current rule is wrong; a word check finds none. The glossary defines positions 0–3
  from the left, `;` composition, `shift_symbols`, `subst` and `subst_if`. All 117 keys are in every
  prompt.
- **Mapper stub: all cases pass.**
  - own result: valid;
  - relayed received result: valid, output equals the received one;
  - input not in memory: invalid;
  - unknown key: invalid;
  - bad test string: invalid;
  - not JSON: invalid;
  - invalid then valid: accepted on attempt 2;
  - invalid twice: previous rule, no test, no publish;
  - generation 12: no test field is valid; a test field, even null, is invalid.
- **Prompt length.** User message only, before the chat template:

| | gpt-oss-20b | Qwen3-4B-Thinking |
|---|---:|---:|
| catalog block, 117 rules | 1,544 | 1,778 |
| cell prompt, generation 1, B = 1 | 2,204 | 2,473 |
| cell prompt, generation 12 (3 results in memory) | 2,221 | — |
| single-agent prompt, generation 1 | about 1,890 | about 2,135 |

  Memory lines add about 12 tokens each.

## 4. Outcomes

- **Primary:**
  - **abandonment:** the share of cells not holding $H_F$ at g = 12;
  - **recovery:** the share holding $H_T$ at g = 12.
- **Main measure.** The gap between abandonment and recovery under relay, compared with the scripted
  references and the pooled single-agent baseline (§5).
- **Descriptive:**
  - **first refutation:** informative only at δ = 1/64; at δ = 1/8 it is always generation 2.
  - accuracy of each cell's final rule, on all inputs and on δ-inputs;
  - test quality: the share of tests on δ-inputs; the random baseline is δ;
  - overturn within k = 2 generations of receiving a counterexample, own or shared;
  - explained away;
  - fallback rate;
  - share of published results that are relayed, and that refute $H_F$.

## 5. Scripted references (locked values)

**Agents.** Every cell of a population runs the same agent. A cell starts with the rules its two
examples leave consistent, switches only when the current rule stops fitting its evidence, and never
tests in generation 12.

- **random:** tests uniform inputs, switches to a uniformly random consistent rule, publishes its
  rule, ignores messages.
- **perfect:** like random, but each test is an input on which its current rule and $H_T$ disagree
  (oracle).
- **never_revise:** tests like random and always holds $H_F$.
- **shortest:** like random, but switches to the shortest consistent rule: fewest operations, then
  fewest characters, ties uniform. `subst_if` is one operation.
- **adopt_shared:** like random, but it treats every shared result as its own evidence and keeps it in
  memory. It publishes the latest result in memory that refutes $H_F$, own or received.
- **adopt_shortest:** adopt_shared with the shortest-rule switch.
- **relay_any:** like adopt_shared, but it publishes its most recent result of any kind: uniformly
  one of this generation's arrivals, own or received, else its last one.

1,000 population replicates and 2,000 single-agent replicates per row. Means of abandonment /
recovery. Monte Carlo SE ≈ 0.013 on rows where a run either spreads or does not (e.g. adopt_shared at
B = 1). Quantiles are in `sim_reference.json`.

**δ = 1/64 (main)**

| B | random | perfect | shortest | adopt_shared | adopt_shortest | relay_any | single pooled | single cell |
|---:|---|---|---|---|---|---|---|---|
| 1 | 0.015 / 0.004 | 1.000 / 0.270 | 0.015 / 0.000 | 0.770 / 0.294 | 0.795 / 0.088 | 0.306 / 0.294 | 0.785 / 0.785 | 0.017 / 0.004 |
| 2 | 0.031 / 0.011 | 1.000 / 0.854 | 0.031 / 0.003 | 0.961 / 0.455 | 0.952 / 0.199 | 0.330 / 0.320 | 0.954 / 0.954 | 0.025 / 0.011 |
| 4 | 0.061 / 0.032 | 1.000 / 1.000 | 0.062 / 0.018 | 0.998 / 0.610 | 0.999 / 0.371 | 0.388 / 0.381 | 0.996 / 0.996 | 0.064 / 0.030 |

**δ = 1/8 (control)**

| B | random | perfect | shortest | adopt_shared | adopt_shortest | relay_any | single pooled | single cell |
|---:|---|---|---|---|---|---|---|---|
| 1 | 0.124 / 0.045 | 1.000 / 0.362 | 0.125 / 0.125 | 1.000 / 0.650 | 1.000 / 1.000 | 0.955 / 0.904 | 1.000 / 1.000 | 0.129 / 0.049 |
| 2 | 0.233 / 0.094 | 1.000 / 0.729 | 0.233 / 0.233 | 1.000 / 0.726 | 1.000 / 1.000 | 0.962 / 0.921 | 1.000 / 1.000 | 0.228 / 0.098 |
| 4 | 0.410 / 0.207 | 1.000 / 1.000 | 0.413 / 0.413 | 1.000 / 0.777 | 1.000 / 1.000 | 0.979 / 0.953 | 1.000 / 1.000 | 0.412 / 0.199 |

The single-agent columns are random testers. The no-test control never leaves $H_F$. Random test
quality equals δ (0.0155 and 0.124).

**Reading:**

1. **Relaying refutations closes the abandonment gap to central pooling, not the recovery gap.**
   At δ = 1/64, adopt_shared's abandonment is 0.77 / 0.96 / 1.00, about the same as pooled
   (0.79 / 0.95 / 1.00). Its recovery is only 0.29 / 0.46 / 0.61.
2. **Relaying any result trades abandonment for precision.** relay_any spreads fewer refutations:
   abandonment at δ = 1/64 is 0.31–0.39. But it spreads the results that separate U_t from C_t, so
   almost every cell that leaves $H_F$ lands on $H_T$.
   
   Neither scripted relay reaches pooled recovery. The room between them and the pooled baseline is
   what a model's choice of *which* result to share can fill.
3. **Simplicity separates the δ cells.**
   - δ = 1/8: adopt_shortest recovers 1.000 at every B.
   - δ = 1/64: the shortcut points to U_t. adopt_shortest recovers 0.09 / 0.20 / 0.37.

## 6. Cost lines for the phase-2 amendment (informational, not locked)

**gpt-oss-20b pilot time.**

- Basis: QX-1p on 20b (2026-10-28), 480 calls at concurrency 16 in 1,547 s, so **3.2 s per call**.
  Prompts averaged 1,856 tokens and completions 972 (median 809, p95 2,101).
- QX-2 prompts are 2,050–2,240 tokens at the start, growing about 12 tokens per memory line.
- Scaling by prompt + completion tokens: **3.6 s per call** central. Range 3.2–4.8 s, where the top
  covers late-generation prompts near 3,200 tokens or completions twice as long.
- The plan's 4.6 s was not a QX-2 measurement. With the measured basis, a population run (1,200
  calls) takes about **1.2 h** (1.1–1.6 h).
- Pilot as sketched in `QX2_PLAN.md` §6: 2 budgets × 2 replicates, a no-test control with
  2 replicates, and both single-agent baselines with 2 replicates each. Calls do not depend on δ.
  - About 7,300 calls (4,800 + 2,400 + 96), +5 % for retries.
  - **About 7.5 h** (6.5–10 h), below the plan's 12 h.

**Luna cost.**

- Basis: QX-1p Luna medium, $0.2185 for 480 calls = **$0.000455 per call**. That breaks down into a
  cached fixed prefix of 14,764 tokens ($0.000148), cache writes of 476 tokens ($0.000060) and
  400 output tokens ($0.000200).
- QX-2's per-cell prompt is not cacheable across calls, because the catalog order is shuffled. Billing
  its about 2,200 tokens at the cache-write rate ($0.125/M) adds $0.000275.
- Output is assumed 400–1,200 tokens.
- **$0.00062–0.00102 per call**:

| scope | calls | cost |
|---|---:|---:|
| one 1,200-call run | 1,200 | $0.75–1.23 |
| a pilot-sized Luna arm | about 7,300 | $4.5–7.5 |
| a full δ × B grid with 2 replicates + control | about 16,800 | $10.4–17.1 |

- The $100 envelope has $13.20 left ($86.80 spent). A pilot-sized arm fits. A full grid fits only at
  the low end.
- The estimate is re-done from the 20b pilot's measured QX-2 completion lengths before any Luna call
  (plan §7).

## Files

- `runs/qx2_world.py`, `runs/qx2_sim.py`, `runs/qx2_dry_build.py`.
- `runs/qx2/`: `world.json`, `world_checks.json`, `prompts/`, `sim_reference.json`, `readout.md`,
  `dry_build.json`, `build.log`.
