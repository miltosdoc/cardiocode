"""
ESC 2022 Cardio-Oncology Guidelines.

Source: 2022 ESC Guidelines on cardio-oncology
DOI: 10.1093/eurheartj/ehac244
PDF: ehac244.pdf

Modules:
- baseline_risk: Pre-treatment CV risk assessment (HFA-ICOS)
- surveillance: Cardiac monitoring protocols during cancer therapy
- cardiotoxicity: CTRCD definition and management
"""

from cardiocode.guidelines.cardio_oncology.baseline_risk import (
    CardiotoxicityRisk,
    CancerTherapyType,
    CVRiskFactor,
    BaselineRiskAssessment,
    calculate_hfa_icos_risk,
    assess_anthracycline_risk,
    assess_her2_therapy_risk,
    assess_baseline_cv_risk,
)
from cardiocode.guidelines.cardio_oncology.surveillance import (
    SurveillanceIntensity,
    SurveillanceSchedule,
    get_anthracycline_surveillance,
    get_her2_surveillance,
    get_vegf_inhibitor_surveillance,
    get_checkpoint_inhibitor_surveillance,
    get_surveillance_protocol,
)
from cardiocode.guidelines.cardio_oncology.cardiotoxicity import (
    CTRCDSeverity,
    CardiotoxicityType,
    CTRCDAssessment,
    define_ctrcd,
    manage_ctrcd,
    manage_ici_myocarditis,
    manage_cardiotoxicity,
)

GUIDELINE_INFO = {
    "name": "2022 ESC Guidelines on cardio-oncology",
    "short_name": "ESC Cardio-Oncology 2022",
    "year": 2022,
    "doi": "10.1093/eurheartj/ehac244",
    "pdf": "ehac244.pdf",
    "status": "complete",
}

__all__ = [
    "GUIDELINE_INFO",
    # Baseline risk assessment
    "CardiotoxicityRisk",
    "CancerTherapyType",
    "CVRiskFactor",
    "BaselineRiskAssessment",
    "calculate_hfa_icos_risk",
    "assess_anthracycline_risk",
    "assess_her2_therapy_risk",
    "assess_baseline_cv_risk",
    # Surveillance
    "SurveillanceIntensity",
    "SurveillanceSchedule",
    "get_anthracycline_surveillance",
    "get_her2_surveillance",
    "get_vegf_inhibitor_surveillance",
    "get_checkpoint_inhibitor_surveillance",
    "get_surveillance_protocol",
    # Cardiotoxicity management
    "CTRCDSeverity",
    "CardiotoxicityType",
    "CTRCDAssessment",
    "define_ctrcd",
    "manage_ctrcd",
    "manage_ici_myocarditis",
    "manage_cardiotoxicity",
]
