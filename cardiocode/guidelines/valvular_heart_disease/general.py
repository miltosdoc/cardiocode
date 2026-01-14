"""
General VHD Management - ESC 2021 VHD Guidelines.

Implements:
- Endocarditis prophylaxis
- Follow-up scheduling
- Surgical risk assessment
"""

from __future__ import annotations
from typing import Optional, List, TYPE_CHECKING

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
from cardiocode.knowledge.scores import euro_score_ii


def get_endocarditis_prophylaxis(
    patient: "Patient",
    procedure_type: str,  # "dental", "respiratory", "gi", "gu", "skin"
) -> RecommendationSet:
    """
    Endocarditis prophylaxis recommendations.
    
    Per ESC 2021 VHD Guidelines Section 12
    
    HIGH-RISK patients for IE prophylaxis:
    - Prosthetic valve or prosthetic material
    - Previous infective endocarditis
    - Congenital heart disease (specific types)
    
    Args:
        patient: Patient to assess
        procedure_type: Type of procedure being performed
    
    Returns:
        RecommendationSet with prophylaxis recommendations
    """
    rec_set = RecommendationSet(
        title="Infective Endocarditis Prophylaxis",
        primary_guideline="ESC VHD 2021",
    )
    
    # Determine if high-risk
    has_prosthetic_valve = (
        patient.has_diagnosis("prosthetic_valve") or
        patient.has_diagnosis("mechanical_valve") or
        patient.has_diagnosis("bioprosthetic_valve") or
        any(d.device_type in ["prosthetic_valve"] for d in patient.devices) if patient.devices else False
    )
    
    has_prior_ie = patient.has_diagnosis("endocarditis") or patient.has_diagnosis("infective_endocarditis")
    
    has_high_risk_chd = (
        patient.has_diagnosis("cyanotic_chd") or
        patient.has_diagnosis("unrepaired_chd")
    )
    
    is_high_risk = has_prosthetic_valve or has_prior_ie or has_high_risk_chd
    
    if not is_high_risk:
        rec_set.add(guideline_recommendation(
            action="Patient is NOT in high-risk category. Antibiotic prophylaxis for IE is generally NOT recommended.",
            guideline_key="esc_vhd_2021",
            evidence_class=EvidenceClass.III,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.PHARMACOTHERAPY,
            section="12.1",
            rationale="Prophylaxis only for highest-risk patients and high-risk procedures",
        ))
        return rec_set
    
    # High-risk patient
    rec_set.add(guideline_recommendation(
        action="Patient is HIGH-RISK for IE. Assess procedure risk.",
        guideline_key="esc_vhd_2021",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.C,
        category=RecommendationCategory.DIAGNOSTIC,
        section="12.1",
    ))
    
    if procedure_type == "dental":
        rec_set.add(guideline_recommendation(
            action="DENTAL procedures involving gingival manipulation or perforation: Antibiotic prophylaxis RECOMMENDED",
            guideline_key="esc_vhd_2021",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PHARMACOTHERAPY,
            section="12.1",
        ))
        
        rec_set.add(guideline_recommendation(
            action="Amoxicillin 2g PO (or IV ampicillin) 30-60 minutes before procedure. If penicillin allergy: clindamycin 600mg.",
            guideline_key="esc_vhd_2021",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PHARMACOTHERAPY,
            section="12.1",
        ))
    
    elif procedure_type in ["gi", "gu"]:
        rec_set.add(guideline_recommendation(
            action="GI/GU procedures: Antibiotic prophylaxis NOT routinely recommended, but treat any existing infection before procedure",
            guideline_key="esc_vhd_2021",
            evidence_class=EvidenceClass.III,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.PHARMACOTHERAPY,
            section="12.1",
        ))
    
    elif procedure_type == "skin":
        rec_set.add(guideline_recommendation(
            action="Skin procedures involving infected tissue: Antibiotic prophylaxis covering staphylococci SHOULD BE CONSIDERED",
            guideline_key="esc_vhd_2021",
            evidence_class=EvidenceClass.IIA,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.PHARMACOTHERAPY,
            section="12.1",
        ))
    
    # General hygiene measures
    rec_set.add(guideline_recommendation(
        action="Emphasize good oral hygiene and regular dental care to all high-risk patients",
        guideline_key="esc_vhd_2021",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.C,
        category=RecommendationCategory.LIFESTYLE,
        section="12.1",
    ))
    
    return rec_set


def get_vhd_followup_schedule(
    valve_disease: str,  # "aortic_stenosis", "mitral_regurgitation", etc.
    severity: str,  # "mild", "moderate", "severe"
    post_intervention: bool = False,
) -> RecommendationSet:
    """
    Follow-up schedule recommendations for VHD.
    
    Per ESC 2021 VHD Guidelines Section 4
    
    Args:
        valve_disease: Type of valve disease
        severity: Severity classification
        post_intervention: Whether patient had valve intervention
    
    Returns:
        RecommendationSet with follow-up recommendations
    """
    rec_set = RecommendationSet(
        title=f"Follow-up for {valve_disease.replace('_', ' ').title()} ({severity})",
        primary_guideline="ESC VHD 2021",
    )
    
    if post_intervention:
        rec_set.add(guideline_recommendation(
            action="Post-intervention: Clinical assessment and TTE at 30 days, then at 1 year, then annually",
            guideline_key="esc_vhd_2021",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.MONITORING,
            section="4.2",
        ))
        return rec_set
    
    if severity == "mild":
        rec_set.add(guideline_recommendation(
            action="MILD VHD: Clinical follow-up every 2-3 years. Echo if symptoms develop or change.",
            guideline_key="esc_vhd_2021",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.MONITORING,
            section="4.2",
        ))
    
    elif severity == "moderate":
        rec_set.add(guideline_recommendation(
            action="MODERATE VHD: Clinical and echo assessment every 1-2 years",
            guideline_key="esc_vhd_2021",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.MONITORING,
            section="4.2",
        ))
    
    else:  # severe
        rec_set.add(guideline_recommendation(
            action="SEVERE VHD: Clinical and echo assessment every 6-12 months. Closer follow-up if asymptomatic approaching intervention thresholds.",
            guideline_key="esc_vhd_2021",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.MONITORING,
            section="4.2",
        ))
    
    return rec_set


def assess_surgical_risk(patient: "Patient") -> RecommendationSet:
    """
    Assess surgical risk for valve intervention.
    
    Uses EuroSCORE II and STS scores.
    
    Args:
        patient: Patient being evaluated
    
    Returns:
        RecommendationSet with risk assessment
    """
    rec_set = RecommendationSet(
        title="Surgical Risk Assessment for Valve Intervention",
        primary_guideline="ESC VHD 2021",
    )
    
    rec_set.add(guideline_recommendation(
        action="Calculate EuroSCORE II or STS score for surgical risk assessment",
        guideline_key="esc_vhd_2021",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.B,
        category=RecommendationCategory.DIAGNOSTIC,
        section="5.1",
    ))
    
    # Calculate EuroSCORE if we have data
    if patient.age and patient.labs and patient.labs.egfr:
        result = euro_score_ii(
            age=patient.age,
            sex=patient.sex.value if patient.sex else "male",
            egfr=patient.labs.egfr,
            lvef=patient.lvef or 55,
        )
        
        rec_set.add(guideline_recommendation(
            action=f"Estimated EuroSCORE II: {result.score_value}% - {result.risk_category.upper()} surgical risk",
            guideline_key="esc_vhd_2021",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.DIAGNOSTIC,
            section="5.1",
            rationale=result.recommendation,
        ))
    
    rec_set.add(guideline_recommendation(
        action="Risk scores alone should not determine intervention. Heart Team assessment integrating frailty, comorbidities, anatomy, and patient preferences is essential.",
        guideline_key="esc_vhd_2021",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.C,
        category=RecommendationCategory.REFERRAL,
        section="5.1",
    ))
    
    return rec_set
