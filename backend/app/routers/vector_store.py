"""Vector store management API endpoints for exam assistant."""

from __future__ import annotations

import time
from io import BytesIO
from pathlib import Path
from typing import Annotated
from typing import Any

import anyio
from fastapi import APIRouter
from fastapi import File
from fastapi import HTTPException
from fastapi import UploadFile

from ..document_metadata import DocumentMetadata
from ..document_metadata import metadata_store
from ..document_summarizer import document_summarizer
from ..vector_store_service import as_file_dicts
from ..vector_store_service import vector_store_service


router = APIRouter()


@router.get("/vector-store")
async def get_vector_store_info() -> dict[str, Any]:
    """Get information about the exam assistant vector store."""
    try:
        info = await vector_store_service.get_vector_store_info()
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
async def upload_file_to_vector_store(file: Annotated[UploadFile, File()] = ...) -> dict[str, Any]:
    """Upload a file to the exam assistant vector store with intelligent description generation."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="File must have a filename")

    # Validate file type (optional - you can customize this)
    allowed_extensions = {".pdf", ".txt", ".md", ".html", ".docx", ".json"}
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file_extension} not supported. Allowed types: {', '.join(allowed_extensions)}",
        )

    try:
        # Read file content
        content = await file.read()
        file_obj = BytesIO(content)

        # Upload to vector store
        uploaded_file = await vector_store_service.upload_file_to_vector_store(file=file_obj, filename=file.filename)

        # Generate intelligent description using LLM
        try:
            description = await document_summarizer.generate_description(content, file.filename)
        except Exception as e:
            print(f"Failed to generate description for {file.filename}: {e}")
            description = f"Study document ({len(content)} bytes)"

        # Create title from original filename (remove path and clean up)
        file_path = Path(file.filename)
        title = file_path.stem  # Filename without extension

        # Save local copy to data directory
        data_dir = Path("data/uploaded_files")
        data_dir.mkdir(parents=True, exist_ok=True)

        # Create safe filename using file ID to avoid conflicts
        safe_filename = f"{uploaded_file.id}_{file.filename}"
        local_file_path = data_dir / safe_filename

        # Write the file content to local storage
        async with await anyio.open_file(local_file_path) as local_file:
            await local_file.write(content)

        # Store enhanced metadata with local file path
        metadata = DocumentMetadata(
            file_id=uploaded_file.id,
            original_filename=file.filename,
            title=title,
            description=description,
            file_size=len(content),
            upload_time=int(time.time()),
            file_type=file_extension,
            local_file_path=str(local_file_path),
        )
        metadata_store.store_metadata(metadata)

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
    except RuntimeError as exc:
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
    try:
        success = await vector_store_service.delete_file_from_vector_store(file_id)
        if success:
            return {"message": "File deleted successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to delete file")
    except RuntimeError as exc:
        if "not found" in str(exc).lower():
            raise HTTPException(status_code=404, detail="File not found") from exc
        raise HTTPException(status_code=500, detail=str(exc)) from exc
