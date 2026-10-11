"""Life v1b Simulation — v1a engine plus check-mark and source-cell hooks.

Board, delivery, TTL, hash selection, memory, seeds, permutation, and epochs
remain ``constitutional_life.sim.engine.Simulation``. This wrapper only:
  1. annotates delivered inboxes (after delivery / G-perm) for render + logs;
  2. bypasses the Completer for seeded ``SPARSE_SOLVER_IDS`` sources.

Marks are computed **once** per step from the observations that enter the
Completer bridge (the same objects the model render uses). The rule_history
``checks`` field is that single computation — not a second pass over a
pre-step snapshot of ``self.examples``.
"""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any

from constitutional_life.board.board import all_cell_ids
from constitutional_life.board.geometry import N_CELLS
from constitutional_life.cell.observation import CellObservation
from constitutional_life.cell.schema import ParsedDecision, Silence, encode_decision
from constitutional_life.sim.engine import Simulation, Snapshot
from constitutional_life.sim.policy import decide

from life_verify.v1b.checks import SlotAnnotation, annotate_inbox
from life_verify.v1b.render import render_state_v1b
from life_verify.v1b.sources import SOURCE_IDS, is_source, source_raw_decision


def _n_ops_for_pe(pe: str, catalog) -> int:
    for fn in catalog.functions:
        if fn.description() == pe:
            return fn.n_ops
    return -1


def _anns_to_log(
    anns: list[SlotAnnotation | None],
) -> list[list[dict] | None]:
    return [a.to_log() if a is not None else None for a in anns]


@contextmanager
def _patch_render_state(sim: "SimulationV1b"):
    """Point JevCompleter's ``render_state`` at precomputed step annotations."""
    import constitutional_life.cell.prompt as prompt_mod
    import constitutional_life.model.jev as jev_mod

    def _render(obs: CellObservation, channel: bool = True) -> str:
        if obs.cell_id not in sim._step_anns:
            raise RuntimeError(
                f"render_state missing step annotations for cell {obs.cell_id} "
                f"(k={sim.k}); bridge must annotate before Completer render"
            )
        return render_state_v1b(
            obs,
            channel=channel,
            k=sim.k,
            annotations=sim._step_anns[obs.cell_id],
        )

    old_prompt = prompt_mod.render_state
    old_jev = jev_mod.render_state
    prompt_mod.render_state = _render  # type: ignore[assignment]
    jev_mod.render_state = _render  # type: ignore[assignment]
    try:
        yield
    finally:
        prompt_mod.render_state = old_prompt  # type: ignore[assignment]
        jev_mod.render_state = old_jev  # type: ignore[assignment]


class _V1bCompleterBridge:
    """Completer facade: source bypass + one-shot mark compute for render & log."""

    def __init__(self, sim: "SimulationV1b") -> None:
        self._sim = sim

    def complete_batch(
        self,
        observations,
        *,
        channel: bool,
        seeds,
        order_seeds=None,
        **kwargs,
    ) -> list[str]:
        sim = self._sim
        assert sim.fn is not None

        # Merge into step maps — do not wipe. ``step()`` clears; multiple
        # complete_batch calls in one step must accumulate.
        for obs in observations:
            sim._step_obs[obs.cell_id] = obs
            sim._step_anns[obs.cell_id] = annotate_inbox(
                examples=obs.examples,
                inbox=obs.inbox,
                k=sim.k,
                world_seed=sim.world_seed,
                generation=obs.generation,
                cell_id=obs.cell_id,
                catalog=sim.catalog,
            )

        n = len(observations)
        out: list[str | None] = [None] * n
        model_obs: list[CellObservation] = []
        model_idx: list[int] = []
        model_seeds: list[int] = []
        model_order: list[int] = []
        order = list(order_seeds) if order_seeds is not None else list(seeds)

        for i, obs in enumerate(observations):
            if is_source(obs.cell_id, seeded=sim.seeded):
                out[i] = source_raw_decision(sim.fn, obs.query, channel=channel)
                continue
            model_obs.append(obs)
            model_idx.append(i)
            model_seeds.append(int(seeds[i]))
            model_order.append(int(order[i]))
            sim.model_call_counts[obs.cell_id] = (
                sim.model_call_counts.get(obs.cell_id, 0) + 1
            )

        if not model_obs:
            return [r if r is not None else "" for r in out]

        inner = sim._inner_completer
        if inner is None:
            for i, obs in zip(model_idx, model_obs, strict=True):
                inbox = [m for m in obs.inbox if m is not None]
                od = decide(obs.examples, obs.query, inbox, sim.catalog)
                from constitutional_life.cell.schema import Publish

                if od.publish_say is not None and od.signal is not None:
                    comm: Any = Publish(signal=od.signal, say=od.publish_say)
                else:
                    comm = Silence()
                out[i] = encode_decision(
                    ParsedDecision(
                        task_answer=od.answer or "AAAA",
                        inferred_rule=od.inferred_rule or "unsolved",
                        communication=comm,
                    )
                )
        else:
            # Patch while the inner Completer runs so its render_state sees
            # the same annotations that will be written to the log.
            with _patch_render_state(sim) if sim.k > 0 else _nullcontext():
                raws = inner.complete_batch(
                    model_obs,
                    channel=channel,
                    seeds=model_seeds,
                    order_seeds=model_order,
                    **kwargs,
                )
            for i, raw in zip(model_idx, raws, strict=True):
                out[i] = raw

        return [r if r is not None else "" for r in out]


class _nullcontext:
    def __enter__(self):
        return None

    def __exit__(self, *args):
        return False


@dataclass
class SimulationV1b(Simulation):
    """v1a Simulation + ``k`` check strength + optional seeded sources."""

    k: int = 0
    seeded: bool = False
    # When True with seeded=True, keep caller ``sparse`` (TASK_LIFE_REASONING_CELLS
    # arms B–D: sources publish P_e; non-sources get one non-identifying example).
    # Default False preserves v1b dense pilot / acceptance (force sparse=False).
    allow_sparse_seeded: bool = False
    check_history: list = field(default_factory=list)
    model_call_counts: dict = field(default_factory=dict)
    _inner_completer: Any = field(default=None, repr=False, compare=False)
    # Filled each step by the Completer bridge from live observations.
    _step_obs: dict = field(default_factory=dict, repr=False, compare=False)
    _step_anns: dict = field(default_factory=dict, repr=False, compare=False)

    def __post_init__(self) -> None:
        if self.k not in (0, 1, 2):
            raise ValueError(f"k must be 0, 1, or 2; got {self.k}")
        # Seeded arm default: dense identifying examples for everyone (v1b pilot).
        # Reasoning-cell sparse arms set allow_sparse_seeded=True + sparse=True.
        if self.seeded and not self.allow_sparse_seeded:
            self.sparse = False
        self._inner_completer = self.completer
        # Bridge whenever we need source bypass, Completer render patch, or
        # observation-keyed mark logging (k > 0).
        if self.seeded or self.completer is not None or self.k > 0:
            self.completer = _V1bCompleterBridge(self)  # type: ignore[assignment]
        Simulation.__post_init__(self)

    def step(self) -> Snapshot:
        self._step_obs = {}
        self._step_anns = {}
        snap = Simulation.step(self)
        self._extend_rule_history()
        return snap

    def _extend_rule_history(self) -> None:
        if not self.rule_history:
            return
        row = self.rule_history[-1]
        catalog = self.catalog
        source_mask = {
            cid: is_source(cid, seeded=self.seeded) for cid in all_cell_ids()
        }

        if self.k > 0:
            # Every non-source must have been annotated from a live observation.
            missing = [
                cid
                for cid in all_cell_ids()
                if not source_mask[cid] and cid not in self._step_anns
            ]
            if missing:
                raise AssertionError(
                    f"k={self.k}: missing step annotations for non-source cells "
                    f"{missing[:8]}{'…' if len(missing) > 8 else ''} "
                    f"(got {len(self._step_anns)}/{N_CELLS - sum(source_mask.values())})"
                )
            checks = {
                cid: _anns_to_log(anns) for cid, anns in self._step_anns.items()
            }
            # Sources may bypass Completer batches that never saw them only if
            # the engine never passed them — but the bridge always receives all
            # observations. setdefault is for sources / k=0 padding only.
            for cid in all_cell_ids():
                if cid not in checks:
                    if not source_mask[cid]:
                        raise AssertionError(
                            f"k={self.k}: non-source {cid} missing checks after assert"
                        )
                    checks[cid] = [None] * 8
        elif self._step_anns:
            checks = {
                cid: _anns_to_log(anns) for cid, anns in self._step_anns.items()
            }
            for cid in all_cell_ids():
                checks.setdefault(cid, [None] * 8)
        else:
            # No bridge this step (k=0, unseeded, completer=None): nothing to mark.
            checks = {cid: [None] * 8 for cid in all_cell_ids()}

        row["checks"] = checks
        row["source_mask"] = source_mask
        row["n_ops"] = _n_ops_for_pe(row["p_e"], catalog)
        row["k"] = self.k
        row["seeded"] = self.seeded
        self.check_history.append(
            {
                "generation": row["generation"],
                "epoch": row["epoch"],
                "checks": checks,
            }
        )

    def render_obs(self, obs: CellObservation, *, channel: bool | None = None) -> str:
        """Render one observation under this sim's ``k`` (for inspection / tests)."""
        ch = self.channel if channel is None else channel
        anns = annotate_inbox(
            examples=obs.examples,
            inbox=obs.inbox,
            k=self.k,
            world_seed=self.world_seed,
            generation=obs.generation,
            cell_id=obs.cell_id,
            catalog=self.catalog,
        )
        return render_state_v1b(obs, channel=ch, k=self.k, annotations=anns)

    def source_ids(self) -> tuple[int, ...]:
        return SOURCE_IDS if self.seeded else ()
