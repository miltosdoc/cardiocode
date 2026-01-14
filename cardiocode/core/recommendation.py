"""
Recommendation objects for CardioCode.

This module provides the core recommendation structure that all guideline
modules return. Every recommendation includes full evidence provenance
and synthesis flagging.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any, Callable
import json

from cardiocode.core.evidence import (
    Citation,
    EvidenceClass,
    EvidenceLevel,
    SourceType,
    create_citation,
)


class RecommendationCategory(Enum):
    """Categories of clinical recommendations."""
    DIAGNOSTIC = "diagnostic"           # Tests, imaging, procedures for diagnosis
    PHARMACOTHERAPY = "pharmacotherapy" # Medication recommendations
    DEVICE = "device"                   # Pacemaker, ICD, CRT, etc.
    PROCEDURE = "procedure"             # Interventions (PCI, CABG, ablation)
    LIFESTYLE = "lifestyle"             # Diet, exercise, smoking cessation
    MONITORING = "monitoring"           # Follow-up, testing frequency
    REFERRAL = "referral"              # Specialist consultation
    CONTRAINDICATION = "contraindication"  # What NOT to do
    

class Urgency(Enum):
    """Clinical urgency of recommendation."""
    EMERGENT = "emergent"       # Immediate action required
    URGENT = "urgent"           # Within hours to days
    SOON = "soon"               # Within days to weeks
    ROUTINE = "routine"         # Standard scheduling
    ELECTIVE = "elective"       # When convenient


@dataclass
class Recommendation:
    """
    A single clinical recommendation with full evidence provenance.
    
    This is the core output of all guideline queries. It includes:
    - The actual recommendation text
    - Evidence classification and source
    - Full citation trail
    - Synthesis/uncertainty flags
    
    Every recommendation MUST clearly indicate whether it comes directly
    from guidelines or is synthesized/extrapolated.
    """
    # Core recommendation
    action: str                                   # What to do
    rationale: Optional[str] = None               # Why (brief explanation)
    
    # Classification
    category: RecommendationCategory = RecommendationCategory.PHARMACOTHERAPY
    urgency: Urgency = Urgency.ROUTINE
    
    # Evidence (required for guideline-based recommendations)
    citation: Optional[Citation] = None
    source_type: SourceType = SourceType.GUIDELINE
    
    # When source is SYNTHESIS or EXTRAPOLATION
    synthesis_rationale: Optional[str] = None     # Explain the reasoning
    source_guidelines: List[str] = field(default_factory=list)  # Guidelines used
    confidence_score: Optional[float] = None      # 0.0 to 1.0
    
    # Additional context
    conditions: List[str] = field(default_factory=list)  # When this applies
    contraindications: List[str] = field(default_factory=list)  # When NOT to apply
    monitoring: Optional[str] = None              # What to monitor
    follow_up: Optional[str] = None               # Follow-up instructions
    
    # Alternatives
    alternatives: List[str] = field(default_factory=list)
    
    # Metadata
    generated_at: datetime = field(default_factory=datetime.now)
    guideline_version: Optional[str] = None
    
    def __post_init__(self):
        """Validate and compute derived fields."""
        # Ensure synthesis has rationale
        if self.source_type in [SourceType.SYNTHESIS, SourceType.EXTRAPOLATION]:
            if not self.synthesis_rationale:
                self.synthesis_rationale = "Derived from clinical reasoning"
            if self.confidence_score is None:
                self.confidence_score = self.source_type.confidence_modifier
    
    @property
    def is_guideline_based(self) -> bool:
        """Whether this recommendation comes directly from guidelines."""
        return self.source_type in [SourceType.GUIDELINE, SourceType.GUIDELINE_EXPERT]
    
    @property
    def requires_disclaimer(self) -> bool:
        """Whether this recommendation requires synthesis disclaimer."""
        return self.source_type.requires_disclaimer
    
    @property
    def evidence_class(self) -> Optional[EvidenceClass]:
        """Shortcut to evidence class."""
        return self.citation.evidence_class if self.citation else None
    
    @property
    def evidence_level(self) -> Optional[EvidenceLevel]:
        """Shortcut to evidence level."""
        return self.citation.evidence_level if self.citation else None
    
    def format_for_display(self) -> str:
        """
        Format recommendation for clinical display.
        
        This is the primary output format that will be shown to clinicians.
        It MUST clearly distinguish guideline-based from synthesized recommendations.
        """
        lines = []
        
        # Header with source type
        if self.is_guideline_based:
            lines.append("=" * 60)
            lines.append("SOURCE: GUIDELINE")
            if self.citation:
                lines.append(f"  {self.citation.format_short()}")
                if self.citation.page_number:
                    lines.append(f"  PDF: {self.citation.pdf_filename}, p.{self.citation.page_number}")
                if self.citation.supporting_studies:
                    studies = ", ".join(s.name for s in self.citation.supporting_studies)
                    lines.append(f"  Studies: {studies}")
        else:
            lines.append("=" * 60)
            lines.append(f"SOURCE: {self.source_type.value.upper()}")
            if self.confidence_score:
                lines.append(f"  Confidence: {self.confidence_score:.0%}")
            if self.source_guidelines:
                lines.append(f"  Based on: {', '.join(self.source_guidelines)}")
            lines.append("  " + "-" * 40)
            lines.append("  NOTE: This is NOT a direct guideline recommendation.")
            if self.synthesis_rationale:
                lines.append(f"  Reasoning: {self.synthesis_rationale}")
        
        lines.append("=" * 60)
        
        # Recommendation
        lines.append("")
        lines.append(f"RECOMMENDATION: {self.action}")
        
        if self.rationale:
            lines.append(f"  Rationale: {self.rationale}")
        
        # Category and urgency
        lines.append(f"  Category: {self.category.value}")
        lines.append(f"  Urgency: {self.urgency.value}")
        
        # Conditions
        if self.conditions:
            lines.append(f"  Applies when: {'; '.join(self.conditions)}")
        
        if self.contraindications:
            lines.append(f"  Avoid if: {'; '.join(self.contraindications)}")
        
        # Monitoring and follow-up
        if self.monitoring:
            lines.append(f"  Monitor: {self.monitoring}")
        
        if self.follow_up:
            lines.append(f"  Follow-up: {self.follow_up}")
        
        # Alternatives
        if self.alternatives:
            lines.append(f"  Alternatives: {'; '.join(self.alternatives)}")
        
        lines.append("")
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON/API output."""
        result = {
            "action": self.action,
            "rationale": self.rationale,
            "category": self.category.value,
            "urgency": self.urgency.value,
            "source_type": self.source_type.value,
            "is_guideline_based": self.is_guideline_based,
            "requires_disclaimer": self.requires_disclaimer,
        }
        
        if self.citation:
            result["citation"] = self.citation.to_dict()
        
        if not self.is_guideline_based:
            result["synthesis"] = {
                "rationale": self.synthesis_rationale,
                "source_guidelines": self.source_guidelines,
                "confidence_score": self.confidence_score,
            }
        
        if self.conditions:
            result["conditions"] = self.conditions
        if self.contraindications:
            result["contraindications"] = self.contraindications
        if self.monitoring:
            result["monitoring"] = self.monitoring
        if self.follow_up:
            result["follow_up"] = self.follow_up
        if self.alternatives:
            result["alternatives"] = self.alternatives
        
        return result
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2, default=str)


@dataclass
class RecommendationSet:
    """
    A collection of related recommendations.
    
    Used when a clinical query results in multiple recommendations
    (e.g., "What treatment for HFrEF?" returns ACEi + BB + MRA + SGLT2i).
    """
    title: str
    description: Optional[str] = None
    recommendations: List[Recommendation] = field(default_factory=list)
    
    # Query context
    patient_context: Optional[str] = None  # Brief patient description
    clinical_question: Optional[str] = None  # The question that was asked
    
    # Aggregated metadata
    primary_guideline: Optional[str] = None
    generated_at: datetime = field(default_factory=datetime.now)
    
    def add(self, recommendation: Recommendation) -> None:
        """Add a recommendation to the set."""
        self.recommendations.append(recommendation)
    
    def add_all(self, recommendations: List[Recommendation]) -> None:
        """Add multiple recommendations."""
        self.recommendations.extend(recommendations)
    
    @property
    def count(self) -> int:
        """Number of recommendations."""
        return len(self.recommendations)
    
    @property
    def has_synthesis(self) -> bool:
        """Whether any recommendation is synthesized (not direct guideline)."""
        return any(r.requires_disclaimer for r in self.recommendations)
    
    @property
    def guideline_based_count(self) -> int:
        """Count of guideline-based recommendations."""
        return sum(1 for r in self.recommendations if r.is_guideline_based)
    
    @property
    def synthesis_count(self) -> int:
        """Count of synthesized recommendations."""
        return sum(1 for r in self.recommendations if r.requires_disclaimer)
    
    def by_category(self, category: RecommendationCategory) -> List[Recommendation]:
        """Filter recommendations by category."""
        return [r for r in self.recommendations if r.category == category]
    
    def by_urgency(self, urgency: Urgency) -> List[Recommendation]:
        """Filter recommendations by urgency."""
        return [r for r in self.recommendations if r.urgency == urgency]
    
    def by_evidence_class(self, evidence_class: EvidenceClass) -> List[Recommendation]:
        """Filter recommendations by evidence class."""
        return [r for r in self.recommendations 
                if r.citation and r.citation.evidence_class == evidence_class]
    
    def format_for_display(self) -> str:
        """Format all recommendations for display."""
        lines = []
        
        # Header
        lines.append("#" * 60)
        lines.append(f"# {self.title}")
        lines.append("#" * 60)
        
        if self.description:
            lines.append(f"\n{self.description}\n")
        
        if self.clinical_question:
            lines.append(f"Question: {self.clinical_question}")
        
        if self.patient_context:
            lines.append(f"Patient: {self.patient_context}")
        
        # Summary
        lines.append(f"\nTotal recommendations: {self.count}")
        lines.append(f"  - Guideline-based: {self.guideline_based_count}")
        if self.synthesis_count > 0:
            lines.append(f"  - Synthesized: {self.synthesis_count} (see disclaimers)")
        
        lines.append("\n" + "-" * 60 + "\n")
        
        # Individual recommendations
        for i, rec in enumerate(self.recommendations, 1):
            lines.append(f"\n[{i}/{self.count}]")
            lines.append(rec.format_for_display())
        
        # Footer
        lines.append("\n" + "#" * 60)
        lines.append(f"Generated: {self.generated_at.strftime('%Y-%m-%d %H:%M')}")
        if self.primary_guideline:
            lines.append(f"Primary source: {self.primary_guideline}")
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "title": self.title,
            "description": self.description,
            "clinical_question": self.clinical_question,
            "patient_context": self.patient_context,
            "count": self.count,
            "guideline_based_count": self.guideline_based_count,
            "synthesis_count": self.synthesis_count,
            "has_synthesis_disclaimer": self.has_synthesis,
            "recommendations": [r.to_dict() for r in self.recommendations],
            "primary_guideline": self.primary_guideline,
            "generated_at": self.generated_at.isoformat(),
        }
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2, default=str)


# Convenience functions for creating recommendations

def guideline_recommendation(
    action: str,
    guideline_key: str,
    evidence_class: EvidenceClass,
    evidence_level: EvidenceLevel,
    category: RecommendationCategory = RecommendationCategory.PHARMACOTHERAPY,
    urgency: Urgency = Urgency.ROUTINE,
    page: Optional[int] = None,
    section: Optional[str] = None,
    studies: Optional[List[str]] = None,
    rationale: Optional[str] = None,
    monitoring: Optional[str] = None,
    conditions: Optional[List[str]] = None,
    contraindications: Optional[List[str]] = None,
) -> Recommendation:
    """
    Create a guideline-based recommendation.
    
    This is the primary factory function for creating recommendations
    that come directly from ESC guidelines.
    """
    citation = create_citation(
        guideline_key=guideline_key,
        evidence_class=evidence_class,
        evidence_level=evidence_level,
        page=page,
        section=section,
        studies=studies,
    )
    
    return Recommendation(
        action=action,
        rationale=rationale,
        category=category,
        urgency=urgency,
        citation=citation,
        source_type=SourceType.GUIDELINE,
        monitoring=monitoring,
        conditions=conditions or [],
        contraindications=contraindications or [],
    )


def synthesis_recommendation(
    action: str,
    rationale: str,
    source_guidelines: List[str],
    synthesis_rationale: str,
    confidence_score: float = 0.7,
    category: RecommendationCategory = RecommendationCategory.PHARMACOTHERAPY,
    urgency: Urgency = Urgency.ROUTINE,
) -> Recommendation:
    """
    Create a synthesized recommendation (NOT direct from guideline).
    
    Use this when:
    - The clinical scenario is not directly addressed by any single guideline
    - Multiple guidelines need to be combined
    - Expert reasoning is applied beyond explicit guideline text
    
    These recommendations will ALWAYS display a disclaimer to the clinician.
    """
    return Recommendation(
        action=action,
        rationale=rationale,
        category=category,
        urgency=urgency,
        source_type=SourceType.SYNTHESIS,
        synthesis_rationale=synthesis_rationale,
        source_guidelines=source_guidelines,
        confidence_score=confidence_score,
    )
