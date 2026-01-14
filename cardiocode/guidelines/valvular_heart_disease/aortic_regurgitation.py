"""
Aortic Regurgitation - ESC 2021 VHD Guidelines.

Implements:
- AR severity grading
- Intervention timing
"""

from __future__ import annotations
from typing import Optional, List, TYPE_CHECKING
from dataclasses import dataclass
from enum import Enum

if TYPE_CHECKING:
    from cardiocode.core.types import Patient

from cardiocode.core.recommendation import (
    RecommendationSet,
    RecommendationCategory,
    Urgency,
    guideline_recommendation,
)
from cardiocode.core.evidence import EvidenceClass, EvidenceLevel


class ARSeverity(Enum):
    """Aortic regurgitation severity classification."""
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"


@dataclass
class ARSeverityAssessment:
    """Aortic regurgitation severity assessment result."""
    severity: ARSeverity
    vena_contracta: Optional[float] = None  # mm
    regurgitant_volume: Optional[float] = None  # mL
    regurgitant_fraction: Optional[float] = None  # %
    eroa: Optional[float] = None  # mm2
    pressure_half_time: Optional[float] = None  # ms
    classification: str = ""


def assess_ar_severity(
    vena_contracta: Optional[float] = None,  # mm
    regurgitant_volume: Optional[float] = None,  # mL
    regurgitant_fraction: Optional[float] = None,  # %
    eroa: Optional[float] = None,  # mm2
    pressure_half_time: Optional[float] = None,  # ms
    holodiastolic_flow_reversal: bool = False,
) -> ARSeverityAssessment:
    """
    Assess aortic regurgitation severity per ESC 2021 VHD Guidelines.
    
    SEVERE AR criteria (Table 6):
    - Vena contracta >= 6 mm
    - Regurgitant volume >= 60 mL
    - Regurgitant fraction >= 50%
    - EROA >= 30 mm2
    - Pressure half-time < 200 ms (acute severe)
    - Holodiastolic flow reversal in descending aorta
    
    Args:
        vena_contracta: Vena contracta width (mm)
        regurgitant_volume: Regurgitant volume per beat (mL)
        regurgitant_fraction: Regurgitant fraction (%)
        eroa: Effective regurgitant orifice area (mm2)
        pressure_half_time: Pressure half-time (ms)
        holodiastolic_flow_reversal: Holodiastolic flow reversal in descending aorta
    
    Returns:
        ARSeverityAssessment with classification
    """
    severe_criteria = 0
    
    if vena_contracta and vena_contracta >= 6:
        severe_criteria += 1
    if regurgitant_volume and regurgitant_volume >= 60:
        severe_criteria += 1
    if regurgitant_fraction and regurgitant_fraction >= 50:
        severe_criteria += 1
    if eroa and eroa >= 30:
        severe_criteria += 1
    if holodiastolic_flow_reversal:
        severe_criteria += 1
    
    # Acute severe AR
    is_acute = pressure_half_time and pressure_half_time < 200
    
    if severe_criteria >= 2 or is_acute:
        severity = ARSeverity.SEVERE
        classification = "acute_severe_AR" if is_acute else "chronic_severe_AR"
    elif severe_criteria == 1 or (vena_contracta and 3 <= vena_contracta < 6):
        severity = ARSeverity.MODERATE
        classification = "moderate_AR"
    else:
        severity = ARSeverity.MILD
        classification = "mild_AR"
    
    return ARSeverityAssessment(
        severity=severity,
        vena_contracta=vena_contracta,
        regurgitant_volume=regurgitant_volume,
        regurgitant_fraction=regurgitant_fraction,
        eroa=eroa,
        pressure_half_time=pressure_half_time,
        classification=classification,
    )


def get_ar_intervention_indication(patient: "Patient") -> RecommendationSet:
    """
    Get intervention recommendations for aortic regurgitation.
    
    Per ESC 2021 VHD Guidelines Section 6
    
    Intervention indications (Class I):
    - Symptomatic severe AR
    - Asymptomatic severe AR with LVEF <= 50%
    - Asymptomatic severe AR undergoing CABG or other cardiac surgery
    - Asymptomatic severe AR with LVESD > 50mm or LVESD > 25mm/m2 BSA
    
    Args:
        patient: Patient with AR
    
    Returns:
        RecommendationSet with intervention recommendations
    """
    rec_set = RecommendationSet(
        title="Aortic Regurgitation Intervention Recommendations",
        primary_guideline="ESC VHD 2021",
    )
    
    is_symptomatic = patient.nyha_class and patient.nyha_class.value >= 2
    lvef = patient.echo.lvef if patient.echo else None
    lvesd = patient.echo.lvids if patient.echo else None  # LV end-systolic dimension
    lvedd = patient.echo.lvidd if patient.echo else None  # LV end-diastolic dimension
    
    # Symptomatic severe AR
    if is_symptomatic:
        rec_set.add(guideline_recommendation(
            action="Aortic valve surgery RECOMMENDED for symptomatic severe AR",
            guideline_key="esc_vhd_2021",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PROCEDURE,
            urgency=Urgency.SOON,
            section="6.2",
        ))
    
    # Asymptomatic with LV dysfunction
    elif lvef and lvef <= 50:
        rec_set.add(guideline_recommendation(
            action="Aortic valve surgery RECOMMENDED for asymptomatic severe AR with resting LVEF <= 50%",
            guideline_key="esc_vhd_2021",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PROCEDURE,
            section="6.2",
        ))
    
    # Asymptomatic with LV dilation
    elif lvesd and lvesd > 50:
        rec_set.add(guideline_recommendation(
            action="Aortic valve surgery RECOMMENDED for asymptomatic severe AR with LVESD > 50mm (or > 25mm/m2 BSA)",
            guideline_key="esc_vhd_2021",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PROCEDURE,
            section="6.2",
        ))
    
    elif lvedd and lvedd > 65:
        rec_set.add(guideline_recommendation(
            action="Aortic valve surgery SHOULD BE CONSIDERED for asymptomatic severe AR with LVEDD > 65mm if low surgical risk",
            guideline_key="esc_vhd_2021",
            evidence_class=EvidenceClass.IIA,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PROCEDURE,
            section="6.2",
        ))
    
    else:
        rec_set.add(guideline_recommendation(
            action="Asymptomatic severe AR with preserved LV function: Close follow-up every 6-12 months",
            guideline_key="esc_vhd_2021",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.MONITORING,
            section="6.2",
        ))
    
    # Aortic root considerations
    rec_set.add(guideline_recommendation(
        action="Assess aortic root and ascending aorta dimensions. Surgery indicated if aortic root > 55mm (or > 50mm with risk factors/bicuspid valve, > 45mm with Marfan/TGFBR mutations)",
        guideline_key="esc_vhd_2021",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.B,
        category=RecommendationCategory.DIAGNOSTIC,
        section="6.2",
    ))
    
    # Valve repair vs replacement
    rec_set.add(guideline_recommendation(
        action="Aortic valve repair SHOULD BE CONSIDERED in experienced centers for suitable anatomy (tricuspid valve with cusp prolapse/perforation)",
        guideline_key="esc_vhd_2021",
        evidence_class=EvidenceClass.IIA,
        evidence_level=EvidenceLevel.B,
        category=RecommendationCategory.PROCEDURE,
        section="6.2",
    ))
    
    return rec_set
