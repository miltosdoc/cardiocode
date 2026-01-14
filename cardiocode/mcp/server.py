"""
CardioCode MCP Server.

Model Context Protocol server implementation for CardioCode.
Exposes cardiology guideline tools via stdio transport.
"""

from __future__ import annotations
import asyncio
import json
import logging
import sys
from typing import Any, Dict, List, Optional, Sequence

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    CallToolResult,
    ListToolsResult,
)

from cardiocode.mcp.tools import TOOL_REGISTRY, call_tool

# Configure logging
logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger("cardiocode-mcp")

# Create MCP server instance
server = Server("cardiocode")


def _get_tool_schema(name: str, func: callable) -> Dict[str, Any]:
    """Extract JSON schema from function signature and docstring."""
    import inspect
    
    sig = inspect.signature(func)
    doc = func.__doc__ or ""
    
    # Parse docstring for Args section
    properties = {}
    required = []
    
    # Extract parameter descriptions from docstring
    param_docs = {}
    in_args = False
    current_param = None
    for line in doc.split("\n"):
        line = line.strip()
        if line.startswith("Args:"):
            in_args = True
            continue
        if in_args:
            if line.startswith("Returns:") or line.startswith("Raises:"):
                break
            if line and ":" in line:
                # New parameter
                param_name = line.split(":")[0].strip()
                param_desc = ":".join(line.split(":")[1:]).strip()
                param_docs[param_name] = param_desc
                current_param = param_name
            elif current_param and line:
                # Continuation of previous description
                param_docs[current_param] += " " + line
    
    # Build properties from signature
    for param_name, param in sig.parameters.items():
        if param_name in ("self", "cls"):
            continue
        
        # Determine type
        annotation = param.annotation
        param_type = "string"  # default
        
        if annotation != inspect.Parameter.empty:
            if annotation == int:
                param_type = "integer"
            elif annotation == float:
                param_type = "number"
            elif annotation == bool:
                param_type = "boolean"
            elif annotation == str:
                param_type = "string"
            elif hasattr(annotation, "__origin__"):
                # Handle Optional, List, etc.
                origin = getattr(annotation, "__origin__", None)
                if origin is list:
                    param_type = "array"
                elif origin is dict:
                    param_type = "object"
        
        prop = {"type": param_type}
        
        # Add description from docstring
        if param_name in param_docs:
            prop["description"] = param_docs[param_name]
        
        properties[param_name] = prop
        
        # Check if required (no default value)
        if param.default == inspect.Parameter.empty:
            required.append(param_name)
    
    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


@server.list_tools()
async def list_tools() -> ListToolsResult:
    """List all available CardioCode tools."""
    tools = []
    
    for name, info in TOOL_REGISTRY.items():
        func = info["function"]
        schema = _get_tool_schema(name, func)
        
        tools.append(Tool(
            name=name,
            description=info["description"],
            inputSchema=schema,
        ))
    
    logger.info(f"Listed {len(tools)} tools")
    return ListToolsResult(tools=tools)


@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
    """Handle tool invocation."""
    logger.info(f"Tool call: {name} with args: {arguments}")
    
    if name not in TOOL_REGISTRY:
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=json.dumps({
                    "error": f"Unknown tool: {name}",
                    "available_tools": list(TOOL_REGISTRY.keys()),
                }),
            )],
            isError=True,
        )
    
    try:
        result = call_tool(name, arguments or {})
        
        # Format result as JSON
        result_text = json.dumps(result, indent=2, default=str)
        
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=result_text,
            )],
        )
    
    except Exception as e:
        logger.error(f"Tool error: {e}", exc_info=True)
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=json.dumps({
                    "error": str(e),
                    "tool": name,
                    "arguments": arguments,
                }),
            )],
            isError=True,
        )


async def run_server():
    """Run the MCP server."""
    logger.info("Starting CardioCode MCP server...")
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


def serve():
    """Entry point for the MCP server."""
    asyncio.run(run_server())


if __name__ == "__main__":
    serve()
