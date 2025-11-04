from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


def _normalise(value: str) -> str:
    return value.strip().lower()


def _slugify(value: str) -> str:
    return "".join(ch for ch in value.lower() if ch.isalnum())


@dataclass(frozen=True, slots=True)
class DocumentMetadata:
    id: str
    filename: str
    title: str
    description: str | None = None

    @property
    def stem(self) -> str:
        return Path(self.filename).stem


__all__ = [
    "DocumentMetadata",
]
