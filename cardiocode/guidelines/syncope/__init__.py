"""
Syncope Guidelines (ESC 2018).

ESC Guidelines for the diagnosis and management of syncope.

Reference: Eur Heart J. 2018;39(21):1883-1948. doi:10.1093/eurheartj/ehy037
"""

from cardiocode.guidelines.syncope.diagnosis import (
    classify_syncope,
    assess_risk,
    SyncopeType,
    SyncopeRisk,
)

from cardiocode.guidelines.syncope.treatment import (
    get_syncope_management,
    get_reflex_syncope_treatment,
)

__all__ = [
    "classify_syncope",
    "assess_risk",
    "SyncopeType",
    "SyncopeRisk",
    "get_syncope_management",
    "get_reflex_syncope_treatment",
]
