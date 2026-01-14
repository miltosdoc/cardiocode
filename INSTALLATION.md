# 🌍 Universal CardioCode Installation Guide

This guide works for **all users** on macOS, Linux, and Windows with comprehensive troubleshooting.

## 🔍 Step 1: Check Your System

### Check Python Installation
```bash
# Check available Python versions
python --version 2>/dev/null || python3 --version 2>/dev/null || echo "Python not found"

# List all Python versions (macOS/Linux)
ls /usr/bin/python* 2>/dev/null
ls /opt/homebrew/bin/python* 2>/dev/null
ls ~/.pyenv/versions 2>/dev/null

# Windows (Command Prompt)
where python

# Windows (PowerShell)
Get-Command python* -ErrorAction SilentlyContinue
```

### Determine Your Platform
```bash
# macOS/Linux
uname -s

# Windows
echo $env:OS  # PowerShell
```

## 🐍 Step 2: Install Python 3.11+ (if needed)

### macOS
```bash
# Option 1: Homebrew (recommended)
brew install python@3.11

# Option 2: Pyenv (multiple versions)
brew install pyenv
pyenv install 3.11.7
pyenv global 3.11.7

# Option 3: Download from python.org
# Download: https://www.python.org/downloads/macos/
```

### Linux (Ubuntu/Debian)
```bash
# Option 1: APT repository
sudo apt update
sudo apt install python3.11 python3.11-pip python3.11-venv

# Option 2: Deadsnakes PPA (for older Ubuntu)
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.11 python3.11-pip python3.11-venv

# Option 3: Pyenv
curl https://pyenv.run | bash
# Add to ~/.bashrc or ~/.zshrc:
export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init --path)"
eval "$(pyenv init -)"
pyenv install 3.11.7
```

### Linux (CentOS/RHEL/Fedora)
```bash
# Fedora
sudo dnf install python3.11 python3.11-pip

# CentOS/RHEL (with EPEL)
sudo yum install epel-release
sudo yum install python3.11 python3.11-pip
```

### Windows
```powershell
# Option 1: Download from python.org
# Visit: https://www.python.org/downloads/windows/
# Download Python 3.11+ installer and check "Add to PATH"

# Option 2: Microsoft Store
# Search "Python 3.11" in Microsoft Store

# Option 3: Chocolatey
choco install python311

# Option 4: Winget
winget install Python.Python.311

# Verify installation
python --version
```

## 📦 Step 3: Install CardioCode

### Find Your Python Command
```bash
# Test different Python commands
python3.11 --version 2>/dev/null && echo "Use python3.11"
python3.10 --version 2>/dev/null && echo "Use python3.10"
python3 --version 2>/dev/null && echo "Use python3"
python --version 2>/dev/null && echo "Use python"
```

### Clone and Install
```bash
# 1. Clone repository (fresh)
rm -rf cardiocode
git clone https://github.com/miltosdoc/cardiocode.git
cd cardiocode

# 2. Install dependencies (replace with your Python command)
# Use python3.11, python3.10, python3, or python as appropriate
python3.11 -m pip install --user pymupdf 'mcp>=1.0.0'

# 3. Install CardioCode
python3.11 -m pip install --user -e .

# 4. Test installation
python3.11 -m cardiocode.mcp.server
```

## 🔧 Platform-Specific Notes

### macOS Users
```bash
# If you have multiple Python versions:
# Use the full path to avoid conflicts
/opt/homebrew/bin/python3.11 -m pip install --user pymupdf 'mcp>=1.0.0'

# Create aliases (add to ~/.zshrc):
alias py311="/opt/homebrew/bin/python3.11"
alias pip311="/opt/homebrew/bin/python3.11 -m pip"
```

### Linux Users
```bash
# Use python3.11-pip if available
python3.11 -m pip install --user pymupdf 'mcp>=1.0.0'

# Or use pip3.11 directly
pip3.11 install --user pymupdf 'mcp>=1.0.0'

# Create virtual environment (recommended)
python3.11 -m venv cardiocode-env
source cardiocode-env/bin/activate
pip install pymupdf 'mcp>=1.0.0'
pip install -e .
```

### Windows Users
```powershell
# PowerShell commands
python -m pip install --user pymupdf 'mcp>=1.0.0'
python -m pip install --user -e .

# Or if using py launcher
py -3.11 -m pip install --user pymupdf 'mcp>=1.0.0'
py -3.11 -m pip install --user -e .

# Test server
py -3.11 -m cardiocode.mcp.server
```

## 🛠️ Universal Troubleshooting

### Problem: "Command not found: python3.11"
**Solution**: Use the Python command that works for you
```bash
# Test these commands:
python --version
python3 --version
python3.11 --version

# Use whatever version is 3.10+
python3.11 -m pip install  # OR
python3 -m pip install     # OR
python -m pip install
```

### Problem: "pip not recognized"
**Solution**: Use `python -m pip` instead of `pip`
```bash
# Instead of: pip install package
# Use: python -m pip install package
python3.11 -m pip install --user pymupdf 'mcp>=1.0.0'
```

### Problem: "MCP package not available"
**Cause**: MCP requires Python 3.10+
**Solution**: Ensure you're using Python 3.10 or later

```bash
# Check your Python version
python3.11 --version  # Should be 3.10.x or 3.11.x

# If using older Python, install 3.11:
# macOS: brew install python@3.11
# Ubuntu: sudo apt install python3.11
# Windows: Download from python.org
```

### Problem: Permission Denied
**Solution**: Use `--user` flag or virtual environment

```bash
# Option 1: User installation
python3.11 -m pip install --user <package>

# Option 2: Virtual environment
python3.11 -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows
pip install <package>
```

### Problem: "ModuleNotFoundError: No module named 'cardiocode'"
**Solution**: Install in development mode

```bash
cd cardiocode
python3.11 -m pip install --user -e .
```

## 🧪 Verification Tests

### Test 1: Python Version
```bash
# Should show 3.10.x or 3.11.x
python3.11 --version
```

### Test 2: Package Installation
```bash
# Should show package info
python3.11 -m pip show mcp
python3.11 -m pip show pymupdf
```

### Test 3: CardioCode Import
```bash
# Should complete without error
python3.11 -c "import cardiocode.mcp.server; print('✅ CardioCode imported successfully')"
```

### Test 4: Server Startup
```bash
# Should show "MCP package loaded successfully"
python3.11 -m cardiocode.mcp.server
```

## 💡 Pro Tips for All Users

### Use Virtual Environments (Recommended)
```bash
# Create and activate
python3.11 -m venv cardiocode-env
source cardiocode-env/bin/activate  # Linux/macOS
# or
cardiocode-env\Scripts\activate     # Windows

# Install (no --user flag needed in venv)
pip install pymupdf 'mcp>=1.0.0'
pip install -e .

# Run server
python -m cardiocode.mcp.server
```

### Create Permanent Aliases
```bash
# Add to your shell profile (~/.bashrc, ~/.zshrc, ~/.profile):
alias py311="python3.11"
alias pip311="python3.11 -m pip"

# Then use:
pip311 install --user pymupdf 'mcp>=1.0.0'
```

### Update Regularly
```bash
# Update CardioCode
cd cardiocode
git pull origin main
python3.11 -m pip install --user -e .

# Update dependencies
python3.11 -m pip install --user --upgrade pymupdf mcp
```

## 📱 Editor Configuration (All Platforms)

### VS Code/Cursor/Windsurf
```json
{
  "mcpServers": {
    "cardiocode": {
      "command": "python3.11",
      "args": ["-m", "cardiocode.mcp.server"],
      "cwd": "/path/to/your/cardiocode"
    }
  }
}
```

### OpenCode Desktop
```json
{
  "mcp": {
    "cardiocode": {
      "type": "local",
      "command": ["python3.11", "-m", "cardiocode.mcp.server"],
      "enabled": true
    }
  }
}
```

## 🆘 Still Stuck?

1. **Check Python version**: Must be 3.10+
2. **Use `python -m pip`**: Never use bare `pip`
3. **Use `--user` flag**: Or use virtual environment
4. **Full paths work**: If commands fail, use full paths
5. **Check Git clone**: Ensure you're in the right directory

---

**🌟 This guide works for everyone!** Whether you're on macOS, Linux, or Windows, a beginner or expert, these steps will get CardioCode running.