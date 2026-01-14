"""
Acute Heart Failure Management - ESC 2021 Guidelines.

Implements acute HF algorithms from ESC HF 2021:
- Clinical profiling (warm-wet, cold-wet, etc.)
- Initial management
- Diuretic strategy
- Vasodilator and inotrope use
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
from cardiocode.guidelines.heart_failure.diagnosis import (
    assess_congestion,
    assess_perfusion,
    CongestionStatus,
    PerfusionStatus,
)


class AHFPrecipitant(Enum):
    """Common precipitants of acute HF decompensation (CHAMP)."""
    ACUTE_CORONARY_SYNDROME = "acs"
    HYPERTENSIVE_EMERGENCY = "hypertension"
    ARRHYTHMIA = "arrhythmia"
    MECHANICAL_CAUSE = "mechanical"  # Valve, VSD, tamponade
    PULMONARY_EMBOLISM = "pe"


@dataclass
class AHFAssessment:
    """Assessment of acute heart failure presentation."""
    clinical_profile: str  # "warm-wet", "cold-wet", "warm-dry", "cold-dry"
    congestion: CongestionStatus
    perfusion: PerfusionStatus
    
    # Precipitants identified
    precipitants: List[str]
    
    # Severity indicators
    cardiogenic_shock: bool
    requires_icu: bool
    
    # Recommendations
    recommendations: List[Recommendation]


def assess_acute_hf(patient: "Patient") -> AHFAssessment:
    """
    Assess acute heart failure presentation.
    
    Per ESC 2021 Section 12: Acute heart failure
    
    Determines:
    1. Clinical profile (warm/cold, wet/dry)
    2. Identifies precipitants requiring urgent treatment
    3. Assesses severity
    
    Args:
        patient: Patient object with current clinical data
    
    Returns:
        AHFAssessment with profile and recommendations
    """
    recommendations = []
    precipitants = []
    
    # Determine clinical profile
    congestion = assess_congestion(patient)
    perfusion = assess_perfusion(patient)
    profile = f"{perfusion.value}-{congestion.value}"
    
    # Check for cardiogenic shock
    cardiogenic_shock = False
    if patient.vitals:
        if patient.vitals.systolic_bp and patient.vitals.systolic_bp < 90:
            if perfusion == PerfusionStatus.COLD:
                cardiogenic_shock = True
    
    # Identify precipitants (CHAMP)
    # C - Acute Coronary Syndrome
    if patient.labs and patient.labs.troponin_t:
        if patient.labs.troponin_t > 14:  # Elevated hs-TnT
            precipitants.append("Possible ACS - elevated troponin")
    
    # H - Hypertension
    if patient.vitals and patient.vitals.systolic_bp:
        if patient.vitals.systolic_bp > 180:
            precipitants.append("Hypertensive emergency")
    
    # A - Arrhythmia
    if patient.ecg:
        if patient.ecg.af_present and patient.vitals and patient.vitals.heart_rate:
            if patient.vitals.heart_rate > 110:
                precipitants.append("Rapid AF")
        if patient.ecg.heart_rate and patient.ecg.heart_rate < 40:
            precipitants.append("Severe bradycardia")
    
    # Determine ICU need
    requires_icu = cardiogenic_shock or (
        patient.vitals and patient.vitals.oxygen_saturation and patient.vitals.oxygen_saturation < 90
    )
    
    # Generate initial recommendations based on profile
    if precipitants:
        recommendations.append(guideline_recommendation(
            action=f"Address precipitants immediately: {', '.join(precipitants)}",
            guideline_key="esc_hf_2021",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.PROCEDURE,
            urgency=Urgency.EMERGENT,
            section="12.2",
        ))
    
    if cardiogenic_shock:
        recommendations.append(guideline_recommendation(
            action="CARDIOGENIC SHOCK: ICU admission. Consider inotropes/vasopressors. Evaluate for MCS.",
            guideline_key="esc_hf_2021",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.PROCEDURE,
            urgency=Urgency.EMERGENT,
            section="12.5",
        ))
    
    return AHFAssessment(
        clinical_profile=profile,
        congestion=congestion,
        perfusion=perfusion,
        precipitants=precipitants,
        cardiogenic_shock=cardiogenic_shock,
        requires_icu=requires_icu,
        recommendations=recommendations,
    )


def get_acute_hf_treatment(patient: "Patient") -> RecommendationSet:
    """
    Get treatment recommendations for acute HF.
    
    Per ESC 2021 Section 12: Acute heart failure management
    
    Based on clinical profile:
    - Warm-Wet: Diuretics +/- vasodilators
    - Cold-Wet: Diuretics + inotropes, consider MCS
    - Warm-Dry: Adjust oral therapy
    - Cold-Dry: Careful fluid challenge, consider inotropes
    
    Args:
        patient: Patient object
    
    Returns:
        RecommendationSet with acute HF treatment
    """
    assessment = assess_acute_hf(patient)
    
    rec_set = RecommendationSet(
        title=f"Acute HF Treatment - Profile: {assessment.clinical_profile.upper()}",
        description=f"ESC 2021 Acute HF Management. Congestion: {assessment.congestion.value}, Perfusion: {assessment.perfusion.value}",
        primary_guideline="ESC HF 2021",
    )
    
    # Add precipitant-related recommendations
    for rec in assessment.recommendations:
        rec_set.add(rec)
    
    # Oxygen therapy
    if patient.vitals and patient.vitals.oxygen_saturation:
        if patient.vitals.oxygen_saturation < 90:
            rec_set.add(guideline_recommendation(
                action="Oxygen therapy to maintain SpO2 >= 90%. Consider NIV if respiratory distress.",
                guideline_key="esc_hf_2021",
                evidence_class=EvidenceClass.I,
                evidence_level=EvidenceLevel.C,
                category=RecommendationCategory.PROCEDURE,
                urgency=Urgency.EMERGENT,
                section="12.3",
            ))
    
    # Profile-specific treatment
    if assessment.clinical_profile == "warm-wet":
        # Most common presentation
        rec_set.add(guideline_recommendation(
            action="IV loop diuretic: furosemide 40-80mg IV (or 1-2.5x oral home dose). Assess response at 2 hours.",
            guideline_key="esc_hf_2021",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.PHARMACOTHERAPY,
            urgency=Urgency.URGENT,
            section="12.4",
            monitoring="Urine output, creatinine, electrolytes, symptoms",
        ))
        
        if patient.vitals and patient.vitals.systolic_bp and patient.vitals.systolic_bp > 110:
            rec_set.add(guideline_recommendation(
                action="Consider IV vasodilator (nitrates) if SBP > 110 mmHg for faster symptom relief",
                guideline_key="esc_hf_2021",
                evidence_class=EvidenceClass.IIA,
                evidence_level=EvidenceLevel.B,
                category=RecommendationCategory.PHARMACOTHERAPY,
                section="12.4",
                conditions=["SBP > 110 mmHg", "No severe aortic stenosis"],
            ))
    
    elif assessment.clinical_profile == "cold-wet":
        # Hypoperfused and congested
        rec_set.add(guideline_recommendation(
            action="Low-dose diuretics initially (may be ineffective with hypoperfusion). Consider inotrope to improve perfusion first.",
            guideline_key="esc_hf_2021",
            evidence_class=EvidenceClass.IIB,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.PHARMACOTHERAPY,
            urgency=Urgency.URGENT,
            section="12.5",
        ))
        
        rec_set.add(guideline_recommendation(
            action="Consider inotrope (dobutamine or milrinone) for persistent hypoperfusion despite fluid optimization",
            guideline_key="esc_hf_2021",
            evidence_class=EvidenceClass.IIB,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.PHARMACOTHERAPY,
            urgency=Urgency.URGENT,
            section="12.5",
            rationale="Inotropes improve hemodynamics but may increase mortality. Use lowest effective dose for shortest duration.",
            monitoring="Continuous telemetry, frequent BP checks",
        ))
        
        if assessment.cardiogenic_shock:
            rec_set.add(guideline_recommendation(
                action="CARDIOGENIC SHOCK: Add vasopressor (norepinephrine) if MAP < 65 despite inotrope. Consider MCS (IABP, Impella, ECMO).",
                guideline_key="esc_hf_2021",
                evidence_class=EvidenceClass.IIB,
                evidence_level=EvidenceLevel.B,
                category=RecommendationCategory.PROCEDURE,
                urgency=Urgency.EMERGENT,
                section="12.5",
            ))
    
    elif assessment.clinical_profile == "warm-dry":
        # Adequately perfused, not congested
        rec_set.add(guideline_recommendation(
            action="Warm-dry profile: Optimize oral GDMT. Evaluate for other causes of symptoms.",
            guideline_key="esc_hf_2021",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.PHARMACOTHERAPY,
            section="12.4",
            rationale="If truly euvolemic and well-perfused, diuretics and IV therapy may not be needed.",
        ))
    
    elif assessment.clinical_profile == "cold-dry":
        # Hypoperfused but not congested - rarest
        rec_set.add(guideline_recommendation(
            action="Cold-dry profile: Consider cautious fluid challenge (250mL). May need inotrope if no response.",
            guideline_key="esc_hf_2021",
            evidence_class=EvidenceClass.IIB,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.PHARMACOTHERAPY,
            urgency=Urgency.URGENT,
            section="12.5",
            rationale="Rare presentation. Exclude RV infarction, PE, hypovolemia.",
        ))
    
    # Continue chronic medications
    rec_set.add(guideline_recommendation(
        action="Continue beta-blocker unless cardiogenic shock, severe bradycardia, or advanced AV block. Consider dose reduction if HR low.",
        guideline_key="esc_hf_2021",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.C,
        category=RecommendationCategory.PHARMACOTHERAPY,
        section="12.3",
    ))
    
    rec_set.add(guideline_recommendation(
        action="Continue ACEi/ARB/ARNI if SBP stable and no AKI. May hold temporarily if hypotensive or significant creatinine rise.",
        guideline_key="esc_hf_2021",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.C,
        category=RecommendationCategory.PHARMACOTHERAPY,
        section="12.3",
    ))
    
    return rec_set
