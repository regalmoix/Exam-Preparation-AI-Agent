from __future__ import annotations

from agents.mcp import MCPServerStdio
from agents.mcp import create_static_tool_filter


AnkiMCPServer = MCPServerStdio(
    cache_tools_list=True,  # Cache the tools list, for demonstration
    tool_filter=create_static_tool_filter(
        allowed_tool_names=["list_decks", "create_deck", "get_due_cards", "present_card", "addNote", "findNotes"]
    ),
    params={
        "command": "npx",
        "args": ["-y", "anki-mcp-http", "--stdio"],
        "env": {"ANKI_CONNECT_URL": "http://localhost:8765"},
    },
)
