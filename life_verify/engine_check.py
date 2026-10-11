"""Engine-check appendix for L-VERIFY pair probes (Luna / Decisions battery)."""
from __future__ import annotations

import life_verify.env as LV


def engine_check_lines(inst: LV.InstanceLV) -> list[str]:
    """One line per named inbox rule: apply to private examples with ✓/✗."""
    lines = []
    for idx in LV.named_indices(inst):
        fn = LV._CAT.functions[idx]
        bits = []
        ok_all = True
        for x, y in inst.examples:
            yhat = fn.apply(x)
            hit = yhat == y
            ok_all = ok_all and hit
            bits.append(f"{x}→{yhat} {'✓' if hit else '✗'}")
        tag = (
            "consistent with your examples"
            if ok_all
            else "inconsistent with your examples"
        )
        lines.append(
            f"- {fn.description()}: {', '.join(bits)}  ({tag})"
        )
    return lines


def render_with_engine_check(
    inst: LV.InstanceLV, *, base: str | None = None
) -> str:
    """Canonical Life state + engine_check_v1 appendix."""
    if base is None:
        base = LV.render_state_lv(inst)
    appendix = [
        "",
        "## Engine checks on named inbox rules (probe surface engine_check_v1)",
        "For each transformation named in your visible messages, the engine applied",
        "it to your private examples. ✓ means the output matches the example; ✗ means it does not.",
        "Use these checks when choosing the hidden transformation.",
        *engine_check_lines(inst),
    ]
    return base + "\n".join(appendix)
