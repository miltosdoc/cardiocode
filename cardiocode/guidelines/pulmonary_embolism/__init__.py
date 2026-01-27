"""
Pulmonary Embolism Guidelines (ESC 2019).

ESC Guidelines for the diagnosis and management of acute pulmonary embolism
developed in collaboration with the European Respiratory Society (ERS).

Reference: Eur Heart J. 2020;41(4):543-603. doi:10.1093/eurheartj/ehz405
"""

from cardiocode.guidelines.pulmonary_embolism.diagnosis import (
    calculate_wells_pe_score,
    calculate_revised_geneva_score,
    calculate_pesi_score,
    calculate_simplified_pesi,
    assess_pe_probability,
    PEProbability,
    PESIRiskClass,
)

from cardiocode.guidelines.pulmonary_embolism.treatment import (
    get_pe_treatment_recommendations,
    assess_thrombolysis_indication,
    get_anticoagulation_recommendations,
)

__all__ = [
    "calculate_wells_pe_score",
    "calculate_revised_geneva_score",
    "calculate_pesi_score",
    "calculate_simplified_pesi",
    "assess_pe_probability",
    "PEProbability",
    "PESIRiskClass",
    "get_pe_treatment_recommendations",
    "assess_thrombolysis_indication",
    "get_anticoagulation_recommendations",
]
