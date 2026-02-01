<p align="center">
  <img src="https://img.shields.io/badge/Tools-58-blue?style=for-the-badge" alt="58 Tools">
  <img src="https://img.shields.io/badge/Guidelines-11%20ESC-red?style=for-the-badge" alt="11 ESC Guidelines">
  <img src="https://img.shields.io/badge/Claude%20Code-Ready-green?style=for-the-badge" alt="Claude Code Ready">
</p>

# CardioCode

**ESC Guidelines as AI-Powered Clinical Tools**

58 clinical decision support tools built from ESC guidelines. Works instantly with Claude Code.

---

## Quick Start (2 Steps)

### 1. Clone & Install

```bash
git clone https://github.com/miltosdoc/cardiocode.git
cd cardiocode
pip install -e .
pip install mcp pymupdf
```

### 2. Use with Claude Code

```bash
cd cardiocode
claude
```

That's it. The MCP tools load automatically. Just ask clinical questions:

- *"Calculate CHA2DS2-VASc for 72yo woman with CHF and HTN"*
- *"HFrEF patient on ACE-I only, LVEF 30% - what's next?"*
- *"Assess PE risk: hemodynamically stable, sPESI 0"*
- *"Search guidelines for aortic stenosis intervention"*

---

## What's Included

### 58 Clinical Tools

| Category | Tools |
|----------|-------|
| **Risk Calculators** | CHA2DS2-VASc, HAS-BLED, GRACE, Wells PE, PESI, sPESI, Geneva, HCM Risk-SCD, MAGGIC, LMNA, LQTS, Brugada |
| **PAH Assessment** | Baseline risk, Follow-up risk, PH hemodynamic classification |
| **Valvular Disease** | AS, AR, MR (primary/secondary), TR, MS - severity & intervention timing |
| **Device Therapy** | ICD (ischemic, DCM, ARVC, sarcoidosis, HCM), CRT, Pacing indication & mode |
| **VTE Management** | PE risk stratification, Thrombolysis, Outpatient eligibility, Anticoagulation duration |
| **Cardio-Oncology** | HFA-ICOS baseline risk, CTRCD severity, Surveillance protocols |
| **Syncope** | Risk stratification, Etiology, Orthostatic hypotension, Tilt test indication |
| **Treatment Pathways** | HFrEF optimization, Device therapy, VT management, PE treatment, Syncope evaluation |
| **Knowledge Search** | Search across all guidelines, Get specific chapters |

### 11 ESC Guidelines

- 2025 ESC/EACTS Valvular Heart Disease
- 2022 Ventricular Arrhythmias & SCD
- 2022 Pulmonary Hypertension
- 2022 Cardio-Oncology
- 2021 Heart Failure
- 2021 Cardiac Pacing & CRT
- 2021 Cardiovascular Prevention
- 2020 Congenital Heart Disease
- 2020 Sports Cardiology
- 2019 Pulmonary Embolism
- 2018 Syncope

---

## Example

**You ask:**
> "68yo man with HFrEF, LVEF 28%, on ACE-I and beta-blocker. What should we add? Does he need a device?"

**CardioCode provides:**
- Add MRA + SGLT2i to reach quadruple therapy (Class I, Level A)
- Consider switching ACE-I to ARNI
- Evaluate for ICD/CRT based on QRS duration and time on optimal medical therapy

---

## Alternative Setup: Claude Desktop

If you prefer Claude Desktop over Claude Code, add to `%APPDATA%\Claude\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "cardiocode": {
      "command": "python",
      "args": ["-m", "cardiocode.mcp.server"],
      "cwd": "C:\\path\\to\\cardiocode"
    }
  }
}
```

---

## Add Your Own Guidelines

Drop PDFs into `source_pdfs/` and run:
```python
cardiocode_process_pdfs()
```

---

## Disclaimer

Decision support tool only. Not a replacement for clinical judgment. Validate against current guidelines and individual patient circumstances.

---

## License

MIT License

---

<p align="center">
  <b>Built for cardiologists, by cardiologists.</b>
</p>
