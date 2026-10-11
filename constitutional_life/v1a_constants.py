"""Frozen v1a constants. Numbers from the enumerator preflight, not guesses.

Overrides CLAUDE.md where this file and that note disagree
(centered regions; why dropped; n_examples measured).
"""

from __future__ import annotations

# Task family — enumerator output, seed 20260830, trials=80
ALPHABET = "ABCDEFGH"
L = 4
N_SYNTACTIC_PROGRAMS = 420
N_CANONICAL_FUNCTIONS = 101
N_ONE_OP = 17
N_TWO_OP = 84
N_IDENTITY = 1
N_EXAMPLES = 2  # min n with P(|H(E)|=1) ≥ 0.95 over random (f, E)
MAX_EXAMPLE_RESAMPLES = 100
SAY_BYTE_LIMIT = 96
MAX_CANONICAL_DESCRIPTION_BYTES = 31

# Board
GRID = 10  # wrapping GRID×GRID torus; 100 cells, max Chebyshev distance 5
READ_BUDGET = 8
WRITES_PER_CELL = 1
TTL_LOCAL = 1
TTL_REGIONAL = 3
TTL_GLOBAL = 3
REGION_RADIUS = 2  # Moore radius around the reader; local ⊂ regional ⊂ global
MESSAGE_TTL_BY_SUBSTRATE = {
    "local": TTL_LOCAL,
    "regional": TTL_REGIONAL,
    "global": TTL_GLOBAL,
}
EPOCH_LENGTH = 10
MEMORY_DEPTH = 1
SCHEMA_VERSION = 1
MAX_OUTPUT_TOKENS = 256

# Cell backend. Jev models first; generative LLM cells come later.
#   openjev  — AlexWortega/openjev served by SGLang (/classify), on the DGX
#   typesafe — TypeSafe Jev API (/v1/systemone), key in $TYPESAFE_API_KEY
#   llm      — generative model via SGLang chat + GBNF (below)
BACKEND = "openjev"

# Jev cells return a probability per option; nothing is generated.
OPENJEV_BASE_URL = "http://192.168.78.32:30000"
OPENJEV_MODEL = "AlexWortega/openjev/qwen3.5-4b-nli-v5"  # label only; the server holds the weights
OPENJEV_CLASSIFY_BATCH = 32  # pairs per /classify call
TYPESAFE_BASE_URL = "https://api.typesafe.ai"
TYPESAFE_MODEL = "jev-1.13.0"  # pinned, not jev-latest
TYPESAFE_API_KEY_ENV = "TYPESAFE_API_KEY"
# Legacy name still used in some local .env files; checked after TYPESAFE_API_KEY.
TYPESAFE_API_KEY_ENV_FALLBACK = "JEV_API_KEY"
JEV_TIMEOUT_S = 120.0
JEV_MAX_WORKERS = 8
# sample: draw each choice from the returned distribution with the cell's
# inference seed (keeps replay K>1 meaningful). argmax: deterministic.
JEV_DECODE = "sample"

# Inference — generative LLM via SGLang
MODEL_ID = "Qwen/Qwen3.6-35B-A3B-FP8"
TEMPERATURE = 0.7  # > 0; same value for trajectory and replay
SGLANG_BASE_URL = "http://192.168.78.32:30000"
INFERENCE_TIMEOUT_S = 180.0
# One in-flight request. Parallel calls do not fix a stalled SGLang; they
# hide which cell hung and reset the socket after a few generations.
INFERENCE_MAX_WORKERS = 1

# Decision schema — v1a
# communication = silence | publish(signal: 0..7, say: ≤96 UTF-8 bytes)
# why is absent. inferred_rule is mandatory and log-only.
SIGNAL_VALUES = range(8)

# Replay
SNAPSHOT_RULE = "mid_epoch_and_last_generation"
# 5 epochs → 10 snapshots
REPLAY_K = 50

# Cascade locks (TypeSafe endpoints). A lock is not "modal ≠ P_e":
# at weak solo accuracy the mode is almost always wrong. Require majority
# convergence first. Declared before the registered run; silent-arm false-lock
# rate near zero is a definition check (independent cells cannot cascade).
FALSE_LOCK_MODAL_SHARE = 0.5  # also the share threshold for true_lock
# Sizing priors for the registered TypeSafe n (content MDE, not pilot direction):
# local false-lock base ≈ 0.02; interesting global rate = 0.15. See V1A_FREEZE.
CASCADE_MDE_LOCAL = 0.02
CASCADE_MDE_GLOBAL = 0.15
# Per substrate arm. Sized for epoch-fraction primary under moderate within-run
# epoch correlation (design effect); see V1A_FREEZE. No optional stopping.
CASCADE_REGISTERED_N = 50
# Registered TypeSafe trajectory length: 4 epochs × EPOCH_LENGTH (matches the
# E=4 row of the design-effect table used to size n).
CASCADE_REGISTERED_EPOCHS = 4
# Confirmatory arms (declared): silent + L/R/G true + G permuted only.
# Local/regional permuted are secondary; add only in a pre-declared follow-up.
CASCADE_REGISTERED_ARMS = (
    "silent",
    "local_true",
    "regional_true",
    "global_true",
    "global_permuted",
)
