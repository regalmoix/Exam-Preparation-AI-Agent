from __future__ import annotations

import asyncio

from agents import Agent
from agents import Runner
from agents import trace
from agents.mcp import MCPServer
from agents.mcp import MCPServerStdio


async def run(mcp_server: MCPServer):
    agent = Agent(
        name="Assistant",
        model="gpt-4o-mini",
        instructions="Help the user with Notion notes",
        mcp_servers=[mcp_server],
    )

    message = "Create a sample placeholder template meeting notes for today's standup with action items and replace the existing contents of 'AI Workshop Notes' with these notes?"

    print("\n" + "-" * 40)
    print(f"Running: {message}")
    result = await Runner.run(starting_agent=agent, input=message)
    print(result.final_output)


async def main():
    async with MCPServerStdio(
        params={
            "command": "npx",
            # "args": ["-y", "mcp-remote", "https://mcp.notion.com/mcp"],
            # "args": ["-y", "@notionhq/notion-mcp-server"],
            "args": ["-y", "@suekou/mcp-notion-server"],
            "env": {
                "NOTION_API_TOKEN": "ntn_****",
                "NOTION_TOKEN": "ntn_****",
            },
        },
    ) as server:
        with trace(workflow_name="Notion MCP Example"):
            await run(server)


if __name__ == "__main__":
    asyncio.run(main())
