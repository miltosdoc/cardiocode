"""
CardioCode MCP Server.

Model Context Protocol server exposing CardioCode as tools for LLMs.
"""

from cardiocode.mcp.server import serve

__all__ = ["serve"]
