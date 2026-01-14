"""
PH Diagnosis - ESC/ERS 2022 Guidelines.

Implements diagnostic algorithms.
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
from cardiocode.guidelines.pulmonary_hypertension.classification import classify_ph


def diagnose_ph(patient: "Patient") -> RecommendationSet:
    """
    Diagnostic evaluation for suspected PH.
    
    Per ESC/ERS 2022 Section 6: Diagnosis
    
    Hemodynamic definition (2022 updated):
    - mPAP > 20 mmHg at rest by RHC
    
    Args:
        patient: Patient with suspected PH
    
    Returns:
        RecommendationSet with diagnostic recommendations
    """
    rec_set = RecommendationSet(
        title="Pulmonary Hypertension Diagnostic Evaluation",
        primary_guideline="ESC/ERS PH 2022",
    )
    
    # Echo screening
    if patient.echo and patient.echo.rvsp:
        if patient.echo.rvsp > 35:
            rec_set.add(guideline_recommendation(
                action=f"Elevated RVSP ({patient.echo.rvsp} mmHg) on echo. RHC recommended to confirm PH diagnosis.",
                guideline_key="esc_ph_2022",
                evidence_class=EvidenceClass.I,
                evidence_level=EvidenceLevel.C,
                category=RecommendationCategory.DIAGNOSTIC,
                section="6.2",
            ))
    else:
        rec_set.add(guideline_recommendation(
            action="Echocardiography RECOMMENDED as first-line screening for PH. Assess TR velocity, RV function, RA size.",
            guideline_key="esc_ph_2022",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.DIAGNOSTIC,
            section="6.2",
        ))
    
    # Right heart catheterization
    rec_set.add(guideline_recommendation(
        action="Right heart catheterization RECOMMENDED to confirm PH diagnosis and determine hemodynamic profile",
        guideline_key="esc_ph_2022",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.C,
        category=RecommendationCategory.DIAGNOSTIC,
        section="6.2",
        rationale="PH definition: mPAP > 20 mmHg. Also measures PAWP, PVR, CO.",
    ))
    
    # Classification workup
    classification = classify_ph(patient)
    rec_set.add(guideline_recommendation(
        action=f"Preliminary classification: {classification.group.value} ({classification.confidence}). {'; '.join(classification.rationale)}",
        guideline_key="esc_ph_2022",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.C,
        category=RecommendationCategory.DIAGNOSTIC,
        section="6.1",
    ))
    
    return rec_set


def get_diagnostic_workup(suspected_group: str) -> RecommendationSet:
    """
    Get targeted diagnostic workup based on suspected PH group.
    """
    rec_set = RecommendationSet(
        title="PH Diagnostic Workup",
        primary_guideline="ESC/ERS PH 2022",
    )
    
    # Universal tests
    rec_set.add(guideline_recommendation(
        action="ECG, chest X-ray, pulmonary function tests, and arterial blood gases for all suspected PH",
        guideline_key="esc_ph_2022",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.C,
        category=RecommendationCategory.DIAGNOSTIC,
        section="6.3",
    ))
    
    rec_set.add(guideline_recommendation(
        action="V/Q scan RECOMMENDED to rule out CTEPH in all patients with unexplained PH",
        guideline_key="esc_ph_2022",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.C,
        category=RecommendationCategory.DIAGNOSTIC,
        section="6.3",
        rationale="V/Q scan is most sensitive for CTEPH. Normal V/Q effectively excludes CTEPH.",
    ))
    
    if suspected_group == "PAH":
        rec_set.add(guideline_recommendation(
            action="For suspected PAH: HIV serology, autoimmune screen (ANA, anti-Scl70), liver function, thyroid function",
            guideline_key="esc_ph_2022",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.DIAGNOSTIC,
            section="6.3",
        ))
        
        rec_set.add(guideline_recommendation(
            action="Vasoreactivity testing at RHC for IPAH, HPAH, drug-induced PAH to identify responders to CCB therapy",
            guideline_key="esc_ph_2022",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.DIAGNOSTIC,
            section="6.3",
        ))
    
    elif suspected_group == "CTEPH":
        rec_set.add(guideline_recommendation(
            action="For suspected CTEPH: CT pulmonary angiography and pulmonary angiography. Refer to expert CTEPH center.",
            guideline_key="esc_ph_2022",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.DIAGNOSTIC,
            section="6.3",
        ))
    
    return rec_set
