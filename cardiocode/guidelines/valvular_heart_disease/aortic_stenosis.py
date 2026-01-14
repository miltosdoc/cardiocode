"""
Aortic Stenosis - ESC 2021 VHD Guidelines.

Implements:
- AS severity grading
- Intervention timing
- TAVI vs SAVR decision algorithm
"""

from __future__ import annotations
from typing import Optional, List, TYPE_CHECKING
from dataclasses import dataclass
from enum import Enum

if TYPE_CHECKING:
    from cardiocode.core.types import Patient

from cardiocode.core.recommendation import (
    Recommendation,
    RecommendationSet,
    RecommendationCategory,
    Urgency,
    guideline_recommendation,
)
from cardiocode.core.evidence import EvidenceClass, EvidenceLevel


class ASSeverity(Enum):
    """Aortic stenosis severity classification."""
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"
    VERY_SEVERE = "very_severe"


@dataclass
class ASSeverityAssessment:
    """Aortic stenosis severity assessment result."""
    severity: ASSeverity
    peak_velocity: Optional[float] = None
    mean_gradient: Optional[float] = None
    ava: Optional[float] = None  # Aortic valve area
    ava_indexed: Optional[float] = None
    flow_status: Optional[str] = None  # "normal_flow", "low_flow"
    gradient_status: Optional[str] = None  # "high_gradient", "low_gradient"
    classification: str = ""  # "high_gradient", "low_flow_low_gradient_reduced_ef", etc.
    recommendations: List[Recommendation] = None
    
    def __post_init__(self):
        if self.recommendations is None:
            self.recommendations = []


def assess_aortic_stenosis_severity(
    peak_velocity: Optional[float] = None,  # m/s
    mean_gradient: Optional[float] = None,  # mmHg
    ava: Optional[float] = None,  # cm2
    ava_indexed: Optional[float] = None,  # cm2/m2
    stroke_volume_index: Optional[float] = None,  # mL/m2
    lvef: Optional[float] = None,  # %
) -> ASSeverityAssessment:
    """
    Assess aortic stenosis severity per ESC 2021 VHD Guidelines.
    
    Per Table 5: Echocardiographic criteria for AS severity
    
    SEVERE AS criteria:
    - Peak velocity > 4.0 m/s
    - Mean gradient > 40 mmHg
    - AVA < 1.0 cm2
    - AVAi < 0.6 cm2/m2
    
    Special categories:
    - Low-flow, low-gradient with reduced EF
    - Low-flow, low-gradient with preserved EF (paradoxical)
    - Normal-flow, low-gradient
    
    Args:
        peak_velocity: Peak aortic jet velocity (m/s)
        mean_gradient: Mean transvalvular gradient (mmHg)
        ava: Aortic valve area (cm2)
        ava_indexed: Indexed AVA (cm2/m2)
        stroke_volume_index: Stroke volume index (mL/m2)
        lvef: Left ventricular ejection fraction (%)
    
    Returns:
        ASSeverityAssessment with classification
    """
    recommendations = []
    
    # Determine flow status
    low_flow = stroke_volume_index is not None and stroke_volume_index < 35
    flow_status = "low_flow" if low_flow else "normal_flow"
    
    # Determine gradient status
    high_gradient = (peak_velocity and peak_velocity >= 4.0) or (mean_gradient and mean_gradient >= 40)
    gradient_status = "high_gradient" if high_gradient else "low_gradient"
    
    # Determine severity
    if peak_velocity and peak_velocity >= 4.0:
        severity = ASSeverity.SEVERE
        if peak_velocity >= 5.0:
            severity = ASSeverity.VERY_SEVERE
    elif mean_gradient and mean_gradient >= 40:
        severity = ASSeverity.SEVERE
    elif ava and ava < 1.0:
        severity = ASSeverity.SEVERE
    elif ava and ava < 1.5:
        severity = ASSeverity.MODERATE
    elif peak_velocity and peak_velocity >= 3.0:
        severity = ASSeverity.MODERATE
    else:
        severity = ASSeverity.MILD
    
    # Classify special scenarios for severe AS
    if severity in [ASSeverity.SEVERE, ASSeverity.VERY_SEVERE]:
        if high_gradient:
            classification = "high_gradient_severe_AS"
        elif low_flow and lvef and lvef < 50:
            classification = "low_flow_low_gradient_reduced_EF"
            recommendations.append(guideline_recommendation(
                action="Low-flow, low-gradient AS with reduced EF: Consider dobutamine stress echo to assess flow reserve and confirm severity",
                guideline_key="esc_vhd_2021",
                evidence_class=EvidenceClass.I,
                evidence_level=EvidenceLevel.B,
                category=RecommendationCategory.DIAGNOSTIC,
                section="5.1",
            ))
        elif low_flow and (lvef is None or lvef >= 50):
            classification = "paradoxical_low_flow_low_gradient"
            recommendations.append(guideline_recommendation(
                action="Paradoxical low-flow, low-gradient AS: Confirm with CT calcium scoring (Agatston >= 2000 men, >= 1200 women suggests severe AS)",
                guideline_key="esc_vhd_2021",
                evidence_class=EvidenceClass.IIA,
                evidence_level=EvidenceLevel.B,
                category=RecommendationCategory.DIAGNOSTIC,
                section="5.1",
            ))
        else:
            classification = "normal_flow_low_gradient"
            recommendations.append(guideline_recommendation(
                action="Normal-flow, low-gradient with small AVA: Likely moderate AS. Reassess measurements.",
                guideline_key="esc_vhd_2021",
                evidence_class=EvidenceClass.IIA,
                evidence_level=EvidenceLevel.C,
                category=RecommendationCategory.DIAGNOSTIC,
                section="5.1",
            ))
    else:
        classification = f"{severity.value}_AS"
    
    return ASSeverityAssessment(
        severity=severity,
        peak_velocity=peak_velocity,
        mean_gradient=mean_gradient,
        ava=ava,
        ava_indexed=ava_indexed,
        flow_status=flow_status,
        gradient_status=gradient_status,
        classification=classification,
        recommendations=recommendations,
    )


def get_aortic_stenosis_intervention(patient: "Patient") -> RecommendationSet:
    """
    Get intervention recommendations for aortic stenosis.
    
    Per ESC 2021 VHD Guidelines Section 5.2
    
    Intervention indications (Class I):
    - Symptomatic severe AS
    - Asymptomatic severe AS with LVEF < 50%
    - Asymptomatic severe AS undergoing other cardiac surgery
    
    Args:
        patient: Patient with AS
    
    Returns:
        RecommendationSet with intervention recommendations
    """
    rec_set = RecommendationSet(
        title="Aortic Stenosis Intervention Recommendations",
        primary_guideline="ESC VHD 2021",
    )
    
    # Get AS severity from echo
    if not patient.echo:
        rec_set.add(guideline_recommendation(
            action="Obtain echocardiography to assess AS severity before intervention planning",
            guideline_key="esc_vhd_2021",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.DIAGNOSTIC,
            section="5.1",
        ))
        return rec_set
    
    # Assess severity
    severity_assessment = assess_aortic_stenosis_severity(
        peak_velocity=patient.echo.aortic_peak_velocity,
        mean_gradient=patient.echo.aortic_mean_gradient,
        ava=patient.echo.aortic_valve_area,
        lvef=patient.echo.lvef,
    )
    
    is_severe = severity_assessment.severity in [ASSeverity.SEVERE, ASSeverity.VERY_SEVERE]
    is_symptomatic = patient.nyha_class and patient.nyha_class.value >= 2
    
    if not is_severe:
        rec_set.add(guideline_recommendation(
            action=f"AS is {severity_assessment.severity.value}. No intervention indicated. Regular follow-up.",
            guideline_key="esc_vhd_2021",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.MONITORING,
            section="5.2",
        ))
        return rec_set
    
    # Severe AS - check for intervention indications
    if is_symptomatic:
        rec_set.add(guideline_recommendation(
            action="Aortic valve intervention RECOMMENDED for symptomatic severe AS",
            guideline_key="esc_vhd_2021",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PROCEDURE,
            urgency=Urgency.SOON,
            section="5.2",
            studies=["PARTNER trials", "CoreValve US Pivotal", "SURTAVI"],
            rationale="Symptomatic severe AS has poor prognosis without intervention",
        ))
    
    elif patient.echo.lvef and patient.echo.lvef < 50:
        rec_set.add(guideline_recommendation(
            action="Aortic valve intervention RECOMMENDED for asymptomatic severe AS with LVEF < 50%",
            guideline_key="esc_vhd_2021",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PROCEDURE,
            section="5.2",
            rationale="LV dysfunction indicates subclinical decompensation",
        ))
    
    elif severity_assessment.severity == ASSeverity.VERY_SEVERE:
        rec_set.add(guideline_recommendation(
            action="Aortic valve intervention SHOULD BE CONSIDERED for asymptomatic very severe AS (Vmax > 5 m/s) if low surgical risk",
            guideline_key="esc_vhd_2021",
            evidence_class=EvidenceClass.IIA,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PROCEDURE,
            section="5.2",
        ))
    
    else:
        rec_set.add(guideline_recommendation(
            action="Asymptomatic severe AS: Close follow-up with exercise testing to unmask symptoms. Intervention may be considered if high-risk features.",
            guideline_key="esc_vhd_2021",
            evidence_class=EvidenceClass.IIA,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.MONITORING,
            section="5.2",
        ))
    
    # Add intervention type recommendation
    type_recs = choose_as_intervention_type(patient)
    rec_set.add_all(type_recs.recommendations)
    
    return rec_set


def choose_as_intervention_type(patient: "Patient") -> RecommendationSet:
    """
    Choose between TAVI and SAVR for aortic stenosis.
    
    Per ESC 2021: Heart Team decision based on:
    - Age
    - Surgical risk (STS/EuroSCORE II)
    - Anatomy (suitability for TAVI)
    - Comorbidities
    - Life expectancy
    
    Args:
        patient: Patient with severe AS needing intervention
    
    Returns:
        RecommendationSet with TAVI vs SAVR recommendation
    """
    rec_set = RecommendationSet(
        title="TAVI vs SAVR Decision",
        primary_guideline="ESC VHD 2021",
    )
    
    # Heart Team assessment is mandatory
    rec_set.add(guideline_recommendation(
        action="Heart Team discussion RECOMMENDED for choice of intervention (TAVI vs SAVR)",
        guideline_key="esc_vhd_2021",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.C,
        category=RecommendationCategory.REFERRAL,
        section="5.2",
    ))
    
    # Age-based recommendations
    age = patient.age or 75
    
    if age < 75:
        rec_set.add(guideline_recommendation(
            action="Age < 75: SAVR preferred in low surgical risk patients. TAVI if high surgical risk or unsuitable for surgery.",
            guideline_key="esc_vhd_2021",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.A,
            category=RecommendationCategory.PROCEDURE,
            section="5.2",
            studies=["PARTNER 3", "Evolut Low Risk"],
            rationale="SAVR has better long-term durability data in younger patients",
        ))
    
    elif age >= 75:
        rec_set.add(guideline_recommendation(
            action="Age >= 75: TAVI recommended over SAVR in patients suitable for transfemoral access",
            guideline_key="esc_vhd_2021",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.A,
            category=RecommendationCategory.PROCEDURE,
            section="5.2",
            studies=["PARTNER 2A", "SURTAVI", "UK TAVI"],
        ))
    
    # Surgical risk considerations
    rec_set.add(guideline_recommendation(
        action="Calculate STS score or EuroSCORE II for surgical risk assessment",
        guideline_key="esc_vhd_2021",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.B,
        category=RecommendationCategory.DIAGNOSTIC,
        section="5.2",
    ))
    
    # TAVI contraindications to mention
    rec_set.add(guideline_recommendation(
        action="TAVI contraindicated if: inadequate vascular access, severe annular calcification precluding implantation, active endocarditis, LV thrombus",
        guideline_key="esc_vhd_2021",
        evidence_class=EvidenceClass.III,
        evidence_level=EvidenceLevel.C,
        category=RecommendationCategory.CONTRAINDICATION,
        section="5.2",
    ))
    
    # Bicuspid valve
    rec_set.add(guideline_recommendation(
        action="Bicuspid aortic valve: SAVR generally preferred. TAVI can be considered in selected patients at experienced centers.",
        guideline_key="esc_vhd_2021",
        evidence_class=EvidenceClass.IIA,
        evidence_level=EvidenceLevel.B,
        category=RecommendationCategory.PROCEDURE,
        section="5.2",
    ))
    
    return rec_set
