"""
Non-ST-Elevation Acute Coronary Syndromes - ESC 2020 Guidelines.

Comprehensive NSTE-ACS management including:
- Initial assessment and risk stratification
- GRACE score calculation
- Antithrombotic therapy
- Invasive strategy timing
- Revascularization decisions
- Secondary prevention
"""

from .risk_stratification import (
    calculate_grace_score,
    assess_risk_category,
    get_invasive_strategy_timing,
)
from .antithrombotic import (
    get_antiplatelet_therapy,
    get_anticoagulation_therapy,
    get_dapt_duration,
)
from .invasive_strategy import (
    assess_invasive_strategy_indication,
    choose_revascularization_approach,
)
from .medical_management import (
    get_initial_medical_therapy,
    get_secondary_prevention,
)

# Guideline metadata
GUIDELINE_INFO = {
    "name": "2020 ESC Guidelines for the management of acute coronary syndromes in patients presenting without persistent ST-segment elevation",
    "short_name": "ESC NSTE-ACS 2020",
    "year": 2020,
    "doi": "10.1093/eurheartj/ehaa475",
    "pdf": "ehaa475.pdf",
    "citation": "Collet JP, et al. Eur Heart J. 2021;42(14):1289-1368.",
}

__all__ = [
    # Risk stratification
    "calculate_grace_score",
    "assess_risk_category",
    "get_invasive_strategy_timing",
    # Antithrombotic
    "get_antiplatelet_therapy",
    "get_anticoagulation_therapy",
    "get_dapt_duration",
    # Invasive strategy
    "assess_invasive_strategy_indication",
    "choose_revascularization_approach",
    # Medical management
    "get_initial_medical_therapy",
    "get_secondary_prevention",
    # Metadata
    "GUIDELINE_INFO",
]