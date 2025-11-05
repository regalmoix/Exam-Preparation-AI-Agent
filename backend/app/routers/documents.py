from __future__ import annotations

import logging
import mimetypes
from pathlib import Path
from typing import Any

import anyio
from fastapi import APIRouter
from fastapi import HTTPException
from fastapi.responses import Response

from ..models.document_metadata import metadata_store
from ..services.vector_store_service import vector_store_service


logger = logging.getLogger(__name__)


router = APIRouter()


@router.get("/documents")
async def list_documents() -> dict[str, Any]:
    logger.info("Listing documents from vector store")

    try:
        files = await vector_store_service.list_vector_store_files(limit=100)
        logger.debug(f"Retrieved {len(files)} files from vector store")

        documents = []
        for file in files:
            metadata = metadata_store.get_metadata(file.id)

            if metadata:
                documents.append(
                    {
                        "id": file.id,
                        "filename": metadata.original_filename,
                        "title": metadata.title,
                        "description": metadata.description,
                        "created_at": file.created_at,
                        "status": file.status,
                        "usage_bytes": file.usage_bytes or metadata.file_size,
                    }
                )
            else:
                original_filename = file.filename

                # Remove common prefixes that OpenAI might add
                clean_filename = original_filename.replace("file_", "")

                if clean_filename.startswith("file-"):
                    title = f"Document {clean_filename[-6:]}"
                    description = f"Study document uploaded to vector store ({file.usage_bytes or 0} bytes)"
                else:
                    file_path = Path(clean_filename)
                    title = file_path.stem

                    extension = file_path.suffix.lower()
                    if extension == ".pdf":
                        description = "PDF study document"
                    elif extension in [".txt", ".md"]:
                        description = "Text-based study material"
                    elif extension == ".html":
                        description = "Web-based study content"
                    elif extension == ".docx":
                        description = "Word document for study"
                    else:
                        description = f"Study document ({file.usage_bytes or 0} bytes)"

                documents.append(
                    {
                        "id": file.id,
                        "filename": original_filename,
                        "title": title,
                        "description": description,
                        "created_at": file.created_at,
                        "status": file.status,
                        "usage_bytes": file.usage_bytes,
                    }
                )

        logger.info(f"Successfully listed {len(documents)} documents")
        return {"documents": documents}
    except RuntimeError as exc:
        logger.error(f"Error listing documents: {exc}")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/documents/{document_id}")
async def get_document_info(document_id: str) -> dict[str, Any]:
    logger.info(f"Getting document info for ID: {document_id}")

    try:
        file_info = await vector_store_service.get_file_info(document_id)

        metadata = metadata_store.get_metadata(document_id)

        if metadata:
            return {
                "id": file_info.id,
                "filename": metadata.original_filename,
                "title": metadata.title,
                "description": metadata.description,
                "created_at": file_info.created_at,
                "status": file_info.status,
                "usage_bytes": file_info.usage_bytes or metadata.file_size,
                "bytes": file_info.bytes,
                "object": file_info.object,
                "file_type": metadata.file_type,
                "upload_time": metadata.upload_time,
            }
        else:
            original_filename = file_info.filename
            clean_filename = original_filename.replace("file_", "")

            if clean_filename.startswith("file-"):
                title = f"Document {clean_filename[-6:]}"
                description = f"Study document uploaded to vector store ({file_info.usage_bytes or 0} bytes)"
            else:
                file_path = Path(clean_filename)
                title = file_path.stem
                extension = file_path.suffix.lower()

                if extension == ".pdf":
                    description = "PDF study document"
                elif extension in [".txt", ".md"]:
                    description = "Text-based study material"
                elif extension == ".html":
                    description = "Web-based study content"
                elif extension == ".docx":
                    description = "Word document for study"
                else:
                    description = f"Study document ({file_info.usage_bytes or 0} bytes)"

            return {
                "id": file_info.id,
                "filename": original_filename,
                "title": title,
                "description": description,
                "created_at": file_info.created_at,
                "status": file_info.status,
                "usage_bytes": file_info.usage_bytes,
                "bytes": file_info.bytes,
                "object": file_info.object,
            }
    except RuntimeError as exc:
        if "not found" in str(exc).lower():
            logger.warning(f"Document not found: {document_id}")
            raise HTTPException(status_code=404, detail="Document not found") from exc
        logger.error(f"Error getting document info for {document_id}: {exc}")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/documents/{document_id}/file")
async def get_document_file(document_id: str) -> Response:
    logger.info(f"Retrieving file content for document ID: {document_id}")

    try:
        file_info = await vector_store_service.get_file_info(document_id)
        metadata = metadata_store.get_metadata(document_id)

        filename = metadata.original_filename if metadata else file_info.filename

        if metadata and metadata.local_file_path:
            logger.debug(f"Attempting to serve from local storage: {metadata.local_file_path}")
            local_path = Path(metadata.local_file_path)
            if not local_path.exists():
                logger.warning(f"Local file not found: {metadata.local_file_path}")
                raise HTTPException(status_code=404, detail="Document not found")

            async with await anyio.open_file(local_path) as local_file:
                file_content = await local_file.read()

                content_type, _ = mimetypes.guess_type(filename)
                if not content_type:
                    content_type = "application/octet-stream"

                logger.info(f"Serving file from local storage: {filename} ({len(file_content)} bytes)")
                return Response(
                    content=file_content,
                    media_type=content_type,
                    headers={
                        "Content-Disposition": f'inline; filename="{filename}"',
                        "Content-Length": str(len(file_content)),
                        "X-Source": "local-storage",
                    },
                )

    except RuntimeError as exc:
        if "not found" in str(exc).lower():
            logger.warning(f"Document file not found: {document_id}")
            raise HTTPException(status_code=404, detail="Document not found") from exc
        logger.error(f"Error retrieving document file {document_id}: {exc}")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.delete("/documents/{document_id}")
async def delete_document(document_id: str) -> dict[str, Any]:
    logger.info(f"Deleting document: {document_id}")

    try:
        metadata = metadata_store.get_metadata(document_id)

        delete_results = await vector_store_service.delete_file_completely(document_id)

        local_deleted = False
        if metadata and metadata.local_file_path:
            try:
                local_path = Path(metadata.local_file_path)
                if local_path.exists():
                    local_path.unlink()
                    local_deleted = True
                    logger.debug(f"Deleted local file: {metadata.local_file_path}")
            except Exception as e:
                logger.warning(f"Failed to delete local file: {e}")

        delete_results["local_storage"] = local_deleted

        metadata_deleted = metadata_store.delete_metadata(document_id)
        logger.debug(f"Metadata deletion result: {metadata_deleted}")

        result = {
            "message": "Document deletion completed",
            "document_id": document_id,
            "filename": metadata.original_filename if metadata else "unknown",
            "deletion_results": {**delete_results, "metadata": metadata_deleted},
            "success": any(delete_results.values()) or metadata_deleted,
        }

        logger.info(f"Document deletion completed: {document_id}, success: {result['success']}")
        return result

    except RuntimeError as exc:
        if "not found" in str(exc).lower():
            logger.warning(f"Document not found for deletion: {document_id}")
            raise HTTPException(status_code=404, detail="Document not found") from exc
        logger.error(f"Error deleting document {document_id}: {exc}")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
