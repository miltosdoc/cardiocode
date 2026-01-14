"""
CardioCode MCP Server.

Model Context Protocol server for clinical decision support.
"""

from __future__ import annotations
import asyncio
import json
import logging
import sys
import inspect
from typing import Any, Dict

# Configure logging
logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger("cardiocode-mcp")

# Try to import MCP
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent, CallToolResult
    MCP_AVAILABLE = True
    logger.info("MCP package loaded successfully")
except ImportError:
    MCP_AVAILABLE = False
    logger.warning("MCP package not available")

# Import tools
from cardiocode.mcp.tools import TOOL_REGISTRY, call_tool


def _build_tool_schema(name: str, func) -> Dict[str, Any]:
    """Build JSON schema from function signature."""
    sig = inspect.signature(func)
    doc = func.__doc__ or ""
    
    # Parse docstring for parameter descriptions
    param_docs = {}
    in_args = False
    current_param = None
    
    for line in doc.split("\n"):
        line_stripped = line.strip()
        if line_stripped.startswith("Args:"):
            in_args = True
            continue
        if line_stripped.startswith("Returns:"):
            in_args = False
            continue
        if in_args and ":" in line_stripped:
            parts = line_stripped.split(":", 1)
            if len(parts) == 2:
                param_name = parts[0].strip()
                param_desc = parts[1].strip()
                param_docs[param_name] = param_desc
                current_param = param_name
        elif in_args and current_param and line_stripped:
            param_docs[current_param] += " " + line_stripped
    
    # Build properties from signature
    properties = {}
    required = []
    
    for param_name, param in sig.parameters.items():
        param_schema = {"type": "string"}  # MCP sends everything as strings
        
        if param_name in param_docs:
            param_schema["description"] = param_docs[param_name]
        
        if param.default == inspect.Parameter.empty:
            required.append(param_name)
        elif param.default is not None:
            param_schema["default"] = str(param.default)
        
        properties[param_name] = param_schema
    
    return {
        "name": name,
        "description": doc.split("\n")[0].strip() if doc else f"CardioCode tool: {name}",
        "inputSchema": {
            "type": "object",
            "properties": properties,
            "required": required,
        }
    }


if MCP_AVAILABLE:
    # Create MCP server
    server = Server("cardiocode")
    
    @server.list_tools()
    async def list_tools():
        """List all available tools."""
        tools = []
        for name, info in TOOL_REGISTRY.items():
            schema = _build_tool_schema(name, info["function"])
            tools.append(Tool(
                name=schema["name"],
                description=schema["description"],
                inputSchema=schema["inputSchema"],
            ))
        return tools
    
    @server.call_tool()
    async def handle_call_tool(name: str, arguments: Dict[str, Any]):
        """Handle tool calls."""
        try:
            result = call_tool(name, arguments or {})
            
            # Convert result to JSON string
            if isinstance(result, dict):
                result_text = json.dumps(result, indent=2, ensure_ascii=False)
            else:
                result_text = str(result)
            
            return [TextContent(type="text", text=result_text)]
            
        except Exception as e:
            logger.error(f"Error calling {name}: {e}")
            return [TextContent(type="text", text=json.dumps({"error": str(e)}))]


async def main():
    """Main entry point."""
    if MCP_AVAILABLE:
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options()
            )
    else:
        # Fallback: print tools and exit
        print(json.dumps({
            "status": "MCP not available",
            "available_tools": list(TOOL_REGISTRY.keys()),
            "message": "Install MCP: pip install mcp"
        }))


def serve():
    """Entry point for module execution."""
    asyncio.run(main())


if __name__ == "__main__":
    serve()
