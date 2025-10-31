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


# Note: Documents are now dynamically loaded from vector store
# Legacy hardcoded documents have been removed in favor of real vector store integration
# The documents API now fetches from vector store via /exam-assistant/documents endpoint

# Legacy support - empty collections for backward compatibility with existing code
DOCUMENTS: tuple[DocumentMetadata, ...] = ()
DOCUMENTS_BY_ID: dict[str, DocumentMetadata] = {}
DOCUMENTS_BY_FILENAME: dict[str, DocumentMetadata] = {}
DOCUMENTS_BY_STEM: dict[str, DocumentMetadata] = {}
DOCUMENTS_BY_SLUG: dict[str, DocumentMetadata] = {}


__all__ = [
    "DOCUMENTS",
    "DOCUMENTS_BY_FILENAME",
    "DOCUMENTS_BY_ID",
    "DOCUMENTS_BY_SLUG",
    "DOCUMENTS_BY_STEM",
    "DocumentMetadata",
]
