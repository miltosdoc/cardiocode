# 🏥 CardioCode - ESC Guidelines as Executable Clinical Logic

CardioCode is a comprehensive cardiology decision support system that encodes European Society of Cardiology (ESC) clinical guidelines as executable Python code. Perfect for clinicians, researchers, and AI assistants.

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/miltosdoc/cardiocode.git
cd cardiocode

# Install (simple)
pip install cardiocode

# Start MCP server
python -m cardiocode.mcp.server

# Or use in Python
python -c "from cardiocode.mcp.tools import tool_calculate_cha2ds2_vasc; print(tool_calculate_cha2ds2_vasc(age='72', female='true', diabetes='true'))"
```

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

## 🌟 GitHub Repository

**https://github.com/miltosdoc/cardiocode**

---

*CardioCode: Evidence-based cardiology, simplified.*