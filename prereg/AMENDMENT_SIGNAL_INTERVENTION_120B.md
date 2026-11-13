# Amendment — signal intervention, gpt-oss-120b follow-up (`all` r3)

**Status:** locked (Artem, 2026-11-13), before any call. It runs on the GPU, after the current queue
(QX-1r, then the check nudge), and only on Artem's go.

## Why

`AMENDMENT_SIGNAL_INTERVENTION.md` (gpt-oss-20b) pre-stated an optional follow-up on gpt-oss-120b `all`
r3, to run if at least one 20b contrast was ≠ 0. The 20b readout, rechecked on 2026-11-13, has three
such contrasts:

- ADOPT `zero` −0.104;
- ADOPT `cross` −0.105;
- KEEP `cross` −0.056.

So the follow-up runs. It asks whether the larger model reads its own convention the same way. In r3,
"3 = P_e" covers 0.94 of the 619 P_e messages in rounds 6–20 (0.99 over rounds 6–80).

**Copied from the 20b amendment unless stated here:** the item definitions, the edit rules, the gates
and the measures. The arms, the contrasts and the readings differ (below).

## Differences from the 20b amendment

- **Source.** gpt-oss-120b, world 1, `all`, run r3 only, rounds 6–20. This is the only 120b run with
  a convention.
- **$s^*$ and $s_{\text{pre}}$.** They follow the same operational definitions. The pre-lock check
  found $s^* = 3$ (gap 0.973 over rounds 1–80) and $s_{\text{pre}} = 0$ (675 of 677 prefix messages
  in rounds 6–20), so `cross` swaps 3 ↔ 0. The dry check must reproduce both.
- **Cluster.** The cell, because there is a single run: up to 100 clusters per stratum.
- **Engine.** This is not the 20b engine. It is the stored 120b launch (`run_oss120_part_a._start`):
  - SGLang 0.5.22, image `lmsysorg/sglang@sha256:06441be3…`;
  - `openai/gpt-oss-120b` at revision `b5c939de…`;
  - context 40,960, memory fraction 0.82, 4 concurrent requests;
  - deterministic inference off, flashinfer sampling, reasoning parser `gpt-oss`.

  The request body is the stored one: temperature 1.0, top_p 1.0, max_tokens 32,768, reasoning effort
  `medium`, strict schema `life_cell_decision_v2`, no seed. The rendered date is pinned to the stored
  2026-10-22 (template `chat_template_date_20261022.jinja`, sha256 `e6433aba…`), so one launch serves
  every item. Unparsed answers get the stored retry: one re-ask if not truncated, with the draw
  offset by 1,000.
- **Arms: `orig`, `zero`, `cross`.** `perm` is dropped. On 20b it showed that the particular number
  does not matter (−0.022), and the question here is only whether 120b reads a non-zero mark on $P_e$.
  Its budget goes to power.
- **Contrasts: four** (`zero` and `cross` against `orig`, in two strata), each at $1 - 0.05/4$ = 98.75 %.
- **Sample size: derived from the 20b effect, not from a time budget.**
  - At 120b's stored ADOPT rate (about 0.17), a floor limits how far adoption can fall.
  - The comparable effect is 20b's relative drop in ADOPT (−0.104 / 0.385 = −27 %) applied to
    120b's base rate: about −0.045.
  - **ADOPT: n = 861, all eligible items, 2 draws.** The rule was the smallest n whose simulated
    effective detectable decrease at 80 % power is ≤ 0.045. The simulated value is noisy in n. It
    first reaches ≤ 0.045 at n = 626, fails again at 629, 640, 775 and 800, and passes for every
    n ≥ 825. So the whole pool is used. The power simulation is not outcome data, so this choice
    does not bias the test.
    - Detectable decrease at 98.75 %: 0.039 effective (0.04 nominal).
    - With the whole pool used, the hash ranking does not apply to ADOPT.
  - **KEEP: n = 250, 2 draws.** Its detectable decrease at 98.75 % is 0.058, near 20b's KEEP
    `cross` effect of −0.056. Items are drawn without replacement, ranked by
    `sha256("sigint120|round|cell")`.
  - **Run size.** 6,666 calls. At the measured 10.76 s per call (4 concurrent requests), this is
    about 20.1 GPU hours including server start.

**Pre-stated readings (per stratum).**

| zero | cross | reading |
|---|---|---|
| ≠ 0 (down) | ≠ 0 (down) | As on 20b: a non-zero mark on $P_e$ persuades. |
| ≈ 0 | ≈ 0 | No effect of the mark is detected at the stated detectable difference. 120b reads the name, not the mark, at this precision. |
| ≈ 0 | ≠ 0 | Only giving $P_e$ the prefix's number matters: a prior on that number. |
| ≠ 0 | ≈ 0 | Removing every mark matters, but swapping them does not: the contrast is what is read. |

Other patterns are reported as observed.

## Additional reading (beside, descriptive)

The 120b contrasts are compared with the 20b ones as a difference of differences, with an interval
from bootstrapping each model's clusters independently. This shows whether the two models read the
mark alike. It is not a test.

## Limits

- One run of one model, so its convention may be specific to that run.
- A fresh draw on rounds 6–20 cuts the population feedback, as in the 20b study.