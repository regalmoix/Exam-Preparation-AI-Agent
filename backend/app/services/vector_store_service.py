"""Vector store service for document management operations."""

from __future__ import annotations

import mimetypes
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
        self.vector_store_id = config.exam_prep_vector_store_id

    async def get_vector_store_info(self) -> VectorStoreInfo:
        """Get information about the configured vector store."""
        try:
            response = self.client.vector_stores.retrieve(self.vector_store_id)
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
            response = self.client.vector_stores.files.list(
                vector_store_id=self.vector_store_id,
                limit=limit,
                order=order,
                after=after,
                before=before,
            )
            files = []
            for file in response.data:
                # Create VectorStoreFile manually since the response structure varies
                vector_file = VectorStoreFile(
                    id=file.id,
                    filename=getattr(file, "filename", f"file_{file.id}"),  # Fallback filename
                    bytes=getattr(file, "size", 0) or getattr(file, "bytes", 0),
                    created_at=file.created_at,
                    status=file.status,
                    usage_bytes=getattr(file, "usage_bytes", None),
                    object=getattr(file, "object", "vector_store.file"),
                )
                files.append(vector_file)
            return files
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
            # Guess the MIME type based on filename
            mime_type, _ = mimetypes.guess_type(filename)
            if not mime_type:
                mime_type = "application/octet-stream"

            # Reset file pointer to beginning
            file.seek(0)

            # Create a tuple with the file content and filename for OpenAI
            file_tuple = (filename, file, mime_type)
            uploaded_file = self.client.files.create(file=file_tuple, purpose="user_data")

            # Then, add it to the vector store
            vector_store_file = self.client.vector_stores.files.create(
                vector_store_id=self.vector_store_id, file_id=uploaded_file.id
            )

            # Create VectorStoreFile from the response
            # Use filename from the original uploaded file since vector store file might not have it
            return VectorStoreFile(
                id=vector_store_file.id,
                filename=uploaded_file.filename or filename,  # Use original filename as fallback
                bytes=getattr(vector_store_file, "size", 0) or uploaded_file.bytes,
                created_at=vector_store_file.created_at,
                status=vector_store_file.status,
                usage_bytes=getattr(vector_store_file, "usage_bytes", None),
                object=getattr(vector_store_file, "object", "vector_store.file"),
            )
        except Exception as e:
            raise RuntimeError(f"Failed to upload file to vector store: {e!s}") from e

    async def delete_file_from_vector_store(self, file_id: str) -> bool:
        """Delete a file from the vector store."""
        try:
            self.client.vector_stores.files.delete(vector_store_id=self.vector_store_id, file_id=file_id)
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to delete file from vector store: {e!s}") from e

    async def delete_file_from_openai(self, file_id: str) -> bool:
        """Delete a file from OpenAI Files API."""
        try:
            self.client.files.delete(file_id)
            return True
        except Exception as e:
            # Don't raise error if file doesn't exist in OpenAI
            print(f"Warning: Could not delete file from OpenAI Files API: {e}")
            return False

    async def delete_file_completely(self, file_id: str) -> dict[str, bool]:
        """Delete a file from all locations: vector store, OpenAI Files, and local storage."""
        results = {"vector_store": False, "openai_files": False, "local_storage": False}

        # 1. Delete from vector store
        try:
            results["vector_store"] = await self.delete_file_from_vector_store(file_id)
        except Exception as e:
            print(f"Failed to delete from vector store: {e}")

        # 2. Delete from OpenAI Files API
        try:
            results["openai_files"] = await self.delete_file_from_openai(file_id)
        except Exception as e:
            print(f"Failed to delete from OpenAI Files: {e}")

        return results

    async def get_file_info(self, file_id: str) -> VectorStoreFile:
        """Get information about a specific file in the vector store."""
        try:
            response = self.client.vector_stores.files.retrieve(vector_store_id=self.vector_store_id, file_id=file_id)

            # Create VectorStoreFile manually since the response structure varies
            return VectorStoreFile(
                id=response.id,
                filename=getattr(response, "filename", f"file_{response.id}"),  # Fallback filename
                bytes=getattr(response, "size", 0) or getattr(response, "bytes", 0),
                created_at=response.created_at,
                status=response.status,
                usage_bytes=getattr(response, "usage_bytes", None),
                object=getattr(response, "object", "vector_store.file"),
            )
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
