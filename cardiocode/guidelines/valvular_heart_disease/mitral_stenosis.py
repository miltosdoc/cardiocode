"""
Mitral Stenosis - ESC 2021 VHD Guidelines.

Implements:
- MS severity grading
- PMBV eligibility assessment
- Intervention indications
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


class MSSeverity(Enum):
    """Mitral stenosis severity classification."""
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"


@dataclass
class MSSeverityAssessment:
    """Mitral stenosis severity assessment result."""
    severity: MSSeverity
    mva: Optional[float] = None  # Mitral valve area (cm2)
    mean_gradient: Optional[float] = None  # mmHg
    pasp: Optional[float] = None  # Pulmonary artery systolic pressure (mmHg)
    classification: str = ""


@dataclass 
class WilkinsScore:
    """Wilkins echocardiographic score for PMBV eligibility."""
    leaflet_mobility: int  # 1-4
    leaflet_thickening: int  # 1-4
    subvalvular_thickening: int  # 1-4
    calcification: int  # 1-4
    total_score: int = 0
    pmbv_favorable: bool = True
    
    def __post_init__(self):
        self.total_score = (
            self.leaflet_mobility + 
            self.leaflet_thickening + 
            self.subvalvular_thickening + 
            self.calcification
        )
        self.pmbv_favorable = self.total_score <= 8


def assess_ms_severity(
    mva: Optional[float] = None,  # cm2
    mean_gradient: Optional[float] = None,  # mmHg
    pasp: Optional[float] = None,  # mmHg
) -> MSSeverityAssessment:
    """
    Assess mitral stenosis severity per ESC 2021 VHD Guidelines.
    
    SEVERE MS criteria (Table 8):
    - MVA <= 1.0 cm2 (very severe if < 1.0 cm2)
    - MVA 1.0-1.5 cm2 is moderate-severe
    - Mean gradient typically > 10-15 mmHg at rest (heart rate dependent)
    
    MODERATE MS:
    - MVA 1.5-2.0 cm2
    - Mean gradient 5-10 mmHg
    
    MILD MS:
    - MVA > 2.0 cm2
    - Mean gradient < 5 mmHg
    
    Args:
        mva: Mitral valve area (cm2)
        mean_gradient: Mean transmitral gradient (mmHg)
        pasp: Pulmonary artery systolic pressure (mmHg)
    
    Returns:
        MSSeverityAssessment with classification
    """
    if mva is not None:
        if mva <= 1.0:
            severity = MSSeverity.SEVERE
            classification = "very_severe_MS" if mva < 1.0 else "severe_MS"
        elif mva <= 1.5:
            severity = MSSeverity.MODERATE
            classification = "moderate_severe_MS"
        elif mva <= 2.0:
            severity = MSSeverity.MODERATE
            classification = "moderate_MS"
        else:
            severity = MSSeverity.MILD
            classification = "mild_MS"
    elif mean_gradient is not None:
        if mean_gradient >= 10:
            severity = MSSeverity.SEVERE
            classification = "severe_MS_by_gradient"
        elif mean_gradient >= 5:
            severity = MSSeverity.MODERATE
            classification = "moderate_MS_by_gradient"
        else:
            severity = MSSeverity.MILD
            classification = "mild_MS_by_gradient"
    else:
        severity = MSSeverity.MODERATE
        classification = "unable_to_assess"
    
    return MSSeverityAssessment(
        severity=severity,
        mva=mva,
        mean_gradient=mean_gradient,
        pasp=pasp,
        classification=classification,
    )


def calculate_wilkins_score(
    leaflet_mobility: int,
    leaflet_thickening: int,
    subvalvular_thickening: int,
    calcification: int,
) -> WilkinsScore:
    """
    Calculate Wilkins echocardiographic score for PMBV eligibility.
    
    Each component scored 1-4:
    
    Leaflet mobility:
    1 = Highly mobile valve with only leaflet tips restricted
    2 = Leaflet mid and base portions have normal mobility
    3 = Valve continues to move forward in diastole, mainly from the base
    4 = No or minimal forward movement of the leaflets in diastole
    
    Leaflet thickening:
    1 = Leaflets near normal thickness (4-5 mm)
    2 = Midleaflets normal, considerable thickening of margins (5-8 mm)
    3 = Thickening extending through the entire leaflet (5-8 mm)
    4 = Considerable thickening of all leaflet tissue (>8-10 mm)
    
    Subvalvular thickening:
    1 = Minimal thickening just below the mitral leaflets
    2 = Thickening of chordal structures extending up to one third of the chordal length
    3 = Thickening extending to the distal third of the chords
    4 = Extensive thickening and shortening of all chordal structures
    
    Calcification:
    1 = A single area of increased echo brightness
    2 = Scattered areas of brightness confined to leaflet margins
    3 = Brightness extending into the mid portions of the leaflets
    4 = Extensive brightness throughout much of the leaflet tissue
    
    Total score <= 8: FAVORABLE for PMBV
    Total score > 8: UNFAVORABLE for PMBV
    
    Args:
        leaflet_mobility: Score 1-4
        leaflet_thickening: Score 1-4
        subvalvular_thickening: Score 1-4
        calcification: Score 1-4
    
    Returns:
        WilkinsScore with total and PMBV eligibility
    """
    return WilkinsScore(
        leaflet_mobility=leaflet_mobility,
        leaflet_thickening=leaflet_thickening,
        subvalvular_thickening=subvalvular_thickening,
        calcification=calcification,
    )


def assess_pmbv_eligibility(
    patient: "Patient",
    wilkins_score: Optional[WilkinsScore] = None,
    has_la_thrombus: bool = False,
    has_more_than_mild_mr: bool = False,
) -> RecommendationSet:
    """
    Assess eligibility for percutaneous mitral balloon valvuloplasty (PMBV).
    
    PMBV is preferred over surgery for suitable patients per ESC 2021.
    
    FAVORABLE for PMBV:
    - Wilkins score <= 8
    - No LA thrombus
    - No more than mild MR
    - No commissural calcification
    
    CONTRAINDICATIONS:
    - LA thrombus
    - More than mild MR
    - Severe or bi-commissural calcification
    - Severe concomitant aortic valve disease
    - Severe CAD requiring CABG
    
    Args:
        patient: Patient with MS
        wilkins_score: Wilkins echocardiographic score
        has_la_thrombus: LA thrombus present
        has_more_than_mild_mr: More than mild MR present
    
    Returns:
        RecommendationSet with PMBV eligibility assessment
    """
    rec_set = RecommendationSet(
        title="PMBV Eligibility Assessment",
        primary_guideline="ESC VHD 2021",
    )
    
    # Absolute contraindications
    if has_la_thrombus:
        rec_set.add(guideline_recommendation(
            action="PMBV CONTRAINDICATED: LA thrombus present. Consider anticoagulation for 3-6 months then reassess with TEE.",
            guideline_key="esc_vhd_2021",
            evidence_class=EvidenceClass.III,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.CONTRAINDICATION,
            section="8.2",
        ))
        return rec_set
    
    if has_more_than_mild_mr:
        rec_set.add(guideline_recommendation(
            action="PMBV CONTRAINDICATED: More than mild MR present. Surgical valve replacement recommended.",
            guideline_key="esc_vhd_2021",
            evidence_class=EvidenceClass.III,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.CONTRAINDICATION,
            section="8.2",
        ))
        return rec_set
    
    # Assess Wilkins score
    if wilkins_score:
        if wilkins_score.pmbv_favorable:
            rec_set.add(guideline_recommendation(
                action=f"Wilkins score {wilkins_score.total_score}/16 - FAVORABLE for PMBV. PMBV recommended as first-line intervention.",
                guideline_key="esc_vhd_2021",
                evidence_class=EvidenceClass.I,
                evidence_level=EvidenceLevel.B,
                category=RecommendationCategory.PROCEDURE,
                section="8.2",
            ))
        else:
            rec_set.add(guideline_recommendation(
                action=f"Wilkins score {wilkins_score.total_score}/16 - UNFAVORABLE anatomy for PMBV. Consider surgical MVR or PMBV only if surgery contraindicated.",
                guideline_key="esc_vhd_2021",
                evidence_class=EvidenceClass.IIA,
                evidence_level=EvidenceLevel.C,
                category=RecommendationCategory.PROCEDURE,
                section="8.2",
            ))
    else:
        rec_set.add(guideline_recommendation(
            action="Perform detailed echo assessment including Wilkins score to determine PMBV suitability",
            guideline_key="esc_vhd_2021",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.DIAGNOSTIC,
            section="8.2",
        ))
    
    # TEE before PMBV
    rec_set.add(guideline_recommendation(
        action="TEE MANDATORY before PMBV to exclude LA thrombus",
        guideline_key="esc_vhd_2021",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.C,
        category=RecommendationCategory.DIAGNOSTIC,
        section="8.2",
    ))
    
    return rec_set


def get_ms_intervention_indication(patient: "Patient") -> RecommendationSet:
    """
    Get intervention recommendations for mitral stenosis.
    
    Per ESC 2021 VHD Guidelines Section 8
    
    Intervention indications:
    - Symptomatic severe MS (Class I)
    - Asymptomatic severe MS with high thromboembolic risk or hemodynamic decompensation (Class IIa)
    
    Args:
        patient: Patient with MS
    
    Returns:
        RecommendationSet with intervention recommendations
    """
    rec_set = RecommendationSet(
        title="Mitral Stenosis Intervention Recommendations",
        primary_guideline="ESC VHD 2021",
    )
    
    is_symptomatic = patient.nyha_class and patient.nyha_class.value >= 2
    has_pah = patient.echo and patient.echo.rvsp and patient.echo.rvsp > 50
    has_af = patient.has_diagnosis("atrial_fibrillation") or (patient.ecg and patient.ecg.af_present)
    
    # Anticoagulation for AF
    if has_af:
        rec_set.add(guideline_recommendation(
            action="Anticoagulation RECOMMENDED for MS with AF. VKA preferred (INR 2-3). DOACs can be considered if no LA thrombus and not severe MS.",
            guideline_key="esc_vhd_2021",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PHARMACOTHERAPY,
            section="8.1",
        ))
    
    # Symptomatic severe MS
    if is_symptomatic:
        rec_set.add(guideline_recommendation(
            action="Intervention RECOMMENDED for symptomatic severe MS (MVA <= 1.5 cm2)",
            guideline_key="esc_vhd_2021",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PROCEDURE,
            urgency=Urgency.SOON,
            section="8.2",
        ))
        
        rec_set.add(guideline_recommendation(
            action="PMBV is preferred over surgery if anatomy is favorable (Wilkins score <= 8, no LA thrombus, no more than mild MR)",
            guideline_key="esc_vhd_2021",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PROCEDURE,
            section="8.2",
        ))
    
    # Asymptomatic with high-risk features
    elif has_pah:
        rec_set.add(guideline_recommendation(
            action="Intervention SHOULD BE CONSIDERED for asymptomatic severe MS with PASP > 50 mmHg at rest",
            guideline_key="esc_vhd_2021",
            evidence_class=EvidenceClass.IIA,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.PROCEDURE,
            section="8.2",
        ))
    
    elif has_af:
        rec_set.add(guideline_recommendation(
            action="Intervention SHOULD BE CONSIDERED for asymptomatic severe MS with new-onset AF",
            guideline_key="esc_vhd_2021",
            evidence_class=EvidenceClass.IIA,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.PROCEDURE,
            section="8.2",
        ))
    
    else:
        rec_set.add(guideline_recommendation(
            action="Asymptomatic moderate-severe MS: Annual clinical and echo follow-up",
            guideline_key="esc_vhd_2021",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.MONITORING,
            section="8.2",
        ))
    
    return rec_set
