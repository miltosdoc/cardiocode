"""
CCS Antithrombotic Therapy - ESC 2019 Guidelines.

Implements:
- Antiplatelet therapy selection
- DAPT duration decisions
- Combination with anticoagulation
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


class DAPTDuration(Enum):
    """DAPT duration categories."""
    SHORT = "short"  # 1-3 months
    STANDARD = "standard"  # 6 months
    PROLONGED = "prolonged"  # 12+ months


@dataclass
class DAPTRecommendation:
    """DAPT duration recommendation."""
    duration_months: int
    duration_category: DAPTDuration
    p2y12_inhibitor: str  # "clopidogrel", "ticagrelor", "prasugrel"
    rationale: str
    can_shorten: bool
    can_extend: bool


def get_antiplatelet_therapy(
    patient: "Patient",
    post_pci: bool = False,
    stent_type: Optional[str] = None,  # "des", "bms", None
) -> RecommendationSet:
    """
    Get antiplatelet therapy recommendations for CCS.
    
    Per ESC 2019 Section 5.2.3
    
    Args:
        patient: Patient with CCS
        post_pci: Whether patient is post-PCI
        stent_type: Type of stent if applicable
    
    Returns:
        RecommendationSet with antiplatelet recommendations
    """
    rec_set = RecommendationSet(
        title="Antiplatelet Therapy for CCS",
        primary_guideline="ESC CCS 2019",
    )
    
    on_anticoagulation = patient.is_on_medication("anticoagulant") or patient.is_on_medication("warfarin") or patient.is_on_medication("doac")
    high_bleeding_risk = patient.has_prior_bleeding or (patient.age and patient.age > 80)
    
    if on_anticoagulation:
        # Triple/dual therapy considerations
        if post_pci:
            rec_set.add(guideline_recommendation(
                action="Post-PCI on OAC: Triple therapy (OAC + aspirin + clopidogrel) for 1 week, then dual therapy (OAC + clopidogrel) for up to 12 months",
                guideline_key="esc_ccs_2019",
                evidence_class=EvidenceClass.I,
                evidence_level=EvidenceLevel.B,
                category=RecommendationCategory.PHARMACOTHERAPY,
                section="5.2.3",
                studies=["AUGUSTUS", "ENTRUST-AF PCI"],
            ))
            
            if high_bleeding_risk:
                rec_set.add(guideline_recommendation(
                    action="High bleeding risk: Consider direct dual therapy (OAC + P2Y12) without aspirin",
                    guideline_key="esc_ccs_2019",
                    evidence_class=EvidenceClass.IIA,
                    evidence_level=EvidenceLevel.B,
                    category=RecommendationCategory.PHARMACOTHERAPY,
                    section="5.2.3",
                ))
        else:
            rec_set.add(guideline_recommendation(
                action="CCS on OAC (no recent PCI): Single antiplatelet NOT recommended in addition to OAC",
                guideline_key="esc_ccs_2019",
                evidence_class=EvidenceClass.III,
                evidence_level=EvidenceLevel.B,
                category=RecommendationCategory.PHARMACOTHERAPY,
                section="5.2.3",
            ))
        return rec_set
    
    # Not on anticoagulation
    rec_set.add(guideline_recommendation(
        action="Aspirin 75-100 mg daily RECOMMENDED for all CCS patients",
        guideline_key="esc_ccs_2019",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.A,
        category=RecommendationCategory.PHARMACOTHERAPY,
        section="5.2.3",
    ))
    
    # If aspirin intolerant
    rec_set.add(guideline_recommendation(
        action="Clopidogrel 75 mg daily recommended if aspirin intolerant",
        guideline_key="esc_ccs_2019",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.B,
        category=RecommendationCategory.PHARMACOTHERAPY,
        section="5.2.3",
        studies=["CAPRIE"],
    ))
    
    # COMPASS strategy - aspirin + rivaroxaban
    if not high_bleeding_risk and (patient.has_diabetes or patient.has_diagnosis("peripheral_arterial_disease") or patient.has_ckd):
        rec_set.add(guideline_recommendation(
            action="Adding low-dose rivaroxaban 2.5 mg BID to aspirin SHOULD BE CONSIDERED in high-risk CCS (diabetes, PAD, multivessel CAD)",
            guideline_key="esc_ccs_2019",
            evidence_class=EvidenceClass.IIA,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PHARMACOTHERAPY,
            section="5.2.3",
            studies=["COMPASS"],
            rationale="34% reduction in CV events, but increases bleeding",
        ))
    
    return rec_set


def get_dapt_duration(
    patient: "Patient",
    indication: str = "ccs_pci",  # "ccs_pci", "acs_pci", "cabg"
    stent_type: str = "des",
    months_since_event: Optional[int] = None,
) -> RecommendationSet:
    """
    Determine optimal DAPT duration after revascularization.
    
    Per ESC 2019 CCS and ESC 2020 NSTE-ACS Guidelines.
    
    Key factors:
    - Ischemic risk (ACS vs CCS, diabetes, complex PCI, multivessel disease)
    - Bleeding risk (age, prior bleeding, renal dysfunction, anemia)
    - Time since event
    
    Args:
        patient: Patient post-revascularization
        indication: Reason for revascularization
        stent_type: Type of stent
        months_since_event: Months since PCI/event
    
    Returns:
        RecommendationSet with DAPT duration recommendation
    """
    rec_set = RecommendationSet(
        title="DAPT Duration Recommendation",
        primary_guideline="ESC CCS 2019",
    )
    
    high_bleeding_risk = patient.has_prior_bleeding or (patient.age and patient.age > 75) or (patient.labs and patient.labs.hemoglobin and patient.labs.hemoglobin < 11)
    high_ischemic_risk = patient.has_diabetes or (patient.labs and patient.labs.egfr and patient.labs.egfr < 60)
    
    if indication == "ccs_pci":
        # Chronic coronary syndrome - elective PCI
        if high_bleeding_risk:
            rec_set.add(guideline_recommendation(
                action="High bleeding risk: Short DAPT (1-3 months) followed by P2Y12 monotherapy or aspirin monotherapy",
                guideline_key="esc_ccs_2019",
                evidence_class=EvidenceClass.IIA,
                evidence_level=EvidenceLevel.A,
                category=RecommendationCategory.PHARMACOTHERAPY,
                section="5.3.2",
                studies=["TWILIGHT", "STOPDAPT-2", "SMART-CHOICE"],
            ))
        else:
            rec_set.add(guideline_recommendation(
                action="Standard DAPT duration after elective PCI: 6 months (aspirin + clopidogrel)",
                guideline_key="esc_ccs_2019",
                evidence_class=EvidenceClass.I,
                evidence_level=EvidenceLevel.A,
                category=RecommendationCategory.PHARMACOTHERAPY,
                section="5.3.2",
            ))
            
            if high_ischemic_risk:
                rec_set.add(guideline_recommendation(
                    action="High ischemic risk without high bleeding risk: Extended DAPT beyond 6 months may be considered",
                    guideline_key="esc_ccs_2019",
                    evidence_class=EvidenceClass.IIB,
                    evidence_level=EvidenceLevel.A,
                    category=RecommendationCategory.PHARMACOTHERAPY,
                    section="5.3.2",
                    studies=["DAPT trial", "PEGASUS-TIMI 54"],
                ))
    
    elif indication == "acs_pci":
        # ACS - more potent P2Y12 and longer duration
        rec_set.add(guideline_recommendation(
            action="Post-ACS PCI: DAPT with ticagrelor or prasugrel for 12 months (over clopidogrel)",
            guideline_key="esc_nste_acs_2020",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.A,
            category=RecommendationCategory.PHARMACOTHERAPY,
            section="5.4",
            studies=["PLATO", "TRITON-TIMI 38"],
        ))
        
        if high_bleeding_risk:
            rec_set.add(guideline_recommendation(
                action="ACS with high bleeding risk: De-escalation to clopidogrel or shortened DAPT (3-6 months) may be considered",
                guideline_key="esc_nste_acs_2020",
                evidence_class=EvidenceClass.IIB,
                evidence_level=EvidenceLevel.B,
                category=RecommendationCategory.PHARMACOTHERAPY,
                section="5.4",
                studies=["TROPICAL-ACS", "POPular Genetics"],
            ))
    
    elif indication == "cabg":
        rec_set.add(guideline_recommendation(
            action="Post-CABG: Aspirin alone lifelong. DAPT if recent ACS or prior PCI with recent stent.",
            guideline_key="esc_ccs_2019",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.A,
            category=RecommendationCategory.PHARMACOTHERAPY,
            section="5.3.3",
        ))
    
    # P2Y12 monotherapy option
    rec_set.add(guideline_recommendation(
        action="After DAPT completion: P2Y12 inhibitor monotherapy (clopidogrel or ticagrelor) may be considered as alternative to aspirin",
        guideline_key="esc_ccs_2019",
        evidence_class=EvidenceClass.IIB,
        evidence_level=EvidenceLevel.A,
        category=RecommendationCategory.PHARMACOTHERAPY,
        section="5.3.2",
        studies=["HOST-EXAM", "TWILIGHT"],
    ))
    
    return rec_set
