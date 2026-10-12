# Amendment — Life reasoning cells: arm Cas (Ca without channel)

**Status:** locked 2026-10-10. Commit before any Cas number.
Parent: `TASK_LIFE_REASONING_CELLS.md` (arms A, B, Bs, C, Ca, D, Da). Nothing in the parent
changes; this adds one arm and its predictions.

## Why

Ca (Luna Decisions, sparse, argmax, channel on) gives J ≈ 0.53 on 1-op and ≈ 0.14 on 2-op,
and on 2-op more false locks than correct ones (FL_gen 0.26 vs CL_gen 0.08). Without a
no-channel control we cannot say:
- whether the 1-op rise (g1 ≈ 0.24 → g10 ≈ 0.71) comes from the channel or from each cell's own
  memory + feedback;
- whether Ca's 2-op false locks are contagion through the channel or a shared prior, as in Bs
  (Bs 2-op FL_gen 0.44 with no channel at all).

Cas is to Ca what Bs is to B.

## Arm

**Cas** = Ca with `channel=False`. Everything else is identical to Ca:
- model, Decisions estimator, P=4 orderings, `order_seed`, argmax decode with seeded tie-break;
- sparse examples, sources `SPARSE_SOLVER_IDS` (0, 5, 50, 55), feedback, memory (answer + correct;
  no `say`, since nothing is published), epoch length 10, `n_epochs=1`;
- **same seeds as Ca:** 1-op seeds 6, 7, 18, 22, 29; 2-op seeds 1–5 (n=5 per n_ops).
- Same prompt text as Ca except that the inbox/publish part is absent, exactly as Bs relative
  to B (`map_responses_payload` / Decisions mapping with `communication=None`).

**Invariant checks (abort on violation):**
- `assert_encode_logs_rule` on every step (as for all arms; only `None` aborts);
- every cell's inbox is empty at every generation;
- no publish/`say` field in any request payload;
- source cells behave as in Ca (they hold P_e; with no channel they cannot spread it).

## Metrics

As in the parent: J (non-source) by generation and epoch mean, lock (modal share ≥ 0.5),
`false_lock_gens`, `correct_lock_gens`, ΔAUC, by n_ops. Contrasts are paired by seed (same
seeds as Ca), with a cluster bootstrap by seed. n=5 per n_ops, so CIs will be wide; report
per-seed rows.

## Predictions (lock)

- **CS1 (2-op):** |J(Ca) − J(Cas)| < 0.05. The channel adds nothing for cells that cannot
  verify a two-op claim.
- **CS2 (1-op, primary):** J(Ca) − J(Cas) > 0, CI excludes 0. Magnitude reported descriptively.
- **CS3 (2-op):** Cas `false_lock_gens` ≥ 0.10. One-pass cells, like Bs, reach false
  consensus from a shared prior without any messages.
- **CS4 (descriptive):** g1 J of Cas vs Ca, by n_ops. Before any delivery the two arms should
  differ only by the missing inbox text; a large g1 gap is a prompt effect, which must be
  reported before any contrast is interpreted.

## Readout

- CS1 + CS2 PASS → Decision cells use the channel only where they can check a claim
  themselves (1-op). On 2-op, communication needs the intermediate step (B) or external checks
  (D/Da).
- CS2 FAIL (Ca ≈ Cas on 1-op) → Ca's 1-op rise comes from individual memory + feedback; the
  answer to "can Decision cells communicate?" is no on both depths.
- CS1 FAIL with Ca > Cas on 2-op → the channel helps one-pass cells somewhat even without
  verification; inspect what the gain consists of (copying sources? fewer false locks?).
- CS1 FAIL with Ca < Cas on 2-op → the channel harms: false claims spread. Compare FL_gen.

## Add-on diagnostics (descriptive, no new runs; for Bs, Ca and Cas)

For every seed with a false lock (Bs 2-op seeds 1, 3, 5; Ca 1-op seed 7, Ca 2-op seeds 1, 2, 5;
any Cas seeds):
1. the locked false rule and its n_ops (is a 1-op rule winning on a 2-op task?);
2. whether it is consistent with each locking cell's private example;
3. for Ca: whether the rule was in the cell's inbox before the cell first chose it, or was
   chosen at g1 before any delivery (contagion vs shared prior);
4. the base rate: the share of g1 picks that are 1-op rules, against the share of 1-op rules
   among the rules consistent with the examples.

## Cost and scheduling

API only (no GPU); runs in parallel with Da and the Unsloth battery. Expected cost is close to
Ca's (Cas sends shorter prompts). Record the actual cost.

## Artifacts

- `runs/life_reasoning_cells/arm_Cas/seed{n}/` (same layout as Ca)
- `runs/life_reasoning_cells/summary_Cas.json`, `contrast_ca_cas.json`
- `runs/life_reasoning_cells/false_lock_diagnostics.json`
- add Cas to `false_lock_all_arms.json` and `fig_j_by_gen.png` (dashed orange next to Ca)