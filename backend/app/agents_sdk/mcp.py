from __future__ import annotations

import logging

from agents.mcp import MCPServerStdio

from ..services.config import config


logger = logging.getLogger(__name__)

AnkiMCPServer = MCPServerStdio(
    cache_tools_list=True,
    # tool_filter=create_static_tool_filter(
    #     allowed_tool_names=["list_decks", "create_deck", "get_due_cards", "present_card", "addNote", "findNotes"]
    # ),
    params={
        "command": "npx",
        "args": ["-y", "anki-mcp-http", "--stdio"],
        "env": {"ANKI_CONNECT_URL": "http://localhost:8765"},
    },
)


NotionMCPServer = MCPServerStdio(
    params={
        "command": "npx",
        "args": ["-y", "@suekou/mcp-notion-server"],
        "env": {
            "NOTION_API_TOKEN": config.notion_token,
            "NOTION_TOKEN": config.notion_token,
        },
    },
)


async def connect():
    try:
        await AnkiMCPServer.connect()
        logger.info("Anki MCP Server connected successfully")
    except Exception as e:
        logger.error(f"Error connecting to Anki MCP Server: {e}")

    try:
        await NotionMCPServer.connect()
        logger.info("Notion MCP Server connected successfully")
    except Exception as e:
        logger.error(f"Error connecting to Notion MCP Server: {e}")
