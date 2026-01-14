"""
Prosthetic Valve Management - ESC 2021 VHD Guidelines.

Implements:
- Antithrombotic therapy for mechanical and bioprosthetic valves
- INR targets
- Prosthetic valve thrombosis management
"""

from __future__ import annotations
from typing import Optional, List, TYPE_CHECKING
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


class ProstheticValveType(Enum):
    """Type of prosthetic valve."""
    MECHANICAL = "mechanical"
    BIOPROSTHETIC = "bioprosthetic"


class ValvePosition(Enum):
    """Position of prosthetic valve."""
    AORTIC = "aortic"
    MITRAL = "mitral"
    TRICUSPID = "tricuspid"


def get_prosthetic_valve_anticoagulation(
    valve_type: ProstheticValveType,
    position: ValvePosition,
    has_af: bool = False,
    has_other_indication: bool = False,  # LV thrombus, hypercoagulable, etc.
    patient: Optional["Patient"] = None,
) -> RecommendationSet:
    """
    Get antithrombotic recommendations for prosthetic valves.
    
    Per ESC 2021 VHD Guidelines Section 11
    
    Key points:
    - Mechanical valves: Lifelong VKA (warfarin), DOACs contraindicated
    - Bioprosthetic valves: VKA or DOAC for 3 months post-op, then based on other indications
    
    Args:
        valve_type: Mechanical or bioprosthetic
        position: Valve position (aortic, mitral, tricuspid)
        has_af: Does patient have atrial fibrillation
        has_other_indication: Other indication for anticoagulation
        patient: Optional patient object for additional context
    
    Returns:
        RecommendationSet with anticoagulation recommendations
    """
    rec_set = RecommendationSet(
        title=f"Antithrombotic Therapy for {valve_type.value.title()} Valve ({position.value.title()} position)",
        primary_guideline="ESC VHD 2021",
    )
    
    if valve_type == ProstheticValveType.MECHANICAL:
        # MECHANICAL VALVE - VKA mandatory, DOACs contraindicated
        rec_set.add(guideline_recommendation(
            action="WARFARIN (VKA) is MANDATORY for ALL mechanical heart valves. DOACs are CONTRAINDICATED.",
            guideline_key="esc_vhd_2021",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PHARMACOTHERAPY,
            section="11.2",
            studies=["RE-ALIGN (dabigatran harmful in mechanical valves)"],
            contraindications=["All DOACs (apixaban, rivaroxaban, dabigatran, edoxaban)"],
        ))
        
        # INR target based on valve type and position
        if position == ValvePosition.AORTIC:
            rec_set.add(guideline_recommendation(
                action="Mechanical AORTIC valve: Target INR 2.5 (range 2.0-3.0) for newer-generation bileaflet valves. Higher target (3.0, range 2.5-3.5) for older valves or additional risk factors.",
                guideline_key="esc_vhd_2021",
                evidence_class=EvidenceClass.I,
                evidence_level=EvidenceLevel.B,
                category=RecommendationCategory.PHARMACOTHERAPY,
                section="11.2",
            ))
        else:
            rec_set.add(guideline_recommendation(
                action="Mechanical MITRAL valve: Target INR 3.0 (range 2.5-3.5). Mitral position has higher thrombogenicity.",
                guideline_key="esc_vhd_2021",
                evidence_class=EvidenceClass.I,
                evidence_level=EvidenceLevel.B,
                category=RecommendationCategory.PHARMACOTHERAPY,
                section="11.2",
            ))
        
        # Consider adding aspirin
        rec_set.add(guideline_recommendation(
            action="Low-dose aspirin (75-100mg) SHOULD BE CONSIDERED in addition to VKA if atherosclerotic disease or after thromboembolism despite adequate INR",
            guideline_key="esc_vhd_2021",
            evidence_class=EvidenceClass.IIA,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.PHARMACOTHERAPY,
            section="11.2",
        ))
    
    else:
        # BIOPROSTHETIC VALVE
        rec_set.add(guideline_recommendation(
            action="Bioprosthetic valve: Anticoagulation (VKA or DOAC) SHOULD BE CONSIDERED for first 3 months after surgical implantation",
            guideline_key="esc_vhd_2021",
            evidence_class=EvidenceClass.IIA,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PHARMACOTHERAPY,
            section="11.2",
        ))
        
        if has_af:
            rec_set.add(guideline_recommendation(
                action="Bioprosthetic valve with AF: Long-term anticoagulation indicated. DOAC may be used if no other indication for VKA.",
                guideline_key="esc_vhd_2021",
                evidence_class=EvidenceClass.IIA,
                evidence_level=EvidenceLevel.B,
                category=RecommendationCategory.PHARMACOTHERAPY,
                section="11.2",
                studies=["RIVER (rivaroxaban in bioprosthetic + AF)"],
            ))
        else:
            rec_set.add(guideline_recommendation(
                action="Bioprosthetic valve without AF: After 3 months, single antiplatelet (aspirin 75-100mg) or no antithrombotic therapy",
                guideline_key="esc_vhd_2021",
                evidence_class=EvidenceClass.IIA,
                evidence_level=EvidenceLevel.B,
                category=RecommendationCategory.PHARMACOTHERAPY,
                section="11.2",
            ))
        
        # TAVI-specific
        rec_set.add(guideline_recommendation(
            action="After TAVI: Single antiplatelet therapy (aspirin or clopidogrel) lifelong recommended. DAPT or anticoagulation not routinely needed.",
            guideline_key="esc_vhd_2021",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.A,
            category=RecommendationCategory.PHARMACOTHERAPY,
            section="11.2",
            studies=["POPular TAVI"],
        ))
    
    # Self-monitoring recommendation
    rec_set.add(guideline_recommendation(
        action="Patient self-management of INR RECOMMENDED if trained and suitable",
        guideline_key="esc_vhd_2021",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.B,
        category=RecommendationCategory.MONITORING,
        section="11.2",
    ))
    
    return rec_set


def manage_prosthetic_valve_thrombosis(
    is_obstructive: bool,
    thrombus_size: Optional[str] = None,  # "small" (<10mm), "large" (>=10mm)
) -> RecommendationSet:
    """
    Management of prosthetic valve thrombosis.
    
    Per ESC 2021 VHD Guidelines Section 11.3
    
    Args:
        is_obstructive: Is the thrombosis causing valve obstruction
        thrombus_size: Size of thrombus if known
    
    Returns:
        RecommendationSet with management recommendations
    """
    rec_set = RecommendationSet(
        title="Prosthetic Valve Thrombosis Management",
        primary_guideline="ESC VHD 2021",
    )
    
    if is_obstructive:
        rec_set.add(guideline_recommendation(
            action="OBSTRUCTIVE prosthetic valve thrombosis: Urgent surgery RECOMMENDED if available and patient operable",
            guideline_key="esc_vhd_2021",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.PROCEDURE,
            urgency=Urgency.EMERGENT,
            section="11.3",
        ))
        
        rec_set.add(guideline_recommendation(
            action="Fibrinolysis may be considered if surgery not available, patient inoperable, or as bridge to surgery",
            guideline_key="esc_vhd_2021",
            evidence_class=EvidenceClass.IIA,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.PHARMACOTHERAPY,
            urgency=Urgency.EMERGENT,
            section="11.3",
            rationale="Higher risk of embolism and bleeding, but may be lifesaving",
        ))
    
    else:
        # Non-obstructive
        if thrombus_size == "small":
            rec_set.add(guideline_recommendation(
                action="Small non-obstructive thrombus (<10mm): Optimize anticoagulation (IV heparin or increase INR) with close follow-up imaging",
                guideline_key="esc_vhd_2021",
                evidence_class=EvidenceClass.IIA,
                evidence_level=EvidenceLevel.C,
                category=RecommendationCategory.PHARMACOTHERAPY,
                section="11.3",
            ))
        else:
            rec_set.add(guideline_recommendation(
                action="Large non-obstructive thrombus (>=10mm): Consider surgery, especially if recurrent embolism",
                guideline_key="esc_vhd_2021",
                evidence_class=EvidenceClass.IIA,
                evidence_level=EvidenceLevel.C,
                category=RecommendationCategory.PROCEDURE,
                section="11.3",
            ))
    
    # Always optimize anticoagulation
    rec_set.add(guideline_recommendation(
        action="Optimize anticoagulation: Ensure therapeutic INR, consider IV unfractionated heparin initially",
        guideline_key="esc_vhd_2021",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.C,
        category=RecommendationCategory.PHARMACOTHERAPY,
        section="11.3",
    ))
    
    return rec_set
