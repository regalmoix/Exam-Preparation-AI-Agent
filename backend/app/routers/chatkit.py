"""ChatKit API endpoints for exam assistant."""

from __future__ import annotations

from typing import Annotated
from typing import Any

from chatkit.server import StreamingResult
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request
from fastapi import Response
from fastapi.responses import StreamingResponse
from starlette.responses import JSONResponse

from ..server import KnowledgeAssistantServer
from ..server import get_server


router = APIRouter()


@router.post("/chatkit")
async def chatkit_endpoint(
    request: Request, server: Annotated[KnowledgeAssistantServer, Depends(get_server)]
) -> Response:
    """Main ChatKit interaction endpoint for the exam assistant."""
    payload = await request.body()
    result = await server.process(payload, {"request": request})
    if isinstance(result, StreamingResult):
        return StreamingResponse(result, media_type="text/event-stream")
    if hasattr(result, "json"):
        return Response(content=result.json, media_type="application/json")
    return JSONResponse(result)


@router.get("/threads/{thread_id}/citations")
async def thread_citations(
    thread_id: str,
    request: Request,
    server: Annotated[KnowledgeAssistantServer, Depends(get_server)],
) -> dict[str, Any]:
    """Get citations for a specific thread in the exam assistant."""
    context = {"request": request}
    try:
        citations = await server.latest_citations(thread_id, context=context)
    except Exception as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    document_ids = sorted({citation["document_id"] for citation in citations})
    return {"documentIds": document_ids, "citations": citations}


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint for the exam assistant."""
    return {"status": "healthy"}
