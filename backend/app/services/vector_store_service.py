from __future__ import annotations

import logging
import mimetypes
import time
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Any
from typing import BinaryIO

import anyio
from openai import OpenAI

from ..models.document_metadata import DocumentMetadata
from ..models.document_metadata import metadata_store
from .config import config
from .document_summarizer import document_summarizer


logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class VectorStoreFile:
    id: str
    filename: str
    bytes: int
    created_at: int
    status: str
    usage_bytes: int | None = None
    object: str = "vector_store.file"

    @classmethod
    def from_openai_response(cls, response: dict[str, Any]) -> VectorStoreFile:
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
    id: str
    name: str | None
    file_counts: dict[str, int]
    status: str
    created_at: int
    usage_bytes: int
    object: str = "vector_store"

    @classmethod
    def from_openai_response(cls, response: dict[str, Any]) -> VectorStoreInfo:
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
    def __init__(self):
        self.client = OpenAI(api_key=config.openai_api_key)
        self.vector_store_id = config.exam_prep_vector_store_id

    async def get_vector_store_info(self) -> VectorStoreInfo:
        logger.info("Retrieving vector store info")
        try:
            response = self.client.vector_stores.retrieve(self.vector_store_id)
            info = VectorStoreInfo.from_openai_response(response.model_dump())
            logger.info(f"Vector store info retrieved: {info.file_counts} files")
            return info
        except Exception as e:
            logger.exception(f"Failed to retrieve vector store info: {e}")
            raise RuntimeError(f"Failed to retrieve vector store info: {e!s}") from e

    async def list_vector_store_files(
        self,
        limit: int = 20,
        order: str = "desc",
        after: str | None = None,
        before: str | None = None,
    ) -> list[VectorStoreFile]:
        logger.debug(f"Listing vector store files: limit={limit}, order={order}")
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
                vector_file = VectorStoreFile(
                    id=file.id,
                    filename=getattr(file, "filename", f"file_{file.id}"),
                    bytes=getattr(file, "size", 0) or getattr(file, "bytes", 0),
                    created_at=file.created_at,
                    status=file.status,
                    usage_bytes=getattr(file, "usage_bytes", None),
                    object=getattr(file, "object", "vector_store.file"),
                )
                files.append(vector_file)

            logger.debug(f"Retrieved {len(files)} files from vector store")
            return files
        except Exception as e:
            logger.error(f"Failed to list vector store files: {e}")
            raise RuntimeError(f"Failed to list vector store files: {e!s}") from e

    async def upload_file_to_vector_store(
        self,
        file: BinaryIO,
        filename: str,
    ) -> VectorStoreFile:
        try:
            mime_type, _ = mimetypes.guess_type(filename)
            if not mime_type:
                mime_type = "application/octet-stream"

            file.seek(0)

            file_tuple = (filename, file, mime_type)
            uploaded_file = self.client.files.create(file=file_tuple, purpose="user_data")

            vector_store_file = self.client.vector_stores.files.create(
                vector_store_id=self.vector_store_id, file_id=uploaded_file.id
            )

            return VectorStoreFile(
                id=vector_store_file.id,
                filename=uploaded_file.filename or filename,
                bytes=getattr(vector_store_file, "size", 0) or uploaded_file.bytes,
                created_at=vector_store_file.created_at,
                status=vector_store_file.status,
                usage_bytes=getattr(vector_store_file, "usage_bytes", None),
                object=getattr(vector_store_file, "object", "vector_store.file"),
            )
        except Exception as e:
            raise RuntimeError(f"Failed to upload file to vector store: {e!s}") from e

    async def delete_file_from_vector_store(self, file_id: str) -> bool:
        try:
            self.client.vector_stores.files.delete(vector_store_id=self.vector_store_id, file_id=file_id)
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to delete file from vector store: {e!s}") from e

    async def delete_file_from_openai(self, file_id: str) -> bool:
        try:
            self.client.files.delete(file_id)
            return True
        except Exception as e:
            print(f"Warning: Could not delete file from OpenAI Files API: {e}")
            return False

    async def delete_file_completely(self, file_id: str) -> dict[str, bool]:
        results = {"vector_store": False, "openai_files": False, "local_storage": False}

        try:
            results["vector_store"] = await self.delete_file_from_vector_store(file_id)
        except Exception as e:
            print(f"Failed to delete from vector store: {e}")

        try:
            results["openai_files"] = await self.delete_file_from_openai(file_id)
        except Exception as e:
            print(f"Failed to delete from OpenAI Files: {e}")

        return results

    async def get_file_info(self, file_id: str) -> VectorStoreFile:
        try:
            response = self.client.vector_stores.files.retrieve(vector_store_id=self.vector_store_id, file_id=file_id)

            return VectorStoreFile(
                id=response.id,
                filename=getattr(response, "filename", f"file_{response.id}"),
                bytes=getattr(response, "size", 0) or getattr(response, "bytes", 0),
                created_at=response.created_at,
                status=response.status,
                usage_bytes=getattr(response, "usage_bytes", None),
                object=getattr(response, "object", "vector_store.file"),
            )
        except Exception as e:
            raise RuntimeError(f"Failed to retrieve file info: {e!s}") from e

    async def add_file_to_vector_store(
        self,
        file_content: bytes,
        filename: str,
        file_extension: str,
    ):
        logger.info(f"Adding file to vector store: {filename} ({len(file_content)} bytes)")
        file_obj = BytesIO(file_content)

        uploaded_file = await self.upload_file_to_vector_store(file=file_obj, filename=filename)

        try:
            logger.debug(f"Generating description for {filename}")
            description = await document_summarizer.generate_description(file_content, filename)
            logger.debug(f"Generated description for {filename}: {description[:100]}...")
        except Exception as e:
            logger.warning(f"Failed to generate description for {filename}: {e}")
            description = f"Study document ({len(file_content)} bytes)"

        file_path = Path(filename)
        title = file_path.stem

        data_dir = Path("../data/uploaded_files")
        data_dir.mkdir(parents=True, exist_ok=True)

        safe_filename = f"{uploaded_file.id}_{filename}"
        local_file_path = data_dir / safe_filename
        logger.debug(f"Saving local copy to: {local_file_path}")

        async with await anyio.open_file(local_file_path, "wb") as local_file:
            await local_file.write(file_content)

        metadata = DocumentMetadata(
            file_id=uploaded_file.id,
            original_filename=filename,
            title=title,
            description=description,
            file_size=len(file_content),
            upload_time=int(time.time()),
            file_type=file_extension,
            local_file_path=str(local_file_path),
        )
        metadata_store.store_metadata(metadata)
        logger.info(f"File successfully added to vector store: {uploaded_file.id}")

        return {
            "message": "File uploaded successfully",
            "file": {
                "id": uploaded_file.id,
                "filename": uploaded_file.filename,
                "title": title,
                "description": description,
                "bytes": uploaded_file.bytes,
                "status": uploaded_file.status,
            },
        }


def as_file_dicts(files: list[VectorStoreFile]) -> list[dict[str, Any]]:
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


vector_store_service = VectorStoreService()


__all__ = [
    "VectorStoreFile",
    "VectorStoreInfo",
    "VectorStoreService",
    "as_file_dicts",
    "vector_store_service",
]
