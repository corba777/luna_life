# Amendment — anchor or inference? Two prompt changes on Qwen's adoption (cell-level battery)

**Status:** locked v2 (2026-11-14; v2 fixes the four defects the agent's dry check found), before any
call. Written by the reviewer for Artem; dry check passed; locked on Artem's instruction. No call is
made before Artem's go. It runs locally on the GPU, after the QX-2 pilot.

## Why

Under the check nudge (`AMENDMENT_QWEN_CHECK_NUDGE.md`, locked, rechecked 2026-11-14), Qwen
checked more but did not adopt more.

- The share of traces stating that both rules fit rose from 0.40 to 0.61 (N3 holds).
- Adoption did not rise (N1 and N2 fail).
- Post hoc, a "both fit" statement that names the neighbours' rule was followed by adoption half
  as often (0.16 against 0.33).

So the barrier is not a missing check. Three explanations remain. The literature names the first
and the third.

1. **Anchor.** The prompt shows the cell its own last rule ("Previous step: rule='…'
   published=…"). Models that see their own earlier answer show a choice-supportive bias and change
   their mind less (Kumaran et al. 2025, arXiv 2507.03120).
2. **Missing inference.** A neighbour's message is evidence about that neighbour's private
   examples. A cell whose own example fits both rules can switch only by inferring this. Qwen may
   read the messages as opinions.
3. **Simplicity.** When two rules fit, Qwen prefers the shorter one. Transformers tend to choose
   the least complex sufficient explanation (Deora et al. 2025, arXiv 2506.19351).

This amendment tests (1) and (2) directly. It cannot test (3) directly. If neither (1) nor (2)
moves adoption, (3) is the remaining reading, and it is stated as such, not as a result.

## Model, engine, sampling

As in the check nudge, unchanged:

- Qwen3-4B-Thinking-2507, revision `768f209d`;
- SGLang 0.5.18 (image `223b675f`, unpatched), context 40,960;
- the battery request body (W1-r1-think);
- one draw per prompt and arm, no request seed;
- reasoning text stored for every call (open model).

The canary rule is the same as in the nudge.

## Items

The same 440 prompts as in the check nudge, taken from that run's `control` arm. Its `items.json` is pinned
by sha256 `6ce498f11abd8a1c3208284d29c325951688432b00be3a2b858f426ed43e8791`, and its
`calls_control.jsonl` (used by the fidelity gate) by sha256
`8f8f371495fcff6d2e01bed3b6e76812e6a353d359fb4bc1b0d7b435958df830`.

- **MAIN:** 400 prompts (the 18 lattice conditions with k ≥ 1 and the two S88 `all` conditions,
  20 cells each);
- **DECOY:** 40 prompts, in which the P_e lines are replaced by D = `shift_symbols(2);swap(2,3)`,
  which fits no example.

## Arms

The order of all calls is shuffled by `sha256("anchor-order|id|arm")`.

| arm | change to the `control` prompt |
|---|---|
| `control` | none (byte-identical to the nudge's `control`) |
| `noanchor` | two deletions: the line "Previous step: rule='…' published=…" together with the blank line after it, so the paragraph structure is unchanged; and, so that the prompt does not contradict itself, the clause ", a one-step memory of the rule you held last generation (and whether you published it)" in the paragraph that lists what the cell sees |
| `inference` | one line is inserted immediately before "Decide for this cell now.": "Each neighbour chose its rule from its own private examples, which differ from yours." |

- **The inference sentence.** It is true in the game: every cell answers from its own examples. It
  does not name a rule. It does not say whether a rule fits, or which rule fits. It does not
  mention adopting, majority or checking.
- **Dry check.** The dry check verifies that the sentence matches none of REFUTE, BOTHFIT or
  MAJORITY, and reports its length in Qwen tokens.
- **`noanchor`.**
  - The removed line and the removed clause must each occur exactly once in every prompt. The dry
    check verifies this and shows the removed bytes for three prompts.
  - The sentence "You are not told whether your last rule was correct." is kept. It is still true,
    and removing it would be a third change.
  - Nothing else changes. In particular, the cell's own example and the messages stay.
- **Byte identity.**
  - Re-inserting both removed pieces into `noanchor` must give `control` byte for byte.
  - Removing the inserted line from `inference` must give `control` byte for byte.

**Total calls:** 440 × 3 = 1,320. At the nudge's measured speed, this is about 11 GPU hours.

## Measures and rule (locked)

- **Unit.** The cell. Differences are paired by prompt. Intervals come from a cell bootstrap:
  4,000 resamples, numpy `default_rng(0)`, percentile intervals.
- **Contrasts.** Two, on MAIN adoption of P_e. Each is two-sided at 1 − 0.05/2 = 97.5 %
  (Bonferroni over two).

| name | statistic (MAIN) | holds if |
|---|---|---|
| A1 | adoption: `noanchor` − `control` | interval above 0 |
| I1 | adoption: `inference` − `control` | interval above 0 |

- **Minimum detectable difference.** At 80 % power, from a null that permutes arm labels within a
  prompt. It is reported beside each contrast. The nudge run's MDD80 was 0.057–0.066 at the same n.
- **Descriptive only, each with its interval:**
  - DECOY adoption of D by arm, and each arm minus `control`;
  - per arm: the BOTHFIT, MAJORITY and REFUTE shares (v3 patterns);
  - adoption given a BOTHFIT sentence that names swap(2,3) or R064;
  - reasoning tokens (mean, median, p95, truncation share);
  - per arm on MAIN: the share of answers equal to the prefix `shift_symbols(1)`. In this battery the
    cell's last rule is always the prefix (440 of 440 prompts, published=yes);
  - for "adoption given a BOTHFIT sentence that names swap(2,3) or R064", the match is within the
    same sentence (the v3 sentence split), as in the reviewer's nudge recheck.
- **Gates.**
  - **Format.** Invalid or truncated answers score 0. The run stops if they exceed 4 of the first
    400 calls. The stored basis is the check nudge: 0 invalid and 0 truncated in its 1,320 calls on the
    same prompts.
  - **Fidelity.** `control` adoption on MAIN minus the nudge run's `control` on the same prompts,
    with a two-sided 95 % interval that must contain 0. If the gate fails, the contrasts are read
    as conditional on this launch.

## Pre-stated readings

- **A1 holds, I1 does not.** Seeing its own last rule keeps Qwen on it. This is the
  choice-supportive account.
- **I1 holds, A1 does not.** Qwen does not by itself treat the messages as evidence about other
  cells' examples. Saying so raises adoption.
- **Both hold.** Both contribute. The two effect sizes are reported side by side. They are not
  tested against each other.
- **Neither holds.** At this precision, neither the anchor nor the missing inference is the
  barrier. The remaining reading, a preference for the shorter fitting rule, is consistent with the
  data, but this design does not test it.
- **DECOY.** If an arm raises adoption of D, that arm makes Qwen more credulous rather than better
  at using evidence. This is reported whatever A1 and I1 show.

## Outputs

- `items.json` with the prompts per arm and the dry-check results.
- `calls_<arm>.jsonl` with the reasoning and final text.
- `readout.json` / `.md`.
- A recheck package in the nudge's format, with `derived/reasoning_length`.

Nothing enters the paper before the reviewer's recheck from raw data.

## Limits

- One model, one world, one draw per prompt. The battery is cell-level, not a population run.
- **In this battery the anchor always points to the shorter rule.** Every cell's last rule is the
  prefix. A1 therefore cannot separate an anchor on the cell's own rule from an anchor that only
  reinforces the simpler rule.
- **`noanchor` removes information as well as an anchor.** In the population game, a cell's last
  rule is real memory. A positive A1 shows that the line holds Qwen back; it does not show that
  memory should be removed.
- **The inference sentence can work as a hint even though it names no rule.** DECOY is the only
  specificity check, and it is small (40 prompts).
- MAIN cannot separate better use of evidence from more acceptance, because both rules fit every
  class-A example. This limit is the same as in the nudge.

## Queue

A new waiter after the QX-2 pilot waiter's done file. It follows the usual sequence:

1. `wait_qx2_pilot20b_done`;
2. `wait_go_qwen_anchor_inference`, which needs a go file and a switch-log line with Artem's
   words;
3. precheck: the manifest sha, a free GPU, no `jev-sglang` running;
4. run;
5. readout;
6. package.

Watcher v3 and the GPU monitor run beside it. Every `gpu_step` call site uses `|| fail`, so the
dead-`rc=$?` pattern from the 2026-11-14 audit does not occur.