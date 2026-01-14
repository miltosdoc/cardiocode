"""
Mitral Regurgitation - ESC 2021 VHD Guidelines.

Implements:
- MR severity grading
- Primary vs Secondary MR classification
- Intervention indications
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


class MRSeverity(Enum):
    """Mitral regurgitation severity."""
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"


class MREtiology(Enum):
    """Mitral regurgitation etiology classification."""
    PRIMARY = "primary"      # Degenerative, endocarditis, etc. - valve pathology
    SECONDARY = "secondary"  # Functional - LV pathology causing MR


@dataclass
class MRAssessment:
    """Mitral regurgitation assessment result."""
    severity: MRSeverity
    etiology: MREtiology
    eroa: Optional[float] = None  # Effective regurgitant orifice area (mm2)
    regurgitant_volume: Optional[float] = None  # mL
    vena_contracta: Optional[float] = None  # mm
    recommendations: List[Recommendation] = None
    
    def __post_init__(self):
        if self.recommendations is None:
            self.recommendations = []


def classify_mr_etiology(patient: "Patient") -> MREtiology:
    """
    Classify MR as primary (degenerative) or secondary (functional).
    
    Primary MR: Intrinsic valve disease (prolapse, flail, rheumatic, endocarditis)
    Secondary MR: LV dilation/dysfunction causing functional MR
    
    Args:
        patient: Patient with MR
    
    Returns:
        MREtiology classification
    """
    # If significant LV dysfunction or dilation with no mention of valve pathology
    if patient.echo:
        if patient.echo.lvef and patient.echo.lvef < 50:
            # Likely secondary if LV is dysfunctional
            return MREtiology.SECONDARY
        if patient.echo.lvidd and patient.echo.lvidd > 60:
            # Dilated LV suggests secondary
            return MREtiology.SECONDARY
    
    # Check for diagnoses suggesting primary
    if patient.has_diagnosis("mitral_prolapse") or patient.has_diagnosis("endocarditis"):
        return MREtiology.PRIMARY
    
    # Default to primary if no clear secondary cause
    return MREtiology.PRIMARY


def assess_mitral_regurgitation_severity(
    eroa: Optional[float] = None,  # mm2
    regurgitant_volume: Optional[float] = None,  # mL
    vena_contracta: Optional[float] = None,  # mm
    etiology: MREtiology = MREtiology.PRIMARY,
) -> MRAssessment:
    """
    Assess MR severity per ESC 2021 VHD Guidelines.
    
    PRIMARY MR severe criteria:
    - EROA >= 40 mm2
    - Regurgitant volume >= 60 mL
    - Vena contracta >= 7 mm
    
    SECONDARY MR severe criteria (lower thresholds):
    - EROA >= 20 mm2
    - Regurgitant volume >= 30 mL
    - Vena contracta >= 7 mm
    
    Args:
        eroa: Effective regurgitant orifice area (mm2)
        regurgitant_volume: Regurgitant volume per beat (mL)
        vena_contracta: Vena contracta width (mm)
        etiology: Primary or secondary MR
    
    Returns:
        MRAssessment with severity classification
    """
    # Thresholds differ by etiology
    if etiology == MREtiology.PRIMARY:
        eroa_severe = 40
        rv_severe = 60
    else:
        eroa_severe = 20
        rv_severe = 30
    
    vc_severe = 7  # Same for both
    
    # Determine severity
    severe_criteria_met = 0
    if eroa and eroa >= eroa_severe:
        severe_criteria_met += 1
    if regurgitant_volume and regurgitant_volume >= rv_severe:
        severe_criteria_met += 1
    if vena_contracta and vena_contracta >= vc_severe:
        severe_criteria_met += 1
    
    if severe_criteria_met >= 2:
        severity = MRSeverity.SEVERE
    elif severe_criteria_met == 1:
        severity = MRSeverity.MODERATE  # Borderline
    elif eroa and eroa >= eroa_severe * 0.5:
        severity = MRSeverity.MODERATE
    else:
        severity = MRSeverity.MILD
    
    return MRAssessment(
        severity=severity,
        etiology=etiology,
        eroa=eroa,
        regurgitant_volume=regurgitant_volume,
        vena_contracta=vena_contracta,
    )


def get_mitral_regurgitation_intervention(patient: "Patient") -> RecommendationSet:
    """
    Get intervention recommendations for mitral regurgitation.
    
    Per ESC 2021 VHD Guidelines Section 7
    
    Key decision points:
    1. Primary vs Secondary MR
    2. Severity assessment
    3. Symptoms
    4. LV function/dimensions
    5. AF presence
    6. Pulmonary pressures
    
    Args:
        patient: Patient with MR
    
    Returns:
        RecommendationSet with intervention recommendations
    """
    rec_set = RecommendationSet(
        title="Mitral Regurgitation Intervention Recommendations",
        primary_guideline="ESC VHD 2021",
    )
    
    # Classify etiology
    etiology = classify_mr_etiology(patient)
    
    if etiology == MREtiology.PRIMARY:
        rec_set.description = "Primary (Degenerative) Mitral Regurgitation"
        return _get_primary_mr_recommendations(patient, rec_set)
    else:
        rec_set.description = "Secondary (Functional) Mitral Regurgitation"
        return _get_secondary_mr_recommendations(patient, rec_set)


def _get_primary_mr_recommendations(patient: "Patient", rec_set: RecommendationSet) -> RecommendationSet:
    """Recommendations for primary MR."""
    
    is_symptomatic = patient.nyha_class and patient.nyha_class.value >= 2
    lvef = patient.echo.lvef if patient.echo else None
    lv_dilated = patient.echo and patient.echo.lvids and patient.echo.lvids >= 40
    has_af = patient.af_type or (patient.ecg and patient.ecg.af_present)
    has_pah = patient.echo and patient.echo.rvsp and patient.echo.rvsp > 50
    
    # Symptomatic severe primary MR
    if is_symptomatic:
        rec_set.add(guideline_recommendation(
            action="Mitral valve surgery RECOMMENDED for symptomatic severe primary MR",
            guideline_key="esc_vhd_2021",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PROCEDURE,
            urgency=Urgency.SOON,
            section="7.1",
            rationale="Repair preferred over replacement when feasible",
        ))
        
        rec_set.add(guideline_recommendation(
            action="Mitral valve REPAIR preferred over replacement in primary MR when durable repair is feasible",
            guideline_key="esc_vhd_2021",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PROCEDURE,
            section="7.1",
        ))
    
    # Asymptomatic with LV dysfunction
    elif lvef and lvef < 60:
        rec_set.add(guideline_recommendation(
            action="Mitral valve surgery RECOMMENDED for asymptomatic severe primary MR with LV dysfunction (LVEF <= 60%)",
            guideline_key="esc_vhd_2021",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PROCEDURE,
            section="7.1",
        ))
    
    # Asymptomatic with LV dilation
    elif lv_dilated:
        rec_set.add(guideline_recommendation(
            action="Mitral valve surgery RECOMMENDED for asymptomatic severe primary MR with LV dilation (LVESD >= 40mm)",
            guideline_key="esc_vhd_2021",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PROCEDURE,
            section="7.1",
        ))
    
    # Asymptomatic with AF or pulmonary hypertension
    elif has_af or has_pah:
        rec_set.add(guideline_recommendation(
            action="Mitral valve surgery SHOULD BE CONSIDERED for asymptomatic severe primary MR with new-onset AF or pulmonary hypertension (PASP > 50 mmHg)",
            guideline_key="esc_vhd_2021",
            evidence_class=EvidenceClass.IIA,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PROCEDURE,
            section="7.1",
        ))
    
    # Otherwise watchful waiting
    else:
        rec_set.add(guideline_recommendation(
            action="Asymptomatic severe primary MR with preserved LV function: Close follow-up every 6 months. Surgery if triggers develop.",
            guideline_key="esc_vhd_2021",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.MONITORING,
            section="7.1",
        ))
    
    return rec_set


def _get_secondary_mr_recommendations(patient: "Patient", rec_set: RecommendationSet) -> RecommendationSet:
    """Recommendations for secondary (functional) MR."""
    
    # GDMT is primary treatment
    rec_set.add(guideline_recommendation(
        action="Optimize guideline-directed medical therapy (GDMT) for HF as primary treatment for secondary MR",
        guideline_key="esc_vhd_2021",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.B,
        category=RecommendationCategory.PHARMACOTHERAPY,
        section="7.2",
        rationale="Medical therapy and CRT can reduce secondary MR",
    ))
    
    # CRT if eligible
    if patient.ecg and patient.ecg.qrs_duration and patient.ecg.qrs_duration >= 130:
        if patient.ecg.lbbb:
            rec_set.add(guideline_recommendation(
                action="Consider CRT if eligible - may reduce secondary MR",
                guideline_key="esc_vhd_2021",
                evidence_class=EvidenceClass.I,
                evidence_level=EvidenceLevel.A,
                category=RecommendationCategory.DEVICE,
                section="7.2",
            ))
    
    # Surgery if undergoing CABG/other cardiac surgery
    rec_set.add(guideline_recommendation(
        action="Mitral valve surgery SHOULD BE CONSIDERED in severe secondary MR undergoing CABG or other cardiac surgery",
        guideline_key="esc_vhd_2021",
        evidence_class=EvidenceClass.IIA,
        evidence_level=EvidenceLevel.B,
        category=RecommendationCategory.PROCEDURE,
        section="7.2",
    ))
    
    # TEER (MitraClip) for selected patients
    lvef = patient.echo.lvef if patient.echo else None
    
    if lvef and 20 <= lvef <= 50:
        rec_set.add(guideline_recommendation(
            action="Transcatheter edge-to-edge repair (TEER/MitraClip) SHOULD BE CONSIDERED for severe secondary MR remaining symptomatic despite optimal medical therapy and CRT if eligible, with LVEF 20-50%, and suitable anatomy",
            guideline_key="esc_vhd_2021",
            evidence_class=EvidenceClass.IIA,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PROCEDURE,
            section="7.2",
            studies=["COAPT", "MITRA-FR (different population)"],
            rationale="COAPT criteria: EROA >=30mm2, LVEDV <96mL/m2, on optimal GDMT",
        ))
    
    return rec_set
