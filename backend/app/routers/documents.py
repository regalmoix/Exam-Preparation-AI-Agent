"""Document management API endpoints for exam assistant."""

from __future__ import annotations

import mimetypes
from pathlib import Path
from typing import Any

import anyio
from fastapi import APIRouter
from fastapi import HTTPException
from fastapi.responses import Response

from ..document_metadata import metadata_store
from ..vector_store_service import vector_store_service


router = APIRouter()


@router.get("/documents")
async def list_documents() -> dict[str, Any]:
    """List all available documents in the exam assistant study materials from vector store."""
    try:
        files = await vector_store_service.list_vector_store_files(limit=100)

        documents = []
        for file in files:
            # Try to get enhanced metadata first
            metadata = metadata_store.get_metadata(file.id)

            if metadata:
                # Use enhanced metadata with LLM-generated descriptions
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
                # Fallback to improved logic for existing files without enhanced metadata
                # Try to extract meaningful info from the filename
                original_filename = file.filename

                # Remove common prefixes that OpenAI might add
                clean_filename = original_filename.replace("file_", "")

                if clean_filename.startswith("file-"):
                    # For auto-generated names, try to create a better title
                    title = f"Document {clean_filename[-6:]}"
                    description = f"Study document uploaded to vector store ({file.usage_bytes or 0} bytes)"
                else:
                    # Use the actual filename
                    file_path = Path(clean_filename)
                    title = file_path.stem  # Filename without extension

                    # Generate a basic description based on file type
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

        return {"documents": documents}
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/documents/{document_id}")
async def get_document_info(document_id: str) -> dict[str, Any]:
    """Get information about a specific document in the vector store."""
    try:
        file_info = await vector_store_service.get_file_info(document_id)

        # Try to get enhanced metadata first
        metadata = metadata_store.get_metadata(document_id)

        if metadata:
            # Use enhanced metadata with LLM-generated descriptions
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
            # Fallback to improved logic for existing files
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
            raise HTTPException(status_code=404, detail="Document not found") from exc
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/documents/{document_id}/file")
async def get_document_file(document_id: str) -> Response:
    """Retrieve the actual file content of a document, either from local storage or OpenAI."""
    try:
        # Get file info and metadata
        file_info = await vector_store_service.get_file_info(document_id)
        metadata = metadata_store.get_metadata(document_id)

        filename = metadata.original_filename if metadata else file_info.filename

        # Try to serve from local storage first
        if metadata and metadata.local_file_path:
            local_path = Path(metadata.local_file_path)
            if not local_path.exists():
                raise HTTPException(status_code=404, detail="Document not found")
            # Serve from local storage
            async with await anyio.open_file(local_path) as local_file:
                file_content = await local_file.read()

                # Determine content type from filename

                content_type, _ = mimetypes.guess_type(filename)
                if not content_type:
                    content_type = "application/octet-stream"

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
            raise HTTPException(status_code=404, detail="Document not found") from exc
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.delete("/documents/{document_id}")
async def delete_document(document_id: str) -> dict[str, Any]:
    """Delete a document from all locations: local storage, vector store, and OpenAI Files."""
    try:
        # Get metadata for local file path
        metadata = metadata_store.get_metadata(document_id)

        # Delete from vector store and OpenAI Files
        delete_results = await vector_store_service.delete_file_completely(document_id)

        # Delete local file if it exists
        local_deleted = False
        if metadata and metadata.local_file_path:
            try:
                local_path = Path(metadata.local_file_path)
                if local_path.exists():
                    local_path.unlink()
                    local_deleted = True
            except Exception as e:
                print(f"Failed to delete local file: {e}")

        delete_results["local_storage"] = local_deleted

        # Delete metadata
        metadata_deleted = metadata_store.delete_metadata(document_id)

        return {
            "message": "Document deletion completed",
            "document_id": document_id,
            "filename": metadata.original_filename if metadata else "unknown",
            "deletion_results": {**delete_results, "metadata": metadata_deleted},
            "success": any(delete_results.values()) or metadata_deleted,
        }

    except RuntimeError as exc:
        if "not found" in str(exc).lower():
            raise HTTPException(status_code=404, detail="Document not found") from exc
        raise HTTPException(status_code=500, detail=str(exc)) from exc
