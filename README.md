# CardioCode

Clinical decision support system that encodes ESC (European Society of Cardiology) guidelines as executable Python code. Works as an MCP server for AI assistants.

## Installation

**See [INSTALLATION.md](INSTALLATION.md) for step-by-step setup on macOS and Windows.**

### Quick Install (if you have Python 3.10+)

```bash
git clone https://github.com/miltosdoc/cardiocode.git
cd cardiocode
python3 -m pip install --user pymupdf mcp
python3 -m pip install --user -e .
python3 -m cardiocode.mcp.server
```

On Windows, use `python` instead of `python3`.

## MCP Server Configuration

### Claude Desktop

Add to your Claude Desktop config:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "cardiocode": {
      "command": "python3",
      "args": ["-m", "cardiocode.mcp.server"],
      "cwd": "/path/to/cardiocode"
    }
  }
}
```

### VS Code / Cursor / Windsurf

Add to your editor's MCP settings (same format as above).

### OpenCode

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

## Available Tools

### Stroke Prevention
- `calculate_cha2ds2_vasc` - CHA2DS2-VASc stroke risk score
- `calculate_has_bled` - HAS-BLED bleeding risk score

### Heart Failure
- `get_hf_recommendations` - ESC 2021 heart failure treatment

### Arrhythmias & Devices
- `calculate_hcm_scd_risk` - HCM sudden cardiac death risk
- `get_icd_indication` - ICD indication assessment
- `get_vt_management` - Ventricular tachycardia management

### Valvular Heart Disease
- `assess_aortic_stenosis` - Aortic stenosis severity and intervention timing
- `assess_mitral_regurgitation` - Mitral regurgitation assessment

### Coronary Syndromes
- `calculate_ptp` - Pre-test probability of CAD (ESC 2019)
- `calculate_nste_grace` - NSTE-ACS GRACE score

### Other
- `assess_pulmonary_hypertension` - PAH assessment (ESC 2022)
- `assess_cardio_oncology_risk` - Cardio-oncology CV risk
- `manage_ctrcd` - Cancer therapy cardiac dysfunction

## Guidelines Included

- Valvular Heart Disease (ESC 2021, updated 2025)
- Atrial Fibrillation (ESC 2020/2024)
- Heart Failure (ESC 2021)
- Ventricular Arrhythmias (ESC 2022)
- Pulmonary Hypertension (ESC 2022)
- Cardio-Oncology (ESC 2022)
- Chronic Coronary Syndromes (ESC 2019)
- NSTE-ACS (ESC 2020)
- STEMI (ESC 2023)

## Usage Example

```python
from cardiocode.mcp.tools import tool_calculate_cha2ds2_vasc

# 72-year-old woman with diabetes and AF
result = tool_calculate_cha2ds2_vasc(age='72', female='true', diabetes='true')
print(f"CHA2DS2-VASc: {result['score']}")
```

## Troubleshooting

See [INSTALLATION.md](INSTALLATION.md) for common issues and solutions.

## Links

- **Repository:** https://github.com/miltosdoc/cardiocode
- **Issues:** https://github.com/miltosdoc/cardiocode/issues

## License

MIT License - Free for clinical and research use
