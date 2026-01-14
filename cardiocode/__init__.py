"""
CardioCode - ESC Cardiology Guidelines as Executable Code

A knowledge framework that encodes ESC clinical guidelines as Python code,
providing evidence-backed recommendations with full provenance tracking.

Usage:
    from cardiocode import Patient, get_recommendation
    from cardiocode.guidelines import heart_failure, atrial_fibrillation

    patient = Patient(age=72, sex="male", lvef=35, ...)
    recommendations = heart_failure.get_treatment_recommendations(patient)

Every recommendation includes:
    - Evidence class (I, IIa, IIb, III)
    - Evidence level (A, B, C)
    - Source guideline and page reference
    - Original study citations
    - Synthesis flag when extrapolating beyond explicit guidelines

Author: CardioCode Framework
Version: 1.0.0
"""

__version__ = "1.0.0"

from cardiocode.core.types import Patient, Diagnosis, Medication
from cardiocode.core.evidence import EvidenceClass, EvidenceLevel, SourceType
from cardiocode.core.recommendation import Recommendation, RecommendationSet
from cardiocode.knowledge.scores import (
    cha2ds2_vasc,
    has_bled,
    nyha_class,
    grace_score,
    euro_score_ii,
)
from cardiocode.reasoning.synthesizer import ClinicalReasoner

__all__ = [
    "Patient",
    "Diagnosis", 
    "Medication",
    "Recommendation",
    "RecommendationSet",
    "EvidenceClass",
    "EvidenceLevel",
    "SourceType",
    "cha2ds2_vasc",
    "has_bled",
    "nyha_class",
    "grace_score",
    "euro_score_ii",
    "ClinicalReasoner",
]
