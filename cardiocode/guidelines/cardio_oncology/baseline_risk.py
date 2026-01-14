"""
Baseline CV Risk Assessment - ESC 2022 Cardio-Oncology Guidelines.

Pre-treatment cardiovascular risk assessment for cancer patients:
- HFA-ICOS risk stratification
- Risk factors for cardiotoxicity
- Agent-specific risk assessment
"""

from __future__ import annotations
from typing import Optional, List, Dict, TYPE_CHECKING
from dataclasses import dataclass, field
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


class CardiotoxicityRisk(Enum):
    """Baseline cardiotoxicity risk category."""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"


class CancerTherapyType(Enum):
    """Types of cancer therapy with cardiotoxic potential."""
    ANTHRACYCLINE = "anthracycline"
    HER2_TARGETED = "her2_targeted"  # Trastuzumab, pertuzumab
    VEGF_INHIBITOR = "vegf_inhibitor"  # Bevacizumab, sunitinib, etc.
    BCR_ABL_INHIBITOR = "bcr_abl_inhibitor"  # Ponatinib, nilotinib, dasatinib
    PROTEASOME_INHIBITOR = "proteasome_inhibitor"  # Carfilzomib
    IMMUNE_CHECKPOINT = "immune_checkpoint"  # PD-1, PD-L1, CTLA-4 inhibitors
    CAR_T = "car_t_cell"
    RADIATION_CHEST = "radiation_chest"
    FLUOROPYRIMIDINE = "fluoropyrimidine"  # 5-FU, capecitabine


@dataclass
class CVRiskFactor:
    """Individual cardiovascular risk factor."""
    name: str
    present: bool
    weight: int = 1  # For HFA-ICOS scoring
    details: Optional[str] = None


@dataclass
class BaselineRiskAssessment:
    """Result of baseline CV risk assessment."""
    risk_category: CardiotoxicityRisk
    hfa_icos_score: Optional[int] = None
    risk_factors: List[CVRiskFactor] = field(default_factory=list)
    recommendations: List[Recommendation] = field(default_factory=list)
    monitoring_intensity: str = "standard"  # "standard", "enhanced", "intensive"
    cardiology_referral_needed: bool = False
    can_proceed_with_therapy: bool = True
    precautions: List[str] = field(default_factory=list)


def calculate_hfa_icos_risk(
    # Existing CV disease
    heart_failure: bool = False,
    cardiomyopathy: bool = False,
    severe_vhd: bool = False,
    mi_or_pci_cabg: bool = False,
    stable_angina: bool = False,
    # CV risk factors
    age: Optional[int] = None,
    hypertension: bool = False,
    diabetes: bool = False,
    hyperlipidemia: bool = False,
    obesity: bool = False,  # BMI >= 30
    smoking_current: bool = False,
    family_history_premature_cvd: bool = False,
    # Prior cardiotoxic therapy
    prior_anthracycline: bool = False,
    prior_anthracycline_dose: Optional[float] = None,  # mg/m2 doxorubicin equivalent
    prior_chest_radiation: bool = False,
    prior_chest_radiation_dose: Optional[float] = None,  # Gy
    # Baseline cardiac function
    lvef: Optional[float] = None,
    elevated_troponin: bool = False,
    elevated_bnp: bool = False,
) -> BaselineRiskAssessment:
    """
    Calculate HFA-ICOS baseline cardiotoxicity risk.
    
    Per ESC 2022 Cardio-Oncology Guidelines Section 4.
    
    HFA-ICOS risk stratification:
    - Very high: Existing cardiomyopathy/HF, or LVEF <50%
    - High: Prior cardiotoxic therapy + additional RF, or multiple major RF
    - Moderate: Single major RF or prior cardiotoxic therapy
    - Low: No significant RF
    
    Args:
        Various CV risk factors and prior treatment history
    
    Returns:
        BaselineRiskAssessment with risk category and recommendations
    """
    risk_factors = []
    total_score = 0
    precautions = []
    
    # VERY HIGH RISK factors (immediate cardiology referral)
    very_high_risk = False
    
    if heart_failure or cardiomyopathy:
        risk_factors.append(CVRiskFactor("Heart failure/cardiomyopathy", True, 5))
        total_score += 5
        very_high_risk = True
        precautions.append("Existing HF - multidisciplinary team discussion required")
    
    if lvef is not None and lvef < 50:
        risk_factors.append(CVRiskFactor(f"Reduced LVEF ({lvef}%)", True, 5))
        total_score += 5
        very_high_risk = True
        precautions.append("LVEF <50% at baseline - high risk of further decline")
    
    if severe_vhd:
        risk_factors.append(CVRiskFactor("Severe valvular heart disease", True, 4))
        total_score += 4
        very_high_risk = True
    
    # HIGH RISK factors
    if mi_or_pci_cabg:
        risk_factors.append(CVRiskFactor("Prior MI/PCI/CABG", True, 3))
        total_score += 3
    
    if stable_angina:
        risk_factors.append(CVRiskFactor("Stable angina", True, 2))
        total_score += 2
    
    # Prior cardiotoxic therapy
    if prior_anthracycline:
        dose_str = f" (cumulative {prior_anthracycline_dose} mg/m2)" if prior_anthracycline_dose else ""
        weight = 3 if (prior_anthracycline_dose and prior_anthracycline_dose >= 250) else 2
        risk_factors.append(CVRiskFactor(f"Prior anthracycline{dose_str}", True, weight))
        total_score += weight
        if prior_anthracycline_dose and prior_anthracycline_dose >= 400:
            precautions.append("High cumulative anthracycline dose - consider avoiding further anthracyclines")
    
    if prior_chest_radiation:
        dose_str = f" ({prior_chest_radiation_dose} Gy)" if prior_chest_radiation_dose else ""
        weight = 3 if (prior_chest_radiation_dose and prior_chest_radiation_dose >= 30) else 2
        risk_factors.append(CVRiskFactor(f"Prior chest radiation{dose_str}", True, weight))
        total_score += weight
    
    # CV risk factors
    if age is not None:
        if age >= 75:
            risk_factors.append(CVRiskFactor(f"Age {age} >= 75", True, 2))
            total_score += 2
        elif age >= 65:
            risk_factors.append(CVRiskFactor(f"Age {age} >= 65", True, 1))
            total_score += 1
        elif age < 18:
            risk_factors.append(CVRiskFactor(f"Pediatric age {age}", True, 1))
            total_score += 1
            precautions.append("Pediatric patient - increased lifetime risk of late cardiotoxicity")
    
    if hypertension:
        risk_factors.append(CVRiskFactor("Hypertension", True, 1))
        total_score += 1
    
    if diabetes:
        risk_factors.append(CVRiskFactor("Diabetes mellitus", True, 1))
        total_score += 1
    
    if smoking_current:
        risk_factors.append(CVRiskFactor("Current smoking", True, 1))
        total_score += 1
        precautions.append("Smoking cessation strongly recommended")
    
    if obesity:
        risk_factors.append(CVRiskFactor("Obesity (BMI >= 30)", True, 1))
        total_score += 1
    
    if hyperlipidemia:
        risk_factors.append(CVRiskFactor("Hyperlipidemia", True, 1))
        total_score += 1
    
    if family_history_premature_cvd:
        risk_factors.append(CVRiskFactor("Family history premature CVD", True, 1))
        total_score += 1
    
    # Biomarkers
    if elevated_troponin:
        risk_factors.append(CVRiskFactor("Elevated troponin at baseline", True, 2))
        total_score += 2
        precautions.append("Elevated baseline troponin - evaluate for underlying cardiac disease")
    
    if elevated_bnp:
        risk_factors.append(CVRiskFactor("Elevated BNP/NT-proBNP", True, 2))
        total_score += 2
    
    # Determine risk category
    if very_high_risk or total_score >= 6:
        risk_category = CardiotoxicityRisk.VERY_HIGH
        monitoring = "intensive"
        referral = True
    elif total_score >= 4:
        risk_category = CardiotoxicityRisk.HIGH
        monitoring = "enhanced"
        referral = True
    elif total_score >= 2:
        risk_category = CardiotoxicityRisk.MODERATE
        monitoring = "enhanced"
        referral = False
    else:
        risk_category = CardiotoxicityRisk.LOW
        monitoring = "standard"
        referral = False
    
    # Generate recommendations
    recommendations = []
    
    # Baseline evaluation
    recommendations.append(guideline_recommendation(
        action="Baseline ECG before potentially cardiotoxic cancer therapy",
        guideline_key="esc_cardio_onc_2022",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.C,
        category=RecommendationCategory.DIAGNOSTIC,
        urgency=Urgency.SOON,
        section="4",
    ))
    
    recommendations.append(guideline_recommendation(
        action="Baseline echocardiogram (preferably with GLS) before anthracyclines or HER2-targeted therapy",
        guideline_key="esc_cardio_onc_2022",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.B,
        category=RecommendationCategory.DIAGNOSTIC,
        urgency=Urgency.SOON,
        section="4",
        rationale="LVEF and GLS are key baseline parameters for monitoring",
    ))
    
    if risk_category in [CardiotoxicityRisk.HIGH, CardiotoxicityRisk.VERY_HIGH]:
        recommendations.append(guideline_recommendation(
            action="Baseline cardiac biomarkers (troponin, BNP/NT-proBNP)",
            guideline_key="esc_cardio_onc_2022",
            evidence_class=EvidenceClass.IIA,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.DIAGNOSTIC,
            urgency=Urgency.SOON,
            section="4",
        ))
        
        recommendations.append(guideline_recommendation(
            action="Cardiology/cardio-oncology consultation before starting therapy",
            guideline_key="esc_cardio_onc_2022",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.REFERRAL,
            urgency=Urgency.SOON,
            section="4",
            rationale=f"High/very high baseline risk (score {total_score})",
        ))
    
    # CV risk optimization
    if hypertension or diabetes or hyperlipidemia:
        recommendations.append(guideline_recommendation(
            action="Optimize CV risk factors before cancer therapy",
            guideline_key="esc_cardio_onc_2022",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.PHARMACOTHERAPY,
            urgency=Urgency.SOON,
            section="4",
            rationale="BP, glucose, lipid control reduce cardiotoxicity risk",
        ))
    
    return BaselineRiskAssessment(
        risk_category=risk_category,
        hfa_icos_score=total_score,
        risk_factors=risk_factors,
        recommendations=recommendations,
        monitoring_intensity=monitoring,
        cardiology_referral_needed=referral,
        can_proceed_with_therapy=True,  # Usually can proceed with precautions
        precautions=precautions,
    )


def assess_anthracycline_risk(
    planned_cumulative_dose: float,  # mg/m2 doxorubicin equivalent
    prior_anthracycline_dose: float = 0,
    age: Optional[int] = None,
    lvef: Optional[float] = None,
    hypertension: bool = False,
    diabetes: bool = False,
    prior_chest_radiation: bool = False,
) -> BaselineRiskAssessment:
    """
    Assess risk specifically for anthracycline therapy.
    
    Per ESC 2022 Section 5.1.
    
    Doxorubicin equivalent doses:
    - Doxorubicin: 1.0
    - Epirubicin: 0.67
    - Daunorubicin: 0.83
    - Idarubicin: 5.0
    - Mitoxantrone: 4.0
    
    Risk increases with cumulative dose:
    - <250 mg/m2: Low risk (~1-2%)
    - 250-400 mg/m2: Moderate risk (~5-8%)
    - 400-550 mg/m2: High risk (~16-26%)
    - >550 mg/m2: Very high risk (>30%)
    
    Args:
        planned_cumulative_dose: Planned cumulative dose (doxorubicin equivalent)
        prior_anthracycline_dose: Previous anthracycline exposure
        Other risk factors
    
    Returns:
        BaselineRiskAssessment
    """
    total_dose = prior_anthracycline_dose + planned_cumulative_dose
    risk_factors = []
    precautions = []
    recommendations = []
    
    # Dose-based risk
    if total_dose >= 550:
        risk_category = CardiotoxicityRisk.VERY_HIGH
        risk_factors.append(CVRiskFactor(f"Cumulative dose >= 550 mg/m2 ({total_dose})", True, 5))
        precautions.append("Cumulative dose exceeds threshold - consider alternative regimen")
    elif total_dose >= 400:
        risk_category = CardiotoxicityRisk.HIGH
        risk_factors.append(CVRiskFactor(f"Cumulative dose 400-550 mg/m2 ({total_dose})", True, 3))
    elif total_dose >= 250:
        risk_category = CardiotoxicityRisk.MODERATE
        risk_factors.append(CVRiskFactor(f"Cumulative dose 250-400 mg/m2 ({total_dose})", True, 2))
    else:
        risk_category = CardiotoxicityRisk.LOW
    
    # Age modifiers
    if age is not None:
        if age >= 65:
            risk_factors.append(CVRiskFactor(f"Age >= 65 ({age})", True, 2))
            if risk_category == CardiotoxicityRisk.LOW:
                risk_category = CardiotoxicityRisk.MODERATE
        if age < 18:
            risk_factors.append(CVRiskFactor(f"Pediatric age ({age})", True, 1))
            precautions.append("Children have increased lifetime risk - long-term surveillance needed")
    
    # LVEF
    if lvef is not None and lvef < 55:
        risk_factors.append(CVRiskFactor(f"Borderline LVEF ({lvef}%)", True, 3))
        if risk_category in [CardiotoxicityRisk.LOW, CardiotoxicityRisk.MODERATE]:
            risk_category = CardiotoxicityRisk.HIGH
    
    # Prior radiation
    if prior_chest_radiation:
        risk_factors.append(CVRiskFactor("Prior chest radiation", True, 2))
        if risk_category == CardiotoxicityRisk.LOW:
            risk_category = CardiotoxicityRisk.MODERATE
    
    # Recommendations
    recommendations.append(guideline_recommendation(
        action="Echo with GLS before anthracycline therapy",
        guideline_key="esc_cardio_onc_2022",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.B,
        category=RecommendationCategory.DIAGNOSTIC,
        urgency=Urgency.SOON,
        section="5.1",
    ))
    
    if risk_category in [CardiotoxicityRisk.HIGH, CardiotoxicityRisk.VERY_HIGH]:
        recommendations.append(guideline_recommendation(
            action="Consider cardioprotection with dexrazoxane if cumulative dose > 300 mg/m2",
            guideline_key="esc_cardio_onc_2022",
            evidence_class=EvidenceClass.IIA,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PHARMACOTHERAPY,
            urgency=Urgency.SOON,
            section="5.1",
            rationale="Dexrazoxane reduces anthracycline cardiotoxicity",
        ))
        
        recommendations.append(guideline_recommendation(
            action="Consider prophylactic ACE-I/ARB and/or beta-blocker",
            guideline_key="esc_cardio_onc_2022",
            evidence_class=EvidenceClass.IIB,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PHARMACOTHERAPY,
            urgency=Urgency.ROUTINE,
            section="5.1",
            rationale="May reduce cardiotoxicity incidence in high-risk patients",
            studies=["OVERCOME", "PRADA", "CECCY"],
        ))
    
    if total_dose >= 400:
        recommendations.append(guideline_recommendation(
            action="Consider liposomal doxorubicin formulation to reduce cardiotoxicity",
            guideline_key="esc_cardio_onc_2022",
            evidence_class=EvidenceClass.IIA,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PHARMACOTHERAPY,
            urgency=Urgency.ROUTINE,
            section="5.1",
        ))
    
    return BaselineRiskAssessment(
        risk_category=risk_category,
        risk_factors=risk_factors,
        recommendations=recommendations,
        monitoring_intensity="enhanced" if risk_category != CardiotoxicityRisk.LOW else "standard",
        cardiology_referral_needed=risk_category in [CardiotoxicityRisk.HIGH, CardiotoxicityRisk.VERY_HIGH],
        precautions=precautions,
    )


def assess_her2_therapy_risk(
    concurrent_anthracycline: bool = False,
    prior_anthracycline: bool = False,
    prior_anthracycline_dose: Optional[float] = None,
    lvef: Optional[float] = None,
    age: Optional[int] = None,
    hypertension: bool = False,
    obesity: bool = False,
) -> BaselineRiskAssessment:
    """
    Assess risk for HER2-targeted therapy (trastuzumab, pertuzumab).
    
    Per ESC 2022 Section 5.2.
    
    Key points:
    - HER2 inhibitor cardiotoxicity is usually reversible
    - Risk increased with concurrent/prior anthracycline
    - LVEF < 50% is relative contraindication
    
    Args:
        concurrent_anthracycline: Concurrent anthracycline use
        prior_anthracycline: Prior anthracycline exposure
        Other risk factors
    
    Returns:
        BaselineRiskAssessment
    """
    risk_factors = []
    precautions = []
    recommendations = []
    
    # LVEF is critical
    if lvef is not None:
        if lvef < 50:
            risk_factors.append(CVRiskFactor(f"LVEF < 50% ({lvef}%)", True, 5))
            precautions.append("LVEF < 50% - trastuzumab relatively contraindicated, discuss with cardio-oncology")
            risk_category = CardiotoxicityRisk.VERY_HIGH
        elif lvef < 55:
            risk_factors.append(CVRiskFactor(f"LVEF 50-54% ({lvef}%)", True, 2))
            risk_category = CardiotoxicityRisk.HIGH
        else:
            risk_category = CardiotoxicityRisk.LOW
    else:
        risk_category = CardiotoxicityRisk.MODERATE
        precautions.append("LVEF not available - must obtain before starting HER2 therapy")
    
    # Anthracycline interaction
    if concurrent_anthracycline:
        risk_factors.append(CVRiskFactor("Concurrent anthracycline", True, 3))
        precautions.append("Concurrent anthracycline + trastuzumab - highest cardiotoxicity risk")
        if risk_category.value in ["low", "moderate"]:
            risk_category = CardiotoxicityRisk.HIGH
    
    if prior_anthracycline:
        dose_str = f" ({prior_anthracycline_dose} mg/m2)" if prior_anthracycline_dose else ""
        risk_factors.append(CVRiskFactor(f"Prior anthracycline{dose_str}", True, 2))
        if risk_category == CardiotoxicityRisk.LOW:
            risk_category = CardiotoxicityRisk.MODERATE
    
    # Other factors
    if age and age >= 65:
        risk_factors.append(CVRiskFactor(f"Age >= 65 ({age})", True, 1))
    
    if hypertension:
        risk_factors.append(CVRiskFactor("Hypertension", True, 1))
    
    if obesity:
        risk_factors.append(CVRiskFactor("Obesity", True, 1))
    
    # Recommendations
    recommendations.append(guideline_recommendation(
        action="Baseline echocardiogram with LVEF and GLS before HER2 therapy",
        guideline_key="esc_cardio_onc_2022",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.B,
        category=RecommendationCategory.DIAGNOSTIC,
        urgency=Urgency.SOON,
        section="5.2",
    ))
    
    recommendations.append(guideline_recommendation(
        action="Repeat echocardiogram every 3 months during HER2 therapy",
        guideline_key="esc_cardio_onc_2022",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.B,
        category=RecommendationCategory.MONITORING,
        urgency=Urgency.ROUTINE,
        section="5.2",
        rationale="HER2 cardiotoxicity is often reversible if detected early",
    ))
    
    if risk_category in [CardiotoxicityRisk.HIGH, CardiotoxicityRisk.VERY_HIGH]:
        recommendations.append(guideline_recommendation(
            action="Cardio-oncology consultation before HER2 therapy",
            guideline_key="esc_cardio_onc_2022",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.REFERRAL,
            urgency=Urgency.SOON,
            section="5.2",
        ))
    
    return BaselineRiskAssessment(
        risk_category=risk_category,
        risk_factors=risk_factors,
        recommendations=recommendations,
        monitoring_intensity="enhanced",  # Always enhanced for HER2
        cardiology_referral_needed=risk_category in [CardiotoxicityRisk.HIGH, CardiotoxicityRisk.VERY_HIGH],
        can_proceed_with_therapy=lvef is None or lvef >= 50,
        precautions=precautions,
    )


def assess_baseline_cv_risk(patient: "Patient", planned_therapy: List[CancerTherapyType]) -> RecommendationSet:
    """
    Comprehensive baseline CV risk assessment for a patient.
    
    Args:
        patient: Patient object
        planned_therapy: List of planned cancer therapies
    
    Returns:
        RecommendationSet with baseline assessment recommendations
    """
    rec_set = RecommendationSet(
        title="Baseline Cardiovascular Risk Assessment",
        description="Per ESC 2022 Cardio-Oncology Guidelines",
        primary_guideline="ESC Cardio-Oncology 2022",
    )
    
    # General HFA-ICOS assessment
    hfa_icos = calculate_hfa_icos_risk(
        heart_failure=patient.has_diagnosis("heart_failure"),
        cardiomyopathy=patient.has_diagnosis("cardiomyopathy"),
        mi_or_pci_cabg=patient.has_diagnosis("mi") or patient.has_diagnosis("coronary_artery_disease"),
        hypertension=patient.has_diagnosis("hypertension"),
        diabetes=patient.has_diagnosis("diabetes"),
        lvef=patient.lvef,
        age=patient.age,
    )
    
    rec_set.add_all(hfa_icos.recommendations)
    rec_set.description += f"\n\nHFA-ICOS Risk: {hfa_icos.risk_category.value.upper()} (score: {hfa_icos.hfa_icos_score})"
    
    if hfa_icos.precautions:
        rec_set.description += "\nPrecautions: " + "; ".join(hfa_icos.precautions)
    
    return rec_set
