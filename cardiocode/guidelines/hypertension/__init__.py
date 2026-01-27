"""
Hypertension Guidelines (ESC 2024).

ESC Guidelines for the management of elevated blood pressure and hypertension.

Reference: Eur Heart J. 2024;45(38):3912-4018. doi:10.1093/eurheartj/ehae178
"""

from cardiocode.guidelines.hypertension.diagnosis import (
    classify_blood_pressure,
    assess_cv_risk,
    BPCategory,
    CVRiskCategory,
)

from cardiocode.guidelines.hypertension.treatment import (
    get_treatment_recommendations,
    get_bp_target,
    get_initial_therapy,
)

__all__ = [
    "classify_blood_pressure",
    "assess_cv_risk",
    "BPCategory",
    "CVRiskCategory",
    "get_treatment_recommendations",
    "get_bp_target",
    "get_initial_therapy",
]
