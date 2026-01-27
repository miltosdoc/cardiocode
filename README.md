# CardioCode - ESC Guidelines as Executable Clinical Logic

CardioCode is a comprehensive cardiology clinical decision support system that encodes European Society of Cardiology (ESC) guidelines as executable Python code. It exposes 32 clinical tools via MCP (Model Context Protocol) for use with AI assistants.

## Quick Start

```bash
# Clone the repository
git clone https://github.com/miltosdoc/cardiocode.git
cd cardiocode

# Install dependencies
pip install -e .

# Test the installation
python -c "from cardiocode.mcp.tools import TOOL_REGISTRY; print(f'{len(TOOL_REGISTRY)} tools available')"

# Start MCP server
python -m cardiocode.mcp.server
```

## Features

- **32 MCP Tools** for clinical decision support
- **14 Complete ESC Guideline Modules** (2018-2024)
- **Comprehensive Knowledge Resources** accessible via MCP (56,000+ characters)
- **Full Evidence Traceability** for all recommendations
- **Type-Safe** with proper Python typing

## ESC Guidelines Included

| Guideline | Year | Key Features |
|-----------|------|--------------|
| Heart Failure | 2021 | HFrEF/HFmrEF/HFpEF treatment, GDMT, ICD/CRT |
| Atrial Fibrillation | 2020/2024 | CHA2DS2-VASc, anticoagulation, rate/rhythm control |
| Ventricular Arrhythmias | 2022 | VT management, SCD prevention, ICD indication |
| Valvular Heart Disease | 2021 | AS/MR/AR severity, intervention timing |
| Chronic Coronary Syndromes | 2019 | Pre-test probability, diagnostic pathway |
| NSTE-ACS | 2020 | GRACE score, invasive strategy timing |
| STEMI | 2023 | Reperfusion timing, adjunctive therapy |
| Pulmonary Hypertension | 2022 | PH classification, PAH treatment |
| Cardio-Oncology | 2022 | CV risk assessment, CTRCD management |
| **Pulmonary Embolism** | 2019 | Wells, Geneva, PESI, risk stratification |
| **Hypertension** | 2024 | BP classification, CV risk, treatment targets |
| **CV Prevention** | 2021 | SCORE2, lipid targets, lifestyle |
| **Peripheral Arterial Disease** | 2024 | ABI, PAD, AAA, carotid stenosis |
| **Syncope** | 2018 | Classification, risk stratification, management |

## Available MCP Tools (32 Total)

### Clinical Risk Calculators (9 tools)
| Tool | Description |
|------|-------------|
| `calculate_cha2ds2_vasc` | Stroke risk in atrial fibrillation |
| `calculate_has_bled` | Bleeding risk assessment |
| `calculate_grace_score` | ACS mortality risk |
| `calculate_wells_pe` | Pulmonary embolism probability |
| `calculate_hcm_scd_risk` | 5-year SCD risk in HCM |
| `calculate_pesi` | PE severity index (30-day mortality) |
| `calculate_spesi` | Simplified PESI for PE |
| `calculate_geneva_pe` | Revised Geneva Score for PE |
| `calculate_score2` | SCORE2 10-year CV risk |

### Heart Failure
| Tool | Description |
|------|-------------|
| `get_hf_recommendations` | HFrEF/HFmrEF/HFpEF treatment (ESC 2021) |
| `assess_icd_indication` | ICD indication assessment |

### Arrhythmias
| Tool | Description |
|------|-------------|
| `get_vt_management` | VT management recommendations |

### Valvular Heart Disease
| Tool | Description |
|------|-------------|
| `assess_aortic_stenosis` | AS severity assessment (ESC 2021) |
| `assess_mitral_regurgitation` | MR severity assessment (ESC 2021) |

### Coronary Syndromes
| Tool | Description |
|------|-------------|
| `calculate_ptp` | Pre-test probability of CAD (ESC 2019) |
| `calculate_nste_grace` | NSTE-ACS GRACE with timing (ESC 2020) |

### Pulmonary Hypertension
| Tool | Description |
|------|-------------|
| `assess_pulmonary_hypertension` | PH classification and risk (ESC 2022) |

### Cardio-Oncology
| Tool | Description |
|------|-------------|
| `assess_cardio_oncology_risk` | CV risk before cancer therapy |
| `manage_ctrcd` | CTRCD management |

### Pulmonary Embolism (ESC 2019)
| Tool | Description |
|------|-------------|
| `calculate_pesi` | PESI score for 30-day mortality |
| `calculate_spesi` | Simplified PESI |
| `calculate_geneva_pe` | Revised Geneva Score |
| `calculate_age_adjusted_ddimer` | Age-adjusted D-dimer cutoff |

### Hypertension (ESC 2024)
| Tool | Description |
|------|-------------|
| `classify_blood_pressure` | BP classification per ESC 2024 |
| `assess_hypertension_risk` | CV risk in hypertension |

### CV Prevention (ESC 2021)
| Tool | Description |
|------|-------------|
| `calculate_score2` | SCORE2 10-year CV risk |
| `get_lipid_targets` | LDL-C targets by risk level |

### Peripheral Arterial Disease (ESC 2024)
| Tool | Description |
|------|-------------|
| `calculate_abi` | Ankle-Brachial Index for PAD |
| `assess_aaa` | AAA management and surveillance |

### Syncope (ESC 2018)
| Tool | Description |
|------|-------------|
| `assess_syncope_risk` | Syncope risk stratification |
| `classify_syncope` | Syncope etiology classification |

### PDF Management
| Tool | Description |
|------|-------------|
| `check_new_pdfs` | Detect new guideline PDFs |
| `get_pdf_status` | PDF processing status |
| `extract_pdf_recommendations` | Generate extraction prompts |
| `get_pdf_notifications` | PDF detection notifications |
| `acknowledge_pdf_notification` | Acknowledge notification |

## MCP Knowledge Resources

CardioCode provides comprehensive knowledge resources accessible via MCP (56,000+ characters of clinical content):

| Resource URI | Content |
|--------------|---------|
| `cardiocode://knowledge/complete` | Complete knowledge base (all guidelines) |
| `cardiocode://guidelines/heart-failure` | Heart Failure ESC 2021 |
| `cardiocode://guidelines/atrial-fibrillation` | AF ESC 2020/2024 |
| `cardiocode://guidelines/ventricular-arrhythmias` | VA/SCD ESC 2022 |
| `cardiocode://guidelines/valvular-disease` | VHD ESC 2021 |
| `cardiocode://guidelines/coronary-syndromes` | CCS/NSTE-ACS ESC 2019-2020 |
| `cardiocode://guidelines/pulmonary-hypertension` | PH ESC 2022 |
| `cardiocode://guidelines/cardio-oncology` | Cardio-Oncology ESC 2022 |
| `cardiocode://guidelines/pulmonary-embolism` | PE ESC 2019 |
| `cardiocode://guidelines/hypertension` | Hypertension ESC 2024 |
| `cardiocode://guidelines/cv-prevention` | CV Prevention ESC 2021 |
| `cardiocode://guidelines/peripheral-arterial` | PAD ESC 2024 |
| `cardiocode://guidelines/syncope` | Syncope ESC 2018 |
| `cardiocode://tools/list` | Complete tools reference |

## MCP Configuration

### Claude Desktop

Add to your Claude Desktop configuration file:

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "cardiocode": {
      "command": "python",
      "args": ["-m", "cardiocode.mcp.server"],
      "cwd": "C:/path/to/cardiocode"
    }
  }
}
```

### OpenCode

Add to `opencode.json` in your project:

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

### Claude Code CLI

The MCP server can be used with Claude Code CLI via the included configuration files.

## Usage Examples

### Python Direct Usage

```python
from cardiocode.mcp.tools import call_tool

# Calculate stroke risk
result = call_tool('calculate_cha2ds2_vasc', {
    'age': '72',
    'female': 'true',
    'chf': 'true',
    'hypertension': 'true',
    'diabetes': 'true'
})
print(f"CHA2DS2-VASc: {result['score']}")
print(f"Recommendation: {result['recommendation']}")

# Calculate PE severity
result = call_tool('calculate_pesi', {
    'age': '68',
    'cancer': 'true',
    'heart_rate_110_plus': 'true'
})
print(f"PESI Score: {result['score']}, Class: {result['risk_class']}")

# Classify blood pressure
result = call_tool('classify_blood_pressure', {
    'systolic': '158',
    'diastolic': '95'
})
print(f"BP Category: {result['category']}")

# Calculate 10-year CV risk
result = call_tool('calculate_score2', {
    'age': '55',
    'sex': 'male',
    'smoking': 'true',
    'systolic_bp': '145',
    'non_hdl_cholesterol': '5.2'
})
print(f"SCORE2: {result['risk_percent']}% risk")
```

### Via MCP Client

When connected via MCP, tools are available as:

```
Tool: calculate_cha2ds2_vasc
Parameters: { "age": "72", "female": "true", "diabetes": "true" }
```

## Project Structure

```
cardiocode/
├── core/                   # Core data types
│   ├── types.py           # Patient, VitalSigns, Labs, Echo, ECG
│   ├── recommendation.py  # Recommendation objects
│   └── evidence.py        # Evidence classification
├── guidelines/            # Guideline implementations
│   ├── heart_failure/
│   ├── atrial_fibrillation/
│   ├── ventricular_arrhythmias/
│   ├── valvular_heart_disease/
│   ├── chronic_coronary_syndromes/
│   ├── nste_acs/
│   ├── pulmonary_hypertension/
│   ├── cardio_oncology/
│   ├── pulmonary_embolism/     # NEW
│   ├── hypertension/           # NEW
│   ├── cv_prevention/          # NEW
│   ├── peripheral_arterial/    # NEW
│   └── syncope/                # NEW
├── knowledge/             # Clinical scores
│   └── scores.py
├── mcp/                   # MCP Server
│   ├── server.py         # Server implementation
│   ├── tools.py          # 32 tool definitions
│   └── knowledge.py      # Knowledge resources (56K+ chars)
├── ingestion/            # PDF processing
│   ├── pdf_watcher.py
│   └── knowledge_builder.py
└── source_pdfs/          # ESC guideline PDFs
```

## Evidence Classification

All recommendations include ESC evidence grading:

### Classes of Recommendation
- **Class I**: Is recommended (strong evidence)
- **Class IIa**: Should be considered (moderate evidence)
- **Class IIb**: May be considered (weak evidence)
- **Class III**: Is not recommended

### Levels of Evidence
- **Level A**: Multiple RCTs or meta-analyses
- **Level B**: Single RCT or large non-randomized studies
- **Level C**: Expert consensus

## Requirements

- Python 3.8+
- mcp >= 1.0.0
- pydantic >= 2.0 (optional, for validation)

## Installation

```bash
# From PyPI (when published)
pip install cardiocode

# From source
git clone https://github.com/miltosdoc/cardiocode.git
cd cardiocode
pip install -e .
```

## Testing

```bash
# Run all tests
pytest

# Test specific module
pytest tests/test_scores.py

# Quick sanity check
python -c "from cardiocode.mcp.tools import TOOL_REGISTRY; print(f'{len(TOOL_REGISTRY)} tools available')"
```

## Disclaimer

CardioCode is a clinical decision support tool intended for educational and research purposes. All recommendations should be validated by qualified healthcare professionals. Individual patient circumstances may require deviation from guideline recommendations.

Always consult the original ESC guidelines for the most current recommendations:
- https://www.escardio.org/Guidelines

## License

MIT License - Free for clinical and research use.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add your improvements
4. Submit a pull request

## Contact

- GitHub: https://github.com/miltosdoc/cardiocode
- Issues: https://github.com/miltosdoc/cardiocode/issues

---

*CardioCode: Evidence-based cardiology, simplified.*
