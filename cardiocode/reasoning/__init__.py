"""
CardioCode Reasoning and Synthesis Layer.

Handles:
- Clinical reasoning when guidelines don't directly apply
- Synthesis from multiple guidelines
- Uncertainty quantification
- Transparent flagging of non-guideline recommendations
"""

from cardiocode.reasoning.synthesizer import ClinicalReasoner, ReasoningResult
from cardiocode.reasoning.uncertainty import ConfidenceLevel, UncertaintyAssessment

__all__ = [
    "ClinicalReasoner",
    "ReasoningResult",
    "ConfidenceLevel",
    "UncertaintyAssessment",
]
