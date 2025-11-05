from __future__ import annotations

import json
from dataclasses import asdict
from dataclasses import dataclass
from pathlib import Path


@dataclass
class DocumentMetadata:
    file_id: str
    original_filename: str
    title: str
    description: str
    file_size: int
    upload_time: int
    file_type: str
    local_file_path: str | None = None


class DocumentMetadataStore:
    def __init__(self, storage_path: str = "../data/document_metadata.json"):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(exist_ok=True)
        self._metadata: dict[str, DocumentMetadata] = {}
        self._load_metadata()

    def _load_metadata(self) -> None:
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
        try:
            data = {file_id: asdict(metadata) for file_id, metadata in self._metadata.items()}
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving document metadata: {e}")

    def store_metadata(self, metadata: DocumentMetadata) -> None:
        self._metadata[metadata.file_id] = metadata
        self._save_metadata()

    def get_metadata(self, file_id: str) -> DocumentMetadata | None:
        return self._metadata.get(file_id)

    def delete_metadata(self, file_id: str) -> bool:
        if file_id in self._metadata:
            del self._metadata[file_id]
            self._save_metadata()
            return True
        return False


metadata_store = DocumentMetadataStore()

__all__ = ["DocumentMetadata", "DocumentMetadataStore", "metadata_store"]
