from __future__ import annotations

import logging

from agents.mcp import MCPServerStdio

from ..services.config import config


logger = logging.getLogger(__name__)


logger.info("Initializing Notion MCP Server")
NotionMCPServer = MCPServerStdio(
    cache_tools_list=True,  # Cache the tools list, for demonstration
    params={
        "command": "npx",
        "args": ["-y", "@suekou/mcp-notion-server"],
        "env": {
            "NOTION_API_TOKEN": config.notion_token,
            "NOTION_TOKEN": config.notion_token,
        },
    },
)
logger.info("Notion Server initialized successfully")
