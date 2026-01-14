"""
PH Classification - ESC/ERS 2022 Guidelines.

Implements PH classification into Groups 1-5.
"""

from __future__ import annotations
from enum import Enum
from typing import Optional, List, TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from cardiocode.core.types import Patient


class PHGroup(Enum):
    """Pulmonary Hypertension clinical classification (Dana Point/Nice)."""
    GROUP_1 = "PAH"                    # Pulmonary Arterial Hypertension
    GROUP_2 = "PH_left_heart"          # PH due to left heart disease
    GROUP_3 = "PH_lung_disease"        # PH due to lung disease/hypoxia
    GROUP_4 = "CTEPH"                  # Chronic thromboembolic PH
    GROUP_5 = "PH_multifactorial"      # PH with unclear/multifactorial mechanisms
    UNKNOWN = "unknown"


@dataclass
class PHClassification:
    """Result of PH classification."""
    group: PHGroup
    subtype: Optional[str] = None
    confidence: str = "probable"  # "definite", "probable", "possible"
    rationale: List[str] = None
    
    def __post_init__(self):
        if self.rationale is None:
            self.rationale = []


def classify_ph(patient: "Patient") -> PHClassification:
    """
    Classify PH into hemodynamic groups.
    
    Per ESC/ERS 2022 Table 3: Updated classification
    
    Hemodynamic definitions:
    - Pre-capillary PH: mPAP > 20 mmHg, PAWP <= 15 mmHg, PVR > 2 WU
    - Post-capillary PH: mPAP > 20 mmHg, PAWP > 15 mmHg
    - Combined pre/post: mPAP > 20 mmHg, PAWP > 15 mmHg, PVR > 2 WU
    
    Args:
        patient: Patient with suspected PH
    
    Returns:
        PHClassification with group assignment
    """
    rationale = []
    
    # Check for left heart disease (Group 2)
    if patient.has_diagnosis("heart_failure"):
        if patient.lvef and patient.lvef < 50:
            rationale.append("Left heart disease with reduced EF present")
            return PHClassification(
                group=PHGroup.GROUP_2,
                subtype="HFrEF",
                confidence="probable",
                rationale=rationale,
            )
        else:
            rationale.append("Left heart disease with preserved EF")
            return PHClassification(
                group=PHGroup.GROUP_2,
                subtype="HFpEF",
                confidence="probable",
                rationale=rationale,
            )
    
    if patient.echo:
        if patient.echo.e_e_prime_ratio and patient.echo.e_e_prime_ratio > 14:
            rationale.append("Elevated E/e' suggests elevated LVEDP")
        if patient.echo.la_volume_index and patient.echo.la_volume_index > 34:
            rationale.append("LA dilation suggests left heart disease")
        
        if len(rationale) >= 2:
            return PHClassification(
                group=PHGroup.GROUP_2,
                subtype="left_heart_disease",
                confidence="probable",
                rationale=rationale,
            )
    
    # Check for lung disease (Group 3)
    if patient.has_diagnosis("copd") or patient.has_diagnosis("pulmonary_fibrosis"):
        rationale.append("Significant lung disease present")
        return PHClassification(
            group=PHGroup.GROUP_3,
            subtype="COPD" if patient.has_diagnosis("copd") else "ILD",
            confidence="probable",
            rationale=rationale,
        )
    
    # Check for CTEPH (Group 4)
    if patient.has_diagnosis("pulmonary_embolism"):
        rationale.append("History of pulmonary embolism - consider CTEPH")
        return PHClassification(
            group=PHGroup.GROUP_4,
            subtype="CTEPH",
            confidence="possible",
            rationale=rationale + ["Requires V/Q scan and RHC to confirm"],
        )
    
    # Default to possible PAH (Group 1) if no clear secondary cause
    rationale.append("No clear secondary cause identified")
    return PHClassification(
        group=PHGroup.GROUP_1,
        subtype="idiopathic_PAH",
        confidence="possible",
        rationale=rationale + ["Requires RHC and full workup to confirm PAH diagnosis"],
    )
