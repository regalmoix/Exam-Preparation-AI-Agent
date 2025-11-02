"""Study Assistant agents using the agents SDK."""

from __future__ import annotations

from agents import Agent

from ..services.config import config
from . import prompts
from .models import IntentClassificationSchema
from .models import ResearchResultSchema
from .models import SummarySchema
from .tools import anki_mcp_tool
from .tools import create_flashcard_deck
from .tools import extract_document_summary
from .tools import file_search_tool
from .tools import store_research_summary
from .tools import web_search_tool


IntentClassifierAgent = Agent(
    name="Intent Classifier Agent",
    instructions=prompts.INTENT_CLASSIFIER_PROMPT,
    model=config.openai_model,
    output_type=IntentClassificationSchema,
)


SummarizerAgent = Agent(
    name="Document Summarizer Agent",
    instructions=prompts.SUMMARIZER_PROMPT,
    model=config.openai_model,
    tools=[file_search_tool, extract_document_summary],
    output_type=SummarySchema,
)


ResearchAgent = Agent(
    name="Research Agent",
    instructions=prompts.RESEARCH_PROMPT,
    model=config.openai_model,
    tools=[web_search_tool, store_research_summary],
    output_type=ResearchResultSchema,
)


RagQAAgent = Agent(
    name="RAG Q&A Agent",
    instructions=prompts.RAG_QA_PROMPT,
    model=config.openai_model,
    tools=[file_search_tool],
)


FlashcardGeneratorAgent = Agent(
    name="Flashcard Generator Agent",
    instructions=prompts.FLASHCARD_PROMPT,
    model=config.openai_model,
    tools=[file_search_tool, create_flashcard_deck, anki_mcp_tool],
    # Note: For flashcards, we'll return a custom response format in the runner
)
