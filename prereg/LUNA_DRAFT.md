# Same Weights, Three Ways to Answer

Oct 9, 2026 · @Artem Zvyagintsev

<!-- REVIEW: Opening uses rounded 1% for false-follow; exact high 2-op is 1.2% (1/84). Keep 1% for the lead if you want; Results / caveats can stay exact. -->

Asked to pick one option in a single pass, a frontier model cannot check a two-step rule (59% on pairs, near chance) and follows a false rule it is told 76% of the time. Let the same model think for a few hundred tokens and it checks almost perfectly (100%) and follows the false rule only 1% of the time. Without thinking, switching APIs changes nothing.

## The setup

The task is to check a rule against evidence. A hidden transformation maps 4-symbol strings over A–H to other strings, and the model sees a few input → output examples. The catalog has 101 candidate rules: 17 single operations (`reverse`, `rotate_left(k)`, `shift_symbols(k)`, `swap(i,j)`) and 84 compositions of two, such as `shift_symbols(1);swap(1,2)`.

Three tests, all on held-out rules:

1. **Pairs.** One true and one false candidate rule, named; does the model prefer the true one? 200 pairs, 100 single-op and 100 two-op. Chance is 50%.
2. **Told a lie.** A message names a false rule as the answer; does the model follow it, or recover the true rule from its examples? 84 two-op cases.
3. **Pragmatic listening.** A reference game where the right answer depends on what the speaker would have said instead (46 instances, 153 words). Scored against an ideal pragmatic listener.

One model, `gpt-6-luna` (OpenAI, public beta), asked three ways:

- **Decisions API:** one choice question, the model returns a probability for every option in one pass. Averaged over 4 option orderings.
- **Responses API, reasoning off** (`effort=none`): the model writes the option key directly.
- **Responses API, reasoning on** (`effort=medium` and `high`): the model may think before writing the key.

Responses modes were sampled 8 times per question across the 4 orderings; all modes are compared on the chosen answer, not on probabilities. Predictions and pass thresholds were locked before any Responses accuracy number (public witness: [`PROVENANCE.md`](../PROVENANCE.md) and tag `prereg-luna-modes-lock`), including a control: without reasoning, the API should not matter.

<!-- REVIEW: Lock = TASK_LUNA predictions + $50 budget before Responses numbers. Cite PROVENANCE / prereg-luna-modes-lock, not a private-repo URL. Close status on TASK_LUNA was updated after CIs; the *predictions* remain those of the lock. -->

## Results

*[Figure: three panels — two-op pairs / told a lie / pragmatic listening — Decisions vs Responses none / medium / high, with honest cluster CIs. Source: `runs/openai_decisions/luna_modes.json` + `luna_modes_cis_fixed.json`, gpt-6-luna public beta, Oct 2026.]*

Paired cluster-bootstrap intervals against Decisions: reasoning high +0.41 \[+0.32, +0.50\] on two-op pairs, reasoning off +0.01 \[−0.06, +0.08\], and +0.35 \[+0.27, +0.44\] on pragmatic listening. Medium and high sit within two points of each other everywhere, so the effect saturates after a few hundred tokens.

<!-- REVIEW — GLiDE naming (your call):
  Numbers are correct: same Part-B subset, GLiDE pragmatic_argmax_L2 = 0.817, Luna high = 0.967.
  For a public post that is “one model, three interfaces,” naming another vendor is optional.
  Prefer A for Medium; keep B if you want the ladder placement. -->

<!-- Option A (no external model): omit the next sentence. -->
<!-- Option B (keep): -->
On pragmatic listening, reasoning also clears the best prior model we had tested on the same subset (GLiDE at 82%).

<!-- POST GATE: do not publish until TASK_LUNA_DEPTH (3-op curve) is closed — or D2 fails
     and that failure is written here. Results figure becomes depth × mode. -->

## What it means

The knowledge is in the weights; in one pass, this model does not use it for two-step checks.
Checking a two-op rule means applying the first operation, holding the intermediate string,
applying the second and comparing. Under the Decisions / no-reasoning interface, Luna does
not do that. A few hundred tokens of reasoning and it does. This is a limit of the **mode as
observed**, not a proof that one pass cannot compose: a transformer has many layers inside
one forward pass, and models can in principle compose internally. Whether training can teach
a one-pass decision head to take that intermediate step is an open question — exactly our
Part C.

Three observations point the same way:

- **Single operations are fine without reasoning.** On single-op pairs Decisions already scores 94%. The failure shows up at composition (two points so far; a 3-op depth point is queued — `TASK_LUNA_DEPTH.md`).
- **The control holds.** Reasoning off, Responses − Decisions on two-op pairs is +0.01 \[−0.06, +0.08\]. The gain comes from thinking, not from a different API.
- **An external step works as well as an internal one.** When the environment attaches a ready-made ✓/✗ check to each candidate rule, the same one-pass model goes from 65% to 99.5% on picking the rule from the full catalog. Someone has to do the intermediate step; it does not matter much who.

Dose saturates early on two-op: medium (mean ~460 reasoning tokens on pairs overall; ~690 on the two-op stratum) is already at the ceiling. Whether that budget still covers three steps is what the depth curve answers.

<!-- REVIEW: Draft had “~460 on pairs” — that is pooled 1-op+2-op. Two-op medium mean is ~689. Both support “a few hundred tokens”; I made the split explicit so a reader who only cares about composition is not misled. -->

## Caveats

- **One model, one task family.** String transformations over a 101-rule catalog. Other domains may need more or fewer steps.
- **Public beta.** `gpt-6-luna` and the Decisions API may change before release. How Decisions mode is built internally is not documented, so I make no claim about it beyond what it outputs.
- **Different estimators.** Decisions returns probabilities; Responses modes are estimated from 8 samples, with ties scored as half. That is why every comparison is on the chosen answer.
- **Small held-out sets.** Intervals are cluster bootstraps over the 26 held-out two-op functions (pairs) or the 46 instances (pragmatic listening).
- **Validity.** 0 invalid answers with reasoning off or medium; 1 truncated answer out of 1,600 at high, where reasoning hit the 8,192-token cap.

## Why this matters for multi-agent work

I study whether a population of decision-model agents on a 10×10 grid can spread a correct rule by messaging each other. An agent that follows whatever its neighbours say spreads errors as easily as truths; spreading the truth needs agents that check claims against their own evidence.

These results say one-pass decision models, small or frontier, do not check two-step claims, while the same weights with a little reasoning do. That splits the next steps into two routes:

- **Verify from outside:** the environment attaches checks to messages (our engine-check stand).
- **Verify from inside:** agents that reason, or decision models trained to make the intermediate step within one pass.

The next experiment puts both on the same grid, with each agent given too little evidence to find the rule alone. If the right rule spreads there, the population is computing something no single agent can.

<!-- REVIEW: Life section stays number-free — good. Do not add v1b pilot numbers until that close is written. -->
