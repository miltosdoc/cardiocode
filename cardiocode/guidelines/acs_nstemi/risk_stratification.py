"""
NSTE-ACS Risk Stratification - ESC 2020 Guidelines.

Implements risk stratification and invasive timing:
- GRACE score integration
- Risk categories
- Invasive strategy timing
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
from cardiocode.knowledge.scores import grace_score, ScoreResult


@dataclass
class RiskStratification:
    """NSTE-ACS risk stratification result."""
    risk_category: str  # "very_high", "high", "intermediate", "low"
    grace_score: Optional[int] = None
    grace_result: Optional[ScoreResult] = None
    invasive_timing: str = ""  # "immediate", "early_24h", "within_72h", "selective"
    recommendations: List[Recommendation] = None
    
    def __post_init__(self):
        if self.recommendations is None:
            self.recommendations = []


def stratify_risk(patient: "Patient") -> RiskStratification:
    """
    Risk stratify NSTE-ACS patient.
    
    Per ESC 2020 Section 6: Risk stratification
    
    Categories:
    - Very high risk: Immediate invasive (<2h)
    - High risk: Early invasive (<24h)
    - Intermediate risk: Invasive (<72h)
    - Low risk: Selective invasive strategy
    
    Args:
        patient: Patient object
    
    Returns:
        RiskStratification with category and timing
    """
    recommendations = []
    
    # Check for very high risk criteria (immediate invasive)
    very_high_risk = False
    very_high_criteria = []
    
    # Hemodynamic instability / cardiogenic shock
    if patient.vitals and patient.vitals.systolic_bp and patient.vitals.systolic_bp < 90:
        very_high_risk = True
        very_high_criteria.append("Hemodynamic instability")
    
    # Ongoing chest pain despite medical therapy
    # (would need symptom assessment - proxy with NYHA/symptoms)
    
    # Life-threatening arrhythmias
    if patient.ecg:
        if patient.ecg.rhythm.value in ["ventricular_tachycardia", "ventricular_fibrillation"]:
            very_high_risk = True
            very_high_criteria.append("Life-threatening arrhythmia")
    
    # Mechanical complications
    # (would need echo findings)
    
    # Acute heart failure clearly related to ACS
    if patient.nyha_class and patient.nyha_class.value >= 3:
        very_high_criteria.append("Acute heart failure")
        very_high_risk = True
    
    # Recurrent or persistent ST changes
    if patient.ecg and patient.ecg.st_depression:
        very_high_criteria.append("Dynamic ST changes")
    
    if very_high_risk:
        recommendations.append(guideline_recommendation(
            action=f"VERY HIGH RISK: Immediate invasive strategy (<2 hours). Criteria: {', '.join(very_high_criteria)}",
            guideline_key="esc_acs_2020",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.PROCEDURE,
            urgency=Urgency.EMERGENT,
            section="6.3",
        ))
        return RiskStratification(
            risk_category="very_high",
            invasive_timing="immediate",
            recommendations=recommendations,
        )
    
    # Calculate GRACE score if data available
    grace_result = None
    if (patient.age and patient.vitals and patient.vitals.heart_rate and 
        patient.vitals.systolic_bp and patient.labs and patient.labs.creatinine):
        
        grace_result = grace_score(
            age=patient.age,
            heart_rate=patient.vitals.heart_rate,
            systolic_bp=patient.vitals.systolic_bp,
            creatinine=patient.labs.creatinine,
            killip_class=1,  # Default if not specified
            cardiac_arrest=False,
            st_deviation=bool(patient.ecg and (patient.ecg.st_depression or patient.ecg.st_elevation)),
            elevated_troponin=bool(patient.labs.troponin_t and patient.labs.troponin_t > 14),
        )
    
    # High risk criteria (early invasive <24h)
    high_risk = False
    high_criteria = []
    
    if grace_result and grace_result.score_value > 140:
        high_risk = True
        high_criteria.append(f"GRACE score {int(grace_result.score_value)} > 140")
    
    if patient.labs and patient.labs.troponin_t:
        # Significant troponin rise/fall
        if patient.labs.troponin_t > 52:  # Significantly elevated
            high_risk = True
            high_criteria.append("Significant troponin elevation")
    
    if patient.ecg and patient.ecg.st_depression:
        high_risk = True
        high_criteria.append("ST-segment depression")
    
    if high_risk:
        recommendations.append(guideline_recommendation(
            action=f"HIGH RISK: Early invasive strategy (<24 hours). Criteria: {', '.join(high_criteria)}",
            guideline_key="esc_acs_2020",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.A,
            category=RecommendationCategory.PROCEDURE,
            urgency=Urgency.URGENT,
            section="6.3",
            studies=["TIMACS", "VERDICT"],
        ))
        return RiskStratification(
            risk_category="high",
            grace_score=int(grace_result.score_value) if grace_result else None,
            grace_result=grace_result,
            invasive_timing="early_24h",
            recommendations=recommendations,
        )
    
    # Intermediate risk (invasive <72h)
    intermediate_risk = False
    if grace_result and grace_result.score_value > 109:
        intermediate_risk = True
    
    if patient.has_diabetes or patient.labs and patient.labs.egfr and patient.labs.egfr < 60:
        intermediate_risk = True
    
    if patient.lvef and patient.lvef < 40:
        intermediate_risk = True
    
    if intermediate_risk:
        recommendations.append(guideline_recommendation(
            action="INTERMEDIATE RISK: Invasive strategy within 72 hours",
            guideline_key="esc_acs_2020",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.A,
            category=RecommendationCategory.PROCEDURE,
            urgency=Urgency.SOON,
            section="6.3",
        ))
        return RiskStratification(
            risk_category="intermediate",
            grace_score=int(grace_result.score_value) if grace_result else None,
            grace_result=grace_result,
            invasive_timing="within_72h",
            recommendations=recommendations,
        )
    
    # Low risk - selective invasive
    recommendations.append(guideline_recommendation(
        action="LOW RISK: Selective invasive strategy. Non-invasive testing for inducible ischemia may be considered first.",
        guideline_key="esc_acs_2020",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.A,
        category=RecommendationCategory.PROCEDURE,
        section="6.3",
    ))
    
    return RiskStratification(
        risk_category="low",
        grace_score=int(grace_result.score_value) if grace_result else None,
        grace_result=grace_result,
        invasive_timing="selective",
        recommendations=recommendations,
    )


def get_invasive_timing(patient: "Patient") -> RecommendationSet:
    """
    Get invasive strategy timing recommendations.
    
    Wrapper around stratify_risk with additional context.
    """
    stratification = stratify_risk(patient)
    
    rec_set = RecommendationSet(
        title=f"NSTE-ACS Invasive Strategy - {stratification.risk_category.upper()} RISK",
        description=f"Recommended timing: {stratification.invasive_timing}",
        primary_guideline="ESC NSTE-ACS 2020",
    )
    
    for rec in stratification.recommendations:
        rec_set.add(rec)
    
    if stratification.grace_result:
        rec_set.description += f"\nGRACE Score: {stratification.grace_score}"
    
    return rec_set
