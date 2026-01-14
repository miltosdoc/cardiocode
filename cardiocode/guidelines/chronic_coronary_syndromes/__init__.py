"""
Chronic Coronary Syndromes - ESC 2019 Guidelines.

Comprehensive CCS management including:
- Diagnosis and risk stratification
- Pre-test probability of CAD
- Optimal medical therapy
- Revascularization decisions
- Secondary prevention
- DAPT duration
"""

from .diagnosis import (
    calculate_pretest_probability,
    get_diagnostic_strategy,
    interpret_stress_test,
)
from .medical_therapy import (
    get_antianginal_therapy,
    get_secondary_prevention,
    optimize_medical_therapy,
)
from .revascularization import (
    assess_revascularization_indication,
    choose_pci_vs_cabg,
)
from .antithrombotic import (
    get_antiplatelet_therapy,
    get_dapt_duration,
)

# Guideline metadata
GUIDELINE_INFO = {
    "name": "2019 ESC Guidelines for the diagnosis and management of chronic coronary syndromes",
    "short_name": "ESC CCS 2019",
    "year": 2019,
    "doi": "10.1093/eurheartj/ehz425",
    "pdf": "ehz425.pdf",
    "citation": "Knuuti J, et al. Eur Heart J. 2020;41(3):407-477.",
}

__all__ = [
    # Diagnosis
    "calculate_pretest_probability",
    "get_diagnostic_strategy",
    "interpret_stress_test",
    # Medical therapy
    "get_antianginal_therapy",
    "get_secondary_prevention",
    "optimize_medical_therapy",
    # Revascularization
    "assess_revascularization_indication",
    "choose_pci_vs_cabg",
    # Antithrombotic
    "get_antiplatelet_therapy",
    "get_dapt_duration",
    # Metadata
    "GUIDELINE_INFO",
]
