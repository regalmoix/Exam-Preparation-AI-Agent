"""Study Assistant agents using the agents SDK."""

from __future__ import annotations

from agents import Agent

from . import prompts
from .mcp import AnkiMCPServer
from .tools import file_search_tool
from .tools import store_research_summary
from .tools import web_search_tool


AnswerStudentQueryAgent = Agent(
    name="RAG Question Answer Agent",
    handoff_description="This agent can find the relevant information from document store to answer any query of the student. If the information is not available in the document store, it researches the internet to get information",
    instructions=prompts.QA_PROMPT,
    tools=[file_search_tool, web_search_tool, store_research_summary],
)


FlashcardAgent = Agent(
    name="Flashcard Agent",
    handoff_description="This agent can use Anki to create flashcards and quiz materials and decks.",
    instructions=prompts.FLASHCARD_PROMPT,
    tools=[file_search_tool],
    mcp_servers=[AnkiMCPServer],
)

TriageAgent = Agent(
    name="Triage Agent",
    instructions=prompts.TRIAGE_PROMPT,
    handoffs=[AnswerStudentQueryAgent, FlashcardAgent],
)
