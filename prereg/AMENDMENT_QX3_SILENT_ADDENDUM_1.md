# Addendum 1 — QX-3 silent: the S-L stop

**Status:** locked (2026-11-19), on Artem's go: "GO to complete".
Written before any S-L result was read. No trace was opened. The parent
`AMENDMENT_QX3_SILENT.md` stays locked v2; this addendum changes one number in it.

## The one change

The S-L hard stop rises from **$5.00 to $6.00**.

The measured cost of a silent run is $1.19. The projection used by the start rule is $1.06.
After w0, w1 and w2 the amendment's spend is $3.5690, so the unchanged start rule asks for
$3.5690 + 1.5 × $1.06 = $5.159 before w3. That is above $5.00 and at most $6.00, which is
why w3 did not start and why this stop is enough for it to start.

Everything else stays as locked:

- The start rule is unchanged: this amendment's spend so far plus 1.5 × the run's projected
  cost ($1.06) is at most the hard stop, and all Luna spend stays within the $45.00
  authorization with the why-probe's $2.00 and the withhold probe's $0.60 still unspent.
- S-O, the tests, the predictions and the parent text are unchanged.
- w0, w1 and w2 are not re-run. Their traces stay on file and are skipped.

## Projected Luna spend after w3

Prior Luna spend at the silent start, from the runner's start line: $36.9524.
Silent spend after three runs, from the runner's log: $3.5690.
w3 is projected at the measured $1.19, not at $1.06.

| | USD |
|---|---:|
| Prior Luna spend | 36.9524 |
| S-L after w3 ($3.5690 + $1.19) | 4.7590 |
| **Total Luna spend after w3** | **41.7114** |
| Why-probe, still unspent | 2.00 |
| Withhold probe, still unspent | 0.60 |
| Total with both reserves | 44.3114 |
| Authorization | 45.00 |

$41.71 of $45.00 after w3. Both reserves stay unspent, and $0.69 of the authorization remains
beyond them. The start check for w3 itself still uses $1.06:
$36.9524 + $3.5690 + $1.06 = $41.5814, against $45.00 − $2.60 = $42.40.
