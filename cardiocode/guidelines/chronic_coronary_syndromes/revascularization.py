"""
CCS Revascularization - ESC 2019 Guidelines.

Implements:
- Revascularization indications
- PCI vs CABG decision
- Complete revascularization considerations
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


class CADExtent(Enum):
    """Extent of coronary artery disease."""
    ONE_VESSEL = "one_vessel"
    TWO_VESSEL = "two_vessel"
    THREE_VESSEL = "three_vessel"
    LEFT_MAIN = "left_main"


def assess_revascularization_indication(
    patient: "Patient",
    cad_extent: Optional[CADExtent] = None,
    has_proximal_lad: bool = False,
    ischemic_burden_percent: Optional[float] = None,
) -> RecommendationSet:
    """
    Assess indication for coronary revascularization in CCS.
    
    Per ESC 2019 Section 5.3: Revascularization
    
    Indications for revascularization:
    1. Prognostic benefit:
       - Left main > 50%
       - Proximal LAD > 50%
       - 2-3 vessel disease with impaired LV function
       - Large area of ischemia (> 10% LV)
       
    2. Symptomatic benefit:
       - Angina limiting QoL despite optimal medical therapy
    
    Args:
        patient: Patient with CCS
        cad_extent: Extent of CAD
        has_proximal_lad: Proximal LAD involvement
        ischemic_burden_percent: Percentage of myocardium ischemic
    
    Returns:
        RecommendationSet with revascularization recommendation
    """
    rec_set = RecommendationSet(
        title="Revascularization Indication Assessment",
        primary_guideline="ESC CCS 2019",
    )
    
    has_prognostic_indication = False
    has_symptomatic_indication = False
    
    is_symptomatic = patient.nyha_class and patient.nyha_class.value >= 2
    has_hfref = patient.lvef is not None and patient.lvef <= 40
    
    # ISCHEMIA trial context
    rec_set.add(guideline_recommendation(
        action="ISCHEMIA trial showed no mortality benefit with routine revascularization in stable CAD. Prioritize optimal medical therapy.",
        guideline_key="esc_ccs_2019",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.A,
        category=RecommendationCategory.PHARMACOTHERAPY,
        section="5.3",
        studies=["ISCHEMIA"],
        rationale="OMT first. Revascularize for refractory symptoms or prognostic indications.",
    ))
    
    # Left main disease
    if cad_extent == CADExtent.LEFT_MAIN:
        has_prognostic_indication = True
        rec_set.add(guideline_recommendation(
            action="Left main disease > 50%: Revascularization RECOMMENDED for prognostic benefit",
            guideline_key="esc_ccs_2019",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.A,
            category=RecommendationCategory.PROCEDURE,
            section="5.3",
            urgency=Urgency.SOON,
        ))
    
    # Proximal LAD
    elif has_proximal_lad:
        has_prognostic_indication = True
        rec_set.add(guideline_recommendation(
            action="Proximal LAD stenosis > 50%: Revascularization SHOULD BE CONSIDERED for prognostic benefit",
            guideline_key="esc_ccs_2019",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.A,
            category=RecommendationCategory.PROCEDURE,
            section="5.3",
        ))
    
    # Multivessel disease with LV dysfunction
    elif cad_extent in [CADExtent.TWO_VESSEL, CADExtent.THREE_VESSEL] and has_hfref:
        has_prognostic_indication = True
        rec_set.add(guideline_recommendation(
            action="Multivessel CAD with LV dysfunction (LVEF <= 35%): CABG RECOMMENDED for prognostic benefit",
            guideline_key="esc_ccs_2019",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PROCEDURE,
            section="5.3",
            studies=["STICH", "STICHES"],
        ))
    
    # Large ischemic burden
    if ischemic_burden_percent and ischemic_burden_percent >= 10:
        has_prognostic_indication = True
        rec_set.add(guideline_recommendation(
            action=f"Large ischemic burden ({ischemic_burden_percent}%): Revascularization may improve prognosis",
            guideline_key="esc_ccs_2019",
            evidence_class=EvidenceClass.IIA,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PROCEDURE,
            section="5.3",
        ))
    
    # Symptomatic indication
    if is_symptomatic:
        has_symptomatic_indication = True
        rec_set.add(guideline_recommendation(
            action="Persistent angina despite optimal medical therapy: Revascularization RECOMMENDED for symptom relief",
            guideline_key="esc_ccs_2019",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.A,
            category=RecommendationCategory.PROCEDURE,
            section="5.3",
        ))
    
    if not has_prognostic_indication and not has_symptomatic_indication:
        rec_set.add(guideline_recommendation(
            action="No clear indication for revascularization. Continue optimal medical therapy with close follow-up.",
            guideline_key="esc_ccs_2019",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.A,
            category=RecommendationCategory.PHARMACOTHERAPY,
            section="5.3",
        ))
    
    return rec_set


def choose_pci_vs_cabg(
    patient: "Patient",
    cad_extent: CADExtent,
    syntax_score: Optional[int] = None,
) -> RecommendationSet:
    """
    Choose between PCI and CABG for revascularization.
    
    Per ESC 2019 Section 5.3.2 and ESC/EACTS 2018 Myocardial Revascularization Guidelines.
    
    Key factors:
    - Anatomical complexity (SYNTAX score)
    - Diabetes
    - LV function
    - Surgical risk
    - Patient preference
    
    Args:
        patient: Patient requiring revascularization
        cad_extent: Extent of CAD
        syntax_score: SYNTAX score (anatomical complexity)
    
    Returns:
        RecommendationSet with PCI vs CABG recommendation
    """
    rec_set = RecommendationSet(
        title="PCI vs CABG Decision",
        primary_guideline="ESC CCS 2019",
    )
    
    has_diabetes = patient.has_diabetes
    has_hfref = patient.lvef is not None and patient.lvef <= 40
    
    # Heart Team discussion
    rec_set.add(guideline_recommendation(
        action="Heart Team discussion RECOMMENDED for multivessel or left main disease to choose between PCI and CABG",
        guideline_key="esc_ccs_2019",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.C,
        category=RecommendationCategory.REFERRAL,
        section="5.3.2",
    ))
    
    # Calculate SYNTAX if available
    if syntax_score is not None:
        rec_set.description = f"SYNTAX Score: {syntax_score}"
        
        if syntax_score <= 22:
            rec_set.add(guideline_recommendation(
                action=f"Low SYNTAX score ({syntax_score}): PCI and CABG have similar outcomes. Consider patient factors and preference.",
                guideline_key="esc_ccs_2019",
                evidence_class=EvidenceClass.I,
                evidence_level=EvidenceLevel.A,
                category=RecommendationCategory.PROCEDURE,
                section="5.3.2",
                studies=["SYNTAX", "EXCEL", "NOBLE"],
            ))
        elif syntax_score <= 32:
            rec_set.add(guideline_recommendation(
                action=f"Intermediate SYNTAX score ({syntax_score}): Individualize decision. CABG may be preferred, especially with diabetes.",
                guideline_key="esc_ccs_2019",
                evidence_class=EvidenceClass.IIA,
                evidence_level=EvidenceLevel.B,
                category=RecommendationCategory.PROCEDURE,
                section="5.3.2",
            ))
        else:
            rec_set.add(guideline_recommendation(
                action=f"High SYNTAX score ({syntax_score}): CABG RECOMMENDED over PCI",
                guideline_key="esc_ccs_2019",
                evidence_class=EvidenceClass.I,
                evidence_level=EvidenceLevel.A,
                category=RecommendationCategory.PROCEDURE,
                section="5.3.2",
            ))
    
    # Left main specific
    if cad_extent == CADExtent.LEFT_MAIN:
        rec_set.add(guideline_recommendation(
            action="Left main disease: CABG and PCI both acceptable with low-intermediate SYNTAX. CABG preferred for high SYNTAX or complex disease.",
            guideline_key="esc_ccs_2019",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.A,
            category=RecommendationCategory.PROCEDURE,
            section="5.3.2",
            studies=["SYNTAX", "EXCEL", "PRECOMBAT"],
        ))
    
    # Three-vessel disease
    elif cad_extent == CADExtent.THREE_VESSEL:
        rec_set.add(guideline_recommendation(
            action="Three-vessel CAD: CABG RECOMMENDED, especially with diabetes, reduced LV function, or high SYNTAX score",
            guideline_key="esc_ccs_2019",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.A,
            category=RecommendationCategory.PROCEDURE,
            section="5.3.2",
            studies=["FREEDOM", "SYNTAX"],
        ))
    
    # Diabetes consideration
    if has_diabetes and cad_extent in [CADExtent.THREE_VESSEL, CADExtent.LEFT_MAIN]:
        rec_set.add(guideline_recommendation(
            action="Diabetes with multivessel/left main disease: CABG RECOMMENDED over PCI",
            guideline_key="esc_ccs_2019",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.A,
            category=RecommendationCategory.PROCEDURE,
            section="5.3.2",
            studies=["FREEDOM"],
            rationale="CABG provides survival benefit in diabetics with MVD",
        ))
    
    # LV dysfunction consideration
    if has_hfref:
        rec_set.add(guideline_recommendation(
            action="LV dysfunction: CABG RECOMMENDED to improve survival. Ensure viable myocardium if LVEF severely reduced.",
            guideline_key="esc_ccs_2019",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PROCEDURE,
            section="5.3.2",
            studies=["STICH"],
        ))
    
    # One or two vessel disease (non-proximal LAD)
    if cad_extent in [CADExtent.ONE_VESSEL, CADExtent.TWO_VESSEL]:
        rec_set.add(guideline_recommendation(
            action="One or two-vessel disease (non-proximal LAD): PCI is reasonable if symptoms persist despite OMT",
            guideline_key="esc_ccs_2019",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.A,
            category=RecommendationCategory.PROCEDURE,
            section="5.3.2",
        ))
    
    # Complete revascularization
    rec_set.add(guideline_recommendation(
        action="Complete revascularization SHOULD BE CONSIDERED when feasible to improve outcomes",
        guideline_key="esc_ccs_2019",
        evidence_class=EvidenceClass.IIA,
        evidence_level=EvidenceLevel.B,
        category=RecommendationCategory.PROCEDURE,
        section="5.3.2",
        studies=["COMPLETE"],
    ))
    
    return rec_set
