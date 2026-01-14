"""
ESC 2020 Atrial Fibrillation Guidelines - Encoded as Executable Clinical Logic.

Source: 2020 ESC Guidelines for the diagnosis and management of atrial fibrillation
DOI: 10.1093/eurheartj/ehaa612
PDF: ehaa554.pdf

This module provides:
- Stroke risk assessment (CHA2DS2-VASc)
- Anticoagulation recommendations
- Rate vs rhythm control strategy
- Cardioversion guidance
- Ablation indications

The CC-to-ABC pathway:
- Confirm AF
- Characterize AF (4S: Stroke risk, Symptom severity, Severity of AF burden, Substrate severity)
- Treat AF (Anticoagulation, Better symptom control, Comorbidities/CV risk)
"""

from cardiocode.guidelines.atrial_fibrillation.stroke_prevention import (
    assess_stroke_risk,
    get_anticoagulation_recommendation,
    select_anticoagulant,
)

from cardiocode.guidelines.atrial_fibrillation.rate_control import (
    get_rate_control_strategy,
    get_rate_control_targets,
)

from cardiocode.guidelines.atrial_fibrillation.rhythm_control import (
    assess_rhythm_control_candidacy,
    get_rhythm_control_strategy,
    get_cardioversion_guidance,
)

from cardiocode.guidelines.atrial_fibrillation.ablation import (
    assess_ablation_indication,
    get_ablation_recommendation,
)

# Guideline metadata
GUIDELINE_INFO = {
    "name": "2020 ESC Guidelines for the diagnosis and management of atrial fibrillation",
    "short_name": "ESC AF 2020",
    "year": 2020,
    "doi": "10.1093/eurheartj/ehaa612",
    "pdf": "ehaa554.pdf",
    "citation": "Hindricks G, et al. Eur Heart J. 2021;42(5):373-498.",
}

__all__ = [
    "assess_stroke_risk",
    "get_anticoagulation_recommendation",
    "select_anticoagulant",
    "get_rate_control_strategy",
    "get_rate_control_targets",
    "assess_rhythm_control_candidacy",
    "get_rhythm_control_strategy",
    "get_cardioversion_guidance",
    "assess_ablation_indication",
    "get_ablation_recommendation",
    "GUIDELINE_INFO",
]
