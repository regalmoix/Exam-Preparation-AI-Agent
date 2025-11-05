from __future__ import annotations

import logging
from typing import Annotated

from chatkit.server import StreamingResult
from fastapi import APIRouter
from fastapi import Depends
from fastapi import Request
from fastapi import Response
from fastapi.responses import StreamingResponse
from starlette.responses import JSONResponse

from ..agents_sdk.mcp import AnkiMCPServer
from ..services.server import ExamPrepAssistantServer
from ..services.server import get_server


logger = logging.getLogger(__name__)


router = APIRouter()


@router.post("/chatkit")
async def chatkit_endpoint(
    request: Request, server: Annotated[ExamPrepAssistantServer, Depends(get_server)]
) -> Response:
    logger.info(f"Received chatkit request from {request.client.host if request.client else 'unknown'}")

    try:
        logger.debug("Connecting to Anki MCP Server")
        await AnkiMCPServer.connect()

        payload = await request.body()
        logger.debug(f"Processing request payload of size: {len(payload)} bytes")

        result = await server.process(payload, {"request": request})

        if isinstance(result, StreamingResult):
            logger.debug("Returning streaming response")
            return StreamingResponse(result, media_type="text/event-stream")

        if hasattr(result, "json"):
            logger.debug("Returning JSON response")
            return Response(content=result.json, media_type="application/json")

        logger.debug("Returning JSON response via JSONResponse")
        return JSONResponse(result)

    except Exception as e:
        logger.error(f"Error processing chatkit request: {e}")
        raise


@router.get("/health")
async def health_check() -> dict[str, str]:
    logger.debug("Health check endpoint called")
    return {"status": "healthy"}
