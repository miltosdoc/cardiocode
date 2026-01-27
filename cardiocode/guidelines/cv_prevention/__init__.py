"""
Cardiovascular Prevention Guidelines (ESC 2021).

ESC Guidelines on cardiovascular disease prevention in clinical practice.

Reference: Eur Heart J. 2021;42(34):3227-3337. doi:10.1093/eurheartj/ehab484
"""

from cardiocode.guidelines.cv_prevention.risk_assessment import (
    calculate_score2,
    calculate_score2_op,
    get_risk_category,
    CVRiskLevel,
)

from cardiocode.guidelines.cv_prevention.treatment import (
    get_prevention_recommendations,
    get_lipid_targets,
    get_bp_targets,
)

__all__ = [
    "calculate_score2",
    "calculate_score2_op",
    "get_risk_category",
    "CVRiskLevel",
    "get_prevention_recommendations",
    "get_lipid_targets",
    "get_bp_targets",
]
