"""One place that turns a backend name into a Completer and a policy label."""

from __future__ import annotations

from typing import Literal

from constitutional_life.model.client import SglangClient
from constitutional_life.model.jev import JevCompleter, OpenJevSGLang, TypeSafeJev
from constitutional_life.model.types import Completer
from constitutional_life.v1a_constants import (
    JEV_DECODE,
    MODEL_ID,
    OPENJEV_BASE_URL,
    OPENJEV_MODEL,
    SGLANG_BASE_URL,
    TEMPERATURE,
    TYPESAFE_BASE_URL,
    TYPESAFE_MODEL,
)

Backend = Literal["openjev", "typesafe", "llm"]
BACKENDS: tuple[Backend, ...] = ("openjev", "typesafe", "llm")


def make_completer(
    backend: Backend,
    *,
    base_url: str | None = None,
    model: str | None = None,
) -> tuple[Completer, str]:
    if backend == "llm":
        client = SglangClient(base_url=base_url or SGLANG_BASE_URL, model=model or MODEL_ID)
        return client, f"{client.model} sglang T={TEMPERATURE}"
    if backend == "openjev":
        jev = OpenJevSGLang(base_url=base_url or OPENJEV_BASE_URL, model=model or OPENJEV_MODEL)
    elif backend == "typesafe":
        jev = TypeSafeJev(base_url=base_url or TYPESAFE_BASE_URL, model=model or TYPESAFE_MODEL)
    else:
        raise ValueError(f"unknown backend {backend!r}")
    return JevCompleter(jev), f"{jev.model} {backend} {JEV_DECODE}"


def describe(completer: Completer) -> dict:
    """Backend fields for report.json."""
    if isinstance(completer, JevCompleter):
        out = {
            "base_url": completer.backend.base_url,  # type: ignore[attr-defined]
            "model": completer.model,
            "decode": completer.decode,
            "communication_type": completer.communication_type,
        }
        reported = getattr(completer.backend, "model_reported", None)
        if reported is not None:
            out["model_reported"] = reported
        return out
    if isinstance(completer, SglangClient):
        return {
            "base_url": completer.base_url,
            "model": completer.model,
            "temperature": TEMPERATURE,
        }
    return {}
