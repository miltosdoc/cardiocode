"""
Secondary Prevention after NSTE-ACS - ESC 2020 Guidelines.

Implements long-term management:
- Lipid-lowering therapy
- Blood pressure management
- Cardiac rehabilitation
- Risk factor modification
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


def get_secondary_prevention(patient: "Patient") -> RecommendationSet:
    """
    Secondary prevention recommendations post-ACS.
    
    Per ESC 2020 Section 7: Long-term management
    """
    rec_set = RecommendationSet(
        title="Secondary Prevention After NSTE-ACS",
        primary_guideline="ESC NSTE-ACS 2020",
    )
    
    # High-intensity statin
    rec_set.add(guideline_recommendation(
        action="High-intensity statin (atorvastatin 40-80mg or rosuvastatin 20-40mg) for ALL ACS patients regardless of baseline LDL",
        guideline_key="esc_acs_2020",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.A,
        category=RecommendationCategory.PHARMACOTHERAPY,
        section="7.2",
        studies=["PROVE IT-TIMI 22", "MIRACL"],
        rationale="LDL target < 55 mg/dL AND >= 50% reduction from baseline",
    ))
    
    # Ezetimibe if LDL not at goal
    rec_set.add(guideline_recommendation(
        action="Add ezetimibe 10mg if LDL not at goal on maximal statin",
        guideline_key="esc_acs_2020",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.B,
        category=RecommendationCategory.PHARMACOTHERAPY,
        section="7.2",
        studies=["IMPROVE-IT"],
    ))
    
    # PCSK9 inhibitor
    rec_set.add(guideline_recommendation(
        action="Add PCSK9 inhibitor if LDL still not at goal despite statin + ezetimibe",
        guideline_key="esc_acs_2020",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.A,
        category=RecommendationCategory.PHARMACOTHERAPY,
        section="7.2",
        studies=["FOURIER", "ODYSSEY OUTCOMES"],
    ))
    
    # Beta-blocker
    rec_set.add(guideline_recommendation(
        action="Beta-blocker should be considered in all ACS patients without contraindications",
        guideline_key="esc_acs_2020",
        evidence_class=EvidenceClass.IIA,
        evidence_level=EvidenceLevel.B,
        category=RecommendationCategory.PHARMACOTHERAPY,
        section="7.3",
    ))
    
    if patient.lvef and patient.lvef <= 40:
        rec_set.add(guideline_recommendation(
            action="Beta-blocker RECOMMENDED for LVEF <= 40% post-ACS (Class I)",
            guideline_key="esc_acs_2020",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.A,
            category=RecommendationCategory.PHARMACOTHERAPY,
            section="7.3",
            studies=["CAPRICORN"],
        ))
    
    # ACEi/ARB
    rec_set.add(guideline_recommendation(
        action="ACEi (or ARB if intolerant) recommended for ACS with LVEF <= 40%, diabetes, hypertension, or CKD",
        guideline_key="esc_acs_2020",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.A,
        category=RecommendationCategory.PHARMACOTHERAPY,
        section="7.3",
        studies=["HOPE", "EUROPA", "VALIANT"],
    ))
    
    # Cardiac rehabilitation
    rec_set.add(guideline_recommendation(
        action="Cardiac rehabilitation RECOMMENDED for all ACS patients",
        guideline_key="esc_acs_2020",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.A,
        category=RecommendationCategory.LIFESTYLE,
        section="7.5",
        rationale="Reduces mortality and improves quality of life",
    ))
    
    # Smoking cessation
    rec_set.add(guideline_recommendation(
        action="Smoking cessation with behavioral support and pharmacotherapy",
        guideline_key="esc_acs_2020",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.A,
        category=RecommendationCategory.LIFESTYLE,
        section="7.5",
    ))
    
    # Diabetes management
    if patient.has_diabetes:
        rec_set.add(guideline_recommendation(
            action="SGLT2 inhibitor or GLP-1 RA with proven CV benefit recommended for diabetic ACS patients",
            guideline_key="esc_acs_2020",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.A,
            category=RecommendationCategory.PHARMACOTHERAPY,
            section="7.4",
            studies=["EMPA-REG OUTCOME", "LEADER", "DECLARE-TIMI 58"],
        ))
    
    # Influenza vaccination
    rec_set.add(guideline_recommendation(
        action="Annual influenza vaccination for all ACS patients",
        guideline_key="esc_acs_2020",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.B,
        category=RecommendationCategory.LIFESTYLE,
        section="7.5",
    ))
    
    return rec_set
