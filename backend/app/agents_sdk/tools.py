"""Custom tools for the Study Assistant agents."""

from __future__ import annotations

from typing import Any

from agents import FileSearchTool
from agents import WebSearchTool
from agents import function_tool

from ..services.config import config


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


file_search_tool = FileSearchTool(vector_store_ids=[config.exam_prep_vector_store_id], max_num_results=3)
web_search_tool = WebSearchTool(search_context_size="medium")
