"""
Antithrombotic Therapy for NSTE-ACS - ESC 2020 Guidelines.

Implements antithrombotic recommendations:
- Antiplatelet therapy (DAPT)
- Parenteral anticoagulation
- Duration of therapy
- Special populations (AF, high bleeding risk)
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


def get_antithrombotic_strategy(patient: "Patient") -> RecommendationSet:
    """
    Get comprehensive antithrombotic strategy for NSTE-ACS.
    
    Per ESC 2020 Section 5: Antithrombotic therapy
    """
    rec_set = RecommendationSet(
        title="NSTE-ACS Antithrombotic Strategy",
        primary_guideline="ESC NSTE-ACS 2020",
    )
    
    # Aspirin - universal
    rec_set.add(guideline_recommendation(
        action="Aspirin loading 150-300mg (non-enteric) followed by 75-100mg daily",
        guideline_key="esc_acs_2020",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.A,
        category=RecommendationCategory.PHARMACOTHERAPY,
        urgency=Urgency.EMERGENT,
        section="5.2",
    ))
    
    # P2Y12 inhibitor selection
    on_oac = patient.on_anticoagulation
    
    if not on_oac:
        # Standard DAPT
        rec_set.add(guideline_recommendation(
            action="Ticagrelor 180mg load then 90mg BID RECOMMENDED in addition to aspirin, regardless of initial strategy",
            guideline_key="esc_acs_2020",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PHARMACOTHERAPY,
            urgency=Urgency.URGENT,
            section="5.2",
            studies=["PLATO"],
            rationale="Ticagrelor superior to clopidogrel for MACE reduction",
            contraindications=["Prior ICH", "On strong CYP3A4 inhibitor", "Moderate-severe hepatic impairment"],
        ))
        
        rec_set.add(guideline_recommendation(
            action="Prasugrel 60mg load then 10mg daily is alternative for PCI-managed patients (not used pre-cath)",
            guideline_key="esc_acs_2020",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PHARMACOTHERAPY,
            section="5.2",
            studies=["TRITON-TIMI 38", "ACCOAST (pretreatment harmful)"],
            contraindications=["Prior stroke/TIA", "Age >= 75 (use 5mg)", "Weight < 60kg (use 5mg)"],
        ))
        
        rec_set.add(guideline_recommendation(
            action="Clopidogrel 300-600mg load then 75mg daily if ticagrelor/prasugrel contraindicated or unavailable",
            guideline_key="esc_acs_2020",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.A,
            category=RecommendationCategory.PHARMACOTHERAPY,
            section="5.2",
            studies=["CURE"],
        ))
    else:
        # ACS + AF requiring OAC
        rec_set.add(guideline_recommendation(
            action="TRIPLE THERAPY (OAC + aspirin + clopidogrel) for shortest necessary duration, then OAC + clopidogrel",
            guideline_key="esc_acs_2020",
            evidence_class=EvidenceClass.IIA,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PHARMACOTHERAPY,
            section="5.4",
            studies=["PIONEER AF-PCI", "RE-DUAL PCI", "AUGUSTUS"],
            rationale="Minimize triple therapy duration due to high bleeding risk",
        ))
        
        rec_set.add(guideline_recommendation(
            action="Use CLOPIDOGREL (not ticagrelor/prasugrel) with OAC to reduce bleeding risk",
            guideline_key="esc_acs_2020",
            evidence_class=EvidenceClass.IIA,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PHARMACOTHERAPY,
            section="5.4",
        ))
        
        rec_set.add(guideline_recommendation(
            action="Consider dropping aspirin after PCI (within days to 1 week) if low ischemic risk, continuing OAC + clopidogrel",
            guideline_key="esc_acs_2020",
            evidence_class=EvidenceClass.IIA,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PHARMACOTHERAPY,
            section="5.4",
            studies=["AUGUSTUS"],
        ))
    
    # Parenteral anticoagulation
    rec_set.add(guideline_recommendation(
        action="Fondaparinux 2.5mg SC daily RECOMMENDED (lowest bleeding risk)",
        guideline_key="esc_acs_2020",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.B,
        category=RecommendationCategory.PHARMACOTHERAPY,
        section="5.3",
        studies=["OASIS-5"],
        conditions=["Not for PCI (add UFH at time of procedure)", "CrCl >= 20 mL/min"],
    ))
    
    rec_set.add(guideline_recommendation(
        action="Enoxaparin 1mg/kg SC q12h is alternative. Use 1mg/kg q24h if CrCl 15-30 mL/min.",
        guideline_key="esc_acs_2020",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.B,
        category=RecommendationCategory.PHARMACOTHERAPY,
        section="5.3",
        studies=["SYNERGY"],
    ))
    
    rec_set.add(guideline_recommendation(
        action="UFH for PCI if fondaparinux used upstream (catheter thrombosis risk)",
        guideline_key="esc_acs_2020",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.B,
        category=RecommendationCategory.PHARMACOTHERAPY,
        section="5.3",
    ))
    
    return rec_set


def get_dual_antiplatelet_therapy(
    patient: "Patient",
    stent_type: Optional[str] = None,  # "DES", "BMS", "none"
    time_since_pci_months: Optional[int] = None,
) -> RecommendationSet:
    """
    DAPT duration recommendations.
    
    Per ESC 2020 Section 5.2: Duration of antiplatelet therapy
    """
    rec_set = RecommendationSet(
        title="DAPT Duration Recommendations",
        primary_guideline="ESC NSTE-ACS 2020",
    )
    
    # Standard recommendation: 12 months DAPT
    rec_set.add(guideline_recommendation(
        action="DAPT (aspirin + P2Y12 inhibitor) for 12 months after ACS, regardless of revascularization strategy",
        guideline_key="esc_acs_2020",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.A,
        category=RecommendationCategory.PHARMACOTHERAPY,
        section="5.2",
    ))
    
    # Shortened DAPT for high bleeding risk
    if patient.has_prior_bleeding or (patient.age and patient.age > 75):
        rec_set.add(guideline_recommendation(
            action="High bleeding risk: Consider shortened DAPT (3-6 months) followed by P2Y12 monotherapy",
            guideline_key="esc_acs_2020",
            evidence_class=EvidenceClass.IIA,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PHARMACOTHERAPY,
            section="5.2",
            studies=["TWILIGHT", "TICO", "STOPDAPT-2"],
        ))
    
    # Extended DAPT for high ischemic risk without high bleeding risk
    if patient.has_diabetes or patient.has_cad:
        rec_set.add(guideline_recommendation(
            action="High ischemic risk without high bleeding risk: Consider extended DAPT beyond 12 months or ticagrelor 60mg BID",
            guideline_key="esc_acs_2020",
            evidence_class=EvidenceClass.IIA,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PHARMACOTHERAPY,
            section="5.2",
            studies=["PEGASUS-TIMI 54"],
        ))
    
    return rec_set


def manage_anticoagulation(patient: "Patient") -> RecommendationSet:
    """
    Manage anticoagulation in NSTE-ACS.
    """
    rec_set = RecommendationSet(
        title="Anticoagulation Management in NSTE-ACS",
        primary_guideline="ESC NSTE-ACS 2020",
    )
    
    # Discontinue after PCI if no other indication
    rec_set.add(guideline_recommendation(
        action="Discontinue parenteral anticoagulation after PCI unless other indication (e.g., LV thrombus, AF)",
        guideline_key="esc_acs_2020",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.C,
        category=RecommendationCategory.PHARMACOTHERAPY,
        section="5.3",
    ))
    
    return rec_set
