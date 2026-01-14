# CardioCode Installation Guide

Simple steps to install the CardioCode MCP server on macOS or Windows.

---

## Step 1: Install Python

You need Python 3.10 or newer. Check if you already have it:

**macOS:**
```bash
python3 --version
```

**Windows:**
```
python --version
```

If you see `Python 3.10.x` or higher, skip to Step 2. Otherwise, install Python:

### macOS

**Option A: Download installer (easiest)**
1. Go to https://www.python.org/downloads/
2. Download Python 3.11
3. Run the installer

**Option B: Using Homebrew**
```bash
brew install python@3.11
```

### Windows

1. Go to https://www.python.org/downloads/
2. Download Python 3.11
3. Run the installer
4. **IMPORTANT: Check the box "Add Python to PATH"**

After installing, close and reopen your terminal, then verify:
```
python --version
```

---

## Step 2: Install Git (if you don't have it)

**macOS:**
```bash
git --version
```
If not installed, it will prompt you to install Xcode Command Line Tools. Click Install.

**Windows:**
1. Go to https://git-scm.com/download/win
2. Download and run the installer
3. Use default options

---

## Step 3: Download CardioCode

Open Terminal (macOS) or Command Prompt/PowerShell (Windows):

```bash
git clone https://github.com/miltosdoc/cardiocode.git
cd cardiocode
```

---

## Step 4: Install CardioCode

**macOS:**
```bash
python3 -m pip install --user pymupdf mcp
python3 -m pip install --user -e .
```

**Windows:**
```
python -m pip install --user pymupdf mcp
python -m pip install --user -e .
```

---

## Step 5: Test the Installation

**macOS:**
```bash
python3 -m cardiocode.mcp.server
```

**Windows:**
```
python -m cardiocode.mcp.server
```

You should see output indicating the server started. Press Ctrl+C to stop it.

---

## Step 6: Configure Your Editor

### For Claude Desktop

**macOS:** Edit `~/Library/Application Support/Claude/claude_desktop_config.json`

**Windows:** Edit `%APPDATA%\Claude\claude_desktop_config.json`

Add this configuration (replace the path with your actual cardiocode folder):

**macOS example:**
```json
{
  "mcpServers": {
    "cardiocode": {
      "command": "python3",
      "args": ["-m", "cardiocode.mcp.server"],
      "cwd": "/Users/YOURUSERNAME/cardiocode"
    }
  }
}
```

**Windows example:**
```json
{
  "mcpServers": {
    "cardiocode": {
      "command": "python",
      "args": ["-m", "cardiocode.mcp.server"],
      "cwd": "C:\\Users\\YOURUSERNAME\\cardiocode"
    }
  }
}
```

### For VS Code / Cursor / Windsurf

Add to your editor's MCP settings (same JSON format as above).

### For OpenCode

Add to `opencode.json`:
```json
{
  "mcp": {
    "cardiocode": {
      "type": "local",
      "command": ["python3", "-m", "cardiocode.mcp.server"],
      "enabled": true
    }
  }
}
```

On Windows, use `"python"` instead of `"python3"`.

---

## Troubleshooting

### "python not found" or "python3 not found"

- **Windows:** Reinstall Python and make sure to check "Add Python to PATH"
- **macOS:** Try `python3.11` instead of `python3`

### "pip not found"

Use `python -m pip` instead of just `pip`:
```bash
python3 -m pip install --user pymupdf mcp
```

### "Permission denied"

Add the `--user` flag to pip commands:
```bash
python3 -m pip install --user pymupdf mcp
```

### "ModuleNotFoundError: No module named 'cardiocode'"

Make sure you ran the install command from inside the cardiocode folder:
```bash
cd cardiocode
python3 -m pip install --user -e .
```

### MCP server won't start

1. Check Python version is 3.10+: `python3 --version`
2. Check packages installed: `python3 -m pip list | grep mcp`
3. Make sure you're in the cardiocode directory

---

## Quick Reference

| Task | macOS | Windows |
|------|-------|---------|
| Check Python | `python3 --version` | `python --version` |
| Install packages | `python3 -m pip install --user ...` | `python -m pip install --user ...` |
| Run server | `python3 -m cardiocode.mcp.server` | `python -m cardiocode.mcp.server` |

---

## Need Help?

- GitHub Issues: https://github.com/miltosdoc/cardiocode/issues
- Include your OS, Python version, and the full error message
