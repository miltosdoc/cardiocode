"""
NSTE-ACS Medical Management - ESC 2020 Guidelines.

Implements:
- Initial medical therapy
- Secondary prevention
- Discharge planning
"""

from __future__ import annotations
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from cardiocode.core.types import Patient

from cardiocode.core.recommendation import (
    RecommendationSet,
    RecommendationCategory,
    Urgency,
    guideline_recommendation,
)
from cardiocode.core.evidence import EvidenceClass, EvidenceLevel


def get_initial_medical_therapy(
    patient: "Patient",
    invasive_strategy: bool = True,
) -> RecommendationSet:
    """
    Get initial medical therapy recommendations for NSTE-ACS.
    
    Per ESC 2020 Section 3: Initial management
    
    Args:
        patient: NSTE-ACS patient
        invasive_strategy: Whether invasive strategy planned
    
    Returns:
        RecommendationSet with initial therapy recommendations
    """
    rec_set = RecommendationSet(
        title="Initial NSTE-ACS Medical Therapy",
        primary_guideline="ESC NSTE-ACS 2020",
    )
    
    # General measures
    rec_set.add(guideline_recommendation(
        action="Admit to cardiac care unit with continuous ECG monitoring",
        guideline_key="esc_nste_acs_2020",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.C,
        category=RecommendationCategory.MONITORING,
        urgency=Urgency.URGENT,
        section="3.1",
    ))
    
    rec_set.add(guideline_recommendation(
        action="Bed rest, oxygen if SpO2 < 90%, nitrates for ongoing chest pain",
        guideline_key="esc_nste_acs_2020",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.C,
        category=RecommendationCategory.PHARMACOTHERAPY,
        urgency=Urgency.URGENT,
        section="3.1",
    ))
    
    # Beta-blockers
    if patient.vitals and patient.vitals.heart_rate and patient.vitals.heart_rate > 60:
        if patient.vitals.systolic_bp and patient.vitals.systolic_bp > 100:
            if not (patient.lvef and patient.lvef < 40):
                rec_set.add(guideline_recommendation(
                    action="Oral beta-blocker RECOMMENDED within 24 hours if no contraindications (HF, bradycardia, hypotension)",
                    guideline_key="esc_nste_acs_2020",
                    evidence_class=EvidenceClass.I,
                    evidence_level=EvidenceLevel.B,
                    category=RecommendationCategory.PHARMACOTHERAPY,
                    section="3.2",
                    rationale="Reduces myocardial oxygen demand and arrhythmia risk",
                ))
            else:
                rec_set.add(guideline_recommendation(
                    action="Beta-blocker should be used with caution in HFrEF. Consider low-dose carvedilol or bisoprolol.",
                    guideline_key="esc_nste_acs_2020",
                    evidence_class=EvidenceClass.IIA,
                    evidence_level=EvidenceLevel.B,
                    category=RecommendationCategory.PHARMACOTHERAPY,
                    section="3.2",
                ))
    
    # Nitrates
    rec_set.add(guideline_recommendation(
        action="IV nitrates RECOMMENDED for ongoing chest pain or hypertension, unless contraindicated",
        guideline_key="esc_nste_acs_2020",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.C,
        category=RecommendationCategory.PHARMACOTHERAPY,
        section="3.2",
        contraindications=["Right ventricular infarction", "Severe aortic stenosis", "PDE5 inhibitor use"],
    ))
    
    # Morphine
    rec_set.add(guideline_recommendation(
        action="IV morphine may be considered for refractory chest pain despite nitrates and beta-blockers",
        guideline_key="esc_nste_acs_2020",
        evidence_class=EvidenceClass.IIB,
        evidence_level=EvidenceLevel.C,
        category=RecommendationCategory.PHARMACOTHERAPY,
        section="3.2",
        rationale="Use with caution - may delay P2Y12 absorption and cause hypotension/respiratory depression",
    ))
    
    # Oxygen therapy
    if patient.vitals and patient.vitals.oxygen_saturation and patient.vitals.oxygen_saturation < 90:
        rec_set.add(guideline_recommendation(
            action="Oxygen therapy RECOMMENDED for SpO2 < 90%",
            guideline_key="esc_nste_acs_2020",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.PHARMACOTHERAPY,
            section="3.1",
        ))
    elif patient.vitals and patient.vitals.oxygen_saturation and patient.vitals.oxygen_saturation >= 94:
        rec_set.add(guideline_recommendation(
            action="Routine oxygen therapy NOT RECOMMENDED for SpO2 ≥ 94%",
            guideline_key="esc_nste_acs_2020",
            evidence_class=EvidenceClass.III,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.CONTRAINDICATION,
            section="3.1",
            studies=["DETO2X"],
        ))
    
    return rec_set


def get_secondary_prevention(
    patient: "Patient",
) -> RecommendationSet:
    """
    Get secondary prevention recommendations for NSTE-ACS discharge.
    
    Per ESC 2020 Section 7: Secondary prevention
    
    Args:
        patient: NSTE-ACS patient
    
    Returns:
        RecommendationSet with secondary prevention recommendations
    """
    rec_set = RecommendationSet(
        title="NSTE-ACS Secondary Prevention",
        description="Discharge medications and lifestyle recommendations",
        primary_guideline="ESC NSTE-ACS 2020",
    )
    
    # Core medications
    rec_set.add(guideline_recommendation(
        action="Aspirin 75-100 mg daily indefinitely RECOMMENDED",
        guideline_key="esc_nste_acs_2020",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.A,
        category=RecommendationCategory.PHARMACOTHERAPY,
        section="7.1",
    ))
    
    rec_set.add(guideline_recommendation(
        action="P2Y12 inhibitor (ticagrelor 90mg BID or clopidogrel 75mg daily) for 12 months RECOMMENDED",
        guideline_key="esc_nste_acs_2020",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.A,
        category=RecommendationCategory.PHARMACOTHERAPY,
        section="7.1",
    ))
    
    rec_set.add(guideline_recommendation(
        action="High-intensity statin RECOMMENDED regardless of baseline LDL. Target LDL < 55 mg/dL and ≥ 50% reduction.",
        guideline_key="esc_nste_acs_2020",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.A,
        category=RecommendationCategory.PHARMACOTHERAPY,
        section="7.1",
        studies=["PROVE-IT", "IMPROVE-IT", "FOURIER", "ODYSSEY OUTCOMES"],
    ))
    
    rec_set.add(guideline_recommendation(
        action="ACE inhibitor or ARB RECOMMENDED for all patients, especially with diabetes, hypertension, HF, or LV dysfunction",
        guideline_key="esc_nste_acs_2020",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.A,
        category=RecommendationCategory.PHARMACOTHERAPY,
        section="7.1",
        studies=["HOPE", "EUROPA", "PEACE"],
    ))
    
    rec_set.add(guideline_recommendation(
        action="Beta-blocker RECOMMENDED for 1 year post-MI, especially if HF or reduced LVEF",
        guideline_key="esc_nste_acs_2020",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.A,
        category=RecommendationCategory.PHARMACOTHERAPY,
        section="7.1",
    ))
    
    # Diabetes management
    if patient.has_diabetes:
        rec_set.add(guideline_recommendation(
            action="SGLT2 inhibitor or GLP-1 RA RECOMMENDED for type 2 diabetes post-ACS",
            guideline_key="esc_nste_acs_2020",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.A,
            category=RecommendationCategory.PHARMACOTHERAPY,
            section="7.1",
            studies=["EMPA-REG OUTCOME", "LEADER", "SUSTAIN-6"],
        ))
    
    # Lifestyle modifications
    rec_set.add(guideline_recommendation(
        action="Smoking cessation with pharmacotherapy and behavioral support RECOMMENDED",
        guideline_key="esc_nste_acs_2020",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.A,
        category=RecommendationCategory.LIFESTYLE,
        section="7.2",
    ))
    
    rec_set.add(guideline_recommendation(
        action="Cardiac rehabilitation RECOMMENDED for all eligible patients",
        guideline_key="esc_nste_acs_2020",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.A,
        category=RecommendationCategory.REFERRAL,
        section="7.2",
    ))
    
    rec_set.add(guideline_recommendation(
        action="Regular physical activity: ≥ 150 min/week moderate intensity or ≥ 75 min/week vigorous intensity",
        guideline_key="esc_nste_acs_2020",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.A,
        category=RecommendationCategory.LIFESTYLE,
        section="7.2",
    ))
    
    rec_set.add(guideline_recommendation(
        action="Heart-healthy diet (Mediterranean or similar) RECOMMENDED",
        guideline_key="esc_nste_acs_2020",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.B,
        category=RecommendationCategory.LIFESTYLE,
        section="7.2",
    ))
    
    rec_set.add(guideline_recommendation(
        action="Weight management: Target BMI 20-25 kg/m²",
        guideline_key="esc_nste_acs_2020",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.B,
        category=RecommendationCategory.LIFESTYLE,
        section="7.2",
    ))
    
    # Follow-up
    rec_set.add(guideline_recommendation(
        action="Outpatient cardiology follow-up within 2-6 weeks post-discharge RECOMMENDED",
        guideline_key="esc_nste_acs_2020",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.C,
        category=RecommendationCategory.MONITORING,
        section="7.3",
    ))
    
    return rec_set