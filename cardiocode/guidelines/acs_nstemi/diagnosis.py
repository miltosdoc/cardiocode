"""
NSTE-ACS Diagnosis - ESC 2020 Guidelines.

Implements diagnostic algorithms:
- High-sensitivity troponin interpretation
- 0h/1h and 0h/2h algorithms
- Rule-in / Rule-out / Observe pathways
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


class TroponinOutcome(Enum):
    """Outcome of hs-troponin algorithm."""
    RULE_OUT = "rule_out"           # NSTEMI ruled out
    RULE_IN = "rule_in"             # NSTEMI ruled in
    OBSERVE = "observe"             # Requires further testing
    INDETERMINATE = "indeterminate" # Cannot classify


@dataclass
class NSTEACSAssessment:
    """Assessment result for suspected NSTE-ACS."""
    diagnosis: str  # "NSTEMI", "Unstable_Angina", "Non_ACS", "Indeterminate"
    troponin_outcome: TroponinOutcome
    confidence: str
    recommendations: List[Recommendation]


def apply_hs_troponin_algorithm(
    troponin_0h: float,
    troponin_1h: Optional[float] = None,
    troponin_type: str = "hs_tnt",  # "hs_tnt" or "hs_tni"
    symptom_onset_hours: Optional[float] = None,
) -> TroponinOutcome:
    """
    Apply ESC 0h/1h hs-troponin algorithm.
    
    Per ESC 2020 Figure 4: 0h/1h algorithm for rule-out and rule-in of NSTEMI
    
    Using hs-TnT (Elecsys):
    - Rule-out: 0h < 5 ng/L OR (0h < 12 ng/L AND delta < 3 ng/L)
    - Rule-in: 0h >= 52 ng/L OR delta >= 5 ng/L
    - Observe: All others
    
    Args:
        troponin_0h: Troponin at presentation (ng/L)
        troponin_1h: Troponin at 1 hour (ng/L), optional
        troponin_type: Type of assay ("hs_tnt" or "hs_tni")
        symptom_onset_hours: Hours since symptom onset
    
    Returns:
        TroponinOutcome classification
    """
    # Thresholds for hs-TnT (Elecsys)
    # Note: Different assays have different thresholds
    if troponin_type == "hs_tnt":
        very_low = 5
        low = 12
        high = 52
        delta_rule_out = 3
        delta_rule_in = 5
    else:
        # hs-TnI (Abbott Architect) - different thresholds
        very_low = 4
        low = 6
        high = 64
        delta_rule_out = 2
        delta_rule_in = 6
    
    # Very early presenters (< 2h from onset) - need serial testing
    if symptom_onset_hours is not None and symptom_onset_hours < 2:
        if troponin_0h < very_low:
            return TroponinOutcome.OBSERVE  # Too early to rule out
    
    # 0h only (if 1h not available)
    if troponin_1h is None:
        if troponin_0h < very_low:
            return TroponinOutcome.RULE_OUT
        elif troponin_0h >= high:
            return TroponinOutcome.RULE_IN
        else:
            return TroponinOutcome.OBSERVE
    
    # 0h/1h algorithm
    delta = abs(troponin_1h - troponin_0h)
    
    # Rule-out pathway
    if troponin_0h < very_low:
        return TroponinOutcome.RULE_OUT
    
    if troponin_0h < low and delta < delta_rule_out:
        return TroponinOutcome.RULE_OUT
    
    # Rule-in pathway
    if troponin_0h >= high:
        return TroponinOutcome.RULE_IN
    
    if delta >= delta_rule_in:
        return TroponinOutcome.RULE_IN
    
    # Observe zone
    return TroponinOutcome.OBSERVE


def diagnose_nste_acs(patient: "Patient") -> NSTEACSAssessment:
    """
    Comprehensive NSTE-ACS diagnostic assessment.
    
    Per ESC 2020: Diagnostic workup for suspected NSTE-ACS
    
    Args:
        patient: Patient object with clinical data
    
    Returns:
        NSTEACSAssessment with diagnosis and recommendations
    """
    recommendations = []
    
    # Get troponin values
    troponin_0h = None
    if patient.labs:
        if patient.labs.troponin_t is not None:
            troponin_0h = patient.labs.troponin_t
        elif patient.labs.troponin_i is not None:
            troponin_0h = patient.labs.troponin_i
    
    if troponin_0h is None:
        recommendations.append(guideline_recommendation(
            action="Obtain high-sensitivity troponin (hs-TnT or hs-TnI) immediately",
            guideline_key="esc_acs_2020",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.DIAGNOSTIC,
            urgency=Urgency.EMERGENT,
            section="4.2",
        ))
        return NSTEACSAssessment(
            diagnosis="Indeterminate",
            troponin_outcome=TroponinOutcome.INDETERMINATE,
            confidence="low",
            recommendations=recommendations,
        )
    
    # Apply troponin algorithm
    troponin_type = "hs_tnt" if patient.labs.troponin_t else "hs_tni"
    outcome = apply_hs_troponin_algorithm(
        troponin_0h=troponin_0h,
        troponin_type=troponin_type,
    )
    
    if outcome == TroponinOutcome.RULE_OUT:
        # Ruled out - but still may have unstable angina
        recommendations.append(guideline_recommendation(
            action="NSTEMI ruled out by hs-troponin. Consider unstable angina if symptoms consistent. Non-invasive testing may be appropriate.",
            guideline_key="esc_acs_2020",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.DIAGNOSTIC,
            section="4.2",
            studies=["0h/1h validation studies"],
        ))
        diagnosis = "Non_ACS_or_UA"
        confidence = "high"
        
    elif outcome == TroponinOutcome.RULE_IN:
        # NSTEMI confirmed
        recommendations.append(guideline_recommendation(
            action="NSTEMI diagnosed. Initiate antithrombotic therapy and plan invasive strategy based on risk.",
            guideline_key="esc_acs_2020",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.A,
            category=RecommendationCategory.PROCEDURE,
            urgency=Urgency.URGENT,
            section="5",
        ))
        diagnosis = "NSTEMI"
        confidence = "high"
        
    else:
        # Observe zone
        recommendations.append(guideline_recommendation(
            action="In observe zone: Repeat hs-troponin at 1-2 hours and apply serial algorithm",
            guideline_key="esc_acs_2020",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.DIAGNOSTIC,
            urgency=Urgency.URGENT,
            section="4.2",
        ))
        diagnosis = "Indeterminate"
        confidence = "low"
    
    # ECG recommendations
    if patient.ecg is None:
        recommendations.append(guideline_recommendation(
            action="Obtain 12-lead ECG within 10 minutes of first medical contact",
            guideline_key="esc_acs_2020",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.DIAGNOSTIC,
            urgency=Urgency.EMERGENT,
            section="4.1",
        ))
    elif patient.ecg.st_depression or patient.ecg.t_wave_inversion:
        recommendations.append(guideline_recommendation(
            action="Ischemic ECG changes present. Higher risk. Consider early invasive strategy.",
            guideline_key="esc_acs_2020",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.DIAGNOSTIC,
            section="4.1",
        ))
    
    return NSTEACSAssessment(
        diagnosis=diagnosis,
        troponin_outcome=outcome,
        confidence=confidence,
        recommendations=recommendations,
    )
