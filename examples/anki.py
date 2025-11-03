from __future__ import annotations

import asyncio

from agents import Agent
from agents import RunContextWrapper
from agents import Runner
from agents import trace
from agents.mcp import MCPServer
from agents.mcp import MCPServerStdio


async def run(mcp_server: MCPServer):
    agent = Agent(
        name="Assistant",
        instructions="Help the user with flashcards management using Anki",
        mcp_servers=[mcp_server],
    )
    print(await agent.get_mcp_tools(RunContextWrapper(context=None)))

    message = "What all are the flashcards?"
    print("\n" + "-" * 40)
    print(f"Running: {message}")
    result = await Runner.run(starting_agent=agent, input=message)
    print(result.final_output)

    message = "Create a new deck called AI Agents Workshop?"
    print("\n" + "-" * 40)
    print(f"Running: {message}")
    result = await Runner.run(starting_agent=agent, input=message)
    print(result.final_output)


async def main():
    async with MCPServerStdio(
        cache_tools_list=True,  # Cache the tools list, for demonstration
        params={
            "command": "npx",
            "args": ["-y", "anki-mcp-http", "--stdio"],
            "env": {"ANKI_CONNECT_URL": "http://localhost:8765"},
        },
    ) as server:
        with trace(workflow_name="Anki Flashcard Example"):
            await run(server)


if __name__ == "__main__":
    asyncio.run(main())
