"""
CCS Diagnosis - ESC 2019 Guidelines.

Implements:
- Pre-test probability calculation (updated 2019 model)
- Diagnostic testing strategy
- Stress test interpretation
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
    guideline_recommendation,
)
from cardiocode.core.evidence import EvidenceClass, EvidenceLevel


class ChestPainType(Enum):
    """Classification of chest pain."""
    TYPICAL_ANGINA = "typical_angina"
    ATYPICAL_ANGINA = "atypical_angina"
    NON_ANGINAL = "non_anginal"
    DYSPNEA = "dyspnea"


@dataclass
class PTPResult:
    """Pre-test probability calculation result."""
    ptp_percent: float
    ptp_category: str  # "very_low", "low", "moderate", "high"
    diagnostic_recommendation: str
    further_testing_needed: bool


def calculate_pretest_probability(
    age: int,
    sex: str,  # "male" or "female"
    chest_pain_type: ChestPainType,
    has_dyspnea: bool = False,
) -> PTPResult:
    """
    Calculate pre-test probability of obstructive CAD per ESC 2019.
    
    Uses updated PTP model from ESC 2019 (Table 5).
    Much lower PTPs than Duke clinical score.
    
    Args:
        age: Patient age
        sex: "male" or "female"
        chest_pain_type: Type of chest pain
        has_dyspnea: Dyspnea on exertion as angina equivalent
    
    Returns:
        PTPResult with probability and recommendation
    """
    # Simplified ESC 2019 PTP table (approximate values)
    # Format: ptp_table[age_group][sex][symptom_type] = PTP%
    
    is_male = sex.lower() == "male"
    
    # Age groups: 30-39, 40-49, 50-59, 60-69, 70+
    if age < 40:
        age_group = 0
    elif age < 50:
        age_group = 1
    elif age < 60:
        age_group = 2
    elif age < 70:
        age_group = 3
    else:
        age_group = 4
    
    # PTP values from ESC 2019 Table 5 (approximate)
    ptp_table = {
        # [typical, atypical, non-anginal, dyspnea]
        "male": [
            [3, 2, 1, 0],    # 30-39
            [22, 10, 3, 3],  # 40-49
            [32, 17, 6, 5],  # 50-59
            [44, 26, 10, 8], # 60-69
            [52, 34, 14, 12] # 70+
        ],
        "female": [
            [1, 1, 1, 0],    # 30-39
            [6, 3, 1, 1],    # 40-49
            [10, 6, 2, 2],   # 50-59
            [16, 11, 4, 4],  # 60-69
            [24, 19, 8, 6]   # 70+
        ]
    }
    
    sex_key = "male" if is_male else "female"
    
    symptom_idx = {
        ChestPainType.TYPICAL_ANGINA: 0,
        ChestPainType.ATYPICAL_ANGINA: 1,
        ChestPainType.NON_ANGINAL: 2,
        ChestPainType.DYSPNEA: 3,
    }[chest_pain_type]
    
    ptp = ptp_table[sex_key][age_group][symptom_idx]
    
    # Determine category and recommendation
    if ptp < 5:
        category = "very_low"
        recommendation = "CAD very unlikely. Consider other causes. No routine testing for CAD."
        further_testing = False
    elif ptp < 15:
        category = "low"
        recommendation = "CAD unlikely. Consider functional imaging if clinical suspicion persists. Coronary CT angiography may be used."
        further_testing = True
    elif ptp <= 85:
        category = "moderate"
        recommendation = "Non-invasive testing recommended. CCTA or functional imaging based on local expertise and patient factors."
        further_testing = True
    else:
        category = "high"
        recommendation = "CAD highly likely. Consider direct invasive coronary angiography if symptoms warrant."
        further_testing = True
    
    return PTPResult(
        ptp_percent=ptp,
        ptp_category=category,
        diagnostic_recommendation=recommendation,
        further_testing_needed=further_testing,
    )


def get_diagnostic_strategy(
    patient: "Patient",
    ptp_result: Optional[PTPResult] = None,
) -> RecommendationSet:
    """
    Get diagnostic testing recommendations for suspected CCS.
    
    Per ESC 2019 Section 4.3: Diagnostic testing
    
    Args:
        patient: Patient object
        ptp_result: Pre-test probability result
    
    Returns:
        RecommendationSet with diagnostic recommendations
    """
    rec_set = RecommendationSet(
        title="CCS Diagnostic Strategy",
        primary_guideline="ESC CCS 2019",
    )
    
    # Calculate PTP if not provided
    if not ptp_result and patient.age:
        ptp_result = calculate_pretest_probability(
            age=patient.age,
            sex=patient.sex.value if patient.sex else "male",
            chest_pain_type=ChestPainType.ATYPICAL_ANGINA,  # Default
        )
    
    if ptp_result:
        rec_set.description = f"Pre-test probability: {ptp_result.ptp_percent}% ({ptp_result.ptp_category})"
    
    # Basic workup for all
    rec_set.add(guideline_recommendation(
        action="Resting 12-lead ECG RECOMMENDED in all patients with suspected CCS",
        guideline_key="esc_ccs_2019",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.C,
        category=RecommendationCategory.DIAGNOSTIC,
        section="4.2",
    ))
    
    rec_set.add(guideline_recommendation(
        action="Resting echocardiography RECOMMENDED to assess LV function and exclude other causes of symptoms",
        guideline_key="esc_ccs_2019",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.B,
        category=RecommendationCategory.DIAGNOSTIC,
        section="4.2",
    ))
    
    rec_set.add(guideline_recommendation(
        action="Basic labs: CBC, creatinine/eGFR, lipid panel, fasting glucose/HbA1c, TSH (if clinical suspicion)",
        guideline_key="esc_ccs_2019",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.C,
        category=RecommendationCategory.DIAGNOSTIC,
        section="4.2",
    ))
    
    # PTP-based testing recommendations
    if ptp_result and ptp_result.further_testing_needed:
        if ptp_result.ptp_category in ["low", "moderate"]:
            rec_set.add(guideline_recommendation(
                action="Coronary CT angiography (CCTA) RECOMMENDED as initial test if clinical likelihood of CAD is low-moderate",
                guideline_key="esc_ccs_2019",
                evidence_class=EvidenceClass.I,
                evidence_level=EvidenceLevel.B,
                category=RecommendationCategory.DIAGNOSTIC,
                section="4.3",
                studies=["PROMISE", "SCOT-HEART"],
                rationale="CCTA has high NPV to rule out CAD",
            ))
            
            rec_set.add(guideline_recommendation(
                action="Functional imaging (stress echo, stress CMR, SPECT, PET) RECOMMENDED as alternative, especially if known CAD or need to assess ischemia burden",
                guideline_key="esc_ccs_2019",
                evidence_class=EvidenceClass.I,
                evidence_level=EvidenceLevel.B,
                category=RecommendationCategory.DIAGNOSTIC,
                section="4.3",
            ))
        
        elif ptp_result.ptp_category == "high":
            rec_set.add(guideline_recommendation(
                action="Functional imaging or invasive coronary angiography RECOMMENDED for high PTP",
                guideline_key="esc_ccs_2019",
                evidence_class=EvidenceClass.I,
                evidence_level=EvidenceLevel.B,
                category=RecommendationCategory.DIAGNOSTIC,
                section="4.3",
            ))
    
    # Exercise ECG - limited role
    rec_set.add(guideline_recommendation(
        action="Exercise ECG (without imaging) may be considered for initial diagnosis if imaging not available, but has lower diagnostic accuracy",
        guideline_key="esc_ccs_2019",
        evidence_class=EvidenceClass.IIB,
        evidence_level=EvidenceLevel.B,
        category=RecommendationCategory.DIAGNOSTIC,
        section="4.3",
        rationale="Exercise ECG has lower sensitivity/specificity than imaging. Use for functional assessment in known CAD.",
    ))
    
    return rec_set


def interpret_stress_test(
    test_type: str,  # "exercise_ecg", "stress_echo", "stress_cmr", "spect", "pet", "ccta"
    result: str,  # "positive", "negative", "equivocal"
    ischemic_burden: Optional[float] = None,  # Percentage of myocardium
    exercise_duration_minutes: Optional[float] = None,
    mets_achieved: Optional[float] = None,
    max_heart_rate_percent: Optional[float] = None,
) -> RecommendationSet:
    """
    Interpret stress test results and recommend next steps.
    
    Args:
        test_type: Type of stress test performed
        result: Overall result
        ischemic_burden: Percentage of myocardium ischemic (if applicable)
        exercise_duration_minutes: Duration of exercise
        mets_achieved: Metabolic equivalents achieved
        max_heart_rate_percent: Percentage of age-predicted max HR
    
    Returns:
        RecommendationSet with interpretation and next steps
    """
    rec_set = RecommendationSet(
        title=f"Stress Test Interpretation ({test_type})",
        primary_guideline="ESC CCS 2019",
    )
    
    # High-risk features
    high_risk = False
    
    if ischemic_burden and ischemic_burden >= 10:
        high_risk = True
        rec_set.add(guideline_recommendation(
            action=f"Significant ischemic burden ({ischemic_burden}% of myocardium). Revascularization SHOULD BE CONSIDERED.",
            guideline_key="esc_ccs_2019",
            evidence_class=EvidenceClass.IIA,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PROCEDURE,
            section="5.3",
            studies=["ISCHEMIA trial nuances"],
        ))
    
    if mets_achieved and mets_achieved < 5:
        high_risk = True
        rec_set.add(guideline_recommendation(
            action=f"Poor functional capacity ({mets_achieved} METs). Associated with increased mortality.",
            guideline_key="esc_ccs_2019",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.DIAGNOSTIC,
            section="4.3",
        ))
    
    if result == "positive":
        if not high_risk:
            rec_set.add(guideline_recommendation(
                action="Positive stress test: Optimize medical therapy. Consider invasive angiography if symptoms persist or significant ischemia suspected.",
                guideline_key="esc_ccs_2019",
                evidence_class=EvidenceClass.I,
                evidence_level=EvidenceLevel.B,
                category=RecommendationCategory.PHARMACOTHERAPY,
                section="5.2",
            ))
        else:
            rec_set.add(guideline_recommendation(
                action="High-risk positive stress test: Invasive coronary angiography RECOMMENDED for risk stratification and potential revascularization",
                guideline_key="esc_ccs_2019",
                evidence_class=EvidenceClass.I,
                evidence_level=EvidenceLevel.B,
                category=RecommendationCategory.PROCEDURE,
                section="5.3",
            ))
    
    elif result == "negative":
        rec_set.add(guideline_recommendation(
            action="Negative stress test: CAD unlikely or low-risk. Reassess if symptoms persist. Optimize CV risk factors.",
            guideline_key="esc_ccs_2019",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.MONITORING,
            section="4.3",
        ))
    
    else:  # equivocal
        rec_set.add(guideline_recommendation(
            action="Equivocal stress test: Consider alternative imaging modality or invasive angiography based on clinical suspicion",
            guideline_key="esc_ccs_2019",
            evidence_class=EvidenceClass.IIA,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.DIAGNOSTIC,
            section="4.3",
        ))
    
    return rec_set
