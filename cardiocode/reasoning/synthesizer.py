"""
Clinical Reasoning and Synthesis for CardioCode.

This module handles scenarios where:
1. No single guideline directly addresses the clinical question
2. Multiple guidelines need to be integrated
3. Clinical judgment must be applied beyond explicit guideline text

CRITICAL: All synthesized recommendations are explicitly flagged.
The clinician must ALWAYS know when they're receiving guideline-based
vs. synthesized/extrapolated recommendations.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any, Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from cardiocode.core.types import Patient

from cardiocode.core.recommendation import (
    Recommendation,
    RecommendationSet,
    RecommendationCategory,
    Urgency,
    synthesis_recommendation,
)
from cardiocode.core.evidence import SourceType


class ReasoningStrategy(Enum):
    """Types of clinical reasoning strategies."""
    DIRECT_GUIDELINE = "direct_guideline"           # Exact guideline match
    ANALOGICAL = "analogical"                        # Similar scenario in guideline
    MULTI_GUIDELINE = "multi_guideline"             # Combine multiple guidelines
    EXPERT_EXTRAPOLATION = "expert_extrapolation"   # Extend beyond guideline scope
    FIRST_PRINCIPLES = "first_principles"           # Basic pathophysiology reasoning


@dataclass
class ReasoningStep:
    """A single step in the clinical reasoning chain."""
    step_number: int
    description: str
    source: Optional[str] = None          # Guideline or reasoning basis
    confidence: float = 1.0               # 0.0 to 1.0


@dataclass
class ReasoningResult:
    """
    Result of clinical reasoning process.
    
    Contains the full reasoning chain for transparency and auditability.
    """
    question: str
    answer: str
    strategy: ReasoningStrategy
    reasoning_chain: List[ReasoningStep] = field(default_factory=list)
    
    # Source information
    guidelines_consulted: List[str] = field(default_factory=list)
    evidence_found: bool = False
    
    # Confidence assessment
    overall_confidence: float = 1.0
    uncertainty_factors: List[str] = field(default_factory=list)
    
    # Recommendations generated
    recommendations: List[Recommendation] = field(default_factory=list)
    
    # Metadata
    generated_at: datetime = field(default_factory=datetime.now)
    
    @property
    def is_synthesis(self) -> bool:
        """Whether this result involved synthesis beyond direct guidelines."""
        return self.strategy not in [ReasoningStrategy.DIRECT_GUIDELINE]
    
    def format_reasoning_chain(self) -> str:
        """Format the reasoning chain for display."""
        lines = ["Reasoning Chain:", "-" * 40]
        for step in self.reasoning_chain:
            source_info = f" [{step.source}]" if step.source else ""
            conf = f" (confidence: {step.confidence:.0%})"
            lines.append(f"{step.step_number}. {step.description}{source_info}{conf}")
        return "\n".join(lines)
    
    def format_for_display(self) -> str:
        """Format the complete reasoning result."""
        lines = []
        
        # Header with synthesis warning if applicable
        if self.is_synthesis:
            lines.append("!" * 60)
            lines.append("! SYNTHESIS / EXTRAPOLATION - NOT DIRECT GUIDELINE")
            lines.append("!" * 60)
            lines.append(f"Reasoning strategy: {self.strategy.value}")
            lines.append(f"Overall confidence: {self.overall_confidence:.0%}")
            if self.uncertainty_factors:
                lines.append("Uncertainty factors:")
                for factor in self.uncertainty_factors:
                    lines.append(f"  - {factor}")
            lines.append("")
        
        lines.append(f"Question: {self.question}")
        lines.append("")
        lines.append(f"Answer: {self.answer}")
        lines.append("")
        
        if self.guidelines_consulted:
            lines.append(f"Guidelines consulted: {', '.join(self.guidelines_consulted)}")
        
        lines.append("")
        lines.append(self.format_reasoning_chain())
        
        if self.recommendations:
            lines.append("\n" + "=" * 40)
            lines.append("Recommendations:")
            for rec in self.recommendations:
                lines.append(rec.format_for_display())
        
        return "\n".join(lines)


class ClinicalReasoner:
    """
    Clinical reasoning engine for CardioCode.
    
    Integrates multiple guidelines and applies clinical reasoning
    when direct guideline recommendations are not available.
    
    Usage:
        reasoner = ClinicalReasoner()
        result = reasoner.reason(
            patient=patient,
            question="What anticoagulation for this AF patient with CKD?"
        )
    """
    
    def __init__(self):
        """Initialize the clinical reasoner."""
        # Import guidelines (will be populated as they're encoded)
        self._guideline_modules = {}
        self._reasoning_rules = []
    
    def register_guideline(self, name: str, module: Any) -> None:
        """Register a guideline module for reasoning."""
        self._guideline_modules[name] = module
    
    def reason(
        self,
        patient: "Patient",
        question: str,
        require_guideline: bool = False,
    ) -> ReasoningResult:
        """
        Apply clinical reasoning to answer a question.
        
        Args:
            patient: Patient object with clinical data
            question: Clinical question to answer
            require_guideline: If True, only return guideline-based answers
        
        Returns:
            ReasoningResult with answer, reasoning chain, and recommendations
        """
        # Initialize result
        result = ReasoningResult(
            question=question,
            answer="",
            strategy=ReasoningStrategy.FIRST_PRINCIPLES,
            guidelines_consulted=[],
        )
        
        # Step 1: Identify relevant guidelines
        relevant_guidelines = self._identify_relevant_guidelines(patient, question)
        result.guidelines_consulted = list(relevant_guidelines.keys())
        
        step_num = 1
        result.reasoning_chain.append(ReasoningStep(
            step_number=step_num,
            description=f"Identified {len(relevant_guidelines)} potentially relevant guidelines",
            source="CardioCode guideline registry",
            confidence=1.0,
        ))
        
        # Step 2: Search for direct guideline match
        direct_match = self._find_direct_guideline_match(
            patient, question, relevant_guidelines
        )
        
        step_num += 1
        if direct_match:
            result.reasoning_chain.append(ReasoningStep(
                step_number=step_num,
                description=f"Found direct guideline recommendation",
                source=direct_match.get("guideline", ""),
                confidence=1.0,
            ))
            result.strategy = ReasoningStrategy.DIRECT_GUIDELINE
            result.evidence_found = True
            result.answer = direct_match.get("answer", "")
            result.overall_confidence = 1.0
            
            if "recommendations" in direct_match:
                result.recommendations = direct_match["recommendations"]
            
            return result
        else:
            result.reasoning_chain.append(ReasoningStep(
                step_number=step_num,
                description="No direct guideline match found",
                confidence=1.0,
            ))
        
        # If require_guideline is True, stop here
        if require_guideline:
            result.answer = (
                "No direct guideline recommendation found for this clinical scenario. "
                "Synthesis was not requested."
            )
            result.overall_confidence = 0.0
            return result
        
        # Step 3: Attempt multi-guideline synthesis
        step_num += 1
        result.reasoning_chain.append(ReasoningStep(
            step_number=step_num,
            description="Attempting synthesis from multiple guidelines",
            confidence=0.8,
        ))
        
        synthesis = self._synthesize_from_multiple_guidelines(
            patient, question, relevant_guidelines
        )
        
        if synthesis:
            result.strategy = ReasoningStrategy.MULTI_GUIDELINE
            result.answer = synthesis.get("answer", "")
            result.overall_confidence = synthesis.get("confidence", 0.7)
            result.uncertainty_factors = synthesis.get("uncertainties", [])
            
            if "recommendations" in synthesis:
                result.recommendations = synthesis["recommendations"]
            
            step_num += 1
            result.reasoning_chain.append(ReasoningStep(
                step_number=step_num,
                description=f"Synthesized recommendation from {len(synthesis.get('sources', []))} guidelines",
                source=", ".join(synthesis.get("sources", [])),
                confidence=result.overall_confidence,
            ))
            
            return result
        
        # Step 4: Expert extrapolation
        step_num += 1
        result.reasoning_chain.append(ReasoningStep(
            step_number=step_num,
            description="Applying clinical reasoning beyond guideline scope",
            confidence=0.5,
        ))
        
        extrapolation = self._extrapolate(patient, question)
        result.strategy = ReasoningStrategy.EXPERT_EXTRAPOLATION
        result.answer = extrapolation.get("answer", "Unable to provide recommendation")
        result.overall_confidence = extrapolation.get("confidence", 0.5)
        result.uncertainty_factors = extrapolation.get("uncertainties", [
            "No direct guideline evidence",
            "Based on clinical reasoning",
            "Consider specialist consultation",
        ])
        
        if "recommendations" in extrapolation:
            result.recommendations = extrapolation["recommendations"]
        
        return result
    
    def _identify_relevant_guidelines(
        self,
        patient: "Patient",
        question: str,
    ) -> Dict[str, Any]:
        """Identify which guidelines are relevant to the question."""
        relevant = {}
        
        question_lower = question.lower()
        
        # Keyword-based guideline matching
        guideline_keywords = {
            "heart_failure": ["heart failure", "hf", "lvef", "ef", "ejection fraction", 
                            "congestion", "diuretic", "gdmt"],
            "atrial_fibrillation": ["atrial fibrillation", "af", "afib", "anticoagulation",
                                    "stroke prevention", "rate control", "rhythm control"],
            "acs": ["acs", "nstemi", "stemi", "acute coronary", "troponin", "chest pain",
                   "unstable angina", "mi", "myocardial infarction"],
            "vhd": ["valve", "valvular", "aortic stenosis", "mitral", "tricuspid",
                   "regurgitation", "stenosis", "tavr", "tavi"],
            "pulmonary_hypertension": ["pulmonary hypertension", "ph", "pah", "rvsp",
                                       "right heart", "pulmonary pressure"],
            "arrhythmia": ["arrhythmia", "vt", "ventricular tachycardia", "scd",
                         "sudden cardiac death", "icd", "pacemaker", "ablation"],
            "cardio_oncology": ["cardio-oncology", "cardiooncology", "chemotherapy",
                               "cancer", "anthracycline", "cardiotoxicity"],
        }
        
        for guideline_key, keywords in guideline_keywords.items():
            if any(kw in question_lower for kw in keywords):
                relevant[guideline_key] = self._guideline_modules.get(guideline_key)
        
        # Also check patient diagnoses
        if patient.has_diagnosis("heart_failure") or (patient.lvef and patient.lvef < 50):
            relevant["heart_failure"] = self._guideline_modules.get("heart_failure")
        
        if patient.af_type or (patient.ecg and patient.ecg.af_present):
            relevant["atrial_fibrillation"] = self._guideline_modules.get("atrial_fibrillation")
        
        return relevant
    
    def _find_direct_guideline_match(
        self,
        patient: "Patient",
        question: str,
        guidelines: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """
        Search for direct guideline recommendation.
        
        This will be implemented as guidelines are encoded.
        """
        # Placeholder - will be populated with actual guideline logic
        return None
    
    def _synthesize_from_multiple_guidelines(
        self,
        patient: "Patient",
        question: str,
        guidelines: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """
        Synthesize recommendation from multiple guidelines.
        
        This will be implemented as guidelines are encoded.
        """
        # Placeholder - will be populated with actual guideline logic
        return None
    
    def _extrapolate(
        self,
        patient: "Patient",
        question: str,
    ) -> Dict[str, Any]:
        """
        Apply clinical reasoning when no guideline applies.
        
        Returns extrapolated recommendation with explicit uncertainty.
        """
        return {
            "answer": (
                "No direct guideline recommendation available for this scenario. "
                "Clinical judgment required. Consider specialist consultation."
            ),
            "confidence": 0.4,
            "uncertainties": [
                "Outside explicit guideline scope",
                "Individual patient factors may apply",
                "Recommend multidisciplinary discussion",
            ],
            "recommendations": [
                synthesis_recommendation(
                    action="Consider specialist consultation for individualized management",
                    rationale="Clinical scenario not directly addressed by available guidelines",
                    source_guidelines=["General cardiology practice"],
                    synthesis_rationale="No direct guideline match; expert opinion recommended",
                    confidence_score=0.4,
                    category=RecommendationCategory.REFERRAL,
                )
            ],
        }
    
    def explain_gap(self, question: str, patient: "Patient") -> str:
        """
        Explain why guidelines may not apply to a specific case.
        
        Useful for transparency when synthesis is required.
        """
        gaps = []
        
        # Check for common gap scenarios
        if patient.age and patient.age > 85:
            gaps.append(
                "Patient age (>85 years) exceeds typical RCT inclusion criteria. "
                "Most trials excluded patients over 75-80 years."
            )
        
        if patient.labs and patient.labs.egfr and patient.labs.egfr < 25:
            gaps.append(
                "Severe CKD (eGFR < 25) often excluded from major trials. "
                "Dosing and safety data may be limited."
            )
        
        if patient.has_diagnosis("frailty"):
            gaps.append(
                "Frailty was exclusion criterion in most major trials. "
                "Risk-benefit may differ from trial populations."
            )
        
        if not gaps:
            gaps.append(
                "This specific clinical combination may not be directly addressed "
                "in available guidelines. Individualized judgment required."
            )
        
        return "\n".join([
            "GUIDELINE GAP EXPLANATION:",
            "-" * 40,
        ] + gaps)


# Singleton reasoner instance
_reasoner_instance: Optional[ClinicalReasoner] = None


def get_reasoner() -> ClinicalReasoner:
    """Get the singleton clinical reasoner instance."""
    global _reasoner_instance
    if _reasoner_instance is None:
        _reasoner_instance = ClinicalReasoner()
    return _reasoner_instance
