"""
Evidence classification and citation tracking for CardioCode.

This module implements the ESC/ACC evidence grading system and provides
full provenance tracking for all recommendations.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Optional, List, Dict, Any


class EvidenceClass(Enum):
    """
    ESC Classes of Recommendations.
    
    Represents the strength of recommendation based on expert consensus
    and available evidence.
    """
    I = "I"       # Evidence/agreement that treatment is beneficial, useful, effective
    IIA = "IIa"   # Weight of evidence/opinion is in favor of usefulness/efficacy
    IIB = "IIb"   # Usefulness/efficacy is less well established
    III = "III"   # Evidence/agreement that treatment is not useful/effective, may be harmful
    
    @property
    def description(self) -> str:
        descriptions = {
            "I": "Is recommended / is indicated",
            "IIa": "Should be considered", 
            "IIb": "May be considered",
            "III": "Is not recommended",
        }
        return descriptions[self.value]
    
    @property
    def strength_text(self) -> str:
        texts = {
            "I": "Strong recommendation",
            "IIa": "Moderate recommendation",
            "IIb": "Weak recommendation", 
            "III": "Not recommended / contraindicated",
        }
        return texts[self.value]
    
    @property
    def color_code(self) -> str:
        """Color for visual display (green/yellow/orange/red)."""
        colors = {
            "I": "green",
            "IIa": "yellow",
            "IIb": "orange",
            "III": "red",
        }
        return colors[self.value]


class EvidenceLevel(Enum):
    """
    ESC Levels of Evidence.
    
    Represents the quality and source of evidence supporting the recommendation.
    """
    A = "A"  # Data from multiple RCTs or meta-analyses
    B = "B"  # Data from single RCT or large non-randomized studies
    C = "C"  # Consensus of experts and/or small studies, retrospective studies, registries
    
    @property
    def description(self) -> str:
        descriptions = {
            "A": "Data derived from multiple randomized clinical trials or meta-analyses",
            "B": "Data derived from a single randomized clinical trial or large non-randomized studies",
            "C": "Consensus of opinion of the experts and/or small studies, retrospective studies, registries",
        }
        return descriptions[self.value]
    
    @property
    def reliability(self) -> str:
        """Human-readable reliability assessment."""
        reliability = {
            "A": "High confidence - robust evidence",
            "B": "Moderate confidence - limited evidence",
            "C": "Lower confidence - expert opinion",
        }
        return reliability[self.value]


class SourceType(Enum):
    """
    Source classification for transparency.
    
    Critical for user communication - must always distinguish between
    direct guideline recommendations and LLM synthesis.
    """
    GUIDELINE = "guideline"           # Direct from ESC/ACC guideline
    GUIDELINE_EXPERT = "guideline_expert"  # Guideline + expert panel consensus
    SYNTHESIS = "synthesis"           # LLM-synthesized from multiple sources
    EXTRAPOLATION = "extrapolation"   # Extended from related guideline content
    CLINICAL_EXPERIENCE = "clinical_experience"  # Not guideline-based
    
    @property
    def requires_disclaimer(self) -> bool:
        """Whether this source type requires explicit disclaimer."""
        return self.value in ["synthesis", "extrapolation", "clinical_experience"]
    
    @property
    def confidence_modifier(self) -> float:
        """Modifier to apply to confidence scores."""
        modifiers = {
            "guideline": 1.0,
            "guideline_expert": 0.95,
            "synthesis": 0.7,
            "extrapolation": 0.6,
            "clinical_experience": 0.5,
        }
        return modifiers[self.value]


@dataclass
class Study:
    """
    Reference to a clinical study supporting a recommendation.
    """
    name: str                                    # e.g., "PARADIGM-HF"
    full_title: Optional[str] = None
    journal: Optional[str] = None
    year: Optional[int] = None
    pmid: Optional[str] = None                   # PubMed ID
    doi: Optional[str] = None
    study_type: Optional[str] = None             # "RCT", "meta-analysis", "observational"
    sample_size: Optional[int] = None
    key_finding: Optional[str] = None
    
    def __str__(self) -> str:
        if self.year:
            return f"{self.name} ({self.year})"
        return self.name


@dataclass
class Citation:
    """
    Complete citation for a recommendation.
    
    Provides full traceability from recommendation back to source material.
    """
    # Primary source
    guideline_name: str                          # "ESC Heart Failure Guidelines 2021"
    guideline_short: str                         # "ESC HF 2021"
    pdf_filename: Optional[str] = None           # "ehab364.pdf"
    page_number: Optional[int] = None            # PDF page number
    section: Optional[str] = None                # "11.2.3"
    section_title: Optional[str] = None          # "Pharmacological treatment of HFrEF"
    table_number: Optional[str] = None           # "Table 15"
    figure_number: Optional[str] = None          # "Figure 3"
    
    # Evidence grading
    evidence_class: EvidenceClass = EvidenceClass.I
    evidence_level: EvidenceLevel = EvidenceLevel.C
    
    # Supporting studies
    supporting_studies: List[Study] = field(default_factory=list)
    
    # Metadata
    guideline_doi: Optional[str] = None
    guideline_year: Optional[int] = None
    last_verified: Optional[date] = None
    
    def format_short(self) -> str:
        """Short citation format for inline use."""
        return f"{self.guideline_short}, Class {self.evidence_class.value}, Level {self.evidence_level.value}"
    
    def format_full(self) -> str:
        """Full citation format."""
        parts = [self.guideline_name]
        if self.section:
            parts.append(f"Section {self.section}")
        if self.page_number:
            parts.append(f"p.{self.page_number}")
        parts.append(f"Class {self.evidence_class.value}")
        parts.append(f"Level {self.evidence_level.value}")
        return " | ".join(parts)
    
    def format_studies(self) -> str:
        """Format supporting studies as string."""
        if not self.supporting_studies:
            return "No specific studies cited"
        return ", ".join(str(s) for s in self.supporting_studies)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "guideline": self.guideline_name,
            "guideline_short": self.guideline_short,
            "pdf": self.pdf_filename,
            "page": self.page_number,
            "section": self.section,
            "section_title": self.section_title,
            "table": self.table_number,
            "figure": self.figure_number,
            "evidence_class": self.evidence_class.value,
            "evidence_level": self.evidence_level.value,
            "studies": [s.name for s in self.supporting_studies],
            "doi": self.guideline_doi,
            "year": self.guideline_year,
        }


# Pre-defined guideline citations for common use
GUIDELINE_REGISTRY: Dict[str, Dict[str, Any]] = {
    "esc_hf_2021": {
        "name": "2021 ESC Guidelines for the diagnosis and treatment of acute and chronic heart failure",
        "short": "ESC HF 2021",
        "pdf": "ehab364.pdf",
        "doi": "10.1093/eurheartj/ehab364",
        "year": 2021,
    },
    "esc_af_2020": {
        "name": "2020 ESC Guidelines for the diagnosis and management of atrial fibrillation",
        "short": "ESC AF 2020",
        "pdf": "ehaa612.pdf",
        "doi": "10.1093/eurheartj/ehaa612",
        "year": 2020,
    },
    "esc_acs_2020": {
        "name": "2020 ESC Guidelines for the management of acute coronary syndromes in patients presenting without persistent ST-segment elevation",
        "short": "ESC NSTE-ACS 2020",
        "pdf": "ehaa575.pdf",
        "doi": "10.1093/eurheartj/ehaa575",
        "year": 2020,
    },
    "esc_vhd_2021": {
        "name": "2021 ESC/EACTS Guidelines for the management of valvular heart disease",
        "short": "ESC VHD 2021",
        "pdf": "ehab395.pdf",
        "doi": "10.1093/eurheartj/ehab395",
        "year": 2021,
    },
    "esc_ph_2022": {
        "name": "2022 ESC/ERS Guidelines for the diagnosis and treatment of pulmonary hypertension",
        "short": "ESC/ERS PH 2022",
        "pdf": "ehac237.pdf",
        "doi": "10.1093/eurheartj/ehac237",
        "year": 2022,
    },
    "esc_va_scd_2022": {
        "name": "2022 ESC Guidelines for the management of patients with ventricular arrhythmias and the prevention of sudden cardiac death",
        "short": "ESC VA/SCD 2022",
        "pdf": "ehac262.pdf",
        "doi": "10.1093/eurheartj/ehac262",
        "year": 2022,
    },
    "esc_cardio_onc_2022": {
        "name": "2022 ESC Guidelines on cardio-oncology",
        "short": "ESC Cardio-Oncology 2022",
        "pdf": "ehac244.pdf",
        "doi": "10.1093/eurheartj/ehac244",
        "year": 2022,
    },
}


def create_citation(
    guideline_key: str,
    evidence_class: EvidenceClass,
    evidence_level: EvidenceLevel,
    page: Optional[int] = None,
    section: Optional[str] = None,
    section_title: Optional[str] = None,
    studies: Optional[List[str]] = None,
) -> Citation:
    """
    Factory function to create citations from guideline registry.
    
    Args:
        guideline_key: Key from GUIDELINE_REGISTRY (e.g., "esc_hf_2021")
        evidence_class: Class of recommendation (I, IIa, IIb, III)
        evidence_level: Level of evidence (A, B, C)
        page: PDF page number
        section: Section number (e.g., "11.2.3")
        section_title: Section title
        studies: List of study names (e.g., ["PARADIGM-HF", "DAPA-HF"])
    
    Returns:
        Citation object with full provenance
    """
    if guideline_key not in GUIDELINE_REGISTRY:
        raise ValueError(f"Unknown guideline key: {guideline_key}")
    
    gl = GUIDELINE_REGISTRY[guideline_key]
    
    study_objects = []
    if studies:
        study_objects = [Study(name=s) for s in studies]
    
    return Citation(
        guideline_name=gl["name"],
        guideline_short=gl["short"],
        pdf_filename=gl["pdf"],
        guideline_doi=gl["doi"],
        guideline_year=gl["year"],
        evidence_class=evidence_class,
        evidence_level=evidence_level,
        page_number=page,
        section=section,
        section_title=section_title,
        supporting_studies=study_objects,
    )
