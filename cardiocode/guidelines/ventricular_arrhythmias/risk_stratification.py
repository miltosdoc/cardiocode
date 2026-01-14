"""
SCD Risk Stratification - ESC 2022 VA/SCD Guidelines.

Implements SCD risk stratification algorithms from ESC 2022:
- General SCD risk assessment
- Disease-specific risk scores (HCM, ARVC, DCM)
- Risk factor identification
"""

from __future__ import annotations
from typing import Optional, List, TYPE_CHECKING
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


class SCDRiskCategory(Enum):
    """SCD risk stratification category."""
    LOW = "low"               # <4% 5-year risk
    INTERMEDIATE = "intermediate"  # 4-6% 5-year risk
    HIGH = "high"             # >6% 5-year risk


class Cardiomyopathy(Enum):
    """Types of cardiomyopathy for risk stratification."""
    HCM = "hypertrophic"
    DCM = "dilated"
    ARVC = "arrhythmogenic_right_ventricular"
    ISCHEMIC = "ischemic"
    NON_ISCHEMIC = "non_ischemic"


@dataclass
class SCDRiskAssessment:
    """Result of SCD risk stratification."""
    risk_category: SCDRiskCategory
    five_year_risk_percent: Optional[float] = None
    risk_factors: List[str] = field(default_factory=list)
    protective_factors: List[str] = field(default_factory=list)
    icd_recommendation: Optional[str] = None
    score_name: Optional[str] = None
    rationale: str = ""
    recommendations: List[Recommendation] = field(default_factory=list)


def calculate_hcm_scd_risk(
    age: int,
    max_wall_thickness: float,  # mm
    la_diameter: float,  # mm
    max_lvot_gradient: float,  # mmHg
    family_history_scd: bool = False,
    nsvt: bool = False,  # Non-sustained VT
    unexplained_syncope: bool = False,
) -> SCDRiskAssessment:
    """
    Calculate 5-year SCD risk in HCM using ESC HCM Risk-SCD score.
    
    Per ESC 2022 VA/SCD Guidelines Section 7.1.1 and ESC HCM 2014.
    
    Formula:
    Risk = 1 - 0.998^exp(prognostic index)
    
    Where prognostic index includes:
    - Age
    - Maximal wall thickness
    - LA diameter
    - Max LVOT gradient
    - Family history of SCD
    - NSVT
    - Unexplained syncope
    
    Args:
        age: Patient age in years (16-80)
        max_wall_thickness: Maximum LV wall thickness in mm
        la_diameter: Left atrial diameter in mm
        max_lvot_gradient: Maximum LVOT gradient at rest or Valsalva in mmHg
        family_history_scd: Family history of SCD in first-degree relative <40 years
        nsvt: Non-sustained VT on Holter (>=3 beats, >=120 bpm)
        unexplained_syncope: Syncope not due to neurocardiogenic mechanism
    
    Returns:
        SCDRiskAssessment with 5-year risk and ICD recommendation
    """
    risk_factors = []
    
    # Coefficients from HCM Risk-SCD model
    # Simplified calculation (actual model uses complex formula)
    prognostic_index = 0.0
    
    # Age (negative coefficient - younger = higher risk)
    prognostic_index += 0.15939858 * max_wall_thickness
    prognostic_index += -0.00294271 * max_wall_thickness ** 2
    prognostic_index += 0.0259082 * la_diameter
    prognostic_index += 0.00446131 * max_lvot_gradient
    prognostic_index += 0.4583082 if family_history_scd else 0
    prognostic_index += 0.82639195 if nsvt else 0
    prognostic_index += 0.71650361 if unexplained_syncope else 0
    prognostic_index += -0.01799934 * age
    
    # Calculate 5-year risk
    five_year_risk = 1 - (0.998 ** (5 * (prognostic_index - 0.5)))
    five_year_risk = max(0, min(1, five_year_risk))  # Clamp to 0-100%
    five_year_risk_percent = five_year_risk * 100
    
    # Collect risk factors
    if max_wall_thickness >= 30:
        risk_factors.append(f"Severe LVH (wall thickness {max_wall_thickness}mm >= 30mm)")
    elif max_wall_thickness >= 25:
        risk_factors.append(f"Marked LVH (wall thickness {max_wall_thickness}mm)")
    
    if family_history_scd:
        risk_factors.append("Family history of SCD")
    if nsvt:
        risk_factors.append("Non-sustained VT")
    if unexplained_syncope:
        risk_factors.append("Unexplained syncope")
    if max_lvot_gradient >= 30:
        risk_factors.append(f"LVOT obstruction ({max_lvot_gradient}mmHg)")
    if la_diameter >= 45:
        risk_factors.append(f"LA enlargement ({la_diameter}mm)")
    
    # Determine risk category and ICD recommendation
    if five_year_risk_percent >= 6:
        risk_category = SCDRiskCategory.HIGH
        icd_rec = "ICD should be considered"
        evidence_class = EvidenceClass.IIA
    elif five_year_risk_percent >= 4:
        risk_category = SCDRiskCategory.INTERMEDIATE
        icd_rec = "ICD may be considered after detailed clinical assessment"
        evidence_class = EvidenceClass.IIB
    else:
        risk_category = SCDRiskCategory.LOW
        icd_rec = "ICD generally not indicated for primary prevention"
        evidence_class = EvidenceClass.III
    
    recommendations = []
    if risk_category in [SCDRiskCategory.HIGH, SCDRiskCategory.INTERMEDIATE]:
        recommendations.append(guideline_recommendation(
            action=f"{icd_rec} for primary prevention of SCD (HCM Risk-SCD {five_year_risk_percent:.1f}%)",
            guideline_key="esc_va_scd_2022",
            evidence_class=evidence_class,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.DEVICE,
            urgency=Urgency.ROUTINE if risk_category == SCDRiskCategory.INTERMEDIATE else Urgency.SOON,
            section="7.1.1",
            rationale=f"5-year SCD risk {five_year_risk_percent:.1f}% by HCM Risk-SCD calculator",
            conditions=["HCM diagnosis confirmed", "No reversible cause of arrhythmia"],
        ))
    
    return SCDRiskAssessment(
        risk_category=risk_category,
        five_year_risk_percent=five_year_risk_percent,
        risk_factors=risk_factors,
        icd_recommendation=icd_rec,
        score_name="HCM Risk-SCD",
        rationale=f"5-year SCD risk calculated at {five_year_risk_percent:.1f}%",
        recommendations=recommendations,
    )


def calculate_arvc_risk(
    male: bool,
    age: int,
    nsvt: bool = False,
    pvc_count_24h: Optional[int] = None,  # PVCs per 24h
    num_leads_twave_inversion: int = 0,
    rvef: Optional[float] = None,  # %
    syncope: bool = False,
    prior_sustained_vt_vf: bool = False,
) -> SCDRiskAssessment:
    """
    ARVC risk stratification per ESC 2022 VA/SCD Guidelines.
    
    Per Section 7.1.2: Risk factors for SCD in ARVC include:
    - Prior cardiac arrest / sustained VT
    - Unexplained syncope
    - Severe RV dysfunction
    - LV involvement
    - Male sex
    - NSVT
    - Multiple gene mutations
    
    Args:
        male: Male sex
        age: Age in years
        nsvt: Non-sustained VT
        pvc_count_24h: 24-hour PVC count
        num_leads_twave_inversion: Number of leads with T-wave inversion
        rvef: Right ventricular ejection fraction (%)
        syncope: Unexplained syncope
        prior_sustained_vt_vf: Prior sustained VT/VF or SCD
    
    Returns:
        SCDRiskAssessment
    """
    risk_factors = []
    protective_factors = []
    recommendations = []
    
    # Secondary prevention takes precedence
    if prior_sustained_vt_vf:
        risk_factors.append("Prior sustained VT/VF or cardiac arrest")
        recommendations.append(guideline_recommendation(
            action="ICD implantation for secondary prevention of SCD",
            guideline_key="esc_va_scd_2022",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.DEVICE,
            urgency=Urgency.URGENT,
            section="7.1.2",
            rationale="Survivor of sustained VT/VF in ARVC",
            studies=["ARVC registries"],
        ))
        return SCDRiskAssessment(
            risk_category=SCDRiskCategory.HIGH,
            risk_factors=risk_factors,
            icd_recommendation="ICD recommended (secondary prevention)",
            score_name="ARVC clinical assessment",
            rationale="Secondary prevention indication based on prior sustained arrhythmia",
            recommendations=recommendations,
        )
    
    # Primary prevention risk assessment
    risk_score = 0
    
    if male:
        risk_score += 1
        risk_factors.append("Male sex")
    
    if syncope:
        risk_score += 2
        risk_factors.append("Unexplained syncope")
    
    if nsvt:
        risk_score += 1
        risk_factors.append("Non-sustained VT")
    
    if pvc_count_24h and pvc_count_24h > 1000:
        risk_score += 1
        risk_factors.append(f"High PVC burden ({pvc_count_24h}/24h)")
    
    if num_leads_twave_inversion >= 3:
        risk_score += 1
        risk_factors.append(f"Extensive T-wave inversion ({num_leads_twave_inversion} leads)")
    
    if rvef and rvef < 40:
        risk_score += 2
        risk_factors.append(f"RV dysfunction (RVEF {rvef}%)")
    
    if age < 25:
        risk_factors.append("Young age at presentation")
    else:
        protective_factors.append("Age >= 25 years")
    
    # Categorize risk
    if risk_score >= 4:
        risk_category = SCDRiskCategory.HIGH
        icd_rec = "ICD should be considered for primary prevention"
        evidence_class = EvidenceClass.IIA
    elif risk_score >= 2:
        risk_category = SCDRiskCategory.INTERMEDIATE
        icd_rec = "ICD may be considered after multidisciplinary assessment"
        evidence_class = EvidenceClass.IIB
    else:
        risk_category = SCDRiskCategory.LOW
        icd_rec = "ICD not routinely indicated - continue surveillance"
        evidence_class = EvidenceClass.III
    
    if risk_category != SCDRiskCategory.LOW:
        recommendations.append(guideline_recommendation(
            action=icd_rec,
            guideline_key="esc_va_scd_2022",
            evidence_class=evidence_class,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.DEVICE,
            urgency=Urgency.SOON,
            section="7.1.2",
            rationale=f"Multiple SCD risk factors present ({risk_score} points)",
        ))
    
    return SCDRiskAssessment(
        risk_category=risk_category,
        risk_factors=risk_factors,
        protective_factors=protective_factors,
        icd_recommendation=icd_rec,
        score_name="ARVC clinical risk assessment",
        rationale=f"Risk score {risk_score} based on clinical parameters",
        recommendations=recommendations,
    )


def stratify_scd_risk_dcm(
    lvef: float,
    lge_present: bool = False,  # Late gadolinium enhancement on CMR
    lge_extent_percent: Optional[float] = None,
    nsvt: bool = False,
    nyha_class: int = 2,
    genetic_mutation: Optional[str] = None,  # LMNA, PLN, etc.
    syncope: bool = False,
    prior_sustained_vt_vf: bool = False,
) -> SCDRiskAssessment:
    """
    SCD risk stratification in dilated cardiomyopathy.
    
    Per ESC 2022 VA/SCD Guidelines Section 7.1.3.
    
    Key risk markers:
    - LVEF (primary criterion for ICD)
    - LGE on CMR (independent predictor)
    - Specific mutations (LMNA, PLN, FLNC, RBM20)
    - NSVT
    - Syncope
    
    Args:
        lvef: LV ejection fraction (%)
        lge_present: Late gadolinium enhancement on CMR
        lge_extent_percent: Extent of LGE (% of LV mass)
        nsvt: Non-sustained VT
        nyha_class: NYHA functional class (1-4)
        genetic_mutation: Known pathogenic mutation
        syncope: Unexplained syncope
        prior_sustained_vt_vf: Prior sustained VT/VF
    
    Returns:
        SCDRiskAssessment
    """
    risk_factors = []
    recommendations = []
    
    # High-risk mutations
    high_risk_mutations = ["LMNA", "PLN", "FLNC", "RBM20"]
    
    # Secondary prevention
    if prior_sustained_vt_vf:
        risk_factors.append("Prior sustained VT/VF")
        recommendations.append(guideline_recommendation(
            action="ICD implantation for secondary prevention of SCD",
            guideline_key="esc_va_scd_2022",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.A,
            category=RecommendationCategory.DEVICE,
            urgency=Urgency.URGENT,
            section="7.1.3",
            rationale="Secondary prevention in DCM with prior sustained arrhythmia",
        ))
        return SCDRiskAssessment(
            risk_category=SCDRiskCategory.HIGH,
            risk_factors=risk_factors,
            icd_recommendation="ICD recommended (secondary prevention)",
            recommendations=recommendations,
        )
    
    # Primary prevention based on LVEF
    if lvef <= 35:
        risk_factors.append(f"Severely reduced LVEF ({lvef}%)")
    elif lvef <= 45:
        risk_factors.append(f"Reduced LVEF ({lvef}%)")
    
    # LGE adds risk
    if lge_present:
        risk_factors.append("LGE on CMR (fibrosis)")
        if lge_extent_percent and lge_extent_percent > 10:
            risk_factors.append(f"Extensive LGE ({lge_extent_percent}% of LV)")
    
    # Genetic mutations
    if genetic_mutation:
        if genetic_mutation.upper() in high_risk_mutations:
            risk_factors.append(f"High-risk mutation ({genetic_mutation})")
        else:
            risk_factors.append(f"Pathogenic mutation ({genetic_mutation})")
    
    if nsvt:
        risk_factors.append("Non-sustained VT")
    
    if syncope:
        risk_factors.append("Unexplained syncope")
    
    # Risk stratification logic
    has_high_risk_mutation = genetic_mutation and genetic_mutation.upper() in high_risk_mutations
    
    # LMNA and other high-risk mutations - ICD at higher LVEF threshold
    if has_high_risk_mutation and lvef < 50:
        if nsvt or syncope or lvef < 45:
            risk_category = SCDRiskCategory.HIGH
            recommendations.append(guideline_recommendation(
                action=f"ICD should be considered for primary prevention ({genetic_mutation} mutation with LVEF {lvef}%)",
                guideline_key="esc_va_scd_2022",
                evidence_class=EvidenceClass.IIA,
                evidence_level=EvidenceLevel.B,
                category=RecommendationCategory.DEVICE,
                urgency=Urgency.SOON,
                section="7.1.3",
                rationale=f"High-risk genetic DCM ({genetic_mutation}) with additional risk factors",
                studies=["LMNA registry data"],
            ))
        else:
            risk_category = SCDRiskCategory.INTERMEDIATE
    # Standard DCM criteria
    elif lvef <= 35 and nyha_class in [2, 3]:
        risk_category = SCDRiskCategory.HIGH
        recommendations.append(guideline_recommendation(
            action="ICD for primary prevention of SCD in DCM with LVEF <= 35% and NYHA II-III",
            guideline_key="esc_va_scd_2022",
            evidence_class=EvidenceClass.IIA,
            evidence_level=EvidenceLevel.A,
            category=RecommendationCategory.DEVICE,
            urgency=Urgency.ROUTINE,
            section="7.1.3",
            rationale="DCM with severely reduced LVEF despite OMT",
            studies=["DANISH", "DEFINITE", "SCD-HeFT"],
            conditions=["On optimal medical therapy >= 3 months", "Expected survival > 1 year"],
        ))
    elif lvef <= 35:
        risk_category = SCDRiskCategory.INTERMEDIATE
    elif lge_present and (nsvt or syncope):
        risk_category = SCDRiskCategory.INTERMEDIATE
        risk_factors.append("LGE with additional arrhythmic markers")
    else:
        risk_category = SCDRiskCategory.LOW
    
    icd_rec = {
        SCDRiskCategory.HIGH: "ICD recommended for primary prevention",
        SCDRiskCategory.INTERMEDIATE: "ICD may be considered - individualized assessment needed",
        SCDRiskCategory.LOW: "ICD not routinely indicated",
    }[risk_category]
    
    return SCDRiskAssessment(
        risk_category=risk_category,
        risk_factors=risk_factors,
        icd_recommendation=icd_rec,
        score_name="DCM SCD risk assessment",
        rationale=f"Risk stratified based on LVEF, LGE, genetics, and arrhythmia markers",
        recommendations=recommendations,
    )


def stratify_scd_risk_ischemic(
    lvef: float,
    nyha_class: int,
    days_post_mi: Optional[int] = None,
    prior_sustained_vt_vf: bool = False,
    inducible_vt_eps: Optional[bool] = None,  # EPS result
    syncope: bool = False,
) -> SCDRiskAssessment:
    """
    SCD risk stratification in ischemic cardiomyopathy.
    
    Per ESC 2022 VA/SCD Guidelines Section 7.1.4.
    
    Key points:
    - ICD indicated if LVEF <= 35% and NYHA II-III despite 3 months OMT
    - Wait >= 40 days post-MI before primary prevention ICD
    - Wait >= 3 months post-revascularization
    
    Args:
        lvef: LV ejection fraction (%)
        nyha_class: NYHA functional class (1-4)
        days_post_mi: Days since MI (if applicable)
        prior_sustained_vt_vf: Prior sustained VT/VF
        inducible_vt_eps: VT inducible at EPS (if performed)
        syncope: Unexplained syncope
    
    Returns:
        SCDRiskAssessment
    """
    risk_factors = []
    recommendations = []
    
    # Secondary prevention
    if prior_sustained_vt_vf:
        risk_factors.append("Prior sustained VT/VF")
        recommendations.append(guideline_recommendation(
            action="ICD implantation for secondary prevention",
            guideline_key="esc_va_scd_2022",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.A,
            category=RecommendationCategory.DEVICE,
            urgency=Urgency.URGENT,
            section="7.1.4",
            rationale="Survivor of sustained VT/VF without reversible cause",
            studies=["AVID", "CIDS", "CASH"],
        ))
        return SCDRiskAssessment(
            risk_category=SCDRiskCategory.HIGH,
            risk_factors=risk_factors,
            icd_recommendation="ICD recommended (secondary prevention)",
            recommendations=recommendations,
        )
    
    # Timing considerations
    if days_post_mi is not None and days_post_mi < 40:
        return SCDRiskAssessment(
            risk_category=SCDRiskCategory.INTERMEDIATE,
            risk_factors=[f"Acute/recent MI ({days_post_mi} days ago)"],
            icd_recommendation="Wait >= 40 days post-MI before ICD for primary prevention",
            rationale="ICD in first 40 days post-MI did not show benefit (DINAMIT, IRIS)",
            recommendations=[guideline_recommendation(
                action="Defer ICD decision until >= 40 days post-MI; reassess LVEF",
                guideline_key="esc_va_scd_2022",
                evidence_class=EvidenceClass.III,
                evidence_level=EvidenceLevel.A,
                category=RecommendationCategory.DEVICE,
                urgency=Urgency.ROUTINE,
                section="7.1.4",
                rationale="No mortality benefit from early ICD post-MI",
                studies=["DINAMIT", "IRIS"],
            )],
        )
    
    # Primary prevention
    if lvef <= 35:
        risk_factors.append(f"LVEF {lvef}% <= 35%")
    
    if nyha_class >= 2:
        risk_factors.append(f"NYHA Class {nyha_class}")
    
    if syncope:
        risk_factors.append("Unexplained syncope")
    
    if inducible_vt_eps:
        risk_factors.append("Inducible VT at EPS")
    
    # Standard ICD indication
    if lvef <= 35 and nyha_class in [2, 3]:
        risk_category = SCDRiskCategory.HIGH
        recommendations.append(guideline_recommendation(
            action="ICD for primary prevention of SCD",
            guideline_key="esc_va_scd_2022",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.A,
            category=RecommendationCategory.DEVICE,
            urgency=Urgency.ROUTINE,
            section="7.1.4",
            rationale=f"Ischemic cardiomyopathy with LVEF {lvef}% and NYHA {nyha_class}",
            studies=["MADIT-II", "SCD-HeFT"],
            conditions=["On optimal medical therapy >= 3 months", "Expected survival > 1 year"],
        ))
    elif lvef <= 35 and nyha_class == 1:
        risk_category = SCDRiskCategory.INTERMEDIATE
        if inducible_vt_eps:
            recommendations.append(guideline_recommendation(
                action="ICD may be considered (LVEF <= 35%, NYHA I, inducible VT)",
                guideline_key="esc_va_scd_2022",
                evidence_class=EvidenceClass.IIB,
                evidence_level=EvidenceLevel.B,
                category=RecommendationCategory.DEVICE,
                urgency=Urgency.ROUTINE,
                section="7.1.4",
                rationale="Asymptomatic but inducible VT on EPS",
                studies=["MUSTT", "MADIT-I"],
            ))
    elif lvef <= 40 and (syncope or inducible_vt_eps):
        risk_category = SCDRiskCategory.INTERMEDIATE
    else:
        risk_category = SCDRiskCategory.LOW
    
    icd_rec = {
        SCDRiskCategory.HIGH: "ICD recommended for primary prevention",
        SCDRiskCategory.INTERMEDIATE: "ICD may be considered - EPS can help guide decision",
        SCDRiskCategory.LOW: "ICD not routinely indicated for primary prevention",
    }[risk_category]
    
    return SCDRiskAssessment(
        risk_category=risk_category,
        risk_factors=risk_factors,
        icd_recommendation=icd_rec,
        score_name="Ischemic CM SCD risk assessment",
        rationale=f"Based on LVEF, symptoms, and arrhythmic markers",
        recommendations=recommendations,
    )


def stratify_scd_risk(patient: "Patient") -> SCDRiskAssessment:
    """
    General SCD risk stratification based on patient's underlying condition.
    
    Routes to appropriate disease-specific algorithm.
    
    Args:
        patient: Patient object
    
    Returns:
        SCDRiskAssessment
    """
    # Check for specific cardiomyopathies
    if patient.has_diagnosis("hcm") or patient.has_diagnosis("hypertrophic_cardiomyopathy"):
        # Would need additional HCM-specific data
        return SCDRiskAssessment(
            risk_category=SCDRiskCategory.INTERMEDIATE,
            rationale="HCM detected - use calculate_hcm_scd_risk() with complete parameters",
        )
    
    if patient.has_diagnosis("arvc") or patient.has_diagnosis("arrhythmogenic_cardiomyopathy"):
        return SCDRiskAssessment(
            risk_category=SCDRiskCategory.INTERMEDIATE,
            rationale="ARVC detected - use calculate_arvc_risk() with complete parameters",
        )
    
    # Check for secondary prevention indication
    if patient.has_diagnosis("cardiac_arrest") or patient.has_diagnosis("ventricular_fibrillation"):
        return SCDRiskAssessment(
            risk_category=SCDRiskCategory.HIGH,
            risk_factors=["Prior cardiac arrest / VF"],
            icd_recommendation="ICD indicated for secondary prevention (Class I)",
            recommendations=[guideline_recommendation(
                action="ICD for secondary prevention of SCD",
                guideline_key="esc_va_scd_2022",
                evidence_class=EvidenceClass.I,
                evidence_level=EvidenceLevel.A,
                category=RecommendationCategory.DEVICE,
                urgency=Urgency.URGENT,
                section="7",
                rationale="Survivor of cardiac arrest / VF without reversible cause",
            )],
        )
    
    # Ischemic vs non-ischemic
    is_ischemic = patient.has_diagnosis("coronary_artery_disease") or patient.has_diagnosis("mi")
    
    if patient.lvef is None:
        return SCDRiskAssessment(
            risk_category=SCDRiskCategory.INTERMEDIATE,
            rationale="LVEF required for complete SCD risk assessment",
        )
    
    nyha = patient.nyha_class.value if patient.nyha_class else 2
    
    if is_ischemic:
        return stratify_scd_risk_ischemic(
            lvef=patient.lvef,
            nyha_class=nyha,
            prior_sustained_vt_vf=patient.has_diagnosis("ventricular_tachycardia"),
        )
    else:
        return stratify_scd_risk_dcm(
            lvef=patient.lvef,
            nyha_class=nyha,
            prior_sustained_vt_vf=patient.has_diagnosis("ventricular_tachycardia"),
        )
