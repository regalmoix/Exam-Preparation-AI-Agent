from __future__ import annotations

import asyncio

from agents import Agent
from agents import Runner
from agents import function_tool
from pydantic import BaseModel


# ========== TOOLS ==========


@function_tool
def search_course_materials(topic: str) -> str:
    """Search through course materials and textbooks."""
    materials = {
        "algorithms": "Big-O notation, sorting algorithms, graph traversal...",
        "databases": "SQL, normalization, ACID properties, indexing...",
        "networks": "TCP/IP, HTTP, DNS, routing protocols...",
    }
    return materials.get(topic.lower(), "Material not found")


@function_tool
def generate_quiz(topic: str, difficulty: str) -> str:
    """Generate practice quiz questions."""
    return f"Generated {difficulty} quiz on {topic}: Q1: ..., Q2: ..., Q3: ..."


@function_tool
def check_assignment_deadline(course: str) -> str:
    """Check upcoming assignment deadlines."""
    deadlines = {"algorithms": "Assignment 3 due Nov 15", "databases": "Project due Nov 20"}
    return deadlines.get(course.lower(), "No upcoming deadlines")


# ========== STRUCTURED OUTPUTS ==========


class StudyPlan(BaseModel):
    topic: str
    concepts_to_review: list[str]
    study_time_estimate: str
    resources: list[str]


class QuizResults(BaseModel):
    topic: str
    questions: list[str]
    difficulty: str
    time_limit: str


# ========== SPECIALIST AGENTS ==========

# Agent 1: Study planner
study_planner_agent = Agent(
    name="Study Planner",
    handoff_description="Creates personalized study plans and schedules",
    instructions="""
    You help students create effective study plans.

    Use search_course_materials to understand what needs to be studied.
    Use check_assignment_deadline to incorporate deadlines.

    Create comprehensive study plans with:
    - Key concepts to focus on
    - Time estimates
    - Recommended resources
    """,
    tools=[search_course_materials, check_assignment_deadline],
    output_type=StudyPlan,
)

# Agent 2: Quiz generator
quiz_agent = Agent(
    name="Quiz Generator",
    handoff_description="Creates practice quizzes and tests",
    instructions="""
    You generate practice quizzes for students.

    Use generate_quiz tool to create questions.
    Adjust difficulty based on student needs.
    Provide clear, educational questions.
    """,
    tools=[generate_quiz],
    output_type=QuizResults,
)

# Agent 3: Content expert
content_agent = Agent(
    name="Content Expert",
    handoff_description="Answers questions about course material",
    instructions="""
    You are an expert tutor who answers student questions.

    Use search_course_materials to find relevant information.
    Explain concepts clearly with examples.
    Break down complex topics into simple terms.
    """,
    tools=[search_course_materials],
)

# ========== COORDINATOR AGENT ==========

triage_agent = Agent(
    name="Study Assistant Coordinator",
    instructions="""
    You are the main coordinator for a study assistant system.

    Analyze student requests and delegate to the right specialist:

    1. **Study Planner** - For creating study schedules and plans
       Keywords: "study plan", "schedule", "how to study", "organize"

    2. **Quiz Generator** - For practice problems and quizzes
       Keywords: "quiz", "practice", "test", "questions"

    3. **Content Expert** - For explaining concepts and answering questions
       Keywords: "explain", "what is", "how does", "understand"

    Always handoff to the appropriate specialist. Be friendly and encouraging!
    """,
    handoffs=[study_planner_agent, quiz_agent, content_agent],
)


# ========== MAIN PROGRAM ==========


async def main():
    queries = [
        "I need help creating a study plan for my algorithms exam next week",
        "Can you explain what Big-O notation is?",
        "Generate a practice quiz on databases",
    ]

    for query in queries:
        print("\n" + "=" * 60)
        print(f"📝 STUDENT QUERY: {query}")
        print("=" * 60)

        result = await Runner.run(triage_agent, query)

        if isinstance(result.final_output, StudyPlan):
            plan = result.final_output
            print(f"\n📚 STUDY PLAN: {plan.topic}")
            print(f"⏰ Time Needed: {plan.study_time_estimate}")
            print("\n📖 Concepts to Review:")
            for concept in plan.concepts_to_review:
                print(f"   • {concept}")
            print("\n📚 Resources:")
            for resource in plan.resources:
                print(f"   • {resource}")

        elif isinstance(result.final_output, QuizResults):
            quiz = result.final_output
            print(f"\n📝 QUIZ: {quiz.topic}")
            print(f"🎯 Difficulty: {quiz.difficulty}")
            print(f"⏱️  Time Limit: {quiz.time_limit}")
            print("\n❓ Questions:")
            for i, q in enumerate(quiz.questions, 1):
                print(f"   {i}. {q}")

        else:
            print(f"\n💡 ANSWER:\n{result.final_output}")

        print("\n")


if __name__ == "__main__":
    asyncio.run(main())
