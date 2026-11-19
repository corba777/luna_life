# Recheck — QX-3 main phase, gpt-oss-20b: Family B and T-M (2026-11-19)

Packages: `qx3_20b_family_b_artem_recheck_2026-11-19.zip` (sha256 `e3f179e0…1bc4`, SHA256SUMS 28,816 files OK)
and `qx3_20b_majority_artem_recheck_2026-11-19.zip` (sha256 `96286234…a3be`, 12/12 OK). Amendments
`AMENDMENT_QX3_MAIN.md` locked v3 and `AMENDMENT_QX3_20B_MAJORITY.md` locked v2 (locked before any r2–r5
rule-only trace was read for it). Recomputed with `fb_check.py` and `tm_check.py` (own code). H_T at δ = 1/8
rebuilt independently; every stored test output, own and received, equals it. Every number in the agent's
readouts reproduces.

## Family B — gpt-oss-20b · δ 1/8 · B 1 · world 0, runs r2–r5

| arm | x̄ | x̄_nf | finders independent / following |
|---|---|---|---|
| rule only | 0.154, 0.273, 0.321, 0.192 | 0.006, 0.008, 0.012, 0.006 | 23/0, 39/0, 45/0, 35/0 |
| + chosen result | 0.418, 0.353, 0.765, 0.603 | 0.263, 0.104, 0.353, 0.284 | 17/7, 34/4, 39/11, 32/9 |
| + attached result | 0.900, 0.857, 0.854, 0.784 | 0.553, 0.604, 0.574, 0.544 | 3/33, 7/21, 2/29, 4/24 |

- **B1** (chosen above rule only) p = 1/70, **B2** (attached above chosen) p = 1/70, **B3** (attached above rule
  only) p = 1/70: all three **hold** at 0.0167. Predictions were B1 and B3 uncertain, B2 none.
- Sharing (refuting result attached, among messages of cells holding one): chosen 16/705, 13/720, 39/1556,
  25/1129 (≈ 2 %); attached 100 %; rule only 0.
- 0 fallbacks, 0 truncations, all runs 24 × 100 and not partial.

Reading, as stated in advance: for gpt-oss-20b the gap between rule only and rule plus evidence is complete
across four runs, and attached evidence beats the model's own sharing in every run: the sender is a limit.

## T-M — gpt-oss-20b against Luna, p_high at five or more naming neighbours

| run | gpt-oss-20b p_high | 1–4 | Luna run | Luna p_high | 1–4 |
|---|---:|---:|---|---:|---:|
| r2 | 0/5 | 1/88 | r2 | 32/32 | 0/65 |
| r3 | 1/19 | 0/93 | r3 | 32/36 | 0/69 |
| r4 | 0/16 | 0/93 | r4 | 37/42 | 0/73 |
| r5 | 0/15 | 1/89 | r5 | 36/38 | 1/69 |
| | | | r6 | 29/35 | 0/54 |

No run excluded (each ≥ 5 cells at five or more). **T-M holds**, p = 1/126, as predicted. Pooled gpt-oss-20b:
1 of 55 cells left H_F at five or more naming neighbours, 2 of 363 at one to four. Reading: gpt-oss-20b does
not follow a majority of rule names; the majority step is a property of Luna, not of the setup.
