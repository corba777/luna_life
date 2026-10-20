# Amendment — TASK_LIFE_DR_QWEN_INTERVENTIONS: QI-G, the signal 2 × 2 on Qwen

**Status:** locked before any QI-G call. Local, no API cost (approved; local work is pre-approved by
Artem). Parents: `TASK_LIFE_DR_QWEN_INTERVENTIONS.md` and its QI-1m amendment,
`AMENDMENT_DR_TIPPING_PART_G.md`.

## Design

- The 1280 Part G prompts (redo D-logged geometry; P_e signal 7 or 0 × opposition signal logged or 0;
  8 and 88 lines; shares 0.25 and 0.375; the 40 Part 0c/D source cells; 2 draws), rebuilt by the Part G
  builder and checked byte-identical to the prompts Luna received, before any Qwen call.
- Model and settings exactly as Qwen Stage 1. Own cache namespace, own lock. Parse failures and
  truncations are counted and excluded from n.
- Queue: after QI-1 and QI-1m, before any moore run. Nothing else on the server at the same time.

## Predictions (locked)

The same tests as Part G, on Qwen, pooled over lengths and shares, one-sided Fisher, α = 0.05:
- **G1q:** with opposition logged, P(leave | P_e at 0) > P(leave | P_e at 7).
- **G2q:** with P_e at 7, P(leave | opposition logged) > P(leave | opposition at 0).
- **Descriptive:** all 16 cells with Wilson intervals; per-prompt agreement with Luna's Part G answers;
  the length contrast inside each signal condition (does the Luna length effect replicate on Qwen).

## Correction (2026-10-20)

The Part G prompts are the corrected ones. All four signal conditions share the redo D-logged
geometry, and (P_e 0, opposition 0) is not the redo D-zero prompt. Before any Qwen call, each prompt
is still checked byte-identical to the prompt Luna received.

## Note

The source cells are Luna states (Luna's memory line and Luna's prior rule). The comparison is two
models on identical inputs, not Qwen in its own states. That is stated in the readout.