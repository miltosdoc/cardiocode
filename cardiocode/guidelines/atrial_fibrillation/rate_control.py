"""
Rate Control in Atrial Fibrillation - ESC 2020 Guidelines.

Implements rate control strategy from ESC AF 2020:
- Rate control targets
- Drug selection for rate control
- Special populations (HFrEF, etc.)
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


def get_rate_control_targets(patient: "Patient") -> RecommendationSet:
    """
    Determine heart rate targets for AF rate control.
    
    Per ESC 2020 Section 11.3.1: Rate control
    
    Initial target: HR < 110 bpm at rest (lenient control)
    Stricter control (HR < 80) if symptoms persist
    """
    rec_set = RecommendationSet(
        title="AF Rate Control Targets",
        primary_guideline="ESC AF 2020",
    )
    
    rec_set.add(guideline_recommendation(
        action="Initial rate target: resting heart rate < 110 bpm (lenient rate control)",
        guideline_key="esc_af_2020",
        evidence_class=EvidenceClass.IIA,
        evidence_level=EvidenceLevel.B,
        category=RecommendationCategory.MONITORING,
        section="11.3.1",
        studies=["RACE II"],
        rationale="RACE II showed lenient control (HR <110) non-inferior to strict control",
    ))
    
    rec_set.add(guideline_recommendation(
        action="If symptoms persist despite HR < 110: consider stricter control (HR < 80 bpm at rest)",
        guideline_key="esc_af_2020",
        evidence_class=EvidenceClass.IIA,
        evidence_level=EvidenceLevel.B,
        category=RecommendationCategory.MONITORING,
        section="11.3.1",
    ))
    
    return rec_set


def get_rate_control_strategy(patient: "Patient") -> RecommendationSet:
    """
    Get rate control drug recommendations for AF.
    
    Per ESC 2020 Section 11.3: Long-term rate control
    
    Drug selection depends on:
    - Presence of HFrEF
    - Hemodynamic status
    - Current medications
    
    Args:
        patient: Patient object
    
    Returns:
        RecommendationSet with rate control recommendations
    """
    rec_set = RecommendationSet(
        title="AF Rate Control Strategy",
        description="Drug selection for long-term rate control",
        primary_guideline="ESC AF 2020",
    )
    
    # Add rate targets
    target_recs = get_rate_control_targets(patient)
    rec_set.add_all(target_recs.recommendations)
    
    # Determine if HFrEF present
    has_hfref = patient.lvef is not None and patient.lvef <= 40
    
    # Check current medications
    on_beta_blocker = patient.is_on_medication("beta_blocker")
    on_diltiazem = patient.is_on_medication("diltiazem")
    on_verapamil = patient.is_on_medication("verapamil")
    on_digoxin = patient.is_on_medication("digoxin")
    
    if has_hfref:
        # HFrEF - specific recommendations
        rec_set.add(guideline_recommendation(
            action="Beta-blocker RECOMMENDED for rate control in AF with HFrEF (bisoprolol, carvedilol, metoprolol, nebivolol)",
            guideline_key="esc_af_2020",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PHARMACOTHERAPY,
            section="11.3.1",
            rationale="Beta-blockers also provide HF mortality benefit",
        ))
        
        rec_set.add(guideline_recommendation(
            action="Digoxin may be added if rate control inadequate with beta-blocker alone",
            guideline_key="esc_af_2020",
            evidence_class=EvidenceClass.IIB,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PHARMACOTHERAPY,
            section="11.3.1",
            monitoring="Monitor digoxin levels (target 0.5-1.0 ng/mL). Adjust for renal function.",
        ))
        
        rec_set.add(guideline_recommendation(
            action="Diltiazem and verapamil are CONTRAINDICATED in HFrEF due to negative inotropy",
            guideline_key="esc_af_2020",
            evidence_class=EvidenceClass.III,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.CONTRAINDICATION,
            section="11.3.1",
        ))
        
        rec_set.add(guideline_recommendation(
            action="Consider amiodarone if rate control inadequate with beta-blocker + digoxin",
            guideline_key="esc_af_2020",
            evidence_class=EvidenceClass.IIB,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PHARMACOTHERAPY,
            section="11.3.1",
            rationale="Amiodarone effective but has significant toxicity with long-term use",
        ))
    
    else:
        # No HFrEF - more options
        rec_set.add(guideline_recommendation(
            action="Beta-blocker OR diltiazem/verapamil RECOMMENDED as first-line for rate control",
            guideline_key="esc_af_2020",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PHARMACOTHERAPY,
            section="11.3.1",
        ))
        
        rec_set.add(guideline_recommendation(
            action="Digoxin may be used as monotherapy in sedentary patients or added to beta-blocker/CCB",
            guideline_key="esc_af_2020",
            evidence_class=EvidenceClass.IIB,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PHARMACOTHERAPY,
            section="11.3.1",
            rationale="Digoxin less effective during exercise; best for sedentary patients",
        ))
    
    # AV node ablation as last resort
    rec_set.add(guideline_recommendation(
        action="AV node ablation + pacemaker may be considered if pharmacological rate control fails",
        guideline_key="esc_af_2020",
        evidence_class=EvidenceClass.IIB,
        evidence_level=EvidenceLevel.B,
        category=RecommendationCategory.PROCEDURE,
        section="11.3.2",
        conditions=["Failed pharmacological rate control", "Symptoms significantly affecting QoL"],
        rationale="Creates pacemaker dependence but effectively controls rate",
    ))
    
    return rec_set


def acute_rate_control(patient: "Patient") -> RecommendationSet:
    """
    Acute rate control for rapid AF.
    
    Per ESC 2020: Acute rate control in hemodynamically stable patients
    """
    rec_set = RecommendationSet(
        title="Acute AF Rate Control",
        description="Immediate rate control for rapid AF",
        primary_guideline="ESC AF 2020",
    )
    
    has_hfref = patient.lvef is not None and patient.lvef <= 40
    
    if has_hfref:
        rec_set.add(guideline_recommendation(
            action="IV beta-blocker (metoprolol or esmolol) OR IV digoxin for acute rate control in HFrEF",
            guideline_key="esc_af_2020",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PHARMACOTHERAPY,
            urgency=Urgency.URGENT,
            section="11.3.1",
            contraindications=["IV diltiazem/verapamil contraindicated in HFrEF"],
        ))
        
        rec_set.add(guideline_recommendation(
            action="IV amiodarone may be used if other agents ineffective or contraindicated",
            guideline_key="esc_af_2020",
            evidence_class=EvidenceClass.IIB,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PHARMACOTHERAPY,
            urgency=Urgency.URGENT,
            section="11.3.1",
        ))
    else:
        rec_set.add(guideline_recommendation(
            action="IV beta-blocker (metoprolol, esmolol) OR IV diltiazem/verapamil for acute rate control",
            guideline_key="esc_af_2020",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PHARMACOTHERAPY,
            urgency=Urgency.URGENT,
            section="11.3.1",
        ))
    
    return rec_set
