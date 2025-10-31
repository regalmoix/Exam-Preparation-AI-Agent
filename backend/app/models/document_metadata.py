"""Document metadata storage for enhanced document information."""

from __future__ import annotations

import json
from dataclasses import asdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class DocumentMetadata:
    """Enhanced metadata for uploaded documents."""

    file_id: str
    original_filename: str
    title: str
    description: str
    file_size: int
    upload_time: int
    file_type: str
    local_file_path: str | None = None  # Path to local copy of the file


class DocumentMetadataStore:
    """Simple file-based storage for document metadata."""

    def __init__(self, storage_path: str = "data/document_metadata.json"):
        """Initialize the metadata store."""
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(exist_ok=True)
        self._metadata: dict[str, DocumentMetadata] = {}
        self._load_metadata()

    def _load_metadata(self) -> None:
        """Load metadata from storage file."""
        try:
            if self.storage_path.exists():
                with open(self.storage_path, encoding="utf-8") as f:
                    data = json.load(f)
                    self._metadata = {
                        file_id: DocumentMetadata(**metadata_dict) for file_id, metadata_dict in data.items()
                    }
        except Exception as e:
            print(f"Error loading document metadata: {e}")
            self._metadata = {}

    def _save_metadata(self) -> None:
        """Save metadata to storage file."""
        try:
            data = {file_id: asdict(metadata) for file_id, metadata in self._metadata.items()}
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving document metadata: {e}")

    def store_metadata(self, metadata: DocumentMetadata) -> None:
        """Store metadata for a document."""
        self._metadata[metadata.file_id] = metadata
        self._save_metadata()

    def get_metadata(self, file_id: str) -> DocumentMetadata | None:
        """Get metadata for a document."""
        return self._metadata.get(file_id)

    def list_all_metadata(self) -> list[DocumentMetadata]:
        """Get all stored metadata."""
        return list(self._metadata.values())

    def delete_metadata(self, file_id: str) -> bool:
        """Delete metadata for a document."""
        if file_id in self._metadata:
            del self._metadata[file_id]
            self._save_metadata()
            return True
        return False

    def update_metadata(self, file_id: str, **updates: Any) -> bool:
        """Update specific fields of metadata."""
        if file_id in self._metadata:
            metadata = self._metadata[file_id]
            for key, value in updates.items():
                if hasattr(metadata, key):
                    setattr(metadata, key, value)
            self._save_metadata()
            return True
        return False


# Global instance
metadata_store = DocumentMetadataStore()

__all__ = ["DocumentMetadata", "DocumentMetadataStore", "metadata_store"]
