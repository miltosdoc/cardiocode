"""
ESC 2021 Valvular Heart Disease Guidelines - Encoded as Executable Clinical Logic.

Source: 2021 ESC/EACTS Guidelines for the management of valvular heart disease
DOI: 10.1093/eurheartj/ehab395
PDF: ehab484.pdf

This module provides:
- Valve disease severity assessment
- Intervention timing recommendations
- Choice of intervention (surgical vs transcatheter)
- Antithrombotic management for prosthetic valves
- Follow-up scheduling
"""

from cardiocode.guidelines.valvular_heart_disease.aortic_stenosis import (
    assess_aortic_stenosis_severity,
    get_aortic_stenosis_intervention,
    choose_as_intervention_type,
)

from cardiocode.guidelines.valvular_heart_disease.mitral_regurgitation import (
    assess_mitral_regurgitation_severity,
    classify_mr_etiology,
    get_mitral_regurgitation_intervention,
)

from cardiocode.guidelines.valvular_heart_disease.prosthetic_valves import (
    get_prosthetic_valve_anticoagulation,
    manage_prosthetic_valve_thrombosis,
)

from cardiocode.guidelines.valvular_heart_disease.general import (
    get_endocarditis_prophylaxis,
    get_vhd_followup_schedule,
    assess_surgical_risk,
)

# Guideline metadata
GUIDELINE_INFO = {
    "name": "2021 ESC/EACTS Guidelines for the management of valvular heart disease",
    "short_name": "ESC VHD 2021",
    "year": 2021,
    "doi": "10.1093/eurheartj/ehab395",
    "pdf": "ehab484.pdf",
    "citation": "Vahanian A, et al. Eur Heart J. 2022;43(7):561-632.",
}

__all__ = [
    "assess_aortic_stenosis_severity",
    "get_aortic_stenosis_intervention",
    "choose_as_intervention_type",
    "assess_mitral_regurgitation_severity",
    "classify_mr_etiology",
    "get_mitral_regurgitation_intervention",
    "get_prosthetic_valve_anticoagulation",
    "manage_prosthetic_valve_thrombosis",
    "get_endocarditis_prophylaxis",
    "get_vhd_followup_schedule",
    "assess_surgical_risk",
    "GUIDELINE_INFO",
]
