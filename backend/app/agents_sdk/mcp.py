from __future__ import annotations

from agents.mcp import MCPServerStdio


AnkiMCPServer = MCPServerStdio(
    cache_tools_list=True,  # Cache the tools list, for demonstration
    params={
        "command": "npx",
        "args": ["-y", "anki-mcp-http", "--stdio"],
        "env": {"ANKI_CONNECT_URL": "http://localhost:8765"},
    },
)
