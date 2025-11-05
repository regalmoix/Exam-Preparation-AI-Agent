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
        if NotionMCPServer.session is None:
            await NotionMCPServer.connect()
            available_tools = await NotionMCPServer.list_tools()
            logger.info(f"Available tools: {[tool.name for tool in available_tools]}")
            logger.info("Notion MCP Server connected successfully")
        else:
            logger.warning("Notion MCP already connected")
    except Exception as e:
        logger.error(f"Error connecting to Notion MCP Server: {e}")
        await NotionMCPServer.cleanup()
