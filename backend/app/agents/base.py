"""Base classes for AI Study Assistant agents."""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any


class AgentType(Enum):
    """Types of agents available in the study assistant."""

    SUMMARIZER = "summarizer"
    RESEARCH = "research"
    RAG_QA = "rag_qa"
    FLASHCARD = "flashcard"
    INTENT_CLASSIFIER = "intent_classifier"


class TaskPriority(Enum):
    """Priority levels for agent tasks."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class AgentResponse:
    """Standard response format for all agents."""

    agent_type: AgentType
    success: bool
    content: str | dict[str, Any]
    sources: list[dict[str, Any]] | None = None
    reasoning: list[str] | None = None
    metadata: dict[str, Any] | None = None
    error_message: str | None = None


@dataclass
class AgentTask:
    """Task structure for agent processing."""

    task_id: str
    agent_type: AgentType
    priority: TaskPriority
    input_data: dict[str, Any]
    user_id: str | None = None
    session_id: str | None = None


class BaseStudyAgent(ABC):
    """Base class for all study assistant agents."""

    def __init__(self, agent_type: AgentType):
        self.agent_type = agent_type
        self.name = f"{agent_type.value}_agent"

    @abstractmethod
    async def process(self, task: AgentTask) -> AgentResponse:
        """Process a task and return a response."""

    @abstractmethod
    def get_capabilities(self) -> list[str]:
        """Return list of capabilities this agent supports."""

    def validate_input(self, input_data: dict[str, Any]) -> bool:
        """Validate input data for this agent."""
        return True  # Override in subclasses

    def create_response(
        self,
        success: bool,
        content: str | dict[str, Any],
        sources: list[dict[str, Any]] | None = None,
        reasoning: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        error_message: str | None = None,
    ) -> AgentResponse:
        """Helper to create standardized agent responses."""
        return AgentResponse(
            agent_type=self.agent_type,
            success=success,
            content=content,
            sources=sources,
            reasoning=reasoning,
            metadata=metadata,
            error_message=error_message,
        )
