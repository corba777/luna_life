<p align="center">
  <img src="docs/assets/banner.png" alt="luna_life — decisions · reasoning modes · life grid" width="920" />
</p>

<p align="center"><em>same weights, three ways to answer — and a grid that only works when someone checks</em></p>

<p align="center">
  <img src="docs/assets/fig_world_schematic.png" alt="A 10×10 grid of agents; one 3×3 neighbourhood highlighted; a blue cell whose example fits two rules and an orange neighbour whose example rules one out and sends only the rule name." width="720" />
</p>
<p align="center"><em>Illustration: the examples are made up for the picture; the rule is the true rule of one of the five worlds. — <a href="https://corba777.github.io/luna_life/what_none_of_them_knew.html">What None of Them Knew</a></em></p>

<p align="center">
  <b>Frontier decision model vs the same model with reasoning.</b>
  One-pass <code>gpt-6-luna</code> fails two-step rule checks; a few hundred reasoning tokens fix it.
  On a 10×10 Life grid, the true rule spreads only when cells can verify neighbours — by thinking, or with an engine ✓/✗.
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-3fb950?labelColor=24292f" alt="license MIT" /></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-%E2%89%A53.11-3572A5?labelColor=24292f" alt="python >=3.11" /></a>
  <a href="https://developers.openai.com/api/docs/guides/decisions"><img src="https://img.shields.io/badge/model-gpt--6--luna-0f8a8a?labelColor=24292f" alt="gpt-6-luna" /></a>
  <img src="https://img.shields.io/badge/API-Decisions%20%7C%20Responses-0969da?labelColor=24292f" alt="Decisions | Responses" />
  <img src="https://img.shields.io/badge/envs-E1--P%20%7C%20E--HP%20%7C%20Life-1f6feb?labelColor=24292f" alt="E1-P | E-HP | Life" />
  <a href="https://corba777.github.io/luna_life/"><img src="https://img.shields.io/badge/site-GitHub%20Pages-3fb950?labelColor=24292f" alt="GitHub Pages" /></a>
</p>

<p align="center">
  <a href="#summary">Summary</a> ·
  <a href="https://corba777.github.io/luna_life/">Article site</a> ·
  <a href="article/Luna.md">Source note</a> ·
  <a href="#setup">Setup</a> ·
  <a href="#reproduce-live-api--costs-money">Reproduce</a> ·
  <a href="#paper-numbers-without-re-running">Artifacts</a> ·
  <a href="#layout">Layout</a>
</p>

---

## Summary

Short research note on **OpenAI `gpt-6-luna`** (public beta): the same weights asked three ways — **Decisions** (one-pass choice probabilities), **Responses** with reasoning off (`effort=none`), and **Responses** with reasoning on (`medium` / `high`).

**Single-agent.** Checking a two-step string transformation is near chance in one pass (~59% on two-op pairs; ~76% follow a named false rule). With a few hundred reasoning tokens the same model is essentially perfect on pairs and almost never follows the lie. Turning reasoning off, Decisions and Responses agree — so the gain is from thinking, not from switching APIs. Accuracy does not slope off with depth: it cliffs at the first composition (1-op ~94% → 2-op ~59% → 3-op ~52% for Decisions), while reasoning stays at the ceiling and token use roughly doubles per added step. An *external* intermediate step matches an internal one: engine ✓/✗ marks, or an explicit recursive listener on E1-P, lift one-pass performance without a reasoning trace.

**Multi-agent (Life grid).** One hundred copies on a 10×10 torus; most cells see too little evidence to identify the rule alone. Two-step rules spread only when incoming claims are checked — by the cell’s own reasoning, or by an engine check attached to messages. A channel without a check passes errors with truths. Identical agents can also lock onto the same *wrong* simple rule without talking; agreement alone is not evidence of communication. An [Oct 11 update](article/Luna.md#update-oct-11-2026-does-the-grid-need-a-teacher) shows that for reasoning cells a seeded teacher is not required: with zero sources, all five two-op populations still converge on the true rule.

Preregistration for the modes contrast is witnessed by tag [`prereg-luna-modes-lock`](https://github.com/corba777/luna_life/tree/prereg-luna-modes-lock) (slim public extract of the locked task file; original SHA recorded in [PROVENANCE.md](PROVENANCE.md)). Files under `prereg/` on `main` are secondary copies for reading.

**This repo** ships the article, aggregate numbers, and API-only reproduction code (E1-P / E-HP for Luna, L-VERIFY, depth curve, Life arms). No training / LoRA. Narrative: [What None of Them Knew](https://corba777.github.io/luna_life/what_none_of_them_knew.html) · source note: [`article/Luna.md`](article/Luna.md) · rendered site: https://corba777.github.io/luna_life/

---

## Setup

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[plot,stats]"   # plot/stats optional
export OPENAI_API_KEY=sk-...     # required for live API runs; never commit a .env
```

Python ≥ 3.11. No GPU. Set `OPENAI_API_KEY` in the environment only (see `.env.example`). Clients do **not** load `.env` files.

## Layout

| Path | Contents |
|---|---|
| `article/` | Published note (`Luna.md`, `Luna.pdf`) |
| `artifacts/` | Aggregate JSON (+ grid figure); no API caches, no per-seed trajectories |
| `docs/` | GitHub Pages site (`index.html` built from the article) |
| `prereg/` | Locked task / prediction writeups |
| `scripts/` | Eval / Life runners + `build_pages.py` |
| `openai_decisions_client.py`, `openai_responses_luna.py` | API clients |
| `e1_env.py`, `typesafe_policy.py` | E1-P / E-HP environments + P=4 policy wrapper |
| `life_verify/` | L-VERIFY pairs, depth-3 set, v1b Life wrapper, Luna cells |
| `constitutional_life/` | Vendored Life surface (catalog, prompts, board, sim) |

## Reproduce (live API — costs money)

From the repo root (`PYTHONPATH=.`):

```bash
# Decisions battery: E1-P + E-HP v2.1 + L-VERIFY pairs (+ optional engine-check / Part-2)
python scripts/eval_openai_decisions_battery.py --n 100 --pairs --engine-check

# Part-2 probe (told-a-lie / named contrast)
python scripts/eval_openai_luna_part2_probe.py

# Decisions vs Responses modes (reuses Decisions artifacts; runs Responses)
python scripts/eval_luna_reasoning_modes.py

# Honest CIs (cache-friendly recompute)
python scripts/recompute_luna_modes_cis.py

# 3-op depth curve
python scripts/luna_depth_generator_check.py
python scripts/eval_luna_depth.py

# Life reasoning cells (arms A / B / Bs / Ca / Da / …)
python scripts/run_life_reasoning_cells.py --help

# Long chain / zero-source (1 source or 0 sources; see prereg/)
python scripts/run_life_long_chain.py --arms B0 --cost-cap 5 --max-workers 16
```

Artifact defaults write under `artifacts/`. Disk caches go to `artifacts/cache/` (gitignored).

## Paper numbers without re-running

Aggregate results already in `artifacts/`:

- `artifacts/openai_decisions/luna_modes.json` + `luna_modes_cis_fixed.json` — mode contrasts
- `artifacts/openai_decisions/luna_depth.json` — 1/2/3-op curve
- `artifacts/openai_decisions/eval_openai_decisions_battery.json` — E1-P / E-HP / pairs
- `artifacts/openai_decisions/luna_part2_probe.json` — told-a-lie
- `artifacts/life_reasoning_cells/summary_*.json`, `fig_j_by_gen.{json,png}` — grid
- `artifacts/life_long_chain/summary.json`, `fig_wave.png` — zero-/one-source update (Oct 11)
- `artifacts/recursive_listener/summary.json` — explicit recursive listener on E1-P

Per-question `rows` were stripped from large mode/depth dumps; summaries and CIs remain.

## Site

GitHub Pages serves `docs/` (from `article/Luna.md`). Rebuild after editing the article:

```bash
pip install markdown
python scripts/build_pages.py
```

## License

MIT — see [LICENSE](LICENSE).

`gpt-6-luna` and the Decisions API are OpenAI public-beta products; names and behaviour may change.
