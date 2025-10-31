"""Agent workflow endpoints for the AI Study Assistant."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from fastapi import HTTPException
from pydantic import BaseModel

from ..agents_sdk import StudyAgentRunner


router = APIRouter()

# Initialize the agent runner
agent_runner = StudyAgentRunner()


class WorkflowRequest(BaseModel):
    """Request model for agent workflow execution."""

    message: str
    user_id: str | None = None
    session_id: str | None = None


class IntentClassificationRequest(BaseModel):
    """Request model for intent classification only."""

    query: str
    user_id: str | None = None


class QueryRequest(BaseModel):
    """Request model for direct Q&A queries."""

    query: str
    user_id: str | None = None


class ResearchRequest(BaseModel):
    """Request model for research queries."""

    query: str
    save_to_vectorstore: bool = False
    user_id: str | None = None


@router.post("/workflow")
async def execute_workflow(request: WorkflowRequest) -> dict[str, Any]:
    """Execute the full agent workflow: classify intent and route to appropriate agent."""
    try:
        result = await agent_runner.run_workflow(
            message=request.message,
            user_id=request.user_id,
            session_id=request.session_id,
        )

        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error_message"])

        return {
            "success": True,
            "workflow_result": result["workflow_result"],
            "task_id": result["task_id"],
            "message": "Workflow executed successfully",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workflow execution failed: {e!s}")


@router.post("/classify-intent")
async def classify_intent(request: IntentClassificationRequest) -> dict[str, Any]:
    """Classify user intent without executing the workflow."""
    try:
        result = await agent_runner.classify_intent(
            query=request.query,
            user_id=request.user_id,
        )

        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error_message"])

        return {
            "success": True,
            "classification": result["classification"],
            "reasoning": result["reasoning"],
            "task_id": result["task_id"],
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Intent classification failed: {e!s}")


@router.post("/query")
async def answer_query(request: QueryRequest) -> dict[str, Any]:
    """Answer a question using the RAG Q&A agent and knowledge base."""
    try:
        result = await agent_runner.answer_query(
            query=request.query,
            user_id=request.user_id,
        )

        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error_message"])

        return {
            "success": True,
            "answer": result["answer"],
            "reasoning": result["reasoning"],
            "metadata": result["metadata"],
            "task_id": result["task_id"],
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Q&A failed: {e!s}")


@router.post("/research")
async def conduct_research(request: ResearchRequest) -> dict[str, Any]:
    """Conduct research using the research agent."""
    try:
        result = await agent_runner.conduct_research(
            query=request.query,
            save_to_vectorstore=request.save_to_vectorstore,
            user_id=request.user_id,
        )

        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error_message"])

        return {
            "success": True,
            "research_results": result["research_results"],
            "reasoning": result["reasoning"],
            "metadata": result["metadata"],
            "task_id": result["task_id"],
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Research failed: {e!s}")


@router.get("/agents/capabilities")
async def get_agent_capabilities() -> dict[str, Any]:
    """Get information about all available agents and their capabilities."""
    return agent_runner.get_agent_capabilities()


@router.get("/status")
async def get_workflow_status() -> dict[str, Any]:
    """Get the current status of the agent workflow system."""
    return {
        "status": "active",
        "agents_available": len(agent_runner.agents),
        "agents": list(agent_runner.agents.keys()),
        "model_settings": {
            "temperature": agent_runner.model_settings.temperature,
            "max_tokens": agent_runner.model_settings.max_tokens,
        },
        "workflow_features": [
            "Intent classification",
            "Automatic agent routing",
            "RAG-based Q&A",
            "Web research",
            "Document summarization",
            "Flashcard generation",
        ],
        "integration_status": "production_ready",
    }
