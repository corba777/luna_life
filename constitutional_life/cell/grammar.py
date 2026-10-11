"""GBNF for constrained decoding. The parser in schema.py remains the outcome.

SGLang can take this as `ebnf` / GBNF. Unbounded strings are not allowed:
`inferred_rule` and `say` are capped at 96 characters of printable JSON
string content. The Python parser re-checks the UTF-8 byte limit.
"""

from __future__ import annotations

from constitutional_life.v1a_constants import SAY_BYTE_LIMIT

_CHAR_CLASS = r"[^\"\\\x00-\x1F]"


def _grammar(body: str) -> str:
    return body.strip().replace("CHAR", _CHAR_CLASS).replace(
        "NMAX", str(SAY_BYTE_LIMIT)
    )


GRAMMAR_CHANNEL = _grammar(
    r"""
root ::= "{" ws "\"task_answer\"" ws ":" ws answer ws "," ws "\"inferred_rule\"" ws ":" ws rule ws "," ws "\"communication\"" ws ":" ws comm ws "}"
ws ::= [ \t\n]*
answer ::= "\"" [A-H] [A-H] [A-H] [A-H] "\""
rule ::= "\"" CHAR{1,NMAX} "\""
comm ::= silence | publish
silence ::= "{" ws "\"kind\"" ws ":" ws "\"silence\"" ws "}"
publish ::= "{" ws "\"kind\"" ws ":" ws "\"publish\"" ws "," ws "\"signal\"" ws ":" ws [0-7] ws "," ws "\"say\"" ws ":" ws say ws "}"
say ::= "\"" CHAR{1,NMAX} "\""
"""
)

GRAMMAR_NO_CHANNEL = _grammar(
    r"""
root ::= "{" ws "\"task_answer\"" ws ":" ws answer ws "," ws "\"inferred_rule\"" ws ":" ws rule ws "}"
ws ::= [ \t\n]*
answer ::= "\"" [A-H] [A-H] [A-H] [A-H] "\""
rule ::= "\"" CHAR{1,NMAX} "\""
"""
)


def grammar_for(channel: bool) -> str:
    return GRAMMAR_CHANNEL if channel else GRAMMAR_NO_CHANNEL
