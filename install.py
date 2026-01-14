#!/usr/bin/env python3
"""
Cross-platform installation script for CardioCode MCP Server.

This script handles installation on both Windows and macOS systems,
with automatic path separator detection and proper environment setup.
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Optional

def detect_platform() -> str:
    """Detect the current platform."""
    if sys.platform.startswith('win'):
        return 'windows'
    elif sys.platform.startswith('darwin'):
        return 'macos'
    elif sys.platform.startswith('linux'):
        return 'linux'
    else:
        return 'unknown'

def normalize_separators(path_str: str) -> str:
    """Normalize path separators for the current platform."""
    path = Path(path_str)
    return str(path.as_posix())

def check_dependencies() -> bool:
    """Check if required dependencies are installed."""
    try:
        import fitz  # PyMuPDF
        import mcp
        print("✓ Dependencies available")
        return True
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("Please install missing dependencies:")
        print("pip install pymupdf mcp")
        return False

def create_source_directory() -> bool:
    """Create source_pdfs directory with proper permissions."""
    source_dir = Path("source_pdfs")
    
    try:
        source_dir.mkdir(exist_ok=True)
        print(f"✓ Created source directory: {source_dir.absolute()}")
        return True
    except PermissionError:
        print("✗ Permission denied when creating source directory")
        return False
    except Exception as e:
        print(f"✗ Error creating source directory: {e}")
        return False

def setup_config_file() -> bool:
    """Create platform-specific configuration file."""
    platform = detect_platform()
    
    config = {
        "platform": platform,
        "path_separator": "\\" if platform == "windows" else "/",
        "python_path": sys.executable,
        "install_date": json.dumps(datetime.now().isoformat(), default=str),
    }
    
    try:
        config_path = Path("cardiocode") / "install_config.json"
        config_path.parent.mkdir(exist_ok=True)
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✓ Configuration saved to: {config_path}")
        return True
    except Exception as e:
        print(f"✗ Error saving configuration: {e}")
        return False

def install_mcp_server() -> bool:
    """Install MCP server configuration."""
    platform = detect_platform()
    
    try:
        # Check if we can install MCP server
        if platform == "windows":
            # Windows: Use pip install
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", "-e", "."
            ], capture_output=True, text=True)
        else:
            # macOS/Linux: Use pip install
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", "-e", "."
            ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ CardioCode MCP server installed successfully")
            return True
        else:
            print(f"✗ Installation failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"✗ Installation error: {e}")
        return False

def setup_mcp_client_config() -> bool:
    """Setup MCP client configuration for common editors."""
    platform = detect_platform()
    
    # Create example MCP configuration
    mcp_config = {
        "mcpServers": {
            "cardiocode": {
                "command": f"{sys.executable}",
                "args": ["-m", "cardiocode.mcp.server"],
                "env": {
                    "PYTHONPATH": str(Path.cwd().absolute())
                }
            }
        }
    }
    
    config_paths = {
        "windows": Path("~/AppData/Roaming/Code/User/globalStorage/s anthropic-ais-code/mcp_servers.json"),
        "macos": Path("~/Library/Application Support/Code/User/globalStorage/anthropic-ais-code/mcp_servers.json"),
        "linux": Path("~/.config/Code/User/globalStorage/anthropic-ais-code/mcp_servers.json")
    }
    
    try:
        config_path = config_paths.get(platform, config_paths["linux"])
        config_path = config_path.expanduser()
        
        # Create directory if it doesn't exist
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w') as f:
            json.dump(mcp_config, f, indent=2)
        
        print(f"✓ MCP configuration created: {config_path}")
        print("Please restart your editor to load the MCP server")
        return True
        
    except Exception as e:
        print(f"✗ Error creating MCP configuration: {e}")
        return False

def test_installation() -> bool:
    """Test if the installation works correctly."""
    try:
        # Test importing cardiocode
        import cardiocode.mcp.server
        
        # Test basic functionality
        from cardiocode.mcp.tools import TOOL_REGISTRY
        tool_count = len(TOOL_REGISTRY)
        
        print(f"✓ Installation test passed")
        print(f"✓ Available tools: {tool_count}")
        
        # Test knowledge manager
        from cardiocode.ingestion.pdf_watcher import GuidelineWatcher
        watcher = GuidelineWatcher("source_pdfs")
        print("✓ PDF watcher functional")
        
        return True
        
    except Exception as e:
        print(f"✗ Installation test failed: {e}")
        return False

def main():
    """Main installation process."""
    print("CardioCode MCP Server - Cross-platform Installation")
    print("=" * 50)
    
    platform = detect_platform()
    print(f"Platform: {platform}")
    print(f"Python: {sys.version}")
    print(f"Directory: {Path.cwd().absolute()}")
    
    # Step 1: Check dependencies
    print("\n1. Checking dependencies...")
    if not check_dependencies():
        return 1
    
    # Step 2: Create source directory
    print("\n2. Setting up directories...")
    if not create_source_directory():
        return 1
    
    # Step 3: Install package
    print("\n3. Installing CardioCode MCP server...")
    if not install_mcp_server():
        return 1
    
    # Step 4: Setup configuration
    print("\n4. Creating configuration...")
    if not setup_config_file():
        return 1
    
    # Step 5: Setup MCP client config
    print("\n5. Setting up editor integration...")
    if not setup_mcp_client_config():
        return 1
    
    # Step 6: Test installation
    print("\n6. Testing installation...")
    if not test_installation():
        return 1
    
    print("\n" + "=" * 50)
    print("✓ Installation completed successfully!")
    print("\nNext steps:")
    print("1. Add guideline PDFs to the 'source_pdfs' directory")
    print("2. Start your editor and use CardioCode tools")
    print("3. Call 'cardiocode_get_system_context' to begin")
    
    return 0

if __name__ == "__main__":
    from datetime import datetime
    sys.exit(main())