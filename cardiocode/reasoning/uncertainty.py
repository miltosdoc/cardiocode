"""
Uncertainty Quantification for CardioCode.

Provides tools for expressing and communicating uncertainty
in clinical recommendations.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Dict, Any


class ConfidenceLevel(Enum):
    """
    Confidence levels for recommendations.
    
    Used to communicate uncertainty to clinicians.
    """
    VERY_HIGH = "very_high"   # Direct Class I/Level A guideline
    HIGH = "high"             # Direct guideline, Class I-IIa
    MODERATE = "moderate"     # Guideline with caveats or Class IIb
    LOW = "low"               # Synthesis or extrapolation
    VERY_LOW = "very_low"     # Significant uncertainty
    
    @property
    def numeric_value(self) -> float:
        """Numeric confidence score (0-1)."""
        values = {
            "very_high": 0.95,
            "high": 0.85,
            "moderate": 0.70,
            "low": 0.50,
            "very_low": 0.30,
        }
        return values[self.value]
    
    @property
    def display_text(self) -> str:
        """Text for display to clinicians."""
        texts = {
            "very_high": "Very High Confidence - Strong guideline evidence",
            "high": "High Confidence - Good guideline evidence",
            "moderate": "Moderate Confidence - Limited or mixed evidence",
            "low": "Low Confidence - Synthesis or extrapolation",
            "very_low": "Very Low Confidence - Significant uncertainty",
        }
        return texts[self.value]
    
    @property
    def action_guidance(self) -> str:
        """Guidance on how to interpret this confidence level."""
        guidance = {
            "very_high": "Follow recommendation with high assurance",
            "high": "Follow recommendation with reasonable assurance",
            "moderate": "Consider recommendation but review patient-specific factors",
            "low": "Use clinical judgment; consider specialist input",
            "very_low": "Seek specialist consultation; individualized decision required",
        }
        return guidance[self.value]


class UncertaintySource(Enum):
    """Sources of uncertainty in recommendations."""
    EVIDENCE_GAP = "evidence_gap"                 # No direct study evidence
    POPULATION_MISMATCH = "population_mismatch"   # Patient differs from trial population
    CONFLICTING_EVIDENCE = "conflicting_evidence" # Studies disagree
    OUTDATED_EVIDENCE = "outdated_evidence"       # Guidelines may be superseded
    EXPERT_OPINION = "expert_opinion"             # Based on expert consensus, not RCTs
    MULTIPLE_GUIDELINES = "multiple_guidelines"   # Synthesized from multiple sources
    PATIENT_SPECIFIC = "patient_specific"         # Unique patient factors


@dataclass
class UncertaintyFactor:
    """A single factor contributing to uncertainty."""
    source: UncertaintySource
    description: str
    impact: float = 0.1  # How much this reduces confidence (0-1)
    mitigating_factors: List[str] = field(default_factory=list)


@dataclass
class UncertaintyAssessment:
    """
    Complete uncertainty assessment for a recommendation.
    
    Provides transparency about what we know, don't know,
    and why confidence may be limited.
    """
    base_confidence: ConfidenceLevel
    uncertainty_factors: List[UncertaintyFactor] = field(default_factory=list)
    
    # What we know
    supporting_evidence: List[str] = field(default_factory=list)
    
    # What we don't know
    evidence_gaps: List[str] = field(default_factory=list)
    
    # Patient-specific modifiers
    patient_factors_increasing_uncertainty: List[str] = field(default_factory=list)
    patient_factors_supporting_recommendation: List[str] = field(default_factory=list)
    
    @property
    def adjusted_confidence(self) -> float:
        """Calculate confidence after accounting for uncertainty factors."""
        base = self.base_confidence.numeric_value
        total_impact = sum(f.impact for f in self.uncertainty_factors)
        adjusted = max(0.1, base - total_impact)
        return round(adjusted, 2)
    
    @property
    def adjusted_confidence_level(self) -> ConfidenceLevel:
        """Get the confidence level after adjustment."""
        score = self.adjusted_confidence
        if score >= 0.9:
            return ConfidenceLevel.VERY_HIGH
        if score >= 0.75:
            return ConfidenceLevel.HIGH
        if score >= 0.55:
            return ConfidenceLevel.MODERATE
        if score >= 0.35:
            return ConfidenceLevel.LOW
        return ConfidenceLevel.VERY_LOW
    
    def format_for_display(self) -> str:
        """Format uncertainty assessment for clinical display."""
        lines = [
            "UNCERTAINTY ASSESSMENT",
            "=" * 40,
            f"Base confidence: {self.base_confidence.display_text}",
            f"Adjusted confidence: {self.adjusted_confidence:.0%} ({self.adjusted_confidence_level.value})",
            "",
        ]
        
        if self.supporting_evidence:
            lines.append("Supporting evidence:")
            for evidence in self.supporting_evidence:
                lines.append(f"  + {evidence}")
            lines.append("")
        
        if self.uncertainty_factors:
            lines.append("Uncertainty factors:")
            for factor in self.uncertainty_factors:
                lines.append(f"  - {factor.description} (impact: -{factor.impact:.0%})")
                for mitigator in factor.mitigating_factors:
                    lines.append(f"    * Mitigator: {mitigator}")
            lines.append("")
        
        if self.evidence_gaps:
            lines.append("Evidence gaps:")
            for gap in self.evidence_gaps:
                lines.append(f"  ? {gap}")
            lines.append("")
        
        if self.patient_factors_increasing_uncertainty:
            lines.append("Patient factors increasing uncertainty:")
            for factor in self.patient_factors_increasing_uncertainty:
                lines.append(f"  ! {factor}")
            lines.append("")
        
        lines.append(f"Recommended action: {self.adjusted_confidence_level.action_guidance}")
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "base_confidence": self.base_confidence.value,
            "base_confidence_score": self.base_confidence.numeric_value,
            "adjusted_confidence": self.adjusted_confidence,
            "adjusted_confidence_level": self.adjusted_confidence_level.value,
            "uncertainty_factors": [
                {
                    "source": f.source.value,
                    "description": f.description,
                    "impact": f.impact,
                }
                for f in self.uncertainty_factors
            ],
            "supporting_evidence": self.supporting_evidence,
            "evidence_gaps": self.evidence_gaps,
            "patient_factors_increasing_uncertainty": self.patient_factors_increasing_uncertainty,
            "patient_factors_supporting_recommendation": self.patient_factors_supporting_recommendation,
        }


def assess_evidence_quality(
    evidence_class: str,
    evidence_level: str,
    is_synthesis: bool = False,
    patient_excluded_population: bool = False,
    guideline_age_years: int = 0,
) -> UncertaintyAssessment:
    """
    Create an uncertainty assessment based on evidence characteristics.
    
    Args:
        evidence_class: "I", "IIa", "IIb", "III"
        evidence_level: "A", "B", "C"
        is_synthesis: Whether recommendation is synthesized
        patient_excluded_population: Whether patient would be excluded from trials
        guideline_age_years: Years since guideline publication
    
    Returns:
        UncertaintyAssessment object
    """
    # Determine base confidence from evidence grading
    if evidence_class == "I" and evidence_level == "A":
        base = ConfidenceLevel.VERY_HIGH
    elif evidence_class in ["I", "IIa"] and evidence_level in ["A", "B"]:
        base = ConfidenceLevel.HIGH
    elif evidence_class == "IIb" or evidence_level == "C":
        base = ConfidenceLevel.MODERATE
    elif evidence_class == "III":
        base = ConfidenceLevel.LOW
    else:
        base = ConfidenceLevel.MODERATE
    
    assessment = UncertaintyAssessment(base_confidence=base)
    
    # Add uncertainty factors
    if is_synthesis:
        assessment.uncertainty_factors.append(UncertaintyFactor(
            source=UncertaintySource.MULTIPLE_GUIDELINES,
            description="Recommendation synthesized from multiple sources",
            impact=0.15,
        ))
    
    if patient_excluded_population:
        assessment.uncertainty_factors.append(UncertaintyFactor(
            source=UncertaintySource.POPULATION_MISMATCH,
            description="Patient characteristics differ from trial populations",
            impact=0.20,
        ))
    
    if guideline_age_years > 3:
        assessment.uncertainty_factors.append(UncertaintyFactor(
            source=UncertaintySource.OUTDATED_EVIDENCE,
            description=f"Guideline is {guideline_age_years} years old; newer evidence may exist",
            impact=0.05 * (guideline_age_years - 3),
        ))
    
    if evidence_level == "C":
        assessment.uncertainty_factors.append(UncertaintyFactor(
            source=UncertaintySource.EXPERT_OPINION,
            description="Based primarily on expert consensus, not RCT data",
            impact=0.10,
        ))
        assessment.evidence_gaps.append("Limited randomized trial data")
    
    return assessment
