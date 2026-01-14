# CardioCode MCP Server Installation Guide

## Quick Installation (Both Windows & macOS)

### Option 1: Install with pip (Recommended)
```bash
# macOS/Linux
pip3 install --user 'mcp>=1.0.0'

# Windows  
pip install --user 'mcp>=1.0.0'
```

### Option 2: Install with pip + Force Reinstall
```bash
# If you get version conflicts, try this:
pip3 install --user --force-reinstall 'mcp>=1.0.0'
```

### Option 3: Install Without Virtual Environment (Failsafe)
```bash
# Direct system-wide installation
sudo pip3 install 'mcp>=1.0.0'
```

---

## Start CardioCode MCP Server

### Method 1: After Installation (Recommended)
```bash
python3 -m cardiocode.mcp.server
```

### Method 2: Direct Python (Fallback)
```bash
cd /Users/meditalks/Desktop/cardiocode
python3 -m cardiocode.mcp.server
```

---

## Editor Configuration (VS Code/Cursor/Windsurf)

### Step 1: Install MCP Extension
Install the official MCP extension for your editor:
- **VS Code**: "Claude Dev"
- **Cursor**: Built-in MCP support
- **Windsurf**: Built-in MCP support

### Step 2: Add MCP Server
Add to your editor's MCP settings:

```json
{
  "mcpServers": {
    "cardiocode": {
      "command": "python3",
      "args": [
        "-m", 
        "cardiocode.mcp.server"
      ],
      "cwd": "/Users/meditalks/Desktop/cardiocode"
    }
  }
}
```

**Important**: Set `cwd` to the CardioCode directory path!

---

## Troubleshooting

### Issue: "MCP package not available"
**Solution**: Install with `--user` flag or `sudo` for system-wide

### Issue: Server starts but shows tools as empty
**Solution**: MCP package needs to be properly installed; restart editor after installation

### Issue: Path-related errors on Windows
**Solution**: All fixes are cross-platform compatible now

---

## GitHub Push Checklist

When you push to GitHub, ensure these changes are included:

### ✅ Fixed Files (Ready to Push)
- [ ] `cardiocode/ingestion/pdf_watcher.py` (path normalization)
- [ ] `cardiocode/ingestion/knowledge_extractor.py` (path normalization)
- [ ] `cardiocode/ingestion/dynamic_generator.py` (web search improvements)
- [ ] `install.py` (cross-platform installation script)

### 🔄 MCP Server Improvements (Consider Adding)
- [ ] Better error messages for MCP package missing
- [ ] Graceful fallback when MCP tools not available
- [ ] Automatic PATH environment setup

---

## Verification Commands

After installation, verify everything works:

```bash
# Test MCP server
python3 -c "import cardiocode.mcp.server; print('MCP server works')"

# Test path handling
python3 -c "from cardiocode.ingestion.pdf_watcher import GuidelineWatcher; w = GuidelineWatcher(); print('PDF watcher works')"

# Test web search preferences  
python3 -c "from cardiocode.mcp.llm_tools import tool_propose_web_update; print('Web search works')"
```

---

## For Developers

### Key Changes Made
1. **Path Normalization**: `Path(filepath).as_posix()` for cross-platform compatibility
2. **Web Search Intelligence**: Prioritizes guidelines over presentations
3. **Fallback Server**: Graceful degradation when MCP package unavailable
4. **Installation Script**: Platform detection with proper error handling

### Architecture Improvements
- All path operations use `pathlib.Path` 
- Error handling includes FileNotFoundError for missing files
- Web search validates document type preferences
- Cross-platform string operations throughout

---

**💡 Note**: The CardioCode MCP server should work with both `mcp` package and the fallback implementation. The fallback provides basic functionality while `mcp` enables full feature set.