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

If you already have it, just update:
```bash
cd cardiocode
git pull
```

---

## Step 4: Create Virtual Environment and Install

Modern Python requires a virtual environment. This keeps CardioCode's packages separate from your system.

**macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install pymupdf mcp
pip install -e .
```

**Windows:**
```
python -m venv venv
venv\Scripts\activate
pip install pymupdf mcp
pip install -e .
```

You'll see `(venv)` at the start of your prompt when the environment is active.

---

## Step 5: Test the Installation

With your virtual environment active (you should see `(venv)` in your prompt):

```bash
python -m cardiocode.mcp.server
```

You should see: `CardioCode MCP Server started`

Press Ctrl+C to stop it.

---

## Step 6: Configure Your Editor

The editor needs to use the Python from your virtual environment.

### Find your venv Python path

**macOS:**
```bash
# From inside the cardiocode folder:
echo "$(pwd)/venv/bin/python"
```
Example output: `/Users/yourname/cardiocode/venv/bin/python`

**Windows:**
```
# From inside the cardiocode folder:
echo %cd%\venv\Scripts\python.exe
```
Example output: `C:\Users\yourname\cardiocode\venv\Scripts\python.exe`

### For Claude Desktop

**macOS:** Edit `~/Library/Application Support/Claude/claude_desktop_config.json`

**Windows:** Edit `%APPDATA%\Claude\claude_desktop_config.json`

**macOS example:**
```json
{
  "mcpServers": {
    "cardiocode": {
      "command": "/Users/YOURUSERNAME/cardiocode/venv/bin/python",
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
      "command": "C:\\Users\\YOURUSERNAME\\cardiocode\\venv\\Scripts\\python.exe",
      "args": ["-m", "cardiocode.mcp.server"],
      "cwd": "C:\\Users\\YOURUSERNAME\\cardiocode"
    }
  }
}
```

### For OpenCode

Add to `opencode.json` in the cardiocode folder:

**macOS:**
```json
{
  "mcp": {
    "cardiocode": {
      "type": "local",
      "command": ["/Users/YOURUSERNAME/cardiocode/venv/bin/python", "-m", "cardiocode.mcp.server"],
      "enabled": true
    }
  }
}
```

**Windows:**
```json
{
  "mcp": {
    "cardiocode": {
      "type": "local",
      "command": ["C:\\Users\\YOURUSERNAME\\cardiocode\\venv\\Scripts\\python.exe", "-m", "cardiocode.mcp.server"],
      "enabled": true
    }
  }
}
```

---

## Troubleshooting

### "externally-managed-environment" error

This means you need to use a virtual environment (Step 4). Don't use `--user` flag with Homebrew Python.

### "command not found: python3"

- **macOS with Homebrew:** Try `python3.11` or `/opt/homebrew/bin/python3`
- **Windows:** Reinstall Python and check "Add Python to PATH"

### "No module named 'cardiocode'"

Make sure you:
1. Activated the virtual environment: `source venv/bin/activate` (macOS) or `venv\Scripts\activate` (Windows)
2. Ran `pip install -e .` from inside the cardiocode folder

### Server crashes or shows errors

1. Make sure virtual environment is active
2. Check packages: `pip list | grep -E "mcp|pymupdf"`
3. Reinstall: `pip install --force-reinstall pymupdf mcp`

### Editor can't find the server

Make sure you're using the full path to the venv Python, not just `python3`.

---

## Daily Usage

To work with CardioCode later:

**macOS:**
```bash
cd cardiocode
source venv/bin/activate
python -m cardiocode.mcp.server
```

**Windows:**
```
cd cardiocode
venv\Scripts\activate
python -m cardiocode.mcp.server
```

---

## Quick Reference

| Step | macOS | Windows |
|------|-------|---------|
| Create venv | `python3 -m venv venv` | `python -m venv venv` |
| Activate venv | `source venv/bin/activate` | `venv\Scripts\activate` |
| Install | `pip install pymupdf mcp && pip install -e .` | Same |
| Run server | `python -m cardiocode.mcp.server` | Same |
| Deactivate | `deactivate` | Same |

---

## Need Help?

- GitHub Issues: https://github.com/miltosdoc/cardiocode/issues
- Include your OS, Python version (`python --version`), and the full error message
