from __future__ import annotations

import mimetypes
import re
from collections.abc import AsyncIterator
from collections.abc import Iterable
from io import BytesIO
from itertools import chain
from pathlib import Path
from typing import Annotated
from typing import Any

from agents import Agent
from agents import RunConfig
from agents import Runner
from agents.model_settings import ModelSettings
from chatkit.agents import AgentContext
from chatkit.agents import stream_agent_response
from chatkit.server import ChatKitServer
from chatkit.server import StreamingResult
from chatkit.types import Annotation
from chatkit.types import AssistantMessageContent
from chatkit.types import AssistantMessageItem
from chatkit.types import Attachment
from chatkit.types import ClientToolCallItem
from chatkit.types import ThreadItem
from chatkit.types import ThreadMetadata
from chatkit.types import ThreadStreamEvent
from chatkit.types import UserMessageItem
from fastapi import Depends
from fastapi import FastAPI
from fastapi import File
from fastapi import HTTPException
from fastapi import Request
from fastapi import UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.responses import Response
from fastapi.responses import StreamingResponse
from openai.types.responses import ResponseInputContentParam
from starlette.responses import JSONResponse

from .assistant_agent import assistant_agent
from .config import config
from .documents import DOCUMENTS
from .documents import DOCUMENTS_BY_FILENAME
from .documents import DOCUMENTS_BY_ID
from .documents import DOCUMENTS_BY_SLUG
from .documents import DOCUMENTS_BY_STEM
from .documents import DocumentMetadata
from .documents import as_dicts
from .memory_store import MemoryStore
from .vector_store_service import as_file_dicts
from .vector_store_service import vector_store_service


# Validate configuration on startup
if not config.validate():
    raise RuntimeError("Invalid configuration. Please check your .env file and ensure all required variables are set.")


def _normalise_filename(value: str) -> str:
    return Path(value).name.strip().lower()


def _slug(value: str | None) -> str:
    if not value:
        return ""
    return "".join(ch for ch in value.lower() if ch.isalnum())


def _user_message_text(item: UserMessageItem) -> str:
    parts: list[str] = []
    for part in item.content:
        text = getattr(part, "text", None)
        if text:
            parts.append(text)
    return " ".join(parts).strip()


def _resolve_document(annotation: Annotation) -> DocumentMetadata | None:
    source = getattr(annotation, "source", None)
    if not source or getattr(source, "type", None) != "file":
        return None

    filename = getattr(source, "filename", None)
    if filename:
        normalised = _normalise_filename(filename)
        match = DOCUMENTS_BY_FILENAME.get(normalised)
        if match:
            return match
        stem_match = DOCUMENTS_BY_STEM.get(Path(normalised).stem.lower())
        if stem_match:
            return stem_match
        slug_match = DOCUMENTS_BY_SLUG.get(_slug(normalised))
        if slug_match:
            return slug_match

    title = getattr(source, "title", None)
    if title:
        candidate = DOCUMENTS_BY_SLUG.get(_slug(title))
        if candidate:
            return candidate

    description = getattr(source, "description", None)
    if description:
        candidate = DOCUMENTS_BY_SLUG.get(_slug(description))
        if candidate:
            return candidate

    return None


_FILENAME_REGEX = re.compile(r"(0[1-8]_[a-z0-9_\-]+\.(?:pdf|html))", re.IGNORECASE)


def _documents_from_text(text: str) -> Iterable[DocumentMetadata]:
    if not text:
        return []
    matches = {match.lower() for match in _FILENAME_REGEX.findall(text)}
    if not matches:
        return []
    results: list[DocumentMetadata] = []
    for filename in matches:
        doc = DOCUMENTS_BY_FILENAME.get(filename)
        if doc and doc not in results:
            results.append(doc)
    return results


def _is_tool_completion_item(item: Any) -> bool:
    return isinstance(item, ClientToolCallItem)


class KnowledgeAssistantServer(ChatKitServer[dict[str, Any]]):
    def __init__(self, agent: Agent[AgentContext]) -> None:
        self.store = MemoryStore()
        super().__init__(self.store)
        self.assistant = agent

    async def respond(
        self,
        thread: ThreadMetadata,
        item: ThreadItem | None,
        context: dict[str, Any],
    ) -> AsyncIterator[ThreadStreamEvent]:
        if item is None:
            return

        if _is_tool_completion_item(item):
            return

        if not isinstance(item, UserMessageItem):
            return

        message_text = _user_message_text(item)
        if not message_text:
            return

        agent_context = AgentContext(
            thread=thread,
            store=self.store,
            request_context=context,
        )
        result = Runner.run_streamed(
            self.assistant,
            message_text,
            context=agent_context,
            run_config=RunConfig(model_settings=ModelSettings(temperature=0.3)),
        )

        async for event in stream_agent_response(agent_context, result):
            yield event

    async def to_message_content(self, _input: Attachment) -> ResponseInputContentParam:
        raise RuntimeError("File attachments are not supported in this demo.")

    async def latest_citations(self, thread_id: str, context: dict[str, Any]) -> list[dict[str, Any]]:
        items = await self.store.load_thread_items(
            thread_id,
            after=None,
            limit=50,
            order="desc",
            context=context,
        )

        for item in items.data:
            if isinstance(item, AssistantMessageItem):
                citations = list(self._extract_citations(item))
                if citations:
                    return citations
        return []

    def _extract_citations(self, item: AssistantMessageItem) -> Iterable[dict[str, Any]]:
        found = False
        for content in item.content:
            if not isinstance(content, AssistantMessageContent):
                continue
            for annotation in content.annotations:
                document = _resolve_document(annotation)
                if not document:
                    continue
                found = True
                yield {
                    "document_id": document.id,
                    "filename": document.filename,
                    "title": document.title,
                    "description": document.description,
                    "annotation_index": annotation.index,
                }
        if not found:
            texts = chain.from_iterable(
                content.text.splitlines() for content in item.content if isinstance(content, AssistantMessageContent)
            )
            for line in texts:
                for document in _documents_from_text(line):
                    yield {
                        "document_id": document.id,
                        "filename": document.filename,
                        "title": document.title,
                        "description": document.description,
                        "annotation_index": None,
                    }


knowledge_server = KnowledgeAssistantServer(agent=assistant_agent)

app = FastAPI(title="ChatKit Knowledge Assistant API")

_DATA_DIR = Path(__file__).parent / "data"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_server() -> KnowledgeAssistantServer:
    return knowledge_server


@app.post("/knowledge/chatkit")
async def chatkit_endpoint(request: Request, server: Annotated[KnowledgeAssistantServer, Depends(get_server)]) -> Response:
    payload = await request.body()
    result = await server.process(payload, {"request": request})
    if isinstance(result, StreamingResult):
        return StreamingResponse(result, media_type="text/event-stream")
    if hasattr(result, "json"):
        return Response(content=result.json, media_type="application/json")
    return JSONResponse(result)


@app.get("/knowledge/documents")
async def list_documents() -> dict[str, Any]:
    return {"documents": as_dicts(DOCUMENTS)}


@app.get("/knowledge/documents/{document_id}/file")
async def document_file(document_id: str) -> FileResponse:
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


@app.get("/knowledge/threads/{thread_id}/citations")
async def thread_citations(
    thread_id: str,
    request: Request,
    server: Annotated[KnowledgeAssistantServer, Depends(get_server)],
) -> dict[str, Any]:
    context = {"request": request}
    try:
        citations = await server.latest_citations(thread_id, context=context)
    except Exception as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    document_ids = sorted({citation["document_id"] for citation in citations})
    return {"documentIds": document_ids, "citations": citations}


@app.get("/knowledge/health")
async def health_check() -> dict[str, str]:
    return {"status": "healthy"}


# Vector Store Management Endpoints


@app.get("/knowledge/vector-store")
async def get_vector_store_info() -> dict[str, Any]:
    """Get information about the configured vector store."""
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


@app.get("/knowledge/vector-store/files")
async def list_vector_store_files(
    limit: int = 20,
    order: str = "desc",
    after: str | None = None,
    before: str | None = None,
) -> dict[str, Any]:
    """List files in the vector store."""
    try:
        files = await vector_store_service.list_vector_store_files(limit=limit, order=order, after=after, before=before)
        return {
            "files": as_file_dicts(files),
            "has_more": len(files) == limit,  # Simple pagination indicator
        }
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/knowledge/vector-store/files")
async def upload_file_to_vector_store(file: Annotated[UploadFile, File()] = ...) -> dict[str, Any]:
    """Upload a file to the vector store."""
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

        uploaded_file = await vector_store_service.upload_file_to_vector_store(file=file_obj, filename=file.filename)

        return {
            "message": "File uploaded successfully",
            "file": {
                "id": uploaded_file.id,
                "filename": uploaded_file.filename,
                "bytes": uploaded_file.bytes,
                "status": uploaded_file.status,
            },
        }
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        await file.close()


@app.get("/knowledge/vector-store/files/{file_id}")
async def get_vector_store_file_info(file_id: str) -> dict[str, Any]:
    """Get information about a specific file in the vector store."""
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


@app.delete("/knowledge/vector-store/files/{file_id}")
async def delete_file_from_vector_store(file_id: str) -> dict[str, str]:
    """Delete a file from the vector store."""
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
