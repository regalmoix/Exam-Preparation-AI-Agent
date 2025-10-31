"""Document summarization agent for the AI Study Assistant."""

from __future__ import annotations

from typing import Any

from .base import AgentResponse
from .base import AgentTask
from .base import AgentType
from .base import BaseStudyAgent


class SummarizerAgent(BaseStudyAgent):
    """Agent responsible for summarizing uploaded documents."""

    def __init__(self):
        super().__init__(AgentType.SUMMARIZER)

    async def process(self, task: AgentTask) -> AgentResponse:
        """Process document summarization task."""
        try:
            input_data = task.input_data
            document_id = input_data.get("document_id")
            document_content = input_data.get("content", "")

            if not document_id and not document_content:
                return self.create_response(
                    success=False, content="", error_message="No document ID or content provided for summarization"
                )

            # For workshop demo, return a structured summary
            summary_content = {
                "document_id": document_id,
                "main_topic": "Document Summary Analysis",
                "key_concepts": [
                    "Concept 1: Key learning objective from the document",
                    "Concept 2: Important methodology or framework discussed",
                    "Concept 3: Critical insights for student understanding",
                ],
                "study_notes": [
                    "Focus on understanding the relationship between concepts",
                    "Pay attention to practical applications mentioned",
                    "Review the examples provided for better comprehension",
                ],
                "citations": [
                    {"text": "Important quote or reference from the document", "page": 1, "section": "Introduction"}
                ],
                "summary": "This document covers fundamental concepts essential for student learning. The material presents structured information that builds upon core principles and provides practical applications for better understanding.",
            }

            return self.create_response(
                success=True,
                content=summary_content,
                metadata={
                    "processing_time": "2.3s",
                    "word_count": len(str(summary_content)),
                    "document_type": input_data.get("document_type", "unknown"),
                    "focus_areas": input_data.get("focus_areas", []),
                },
            )

        except Exception as e:
            return self.create_response(success=False, content="", error_message=f"Summarization failed: {e!s}")

    def get_capabilities(self) -> list[str]:
        """Return summarizer capabilities."""
        return [
            "document_summarization",
            "key_concept_extraction",
            "study_note_generation",
            "citation_extraction",
            "academic_content_analysis",
        ]

    def validate_input(self, input_data: dict[str, Any]) -> bool:
        """Validate summarization input."""
        return "document_id" in input_data or "content" in input_data
