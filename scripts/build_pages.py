#!/usr/bin/env python3
"""Build docs/index.html from article/Luna.md for GitHub Pages."""
from __future__ import annotations

import html
import json
import re
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parents[1]
MD = ROOT / "article" / "Luna.md"
OUT = ROOT / "docs" / "index.html"
MODES = ROOT / "artifacts" / "openai_decisions" / "luna_modes.json"
DEPTH = ROOT / "artifacts" / "openai_decisions" / "luna_depth.json"


def load_chart_data() -> dict:
    modes = json.loads(MODES.read_text())
    depth = json.loads(DEPTH.read_text())
    c = modes["contrasts"]
    dc = depth["depth_curve"]
    return {
        "pairs": {
            "decisions": c["high_minus_decisions_2op"]["dec_mean_2op"],
            "none": c["R0_points"]["none"],
            "medium": c["R0_points"]["medium"],
            "high": c["R0_points"]["high"],
        },
        "pragmatic": {
            "decisions": c["high_minus_decisions_e1p"]["dec_mean"],
            "none": c["none_minus_decisions_e1p"]["resp_mean"],
            "medium": c["medium_minus_decisions_e1p"]["resp_mean"],
            "high": c["high_minus_decisions_e1p"]["resp_mean"],
        },
        "depth": {
            "decisions": [dc["decisions"]["1"], dc["decisions"]["2"], dc["decisions"]["3"]],
            "none": [dc["resp_none"]["1"], dc["resp_none"]["2"], dc["resp_none"]["3"]],
            "medium": [dc["resp_medium"]["1"], dc["resp_medium"]["2"], dc["resp_medium"]["3"]],
            "tokens": [
                dc["resp_medium"]["mean_reasoning_1"],
                dc["resp_medium"]["mean_reasoning_2"],
                dc["resp_medium"]["mean_reasoning_3"],
            ],
        },
        "deltas": {
            "high_pairs": c["high_minus_decisions_2op"],
            "none_pairs": c["none_minus_decisions_2op"],
            "high_prg": c["high_minus_decisions_e1p"],
        },
    }


def preprocess_md(text: str) -> str:
    # Drop empty leading H1
    text = re.sub(r"^#\s*\n+", "", text)
    # Decode HTML entity brackets used in the source
    text = text.replace("&#91;", "[").replace("&#93;", "]")
    text = text.replace(r"\_", "_")
    text = text.replace(r"\~", "~")
    text = text.replace(r"\[", "[").replace(r"\]", "]")

    modes_fig = """
<div class="figure" id="fig-modes">
  <div class="figure-head">
    <span class="figure-label">Figure 1</span>
    <span class="figure-meta">gpt-6-luna · Oct 2026 · pairs n=100 two-op · pragmatic 46 / 153</span>
  </div>
  <div class="chart-grid">
    <div class="chart-panel">
      <h3>Two-op pair preference</h3>
      <div class="bars" data-chart="pairs"></div>
      <p class="chance">chance = 0.50</p>
    </div>
    <div class="chart-panel">
      <h3>Pragmatic listening</h3>
      <div class="bars" data-chart="pragmatic"></div>
    </div>
    <div class="chart-panel wide">
      <h3>Accuracy vs composition depth</h3>
      <div class="depth" data-chart="depth"></div>
      <p class="chance">Reasoning tokens (medium): ~227 → 689 → 1,349</p>
    </div>
  </div>
  <p class="caption">Bars are choice accuracy. Decisions = one-pass API; none / medium / high = Responses reasoning effort.</p>
</div>
"""
    grid_fig = """
<figure class="figure photo">
  <div class="figure-head">
    <span class="figure-label">Figure 2</span>
    <span class="figure-meta">J by generation · 5 seeds · 95% bootstrap bands</span>
  </div>
  <img src="assets/fig_j_by_gen.png" alt="Share of non-source cells holding the true rule by generation, one-op and two-op panels" width="1200" height="640" loading="lazy" />
  <figcaption>Share of non-source cells holding the true rule, by generation. “Silent” = no channel; “one-pass” = Decisions API; “+ check” = engine ✓/✗ on incoming rules. Dashed line = topological reachability bound.</figcaption>
</figure>
"""
    text = re.sub(
        r"\[embedded content:[^\]]+\]\s*",
        modes_fig,
        text,
        count=1,
    )
    text = re.sub(
        r"\[image:[^\]]+\]\s*",
        grid_fig,
        text,
        count=1,
    )
    return text


def split_title(body_html: str) -> tuple[str, str, str, str]:
    """Pull first h1 / italic dek / meta line out for the hero."""
    # markdown makes <h1>…</h1>
    m = re.search(r"<h1>(.*?)</h1>\s*", body_html, re.S)
    title = m.group(1).strip() if m else "Same Weights, Three Ways to Answer"
    rest = body_html[m.end() :] if m else body_html

    dek = ""
    m2 = re.search(r"<p><em>(.*?)</em></p>\s*", rest, re.S)
    if m2:
        dek = m2.group(1).strip()
        rest = rest[: m2.start()] + rest[m2.end() :]

    meta = ""
    m3 = re.search(r"<p>(Oct [^<]+)</p>\s*", rest)
    if m3:
        meta = m3.group(1).strip()
        rest = rest[: m3.start()] + rest[m3.end() :]

    return title, dek, meta, rest


def page(title: str, dek: str, meta: str, body: str, data: dict) -> str:
    data_json = html.escape(json.dumps(data), quote=True)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{html.escape(re.sub("<.*?>", "", title))} · luna_life</title>
  <meta name="description" content="{html.escape(re.sub("<.*?>", "", dek) or "gpt-6-luna Decisions vs Responses and Life-grid cells")}" />
  <meta name="author" content="Artem Zvyagintsev" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=Sora:wght@500;600;700&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="styles.css" />
</head>
<body>
  <div class="bg" aria-hidden="true"></div>
  <header class="top">
    <a class="mark" href="https://github.com/corba777/luna_life">luna_life</a>
    <nav>
      <a href="https://github.com/corba777/luna_life">Code</a>
      <a href="https://github.com/corba777/luna_life/blob/main/article/Luna.md">Source</a>
      <a href="https://github.com/corba777/luna_life/tree/main/artifacts">Artifacts</a>
    </nav>
  </header>

  <main>
    <article>
      <header class="hero">
        <p class="eyebrow">Research note · OpenAI gpt-6-luna</p>
        <h1>{title}</h1>
        {f'<p class="dek">{dek}</p>' if dek else ""}
        {f'<p class="meta">{html.escape(meta)}</p>' if meta else ""}
      </header>

      <div class="prose">
{body}
      </div>
    </article>
  </main>

  <footer class="foot">
    <p>MIT · <a href="https://github.com/corba777/luna_life">corba777/luna_life</a> · numbers from committed aggregates under <code>artifacts/</code></p>
  </footer>

  <script id="chart-data" type="application/json">{json.dumps(data)}</script>
  <script src="charts.js"></script>
</body>
</html>
"""


def main() -> None:
    raw = MD.read_text()
    md = preprocess_md(raw)
    body = markdown.markdown(
        md,
        extensions=["tables", "fenced_code", "smarty"],
    )
    title, dek, meta, rest = split_title(body)
    # Wrap bare markdown images (not already inside <figure>) in figure.photo
    # so they share Figure 2's card + width:100% CSS instead of native 1800px.
    def _wrap_md_img(m: re.Match[str]) -> str:
        img = m.group(1)
        if "width=" not in img:
            img = img.replace("<img ", '<img width="1200" ', 1)
        return (
            '<figure class="figure photo">'
            f"{img}"
            "</figure>"
        )

    rest = re.sub(
        r"<p>(<img\s[^>]*src=\"assets/[^\"]+\"[^>]*/?>)</p>",
        _wrap_md_img,
        rest,
    )
    data = load_chart_data()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(page(title, dek, meta, rest, data))
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
