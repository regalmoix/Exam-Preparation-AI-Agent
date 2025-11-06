# Building AI Agents: From LLMs to Multi-Agent Systems
## A Complete Guide for Computer Science Students

---

## Slide 1: Introduction - What You'll Learn Today

Welcome to the world of AI Agents! In this presentation, we'll take you from zero knowledge to building sophisticated multi-agent systems.

**Journey Overview:**
- 🧠 Understanding Large Language Models (LLMs)
- 💬 Chat Completion APIs
- 🤖 Introduction to AI Agents
- 🔧 Tools and Function Calling
- 📋 Structured Outputs
- 🎯 Building Single Agents
- 🤝 Multi-Agent Systems
- 🚀 Real-World Applications

**Prerequisites:** Basic Python knowledge (functions, async/await, classes)

---

## Slide 2: What is a Large Language Model (LLM)?

### Understanding LLMs

A **Large Language Model (LLM)** is a type of artificial intelligence trained on vast amounts of text data to understand and generate human-like text.

**Key Concepts:**

1. **Training Data**: LLMs learn from billions of documents (books, websites, code, etc.)
2. **Parameters**: Numbers (weights) that encode learned patterns (GPT-4 has ~1.7 trillion parameters)
3. **Tokens**: Text is broken into pieces called tokens (~4 characters per token)
4. **Context Window**: Amount of text the model can "remember" at once (e.g., 128K tokens)

**Popular LLMs:**
- OpenAI: GPT-4, GPT-4o, GPT-4o-mini
- Anthropic: Claude 3.5 Sonnet
- Google: Gemini Pro
- Meta: Llama 3

**What LLMs Can Do:**
- Understand and generate text
- Answer questions
- Write code
- Translate languages
- Summarize documents
- And much more!

**What LLMs Cannot Do (by default):**
- Access real-time information
- Perform calculations reliably
- Remember previous conversations
- Take actions in the real world

---

## Slide 3: Chat Completion API - Your First Interaction

### The Foundation: Chat Completion

The **Chat Completion API** is the most basic way to interact with an LLM. You send messages, and the LLM responds.

**Message Structure:**
```python
{
    "role": "user",      # Who is speaking: "user", "assistant", or "system"
    "content": "Hello!"  # The actual message text
}
```

**Roles Explained:**
- **system**: Instructions that guide the AI's behavior
- **user**: Messages from the human user
- **assistant**: Responses from the AI

### How It Works:

```
You → API → LLM → API → Response
```

1. You send a list of messages
2. The LLM processes them
3. The LLM generates a response
4. You receive the assistant's reply

---

## Slide 4: Code Example - Basic Chat Completion

### Let's Write Our First Program!

```python
import asyncio
from openai import AsyncOpenAI

# Initialize the OpenAI client
client = AsyncOpenAI(api_key="your-api-key-here")

async def basic_chat():
    """Simple chat completion example"""
    
    # Create a conversation
    messages = [
        {
            "role": "system",
            "content": "You are a helpful math tutor."
        },
        {
            "role": "user",
            "content": "What is 25 * 4?"
        }
    ]
    
    # Call the API
    response = await client.chat.completions.create(
        model="gpt-4o-mini",  # The model to use
        messages=messages,
        temperature=0.7,      # Creativity (0=focused, 1=creative)
    )
    
    # Extract the response
    answer = response.choices[0].message.content
    print(f"AI: {answer}")

# Run the example
if __name__ == "__main__":
    asyncio.run(basic_chat())
```

**Output:**
```
AI: 25 × 4 = 100. To solve this, you can think of it as 25 four times: 25 + 25 + 25 + 25 = 100!
```

**Key Parameters:**
- `model`: Which LLM to use
- `messages`: The conversation history
- `temperature`: Controls randomness (0.0-2.0)

---

## Slide 5: Multi-Turn Conversations

### Maintaining Context

LLMs are **stateless** - they don't remember previous conversations unless you provide the history!

### Example: Conversation Memory

```python
async def conversation_example():
    """Multi-turn conversation"""
    
    conversation = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]
    
    # First turn
    conversation.append({
        "role": "user",
        "content": "My name is Alice and I love Python."
    })
    
    response1 = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=conversation
    )
    
    # Add assistant's response to history
    conversation.append({
        "role": "assistant",
        "content": response1.choices[0].message.content
    })
    
    # Second turn - referencing previous context
    conversation.append({
        "role": "user",
        "content": "What's my name and favorite programming language?"
    })
    
    response2 = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=conversation
    )
    
    print(response2.choices[0].message.content)
    # Output: "Your name is Alice and your favorite programming language is Python!"
```

**Important**: Always include the full conversation history for context!

---

## Slide 6: What Are AI Agents?

### From Chat to Agents

A **Chat Completion** is like having a conversation.  
An **AI Agent** is like having an assistant who can actually DO things!

### The Agent Paradigm

```
Traditional Program: Input → Logic → Output
AI Agent: Goal → Think & Act → Use Tools → Achieve Goal
```

**What Makes Something an Agent?**

1. **Autonomy**: Can make decisions independently
2. **Tool Use**: Can call functions and use external resources
3. **Goal-Oriented**: Works towards completing a task
4. **Iterative**: Can plan, act, observe, and adapt

### Real-World Analogy

Imagine asking an assistant to "book a flight":
- **Chat Completion**: "Here's how you can book a flight..."
- **AI Agent**: *Actually searches flights, compares prices, and books it*

---

## Slide 7: Tools - Giving Agents Superpowers

### What Are Tools?

**Tools** (also called "function calling") allow LLMs to execute code and interact with external systems.

### How Tools Work:

```
1. Agent receives task: "What's the weather in Tokyo?"
2. Agent thinks: "I need to check the weather"
3. Agent calls: get_weather(city="Tokyo")
4. Function executes: Returns weather data
5. Agent responds: "It's sunny and 20°C in Tokyo!"
```

### Tool Definition Structure:

```python
{
    "name": "get_weather",
    "description": "Get current weather for a city",
    "parameters": {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "The city name"
            }
        },
        "required": ["city"]
    }
}
```

The LLM reads this schema and knows when and how to call the function!

---

## Slide 8: Code Example - Your First Tool

### Building a Simple Tool

```python
from agents import Agent, Runner, function_tool
from pydantic import BaseModel
import asyncio

# Step 1: Define the tool output structure
class Weather(BaseModel):
    city: str
    temperature: str
    conditions: str

# Step 2: Create a tool using the @function_tool decorator
@function_tool
def get_weather(city: str) -> Weather:
    """
    Get the current weather for a given city.
    
    Args:
        city: Name of the city to get weather for
    
    Returns:
        Weather information including temperature and conditions
    """
    # In real life, this would call a weather API
    return Weather(
        city=city,
        temperature="20°C",
        conditions="Sunny"
    )

# Step 3: Create an agent with the tool
weather_agent = Agent(
    name="Weather Assistant",
    instructions="You are a helpful weather assistant. Use the get_weather tool to provide weather information.",
    tools=[get_weather]  # Give the agent access to the tool
)

# Step 4: Run the agent
async def main():
    result = await Runner.run(
        weather_agent,
        "What's the weather like in Tokyo?"
    )
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())
```

**What happens behind the scenes:**
1. Agent receives the question
2. Agent decides to call `get_weather("Tokyo")`
3. Function executes and returns data
4. Agent formats a natural language response

---

## Slide 9: Structured Outputs

### Ensuring Consistent Responses

Sometimes you need the LLM to return data in a specific format (JSON, objects, etc.) instead of free text.

### Why Structured Outputs?

**Problem**: "Give me info about Paris"
- Unstructured: "Paris is the capital of France with a population of about 2.2 million..."
- Structured: `{"city": "Paris", "country": "France", "population": 2200000}`

**Benefits:**
- Easy to parse and use in code
- Guaranteed format
- Type safety
- Integration with databases and APIs

### Using Pydantic Models

```python
from pydantic import BaseModel, Field

class CityInfo(BaseModel):
    """Structured information about a city"""
    city: str = Field(description="The city name")
    country: str = Field(description="The country name")
    population: int = Field(description="Population count")
    famous_for: list[str] = Field(description="List of things the city is famous for")
    fun_fact: str = Field(description="An interesting fact")

# Create an agent with structured output
agent = Agent(
    name="City Expert",
    instructions="Provide detailed city information.",
    output_type=CityInfo  # Force structured output
)

# The response will be a CityInfo object, not text!
result = await Runner.run(agent, "Tell me about Paris")
city_data: CityInfo = result.final_output

print(f"{city_data.city}, {city_data.country}")
print(f"Population: {city_data.population:,}")
print(f"Famous for: {', '.join(city_data.famous_for)}")
```

---

## Slide 10: Code Example - Building a Study Assistant

### Real-World Agent Example

```python
from agents import Agent, Runner, function_tool
from pydantic import BaseModel
import asyncio

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
    knowledge = {
        "data structures": "Arrays: contiguous memory, O(1) access. Linked Lists: dynamic, O(n) access. Trees: hierarchical structure.",
        "algorithms": "Sorting: O(n log n) optimal. Searching: Binary search O(log n) on sorted data.",
        "databases": "ACID properties: Atomicity, Consistency, Isolation, Durability. SQL for relational DBs."
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
    output_type=StudyNotes
)

async def main():
    # Student asks a question
    result = await Runner.run(
        study_assistant,
        "Help me study data structures"
    )
    
    # Get structured output
    notes: StudyNotes = result.final_output
    
    print(f"\n📚 {notes.topic.upper()}\n")
    print("Key Concepts:")
    for i, concept in enumerate(notes.key_concepts, 1):
        print(f"  {i}. {concept}")
    
    print(f"\n📝 Summary:")
    print(f"  {notes.summary}")
    
    print(f"\n❓ Practice Questions:")
    for i, q in enumerate(notes.practice_questions, 1):
        print(f"  {i}. {q}")

if __name__ == "__main__":
    asyncio.run(main())
```

**This demonstrates:**
- Tool usage (search_notes)
- Structured outputs (StudyNotes)
- Clear instructions
- Practical application

---

## Slide 11: The OpenAI Agents SDK

### Why Use a Framework?

Building agents from scratch requires handling:
- Tool execution loops
- Error handling
- Conversation history management
- Streaming responses
- Debugging and tracing

**The OpenAI Agents SDK handles all of this!**

### Core Primitives

The SDK has just 4 main concepts:

1. **Agents**: LLMs with instructions and tools
2. **Tools**: Functions agents can call
3. **Handoffs**: Agents transferring tasks to other agents
4. **Sessions**: Automatic conversation history management

### Installation

```bash
pip install openai-agents
```

### SDK vs Raw API

| Feature | Raw API | Agents SDK |
|---------|---------|------------|
| Tool execution | Manual loop | Automatic |
| History management | Manual | Automatic (Sessions) |
| Multi-agent | Complex | Simple (Handoffs) |
| Debugging | Print statements | Built-in tracing |
| Streaming | Manual handling | Built-in |

---

## Slide 12: Agents SDK - Deep Dive

### Agent Anatomy

```python
from agents import Agent

agent = Agent(
    # Basic configuration
    name="Assistant",
    instructions="You are a helpful assistant",
    
    # Tools this agent can use
    tools=[tool1, tool2],
    
    # Other agents this can hand off to
    handoffs=[other_agent1, other_agent2],
    
    # Force structured output format
    output_type=MyPydanticModel,
    
    # Model configuration
    model="gpt-4o-mini",
    model_settings=ModelSettings(
        temperature=0.7,
        max_tokens=1000
    ),
    
    # How to handle tool results
    tool_use_behavior="run_llm_again",  # or "stop_on_first_tool"
    
    # Description for handoffs
    handoff_description="Specialist for handling X tasks"
)
```

### Running Agents

```python
from agents import Runner

# Synchronous
result = Runner.run_sync(agent, "Hello!")

# Asynchronous (recommended)
result = await Runner.run(agent, "Hello!")

# Streaming
result = Runner.run_streamed(agent, "Hello!")
async for event in result.stream_events():
    # Process events in real-time
    pass
```

---

## Slide 13: Code Example - Advanced Agent with Multiple Tools

### Building a Travel Assistant

```python
from agents import Agent, Runner, function_tool
from pydantic import BaseModel
import asyncio
import json

# Tool 1: Weather forecast
@function_tool
def get_weather_forecast(city: str, date: str) -> str:
    """Get weather forecast for a city on a specific date."""
    weather_db = {
        "Tokyo": "Sunny, 20-25°C",
        "Paris": "Rainy, 15-18°C",
        "New York": "Cloudy, 18-22°C"
    }
    return f"Weather in {city} on {date}: {weather_db.get(city, 'Data not available')}"

# Tool 2: Flight search
@function_tool
def search_flights(origin: str, destination: str, date: str) -> str:
    """Search for available flights."""
    flights = [
        {"airline": "SkyWays", "time": "08:00", "price": 350, "direct": True},
        {"airline": "OceanAir", "time": "14:30", "price": 280, "direct": False}
    ]
    return json.dumps(flights)

# Tool 3: Hotel search
@function_tool
def search_hotels(city: str, max_price: float = 500.0) -> str:
    """Search for hotels in a city."""
    hotels = [
        {"name": "City Center Hotel", "price": 199, "rating": 4.5},
        {"name": "Riverside Inn", "price": 149, "rating": 4.2}
    ]
    filtered = [h for h in hotels if h["price"] <= max_price]
    return json.dumps(filtered)

# Structured output
class TravelPlan(BaseModel):
    destination: str
    travel_dates: str
    weather_summary: str
    flight_recommendation: str
    hotel_recommendation: str
    estimated_budget: float

# Create the travel agent
travel_agent = Agent(
    name="Travel Planner",
    instructions="""
    You are a comprehensive travel planning assistant.
    
    When helping users plan trips:
    1. Ask about destination, dates, and budget if not provided
    2. Check weather using get_weather_forecast
    3. Search flights using search_flights
    4. Find hotels using search_hotels
    5. Create a complete travel plan with recommendations
    
    Always explain your recommendations and consider the user's budget!
    """,
    tools=[get_weather_forecast, search_flights, search_hotels],
    output_type=TravelPlan,
    model="gpt-4o-mini"
)

async def main():
    result = await Runner.run(
        travel_agent,
        "I want to travel to Tokyo next month. My budget is $2000."
    )
    
    plan: TravelPlan = result.final_output
    
    print(f"\n✈️ TRAVEL PLAN TO {plan.destination.upper()} ✈️")
    print(f"📅 Dates: {plan.travel_dates}")
    print(f"🌤️  Weather: {plan.weather_summary}")
    print(f"✈️ Flight: {plan.flight_recommendation}")
    print(f"🏨 Hotel: {plan.hotel_recommendation}")
    print(f"💰 Budget: ${plan.estimated_budget}")

if __name__ == "__main__":
    asyncio.run(main())
```

**Key Features:**
- Multiple tools working together
- Complex decision making
- Structured output for easy parsing
- Real-world use case

---

## Slide 14: Multi-Agent Systems - Introduction

### Why Multiple Agents?

As tasks become complex, a single agent can become:
- Overloaded with too many tools
- Confused about its role
- Less effective at specific tasks

**Solution: Specialist Agents!**

### Multi-Agent Architecture

```
                    ┌─────────────────┐
                    │  Triage Agent   │
                    │  (Coordinator)  │
                    └────────┬────────┘
                             │
                ┌────────────┼────────────┐
                │            │            │
         ┌──────▼──────┐ ┌──▼──────┐ ┌──▼──────────┐
         │   Flight    │ │  Hotel  │ │   Weather   │
         │  Specialist │ │ Expert  │ │  Specialist │
         └─────────────┘ └─────────┘ └─────────────┘
```

### Benefits:

1. **Specialization**: Each agent focuses on one domain
2. **Maintainability**: Easy to update/debug specific capabilities
3. **Scalability**: Add new specialists without affecting others
4. **Clarity**: Clear responsibility boundaries

---

## Slide 15: Handoffs - Agent Collaboration

### What Are Handoffs?

**Handoffs** allow one agent to transfer a task to another agent that's better suited for it.

### How Handoffs Work:

```python
# Define specialist agents
weather_agent = Agent(
    name="Weather Specialist",
    instructions="Provide detailed weather information",
    tools=[get_weather],
    handoff_description="Expert in weather forecasts and climate data"
)

flight_agent = Agent(
    name="Flight Specialist", 
    instructions="Help find and book flights",
    tools=[search_flights, book_flight],
    handoff_description="Expert in flight searches and bookings"
)

# Define coordinator with handoffs
coordinator = Agent(
    name="Travel Coordinator",
    instructions="""
    You coordinate travel planning.
    Handoff to specialists when users ask about:
    - Weather → Weather Specialist
    - Flights → Flight Specialist
    """,
    handoffs=[weather_agent, flight_agent]  # Can delegate to these
)
```

### The Handoff Process:

1. User asks coordinator: "What's the weather in Paris?"
2. Coordinator recognizes this is a weather question
3. Coordinator hands off to Weather Specialist
4. Weather Specialist handles the request
5. User continues conversation with Weather Specialist

---

## Slide 16: Code Example - Multi-Agent Study Assistant

### Building a Complete Study System

```python
from agents import Agent, Runner, function_tool
from pydantic import BaseModel
import asyncio

# ========== TOOLS ==========

@function_tool
def search_course_materials(topic: str) -> str:
    """Search through course materials and textbooks."""
    materials = {
        "algorithms": "Big-O notation, sorting algorithms, graph traversal...",
        "databases": "SQL, normalization, ACID properties, indexing...",
        "networks": "TCP/IP, HTTP, DNS, routing protocols..."
    }
    return materials.get(topic.lower(), "Material not found")

@function_tool
def generate_quiz(topic: str, difficulty: str) -> str:
    """Generate practice quiz questions."""
    return f"Generated {difficulty} quiz on {topic}: Q1: ..., Q2: ..., Q3: ..."

@function_tool
def check_assignment_deadline(course: str) -> str:
    """Check upcoming assignment deadlines."""
    deadlines = {
        "algorithms": "Assignment 3 due Nov 15",
        "databases": "Project due Nov 20"
    }
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
    output_type=StudyPlan
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
    output_type=QuizResults
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
    tools=[search_course_materials]
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
    handoffs=[study_planner_agent, quiz_agent, content_agent]
)

# ========== MAIN PROGRAM ==========

async def main():
    queries = [
        "I need help creating a study plan for my algorithms exam next week",
        "Can you explain what Big-O notation is?",
        "Generate a practice quiz on databases"
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
```

---

## Slide 17: Advanced Multi-Agent Patterns

### Pattern 1: Sequential Processing (Pipeline)

Agents work in sequence, each adding to the result:

```python
# Agent 1: Generates outline
outline_agent = Agent(
    name="Outline Creator",
    instructions="Create a story outline",
    output_type=str
)

# Agent 2: Checks quality
quality_checker = Agent(
    name="Quality Checker",
    instructions="Evaluate if the outline is good",
    output_type=QualityReport
)

# Agent 3: Writes final story
story_writer = Agent(
    name="Story Writer",
    instructions="Write the full story from the outline",
    output_type=str
)

# Sequential execution
outline = await Runner.run(outline_agent, "Write a sci-fi story")
quality = await Runner.run(quality_checker, outline.final_output)

if quality.final_output.is_good:
    story = await Runner.run(story_writer, outline.final_output)
    print(story.final_output)
```

### Pattern 2: Hierarchical (Manager-Worker)

```
       Manager Agent
          │
    ┌─────┼─────┐
    │     │     │
Worker Worker Worker
```

---

## Slide 18: Sessions - Managing Conversation History

### The Session Problem

Without sessions, you must manually track conversation history:

```python
# Manual history management (tedious!)
history = []
history.append({"role": "user", "content": "Hello"})
result = await Runner.run(agent, input=history)
history.append({"role": "assistant", "content": result.final_output})
history.append({"role": "user", "content": "What did I say?"})
result = await Runner.run(agent, input=history)
```

### Sessions to the Rescue!

```python
from agents import SQLiteSession, Runner

# Create a session
session = SQLiteSession(session_id="some_session_id")

# First interaction
result1 = await Runner.run(
    agent,
    input="My name is Alice",
    session=session  # Session tracks history
)

# Second interaction - agent remembers!
result2 = await Runner.run(
    agent,
    input="What's my name?",
    session=session  # Uses same session
)

print(result2.final_output)  # "Your name is Alice!"
```
---

## Slide 19: Tracing and Debugging

### Why Tracing?

With complex multi-agent systems, you need to understand:
- Which tools were called?
- What were the inputs/outputs?
- Where did errors occur?
- How long did each step take?

### Built-in Tracing

```python
from agents import trace, Runner
import logfire

# Setup tracing
logfire.configure()
logfire.instrument_openai_agents()

# Wrap operations in traces
async def process_query(query: str):
    with trace("Student Query Processing"):
        # This entire operation is traced
        result = await Runner.run(agent, query)
        return result

# Run and view traces at logfire.ai
await process_query("Explain binary trees")
```

### What You See in Traces:

```
Student Query Processing (2.3s)
├─ Agent Run: Triage Agent (0.3s)
│  └─ Handoff to Content Expert
├─ Agent Run: Content Expert (1.8s)
│  ├─ Tool Call: search_course_materials (0.2s)
│  │  ├─ Input: {"topic": "binary trees"}
│  │  └─ Output: "Binary trees are hierarchical..."
│  └─ LLM Call: gpt-4o-mini (1.5s)
└─ Final Output: "A binary tree is..." (0.2s)
```

---

## Slide 20: Real-World Example - Complete Study Assistant

Let's look at a production-ready example from the codebase:

### Architecture Overview

```
                    Triage Agent
                         │
           ┌─────────────┴─────────────┐
           │                           │
    QA Agent (RAG)              Notion Agent
           │                           │
    ┌──────┴──────┐            ┌──────┴──────┐
    │             │            │              │
File Search  Web Search    Search Pages  Create Pages
```

### Key Components:

**1. Tools:**
```python
# Built-in tool for file search
file_search_tool = FileSearchTool(
    vector_store_ids=["store_id"],
    max_num_results=3
)

# Built-in web search
web_search_tool = WebSearchTool(
    search_context_size="medium"
)

# Custom tool to store research
@function_tool
async def store_research_data(
    research_text: str,
    filename: str
) -> dict:
    """Store research for future reference"""
    # Add to vector store
    await vector_store.add_file(research_text, filename)
    return {"status": "stored"}
```

**2. Specialist Agents:**
```python
# RAG agent for answering questions
qa_agent = Agent(
    name="RAG Question Answer Agent",
    handoff_description="Finds relevant information from documents or internet",
    instructions="""
    Answer student queries using:
    1. file_search_tool for document store
    2. web_search_tool if not found
    3. store_research_data after web search
    
    Always cite sources!
    """,
    tools=[file_search_tool, web_search_tool, store_research_data]
)

# Notion agent for note-taking
notion_agent = Agent(
    name="Notion Agent",
    handoff_description="Manages notes in Notion workspace",
    instructions="Help students organize notes in Notion",
    mcp_servers=[NotionMCPServer]  # MCP integration
)
```

**3. Coordinator:**
```python
triage_agent = Agent(
    name="Triage Agent",
    instructions="""
    Route student queries:
    - Questions about study materials → QA Agent
    - Note-taking and organization → Notion Agent
    """,
    handoffs=[qa_agent, notion_agent]
)
```

---

## Slide 21: RAG - Retrieval Augmented Generation

### The Problem: LLMs Don't Know Everything

**Scenario:** Student asks: "What are the key concepts in Chapter 5 of my chemistry textbook?"

**Problem:**
- ❌ LLM wasn't trained on your specific document, cant directly access your filesystem
- ❌ LLM might hallucinate or give generic answers

**Solution: RAG (Retrieval Augmented Generation)**

### What is RAG? (Simple Explanation)

Think of RAG like an open-book exam for AI:

```
Regular LLM = Closed-book exam (only uses memory)
RAG = Open-book exam (can look up information before answering)
```

**RAG Process:**
1. **Store** your documents in a searchable database (Vector Store)
2. **Retrieve** relevant information when asked a question
3. **Augment** the LLM's answer with this retrieved information
4. **Generate** a response based on actual facts

### RAG in 3 Simple Steps

```
Question: "What is thermodynamics?"

Step 1 - RETRIEVE 📚
├─ Search vector store for "thermodynamics"
└─ Find: "Thermodynamics is the study of energy transfer..."

Step 2 - AUGMENT 🔧
├─ Add retrieved text to the prompt
└─ "Based on this content: [retrieved text], answer the question"

Step 3 - GENERATE 💬
└─ LLM generates answer using the actual course material!
```

### Key Components (Don't Worry About Details!)

**1. Vector Store**
- A special database that stores documents
- Think of it like a smart library catalog
- Can find similar content even if exact words don't match

**2. Embeddings**
- Mathematical representation of text
- Converts "What is thermodynamics?" into numbers
- Similar concepts have similar numbers (even with different words!)

**3. Similarity Search**
- Finds most relevant documents for a question
- Like Google search, but for your private documents

### Why RAG is Powerful

✅ **Accurate**: Uses your actual documents, not generic knowledge  
✅ **Up-to-date**: Can include latest information  
✅ **Verifiable**: Can cite sources  
✅ **Privacy**: Your documents stay private  
✅ **Expandable**: Add new documents anytime  

---

## Slide 22: Prompting Best Practices for AI Agents

### Why Prompting Matters

The quality of your agent depends heavily on how you prompt it!

**Bad Prompt** → Confused Agent → Poor Results  
**Good Prompt** → Clear Agent → Excellent Results

### Key Insight from OpenAI GPT-4.1 Research

Modern models like GPT-4.1 are **highly steerable** and follow instructions **more literally** than older models.

**What this means for you:**
- Be explicit about what you want
- Don't rely on the model "figuring it out"
- A single clear sentence can dramatically improve behavior

*Source: [OpenAI GPT-4.1 Prompting Guide](https://cookbook.openai.com/examples/gpt4-1_prompting_guide)*

---

### Best Practice 1: System Prompt Reminders for Agents

When building **agentic workflows**, always include these three key reminders:

#### 1️⃣ **Persistence Reminder**

Tell the agent to keep going until the task is done!

```python
Agent(
    instructions="""
    You are an agent - please keep going until the user's query 
    is completely resolved, before ending your turn.
    
    Only terminate when you are SURE the problem is solved.
    """
)
```

**Why?** Prevents the agent from giving up too early.

#### 2️⃣ **Tool-Calling Reminder**

Encourage the agent to use its tools instead of guessing!

```python
Agent(
    instructions="""
    If you are not sure about file content or information,
    use your tools to gather the relevant data.
    
    DO NOT guess or make up an answer - always use tools when available.
    """
)
```

**Why?** Reduces hallucinations and increases accuracy.

#### 3️⃣ **Planning Reminder** (Optional but Recommended)

Ask the agent to think out loud!

```python
Agent(
    instructions="""
    You MUST plan extensively before each function call,
    and reflect on the outcomes of previous function calls.
    
    DO NOT chain function calls silently - explain your thinking.
    """
)
```

**Why?** Makes debugging easier and improves decision quality.

---

### Best Practice 2: Structure Your Instructions

**Bad** ❌ - Vague and unstructured:
```python
Agent(
    instructions="Help students with their questions"
)
```

**Good** ✅ - Clear, structured, and specific:
```python
Agent(
    instructions="""
    You are a helpful study assistant for computer science students.
    
    ## Your Role
    Help students understand course material through:
    - Clear explanations with examples
    - Step-by-step problem solving
    - Encouraging and patient guidance
    
    ## When Answering Questions:
    1. First, search course materials using file_search_tool
    2. If not found, search web using web_search_tool
    3. Always cite your sources
    4. Break down complex topics into simple terms
    
    ## Important:
    - Never give direct answers to homework - guide instead
    - Always be encouraging and patient
    - Use examples relevant to computer science
    """
)
```

**Key Elements:**
- Clear role definition
- Structured sections (use ##, bullets, numbers)
- Step-by-step workflow
- Important constraints and guidelines

---

### Best Practice 3: Use Clear Tool Descriptions

The LLM reads your tool descriptions to decide when and how to use them!

**Bad** ❌:
```python
@function_tool
def search(query: str):
    """Searches stuff"""
    pass
```

**Good** ✅:
```python
@function_tool
def search_course_materials(query: str, course_name: str | None = None) -> str:
    """
    Search through uploaded course materials and study documents.
    
    Use this tool when:
    - Student asks about course content
    - Need to find specific topics in textbooks
    - Looking for definitions or explanations from materials
    
    Args:
        query: The search term (e.g., "binary trees", "thermodynamics")
        course_name: Optional - filter by specific course
    
    Returns:
        Relevant excerpts from course materials with source citations
    """
    pass
```

**Good tool descriptions include:**
- What the tool does
- When to use it
- Parameter explanations
- What it returns

---

### Best Practice 4: Use Delimiters and Structure

Help the model parse your instructions clearly!

**Use clear section markers:**

```python
instructions = """
You are a study assistant.

### WORKFLOW ###
1. Search documents first
2. Search web if needed
3. Provide answer with citations

### RULES ###
- Always cite sources
- Never guess
- Be encouraging

### EXAMPLES ###
Student: "What is polymorphism?"
You: [searches documents] → "Based on your OOP notes, polymorphism is..."
"""
```

**Common delimiters:**
- `###` for section headers
- `"""` for multi-line strings
- `---` for separators
- Numbers and bullets for lists

---

### Best Practice 5: Provide Examples in Instructions

Show the agent what "good" looks like!

```python
Agent(
    instructions="""
    You are a code review assistant.
    
    ## Example of Good Review:
    
    Student Code:
    ```python
    for i in range(len(arr)):
        print(arr[i])
    ```
    
    Your Review:
    "Good start! To make this more Pythonic, you could use:
    ```python
    for item in arr:
        print(item)
    ```
    This is more readable and follows Python best practices."
    
    ## Example of Bad Review (Don't Do This):
    "This code is wrong. Use a better loop."
    
    Always be specific and helpful!
    """
)
```

**Why examples work:**
- Show exact format expected
- Demonstrate tone and style
- Clarify ambiguous instructions

---

### Best Practice 6: Test and Iterate

**Prompting is empirical!** What works for one task might not work for another.

**Recommended workflow:**

```
1. Write initial prompt
2. Test with diverse inputs
3. Identify failure modes
4. Add specific instructions to fix failures
5. Repeat
```

**Example iteration:**

```python
# Version 1 - Too vague
"Answer questions about chemistry"

# Version 2 - Better, but agent searches web too often
"Answer chemistry questions using course materials"

# Version 3 - Much better!
"""
Answer chemistry questions:
1. ALWAYS search file_search_tool FIRST
2. Only use web_search_tool if file search returns no results
3. Cite which document you found the answer in
"""
```

---

### Best Practice 7: Handle Edge Cases Explicitly

Tell the agent what to do when things go wrong!

```python
Agent(
    instructions="""
    You are a study assistant.
    
    ## Normal Case:
    Search documents → Provide answer
    
    ## If Document Search Fails:
    - Try web search
    - Store the result for future use
    - Tell the student: "I didn't find this in your materials, 
      but here's what I found online..."
    
    ## If Both Searches Fail:
    - Be honest: "I couldn't find reliable information on this topic"
    - Suggest: "Could you upload relevant materials or rephrase your question?"
    - DO NOT make up information
    
    ## If Question is Unclear:
    - Ask clarifying questions
    - Example: "Are you asking about [X] or [Y]?"
    """
)
```

---

### Best Practice 8: OpenAI-Specific Tips

From the OpenAI GPT-4.1 Prompting Guide:

#### Use the `tools` Parameter (Not Manual Injection)

**Bad** ❌:
```python
instructions = """
You have these tools:
- search(query: str): Searches documents
- calculate(expr: str): Does math
"""
```

**Good** ✅:
```python
Agent(
    tools=[search_tool, calculator_tool]  # Use SDK's tool system
)
```

**Why?** The SDK formats tools optimally for the model.

#### Dont use too many tools in 1 Agent
One agent with 20+ tools becomes confused!

✅ **Solution:** Split into specialized agents


#### Request Explicit Planning for Complex Tasks

```python
instructions = """
For complex tasks:
1. First, create a plan listing all steps
2. Execute each step using appropriate tools
3. Reflect on results after each step
4. Adjust plan if needed

Example:
Task: "Summarize all chemistry chapters"
Plan:
- Step 1: List all chemistry documents
- Step 2: Read each document
- Step 3: Extract key concepts
- Step 4: Synthesize into summary
"""
```

#### Use Firm, Clear Language

**Weak** ❌:
```
"You should probably search documents first"
"Try to cite sources when possible"
```

**Strong** ✅:
```
"You MUST search documents before answering"
"ALWAYS cite sources - include document name and page number"
```

---

### Quick Reference Card 📋

**For Every Agent Prompt, Ask:**

✅ Is my agent's role crystal clear?  
✅ Did I structure instructions with sections?  
✅ Did I include the 3 agent reminders (persistence, tools, planning)?  
✅ Are my tool descriptions detailed?  
✅ Did I handle edge cases?  
✅ Did I provide examples of good behavior?  
✅ Did I test with diverse inputs?  
✅ Am I using firm, clear language?  

**Remember:**
> "A single sentence firmly and unequivocally clarifying your desired behavior is almost always sufficient to steer the model."  
> — OpenAI GPT-4.1 Prompting Guide

---

## Slide 23: What is MCP (Model Context Protocol)?

### The Integration Problem

**Before MCP:**
```
Building a GitHub integration → Write custom tools
Building a Notion integration → Write custom tools  
Building a Slack integration → Write custom tools
Building a Database integration → Write custom tools
```

Each integration requires:
- Custom API clients
- Authentication handling
- Error management
- Tool definitions
- Maintenance for API changes

**This doesn't scale!**

### What is MCP?

**Model Context Protocol (MCP)** is an **open standard** created by Anthropic for connecting AI agents to external systems.

**Think of MCP like USB-C for AI:**
- USB-C: One standard port for all devices
- MCP: One standard protocol for all integrations

### The MCP Architecture

```
┌─────────────────────────────────────────┐
│         Your AI Agent                   │
│    (Claude, ChatGPT, Custom Agent)      │
└──────────────┬──────────────────────────┘
               │
               │ MCP Protocol
               │
     ┌─────────┴─────────┐
     │   MCP Client      │ (Built into Agent SDK)
     └─────────┬─────────┘
               │
     ┌─────────┴─────────────────────────┐
     │                │                  │
┌────▼─────┐     ┌────▼─────┐     ┌──────▼────┐
│ Notion   │     │ GitHub   │     │ Filesystem│
│ MCP      │     │ MCP      │     │ MCP       │
│ Server   │     │ Server   │     │ Server    │
└──────────┘     └──────────┘     └───────────┘
```

### Key Benefits

**1. For Developers:**
- ✅ No need to write custom integrations
- ✅ Standardized protocol
- ✅ Community-maintained servers
- ✅ Easy to add new capabilities

**2. For Agents:**
- ✅ Access to en-number of pre-built integrations
- ✅ Automatic tool discovery
- ✅ Consistent interface across services

**3. For Users:**
- ✅ More capable agents immediately
- ✅ Better data access
- ✅ Seamless integrations

---

## Slide 24: Why MCP Matters - The Ecosystem

### The MCP Ecosystem is Growing Fast

**Sample MCP Servers (100+):**
- File Search, Google Drive: Documents Management
- Notion, Linear, Jira: Project management
- Gmail, Outlook, Slack: Communication management
- Browserbase: Browser automation
- Supabase, MongoDB, Postgres: Databases
- GitHub: Code Repository
- And hundreds more at [mcpservers.org](https://mcpservers.org/)

### Traditional Integration vs MCP

| Aspect | Traditional | With MCP |
|--------|------------|----------|
| **Development Time** | Days/weeks per integration | Minutes |
| **Code Required** | 100s of lines | 2-3 lines |
| **Maintenance** | You maintain it | Community maintains |
| **Updates** | Manual updates needed | Automatic |
| **Error Handling** | Custom per service | Standardized |



## Slide 25: MCP in Action - Simple Proof of Concept

### Let's Build an Agent with Filesystem Access

We'll use the **Filesystem MCP Server** - one of the simplest MCP servers that requires zero external APIs!


### Step 3: Use MCP in Your Agent

```python
async with MCPServerStdio(
    params={
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", str(repo_path)],
    },
) as FileSystemMCPServer:
    agent = Agent(
        name="File System Agent",
        instructions="You are a file system agent with access to files allowed. Answer any queries about the files",
        mcp_servers=[FileSystemMCPServer],
    )
```

### What Happens Behind the Scenes:

1. **Agent receives task**: "What files are in my study materials folder?"
2. **Agent discovers MCP tools**: `list_directory`, `read_file`, `search_files`, etc.
3. **Agent calls MCP tool**: `list_directory(path="/Users/yourname/Documents/study_materials")`
4. **MCP Server executes**: Returns list of files
5. **Agent formats response**: "You have 5 files: notes.txt, homework.pdf, ..."

**The amazing part?** You didn't write ANY code to interact with the filesystem! The MCP server provides all the tools automatically.

---
