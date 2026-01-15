<p align="center">
  <img src="https://img.shields.io/badge/Tools-50+-blue?style=for-the-badge" alt="50+ Tools">
  <img src="https://img.shields.io/badge/Guidelines-11%20ESC-red?style=for-the-badge" alt="11 ESC Guidelines">
  <img src="https://img.shields.io/badge/MCP-Compatible-green?style=for-the-badge" alt="MCP Compatible">
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" alt="MIT License">
</p>

# CardioCode

**Turn ESC Guidelines into Executable Clinical Intelligence**

CardioCode transforms European Society of Cardiology (ESC) guidelines into a comprehensive suite of clinical decision support tools. It works as an MCP (Model Context Protocol) server, giving AI assistants like Claude, OpenCode, and others instant access to validated cardiology calculations, assessments, and treatment pathways.

---

## Why CardioCode?

| Traditional Approach | With CardioCode |
|---------------------|-----------------|
| Manually look up risk scores | AI calculates CHA2DS2-VASc, GRACE, PESI instantly |
| Search through 100+ page PDFs | AI searches across 11 guidelines in seconds |
| Remember complex treatment algorithms | AI provides step-by-step HFrEF optimization |
| Miss nuanced recommendations | AI surfaces Class I/IIa/IIb distinctions |

---

## What's Included

### 50+ Clinical Tools

| Category | Tools |
|----------|-------|
| **Risk Calculators** | CHA2DS2-VASc, HAS-BLED, GRACE, Wells PE, PESI, sPESI, Geneva, HCM Risk-SCD, MAGGIC, LMNA Risk, LQTS Risk, Brugada Risk |
| **PAH Assessment** | Baseline 3-strata risk, Follow-up 4-strata risk, PH hemodynamic classification |
| **Valvular Disease** | AS, AR, MR (primary & secondary), TR, MS severity and intervention timing, Valve type selection, INR targets |
| **Device Therapy** | ICD indication (ischemic, DCM, ARVC, sarcoidosis, HCM), CRT indication, Pacing indication & mode selection |
| **VTE Management** | PE risk stratification, Thrombolysis indication, Outpatient eligibility, Anticoagulation duration |
| **Cardio-Oncology** | HFA-ICOS baseline risk, CTRCD severity, Surveillance protocols |
| **Syncope** | Risk stratification, Etiology classification, Orthostatic hypotension diagnosis, Tilt test indication |
| **Treatment Pathways** | HFrEF quadruple therapy optimization, HF device therapy, VT acute/chronic management, PE treatment, Syncope evaluation |

### 11 Pre-Indexed ESC Guidelines

- 2025 ESC/EACTS Valvular Heart Disease
- 2022 ESC Ventricular Arrhythmias & SCD
- 2022 ESC/ERS Pulmonary Hypertension
- 2022 ESC Cardio-Oncology
- 2021 ESC Heart Failure
- 2021 ESC Cardiac Pacing & CRT
- 2021 ESC Cardiovascular Prevention
- 2020 ESC Congenital Heart Disease
- 2020 ESC Sports Cardiology
- 2019 ESC Pulmonary Embolism
- 2018 ESC Syncope

---

## Quick Start

### Installation

```bash
git clone https://github.com/miltosdoc/cardiocode.git
cd cardiocode
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install pymupdf mcp
pip install -e .
```

### Connect to Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "cardiocode": {
      "command": "/full/path/to/cardiocode/venv/bin/python",
      "args": ["-m", "cardiocode.mcp.server"],
      "cwd": "/full/path/to/cardiocode"
    }
  }
}
```

### Connect to OpenCode

Add to `opencode.json`:

```json
{
  "mcp": {
    "cardiocode": {
      "type": "local",
      "command": ["/full/path/to/cardiocode/venv/bin/python", "-m", "cardiocode.mcp.server"],
      "enabled": true
    }
  }
}
```

**See [INSTALLATION.md](INSTALLATION.md) for detailed setup instructions.**

---

## Example Usage

### Ask Your AI Assistant:

> "68-year-old man with HFrEF, LVEF 28%, on ACE-I and beta-blocker. What should we add next? Does he need a device?"

**CardioCode provides:**
1. **Treatment Pathway** - Recommends adding MRA + SGLT2i, switching to ARNI
2. **Device Assessment** - Evaluates ICD/CRT indication based on QRS, etiology, time on OMT

### Or Calculate Risk Scores:

> "Calculate stroke and bleeding risk for a 75-year-old woman with AF, hypertension, and diabetes who's on aspirin"

**CardioCode returns:**
- CHA2DS2-VASc: 6 (High risk) - Anticoagulation recommended (Class I)
- HAS-BLED: 3 (High bleeding risk) - Address modifiable factors, anticoagulation still indicated

---

## Extensibility

CardioCode is designed to grow with cardiology practice:

### Add Your Own Guidelines
Drop PDF guidelines into `source_pdfs/` and run:
```
cardiocode_process_pdfs()
```
The knowledge base automatically extracts chapters, tables, and recommendations.

### Add Custom Calculators
Create new calculator modules in `cardiocode/calculators/` following the existing patterns. All tools use a consistent interface with string inputs for MCP compatibility.

### Add New Pathways
Treatment pathways in `cardiocode/pathways/` encode multi-step clinical algorithms. Add your institution's protocols or emerging guidelines.

### Contribute Back
We welcome contributions! Add tools for:
- ACC/AHA guidelines
- ESC guidelines not yet included
- Regional or institutional protocols
- Specialty-specific calculators

---

## Architecture

```
cardiocode/
├── calculators/          # Risk scores (PE, PAH, HF, arrhythmia)
├── assessments/          # Clinical decision tools (valvular, devices, VTE, syncope)
├── pathways/             # Multi-step treatment algorithms
├── knowledge/            # Pre-indexed guideline content
│   ├── guidelines/       # Extracted JSON from PDFs
│   └── severity_tables/  # Reference data
├── mcp/
│   ├── server.py         # MCP server implementation
│   └── tools.py          # Tool wrappers and registry
└── guidelines/           # Legacy structured guideline modules
```

---

## Disclaimer

CardioCode is a decision support tool, not a replacement for clinical judgment. All recommendations should be validated against current guidelines and individual patient circumstances. Not for direct patient care without physician oversight.

---

## Links

- **Documentation:** [AGENTS.md](AGENTS.md) - Complete tool reference
- **Installation:** [INSTALLATION.md](INSTALLATION.md) - Setup guide
- **Issues:** [GitHub Issues](https://github.com/miltosdoc/cardiocode/issues)
- **MCP Protocol:** [modelcontextprotocol.io](https://modelcontextprotocol.io)

---

## License

MIT License - Free for clinical, research, and educational use.

---

<p align="center">
  <b>Built for cardiologists, by cardiologists.</b><br>
  <i>Making evidence-based cardiology accessible to AI.</i>
</p>
