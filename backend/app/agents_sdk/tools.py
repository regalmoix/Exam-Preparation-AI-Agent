"""Custom tools for the Study Assistant agents."""

from __future__ import annotations

from typing import Any

from agents import FileSearchTool
from agents import WebSearchTool
from agents import function_tool

from ..services.config import config
from ..services.vector_store_service import vector_store_service


@function_tool
async def store_research_data(research_detailed_text: str, filename: str) -> dict[str, Any]:
    """
    Store research summary for future reference. Call this always after using the `web_search_tool`
    The input `research_detailed_text` must be the web search data, and use the research topic / short summary as the `filename`

    Args:
        research_detailed_text (str): The web search data, as displayed to the user directly. Store the detailed text of the research
        filename (str): The short topic of research. Max length 20 characters
    """
    filename = f"{filename}.txt"
    print(f"Storing research summary for {filename=}, {research_detailed_text=}")
    data = await vector_store_service.add_file_to_vector_store(research_detailed_text.encode(), filename, ".txt")
    print("Done")
    return {
        "status": "stored",
        "topic": filename,
        "summary_length": len(research_detailed_text),
        **data,
    }


file_search_tool = FileSearchTool(vector_store_ids=[config.exam_prep_vector_store_id], max_num_results=3)
web_search_tool = WebSearchTool(search_context_size="medium")
