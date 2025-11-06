from __future__ import annotations

import asyncio
from pathlib import Path

import prettytable
from agents import Agent
from agents import Runner
from agents.mcp import MCPServerStdio


async def main():
    repo_path = Path(__file__).resolve().parent.parent.parent.resolve()

    print(f"Allowing MCP the access to {repo_path=}")

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
        tools = await FileSystemMCPServer.list_tools()

        table = prettytable.PrettyTable()
        table.field_names = ["Name", "Description"]
        table.hrules = prettytable.ALL

        for tool in tools:
            table.add_row([tool.name, tool.description])
        table.max_width = 120
        print(table)

        print("=" * 120)

        while True:
            result = await Runner.run(agent, input("Enter query to FileSystemAgent: "))
            print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
