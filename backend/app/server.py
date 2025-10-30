"""Server classes and dependencies for the exam assistant."""

from __future__ import annotations

import re
from collections.abc import AsyncIterator
from collections.abc import Iterable
from itertools import chain
from pathlib import Path
from typing import Any

from agents import Agent
from agents import RunConfig
from agents import Runner
from agents.model_settings import ModelSettings
from chatkit.agents import AgentContext
from chatkit.agents import stream_agent_response
from chatkit.server import ChatKitServer
from chatkit.types import Annotation
from chatkit.types import AssistantMessageContent
from chatkit.types import AssistantMessageItem
from chatkit.types import Attachment
from chatkit.types import ClientToolCallItem
from chatkit.types import ThreadItem
from chatkit.types import ThreadMetadata
from chatkit.types import ThreadStreamEvent
from chatkit.types import UserMessageItem
from openai.types.responses import ResponseInputContentParam

from .assistant_agent import assistant_agent
from .documents import DOCUMENTS_BY_FILENAME
from .documents import DOCUMENTS_BY_SLUG
from .documents import DOCUMENTS_BY_STEM
from .documents import DocumentMetadata
from .memory_store import MemoryStore


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


# Global server instance
knowledge_server = KnowledgeAssistantServer(agent=assistant_agent)


def get_server() -> KnowledgeAssistantServer:
    """Dependency to get the server instance."""
    return knowledge_server
