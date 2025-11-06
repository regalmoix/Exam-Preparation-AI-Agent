from __future__ import annotations

import asyncio

from agents import Agent
from agents import Runner
from agents import function_tool
from pydantic import BaseModel


# Define structured output for study notes
class StudyNotes(BaseModel):
    topic: str
    key_concepts: list[str]
    summary: str
    practice_questions: list[str]


# Create a simple knowledge retrieval tool
@function_tool
def search_notes(topic: str) -> str:
    """
    Search through study materials for a topic.

    Args:
        topic: The subject or concept to search for
    """
    # Simulated knowledge base
    print("Searching for:", topic)

    knowledge = {
        "data structures": "Arrays: contiguous memory, O(1) access. Linked Lists: dynamic, O(n) access. Trees: hierarchical structure.",
        "algorithms": "Sorting: O(n log n) optimal. Searching: Binary search O(log n) on sorted data.",
        "databases": "ACID properties: Atomicity, Consistency, Isolation, Durability. SQL for relational DBs.",
    }

    return knowledge.get(topic.lower(), "Topic not found in notes.")


# Create the study assistant agent
study_assistant = Agent(
    name="Study Assistant",
    instructions="""
    You are a helpful study assistant for computer science students.

    When a student asks about a topic:
    1. Search the notes using the search_notes tool
    2. Create comprehensive study notes with:
       - Key concepts (3-5 bullet points)
       - A clear summary (2-3 sentences)
       - Practice questions (2-3 questions)

    Be encouraging and explain concepts clearly!
    """,
    tools=[search_notes],
    output_type=StudyNotes,
)


async def main():
    # Student asks a question
    result = await Runner.run(study_assistant, "Help me study data structures")

    # Get structured output
    notes: StudyNotes = result.final_output

    print(f"\n📚 {notes.topic.upper()}\n")
    print("Key Concepts:")
    for i, concept in enumerate(notes.key_concepts, 1):
        print(f"  {i}. {concept}")

    print("\n📝 Summary:")
    print(f"  {notes.summary}")

    print("\n❓ Practice Questions:")
    for i, q in enumerate(notes.practice_questions, 1):
        print(f"  {i}. {q}")


if __name__ == "__main__":
    asyncio.run(main())
