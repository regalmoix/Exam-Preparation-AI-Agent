"""Vector store management API endpoints for exam assistant."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Annotated
from typing import Any

from fastapi import APIRouter
from fastapi import File
from fastapi import HTTPException
from fastapi import UploadFile

from ..services.vector_store_service import as_file_dicts
from ..services.vector_store_service import vector_store_service


logger = logging.getLogger(__name__)


router = APIRouter()


@router.get("/vector-store")
async def get_vector_store_info() -> dict[str, Any]:
    """Get information about the exam assistant vector store."""
    logger.info("Getting vector store information")

    try:
        info = await vector_store_service.get_vector_store_info()
        logger.debug(f"Vector store info retrieved: {info.file_counts} files, {info.usage_bytes} bytes")
        return {
            "id": info.id,
            "name": info.name,
            "file_counts": info.file_counts,
            "status": info.status,
            "created_at": info.created_at,
            "usage_bytes": info.usage_bytes,
            "object": info.object,
        }
    except RuntimeError as exc:
        logger.error(f"Error getting vector store info: {exc}")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/vector-store/files")
async def list_vector_store_files(
    limit: int = 20,
    order: str = "desc",
    after: str | None = None,
    before: str | None = None,
) -> dict[str, Any]:
    """List files in the exam assistant vector store."""
    try:
        files = await vector_store_service.list_vector_store_files(limit=limit, order=order, after=after, before=before)
        return {
            "files": as_file_dicts(files),
            "has_more": len(files) == limit,  # Simple pagination indicator
        }
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/vector-store/files")
async def upload_file_to_vector_store(file: Annotated[UploadFile, File()]) -> dict[str, Any]:
    """Upload a file to the exam assistant vector store with intelligent description generation."""
    logger.info(f"Uploading file to vector store: {file.filename}")

    if not file.filename:
        logger.error("File upload attempted without filename")
        raise HTTPException(status_code=400, detail="File must have a filename")

    # Validate file type (optional - you can customize this)
    allowed_extensions = {".pdf", ".txt", ".md", ".html", ".docx", ".json"}
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in allowed_extensions:
        logger.warning(f"Unsupported file type upload attempted: {file_extension}")
        raise HTTPException(
            status_code=400,
            detail=f"File type {file_extension} not supported. Allowed types: {', '.join(allowed_extensions)}",
        )

    try:
        content = await file.read()
        logger.debug(f"File read successfully: {file.filename}, size: {len(content)} bytes")

        data = await vector_store_service.add_file_to_vector_store(content, file.filename, file_extension)
        logger.info(f"File uploaded successfully to vector store: {file.filename}")
        return data
    except RuntimeError as exc:
        logger.error(f"Error uploading file {file.filename}: {exc}")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        await file.close()


@router.get("/vector-store/files/{file_id}")
async def get_vector_store_file_info(file_id: str) -> dict[str, Any]:
    """Get information about a specific file in the exam assistant vector store."""
    try:
        file_info = await vector_store_service.get_file_info(file_id)
        return {
            "id": file_info.id,
            "filename": file_info.filename,
            "bytes": file_info.bytes,
            "created_at": file_info.created_at,
            "status": file_info.status,
            "usage_bytes": file_info.usage_bytes,
            "object": file_info.object,
        }
    except RuntimeError as exc:
        if "not found" in str(exc).lower():
            raise HTTPException(status_code=404, detail="File not found") from exc
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.delete("/vector-store/files/{file_id}")
async def delete_file_from_vector_store(file_id: str) -> dict[str, str]:
    """Delete a file from the exam assistant vector store."""
    logger.info(f"Deleting file from vector store: {file_id}")

    try:
        success = await vector_store_service.delete_file_from_vector_store(file_id)
        if success:
            logger.info(f"File deleted successfully from vector store: {file_id}")
            return {"message": "File deleted successfully"}
        else:
            logger.error(f"Failed to delete file from vector store: {file_id}")
            raise HTTPException(status_code=500, detail="Failed to delete file")
    except RuntimeError as exc:
        if "not found" in str(exc).lower():
            logger.warning(f"File not found for deletion: {file_id}")
            raise HTTPException(status_code=404, detail="File not found") from exc
        logger.error(f"Error deleting file from vector store {file_id}: {exc}")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
