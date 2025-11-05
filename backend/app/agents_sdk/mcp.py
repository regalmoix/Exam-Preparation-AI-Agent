from __future__ import annotations

import logging

from agents.mcp import MCPServerStdio

from ..services.config import config


logger = logging.getLogger(__name__)

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
        await NotionMCPServer.connect()
        logger.info("Notion MCP Server connected successfully")
    except Exception as e:
        logger.error(f"Error connecting to Notion MCP Server: {e}")
