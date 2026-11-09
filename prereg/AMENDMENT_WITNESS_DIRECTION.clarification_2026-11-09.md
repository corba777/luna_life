# Witness direction — clarification of fidelity gate (iii)

Written 2026-11-09 (Artem), **before any Stage 1 call**: no forward pass, no generated call, no
activation read. The locked amendment `AMENDMENT_WITNESS_DIRECTION.md` (sha256
`3cf91f25e5de29aaf40973f9c032ef3a06e71bad89fc16d0dbe1d971aca3b68c`) is unchanged; this note states how
one of its sentences is applied.

## The locked sentence

> (iii) At α = 0 every final answer is valid JSON conforming to the schema (580 / 580).

with the consequence

> if (iii) fails, the constrained engine is not faithful and Stage 1b does not run.

## Clarification (verbatim)

> Clarification (Artem, 2026-11-09, before any Stage 1 call): gate (iii) applies to calls that close
> </think> and stop; it fails if any such call is invalid, or if any call ends with EOS inside
> reasoning. Truncated α = 0 calls are reported by count in fidelity.json, do not fail (iii), and count
> as non-adoption and non-fit in every measure, as in the battery. Nothing else changes.

Reason given with it: gate (iii)'s stated purpose is the engine's faithfulness, and a call truncated at
max_tokens has no final answer and is not an engine fault.

## What does not change

- The scale-pilot rule, which names truncation explicitly ("A step passes if invalid-JSON share ≤ 5 %
  and no answer is truncated at max_tokens"), stays as locked.
- Gate (ii), the arms, the measures and the predictions are unchanged. A truncated call was already
  scored as non-adoption and non-fit, as in the stored battery (0 of its 1,400 Stage 1 draws were
  truncated).

## Run it applies to

The run that implements this reading is queue v22c, manifest sha256
`cdc56b34283383934d88d077881b3e289a0f9dc028ce108da5c0753beb4b0922` (same files as the previous
manifest; changed only the runner, the readout and the dry check). Before launch the dry check passed
four simulated α = 0 cases:
- a call truncated inside reasoning, and one truncated after `</think>`, both pass (iii), are counted as
  truncated and score non-adoption / non-fit;
- an invalid call that closed `</think>` and stopped fails (iii);
- a call ending with EOS inside reasoning fails (iii).
