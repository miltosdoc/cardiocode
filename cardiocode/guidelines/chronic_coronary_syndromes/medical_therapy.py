"""
CCS Medical Therapy - ESC 2019 Guidelines.

Implements:
- Antianginal therapy (symptom relief)
- Secondary prevention (event prevention)
- Optimal medical therapy components
"""

from __future__ import annotations
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from cardiocode.core.types import Patient

from cardiocode.core.recommendation import (
    RecommendationSet,
    RecommendationCategory,
    guideline_recommendation,
)
from cardiocode.core.evidence import EvidenceClass, EvidenceLevel


def get_antianginal_therapy(patient: "Patient") -> RecommendationSet:
    """
    Get antianginal therapy recommendations for CCS.
    
    Per ESC 2019 Section 5.2.1: Drugs for symptom relief
    
    First-line: Beta-blockers and/or CCBs
    Second-line: Long-acting nitrates, ivabradine, nicorandil, ranolazine
    
    Args:
        patient: Patient with CCS
    
    Returns:
        RecommendationSet with antianginal recommendations
    """
    rec_set = RecommendationSet(
        title="Antianginal Therapy for CCS",
        description="Drugs for symptom relief",
        primary_guideline="ESC CCS 2019",
    )
    
    has_hfref = patient.lvef is not None and patient.lvef <= 40
    has_bradycardia = patient.vitals and patient.vitals.heart_rate and patient.vitals.heart_rate < 60
    has_hypotension = patient.vitals and patient.vitals.sbp and patient.vitals.sbp < 100
    
    # First-line therapy
    if has_hfref:
        rec_set.add(guideline_recommendation(
            action="Beta-blocker RECOMMENDED as first-line antianginal in CCS with HFrEF",
            guideline_key="esc_ccs_2019",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.A,
            category=RecommendationCategory.PHARMACOTHERAPY,
            section="5.2.1",
            rationale="Beta-blockers provide antianginal effect plus HF mortality benefit",
        ))
        
        rec_set.add(guideline_recommendation(
            action="Non-dihydropyridine CCBs (diltiazem, verapamil) CONTRAINDICATED in HFrEF",
            guideline_key="esc_ccs_2019",
            evidence_class=EvidenceClass.III,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.CONTRAINDICATION,
            section="5.2.1",
        ))
    else:
        rec_set.add(guideline_recommendation(
            action="Beta-blocker and/or calcium channel blocker RECOMMENDED as first-line antianginal therapy",
            guideline_key="esc_ccs_2019",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.A,
            category=RecommendationCategory.PHARMACOTHERAPY,
            section="5.2.1",
            rationale="Reduce heart rate and myocardial oxygen demand",
        ))
    
    # Sublingual NTG for all
    rec_set.add(guideline_recommendation(
        action="Short-acting sublingual nitroglycerin RECOMMENDED for immediate relief of angina and prophylaxis before exertion",
        guideline_key="esc_ccs_2019",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.B,
        category=RecommendationCategory.PHARMACOTHERAPY,
        section="5.2.1",
    ))
    
    # Second-line options
    rec_set.add(guideline_recommendation(
        action="Second-line antianginals: Long-acting nitrates, ivabradine (if HR > 70 and sinus rhythm), nicorandil, ranolazine, or trimetazidine",
        guideline_key="esc_ccs_2019",
        evidence_class=EvidenceClass.IIA,
        evidence_level=EvidenceLevel.B,
        category=RecommendationCategory.PHARMACOTHERAPY,
        section="5.2.1",
    ))
    
    # Ivabradine specific
    if not has_bradycardia:
        rec_set.add(guideline_recommendation(
            action="Ivabradine may be added if angina persists despite beta-blocker, HR > 70 bpm, and sinus rhythm",
            guideline_key="esc_ccs_2019",
            evidence_class=EvidenceClass.IIA,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PHARMACOTHERAPY,
            section="5.2.1",
            studies=["SIGNIFY (some benefit in angina subgroup)"],
        ))
    
    # Ranolazine
    rec_set.add(guideline_recommendation(
        action="Ranolazine may be added if angina persists on first-line therapy. Does not affect HR or BP.",
        guideline_key="esc_ccs_2019",
        evidence_class=EvidenceClass.IIA,
        evidence_level=EvidenceLevel.B,
        category=RecommendationCategory.PHARMACOTHERAPY,
        section="5.2.1",
        studies=["MERLIN-TIMI 36"],
    ))
    
    return rec_set


def get_secondary_prevention(patient: "Patient") -> RecommendationSet:
    """
    Get secondary prevention recommendations for CCS.
    
    Per ESC 2019 Section 5.2.2: Drugs for event prevention
    
    Core components:
    - Antiplatelet therapy
    - Statin (high-intensity)
    - ACEi/ARB if indicated
    - SGLT2i if diabetes/HF
    
    Args:
        patient: Patient with established CCS
    
    Returns:
        RecommendationSet with secondary prevention recommendations
    """
    rec_set = RecommendationSet(
        title="Secondary Prevention in CCS",
        description="Drugs for cardiovascular event prevention",
        primary_guideline="ESC CCS 2019",
    )
    
    has_diabetes = patient.has_diabetes
    has_hfref = patient.lvef is not None and patient.lvef <= 40
    has_hypertension = patient.has_hypertension
    current_ldl = patient.labs.ldl if patient.labs else None
    
    # Lipid management - most important
    rec_set.add(guideline_recommendation(
        action="High-intensity statin RECOMMENDED for all CCS patients. Target LDL-C < 55 mg/dL (1.4 mmol/L) AND >= 50% reduction from baseline.",
        guideline_key="esc_ccs_2019",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.A,
        category=RecommendationCategory.PHARMACOTHERAPY,
        section="5.2.2",
        studies=["CTT meta-analyses", "FOURIER", "ODYSSEY OUTCOMES"],
    ))
    
    if current_ldl and current_ldl > 70:
        rec_set.add(guideline_recommendation(
            action=f"Current LDL {current_ldl} mg/dL. If LDL not at goal on max statin, add ezetimibe. If still not at goal, add PCSK9 inhibitor.",
            guideline_key="esc_ccs_2019",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.A,
            category=RecommendationCategory.PHARMACOTHERAPY,
            section="5.2.2",
        ))
    
    # Blood pressure
    if has_hypertension:
        rec_set.add(guideline_recommendation(
            action="Blood pressure target < 130/80 mmHg in most CCS patients if tolerated (< 140/90 if elderly or frail)",
            guideline_key="esc_ccs_2019",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.A,
            category=RecommendationCategory.PHARMACOTHERAPY,
            section="5.2.2",
        ))
    
    # ACEi/ARB
    if has_hfref or has_diabetes or has_hypertension:
        rec_set.add(guideline_recommendation(
            action="ACE inhibitor (or ARB if intolerant) RECOMMENDED for CCS with hypertension, diabetes, HFrEF, or LV dysfunction",
            guideline_key="esc_ccs_2019",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.A,
            category=RecommendationCategory.PHARMACOTHERAPY,
            section="5.2.2",
            studies=["HOPE", "EUROPA", "PEACE"],
        ))
    
    # Diabetes management
    if has_diabetes:
        rec_set.add(guideline_recommendation(
            action="SGLT2 inhibitor or GLP-1 RA RECOMMENDED in CCS patients with type 2 diabetes",
            guideline_key="esc_ccs_2019",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.A,
            category=RecommendationCategory.PHARMACOTHERAPY,
            section="5.2.2",
            studies=["EMPA-REG OUTCOME", "LEADER", "SUSTAIN-6"],
            rationale="CV outcome benefit independent of glycemic control",
        ))
        
        rec_set.add(guideline_recommendation(
            action="HbA1c target < 7% (individualized based on age, duration, comorbidities)",
            guideline_key="esc_ccs_2019",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.A,
            category=RecommendationCategory.PHARMACOTHERAPY,
            section="5.2.2",
        ))
    
    # Lifestyle
    rec_set.add(guideline_recommendation(
        action="Smoking cessation is ESSENTIAL. Offer pharmacotherapy (varenicline, bupropion, NRT) and behavioral support.",
        guideline_key="esc_ccs_2019",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.A,
        category=RecommendationCategory.LIFESTYLE,
        section="5.2.2",
    ))
    
    rec_set.add(guideline_recommendation(
        action="Regular physical activity RECOMMENDED: >= 150 min/week moderate or >= 75 min/week vigorous aerobic exercise",
        guideline_key="esc_ccs_2019",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.A,
        category=RecommendationCategory.LIFESTYLE,
        section="5.2.2",
    ))
    
    rec_set.add(guideline_recommendation(
        action="Mediterranean diet or similar heart-healthy diet RECOMMENDED",
        guideline_key="esc_ccs_2019",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.B,
        category=RecommendationCategory.LIFESTYLE,
        section="5.2.2",
        studies=["PREDIMED"],
    ))
    
    rec_set.add(guideline_recommendation(
        action="Cardiac rehabilitation RECOMMENDED for all CCS patients, especially post-revascularization",
        guideline_key="esc_ccs_2019",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.A,
        category=RecommendationCategory.REFERRAL,
        section="5.2.2",
    ))
    
    return rec_set


def optimize_medical_therapy(patient: "Patient") -> RecommendationSet:
    """
    Comprehensive optimal medical therapy for CCS.
    
    Combines antianginal therapy and secondary prevention.
    
    Args:
        patient: Patient with CCS
    
    Returns:
        Complete OMT recommendation set
    """
    rec_set = RecommendationSet(
        title="Optimal Medical Therapy for CCS",
        description="Complete medical management",
        primary_guideline="ESC CCS 2019",
    )
    
    # Get antianginal recommendations
    antianginal = get_antianginal_therapy(patient)
    rec_set.add_all(antianginal.recommendations)
    
    # Get secondary prevention
    prevention = get_secondary_prevention(patient)
    rec_set.add_all(prevention.recommendations)
    
    # Get antiplatelet therapy
    from .antithrombotic import get_antiplatelet_therapy
    antiplatelet = get_antiplatelet_therapy(patient)
    rec_set.add_all(antiplatelet.recommendations)
    
    return rec_set
