# Amendment — QX isolation battery, worlds 1–3 and condition U3 (sender names H_T)

**Status:** draft v2 (2026-11-24), written by the reviewer for Artem. v2 takes in the dry build of v1
(`runs/dry_build_qx_isolation_worlds_u3.md`, no model call): the cell lists, 260 distinct prompts (780 calls),
the world checks, U2/U3 differing in one token, and the consistent sets (equal in U2 and U3; four U0 cells
have one extra fitting rule, which does not matter because only *leave* is read in U0). Extends `AMENDMENT_QX_ISOLATION.md`
(v3, locked `efd8bef6…`) and its addendum `ADDENDUM_QX_ISOLATION_JOINT.md` (`143f823b…`); changes neither.
Locked after the agent's dry build (no model call) and the reviewer's review. No call before the lock and
Artem's go, logged with his words. Artem, 2026-11-24 01:20: «давай сделаем isolation на мирах и U3».

## Why

The world-0 battery (entry 16) gave three profiles: Luna and gpt-oss-120b update on their own
counterexample and less often on a received one; gpt-oss-20b updates on about half of either. Two limits
were stated with it:

1. **One world, one counterexample** (`DAAA -> FBBB`). In world 0 gpt-oss-20b's habitual test inputs are
   uninformative (entry 18), and whether it updates may depend on the input. Worlds 1–3 change H_T and
   the counterexample.
2. **In U2 the sender of the counterexample still names H_F.** U2 − U1 mixes the source with a sender that
   votes against its own evidence. In the populations, the rule named beside a received counterexample
   mattered for both models (entry 16, population table: Luna 267/451 to H_T when the sender named H_T,
   14/208 when it named U; gpt-oss-20b 129/237 against 25/113). U3 holds everything of U2 fixed except that
   the sender names H_T.

## Prompts

Rendered by the QX-3 engine exactly as in v3 (generation 6, δ 1/8, B 1 spent, rule + chosen result,
previous and published rule H_F, all eight neighbours named H_F in generation 5, the first-slot neighbour
carries one result), with the world's own catalog, examples and keys.

- **Cells:** per world, the first 20 cells in `sha256("qxiso|<world>|<cell id>")` order; world 0 keeps the v3
  cells (`sha256("qxiso|<cell id>")`). From the dry build (rechecked by the reviewer): w1 39, 90, 37, 84, 17, 11,
  19, 82, 50, 12, 66, 1, 20, 23, 38, 91, 0, 18, 22, 21; w2 75, 39, 52, 26, 34, 84, 45, 79, 98, 63, 21, 82, 94, 33,
  72, 59, 66, 68, 77, 90; w3 63, 34, 44, 51, 41, 0, 31, 39, 85, 25, 60, 78, 45, 33, 87, 3, 56, 83, 71, 16.
- **Counterexample per world** (one input, chosen so that only the substitution differs from H_F):

  | world | H_F | H_T (δ 1/8) | counterexample | H_F gives |
  |---:|---|---|---|---|
  | 0 | K026 | K047 | `DAAA -> FBBB` | `EBBB` |
  | 1 | K035 | K034 | `AAAC -> BBBE` | `BBBD` |
  | 2 | K114 | K015 | `EAAB -> BBBC` | `FBBC` |
  | 3 | K028 | K043 | `AAAD -> BBBC` | `BBBE` |

  Confirming results as in v3 in every world: `AAAA -> BBBB`, `CAAA -> DBBB` (both fit H_F and H_T in all
  four worlds; reviewer's pre-check, to be repeated in the dry build).
- **Conditions:**

  | condition | own result | received result | first-slot sender names |
  |---|---|---|---|
  | U0 control | `AAAA -> BBBB` | `CAAA -> DBBB` | H_F |
  | U1 own counterexample | counterexample | `AAAA -> BBBB` | H_F |
  | U2 received counterexample | `AAAA -> BBBB` | counterexample | H_F |
  | **U3 received, sender names H_T** | `AAAA -> BBBB` | counterexample | **H_T** |

  U3 differs from U2 in one token of the first-slot message (the rule key). In world 0 only U3 is new (the
  v3 U0–U2 calls are reused); worlds 1–3 run U0–U3.
- Three draws. Per model: world 0, 60 calls (U3); worlds 1–3, 3 × 240 = 720; **780 calls per model**.

## Models

Luna (gpt-6-luna, medium, `max_output_tokens` 8192 as in v3), gpt-oss-20b, gpt-oss-120b, Qwen3.6-35B-A3B
(only if its world-0 v3 run passes its format gate), with the v3 decoding. Nemotron is not run (Artem,
2026-11-24: operational). Claude Haiku 5.5 runs the same 780 prompts as Stage 1 of `AMENDMENT_QX_HAIKU55.md`;
for it T-U3 is predicted **uncertain** (no population data).

**Luna cost:** 780 calls at the v3 rate ($0.0003886 per call, dry build) ≈ $0.303; hard stop $0.60, within the
unreserved remainder of the $45 authorization ($0.95). **GPU:** at the v3 timings, about 2–3 h each for
gpt-oss-20b and gpt-oss-120b; Qwen3.6 from its v3 timing.

## Measures

As in v3 and the joint addendum (consistent, leave, exact, attach, attach_cx, pass_rule, silent; joint
counts), per model, world and condition; cell is the unit, draws nested.

## Tests and readings (stated in advance)

**T-U3 (per model): a sender naming H_T raises updating.** Paired difference U3 − U2 in *consistent* by cell,
pooled over the four worlds (80 cells), 95 % cell-bootstrap interval (2,000 resamples, seed 0, cells
resampled within world). Holds if the interval lies above 0. One claim per model, no family correction
(stated). **Prediction:** holds for Luna and gpt-oss-20b, derived from the population first-contact rates
above (59 % against 7 %; 54 % against 21 %); uncertain for gpt-oss-120b and Qwen3.6 (no population data).

**Replication across worlds (descriptive, per model):** the world-0 reading row re-read in worlds 1–3
(U1 level; U2 − U1 interval; attach_cx given consistent). Reported as "same row in k of 3 worlds".

| pattern | reading |
|---|---|
| T-U3 holds, U3 ≈ U1 | The U2 drop was the sender's own vote against its evidence, not distrust of received evidence. |
| T-U3 holds, U3 clearly below U1 | Both: the sender's vote matters, and received evidence is still taken less than own. |
| T-U3 does not hold, U2 < U1 | The drop is about the source (or the message channel), not the sender's named rule. |
| gpt-oss-20b U1 near 0.5 in worlds 1–3 | Its partial updating is not tied to the world-0 input. |

## Gates

Prompt identity across models; format gate per model per world (more than 6 of 240 unparsed or truncated
stops that model in that world and is reported); world checks (the counterexample contradicts H_F and fits
H_T; confirming results fit both; no clash with any cell's example inputs); U3 and U2 prompts differ only
in the first-slot rule key; the stopped-model readout of 2026-11-24.

## Dry build (CPU)

1. The 780 prompts per model and their sha256; diffs U2/U3 per world (one token), U0/U1/U2 against v3's
   structure.
2. The consistent sets per cell and condition in each world.
3. Request bodies; Luna cost estimate; GPU estimate; queue position.
4. The readout and T-U3 on stub answers, including within-world cell resampling.

## Outputs

Per model a recheck package in the v3 form. Nothing enters the QX page before the reviewer's recheck;
the results extend entry 16 (grid with a world selector and U3 row).
