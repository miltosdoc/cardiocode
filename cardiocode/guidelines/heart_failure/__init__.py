"""
ESC 2021 Heart Failure Guidelines - Encoded as Executable Clinical Logic.

Source: 2021 ESC Guidelines for the diagnosis and treatment of acute and chronic heart failure
DOI: 10.1093/eurheartj/ehab364
PDF: ehab364.pdf

This module provides:
- Diagnostic algorithms for heart failure
- Treatment recommendations by HF phenotype (HFrEF, HFmrEF, HFpEF)
- Device therapy indications (ICD, CRT)
- Monitoring and follow-up guidance
- Acute heart failure management

Every recommendation includes ESC evidence class/level and study citations.
"""

from cardiocode.guidelines.heart_failure.diagnosis import (
    diagnose_heart_failure,
    classify_hf_phenotype,
    assess_congestion,
    assess_perfusion,
)

from cardiocode.guidelines.heart_failure.treatment import (
    get_hfref_treatment,
    get_hfmref_treatment,
    get_hfpef_treatment,
    get_diuretic_recommendations,
    optimize_gdmt,
)

from cardiocode.guidelines.heart_failure.devices import (
    assess_icd_indication,
    assess_crt_indication,
)

from cardiocode.guidelines.heart_failure.monitoring import (
    get_followup_schedule,
    get_monitoring_parameters,
)

from cardiocode.guidelines.heart_failure.acute import (
    assess_acute_hf,
    get_acute_hf_treatment,
)

# Guideline metadata
GUIDELINE_INFO = {
    "name": "2021 ESC Guidelines for the diagnosis and treatment of acute and chronic heart failure",
    "short_name": "ESC HF 2021",
    "year": 2021,
    "doi": "10.1093/eurheartj/ehab364",
    "pdf": "ehab364.pdf",
    "citation": "McDonagh TA, et al. Eur Heart J. 2021;42(36):3599-3726.",
}

__all__ = [
    "diagnose_heart_failure",
    "classify_hf_phenotype",
    "assess_congestion",
    "assess_perfusion",
    "get_hfref_treatment",
    "get_hfmref_treatment", 
    "get_hfpef_treatment",
    "get_diuretic_recommendations",
    "optimize_gdmt",
    "assess_icd_indication",
    "assess_crt_indication",
    "get_followup_schedule",
    "get_monitoring_parameters",
    "assess_acute_hf",
    "get_acute_hf_treatment",
    "GUIDELINE_INFO",
]
