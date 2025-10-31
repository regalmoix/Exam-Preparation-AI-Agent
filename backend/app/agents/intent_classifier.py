"""Intent classification agent for routing student queries."""

from __future__ import annotations

from typing import Any

from .base import AgentResponse
from .base import AgentTask
from .base import AgentType
from .base import BaseStudyAgent


class IntentClassifierAgent(BaseStudyAgent):
    """Agent that classifies user intents and routes to appropriate agents."""

    def __init__(self):
        super().__init__(AgentType.INTENT_CLASSIFIER)

    async def process(self, task: AgentTask) -> AgentResponse:
        """Classify user intent and determine routing."""
        try:
            input_data = task.input_data
            user_query = input_data.get("query", "")

            if not user_query:
                return self.create_response(
                    success=False, content="", error_message="No query provided for intent classification"
                )

            # Simple rule-based classification for workshop demo
            classification = self._classify_intent(user_query.lower())

            return self.create_response(
                success=True,
                content=classification,
                reasoning=[classification.get("reasoning", "")],
                metadata={"original_query": user_query, "processing_method": "rule_based_demo"},
            )

        except Exception as e:
            return self.create_response(success=False, content="", error_message=f"Intent classification failed: {e!s}")

    def _classify_intent(self, query: str) -> dict[str, Any]:
        """Simple rule-based intent classification for demo."""

        # Summarization keywords
        summarize_keywords = ["summarize", "summary", "main points", "overview", "key concepts"]
        if any(keyword in query for keyword in summarize_keywords):
            return {
                "intent": "SUMMARIZER",
                "confidence": 90,
                "entities": {"action": "summarize"},
                "reasoning": "Query contains summarization keywords",
            }

        # Research keywords
        research_keywords = ["research", "find information", "look up", "web search", "external"]
        if any(keyword in query for keyword in research_keywords):
            return {
                "intent": "RESEARCH",
                "confidence": 85,
                "entities": {"action": "research"},
                "reasoning": "Query requests external information lookup",
            }

        # Flashcard keywords
        flashcard_keywords = ["flashcard", "quiz", "test me", "study cards", "anki", "memorize"]
        if any(keyword in query for keyword in flashcard_keywords):
            return {
                "intent": "FLASHCARD",
                "confidence": 88,
                "entities": {"action": "create_flashcards"},
                "reasoning": "Query requests study materials creation",
            }

        # Default to RAG Q&A for other queries
        return {
            "intent": "RAG_QA",
            "confidence": 75,
            "entities": {"action": "question_answering"},
            "reasoning": "Default classification for document-based questions",
        }

    def get_capabilities(self) -> list[str]:
        """Return classifier capabilities."""
        return [
            "intent_classification",
            "query_routing",
            "entity_extraction",
            "confidence_scoring",
            "multi_agent_coordination",
        ]

    def validate_input(self, input_data: dict[str, Any]) -> bool:
        """Validate classification input."""
        return "query" in input_data and input_data["query"].strip()
