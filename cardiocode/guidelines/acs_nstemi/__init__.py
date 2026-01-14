"""
ESC 2020 NSTE-ACS Guidelines - Encoded as Executable Clinical Logic.

Source: 2020 ESC Guidelines for the management of acute coronary syndromes 
        in patients presenting without persistent ST-segment elevation
DOI: 10.1093/eurheartj/ehaa575
PDF: ehaa605.pdf

This module provides:
- Risk stratification (GRACE score)
- Diagnosis and troponin algorithms
- Invasive strategy timing
- Antithrombotic therapy
- Secondary prevention
"""

from cardiocode.guidelines.acs_nstemi.diagnosis import (
    diagnose_nste_acs,
    apply_hs_troponin_algorithm,
)

from cardiocode.guidelines.acs_nstemi.risk_stratification import (
    stratify_risk,
    get_invasive_timing,
)

from cardiocode.guidelines.acs_nstemi.antithrombotic import (
    get_antithrombotic_strategy,
    get_dual_antiplatelet_therapy,
    manage_anticoagulation,
)

from cardiocode.guidelines.acs_nstemi.secondary_prevention import (
    get_secondary_prevention,
)

# Guideline metadata
GUIDELINE_INFO = {
    "name": "2020 ESC Guidelines for the management of acute coronary syndromes in patients presenting without persistent ST-segment elevation",
    "short_name": "ESC NSTE-ACS 2020",
    "year": 2020,
    "doi": "10.1093/eurheartj/ehaa575",
    "pdf": "ehaa605.pdf",
    "citation": "Collet JP, et al. Eur Heart J. 2021;42(14):1289-1367.",
}

__all__ = [
    "diagnose_nste_acs",
    "apply_hs_troponin_algorithm",
    "stratify_risk",
    "get_invasive_timing",
    "get_antithrombotic_strategy",
    "get_dual_antiplatelet_therapy",
    "manage_anticoagulation",
    "get_secondary_prevention",
    "GUIDELINE_INFO",
]
