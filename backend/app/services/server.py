"""Server classes and dependencies for the exam assistant."""

from __future__ import annotations

import logging
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

from ..agents_sdk import TriageAgent
from .config import config
from .memory_store import MemoryStore


logger = logging.getLogger(__name__)


if config.debug:
    logger.info("Debug mode enabled - enabling verbose stdout logging")
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
        logger.info("Initializing ExamPrepAssistantServer")
        self.store = MemoryStore()
        super().__init__(self.store)
        self.assistant = agent
        logger.info("ExamPrepAssistantServer initialized successfully")

    async def respond(
        self,
        thread: ThreadMetadata,
        item: ThreadItem | None,
        context: dict[str, Any],
    ) -> AsyncIterator[ThreadStreamEvent]:
        logger.debug(f"Processing request for thread {thread.id}")

        if item is None:
            logger.debug("No item provided, returning")
            return

        if _is_tool_completion_item(item):
            logger.debug("Tool completion item, skipping")
            return

        if not isinstance(item, UserMessageItem):
            logger.debug("Not a user message item, skipping")
            return

        message_text = _user_message_text(item)
        if not message_text:
            logger.debug("Empty message text, returning")
            return

        logger.info(f"Processing user message: {message_text[:100]}...")

        agent_context = AgentContext(
            thread=thread,
            store=self.store,
            request_context=context,
        )

        try:
            result = Runner.run_streamed(
                self.assistant,
                message_text,
                context=agent_context,
                run_config=RunConfig(model_settings=ModelSettings(temperature=0.3)),
            )

            async for event in stream_agent_response(agent_context, result):
                yield event

            logger.debug("Response streaming completed successfully")
        except Exception as e:
            logger.error(f"Error processing user message: {e}")
            raise

    async def to_message_content(self, _input: Attachment) -> ResponseInputContentParam:
        logger.warning("File attachment requested but not supported")
        raise RuntimeError("File attachments are not supported in this demo.")


# Global server instance
logger.info("Creating global ExamPrepAssistantServer instance")
exam_prep_server = ExamPrepAssistantServer(agent=TriageAgent)


def get_server() -> ExamPrepAssistantServer:
    """Dependency to get the exam prep server instance."""
    logger.debug("Returning exam prep server instance")
    return exam_prep_server
