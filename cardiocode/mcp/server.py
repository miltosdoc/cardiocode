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
from typing import Any, Dict, Optional

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import (
        Tool,
        TextContent,
        CallToolResult,
        ListToolsResult,
    )
    MCP_AVAILABLE = True
except ImportError:
    # Fallback if MCP package not available
    print("Warning: MCP package not available. Using fallback implementation.")
    MCP_AVAILABLE = False

# Import tools
from cardiocode.mcp.tools import TOOL_REGISTRY, call_tool

# Configure logging
logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger("cardiocode-mcp")

# Create MCP server instance
if MCP_AVAILABLE:
    server = Server("cardiocode")
    logger.info("MCP package loaded successfully")
else:
    # Simple fallback server when MCP package is not available
    class FallbackServer:
        def __init__(self):
            self.tools = {"status": "MCP package unavailable - fallback mode"}
            
        async def list_tools(self):
            return {"tools": list(TOOL_REGISTRY.keys())}
            
        async def call_tool(self, name: str, arguments: Dict[str, Any]):
            if name in TOOL_REGISTRY:
                func = TOOL_REGISTRY[name]["function"]
                return func(**arguments)
            else:
                return {
                    "error": f"Tool '{name}' not available in fallback mode",
                    "available_tools": list(TOOL_REGISTRY.keys()),
                    "message": "Install MCP package for full functionality"
                }
            
        async def run(self, read_stream, write_stream):
            await write_stream(json.dumps({
                "fallback_mode": not MCP_AVAILABLE,
                "mcp_missing": not MCP_AVAILABLE,
                "message": "MCP server running in fallback mode" if not MCP_AVAILABLE else "MCP server running with full functionality"
            }))
            return
    
    server = FallbackServer()

@server.list_tools()
async def list_tools() -> ListToolsResult:
    """List all available CardioCode tools."""
    tools = []
    
    for name, info in TOOL_REGISTRY.items():
        func = info["function"]
        
        # Extract JSON schema from function signature and docstring
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
        for line in doc.split("\\n"):
            line = line.strip()
            if line.startswith("Args:"):
                in_args = True
                continue
            if in_args and line.startswith("  ") and ":" in line:
                # New parameter
                param_name = line.split(":")[0].strip()
                param_desc = ":".join(line.split(":")[1:]).strip()
                param_docs[param_name] = param_desc
                current_param = param_name
        
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
    
    for name, info in TOOL_REGISTRY.items():
        tools.append(Tool(
            name=name,
            description=info["description"],
            inputSchema=_get_tool_schema(name, info["function"]),
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
    """Run MCP server."""
    logger.info("Starting CardioCode MCP server...")
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )

def serve():
    """Entry point for MCP server."""
    asyncio.run(run_server())

if __name__ == "__main__":
    serve()