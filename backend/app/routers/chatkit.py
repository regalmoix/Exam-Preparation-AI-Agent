"""ChatKit API endpoints for exam assistant."""

from __future__ import annotations

from typing import Annotated

from chatkit.server import StreamingResult
from fastapi import APIRouter
from fastapi import Depends
from fastapi import Request
from fastapi import Response
from fastapi.responses import StreamingResponse
from starlette.responses import JSONResponse

from ..server import ExamPrepAssistantServer
from ..server import get_server


router = APIRouter()


@router.post("/chatkit")
async def chatkit_endpoint(
    request: Request, server: Annotated[ExamPrepAssistantServer, Depends(get_server)]
) -> Response:
    """Main ChatKit interaction endpoint for the exam assistant."""
    payload = await request.body()
    result = await server.process(payload, {"request": request})
    if isinstance(result, StreamingResult):
        return StreamingResponse(result, media_type="text/event-stream")
    if hasattr(result, "json"):
        return Response(content=result.json, media_type="application/json")
    return JSONResponse(result)


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint for the exam assistant."""
    return {"status": "healthy"}
