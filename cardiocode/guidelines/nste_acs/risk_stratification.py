"""
NSTE-ACS Risk Stratification - ESC 2020 Guidelines.

Implements:
- GRACE score calculation
- Risk category assessment
- Invasive strategy timing recommendations
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
    Urgency,
    guideline_recommendation,
)
from cardiocode.core.evidence import EvidenceClass, EvidenceLevel
from cardiocode.knowledge.scores import grace_score


class RiskCategory(Enum):
    """NSTE-ACS risk categories."""
    VERY_HIGH = "very_high"
    HIGH = "high"
    INTERMEDIATE = "intermediate"
    LOW = "low"


@dataclass
class GRACEResult:
    """GRACE score calculation result."""
    score: int
    mortality_risk_percent: float
    risk_category: RiskCategory
    invasive_strategy_timing: str
    recommendations: List[str]


def calculate_grace_score(
    age: int,
    heart_rate: int,
    systolic_bp: int,
    creatinine: float,
    killip_class: int = 1,
    cardiac_arrest: bool = False,
    st_deviation: bool = False,
    elevated_troponin: bool = False,
) -> GRACEResult:
    """
    Calculate GRACE 2.0 score for NSTE-ACS risk stratification.
    
    Per ESC 2020 NSTE-ACS Guidelines Section 4.2
    
    Args:
        age: Age in years
        heart_rate: Heart rate (bpm)
        systolic_bp: Systolic blood pressure (mmHg)
        creatinine: Serum creatinine (mg/dL)
        killip_class: Killip class (1-4)
        cardiac_arrest: Cardiac arrest at admission
        st_deviation: ST-segment deviation
        elevated_troponin: Elevated cardiac troponin
    
    Returns:
        GRACEResult with score and risk category
    """
    result = grace_score(
        age=age,
        heart_rate=heart_rate,
        systolic_bp=systolic_bp,
        creatinine=creatinine,
        killip_class=killip_class,
        cardiac_arrest=cardiac_arrest,
        st_deviation=st_deviation,
        elevated_troponin=elevated_troponin,
    )
    
    # Determine risk category based on GRACE score
    if result.score_value >= 140:
        risk_category = RiskCategory.VERY_HIGH
        timing = "Immediate invasive strategy (< 2 hours)"
    elif result.score_value >= 109:
        risk_category = RiskCategory.HIGH
        timing = "Early invasive strategy (< 24 hours)"
    elif result.score_value >= 85:
        risk_category = RiskCategory.INTERMEDIATE
        timing = "Invasive strategy (< 72 hours)"
    else:
        risk_category = RiskCategory.LOW
        timing = "Selective invasive strategy"
    
    recommendations = [
        f"6-month mortality risk: {result.risk_percentage:.1f}%",
        f"Risk category: {risk_category.value}",
        f"Invasive strategy: {timing}",
    ]
    
    return GRACEResult(
        score=result.score_value,
        mortality_risk_percent=result.risk_percentage,
        risk_category=risk_category,
        invasive_strategy_timing=timing,
        recommendations=recommendations,
    )


def assess_risk_category(
    patient: "Patient",
    grace_result: Optional[GRACEResult] = None,
) -> RecommendationSet:
    """
    Comprehensive risk assessment for NSTE-ACS patient.
    
    Per ESC 2020 Section 4.2: Risk stratification
    
    Very high-risk features (immediate invasive):
    - Hemodynamic instability or cardiogenic shock
    - Recurrent or ongoing chest pain refractory to medical therapy
    - Life-threatening arrhythmias or cardiac arrest
    - Mechanical complications (ventricular septal rupture, papillary muscle rupture)
    - Acute heart failure or significant LV dysfunction
    - Recurrent dynamic ST-T segment changes
    
    High-risk features (early invasive < 24h):
    - GRACE score > 140
    - Recurrent angina with dynamic ST changes
    - Elevated troponin compatible with MI
    
    Args:
        patient: NSTE-ACS patient
        grace_result: GRACE score result
    
    Returns:
        RecommendationSet with risk assessment
    """
    rec_set = RecommendationSet(
        title="NSTE-ACS Risk Assessment",
        primary_guideline="ESC NSTE-ACS 2020",
    )
    
    # Calculate GRACE if not provided
    if not grace_result and patient.age and patient.vitals:
        grace_result = calculate_grace_score(
            age=patient.age,
            heart_rate=patient.vitals.heart_rate or 80,
            systolic_bp=patient.vitals.systolic_bp or 120,
            creatinine=patient.labs.creatinine if patient.labs else 1.0,
            killip_class=1,  # Default
            cardiac_arrest=False,
            st_deviation=patient.ecg.st_deviation if patient.ecg else False,
            elevated_troponin=patient.labs.troponin_elevated if patient.labs else False,
        )
    
    if grace_result:
        rec_set.description = f"GRACE score: {grace_result.score} ({grace_result.risk_category.value})"
        
        for rec in grace_result.recommendations:
            rec_set.add(guideline_recommendation(
                action=rec,
                guideline_key="esc_nste_acs_2020",
                evidence_class=EvidenceClass.I,
                evidence_level=EvidenceLevel.B,
                category=RecommendationCategory.DIAGNOSTIC,
                section="4.2",
            ))
    
    # Check for very high-risk features
    very_high_risk_features = []
    
    if patient.vitals and patient.vitals.sbp and patient.vitals.sbp < 90:
        very_high_risk_features.append("Hypotension/SBP < 90 mmHg")
    
    if patient.nyha_class and patient.nyha_class.value >= 3:
        very_high_risk_features.append("Acute heart failure")
    
    if patient.lvef and patient.lvef < 40:
        very_high_risk_features.append("Severe LV dysfunction")
    
    if patient.has_diagnosis("cardiogenic_shock"):
        very_high_risk_features.append("Cardiogenic shock")
    
    if very_high_risk_features:
        rec_set.add(guideline_recommendation(
            action=f"VERY HIGH RISK: {', '.join(very_high_risk_features)}. Immediate invasive strategy RECOMMENDED (< 2 hours)",
            guideline_key="esc_nste_acs_2020",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.PROCEDURE,
            urgency=Urgency.EMERGENT,
            section="4.3",
        ))
    
    # Additional risk markers
    if patient.labs and patient.labs.nt_pro_bnp and patient.labs.nt_pro_bnp > 1000:
        rec_set.add(guideline_recommendation(
            action=f"Elevated NT-proBNP ({patient.labs.nt_pro_bnp} pg/mL) - high risk marker",
            guideline_key="esc_nste_acs_2020",
            evidence_class=EvidenceClass.IIA,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.DIAGNOSTIC,
            section="4.2",
        ))
    
    return rec_set


def get_invasive_strategy_timing(
    risk_category: RiskCategory,
    has_very_high_risk_features: bool = False,
) -> RecommendationSet:
    """
    Get invasive strategy timing recommendations.
    
    Per ESC 2020 Section 4.3: Invasive strategy
    
    Args:
        risk_category: Patient risk category
        has_very_high_risk_features: Presence of very high-risk features
    
    Returns:
        RecommendationSet with timing recommendations
    """
    rec_set = RecommendationSet(
        title="Invasive Strategy Timing",
        primary_guideline="ESC NSTE-ACS 2020",
    )
    
    if has_very_high_risk_features:
        rec_set.add(guideline_recommendation(
            action="IMMEDIATE invasive strategy (< 2 hours) RECOMMENDED for very high-risk NSTE-ACS",
            guideline_key="esc_nste_acs_2020",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.PROCEDURE,
            urgency=Urgency.EMERGENT,
            section="4.3",
        ))
    
    elif risk_category == RiskCategory.VERY_HIGH:
        rec_set.add(guideline_recommendation(
            action="IMMEDIATE invasive strategy (< 2 hours) RECOMMENDED for GRACE score ≥ 140",
            guideline_key="esc_nste_acs_2020",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PROCEDURE,
            urgency=Urgency.EMERGENT,
            section="4.3",
        ))
    
    elif risk_category == RiskCategory.HIGH:
        rec_set.add(guideline_recommendation(
            action="EARLY invasive strategy (< 24 hours) RECOMMENDED for high-risk NSTE-ACS",
            guideline_key="esc_nste_acs_2020",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PROCEDURE,
            urgency=Urgency.SOON,
            section="4.3",
        ))
    
    elif risk_category == RiskCategory.INTERMEDIATE:
        rec_set.add(guideline_recommendation(
            action="INVASIVE strategy (< 72 hours) RECOMMENDED for intermediate-risk NSTE-ACS",
            guideline_key="esc_nste_acs_2020",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PROCEDURE,
            section="4.3",
        ))
    
    else:  # Low risk
        rec_set.add(guideline_recommendation(
            action="SELECTIVE invasive strategy. Consider non-invasive testing first. Invasive strategy if recurrent symptoms or positive stress test.",
            guideline_key="esc_nste_acs_2020",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PROCEDURE,
            section="4.3",
        ))
    
    return rec_set