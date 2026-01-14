"""
Tricuspid Regurgitation - ESC 2021 VHD Guidelines.

Implements:
- TR severity grading
- Intervention indications
- Transcatheter TR treatment options
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


class TRSeverity(Enum):
    """Tricuspid regurgitation severity classification."""
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"
    MASSIVE = "massive"
    TORRENTIAL = "torrential"


class TREtiology(Enum):
    """Tricuspid regurgitation etiology."""
    PRIMARY = "primary"  # Intrinsic valve disease
    SECONDARY = "secondary"  # Functional (from RV/RA dilation, pulmonary hypertension, left heart disease)


@dataclass
class TRSeverityAssessment:
    """Tricuspid regurgitation severity assessment result."""
    severity: TRSeverity
    etiology: TREtiology
    vena_contracta: Optional[float] = None  # mm
    eroa: Optional[float] = None  # mm2
    regurgitant_volume: Optional[float] = None  # mL
    tricuspid_annulus_diameter: Optional[float] = None  # mm
    classification: str = ""


def assess_tr_severity(
    vena_contracta: Optional[float] = None,  # mm
    eroa: Optional[float] = None,  # mm2
    regurgitant_volume: Optional[float] = None,  # mL
    tricuspid_annulus_diameter: Optional[float] = None,  # mm (>40mm = dilated)
    rv_dilated: bool = False,
    has_left_heart_disease: bool = False,
    has_pulmonary_hypertension: bool = False,
) -> TRSeverityAssessment:
    """
    Assess tricuspid regurgitation severity per ESC 2021 VHD Guidelines.
    
    SEVERE TR criteria (Table 10):
    - Vena contracta >= 7 mm
    - EROA >= 40 mm2
    - Regurgitant volume >= 45 mL
    
    MASSIVE TR: vena contracta >= 14 mm, EROA >= 60 mm2
    TORRENTIAL TR: vena contracta >= 21 mm, EROA >= 80 mm2
    
    Etiology:
    - Primary: Intrinsic valve disease (endocarditis, carcinoid, rheumatic, leaflet prolapse, trauma)
    - Secondary: Most common - from RV/RA dilation, PH, left heart disease, AF with RA dilation
    
    Args:
        vena_contracta: Vena contracta width (mm)
        eroa: Effective regurgitant orifice area (mm2)
        regurgitant_volume: Regurgitant volume (mL)
        tricuspid_annulus_diameter: TV annulus diameter (mm)
        rv_dilated: Is RV dilated
        has_left_heart_disease: Left heart disease present
        has_pulmonary_hypertension: Pulmonary hypertension present
    
    Returns:
        TRSeverityAssessment with classification
    """
    # Determine etiology
    if has_left_heart_disease or has_pulmonary_hypertension or rv_dilated:
        etiology = TREtiology.SECONDARY
    else:
        etiology = TREtiology.PRIMARY
    
    # Determine severity (using expanded grading)
    if vena_contracta and vena_contracta >= 21:
        severity = TRSeverity.TORRENTIAL
    elif vena_contracta and vena_contracta >= 14:
        severity = TRSeverity.MASSIVE
    elif (vena_contracta and vena_contracta >= 7) or (eroa and eroa >= 40) or (regurgitant_volume and regurgitant_volume >= 45):
        severity = TRSeverity.SEVERE
    elif (vena_contracta and 4 <= vena_contracta < 7) or (eroa and 20 <= eroa < 40):
        severity = TRSeverity.MODERATE
    else:
        severity = TRSeverity.MILD
    
    classification = f"{etiology.value}_{severity.value}_TR"
    
    return TRSeverityAssessment(
        severity=severity,
        etiology=etiology,
        vena_contracta=vena_contracta,
        eroa=eroa,
        regurgitant_volume=regurgitant_volume,
        tricuspid_annulus_diameter=tricuspid_annulus_diameter,
        classification=classification,
    )


def get_tr_intervention_indication(patient: "Patient") -> RecommendationSet:
    """
    Get intervention recommendations for tricuspid regurgitation.
    
    Per ESC 2021 VHD Guidelines Section 9
    
    Key points:
    - Surgery during left-sided valve surgery if TR is severe or TV annulus dilated
    - Isolated TR surgery if symptomatic and not due to irreversible RV dysfunction
    - Transcatheter options emerging for high surgical risk patients
    
    Args:
        patient: Patient with TR
    
    Returns:
        RecommendationSet with intervention recommendations
    """
    rec_set = RecommendationSet(
        title="Tricuspid Regurgitation Intervention Recommendations",
        primary_guideline="ESC VHD 2021",
    )
    
    is_symptomatic = patient.nyha_class and patient.nyha_class.value >= 2
    
    # Concomitant with left-sided surgery
    rec_set.add(guideline_recommendation(
        action="TV surgery RECOMMENDED during left-sided valve surgery if TR is SEVERE",
        guideline_key="esc_vhd_2021",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.B,
        category=RecommendationCategory.PROCEDURE,
        section="9.2",
        rationale="TR often progresses after left-sided surgery; opportunity to address",
    ))
    
    rec_set.add(guideline_recommendation(
        action="TV surgery SHOULD BE CONSIDERED during left-sided valve surgery if TR is MODERATE with dilated annulus (>= 40mm or >= 21mm/m2)",
        guideline_key="esc_vhd_2021",
        evidence_class=EvidenceClass.IIA,
        evidence_level=EvidenceLevel.B,
        category=RecommendationCategory.PROCEDURE,
        section="9.2",
    ))
    
    # Isolated TR surgery
    if is_symptomatic:
        rec_set.add(guideline_recommendation(
            action="Isolated TV surgery SHOULD BE CONSIDERED for severe symptomatic PRIMARY TR without severe RV dysfunction",
            guideline_key="esc_vhd_2021",
            evidence_class=EvidenceClass.IIA,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.PROCEDURE,
            section="9.2",
        ))
        
        rec_set.add(guideline_recommendation(
            action="Isolated TV surgery SHOULD BE CONSIDERED for severe symptomatic SECONDARY TR with prior left-sided surgery, absence of left-sided dysfunction, severe PH, or severe RV dysfunction",
            guideline_key="esc_vhd_2021",
            evidence_class=EvidenceClass.IIA,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.PROCEDURE,
            section="9.2",
        ))
    
    # Transcatheter options
    rec_set.add(guideline_recommendation(
        action="Transcatheter TR intervention MAY BE CONSIDERED in symptomatic, inoperable, or high surgical risk patients at experienced centers",
        guideline_key="esc_vhd_2021",
        evidence_class=EvidenceClass.IIB,
        evidence_level=EvidenceLevel.C,
        category=RecommendationCategory.PROCEDURE,
        section="9.2",
        rationale="Edge-to-edge repair (TriClip) and annuloplasty devices emerging",
    ))
    
    # Repair vs replacement
    rec_set.add(guideline_recommendation(
        action="TV REPAIR preferred over replacement when feasible (especially annuloplasty for secondary TR)",
        guideline_key="esc_vhd_2021",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.C,
        category=RecommendationCategory.PROCEDURE,
        section="9.2",
    ))
    
    # Medical management
    rec_set.add(guideline_recommendation(
        action="Optimize medical therapy: Diuretics for RV volume overload, treat underlying cause (left heart disease, PH)",
        guideline_key="esc_vhd_2021",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.C,
        category=RecommendationCategory.PHARMACOTHERAPY,
        section="9.1",
    ))
    
    # AF management
    rec_set.add(guideline_recommendation(
        action="Consider AF ablation or surgical Maze if TR is secondary to AF with RA dilation",
        guideline_key="esc_vhd_2021",
        evidence_class=EvidenceClass.IIA,
        evidence_level=EvidenceLevel.C,
        category=RecommendationCategory.PROCEDURE,
        section="9.2",
    ))
    
    return rec_set
