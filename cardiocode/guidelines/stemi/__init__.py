"""
ST-Elevation Myocardial Infarction - ESC 2023 Guidelines.

Comprehensive STEMI management including:
- Initial assessment and reperfusion strategy
- Fibrinolysis vs primary PCI
- Antithrombotic therapy
- Post-PCI management
- Complications management
- Secondary prevention
"""

from .initial_management import (
    assess_reperfusion_strategy,
    get_fibrinolysis_eligibility,
    calculate_door_to_balloon_time,
)
from .antithrombotic import (
    get_antiplatelet_therapy,
    get_anticoagulation_therapy,
)
from .complications import (
    manage_cardiogenic_shock,
    manage_heart_failure,
    manage_arrhythmias,
)
from .secondary_prevention import (
    get_discharge_medical_therapy,
    get_cardiac_rehabilitation_plan,
)

# Guideline metadata
GUIDELINE_INFO = {
    "name": "2023 ESC Guidelines for the management of acute myocardial infarction in patients presenting with ST-segment elevation",
    "short_name": "ESC STEMI 2023",
    "year": 2023,
    "doi": "10.1093/eurheartj/ehad395",
    "pdf": "ehad395.pdf",
    "citation": "Ibanez B, et al. Eur Heart J. 2023;44(40):4093-4114.",
}

__all__ = [
    # Initial management
    "assess_reperfusion_strategy",
    "get_fibrinolysis_eligibility",
    "calculate_door_to_balloon_time",
    # Antithrombotic
    "get_antiplatelet_therapy",
    "get_anticoagulation_therapy",
    # Complications
    "manage_cardiogenic_shock",
    "manage_heart_failure",
    "manage_arrhythmias",
    # Secondary prevention
    "get_discharge_medical_therapy",
    "get_cardiac_rehabilitation_plan",
    # Metadata
    "GUIDELINE_INFO",
]