"""Document management API endpoints for exam assistant."""

from __future__ import annotations

import mimetypes
from pathlib import Path
from typing import Any

from fastapi import APIRouter
from fastapi import HTTPException
from fastapi.responses import FileResponse

from ..documents import DOCUMENTS
from ..documents import DOCUMENTS_BY_ID
from ..documents import as_dicts


router = APIRouter()

# Data directory path (adjust if needed)
_DATA_DIR = Path(__file__).parent.parent.parent.parent / "data"


@router.get("/documents")
async def list_documents() -> dict[str, Any]:
    """List all available documents in the exam assistant knowledge base."""
    return {"documents": as_dicts(DOCUMENTS)}


@router.get("/documents/{document_id}/file")
async def document_file(document_id: str) -> FileResponse:
    """Download a specific document file from the exam assistant knowledge base."""
    document = DOCUMENTS_BY_ID.get(document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    file_path = _DATA_DIR / document.filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not available")

    media_type, _ = mimetypes.guess_type(str(file_path))
    headers = {"Content-Disposition": f'inline; filename="{document.filename}"'}
    return FileResponse(
        file_path,
        media_type=media_type or "application/octet-stream",
        headers=headers,
    )
