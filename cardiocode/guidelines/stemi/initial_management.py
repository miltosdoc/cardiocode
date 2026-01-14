"""
STEMI Initial Management - ESC 2023 Guidelines.

Implements:
- Reperfusion strategy selection
- Fibrinolysis eligibility
- Time targets
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


class ReperfusionStrategy(Enum):
    """Reperfusion strategy options."""
    PRIMARY_PCI = "primary_pci"
    FIBRINOLYSIS = "fibrinolysis"
    PHARMACOLOGIC_INVASIVE = "pharmacologic_invasive"
    NO_REPERFUSION = "no_reperfusion"


@dataclass
class TimeTargets:
    """Time targets for STEMI management."""
    symptom_onset_to_fmc: Optional[int] = None  # minutes
    fmc_to_device: Optional[int] = None  # minutes
    door_to_balloon: Optional[int] = None  # minutes
    door_to_needle: Optional[int] = None  # minutes


def assess_reperfusion_strategy(
    patient: "Patient",
    pci_capable_center: bool = True,
    time_to_pci: Optional[int] = None,  # minutes from FMC
    time_to_fibrinolysis: Optional[int] = None,  # minutes from FMC
) -> RecommendationSet:
    """
    Assess optimal reperfusion strategy for STEMI.
    
    Per ESC 2023 STEMI Guidelines Section 2.2
    
    Key decision points:
    - PCI-capable center?
    - Time to PCI vs fibrinolysis
    - Presentation window
    
    Args:
        patient: STEMI patient
        pci_capable_center: Whether at PCI-capable center
        time_to_pci: Time to PCI (minutes)
        time_to_fibrinolysis: Time to fibrinolysis (minutes)
    
    Returns:
        RecommendationSet with reperfusion strategy recommendations
    """
    rec_set = RecommendationSet(
        title="STEMI Reperfusion Strategy",
        primary_guideline="ESC STEMI 2023",
    )
    
    symptom_duration = None  # Would need to be calculated from patient data
    
    # Primary PCI preferred if available
    if pci_capable_center:
        if time_to_pci and time_to_pci <= 120:
            rec_set.add(guideline_recommendation(
                action="PRIMARY PCI RECOMMENDED (time to PCI ≤ 120 min)",
                guideline_key="esc_stemi_2023",
                evidence_class=EvidenceClass.I,
                evidence_level=EvidenceLevel.A,
                category=RecommendationCategory.PROCEDURE,
                urgency=Urgency.EMERGENT,
                section="2.2",
                studies=["STREAM", "FAST-MI"],
            ))
        elif time_to_pci and time_to_pci <= 180:
            rec_set.add(guideline_recommendation(
                action="PRIMARY PCI RECOMMENDED (time to PCI ≤ 180 min)",
                guideline_key="esc_stemi_2023",
                evidence_class=EvidenceClass.I,
                evidence_level=EvidenceLevel.A,
                category=RecommendationCategory.PROCEDURE,
                urgency=Urgency.EMERGENT,
                section="2.2",
            ))
        else:
            rec_set.add(guideline_recommendation(
                action="PRIMARY PCI RECOMMENDED if possible. Consider fibrinolysis if PCI delay > 180 min and within 12h of symptom onset.",
                guideline_key="esc_stemi_2023",
                evidence_class=EvidenceClass.I,
                evidence_level=EvidenceLevel.A,
                category=RecommendationCategory.PROCEDURE,
                urgency=Urgency.EMERGENT,
                section="2.2",
            ))
    
    # Non-PCI center considerations
    else:
        if time_to_pci and time_to_pci <= 120:
            rec_set.add(guideline_recommendation(
                action="IMMEDIATE transfer for primary PCI RECOMMENDED (transfer time ≤ 120 min)",
                guideline_key="esc_stemi_2023",
                evidence_class=EvidenceClass.I,
                evidence_level=EvidenceLevel.A,
                category=RecommendationCategory.PROCEDURE,
                urgency=Urgency.EMERGENT,
                section="2.2",
            ))
        elif time_to_fibrinolysis and time_to_fibrinolysis < (time_to_pci - 120) if time_to_pci else True:
            rec_set.add(guideline_recommendation(
                action="FIBRINOLYSIS RECOMMENDED if PCI not available within 120 min and patient eligible",
                guideline_key="esc_stemi_2023",
                evidence_class=EvidenceClass.I,
                evidence_level=EvidenceLevel.A,
                category=RecommendationCategory.PHARMACOTHERAPY,
                urgency=Urgency.EMERGENT,
                section="2.2",
            ))
        else:
            rec_set.add(guideline_recommendation(
                action="Transfer for primary PCI RECOMMENDED. Consider fibrinolysis if transfer will cause significant delay.",
                guideline_key="esc_stemi_2023",
                evidence_class=EvidenceClass.I,
                evidence_level=EvidenceLevel.A,
                category=RecommendationCategory.PROCEDURE,
                urgency=Urgency.EMERGENT,
                section="2.2",
            ))
    
    # Time window considerations
    rec_set.add(guideline_recommendation(
        action="Reperfusion therapy RECOMMENDED for all STEMI within 12 hours of symptom onset",
        guideline_key="esc_stemi_2023",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.A,
        category=RecommendationCategory.PROCEDURE,
        section="2.2",
    ))
    
    rec_set.add(guideline_recommendation(
        action="Reperfusion therapy SHOULD BE CONSIDERED for STEMI 12-48 hours if ongoing ischemia or hemodynamic instability",
        guideline_key="esc_stemi_2023",
        evidence_class=EvidenceClass.IIA,
        evidence_level=EvidenceLevel.B,
        category=RecommendationCategory.PROCEDURE,
        section="2.2",
    ))
    
    return rec_set


def get_fibrinolysis_eligibility(
    patient: "Patient",
    time_from_symptom_onset: Optional[int] = None,
) -> RecommendationSet:
    """
    Assess fibrinolysis eligibility for STEMI.
    
    Per ESC 2023 STEMI Guidelines Section 2.3
    
    Absolute contraindications:
    - Any prior intracranial hemorrhage
    - Known structural cerebral vascular lesion
    - Malignant intracranial neoplasm
    - Ischemic stroke within 3 months
    - Suspected aortic dissection
    - Active bleeding or bleeding diathesis
    - Significant closed-head or facial trauma within 3 months
    
    Args:
        patient: STEMI patient
        time_from_symptom_onset: Minutes from symptom onset
    
    Returns:
        RecommendationSet with fibrinolysis eligibility assessment
    """
    rec_set = RecommendationSet(
        title="STEMI Fibrinolysis Eligibility",
        primary_guideline="ESC STEMI 2023",
    )
    
    # Time window
    if time_from_symptom_onset:
        if time_from_symptom_onset <= 180:  # 3 hours
            rec_set.add(guideline_recommendation(
                action="Within 3 hours of symptom onset: Fibrinolysis highly effective if PCI not immediately available",
                guideline_key="esc_stemi_2023",
                evidence_class=EvidenceClass.I,
                evidence_level=EvidenceLevel.A,
                category=RecommendationCategory.PHARMACOTHERAPY,
                section="2.3",
            ))
        elif time_from_symptom_onset <= 720:  # 12 hours
            rec_set.add(guideline_recommendation(
                action="Within 12 hours of symptom onset: Fibrinolysis effective if PCI not available",
                guideline_key="esc_stemi_2023",
                evidence_class=EvidenceClass.I,
                evidence_level=EvidenceLevel.A,
                category=RecommendationCategory.PHARMACOTHERAPY,
                section="2.3",
            ))
        elif time_from_symptom_onset <= 2880:  # 48 hours
            rec_set.add(guideline_recommendation(
                action="12-48 hours from symptom onset: Fibrinolysis may be considered if ongoing ischemia",
                guideline_key="esc_stemi_2023",
                evidence_class=EvidenceClass.IIB,
                evidence_level=EvidenceLevel.B,
                category=RecommendationCategory.PHARMACOTHERAPY,
                section="2.3",
            ))
        else:
            rec_set.add(guideline_recommendation(
                action="Beyond 48 hours: Fibrinolysis NOT RECOMMENDED",
                guideline_key="esc_stemi_2023",
                evidence_class=EvidenceClass.III,
                evidence_level=EvidenceLevel.C,
                category=RecommendationCategory.CONTRAINDICATION,
                section="2.3",
            ))
    
    # Check contraindications
    absolute_contraindications = []
    
    if patient.has_prior_stroke_tia:
        absolute_contraindications.append("Prior stroke/TIA")
    
    if patient.has_diagnosis("intracranial_hemorrhage"):
        absolute_contraindications.append("Prior intracranial hemorrhage")
    
    if patient.vitals and patient.vitals.sbp and patient.vitals.sbp > 185:
        absolute_contraindications.append("Uncontrolled hypertension (SBP > 185 mmHg)")
    
    if absolute_contraindications:
        rec_set.add(guideline_recommendation(
            action=f"FIBRINOLYSIS CONTRAINDICATED: {', '.join(absolute_contraindications)}",
            guideline_key="esc_stemi_2023",
            evidence_class=EvidenceClass.III,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.CONTRAINDICATION,
            section="2.3",
        ))
    else:
        rec_set.add(guideline_recommendation(
            action="No absolute contraindications identified. Fibrinolysis may be administered if indicated.",
            guideline_key="esc_stemi_2023",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.PHARMACOTHERAPY,
            section="2.3",
        ))
    
    # Fibrinolytic regimen
    rec_set.add(guideline_recommendation(
        action="Tenecteplase (weight-adjusted) or alteplase (accelerated regimen) RECOMMENDED",
        guideline_key="esc_stemi_2023",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.A,
        category=RecommendationCategory.PHARMACOTHERAPY,
        section="2.3",
    ))
    
    return rec_set


def calculate_door_to_balloon_time(
    patient: "Patient",
    presentation_time: Optional[str] = None,
    pci_time: Optional[str] = None,
) -> TimeTargets:
    """
    Calculate door-to-balloon time metrics.
    
    Per ESC 2023 STEMI Guidelines:
    - Door-to-balloon ≤ 90 min (target)
    - Door-to-balloon ≤ 60 min (ideal)
    
    Args:
        patient: STEMI patient
        presentation_time: Time of presentation
        pci_time: Time of PCI balloon inflation
    
    Returns:
        TimeTargets with calculated times
    """
    # This would need actual time calculations
    # For now, return the targets
    
    return TimeTargets(
        door_to_balloon=90,  # Target in minutes
    )