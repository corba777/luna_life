# Amendment — TASK_LIFE_DR_QWEN_INTERVENTIONS: QI-H, compositional completion on Qwen

**Status:** locked before any QI-H call. Local, no API cost. Parents:
`AMENDMENT_DR_TIPPING_PART_H.md`, `AMENDMENT_DR_QWEN_INTERVENTIONS_QIG.md`.

## Design

- The 480 Part H prompts, rebuilt by the Part H builder and checked byte-identical to the prompts
  Luna received, before any Qwen call.
- Model and settings exactly as Qwen Stage 1. Own cache namespace, own lock. Parse failures and
  truncations are counted and excluded from n.
- Queue: after QI-G, before any moore run. Nothing else on the server at the same time.

## Predictions (re-locked for Qwen)

The same tests as Part H. One-sided Fisher, α = 0.05. Beside H1q, the cell-level paired sign-flip
test and a cluster bootstrap over cells (2000 draws, seed 0) are reported and not scored.

- **H1q:** pooled over worlds 1, 2 and 5, P(answer P_e | pre8) > P(answer P_e | empty8).
- **H2q:** pooled over worlds 1, 2, 3 and 5, the share answering the prefix under pre8 is ≤ 0.08.
- **Descriptive:** every world × condition cell with Wilson intervals; world 3 against Luna's Part H
  rebuild; per-prompt agreement with Luna's Part H answers.

## Note

The source cells are Luna states, with the constructed memory line Part H uses. The comparison is
two models on identical inputs. That is stated in the readout.
