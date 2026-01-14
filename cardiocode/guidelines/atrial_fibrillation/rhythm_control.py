"""
Rhythm Control in Atrial Fibrillation - ESC 2020 Guidelines.

Implements rhythm control strategy from ESC AF 2020:
- Rhythm vs rate control decision
- Cardioversion guidance
- Antiarrhythmic drug selection
- Upstream therapy
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
class RhythmControlAssessment:
    """Assessment for rhythm control candidacy."""
    rhythm_control_preferred: bool
    rationale: List[str]
    contraindications: List[str]
    recommendations: List[Recommendation]


def assess_rhythm_control_candidacy(patient: "Patient") -> RhythmControlAssessment:
    """
    Assess whether rhythm control is appropriate for AF patient.
    
    Per ESC 2020: Rhythm control to improve symptoms
    
    Rhythm control preferred when:
    - Symptoms attributable to AF despite rate control
    - Patient preference
    - Younger patients
    - First episode or paroxysmal AF
    - AF-induced cardiomyopathy (tachycardia-mediated)
    - Early after AF onset (early rhythm control per EAST-AFNET 4)
    
    Args:
        patient: Patient object
    
    Returns:
        RhythmControlAssessment with recommendation
    """
    rationale_for = []
    rationale_against = []
    contraindications = []
    recommendations = []
    
    # Factors favoring rhythm control
    if patient.nyha_class and patient.nyha_class.value >= 2:
        rationale_for.append("Symptomatic despite rate control")
    
    if patient.age and patient.age < 65:
        rationale_for.append("Younger patient - may benefit more from rhythm control")
    
    if patient.af_type:
        if patient.af_type.value in ["first_diagnosed", "paroxysmal"]:
            rationale_for.append(f"{patient.af_type.value} AF - higher success rate with rhythm control")
        elif patient.af_type.value == "long_standing_persistent":
            rationale_against.append("Long-standing persistent AF - lower success rate")
    
    # Tachycardia-mediated cardiomyopathy
    if patient.lvef and patient.lvef < 50:
        if patient.vitals and patient.vitals.heart_rate and patient.vitals.heart_rate > 100:
            rationale_for.append("Possible tachycardia-mediated cardiomyopathy - rhythm control may restore LV function")
    
    # EAST-AFNET 4 findings
    if patient.af_type and patient.af_type.value == "first_diagnosed":
        rationale_for.append("EAST-AFNET 4: Early rhythm control associated with better outcomes")
    
    # Factors against
    if patient.echo and patient.echo.la_volume_index:
        if patient.echo.la_volume_index > 50:
            rationale_against.append("Severely dilated LA - lower success rate")
    
    # Determine recommendation
    rhythm_control_preferred = len(rationale_for) > len(rationale_against)
    
    if rhythm_control_preferred:
        recommendations.append(guideline_recommendation(
            action="Rhythm control strategy recommended to reduce AF symptoms and potentially improve outcomes",
            guideline_key="esc_af_2020",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PHARMACOTHERAPY,
            section="11.4",
            studies=["EAST-AFNET 4", "CABANA"],
            rationale="; ".join(rationale_for),
        ))
    else:
        recommendations.append(guideline_recommendation(
            action="Rate control may be acceptable strategy. Rhythm control can still be pursued for symptom improvement.",
            guideline_key="esc_af_2020",
            evidence_class=EvidenceClass.IIA,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PHARMACOTHERAPY,
            section="11.4",
        ))
    
    return RhythmControlAssessment(
        rhythm_control_preferred=rhythm_control_preferred,
        rationale=rationale_for + [f"(Against): {r}" for r in rationale_against],
        contraindications=contraindications,
        recommendations=recommendations,
    )


def get_rhythm_control_strategy(patient: "Patient") -> RecommendationSet:
    """
    Get rhythm control drug recommendations.
    
    Per ESC 2020 Section 11.4: Long-term rhythm control
    
    Drug selection depends on:
    - Presence of structural heart disease
    - CAD
    - HFrEF
    """
    rec_set = RecommendationSet(
        title="AF Rhythm Control - Antiarrhythmic Drug Selection",
        primary_guideline="ESC AF 2020",
    )
    
    has_hfref = patient.lvef is not None and patient.lvef <= 40
    has_cad = patient.has_cad or patient.has_diagnosis("coronary_artery_disease")
    has_lvh = patient.echo and patient.echo.lv_mass_index and patient.echo.lv_mass_index > 115
    has_structural_hd = has_hfref or has_lvh or has_cad
    
    # AAD selection based on substrate
    if has_hfref:
        rec_set.add(guideline_recommendation(
            action="AMIODARONE is the preferred AAD for rhythm control in HFrEF",
            guideline_key="esc_af_2020",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PHARMACOTHERAPY,
            section="11.4.2",
            rationale="Amiodarone is the only AAD safe in HFrEF. Monitor for toxicity.",
            monitoring="TSH, LFTs, PFTs, ophthalmologic exam baseline then annually",
            contraindications=["Class IC drugs (flecainide, propafenone) contraindicated in HFrEF"],
        ))
        
        rec_set.add(guideline_recommendation(
            action="Catheter ablation SHOULD BE CONSIDERED for symptomatic AF in HFrEF to improve LV function and reduce HF hospitalizations",
            guideline_key="esc_af_2020",
            evidence_class=EvidenceClass.IIA,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PROCEDURE,
            section="11.4.3",
            studies=["CASTLE-AF", "AATAC"],
        ))
    
    elif has_cad:
        rec_set.add(guideline_recommendation(
            action="AMIODARONE, DRONEDARONE, or SOTALOL may be used for rhythm control in CAD",
            guideline_key="esc_af_2020",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.A,
            category=RecommendationCategory.PHARMACOTHERAPY,
            section="11.4.2",
            rationale="Flecainide/propafenone contraindicated in CAD due to proarrhythmic risk",
            contraindications=["Flecainide", "Propafenone"],
        ))
        
        rec_set.add(guideline_recommendation(
            action="Dronedarone reduces CV hospitalization and mortality in AF with CAD",
            guideline_key="esc_af_2020",
            evidence_class=EvidenceClass.IIA,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PHARMACOTHERAPY,
            section="11.4.2",
            studies=["ATHENA"],
        ))
    
    elif has_lvh:
        rec_set.add(guideline_recommendation(
            action="AMIODARONE or DRONEDARONE preferred with significant LVH. Avoid sotalol (proarrhythmic risk with LVH).",
            guideline_key="esc_af_2020",
            evidence_class=EvidenceClass.IIA,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PHARMACOTHERAPY,
            section="11.4.2",
        ))
    
    else:
        # No structural heart disease
        rec_set.add(guideline_recommendation(
            action="FLECAINIDE or PROPAFENONE are first-line AADs for AF without structural heart disease",
            guideline_key="esc_af_2020",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.A,
            category=RecommendationCategory.PHARMACOTHERAPY,
            section="11.4.2",
            rationale="Class IC drugs are effective and well-tolerated in structurally normal hearts",
            conditions=["No CAD", "No significant LVH", "No HFrEF", "No Brugada syndrome"],
        ))
        
        rec_set.add(guideline_recommendation(
            action="Combine flecainide/propafenone with AV nodal blocker (beta-blocker or CCB) to prevent rapid conduction during flutter",
            guideline_key="esc_af_2020",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PHARMACOTHERAPY,
            section="11.4.2",
        ))
        
        rec_set.add(guideline_recommendation(
            action="DRONEDARONE, SOTALOL, or AMIODARONE are alternatives if Class IC ineffective or not tolerated",
            guideline_key="esc_af_2020",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.A,
            category=RecommendationCategory.PHARMACOTHERAPY,
            section="11.4.2",
        ))
    
    return rec_set


def get_cardioversion_guidance(
    patient: "Patient",
    af_duration: Optional[str] = None,  # "<48h", ">48h", "unknown"
) -> RecommendationSet:
    """
    Cardioversion guidance for AF.
    
    Per ESC 2020 Section 11.4.1: Cardioversion
    
    Key considerations:
    - Anticoagulation duration before/after
    - TEE if <3 weeks anticoagulation
    - Rate of recurrence
    """
    rec_set = RecommendationSet(
        title="AF Cardioversion Guidance",
        primary_guideline="ESC AF 2020",
    )
    
    # Anticoagulation requirements
    if af_duration == "<48h":
        rec_set.add(guideline_recommendation(
            action="AF < 48 hours: Cardioversion can be performed with anticoagulation initiated as soon as possible",
            guideline_key="esc_af_2020",
            evidence_class=EvidenceClass.IIA,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PROCEDURE,
            section="11.4.1",
            rationale="Shorter AF duration = lower thromboembolic risk",
        ))
    else:
        rec_set.add(guideline_recommendation(
            action="AF >= 48 hours or unknown duration: Anticoagulation for >= 3 weeks OR TEE to exclude LAA thrombus before cardioversion",
            guideline_key="esc_af_2020",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PROCEDURE,
            section="11.4.1",
            studies=["X-VeRT", "ENSURE-AF"],
        ))
    
    # Post-cardioversion anticoagulation
    rec_set.add(guideline_recommendation(
        action="Continue anticoagulation for >= 4 weeks after cardioversion regardless of stroke risk",
        guideline_key="esc_af_2020",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.B,
        category=RecommendationCategory.PHARMACOTHERAPY,
        section="11.4.1",
        rationale="LA stunning occurs post-cardioversion; thromboembolic risk elevated for weeks",
    ))
    
    # Long-term anticoagulation decision
    rec_set.add(guideline_recommendation(
        action="Long-term anticoagulation after cardioversion based on CHA2DS2-VASc score, not maintenance of sinus rhythm",
        guideline_key="esc_af_2020",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.B,
        category=RecommendationCategory.PHARMACOTHERAPY,
        section="11.4.1",
    ))
    
    # Method of cardioversion
    rec_set.add(guideline_recommendation(
        action="Electrical cardioversion preferred for immediate rhythm restoration. Pharmacological cardioversion (ibutilide, vernakalant, flecainide) is alternative.",
        guideline_key="esc_af_2020",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.B,
        category=RecommendationCategory.PROCEDURE,
        section="11.4.1",
    ))
    
    return rec_set
