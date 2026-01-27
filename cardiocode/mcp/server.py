"""
CardioCode MCP Server.

Model Context Protocol server implementation for CardioCode.
Exposes cardiology guideline tools via stdio transport.

This server provides:
- 20 clinical decision support tools
- Comprehensive ESC guideline knowledge resource
- Full evidence traceability
"""

from __future__ import annotations
import asyncio
import json
import logging
import sys
import traceback
from typing import Any, Dict, List, Optional

# Configure logging to stderr (required for MCP)
logging.basicConfig(
    level=logging.INFO,
    stream=sys.stderr,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("cardiocode-mcp")

# Import MCP dependencies with error handling
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import (
        Tool,
        TextContent,
        Resource,
        ResourceContents,
        TextResourceContents,
    )
    MCP_AVAILABLE = True
except ImportError as e:
    logger.error(f"MCP package not installed: {e}")
    logger.error("Install with: pip install mcp>=1.0.0")
    MCP_AVAILABLE = False

# Import CardioCode tools
try:
    from cardiocode.mcp.tools import TOOL_REGISTRY, call_tool
    TOOLS_AVAILABLE = True
except ImportError as e:
    logger.error(f"CardioCode tools import error: {e}")
    TOOLS_AVAILABLE = False

# Import knowledge for resources
try:
    from cardiocode.mcp.knowledge import CARDIOCODE_KNOWLEDGE, get_guideline_summaries
    KNOWLEDGE_AVAILABLE = True
except ImportError:
    KNOWLEDGE_AVAILABLE = False
    CARDIOCODE_KNOWLEDGE = ""
    def get_guideline_summaries():
        return {}


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


def create_server() -> Optional[Server]:
    """Create and configure the MCP server."""
    if not MCP_AVAILABLE:
        logger.error("Cannot create server: MCP package not available")
        return None

    if not TOOLS_AVAILABLE:
        logger.error("Cannot create server: CardioCode tools not available")
        return None

    server = Server("cardiocode")

    @server.list_tools()
    async def list_tools():
        """List all available CardioCode tools."""
        tools = []

        for name, info in TOOL_REGISTRY.items():
            func = info["function"]
            try:
                schema = _get_tool_schema(name, func)
                tools.append(Tool(
                    name=name,
                    description=info["description"],
                    inputSchema=schema,
                ))
            except Exception as e:
                logger.warning(f"Error getting schema for {name}: {e}")
                # Add tool with minimal schema
                tools.append(Tool(
                    name=name,
                    description=info["description"],
                    inputSchema={"type": "object", "properties": {}, "required": []},
                ))

        logger.info(f"Listed {len(tools)} tools")
        return tools

    @server.call_tool()
    async def handle_call_tool(name: str, arguments: Dict[str, Any]):
        """Handle tool invocation."""
        logger.info(f"Tool call: {name} with args: {arguments}")

        if name not in TOOL_REGISTRY:
            error_result = {
                "error": f"Unknown tool: {name}",
                "available_tools": list(TOOL_REGISTRY.keys()),
            }
            return [TextContent(type="text", text=json.dumps(error_result, indent=2))]

        try:
            result = call_tool(name, arguments or {})

            # Format result as JSON
            result_text = json.dumps(result, indent=2, default=str)

            return [TextContent(type="text", text=result_text)]

        except Exception as e:
            logger.error(f"Tool error: {e}", exc_info=True)
            error_result = {
                "error": str(e),
                "error_type": type(e).__name__,
                "tool": name,
                "arguments": arguments,
                "traceback": traceback.format_exc(),
            }
            return [TextContent(type="text", text=json.dumps(error_result, indent=2))]

    @server.list_resources()
    async def list_resources():
        """List available CardioCode knowledge resources."""
        resources = [
            Resource(
                uri="cardiocode://knowledge/complete",
                name="CardioCode Complete Knowledge Base",
                description="Comprehensive ESC cardiology guidelines knowledge including all 9 guideline modules (2019-2024), clinical scores, and decision algorithms",
                mimeType="text/markdown",
            ),
            Resource(
                uri="cardiocode://guidelines/heart-failure",
                name="Heart Failure Guidelines (ESC 2021)",
                description="Complete HFrEF/HFmrEF/HFpEF treatment algorithms, GDMT pillars, device therapy indications",
                mimeType="text/markdown",
            ),
            Resource(
                uri="cardiocode://guidelines/atrial-fibrillation",
                name="Atrial Fibrillation Guidelines (ESC 2020/2024)",
                description="AF management including CHA2DS2-VASc, anticoagulation, rate/rhythm control, ablation",
                mimeType="text/markdown",
            ),
            Resource(
                uri="cardiocode://guidelines/ventricular-arrhythmias",
                name="Ventricular Arrhythmias Guidelines (ESC 2022)",
                description="VT management, SCD prevention, ICD indications, HCM risk stratification",
                mimeType="text/markdown",
            ),
            Resource(
                uri="cardiocode://guidelines/valvular-disease",
                name="Valvular Heart Disease Guidelines (ESC 2021)",
                description="AS, MR, AR severity assessment and intervention timing",
                mimeType="text/markdown",
            ),
            Resource(
                uri="cardiocode://guidelines/coronary-syndromes",
                name="Coronary Syndromes Guidelines (ESC 2019-2020)",
                description="CCS pre-test probability, NSTE-ACS GRACE score, invasive strategy timing",
                mimeType="text/markdown",
            ),
            Resource(
                uri="cardiocode://guidelines/pulmonary-hypertension",
                name="Pulmonary Hypertension Guidelines (ESC 2022)",
                description="PH classification, PAH risk assessment, treatment algorithms",
                mimeType="text/markdown",
            ),
            Resource(
                uri="cardiocode://guidelines/cardio-oncology",
                name="Cardio-Oncology Guidelines (ESC 2022)",
                description="CV risk assessment before cancer therapy, CTRCD management, surveillance protocols",
                mimeType="text/markdown",
            ),
            Resource(
                uri="cardiocode://tools/list",
                name="CardioCode Tools Reference",
                description="Complete list of all 20 available MCP tools with descriptions and parameters",
                mimeType="text/markdown",
            ),
        ]
        logger.info(f"Listed {len(resources)} resources")
        return resources

    @server.read_resource()
    async def read_resource(uri: str):
        """Read a CardioCode knowledge resource."""
        logger.info(f"Reading resource: {uri}")

        # Import knowledge content
        try:
            from cardiocode.mcp.knowledge import (
                CARDIOCODE_KNOWLEDGE,
                HEART_FAILURE_KNOWLEDGE,
                ATRIAL_FIBRILLATION_KNOWLEDGE,
                VENTRICULAR_ARRHYTHMIAS_KNOWLEDGE,
                VALVULAR_DISEASE_KNOWLEDGE,
                CORONARY_SYNDROMES_KNOWLEDGE,
                PULMONARY_HYPERTENSION_KNOWLEDGE,
                CARDIO_ONCOLOGY_KNOWLEDGE,
                TOOLS_REFERENCE,
            )

            content_map = {
                "cardiocode://knowledge/complete": CARDIOCODE_KNOWLEDGE,
                "cardiocode://guidelines/heart-failure": HEART_FAILURE_KNOWLEDGE,
                "cardiocode://guidelines/atrial-fibrillation": ATRIAL_FIBRILLATION_KNOWLEDGE,
                "cardiocode://guidelines/ventricular-arrhythmias": VENTRICULAR_ARRHYTHMIAS_KNOWLEDGE,
                "cardiocode://guidelines/valvular-disease": VALVULAR_DISEASE_KNOWLEDGE,
                "cardiocode://guidelines/coronary-syndromes": CORONARY_SYNDROMES_KNOWLEDGE,
                "cardiocode://guidelines/pulmonary-hypertension": PULMONARY_HYPERTENSION_KNOWLEDGE,
                "cardiocode://guidelines/cardio-oncology": CARDIO_ONCOLOGY_KNOWLEDGE,
                "cardiocode://tools/list": TOOLS_REFERENCE,
            }

            content = content_map.get(uri, f"Unknown resource: {uri}")

        except ImportError:
            content = f"Knowledge module not available for: {uri}"

        return TextResourceContents(
            uri=uri,
            text=content,
            mimeType="text/markdown",
        )

    return server


async def run_server():
    """Run the MCP server."""
    logger.info("Starting CardioCode MCP server...")

    server = create_server()
    if server is None:
        logger.error("Failed to create server")
        sys.exit(1)

    try:
        async with stdio_server() as (read_stream, write_stream):
            logger.info("Server initialized, waiting for connections...")
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options(),
            )
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)


def serve():
    """Entry point for the MCP server (used by setup.py console_scripts)."""
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


# Alias for backwards compatibility and setup.py entry point
main = serve


if __name__ == "__main__":
    serve()
