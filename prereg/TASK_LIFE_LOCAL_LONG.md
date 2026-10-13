# Task — Long Life runs on our own decision models: checks, mixes and ignition

**Status:** registered draft. **Predictions are locked by amendment** after the calibration
step (Part 1) and before any Part 2 number (none locked yet). GPU (local), after `gpu_chain.ok`,
Phase 0 (300) and `TASK_UNSLOTH_DECISION_HYBRID.md` (queue after Unsloth hybrid). Follows
`DESIGN_CHECKLIST.md` and `CONTEXT_MODELS.md`.

## Why

On `gpt-6-luna` (10 generations):
- one-pass populations with an engine check reach the rule without a teacher (Da0 0.79) and are
  still rising at g10;
- without a check the outcome is world-dependent (Ca 0.00–0.56 by seed);
- with 10% reasoning cells, some worlds ignite a wave and others do not (Mx10 one-pass 0.00–0.79).

Ten generations and five seeds cannot show late ignition or a critical share of strong agents.
Projections from 10-generation rates cannot predict rare ignition events. Local models make 50+
generations cheap.

## Cells

From `TASK_UNSLOTH_DECISION_HYBRID.md` (Qwen3-4B-Instruct-2507 and SPADE-4B):
- **V1:** one-pass decision head (Luna Decisions analogue).
- **V2:** reason-then-decide head (Luna reasoning analogue).
- **L0:** untrained logprob baseline: the same base model scoring option keys, P=4. Isolates what
  the Unsloth head adds.

## Part 1 — calibration against Luna (10 generations, 2-op seeds 1–5, same worlds and prompts)

| local arm | Luna reference |
|---|---|
| V1, channel, no check, 4 sources | Ca |
| V1, channel, no check, 4 sources | **An** (Responses `effort=none`; beside Ca) |
| V1, channel, engine check, 0 sources | Da0 |
| V2, channel, 4 sources | B |
| V1 + 10% V2, no check, 4 sources | Mx10 |
| L0, channel, engine check, 0 sources | Da0 |

Candidate (unregistered until An0 / Z1–Z3): also calibrate against **An0** (An with 0 sources)
and, separately, extend Luna An/Ca to 30–50 generations to see whether sticky Ca catches fast An.

Report J(g) per seed against the Luna curves. Calibration is descriptive. Part 2 predictions are
written after it, so they use the local models' own baselines.

## Part 2 — long runs (50 generations; seeds 1–5 plus 5 new 2-op seeds)

- **Check vs none:** V1 populations, 0 sources, with and without engine check.
- **Strong-agent share sweep:** V1 with a share s of V2 cells, s ∈ {0, 2, 5, 10, 25}%, no check,
  0 sources; V2 positions seeded uniformly at random (positions committed per seed).
- **Hard world:** seed 2 (`rotate_left(1);swap(0,3)`) in every condition, reported separately.
  Interpretation uses `TASK_LUNA_RULE_PREFERENCE.md` (R1/R2).

Metrics:
- J(g) per seed, never only the mean;
- generation of ignition (first g with J ≥ 0.25 followed by monotone growth for 5 generations);
- final plateau;
- share of seeds that ignite by g50, per condition;
- h(k) and r per seed;
- cost per cell-generation: prefill and decode tokens and measured GPU-seconds (checklist item 7).

## Gate

As in the parent tasks: prompt diffs vs the matched Luna arm. Expected differences: none in the
text; only the model and the decision readout. Request-level check; startup asserts on sources,
check flag and V2 positions.

## Constraints

Local models only; no closed-model outputs used as training data anywhere. New runner script; do
not edit running scripts. Commit before the gate; Part 2 predictions by amendment before any Part 2
number.