"""
CardioCode MCP Server.

Model Context Protocol server exposing CardioCode as tools for LLMs.

This module provides:
- MCP server with 20 clinical decision support tools
- Comprehensive ESC guideline knowledge resources
- Full evidence traceability for all recommendations

Usage:
    # Start the MCP server
    python -m cardiocode.mcp.server

    # Or use the console script (after pip install)
    cardiocode-mcp
"""

from cardiocode.mcp.server import serve, main

__all__ = ["serve", "main"]
