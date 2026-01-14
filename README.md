# 🏥 CardioCode - ESC Guidelines as Executable Clinical Logic

CardioCode is a comprehensive cardiology decision support system that encodes European Society of Cardiology (ESC) clinical guidelines as executable Python code. Perfect for clinicians, researchers, and AI assistants.

## 🚀 Installation

**🎯 NEW USERS: Start with the [Universal Installation Guide](INSTALLATION.md)** - Works for macOS, Linux, Windows with step-by-step Python setup and troubleshooting for all skill levels.

### Quick Install (Advanced Users)
If you're comfortable with Python and have Python 3.10+:

```bash
git clone https://github.com/miltosdoc/cardiocode.git
cd cardiocode
python3.11 -m pip install --user pymupdf 'mcp>=1.0.0'
python3.11 -m pip install --user -e .
python3.11 -m cardiocode.mcp.server
```

**🎯 FIRST TIME USERS?** Use the [Universal Installation Guide](INSTALLATION.md) for step-by-step setup with Python installation and troubleshooting for all platforms.

#### Method 3: Windows Specific
```cmd
# On Windows, use these commands if pip has issues:
pip install --user cardiocode pymupdf
python -m cardiocode.mcp.server
```

## 🏃 MCP Server Setup for Editors

### VS Code / Cursor / Windsurf
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
      "cwd": "/path/to/cardiocode"
    }
  }
}
```

**⚠️ Important**: Set `cwd` to your CardioCode directory path!

### Direct Usage (Fallback)
If MCP package installation fails, CardioCode automatically falls back to limited functionality. Install MCP package for full features.

## 📋 Available MCP Tools (15 total)

### 🔬 Stroke Prevention
- `calculate_cha2ds2_vasc` - CHA₂DS₂-VASc stroke risk
- `calculate_has_bled` - HAS-BLED bleeding risk

### ❤️ Heart Failure  
- `get_hf_recommendations` - ESC 2021 HF treatment

### ⚡ Arrhythmias & Devices
- `calculate_hcm_scd_risk` - HCM sudden cardiac death risk
- `get_icd_indication` - ICD indication assessment  
- `get_vt_management` - Ventricular tachycardia management

### 🫁 Other Cardiology
- `assess_pulmonary_hypertension` - PAH assessment (ESC 2022)
- `assess_cardio_oncology_risk` - Cardio-oncology CV risk
- `manage_ctrcd` - Cancer therapy cardiac dysfunction

### 🆕 Valvular Heart Disease (ESC 2021+2025)
- `assess_aortic_stenosis` - AS severity & timing
- `assess_mitral_regurgitation` - MR severity assessment

### 🩹 Coronary Syndromes
- `calculate_ptp` - Pre-test probability of CAD (ESC 2019)
- `calculate_nste_grace` - NSTE-ACS GRACE score

## 🏥 Guidelines Included (2019-2025)

### 📚 Core Guidelines
- **Heart Failure (ESC 2021)**
- **Ventricular Arrhythmias (ESC 2022)**  
- **Pulmonary Hypertension (ESC 2022)**
- **Cardio-Oncology (ESC 2022)**
- **Valvular Heart Disease (ESC 2021)** - ✅ **Updated with 2025**
- **Atrial Fibrillation (ESC 2020/2024)**
- **Chronic Coronary Syndromes (ESC 2019)**
- **NSTE-ACS (ESC 2020)**
- **STEMI (ESC 2023)**

## 🔧 Cross-Platform Fixes (Latest)

### ✅ Path Separator Issue Fixed
- **Problem**: Windows paths (`\\`) failing on macOS/Linux
- **Solution**: Cross-platform `Path().as_posix()` normalization
- **Files Updated**: `pdf_watcher.py`, `knowledge_extractor.py`

### ✅ Web Search Intelligence Enhanced  
- **Problem**: Generic search downloads presentations instead of guidelines
- **Solution**: Prioritizes authoritative sources (ESC, PubMed, ACC/AHA)
- **Files Updated**: `dynamic_generator.py`

### ✅ Installation Script Improved
- **New**: `install.py` with platform detection and dependency management
- **Features**: Windows/macOS/Linux support, automatic setup, error handling

## 🚨 Troubleshooting

### MCP Package Issues
**If you see**: "MCP package not available" 
**Solution**: Install with `--user` flag:
```bash
pip3 install --user 'mcp>=1.0.0'
```

### Path Errors
**If you see**: "no such file: 'source_pdfs\\file.pdf'"
**Solution**: Fixed with path normalization - should work cross-platform

### Editor Integration
**For VS Code/Cursor**: Use MCP extension and set `cwd` to CardioCode directory
**Direct usage**: `python3 -m cardiocode.mcp.server` from CardioCode directory

## 🐛 Bug Reports & Feature Requests

- **Issues**: https://github.com/miltosdoc/cardiocode/issues
- **Discussions**: https://github.com/miltosdoc/cardiocode/discussions
- **Contributions**: Welcome! See `CONTRIBUTING.md`

---

**🎯 For GitHub Push**: Include all modified files:
- `cardiocode/ingestion/pdf_watcher.py` 
- `cardiocode/ingestion/knowledge_extractor.py`
- `cardiocode/ingestion/dynamic_generator.py`
- `install.py`
- `INSTALL_GUIDE.md` (this file)

## 📋 Available MCP Tools (15 total)

### Stroke Prevention
- `calculate_cha2ds2_vasc` - CHA₂DS₂-VASc stroke risk
- `calculate_has_bled` - HAS-BLED bleeding risk

### Heart Failure  
- `get_hf_recommendations` - ESC 2021 HF treatment

### Arrhythmias & Devices
- `calculate_hcm_scd_risk` - HCM sudden cardiac death risk
- `get_icd_indication` - ICD indication assessment  
- `get_vt_management` - Ventricular tachycardia management

### Other Cardiology
- `assess_pulmonary_hypertension` - PAH assessment (ESC 2022)
- `assess_cardio_oncology_risk` - Cardio-oncology CV risk
- `manage_ctrcd` - Cancer therapy cardiac dysfunction

### NEW: Valvular Heart Disease (ESC 2021)
- `assess_aortic_stenosis` - AS severity & timing
- `assess_mitral_regurgitation` - MR severity assessment

### NEW: Coronary Syndromes
- `calculate_ptp` - Pre-test probability of CAD (ESC 2019)
- `calculate_nste_grace` - NSTE-ACS GRACE score

## 🏥 Guidelines Included (2019-2024)

✅ **Valvular Heart Disease** (ESC 2021)
✅ **Atrial Fibrillation** (ESC 2020/2024)  
✅ **Heart Failure** (ESC 2021)
✅ **Ventricular Arrhythmias** (ESC 2022)
✅ **Pulmonary Hypertension** (ESC 2022)
✅ **Cardio-Oncology** (ESC 2022)
✅ **Chronic Coronary Syndromes** (ESC 2019)
✅ **NSTE-ACS** (ESC 2020)
✅ **STEMI** (ESC 2023)

## 🔧 MCP Configuration

### OpenCode Desktop
Add to `opencode.json` (included):
```json
{
  "mcp": {
    "cardiocode": {
      "type": "local",
      "command": ["python", "-m", "cardiocode.mcp.server"],
      "enabled": true
    }
  }
}
```

### Claude Desktop
Add to Claude config (template included):
```json
{
  "mcpServers": {
    "cardiocode": {
      "command": "python",
      "args": ["-m", "cardiocode.mcp.server"],
      "cwd": "/path/to/cardiocode"
    }
  }
}
```

## 📚 Features

- ✅ **15 MCP tools** for clinical decision support
- ✅ **9 complete ESC guideline modules** 
- ✅ **Automatic PDF ingestion** system
- ✅ **Type-safe** recommendations with evidence levels
- ✅ **Zero-configuration** deployment
- ✅ **Cross-guideline** conflict detection
- ✅ **Python 3.8+** compatibility

## 🏥‍⚕️ Usage Examples

```python
# Atrial fibrillation management
from cardiocode.mcp.tools import tool_calculate_cha2ds2_vasc, get_anticoagulation_recommendation

# 72yo man with diabetes and AF
result = tool_calculate_cha2ds2_vasc(age='72', female='true', diabetes='true')
print(f"CHA2DS2-VASc: {result['score']}")

# Get anticoagulation recommendation
recs = get_anticoagulation_recommendation(patient)
for rec in recs.recommendations:
    print(f"- {rec.action}")
```

## 🔬 Clinical Validation

All clinical logic is validated against:
- ESC guideline source documents
- Evidence class/level mappings
- Cross-guideline consistency
- Real-world clinical scenarios

## 📖 PDF Management

The system includes all ESC guideline PDFs (2019-2024) in `source_pdfs/` with automatic detection and knowledge extraction capabilities.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add your improvements
4. Submit a pull request

## 📄 License

MIT License - Free for clinical and research use

## 🆘 Getting Help

### 🎯 First-Time Installation
- **Universal Guide**: [INSTALLATION.md](INSTALLATION.md) - Step-by-step for all platforms
- **Common Issues**: Python version conflicts, MCP package requirements
- **Platform Support**: macOS, Linux, Windows covered

### 🔧 Installation Problems
1. Check Python version: `python3.11 --version` (must be 3.10+)
2. Check packages: `python3.11 -m pip list | grep -E "(mcp|pymupdf)"`
3. Test import: `python3.11 -c "import cardiocode.mcp.server"`
4. Update: `git pull origin main && python3.11 -m pip install --user -e .`

### 💬 Community Support
- **Issues**: https://github.com/miltosdoc/cardiocode/issues
- **Discussions**: https://github.com/miltosdoc/cardiocode/discussions
- **Installation Help**: Comment on existing issues or start new discussion

### 📧 Direct Support
Include:
- Your OS (macOS/Linux/Windows + version)
- Python version: `python --version`
- Error message (full output)
- Steps you've tried

## 🌟 GitHub Repository

**https://github.com/miltosdoc/cardiocode**

---

*CardioCode: Evidence-based cardiology, simplified.*