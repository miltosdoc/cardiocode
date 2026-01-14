"""
AF Ablation - ESC 2020 Guidelines.

Implements catheter ablation indications from ESC AF 2020:
- First-line vs second-line indications
- Special populations (HFrEF)
- Success rates and recurrence
"""

from __future__ import annotations
from typing import Optional, List, TYPE_CHECKING
from dataclasses import dataclass

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


@dataclass
class AblationAssessment:
    """Assessment for AF ablation candidacy."""
    ablation_indicated: bool
    indication_strength: str  # "first_line", "second_line", "relative", "not_indicated"
    estimated_success: str  # "high", "moderate", "low"
    considerations: List[str]
    recommendations: List[Recommendation]


def assess_ablation_indication(patient: "Patient") -> AblationAssessment:
    """
    Assess indication for AF catheter ablation.
    
    Per ESC 2020 Section 11.4.3: Catheter ablation
    
    Class I indications:
    - Symptomatic paroxysmal AF refractory to AAD (I, A)
    - Symptomatic persistent AF refractory to AAD (I, A)
    
    Class IIa indications:
    - First-line therapy in selected patients (IIa, B)
    - AF with HFrEF to improve symptoms and LV function (IIa, B)
    
    Args:
        patient: Patient object
    
    Returns:
        AblationAssessment with indication and recommendations
    """
    considerations = []
    recommendations = []
    
    # Factors affecting success
    has_hfref = patient.lvef is not None and patient.lvef <= 40
    
    # AF type affects success rate
    success_estimate = "moderate"
    if patient.af_type:
        if patient.af_type.value == "paroxysmal":
            success_estimate = "high"
            considerations.append("Paroxysmal AF: ~70-80% success at 1 year")
        elif patient.af_type.value == "persistent":
            success_estimate = "moderate"
            considerations.append("Persistent AF: ~50-60% success at 1 year")
        elif patient.af_type.value == "long_standing_persistent":
            success_estimate = "low"
            considerations.append("Long-standing persistent AF: lower success rate")
    
    # LA size affects success
    if patient.echo and patient.echo.la_volume_index:
        if patient.echo.la_volume_index > 50:
            success_estimate = "low"
            considerations.append(f"Dilated LA (LAVI {patient.echo.la_volume_index}): reduces ablation success")
    
    # Special population: HFrEF
    if has_hfref:
        considerations.append("HFrEF present: Ablation may improve LVEF and reduce HF events (CASTLE-AF)")
        recommendations.append(guideline_recommendation(
            action="Catheter ablation SHOULD BE CONSIDERED for symptomatic AF in HFrEF to improve LVEF and reduce HF hospitalization",
            guideline_key="esc_af_2020",
            evidence_class=EvidenceClass.IIA,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PROCEDURE,
            section="11.4.3",
            studies=["CASTLE-AF", "AATAC", "CABANA (HF subgroup)"],
            rationale="Catheter ablation superior to medical therapy in HFrEF for mortality and HF outcomes",
        ))
        
        return AblationAssessment(
            ablation_indicated=True,
            indication_strength="second_line",  # After at least trial of AAD or if AAD unsuitable
            estimated_success=success_estimate,
            considerations=considerations,
            recommendations=recommendations,
        )
    
    # Check if symptomatic and failed AAD
    failed_aad = patient.is_on_medication("antiarrhythmic") or patient.is_on_medication("amiodarone")
    
    if failed_aad:
        recommendations.append(guideline_recommendation(
            action="Catheter ablation RECOMMENDED for symptomatic AF after failure or intolerance of at least one Class I or III AAD",
            guideline_key="esc_af_2020",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.A,
            category=RecommendationCategory.PROCEDURE,
            section="11.4.3",
            studies=["RAAFT-2", "MANTRA-PAF", "CABANA"],
            rationale="Ablation more effective than AAD for rhythm control",
        ))
        
        return AblationAssessment(
            ablation_indicated=True,
            indication_strength="second_line",
            estimated_success=success_estimate,
            considerations=considerations,
            recommendations=recommendations,
        )
    
    # First-line ablation consideration
    if patient.af_type and patient.af_type.value == "paroxysmal":
        recommendations.append(guideline_recommendation(
            action="Catheter ablation as first-line therapy may be considered in selected patients with symptomatic paroxysmal AF",
            guideline_key="esc_af_2020",
            evidence_class=EvidenceClass.IIA,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PROCEDURE,
            section="11.4.3",
            studies=["EARLY-AF", "STOP-AF First"],
            rationale="First-line ablation associated with better rhythm outcomes than AAD",
            conditions=["Patient preference", "Willing to accept procedural risks", "Good ablation candidate"],
        ))
        
        return AblationAssessment(
            ablation_indicated=True,
            indication_strength="first_line",
            estimated_success=success_estimate,
            considerations=considerations,
            recommendations=recommendations,
        )
    
    # Default - ablation available as option
    recommendations.append(guideline_recommendation(
        action="Catheter ablation is an option for symptomatic AF. Discuss risks/benefits with patient.",
        guideline_key="esc_af_2020",
        evidence_class=EvidenceClass.IIA,
        evidence_level=EvidenceLevel.B,
        category=RecommendationCategory.PROCEDURE,
        section="11.4.3",
    ))
    
    return AblationAssessment(
        ablation_indicated=True,
        indication_strength="relative",
        estimated_success=success_estimate,
        considerations=considerations,
        recommendations=recommendations,
    )


def get_ablation_recommendation(patient: "Patient") -> RecommendationSet:
    """
    Get comprehensive ablation recommendations.
    
    Includes procedural considerations and post-ablation care.
    """
    assessment = assess_ablation_indication(patient)
    
    rec_set = RecommendationSet(
        title="AF Catheter Ablation Assessment",
        description=f"Indication: {assessment.indication_strength}, Estimated success: {assessment.estimated_success}",
        primary_guideline="ESC AF 2020",
    )
    
    # Add main recommendations
    for rec in assessment.recommendations:
        rec_set.add(rec)
    
    # Add considerations as context
    if assessment.considerations:
        rec_set.description += "\n\nConsiderations:\n" + "\n".join(f"- {c}" for c in assessment.considerations)
    
    # Procedural recommendations
    if assessment.ablation_indicated:
        rec_set.add(guideline_recommendation(
            action="Pulmonary vein isolation (PVI) is the cornerstone of AF ablation",
            guideline_key="esc_af_2020",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.A,
            category=RecommendationCategory.PROCEDURE,
            section="11.4.3",
        ))
        
        rec_set.add(guideline_recommendation(
            action="Continue anticoagulation during and for at least 2 months after ablation",
            guideline_key="esc_af_2020",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PHARMACOTHERAPY,
            section="11.4.3",
        ))
        
        rec_set.add(guideline_recommendation(
            action="Long-term anticoagulation after ablation based on CHA2DS2-VASc, NOT rhythm outcome",
            guideline_key="esc_af_2020",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.PHARMACOTHERAPY,
            section="11.4.3",
            rationale="Silent AF recurrence is common; stroke risk persists despite apparent sinus rhythm",
        ))
        
        # Complication awareness
        rec_set.add(guideline_recommendation(
            action="Discuss procedural risks: stroke (~0.5%), tamponade (~1%), PV stenosis (<1%), esophageal injury (rare but serious)",
            guideline_key="esc_af_2020",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.PROCEDURE,
            section="11.4.3",
        ))
    
    return rec_set
