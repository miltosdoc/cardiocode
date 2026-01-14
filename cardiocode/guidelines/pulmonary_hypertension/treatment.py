"""
PH Treatment - ESC/ERS 2022 Guidelines.

Implements treatment algorithms for PAH.
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


class PAHRiskCategory(Enum):
    """PAH risk stratification category."""
    LOW = "low"           # 1-year mortality <5%
    INTERMEDIATE = "intermediate"  # 1-year mortality 5-20%
    HIGH = "high"         # 1-year mortality >20%


def assess_pah_risk(
    who_fc: int,  # WHO Functional Class 1-4
    six_mwd: Optional[float] = None,  # 6-minute walk distance (meters)
    nt_pro_bnp: Optional[float] = None,  # pg/mL
    ra_area: Optional[float] = None,  # cm2
    pericardial_effusion: bool = False,
) -> PAHRiskCategory:
    """
    Risk stratify PAH patient.
    
    Per ESC/ERS 2022 Table 19: Risk assessment
    
    LOW risk:
    - WHO FC I-II
    - 6MWD > 440m
    - NT-proBNP < 300 pg/mL
    - RA area < 18 cm2
    - No pericardial effusion
    
    HIGH risk:
    - WHO FC IV
    - 6MWD < 165m
    - NT-proBNP > 1400 pg/mL
    - RA area > 26 cm2
    - Pericardial effusion present
    
    Args:
        who_fc: WHO Functional Class (1-4)
        six_mwd: 6-minute walk distance in meters
        nt_pro_bnp: NT-proBNP level
        ra_area: Right atrial area on echo
        pericardial_effusion: Presence of pericardial effusion
    
    Returns:
        PAHRiskCategory
    """
    low_risk_points = 0
    high_risk_points = 0
    
    # WHO FC
    if who_fc <= 2:
        low_risk_points += 1
    elif who_fc == 4:
        high_risk_points += 1
    
    # 6MWD
    if six_mwd:
        if six_mwd > 440:
            low_risk_points += 1
        elif six_mwd < 165:
            high_risk_points += 1
    
    # NT-proBNP
    if nt_pro_bnp:
        if nt_pro_bnp < 300:
            low_risk_points += 1
        elif nt_pro_bnp > 1400:
            high_risk_points += 1
    
    # RA area
    if ra_area:
        if ra_area < 18:
            low_risk_points += 1
        elif ra_area > 26:
            high_risk_points += 1
    
    # Pericardial effusion
    if pericardial_effusion:
        high_risk_points += 1
    
    # Determine category
    if high_risk_points >= 2:
        return PAHRiskCategory.HIGH
    elif low_risk_points >= 3:
        return PAHRiskCategory.LOW
    else:
        return PAHRiskCategory.INTERMEDIATE


def get_pah_treatment(patient: "Patient") -> RecommendationSet:
    """
    Get PAH treatment recommendations.
    
    Per ESC/ERS 2022 Section 7: Treatment algorithm
    
    Key principles:
    - Risk-based treatment strategy
    - Initial combination therapy for most patients
    - Escalation based on response
    
    Args:
        patient: Patient with diagnosed PAH
    
    Returns:
        RecommendationSet with treatment recommendations
    """
    rec_set = RecommendationSet(
        title="PAH Treatment Recommendations",
        primary_guideline="ESC/ERS PH 2022",
    )
    
    # General measures
    rec_set.add(guideline_recommendation(
        action="Supportive therapy: Supervised exercise rehabilitation, psychosocial support, avoid pregnancy",
        guideline_key="esc_ph_2022",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.A,
        category=RecommendationCategory.LIFESTYLE,
        section="7.1",
    ))
    
    rec_set.add(guideline_recommendation(
        action="Diuretics for signs of RV failure and fluid retention",
        guideline_key="esc_ph_2022",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.C,
        category=RecommendationCategory.PHARMACOTHERAPY,
        section="7.1",
    ))
    
    rec_set.add(guideline_recommendation(
        action="Oxygen therapy if PaO2 < 60 mmHg (8 kPa) to maintain SpO2 > 90%",
        guideline_key="esc_ph_2022",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.C,
        category=RecommendationCategory.PHARMACOTHERAPY,
        section="7.1",
    ))
    
    # Risk assessment
    who_fc = patient.nyha_class.value if patient.nyha_class else 3
    bnp = patient.labs.nt_pro_bnp if patient.labs else None
    
    risk = assess_pah_risk(
        who_fc=who_fc,
        nt_pro_bnp=bnp,
    )
    
    rec_set.add(guideline_recommendation(
        action=f"Risk category: {risk.value.upper()}. Treatment intensity based on risk stratification.",
        guideline_key="esc_ph_2022",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.A,
        category=RecommendationCategory.DIAGNOSTIC,
        section="7.2",
    ))
    
    # Treatment based on risk
    if risk == PAHRiskCategory.LOW:
        rec_set.add(guideline_recommendation(
            action="LOW RISK: Initial monotherapy or oral combination therapy (PDE5i/sGC stimulator + ERA)",
            guideline_key="esc_ph_2022",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.A,
            category=RecommendationCategory.PHARMACOTHERAPY,
            section="7.3",
            studies=["AMBITION", "GRIPHON"],
        ))
        
    elif risk == PAHRiskCategory.INTERMEDIATE:
        rec_set.add(guideline_recommendation(
            action="INTERMEDIATE RISK: Initial oral combination therapy RECOMMENDED (ERA + PDE5i or ERA + sGC stimulator)",
            guideline_key="esc_ph_2022",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.A,
            category=RecommendationCategory.PHARMACOTHERAPY,
            urgency=Urgency.SOON,
            section="7.3",
            studies=["AMBITION"],
            rationale="Combination > monotherapy for intermediate-high risk",
        ))
        
    else:  # HIGH
        rec_set.add(guideline_recommendation(
            action="HIGH RISK: Initial triple therapy including IV/SC prostacyclin RECOMMENDED. Consider lung transplant referral.",
            guideline_key="esc_ph_2022",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PHARMACOTHERAPY,
            urgency=Urgency.URGENT,
            section="7.3",
            rationale="High risk = high mortality. Aggressive upfront therapy needed.",
        ))
        
        rec_set.add(guideline_recommendation(
            action="IV epoprostenol (Flolan) or SC/IV treprostinil for severe/high-risk PAH",
            guideline_key="esc_ph_2022",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.A,
            category=RecommendationCategory.PHARMACOTHERAPY,
            urgency=Urgency.URGENT,
            section="7.3",
        ))
        
        rec_set.add(guideline_recommendation(
            action="Refer to transplant center for evaluation if WHO FC III-IV despite maximal therapy",
            guideline_key="esc_ph_2022",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.REFERRAL,
            section="7.4",
        ))
    
    # Specific drug recommendations
    rec_set.add(guideline_recommendation(
        action="ERA options: ambrisentan 5-10mg daily, bosentan 125mg BID, macitentan 10mg daily",
        guideline_key="esc_ph_2022",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.A,
        category=RecommendationCategory.PHARMACOTHERAPY,
        section="7.3",
        studies=["ARIES", "BREATHE", "SERAPHIN"],
    ))
    
    rec_set.add(guideline_recommendation(
        action="PDE5i options: sildenafil 20mg TID, tadalafil 40mg daily. sGC stimulator: riociguat 2.5mg TID",
        guideline_key="esc_ph_2022",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.A,
        category=RecommendationCategory.PHARMACOTHERAPY,
        section="7.3",
        studies=["SUPER", "PHIRST", "PATENT"],
    ))
    
    # Anticoagulation
    rec_set.add(guideline_recommendation(
        action="Anticoagulation: Consider in IPAH (Class IIb). Not routinely recommended in other PAH forms.",
        guideline_key="esc_ph_2022",
        evidence_class=EvidenceClass.IIB,
        evidence_level=EvidenceLevel.C,
        category=RecommendationCategory.PHARMACOTHERAPY,
        section="7.1",
    ))
    
    return rec_set
