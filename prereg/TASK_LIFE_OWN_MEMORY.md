# Task — Messages or memory? Silent controls that keep each cell's own previous rule

**Status:** locked 2026-10-13 (commit before gate; before Dr-cat). API only (Luna), no GPU.
Parents: `TASK_LIFE_REASONING_CELLS.md` (B, Bs, Ca, Cas), `TASK_LIFE_DISCOVERY_ECHO.md`
(KH-r, KHs-r), `TASK_LIFE_PUBLISH_VOID.md` (KHe-pub, KHv).

## Why

Every Life control "without a channel" removed two things, not one:
- the neighbours' messages;
- the cell's memory of its own previous rule.

`memory.py` clears `say` when a cell does not publish, so a silent cell sees only
`Previous step: answer=… correct=… silence.` It knows its last answer and whether it was right,
but not which rule produced it. A cell with the channel on sees
`… published signal=0 say='<its rule>'`.

The publish-into-void runs isolate that memory line at the highest ambiguity:
- KHe-pub (published, self-echo inbox) proposes P_e at 0.042;
- KHv (published, empty inbox) proposes at 0.041;
- KH-r (live channel) proposes at 0.012;
- KHs-r and KHe (silent) propose at 0.

So the claims below rest on a confounded contrast:
- C-L1 (B − Bs, +0.57 on two-op);
- C-L2 (Ca − Cas);
- the persistence part of C-L4;
- C-L7 / E1;
- K3.

This task restores the cell's own previous rule to silent cells, changing nothing else.

In the void arms, the memory line ties "remembers its rule" to "published it". The arms here
separate those as well: the memory line keeps `silence` and adds the rule.

## Arms

Same seeds, examples, sources, prompts, decoding and 10 generations as the parent arms. Channel
off in every arm. The only change against the matching silent arm is the memory line.

| arm | cells | depth / level | memory line at g ≥ 2 | matched silent arm |
|---|---|---|---|---|
| **Bs-mem** | reasoning (Responses, medium) | 2-op seeds 1–5, 4 sources | `… correct=… silence held_rule='<rule>'.` | Bs-r |
| **Bs-r** | reasoning | same | `… correct=… silence.` (replicate of Bs) | — |
| **Cas-mem** | one-pass (Decisions, argmax) | 2-op seeds 1–5; 1-op seeds 6,7,18,22,29 (parent schedule — see `AMENDMENT_OWN_MEMORY_SEEDS.md`), 4 sources | `… silence held_rule='<rule>'.` | Cas-r |
| **Cas-r** | one-pass | same | `… silence.` (replicate of Cas) | — |
| **KHs-mem** | reasoning | KH level (critical-mass draws), 0 sources | `… silence held_rule='<rule>'.` | KHs-r (echo task) |

- `<rule>` is the rule the cell held after its decision at g−1 (its inferred rule), rendered
  exactly as `say='…'` is rendered in published memory lines.
- The constitution text ("one-step memory of your last answer") is not changed; the memory line is
  the only difference. State this in the readout.
- **References, not rerun:**
  - B and Ca (channel on, 2026-10-10/11);
  - KH-r, KHs-r (echo task, 2026-10-12);
  - KHe-pub and KHv (void task, 2026-10-13).
  - Bs-r and Cas-r are rerun here so the memory contrast is same-day.

## Gate (before the first call)

- Dry-render the g2 prompt for 3 cells per new arm and diff against its matched silent arm (same
  seed, cell, previous answer).
- **The only allowed difference is ` held_rule='<rule>'` in the memory line.** Commit the diffs
  (`prompts/own_memory_gate_diffs.md`).
- Startup asserts:
  - channel off;
  - no deliveries;
  - the held_rule equals the cell's rule at g−1 in every generation;
  - no `inferred_rule=None`.
- Save rendered prompts.

## Metrics

- J at g10 and J averaged over 10 generations; correct and false locks; modal rule at g10.
- **Self-revision hazard:** over cell-generations with g ≥ 2 where the cell did not hold P_e at
  g−1 and was told wrong, the share that holds P_e at g. There is no channel, so every such
  switch is unreceived.
  - Same definition as the echo proposal hazard.
  - Report events, distinct cells, seeds, numerators and denominators.
- **Persistence:** the share of told-wrong cell-generations in which the cell keeps the same rule.
- Retention of P_e after `correct=true`.
- Validity: invalid / fallback counts; mean prompt length; share of false-rule answers marked
  `correct=true`.

## Predictions (lock)

- **M1 (memory matters for reasoning cells):** Bs-mem J at g10 > Bs-r J at g10 in ≥ 4/5 seeds.
- **M2 (messages still add beyond memory):** seed-mean J at g10, B − Bs-mem ≥ 0.20 (B reference
  0.99).
- **M3 (memory, not publication, at high ambiguity):** KHs-mem pooled self-revision hazard ≥ 0.02
  (half of the void arms' ~0.041).
- **M4 (one-pass cells cannot use the memory to compose):** on 2-op, |Cas-mem − Cas-r| J at g10
  < 0.05 (seed mean). The 1-op contrast is descriptive.
- **M5 (descriptive):** persistence in Bs-mem vs Bs-r on seed 1, where the first op alone fits
  almost every example (C-L4).

## Readout

- **M1 PASS, M2 PASS:** both matter. Memory of one's own refuted rule lets a reasoning cell
  refine it alone, but messages still add most of the two-op gain. C-L1 is restated as messages
  on top of memory, with the size of each part.
- **M1 PASS, M2 FAIL:** memory carries most of what was credited to messages. C-L1 is withdrawn in
  its current form and restated: two-op rules need either each agent's memory of its own refuted
  hypothesis, or the channel.
- **M1 FAIL:** memory alone does not help at default ambiguity; C-L1 stands as messages.
- **M3 PASS:** at high ambiguity, unreceived proposals come from remembering one's own refuted
  rule, not from publishing it; C-L7 is restated accordingly. **M3 FAIL** while the void arms are
  high: the publication framing itself matters.
- **M4:** if one-pass cells gain from memory on 2-op, report it; it changes C-L2.

## Cost

Reasoning arms: Bs-mem, Bs-r, KHs-mem, 15 runs at about $0.5 each. One-pass arms: Cas-mem and
Cas-r at both depths, 20 runs, cheap. Estimate ≈ $10–14; cap $20. This task runs before Dr-cat.
Report the actual cost.

## Artifacts

- `prompts/own_memory_gate_diffs.md`
- `runs/life_own_memory/{Bs-mem,Bs-r,Cas-mem,Cas-r,KHs-mem}/seed{n}/` (with depth subfolders for
  Cas)
- `runs/life_own_memory/summary.json` (M1–M5, with the references alongside)
- `fig_own_memory.png`:
  - J(g) for B, Bs-r, Bs-mem (2-op);
  - Ca, Cas-r, Cas-mem;
  - self-revision hazard for KHs-r, KHs-mem, KHv, KHe-pub, KH-r.

## Constraints

Placement only: no training on outputs, no reasoning text requested or stored. The same prompts as
the parent arms except the memory line. Commit this file before the gate. Amendments before numbers.