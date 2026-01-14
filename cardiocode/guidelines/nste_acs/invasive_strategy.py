"""
NSTE-ACS Invasive Strategy - ESC 2020 Guidelines.

Implements:
- Invasive strategy indications
- Revascularization approach selection
- Complete revascularization considerations
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
from .risk_stratification import RiskCategory


def assess_invasive_strategy_indication(
    patient: "Patient",
    risk_category: RiskCategory,
    has_very_high_risk_features: bool = False,
) -> RecommendationSet:
    """
    Assess indication for invasive strategy in NSTE-ACS.
    
    Per ESC 2020 Section 4.3: Invasive strategy
    
    Args:
        patient: NSTE-ACS patient
        risk_category: Risk category
        has_very_high_risk_features: Presence of very high-risk features
    
    Returns:
        RecommendationSet with invasive strategy recommendations
    """
    rec_set = RecommendationSet(
        title="Invasive Strategy Indication",
        primary_guideline="ESC NSTE-ACS 2020",
    )
    
    # Very high-risk features - immediate invasive
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
        return rec_set
    
    # Risk-based recommendations
    if risk_category == RiskCategory.VERY_HIGH:
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
    
    # Contraindications to invasive strategy
    rec_set.add(guideline_recommendation(
        action="Invasive strategy contraindicated if: severe comorbidities limiting life expectancy, patient refusal, or inability to undergo revascularization",
        guideline_key="esc_nste_acs_2020",
        evidence_class=EvidenceClass.III,
        evidence_level=EvidenceLevel.C,
        category=RecommendationCategory.CONTRAINDICATION,
        section="4.3",
    ))
    
    return rec_set


def choose_revascularization_approach(
    patient: "Patient",
    cad_extent: str = "unknown",  # "one_vessel", "two_vessel", "three_vessel", "left_main"
    syntax_score: Optional[int] = None,
) -> RecommendationSet:
    """
    Choose revascularization approach for NSTE-ACS.
    
    Per ESC 2020 Section 6: Revascularization
    
    Args:
        patient: NSTE-ACS patient
        cad_extent: Extent of CAD
        syntax_score: SYNTAX score
    
    Returns:
        RecommendationSet with revascularization recommendations
    """
    rec_set = RecommendationSet(
        title="Revascularization Approach Selection",
        primary_guideline="ESC NSTE-ACS 2020",
    )
    
    has_diabetes = patient.has_diabetes
    has_hfref = patient.lvef is not None and patient.lvef <= 40
    
    # Heart Team discussion for complex disease
    if cad_extent in ["three_vessel", "left_main"] or (syntax_score and syntax_score > 22):
        rec_set.add(guideline_recommendation(
            action="Heart Team discussion RECOMMENDED for complex CAD (3VD, left main, or high SYNTAX score)",
            guideline_key="esc_nste_acs_2020",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.REFERRAL,
            section="6.1",
        ))
    
    # Left main disease
    if cad_extent == "left_main":
        if syntax_score and syntax_score <= 32:
            rec_set.add(guideline_recommendation(
                action="Left main disease with low-intermediate SYNTAX: PCI or CABG both acceptable. Consider patient factors and preference.",
                guideline_key="esc_nste_acs_2020",
                evidence_class=EvidenceClass.I,
                evidence_level=EvidenceLevel.A,
                category=RecommendationCategory.PROCEDURE,
                section="6.1",
                studies=["EXCEL", "NOBLE"],
            ))
        else:
            rec_set.add(guideline_recommendation(
                action="Left main disease with high SYNTAX: CABG RECOMMENDED over PCI",
                guideline_key="esc_nste_acs_2020",
                evidence_class=EvidenceClass.I,
                evidence_level=EvidenceLevel.A,
                category=RecommendationCategory.PROCEDURE,
                section="6.1",
            ))
    
    # Three-vessel disease
    elif cad_extent == "three_vessel":
        if has_diabetes:
            rec_set.add(guideline_recommendation(
                action="Three-vessel disease with diabetes: CABG RECOMMENDED over PCI",
                guideline_key="esc_nste_acs_2020",
                evidence_class=EvidenceClass.I,
                evidence_level=EvidenceLevel.A,
                category=RecommendationCategory.PROCEDURE,
                section="6.1",
                studies=["FREEDOM"],
            ))
        elif has_hfref:
            rec_set.add(guideline_recommendation(
                action="Three-vessel disease with LV dysfunction: CABG RECOMMENDED for survival benefit",
                guideline_key="esc_nste_acs_2020",
                evidence_class=EvidenceClass.I,
                evidence_level=EvidenceLevel.B,
                category=RecommendationCategory.PROCEDURE,
                section="6.1",
            ))
        else:
            rec_set.add(guideline_recommendation(
                action="Three-vessel disease: Individualize decision. CABG preferred for complex anatomy or diabetes.",
                guideline_key="esc_nste_acs_2020",
                evidence_class=EvidenceClass.I,
                evidence_level=EvidenceLevel.A,
                category=RecommendationCategory.PROCEDURE,
                section="6.1",
            ))
    
    # One or two vessel disease
    elif cad_extent in ["one_vessel", "two_vessel"]:
        rec_set.add(guideline_recommendation(
            action="One or two-vessel disease: PCI RECOMMENDED for culprit lesion. Consider complete revascularization if feasible.",
            guideline_key="esc_nste_acs_2020",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.A,
            category=RecommendationCategory.PROCEDURE,
            section="6.1",
        ))
    
    # Complete revascularization
    rec_set.add(guideline_recommendation(
        action="Complete revascularization SHOULD BE CONSIDERED when feasible to reduce recurrent MI and repeat revascularization",
        guideline_key="esc_nste_acs_2020",
        evidence_class=EvidenceClass.IIA,
        evidence_level=EvidenceLevel.B,
        category=RecommendationCategory.PROCEDURE,
        section="6.1",
        studies=["COMPLETE", "CULPRIT"],
    ))
    
    # Culprit-only vs complete revascularization
    rec_set.add(guideline_recommendation(
        action="In hemodynamically unstable NSTE-ACS with multivessel disease: Culprit-only PCI RECOMMENDED initially. Consider staged complete revascularization.",
        guideline_key="esc_nste_acs_2020",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PROCEDURE,
            section="6.1",
            studies=["CULPRIT"],
        ))
    
    return rec_set