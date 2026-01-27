"""
Hypertension Diagnosis and Classification (ESC 2024).

Blood pressure classification and cardiovascular risk assessment.
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional, List, Dict, Any

from cardiocode.core.types import Patient
from cardiocode.core.recommendation import (
    Recommendation,
    RecommendationSet,
    RecommendationCategory,
    Urgency,
    guideline_recommendation,
)
from cardiocode.core.evidence import EvidenceClass, EvidenceLevel


class BPCategory(Enum):
    """Blood pressure categories per ESC 2024."""
    OPTIMAL = "optimal"                    # <120/80
    NORMAL = "normal"                      # 120-129/80-84
    HIGH_NORMAL = "high_normal"            # 130-139/85-89
    GRADE_1_HTN = "grade_1_hypertension"   # 140-159/90-99
    GRADE_2_HTN = "grade_2_hypertension"   # 160-179/100-109
    GRADE_3_HTN = "grade_3_hypertension"   # >=180/>=110
    ISOLATED_SYSTOLIC = "isolated_systolic_hypertension"  # >=140/<90


class CVRiskCategory(Enum):
    """Cardiovascular risk categories."""
    LOW = "low"                    # <5% 10-year risk
    MODERATE = "moderate"          # 5-10% 10-year risk
    HIGH = "high"                  # 10-20% 10-year risk
    VERY_HIGH = "very_high"        # >20% 10-year risk


@dataclass
class BPClassificationResult:
    """Result of blood pressure classification."""
    systolic: int
    diastolic: int
    category: BPCategory
    interpretation: str
    requires_confirmation: bool
    recommendation: str


@dataclass
class CVRiskResult:
    """Result of cardiovascular risk assessment."""
    risk_category: CVRiskCategory
    risk_factors: List[str]
    hmod: List[str]  # Hypertension-mediated organ damage
    established_cvd: bool
    interpretation: str
    treatment_threshold: str


def classify_blood_pressure(
    systolic: int,
    diastolic: int,
    is_office_measurement: bool = True,
) -> BPClassificationResult:
    """
    Classify blood pressure according to ESC 2024 guidelines.

    Args:
        systolic: Systolic blood pressure (mmHg)
        diastolic: Diastolic blood pressure (mmHg)
        is_office_measurement: True if office BP, False if home/ambulatory

    Returns:
        BPClassificationResult with category and interpretation
    """
    # Classification based on higher category
    if systolic >= 180 or diastolic >= 110:
        category = BPCategory.GRADE_3_HTN
        interpretation = f"Grade 3 hypertension (severe): {systolic}/{diastolic} mmHg"
        requires_confirmation = True
        recommendation = "Urgent assessment needed. Consider immediate treatment if symptomatic or with acute organ damage."

    elif systolic >= 160 or diastolic >= 100:
        category = BPCategory.GRADE_2_HTN
        interpretation = f"Grade 2 hypertension (moderate): {systolic}/{diastolic} mmHg"
        requires_confirmation = True
        recommendation = "Confirm with repeat measurements. Drug treatment usually indicated."

    elif systolic >= 140 or diastolic >= 90:
        if systolic >= 140 and diastolic < 90:
            category = BPCategory.ISOLATED_SYSTOLIC
            interpretation = f"Isolated systolic hypertension: {systolic}/{diastolic} mmHg"
        else:
            category = BPCategory.GRADE_1_HTN
            interpretation = f"Grade 1 hypertension (mild): {systolic}/{diastolic} mmHg"
        requires_confirmation = True
        recommendation = "Confirm diagnosis with out-of-office BP measurement (ABPM or HBPM). Assess CV risk."

    elif systolic >= 130 or diastolic >= 85:
        category = BPCategory.HIGH_NORMAL
        interpretation = f"High-normal BP: {systolic}/{diastolic} mmHg"
        requires_confirmation = False
        recommendation = "Lifestyle modification. Reassess periodically. Consider treatment if high CV risk."

    elif systolic >= 120 or diastolic >= 80:
        category = BPCategory.NORMAL
        interpretation = f"Normal BP: {systolic}/{diastolic} mmHg"
        requires_confirmation = False
        recommendation = "Lifestyle advice. Reassess in 3 years."

    else:
        category = BPCategory.OPTIMAL
        interpretation = f"Optimal BP: {systolic}/{diastolic} mmHg"
        requires_confirmation = False
        recommendation = "No intervention needed. Reassess in 5 years."

    # Adjust for office vs out-of-office
    if not is_office_measurement:
        interpretation += " (out-of-office measurement)"

    return BPClassificationResult(
        systolic=systolic,
        diastolic=diastolic,
        category=category,
        interpretation=interpretation,
        requires_confirmation=requires_confirmation,
        recommendation=recommendation,
    )


def assess_cv_risk(
    bp_category: BPCategory,
    age: int,
    male: bool = True,
    smoking: bool = False,
    dyslipidemia: bool = False,
    diabetes: bool = False,
    obesity: bool = False,
    family_history_cvd: bool = False,
    # Hypertension-mediated organ damage (HMOD)
    lvh: bool = False,
    ckd_stage_3: bool = False,
    microalbuminuria: bool = False,
    retinopathy: bool = False,
    pulse_wave_velocity_elevated: bool = False,
    # Established CVD
    coronary_artery_disease: bool = False,
    stroke_tia: bool = False,
    heart_failure: bool = False,
    atrial_fibrillation: bool = False,
    peripheral_artery_disease: bool = False,
    ckd_stage_4_5: bool = False,
) -> CVRiskResult:
    """
    Assess cardiovascular risk in hypertension.

    ESC 2024 Hypertension Guidelines - Risk stratification.

    Args:
        bp_category: Blood pressure category
        age: Patient age
        male: Male sex
        smoking: Current smoking
        dyslipidemia: Dyslipidemia
        diabetes: Diabetes mellitus
        obesity: Obesity (BMI >= 30)
        family_history_cvd: Family history of premature CVD
        lvh: Left ventricular hypertrophy
        ckd_stage_3: CKD stage 3 (eGFR 30-59)
        microalbuminuria: Microalbuminuria
        retinopathy: Hypertensive retinopathy
        pulse_wave_velocity_elevated: PWV > 10 m/s
        coronary_artery_disease: Established CAD
        stroke_tia: Prior stroke or TIA
        heart_failure: Heart failure
        atrial_fibrillation: Atrial fibrillation
        peripheral_artery_disease: PAD
        ckd_stage_4_5: CKD stage 4-5

    Returns:
        CVRiskResult with risk category and recommendations
    """
    risk_factors = []
    hmod = []
    established_cvd = False

    # Count risk factors
    if male:
        risk_factors.append("Male sex")
    if age >= 55 if male else age >= 65:
        risk_factors.append("Age")
    if smoking:
        risk_factors.append("Smoking")
    if dyslipidemia:
        risk_factors.append("Dyslipidemia")
    if diabetes:
        risk_factors.append("Diabetes")
    if obesity:
        risk_factors.append("Obesity")
    if family_history_cvd:
        risk_factors.append("Family history of CVD")

    # Check HMOD
    if lvh:
        hmod.append("LV hypertrophy")
    if ckd_stage_3:
        hmod.append("CKD stage 3")
    if microalbuminuria:
        hmod.append("Microalbuminuria")
    if retinopathy:
        hmod.append("Hypertensive retinopathy")
    if pulse_wave_velocity_elevated:
        hmod.append("Elevated pulse wave velocity")

    # Check established CVD
    cvd_conditions = []
    if coronary_artery_disease:
        cvd_conditions.append("CAD")
        established_cvd = True
    if stroke_tia:
        cvd_conditions.append("Stroke/TIA")
        established_cvd = True
    if heart_failure:
        cvd_conditions.append("Heart failure")
        established_cvd = True
    if atrial_fibrillation:
        cvd_conditions.append("Atrial fibrillation")
        established_cvd = True
    if peripheral_artery_disease:
        cvd_conditions.append("PAD")
        established_cvd = True
    if ckd_stage_4_5:
        cvd_conditions.append("CKD stage 4-5")
        established_cvd = True

    # Determine risk category
    if established_cvd or diabetes or ckd_stage_4_5:
        risk_category = CVRiskCategory.VERY_HIGH
        interpretation = "VERY HIGH CV risk due to established CVD, diabetes, or severe CKD"
        treatment_threshold = "Treat if BP >= 130/80 mmHg"

    elif len(hmod) >= 1 or len(risk_factors) >= 3:
        if bp_category in [BPCategory.GRADE_2_HTN, BPCategory.GRADE_3_HTN]:
            risk_category = CVRiskCategory.VERY_HIGH
            interpretation = "VERY HIGH CV risk due to HMOD/multiple risk factors + grade 2-3 HTN"
            treatment_threshold = "Drug treatment indicated"
        else:
            risk_category = CVRiskCategory.HIGH
            interpretation = "HIGH CV risk due to HMOD or multiple risk factors"
            treatment_threshold = "Drug treatment if BP >= 140/90 mmHg"

    elif len(risk_factors) == 2:
        if bp_category in [BPCategory.GRADE_2_HTN, BPCategory.GRADE_3_HTN]:
            risk_category = CVRiskCategory.HIGH
        else:
            risk_category = CVRiskCategory.MODERATE
        interpretation = f"{'HIGH' if risk_category == CVRiskCategory.HIGH else 'MODERATE'} CV risk"
        treatment_threshold = "Drug treatment if BP >= 140/90 mmHg"

    elif len(risk_factors) == 1:
        if bp_category == BPCategory.GRADE_3_HTN:
            risk_category = CVRiskCategory.HIGH
        else:
            risk_category = CVRiskCategory.MODERATE
        interpretation = f"{'HIGH' if risk_category == CVRiskCategory.HIGH else 'MODERATE'} CV risk"
        treatment_threshold = "Drug treatment if BP >= 140/90 mmHg (or 160/100 if low risk)"

    else:
        if bp_category == BPCategory.GRADE_3_HTN:
            risk_category = CVRiskCategory.MODERATE
        else:
            risk_category = CVRiskCategory.LOW
        interpretation = f"{'MODERATE' if risk_category == CVRiskCategory.MODERATE else 'LOW'} CV risk"
        treatment_threshold = "Lifestyle modification; drug treatment if BP >= 160/100 mmHg"

    return CVRiskResult(
        risk_category=risk_category,
        risk_factors=risk_factors,
        hmod=hmod,
        established_cvd=established_cvd,
        interpretation=interpretation,
        treatment_threshold=treatment_threshold,
    )
