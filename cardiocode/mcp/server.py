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
    print("Warning: MCP package not available. Using fallback implementation.", file=sys.stderr)
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
            await write_stream.write(json.dumps({
                "fallback_mode": not MCP_AVAILABLE,
                "mcp_missing": not MCP_AVAILABLE,
                "message": "MCP server running in fallback mode" if not MCP_AVAILABLE else "MCP server running with full functionality"
            }))
            return
    
    server = FallbackServer()

def _get_tool_schema(name: str, info: Dict[str, Any]) -> Tool:
    """Generate tool schema from function metadata."""
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
    for line in doc.split("\n"):
        line = line.strip()
        if line.startswith("Args:"):
            in_args = True
            continue
        if in_args and line.startswith("  ") and ":" in line:
            # New parameter
            param_name = line.split(":")[0].strip()
            param_desc = line.split(":", 1)[1].strip()
            param_docs[param_name] = param_desc
            current_param = param_name
        elif in_args and line.startswith("    ") and current_param:
            # Continuation of parameter description
            param_docs[current_param] += " " + line.strip()
    
    # Build JSON schema from function signature
    for param_name, param in sig.parameters.items():
        param_type = "string"
        if param.annotation == int:
            param_type = "integer"
        elif param.annotation == float:
            param_type = "number"
        elif param.annotation == bool:
            param_type = "boolean"
        
        param_schema = {"type": param_type}
        
        # Add description if available
        if param_name in param_docs:
            param_schema["description"] = param_docs[param_name]
        
        # Handle optional parameters
        if param.default == inspect.Parameter.empty:
            required.append(param_name)
        else:
            param_schema["default"] = param.default
        
        properties[param_name] = param_schema
    
    return Tool(
        name=name,
        description=doc.split("\n")[0] if doc else f"CardioCode tool: {name}",
        inputSchema={
            "type": "object",
            "properties": properties,
            "required": required,
        },
    )

if MCP_AVAILABLE:
    @server.list_tools()
    async def list_tools() -> ListToolsResult:
        """List all available CardioCode tools."""
        tools = []
        
        for name, info in TOOL_REGISTRY.items():
            tool = _get_tool_schema(name, info)
            tools.append(tool)
        
        return ListToolsResult(tools=tools)

    @server.call_tool()
    async def call_tool_handler(name: str, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle tool calls."""
        try:
            result = call_tool(name, arguments)
            
            if isinstance(result, dict) and "error" in result:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Error: {result['error']}")]
                )
            
            return CallToolResult(
                content=[TextContent(type="text", text=str(result))]
            )
            
        except Exception as e:
            logger.error(f"Error calling tool {name}: {e}")
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error: {str(e)}")]
            )

async def main():
    """Main server entry point."""
    if MCP_AVAILABLE:
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options()
            )
    else:
        # Fallback mode
        import sys
        await server.run(sys.stdin, sys.stdout)

def serve():
    """Serve function for module import."""
    asyncio.run(main())

if __name__ == "__main__":
    serve()