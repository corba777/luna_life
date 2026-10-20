# Amendment — TASK_LIFE_DR_QWEN_INTERVENTIONS: QI-I, the own-example filter on Qwen

**Status:** locked before any QI-I call. Local, no API cost. Parents:
`AMENDMENT_DR_TIPPING_PART_I.md`, `AMENDMENT_DR_QWEN_INTERVENTIONS_QIH.md`.

## Design

- The 480 Part I prompts, rebuilt by the Part I builder and checked byte-identical to the prompts
  Luna received, before any Qwen call.
- Model and settings exactly as Qwen Stage 1. Own cache namespace, own lock. Parse failures and
  truncations are counted and excluded from n.
- Queue: after QI-H, before any moore run. Nothing else on the server at the same time.

## Predictions (re-locked for Qwen)

The same tests as Part I. One-sided Fisher, α = 0.05. Beside each test, a by-example paired
comparison where the same base input serves both groups is reported and not scored.

- **I1q:** pooled over k, P(prefix answer | adjacent pairs) > P(prefix answer | non-adjacent pairs).
- **I2q:** at k = 1, P(prefix answer | (2,3)) > P(prefix answer | (0,3)).
- **Descriptive:** the 2 × 6 table of prefix, consistent and true answers with Wilson intervals; the
  effect of k at fixed (i, j); per-prompt agreement with Luna's Part I answers.

## Note

The source prompt is one Luna round-1 cell, with only the example line replaced. The comparison is
two models on identical inputs. That is stated in the readout.
