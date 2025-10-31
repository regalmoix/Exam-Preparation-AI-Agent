"""Study agent endpoints for the AI Study Assistant Workshop."""

from __future__ import annotations

from typing import Any
from uuid import uuid4

from fastapi import APIRouter
from fastapi import HTTPException
from pydantic import BaseModel

from ..agents.base import AgentTask
from ..agents.base import TaskPriority
from ..agents.flashcard import FlashcardAgent
from ..agents.intent_classifier import IntentClassifierAgent
from ..agents.research import ResearchAgent
from ..agents.summarizer import SummarizerAgent


router = APIRouter()

# Initialize agents
summarizer_agent = SummarizerAgent()
intent_classifier_agent = IntentClassifierAgent()
research_agent = ResearchAgent()
flashcard_agent = FlashcardAgent()


class SummarizeRequest(BaseModel):
    """Request model for document summarization."""

    document_id: str
    document_type: str | None = None
    focus_areas: list[str] | None = None


class IntentClassificationRequest(BaseModel):
    """Request model for intent classification."""

    query: str
    user_id: str | None = None
    session_id: str | None = None


class ChatRequest(BaseModel):
    """Request model for intelligent chat routing."""

    message: str
    user_id: str | None = None
    session_id: str | None = None
    context: dict[str, Any] | None = None


class ResearchRequest(BaseModel):
    """Request model for research queries."""

    query: str
    save_to_vectorstore: bool = False
    user_id: str | None = None
    session_id: str | None = None


class FlashcardRequest(BaseModel):
    """Request model for flashcard generation."""

    document_id: str
    card_count: int = 10
    difficulty: str = "medium"  # easy, medium, hard
    deck_name: str = "Study Deck"
    user_id: str | None = None


# Workshop Phase 1: Document Summarization
@router.post("/summarize")
async def summarize_document(request: SummarizeRequest) -> dict[str, Any]:
    """
    **Workshop Phase 1: Upload & Summarize**

    Generate an AI-powered summary of uploaded study materials.
    Perfect for students to quickly understand key concepts from lectures and readings.
    """
    try:
        task = AgentTask(
            task_id=str(uuid4()),
            agent_type=summarizer_agent.agent_type,
            priority=TaskPriority.MEDIUM,
            input_data={
                "document_id": request.document_id,
                "document_type": request.document_type,
                "focus_areas": request.focus_areas or [],
            },
        )

        response = await summarizer_agent.process(task)

        if not response.success:
            raise HTTPException(status_code=500, detail=response.error_message)

        return {"success": True, "summary": response.content, "metadata": response.metadata, "task_id": task.task_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summarization failed: {e!s}")


@router.get("/summaries/{document_id}")
async def get_document_summary(document_id: str) -> dict[str, Any]:
    """
    Retrieve existing summary for a document.
    Useful for workshop participants to see previously generated summaries.
    """
    # This would typically fetch from a database
    # For workshop demo, return a sample response
    return {
        "document_id": document_id,
        "summary": {
            "main_topic": "Sample document summary",
            "key_concepts": ["Concept 1", "Concept 2"],
            "study_notes": ["Important note 1", "Important note 2"],
            "citations": [],
        },
        "created_at": "2025-10-30T22:00:00Z",
        "status": "completed",
    }


# Workshop Phase 5: Intent Classification & Routing
@router.post("/classify-intent")
async def classify_user_intent(request: IntentClassificationRequest) -> dict[str, Any]:
    """
    **Workshop Phase 5: Intent Classification**

    Classify student queries and route them to appropriate specialized agents.
    Demonstrates how AI can understand context and direct queries intelligently.
    """
    try:
        task = AgentTask(
            task_id=str(uuid4()),
            agent_type=intent_classifier_agent.agent_type,
            priority=TaskPriority.HIGH,
            input_data={"query": request.query, "user_id": request.user_id, "session_id": request.session_id},
        )

        response = await intent_classifier_agent.process(task)

        if not response.success:
            raise HTTPException(status_code=500, detail=response.error_message)

        return {
            "success": True,
            "classification": response.content,
            "reasoning": response.reasoning,
            "task_id": task.task_id,
            "next_action": {
                "recommended_agent": response.content.get("intent"),
                "confidence": response.content.get("confidence"),
                "parameters": response.content.get("entities", {}),
            },
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Intent classification failed: {e!s}")


@router.post("/chat/smart-route")
async def smart_chat_routing(request: ChatRequest) -> dict[str, Any]:
    """
    **Workshop Integration: Smart Chat Routing**

    Combines intent classification with agent routing for seamless student experience.
    Shows how multiple AI agents work together in a real study assistant.
    """
    try:
        # Step 1: Classify intent
        classification_task = AgentTask(
            task_id=str(uuid4()),
            agent_type=intent_classifier_agent.agent_type,
            priority=TaskPriority.HIGH,
            input_data={"query": request.message, "user_id": request.user_id, "session_id": request.session_id},
        )

        classification = await intent_classifier_agent.process(classification_task)

        if not classification.success:
            raise HTTPException(status_code=500, detail="Failed to classify intent")

        intent_data = classification.content
        agent_type = intent_data.get("intent")
        confidence = intent_data.get("confidence", 0)

        # Step 2: Route to appropriate agent based on classification
        response_data = {
            "message_id": str(uuid4()),
            "classified_intent": agent_type,
            "confidence": confidence,
            "reasoning": classification.reasoning,
        }

        # For workshop demo, return routing information
        if agent_type == "SUMMARIZER":
            response_data["agent_response"] = {
                "type": "summarization_prompt",
                "message": "I can help you summarize your study materials. Which document would you like me to summarize?",
                "next_steps": ["document_selection", "summarization"],
            }
        elif agent_type == "RESEARCH":
            response_data["agent_response"] = {
                "type": "research_prompt",
                "message": "I'll help you research additional information. What topic would you like me to look up?",
                "next_steps": ["web_search", "source_compilation"],
            }
        elif agent_type == "FLASHCARD":
            response_data["agent_response"] = {
                "type": "flashcard_prompt",
                "message": "I can create flashcards to help you study. Based on which materials should I generate them?",
                "next_steps": ["material_selection", "flashcard_generation"],
            }
        else:  # RAG_QA
            response_data["agent_response"] = {
                "type": "qa_response",
                "message": "I'll search through your uploaded materials to answer your question.",
                "next_steps": ["document_search", "answer_generation"],
            }

        return response_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Smart routing failed: {e!s}")


# Workshop Phase 3: Research Agent
@router.post("/research/query")
async def conduct_research(request: ResearchRequest) -> dict[str, Any]:
    """
    **Workshop Phase 3: Research Agent**

    Conduct web research to find additional information about study topics.
    Validates sources and synthesizes findings for educational use.
    """
    try:
        task = AgentTask(
            task_id=str(uuid4()),
            agent_type=research_agent.agent_type,
            priority=TaskPriority.MEDIUM,
            input_data={
                "query": request.query,
                "save_to_vectorstore": request.save_to_vectorstore,
                "user_id": request.user_id,
                "session_id": request.session_id,
            },
        )

        response = await research_agent.process(task)

        if not response.success:
            raise HTTPException(status_code=500, detail=response.error_message)

        return {
            "success": True,
            "research_results": response.content,
            "sources": response.sources,
            "reasoning": response.reasoning,
            "metadata": response.metadata,
            "task_id": task.task_id,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Research failed: {e!s}")


@router.get("/research/results/{task_id}")
async def get_research_results(task_id: str) -> dict[str, Any]:
    """
    Retrieve research results by task ID.
    Useful for workshop participants to access previous research.
    """
    # This would typically fetch from a database
    # For workshop demo, return sample response
    return {
        "task_id": task_id,
        "status": "completed",
        "research_results": {
            "synthesis": "Research findings and analysis would appear here",
            "key_findings": ["Finding 1", "Finding 2", "Finding 3"],
            "sources": [],
        },
        "created_at": "2025-10-30T22:00:00Z",
    }


# Workshop Phase 4: Flashcard Generation with MCP
@router.post("/flashcards/generate")
async def generate_flashcards(request: FlashcardRequest) -> dict[str, Any]:
    """
    **Workshop Phase 4: Flashcard Generation**

    Generate AI-powered flashcards from study materials and prepare for Anki integration.
    Demonstrates MCP (Model Context Protocol) usage for external tool integration.
    """
    try:
        task = AgentTask(
            task_id=str(uuid4()),
            agent_type=flashcard_agent.agent_type,
            priority=TaskPriority.MEDIUM,
            input_data={
                "document_id": request.document_id,
                "card_count": request.card_count,
                "difficulty": request.difficulty,
                "deck_name": request.deck_name,
                "user_id": request.user_id,
            },
        )

        response = await flashcard_agent.process(task)

        if not response.success:
            raise HTTPException(status_code=500, detail=response.error_message)

        return {
            "success": True,
            "flashcard_deck": response.content,
            "reasoning": response.reasoning,
            "metadata": response.metadata,
            "task_id": task.task_id,
            "mcp_integration": {
                "anki_ready": True,
                "export_available": True,
                "supported_formats": ["anki", "csv", "json"],
            },
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Flashcard generation failed: {e!s}")


@router.post("/flashcards/export-anki")
async def export_to_anki(request: dict[str, Any]) -> dict[str, Any]:
    """
    **Workshop Phase 4: MCP Anki Integration**

    Export flashcards to Anki using Model Context Protocol.
    Demonstrates real-world integration with external study tools.
    """
    try:
        deck_id = request.get("deck_id")
        if not deck_id:
            raise HTTPException(status_code=400, detail="Deck ID required for Anki export")

        # Simulate MCP Anki export
        export_result = {
            "export_status": "success",
            "anki_deck_id": f"anki_{deck_id}",
            "cards_exported": request.get("card_count", 10),
            "mcp_protocol": "1.0",
            "sync_status": "completed",
            "next_steps": [
                "Open Anki application",
                "Sync with AnkiWeb (optional)",
                "Begin studying with spaced repetition",
            ],
        }

        return {
            "success": True,
            "export_result": export_result,
            "message": "Flashcards successfully exported to Anki via MCP",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Anki export failed: {e!s}")


@router.get("/flashcards/deck/{deck_id}")
async def get_flashcard_deck(deck_id: str) -> dict[str, Any]:
    """
    Retrieve flashcard deck information.
    Useful for workshop participants to review generated cards.
    """
    return {
        "deck_id": deck_id,
        "deck_name": "Study Deck",
        "card_count": 10,
        "difficulty": "medium",
        "status": "ready",
        "anki_compatible": True,
        "created_at": "2025-10-30T22:00:00Z",
    }


# Workshop utilities
@router.get("/agents/capabilities")
async def get_available_agents() -> dict[str, Any]:
    """
    Get information about all available study agents.
    Useful for workshop participants to understand the system architecture.
    """
    return {
        "agents": [
            {
                "type": "SUMMARIZER",
                "name": "Document Summarizer",
                "description": "Creates comprehensive summaries of study materials",
                "capabilities": summarizer_agent.get_capabilities(),
                "workshop_phase": 1,
            },
            {
                "type": "RESEARCH",
                "name": "Research Agent",
                "description": "Looks up additional information from reliable web sources",
                "capabilities": research_agent.get_capabilities(),
                "workshop_phase": 3,
            },
            {
                "type": "RAG_QA",
                "name": "Q&A Agent",
                "description": "Answers questions based on uploaded study materials",
                "capabilities": ["document_retrieval", "contextual_qa", "source_citing"],
                "workshop_phase": 2,
            },
            {
                "type": "FLASHCARD",
                "name": "Flashcard Generator",
                "description": "Creates study cards and integrates with Anki",
                "capabilities": flashcard_agent.get_capabilities(),
                "workshop_phase": 4,
            },
            {
                "type": "INTENT_CLASSIFIER",
                "name": "Intent Router",
                "description": "Classifies student queries and routes to appropriate agents",
                "capabilities": intent_classifier_agent.get_capabilities(),
                "workshop_phase": 5,
            },
        ],
        "workshop_info": {
            "total_phases": 5,
            "estimated_duration": "3-4 hours",
            "learning_objectives": [
                "Understanding AI agent architectures",
                "Building RAG systems for education",
                "Integrating multiple AI services",
                "Creating practical study tools",
            ],
        },
    }
