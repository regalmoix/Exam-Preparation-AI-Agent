"""Server classes and dependencies for the exam assistant."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

from agents import Agent
from agents import RunConfig
from agents import Runner
from agents import enable_verbose_stdout_logging
from agents.model_settings import ModelSettings
from chatkit.agents import AgentContext
from chatkit.agents import stream_agent_response
from chatkit.server import ChatKitServer
from chatkit.types import Attachment
from chatkit.types import ClientToolCallItem
from chatkit.types import ThreadItem
from chatkit.types import ThreadMetadata
from chatkit.types import ThreadStreamEvent
from chatkit.types import UserMessageItem
from openai.types.responses import ResponseInputContentParam

from ..agents_sdk import SummarizerAgent
from .config import config
from .memory_store import MemoryStore


if config.debug:
    enable_verbose_stdout_logging()


def _user_message_text(item: UserMessageItem) -> str:
    parts: list[str] = []
    for part in item.content:
        text = getattr(part, "text", None)
        if text:
            parts.append(text)
    return " ".join(parts).strip()


def _is_tool_completion_item(item: Any) -> bool:
    return isinstance(item, ClientToolCallItem)


class ExamPrepAssistantServer(ChatKitServer[dict[str, Any]]):
    """Simplified exam preparation assistant server focused on study assistance."""

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


# Global server instance
exam_prep_server = ExamPrepAssistantServer(agent=SummarizerAgent)


def get_server() -> ExamPrepAssistantServer:
    """Dependency to get the exam prep server instance."""
    return exam_prep_server
