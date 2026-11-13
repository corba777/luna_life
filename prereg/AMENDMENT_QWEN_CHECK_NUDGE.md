# Amendment — does asking Qwen to check neighbours' rules move adoption? (cell-level battery)

**Status:** locked (Artem, 2026-11-13), before any call. GPU, local. It is queued after QX-1r and runs
only on Artem's go.

## Why

Reasoning-trace v3 (deterministic repro arm, rechecked) found two things.

- **Adopting traces.** 82 % state that the neighbours' rule also fits the cell's own example, against
  29 % of non-adopting traces. 40 % cite the majority, against 10 %.
- **Non-adopting traces.** They do not state a refutation more often than adopting traces (25 %
  against 24 %).

The reading is that most non-adopters never establish that $P_e$ fits their example. If that step is
the barrier, then a neutral instruction to check every named rule against one's own examples should
raise adoption. A sentence of about the same length that does not ask for the check should not.

This is a change to the prompt for one model, so it is not part of the cross-model design. It is a
probe of the mechanism.

## Engine

The engine is the configuration of the Part A repro standard arm:

- SGLang 0.5.18 (image `223b675f…`), unpatched, standard mode, no seed;
- the battery request body;
- context 40,960;
- reasoning text stored per call.

The canary rule is the same as in the repro standard arm.

## Items

- **MAIN.** The Part A adopt prompts with $k \ge 1$ in the 18 lattice conditions, plus the two `all`
  conditions behind S88 (shares 0.40 and 0.60). That is 20 conditions × 20 cells = 400 prompts.
- **DECOY (specificity).** Two lattice conditions built from MAIN: (k, m) = (6, 2) and (8, 0). Each
  $P_e$ line is replaced by a decoy rule $D$, the same for every cell:
  - $D$ is the catalog rule `shift_symbols(2);swap(2,3)`. It has the same form as $P_e$ but the wrong
    shift. Position 0 is swapped by neither rule under either position convention, and $D$ shifts it
    by 2 where the example shifts it by 1. So $D$ fits no class-A example. The dry check verifies this
    on all 20 (closest miss: 4 symbols at 0-based positions, 3 at 1-based);
  - its line positions and signals are the $P_e$ lines' positions and signals.

  That gives 2 × 20 = 40 prompts. The outcome is adoption of $D$.

## Arms (one draw per prompt and arm; the order of all calls is shuffled by `sha256("nudge-order|id|arm")`)

| arm | change to the prompt (one line inserted immediately before "Decide for this cell now.") |
|---|---|
| `control` | none |
| `placebo` | "Before you answer, read your private examples and each of the visible messages again, slowly." |
| `nudge` | "Before you answer, check each rule named in the visible messages against your private examples." |

- **Length.** `placebo` has 93 characters and 15 words; `nudge` has 95 characters and 15 words. The
  dry check reports their Qwen token counts.
- **Content.** Neither sentence names a rule, says which rule fits, or mentions adopting. Neither
  matches REFUTE, BOTHFIT or MAJORITY.
- **Exact bytes.** The insertion is `<sentence>\n`, placed directly before "Decide for this cell
  now.", so the sentence joins that paragraph. The dry check verifies that removing it gives
  `control` back byte for byte.

**Total calls:** (400 + 40) prompts × 3 arms = 1,320. The repro standard arm measured 29.6 s per call
of wall time on these conditions, so this is about 11 GPU hours, or about 13.4 if the nudge lengthens
reasoning by 20 %.

## Measures and rule (locked)

- **Unit.** The cell. Differences are paired by prompt, and intervals come from a cell bootstrap:
  4,000 resamples, numpy `default_rng(0)`, percentile intervals.
- **Contrasts.** Three, each two-sided at $1 - 0.05/3$ = 98.33 % (Bonferroni):

| name | statistic (MAIN) | holds if |
|---|---|---|
| N1 | adoption: `nudge` − `control` | interval above 0 |
| N2 | adoption: `nudge` − `placebo` | interval above 0 |
| N3 | BOTHFIT share (v3 pattern): `nudge` − `control` | interval above 0 |

- **Minimum detectable difference.** At 80 % power, from a null that permutes the arm labels within
  prompt. It is reported beside each contrast.
- **DECOY, descriptive only, with its interval.** Adoption of $D$ by arm, and `nudge` − `control`.
- **Gates.**
  - **Format.** Invalid or truncated answers score 0. A stop is triggered if they exceed 4 of the
    first 400 calls; the stored rate is 0 in 3,200.
  - **Fidelity.** The `control` adoption on MAIN minus the repro standard arm's adoption on the same
    prompts, with a two-sided 95 % interval that must contain 0. If it fails, the contrasts are read
    as conditional on this launch.

## Pre-stated readings

- **N1 and N2 hold:** asking for the check raises adoption, beyond a generic instruction to be careful.
  - If N3 holds too, the step the instruction targets ("both fit") moves with it. The barrier is the
    missing check.
  - If N3 does not hold, adoption moves without the stated check. The mechanism stays open.
- **N1 holds, N2 does not:** any added instruction raises adoption. The effect is not specific to
  checking.
- **N1 does not hold:** the instruction does not move Qwen at this precision. The barrier is not
  just a missing prompt to check.
- **DECOY.** If `nudge` raises adoption of the decoy as well, the instruction makes Qwen more
  credulous rather than more careful. This is reported whatever N1–N3 show.

## Outputs

`runs/qwen_check_nudge/`:

- `items.json`, with the prompts per arm and the decoy check;
- `calls_<arm>.jsonl`;
- `readout.json` and `readout.md`;
- a recheck package in the usual format.

## Limits

- One model, one instruction wording, one draw per prompt and arm.
- The decoy is one rule, and it disagrees with every example in every position (the wrong shift). That
  makes it easy to reject, so this is a weak specificity check.
- On MAIN both rules fit every class-A example, so MAIN cannot show whether the nudge improves
  checking or only acceptance. DECOY is the only specificity check, and it is small.