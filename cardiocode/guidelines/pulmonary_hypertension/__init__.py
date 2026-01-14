"""
ESC/ERS 2022 Pulmonary Hypertension Guidelines.

Source: 2022 ESC/ERS Guidelines for the diagnosis and treatment of pulmonary hypertension
DOI: 10.1093/eurheartj/ehac237
PDF: 2022 ESC_ERS Guidelines for the diagnosis and treatment of pulmonary hypertension.pdf

Modules:
- classification: PH classification into Groups 1-5
- diagnosis: Diagnostic algorithms and workup
- treatment: PAH-specific therapy and risk stratification
"""

from cardiocode.guidelines.pulmonary_hypertension.classification import (
    PHGroup,
    PHClassification,
    classify_ph,
)
from cardiocode.guidelines.pulmonary_hypertension.diagnosis import (
    diagnose_ph,
)
from cardiocode.guidelines.pulmonary_hypertension.treatment import (
    PAHRiskCategory,
    assess_pah_risk,
    get_pah_treatment,
)

GUIDELINE_INFO = {
    "name": "2022 ESC/ERS Guidelines for the diagnosis and treatment of pulmonary hypertension",
    "short_name": "ESC/ERS PH 2022",
    "year": 2022,
    "doi": "10.1093/eurheartj/ehac237",
    "pdf": "2022 ESC_ERS Guidelines for the diagnosis and treatment of pulmonary hypertension.pdf",
    "status": "complete",
}

__all__ = [
    "GUIDELINE_INFO",
    # Classification
    "PHGroup",
    "PHClassification",
    "classify_ph",
    # Diagnosis
    "diagnose_ph",
    # Treatment
    "PAHRiskCategory",
    "assess_pah_risk",
    "get_pah_treatment",
]
