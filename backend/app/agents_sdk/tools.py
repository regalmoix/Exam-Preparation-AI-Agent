"""Custom tools for the Study Assistant agents."""

from __future__ import annotations

from typing import Any

from agents import FileSearchTool
from agents import HostedMCPTool
from agents import WebSearchTool
from agents import function_tool

from backend.app.services.config import config


# Custom function tools for study assistant
@function_tool
def store_research_summary(research_summary: str, topic: str, sources: list[str]) -> dict[str, Any]:
    """Store research summary for future reference."""
    # In a real implementation, this would save to database/vector store
    return {
        "status": "stored",
        "topic": topic,
        "summary_length": len(research_summary),
        "source_count": len(sources),
        "storage_id": f"research_{hash(research_summary) % 10000}",
    }


@function_tool
def create_flashcard_deck(deck_name: str, card_count: int, difficulty: str = "medium") -> dict[str, Any]:
    """Create a flashcard deck with the given parameters."""
    return {
        "deck_id": f"deck_{hash(deck_name) % 10000}",
        "deck_name": deck_name,
        "card_count": card_count,
        "difficulty": difficulty,
        "status": "created",
        "anki_ready": True,
    }


@function_tool
def extract_document_summary(document_content: str, focus_areas: list[str]) -> dict[str, Any]:
    """Extract key information from document content for summarization."""
    # This would typically use the FileSearchTool in a real implementation
    return {
        "extraction_status": "completed",
        "content_length": len(document_content),
        "focus_areas_used": focus_areas or [],
        "key_sections_found": 3,
        "summary_ready": True,
    }


file_search_tool = FileSearchTool(vector_store_ids=[config.exam_prep_vector_store_id], max_num_results=3)
web_search_tool = WebSearchTool(search_context_size="high", user_location={"country": "US", "type": "approximate"})
anki_mcp_tool = HostedMCPTool(
    tool_config={
        "type": "mcp",
        "server_label": "anki_mcp_server",
        "server_url": "http://localhost:8765",
        "server_description": "Anki MCP Server for flashcard management",
        "allowed_tools": [
            "sync",
            "list_decks",
            "create_deck",
            "get_due_cards",
            "present_card",
            "rate_card",
            "modelNames",
            "modelFieldNames",
            "modelStyling",
            "createModel",
            "updateModelStyling",
            "addNote",
            "findNotes",
            "notesInfo",
            "updateNoteFields",
            "deleteNotes",
            "mediaActions",
            "guiBrowse",
            "guiSelectCard",
            "guiSelectedNotes",
            "guiAddCards",
            "guiEditNote",
            "guiDeckOverview",
            "guiDeckBrowser",
            "guiCurrentCard",
            "guiShowQuestion",
            "guiShowAnswer",
            "guiUndo",
        ],
        "require_approval": "always",
    }
)
