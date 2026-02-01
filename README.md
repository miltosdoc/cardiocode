<p align="center">
  <img src="https://img.shields.io/badge/Tools-58-blue?style=for-the-badge" alt="58 Tools">
  <img src="https://img.shields.io/badge/Guidelines-11%20ESC-red?style=for-the-badge" alt="11 ESC Guidelines">
  <img src="https://img.shields.io/badge/Claude%20Code-Ready-green?style=for-the-badge" alt="Claude Code Ready">
</p>

# CardioCode

**ESC Guidelines as AI-Powered Clinical Tools**

58 clinical decision support tools. Works instantly with Claude Code.

---

## Setup

### 1. Download

```bash
git clone https://github.com/miltosdoc/cardiocode.git
cd cardiocode
```

> **Already have it?** Run `cd cardiocode && git pull` instead to update.

### 2. Install

**Mac/Linux:**
```bash
pip3 install -e . && pip3 install mcp pymupdf
```

**Windows:**
```bash
pip install -e . && pip install mcp pymupdf
```

### 3. Run

```bash
claude
```

When prompted "Do you trust the files?", select **Yes**.

That's it. Ask clinical questions:

- *"Calculate CHA2DS2-VASc for 72yo woman with CHF and HTN"*
- *"HFrEF patient on ACE-I only, LVEF 30% - what's next?"*
- *"Search guidelines for aortic stenosis intervention"*

---

## 58 Clinical Tools

| Category | Tools |
|----------|-------|
| **Risk Calculators** | CHA2DS2-VASc, HAS-BLED, GRACE, Wells PE, PESI, sPESI, Geneva, HCM Risk-SCD, MAGGIC, LMNA, LQTS, Brugada |
| **Valvular Disease** | AS, AR, MR, TR, MS - severity & intervention timing |
| **Device Therapy** | ICD, CRT, Pacing indication & mode |
| **VTE/PE** | Risk stratification, Thrombolysis, Outpatient eligibility |
| **Heart Failure** | HFrEF treatment optimization, Device therapy pathway |
| **Syncope** | Risk stratification, Etiology classification |
| **Knowledge Search** | Search all 11 ESC guidelines |

---

## Disclaimer

Decision support tool only. Not a replacement for clinical judgment.

---

<p align="center">
  <b>Built for cardiologists, by cardiologists.</b>
</p>
