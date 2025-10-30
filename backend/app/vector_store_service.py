"""Vector store service for document management operations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from typing import BinaryIO

from openai import OpenAI

from .config import config


@dataclass(frozen=True, slots=True)
class VectorStoreFile:
    """Represents a file in the vector store."""

    id: str
    filename: str
    bytes: int
    created_at: int
    status: str
    usage_bytes: int | None = None
    object: str = "vector_store.file"

    @classmethod
    def from_openai_response(cls, response: dict[str, Any]) -> VectorStoreFile:
        """Create VectorStoreFile from OpenAI API response."""
        return cls(
            id=response["id"],
            filename=response["filename"],
            bytes=response["bytes"],
            created_at=response["created_at"],
            status=response["status"],
            usage_bytes=response.get("usage_bytes"),
            object=response.get("object", "vector_store.file"),
        )


@dataclass(frozen=True, slots=True)
class VectorStoreInfo:
    """Represents vector store metadata."""

    id: str
    name: str | None
    file_counts: dict[str, int]
    status: str
    created_at: int
    usage_bytes: int
    object: str = "vector_store"

    @classmethod
    def from_openai_response(cls, response: dict[str, Any]) -> VectorStoreInfo:
        """Create VectorStoreInfo from OpenAI API response."""
        return cls(
            id=response["id"],
            name=response.get("name"),
            file_counts=response.get("file_counts", {}),
            status=response["status"],
            created_at=response["created_at"],
            usage_bytes=response["usage_bytes"],
            object=response.get("object", "vector_store"),
        )


class VectorStoreService:
    """Service for managing vector store operations."""

    def __init__(self):
        """Initialize the vector store service."""
        self.client = OpenAI(api_key=config.openai_api_key)
        self.vector_store_id = config.knowledge_vector_store_id

    async def get_vector_store_info(self) -> VectorStoreInfo:
        """Get information about the configured vector store."""
        try:
            response = self.client.beta.vector_stores.retrieve(self.vector_store_id)
            return VectorStoreInfo.from_openai_response(response.model_dump())
        except Exception as e:
            raise RuntimeError(f"Failed to retrieve vector store info: {e!s}") from e

    async def list_vector_store_files(
        self,
        limit: int = 20,
        order: str = "desc",
        after: str | None = None,
        before: str | None = None,
    ) -> list[VectorStoreFile]:
        """List files in the vector store."""
        try:
            response = self.client.beta.vector_stores.files.list(
                vector_store_id=self.vector_store_id,
                limit=limit,
                order=order,
                after=after,
                before=before,
            )
            return [VectorStoreFile.from_openai_response(file.model_dump()) for file in response.data]
        except Exception as e:
            raise RuntimeError(f"Failed to list vector store files: {e!s}") from e

    async def upload_file_to_vector_store(
        self,
        file: BinaryIO,
        filename: str,
    ) -> VectorStoreFile:
        """Upload a file to the vector store."""
        try:
            # First, upload the file to OpenAI
            uploaded_file = self.client.files.create(file=file, purpose="assistants")

            # Then, add it to the vector store
            vector_store_file = self.client.beta.vector_stores.files.create(
                vector_store_id=self.vector_store_id, file_id=uploaded_file.id
            )

            return VectorStoreFile.from_openai_response(vector_store_file.model_dump())
        except Exception as e:
            raise RuntimeError(f"Failed to upload file to vector store: {e!s}") from e

    async def delete_file_from_vector_store(self, file_id: str) -> bool:
        """Delete a file from the vector store."""
        try:
            self.client.beta.vector_stores.files.delete(vector_store_id=self.vector_store_id, file_id=file_id)
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to delete file from vector store: {e!s}") from e

    async def get_file_info(self, file_id: str) -> VectorStoreFile:
        """Get information about a specific file in the vector store."""
        try:
            response = self.client.beta.vector_stores.files.retrieve(
                vector_store_id=self.vector_store_id, file_id=file_id
            )
            return VectorStoreFile.from_openai_response(response.model_dump())
        except Exception as e:
            raise RuntimeError(f"Failed to retrieve file info: {e!s}") from e


def as_file_dicts(files: list[VectorStoreFile]) -> list[dict[str, Any]]:
    """Convert VectorStoreFile objects to dictionaries for JSON serialization."""
    return [
        {
            "id": file.id,
            "filename": file.filename,
            "bytes": file.bytes,
            "created_at": file.created_at,
            "status": file.status,
            "usage_bytes": file.usage_bytes,
            "object": file.object,
        }
        for file in files
    ]


# Global service instance
vector_store_service = VectorStoreService()


__all__ = [
    "VectorStoreFile",
    "VectorStoreInfo",
    "VectorStoreService",
    "as_file_dicts",
    "vector_store_service",
]
