from __future__ import annotations

import asyncio

from agents import Agent
from agents import Runner


async def main() -> None:
    # Create agent
    agent = Agent(
        name="Assistant",
        instructions="Reply very concisely.",
    )

    # Create a session instance with a session ID
    # session = SQLiteSession("conversation_123")

    # First turn
    result = await Runner.run(
        agent,
        "What city is the Golden Gate Bridge in?",
        # session=session
    )
    print(result.final_output)  # "San Francisco"

    # Second turn - agent automatically remembers previous context
    result = await Runner.run(
        agent,
        "What state is it in?",
        # session=session
    )
    print(result.final_output)  # "California"


asyncio.run(main())
