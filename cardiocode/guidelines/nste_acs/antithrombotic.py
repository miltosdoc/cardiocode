"""
NSTE-ACS Antithrombotic Therapy - ESC 2020 Guidelines.

Implements:
- Antiplatelet therapy (P2Y12 selection)
- Anticoagulation therapy
- DAPT duration
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


def get_antiplatelet_therapy(
    patient: "Patient",
    invasive_strategy: bool = True,
    pci_performed: bool = False,
    stent_type: Optional[str] = None,
) -> RecommendationSet:
    """
    Get antiplatelet therapy recommendations for NSTE-ACS.
    
    Per ESC 2020 Section 5.1: Antiplatelet therapy
    
    Key points:
    - Aspirin + P2Y12 inhibitor (DAPT) for all NSTE-ACS
    - Ticagrelor or prasugrel preferred over clopidogrel
    - Loading doses given early
    
    Args:
        patient: NSTE-ACS patient
        invasive_strategy: Whether invasive strategy planned
        pci_performed: Whether PCI performed
        stent_type: Type of stent if PCI performed
    
    Returns:
        RecommendationSet with antiplatelet recommendations
    """
    rec_set = RecommendationSet(
        title="NSTE-ACS Antiplatelet Therapy",
        primary_guideline="ESC NSTE-ACS 2020",
    )
    
    has_prior_stroke = patient.has_prior_stroke_tia
    age = patient.age or 65
    high_bleeding_risk = patient.has_prior_bleeding or age > 75
    
    # Aspirin loading
    rec_set.add(guideline_recommendation(
        action="Aspirin 150-300 mg loading dose RECOMMENDED immediately, then 75-100 mg daily indefinitely",
        guideline_key="esc_nste_acs_2020",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.A,
        category=RecommendationCategory.PHARMACOTHERAPY,
        urgency=Urgency.URGENT,
        section="5.1",
    ))
    
    # P2Y12 inhibitor selection
    if invasive_strategy or pci_performed:
        if high_bleeding_risk or has_prior_stroke:
            rec_set.add(guideline_recommendation(
                action="Clopidogrel 600 mg loading dose RECOMMENDED (preferred over ticagrelor/prasugrel in high bleeding risk or prior stroke)",
                guideline_key="esc_nste_acs_2020",
                evidence_class=EvidenceClass.I,
                evidence_level=EvidenceLevel.B,
                category=RecommendationCategory.PHARMACOTHERAPY,
                urgency=Urgency.URGENT,
                section="5.1",
                studies=["PLATO (stroke subgroup)", "TRITON-TIMI 38 (stroke subgroup)"],
            ))
        else:
            rec_set.add(guideline_recommendation(
                action="Ticagrelor 180 mg loading dose RECOMMENDED over clopidogrel (unless contraindicated)",
                guideline_key="esc_nste_acs_2020",
                evidence_class=EvidenceClass.I,
                evidence_level=EvidenceLevel.A,
                category=RecommendationCategory.PHARMACOTHERAPY,
                urgency=Urgency.URGENT,
                section="5.1",
                studies=["PLATO"],
                rationale="Ticagrelor provides greater reduction in CV events than clopidogrel",
            ))
            
            rec_set.add(guideline_recommendation(
                action="Prasugrel 60 mg loading dose RECOMMENDED if PCI performed and no prior stroke/TIA (age < 75, weight > 60kg)",
                guideline_key="esc_nste_acs_2020",
                evidence_class=EvidenceClass.I,
                evidence_level=EvidenceLevel.B,
                category=RecommendationCategory.PHARMACOTHERAPY,
                urgency=Urgency.URGENT,
                section="5.1",
                studies=["TRITON-TIMI 38"],
                contraindications=["Prior stroke/TIA", "Age ≥ 75", "Weight ≤ 60kg"],
            ))
    else:
        # Conservative strategy
        rec_set.add(guideline_recommendation(
            action="Clopidogrel 600 mg loading dose RECOMMENDED for conservative strategy",
            guideline_key="esc_nste_acs_2020",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PHARMACOTHERAPY,
            urgency=Urgency.URGENT,
            section="5.1",
        ))
    
    # GPIIb/IIIa inhibitors
    if pci_performed:
        rec_set.add(guideline_recommendation(
            action="GPIIb/IIIa inhibitors (abciximab, eptifibatide, tirofiban) may be considered for bailout if thrombotic complications during PCI",
            guideline_key="esc_nste_acs_2020",
            evidence_class=EvidenceClass.IIB,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.PHARMACOTHERAPY,
            section="5.1",
            rationale="Routine upstream use not recommended",
        ))
    
    return rec_set


def get_anticoagulation_therapy(
    patient: "Patient",
    invasive_strategy: bool = True,
    pci_performed: bool = False,
) -> RecommendationSet:
    """
    Get anticoagulation therapy recommendations for NSTE-ACS.
    
    Per ESC 2020 Section 5.2: Anticoagulation
    
    Options:
    - UFH (unfractionated heparin)
    - LMWH (enoxaparin)
    - Fondaparinux
    - Bivalirudin (PCI only)
    
    Args:
        patient: NSTE-ACS patient
        invasive_strategy: Whether invasive strategy planned
        pci_performed: Whether PCI performed
    
    Returns:
        RecommendationSet with anticoagulation recommendations
    """
    rec_set = RecommendationSet(
        title="NSTE-ACS Anticoagulation Therapy",
        primary_guideline="ESC NSTE-ACS 2020",
    )
    
    has_ckd = patient.labs and patient.labs.egfr and patient.labs.egfr < 30
    has_prior_bleeding = patient.has_prior_bleeding
    
    # Fondaparinux preferred (unless contraindicated)
    if not has_ckd:
        rec_set.add(guideline_recommendation(
            action="Fondaparinux 2.5 mg SC daily RECOMMENDED over UFH/LMWH (unless contraindicated)",
            guideline_key="esc_nste_acs_2020",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PHARMACOTHERAPY,
            section="5.2",
            studies=["OASIS-5"],
            rationale="Lower bleeding risk than UFH/LMWH",
        ))
    else:
        rec_set.add(guideline_recommendation(
            action="Fondaparinux CONTRAINDICATED in severe CKD (eGFR < 30). Use UFH or LMWH with dose adjustment.",
            guideline_key="esc_nste_acs_2020",
            evidence_class=EvidenceClass.III,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.CONTRAINDICATION,
            section="5.2",
        ))
    
    # UFH alternative
    rec_set.add(guideline_recommendation(
        action="UFH (weight-adjusted) RECOMMENDED as alternative, especially if invasive strategy planned or high bleeding risk",
        guideline_key="esc_nste_acs_2020",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.B,
        category=RecommendationCategory.PHARMACOTHERAPY,
        section="5.2",
        rationale="Short half-life, easily reversible",
    ))
    
    # LMWH alternative
    if not has_ckd:
        rec_set.add(guideline_recommendation(
            action="Enoxaparin 1 mg/kg SC BID RECOMMENDED as alternative to UFH (dose adjust if eGFR 30-50)",
            guideline_key="esc_nste_acs_2020",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PHARMACOTHERAPY,
            section="5.2",
            studies=["EXTRACT-TIMI 25"],
        ))
    
    # Bivalirudin for PCI
    if pci_performed and has_prior_bleeding:
        rec_set.add(guideline_recommendation(
            action="Bivalirudin may be considered during PCI in patients with high bleeding risk",
            guideline_key="esc_nste_acs_2020",
            evidence_class=EvidenceClass.IIB,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PHARMACOTHERAPY,
            section="5.2",
            studies=["ACUITY", "BRIGHT"],
        ))
    
    # Duration
    rec_set.add(guideline_recommendation(
        action="Continue anticoagulation until PCI or discharge (whichever earlier). Stop after PCI if no ongoing indication.",
        guideline_key="esc_nste_acs_2020",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.C,
        category=RecommendationCategory.PHARMACOTHERAPY,
        section="5.2",
    ))
    
    return rec_set


def get_dapt_duration(
    patient: "Patient",
    pci_performed: bool = False,
    stent_type: str = "des",
    high_bleeding_risk: bool = False,
) -> RecommendationSet:
    """
    Get DAPT duration recommendations for NSTE-ACS.
    
    Per ESC 2020 Section 5.3: DAPT duration
    
    Standard: 12 months DAPT
    Shorter: 1-6 months if high bleeding risk
    Longer: >12 months if high ischemic risk without bleeding
    
    Args:
        patient: NSTE-ACS patient
        pci_performed: Whether PCI performed
        stent_type: Type of stent
        high_bleeding_risk: High bleeding risk assessment
    
    Returns:
        RecommendationSet with DAPT duration recommendations
    """
    rec_set = RecommendationSet(
        title="NSTE-ACS DAPT Duration",
        primary_guideline="ESC NSTE-ACS 2020",
    )
    
    high_ischemic_risk = (
        patient.has_diabetes or
        (patient.labs and patient.labs.egfr and patient.labs.egfr < 60) or
        (patient.lvef and patient.lvef < 40)
    )
    
    if not pci_performed:
        rec_set.add(guideline_recommendation(
            action="Conservative strategy: Continue DAPT for 12 months unless contraindicated",
            guideline_key="esc_nste_acs_2020",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.A,
            category=RecommendationCategory.PHARMACOTHERAPY,
            section="5.3",
        ))
        return rec_set
    
    # Post-PCI recommendations
    if high_bleeding_risk:
        rec_set.add(guideline_recommendation(
            action="High bleeding risk: Short DAPT (1-3 months) followed by P2Y12 monotherapy RECOMMENDED",
            guideline_key="esc_nste_acs_2020",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.A,
            category=RecommendationCategory.PHARMACOTHERAPY,
            section="5.3",
            studies=["TWILIGHT", "STOPDAPT-2"],
        ))
    elif high_ischemic_risk:
        rec_set.add(guideline_recommendation(
            action="High ischemic risk without high bleeding risk: Extended DAPT (>12 months) may be considered",
            guideline_key="esc_nste_acs_2020",
            evidence_class=EvidenceClass.IIB,
            evidence_level=EvidenceLevel.A,
            category=RecommendationCategory.PHARMACOTHERAPY,
            section="5.3",
            studies=["PEGASUS-TIMI 54", "DAPT trial"],
        ))
    else:
        rec_set.add(guideline_recommendation(
            action="Standard DAPT duration: 12 months RECOMMENDED",
            guideline_key="esc_nste_acs_2020",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.A,
            category=RecommendationCategory.PHARMACOTHERAPY,
            section="5.3",
        ))
    
    return rec_set