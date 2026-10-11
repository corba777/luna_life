# Provenance

## Predictions were locked privately

The Luna modes predictions (Decisions vs Responses none/medium/high) were
written and committed **before** any Responses evaluation numbers existed.
Those original commits live in a **private** research repository
(`corba777/multi_agent_jev`). That repository is not public; anonymous
requests return 404.

The original lock commit SHA (still only in the private repo) is:

```
60564e8474afeb55ba1a07de27c31f849472782f
```

Subject: `Lock Luna Decisions vs Responses modes (none/medium/high), budget $50.`
Author date: 2026-10-09 02:16:45 −0400.

**Verification of the private history is available on request** (maintainer
can show the private commit / signed statement). Public readers cannot clone
it themselves.

## What is public in this repository

| Object | Role |
|---|---|
| Tag [`prereg-luna-modes-lock`](https://github.com/corba777/luna_life/tree/prereg-luna-modes-lock) | Slim **orphan witness**: only `TASK_LUNA_REASONING_MODES.md` (bytes as locked) plus `ORIGINAL_COMMIT.txt` (records the private SHA and the file SHA-256). No private-repo git objects. |
| [`prereg/`](prereg/) on `main` | Readable copies of task / prediction markdown. **Secondary:** convenient for reading; they do not themselves prove pre-registration timing (they were added when this public extract was assembled). |
| [`artifacts/`](artifacts/) | Aggregate results. Extracts for the paper numbers; not the preregistration event. |

### Verify the witness file

```bash
git fetch origin tag prereg-luna-modes-lock
git show prereg-luna-modes-lock:ORIGINAL_COMMIT.txt
shasum -a 256 <(git show prereg-luna-modes-lock:TASK_LUNA_REASONING_MODES.md)
```

## Repository recreation

This public repository was **recreated from a clean `git archive` of the
intended tree** after a mistaken tag briefly referenced a private-repo SHA.
The new git history starts at a single root commit and does not contain
objects from `multi_agent_jev`.
