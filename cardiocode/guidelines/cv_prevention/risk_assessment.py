"""
CV Prevention Risk Assessment (ESC 2021).

SCORE2 and SCORE2-OP risk calculators and risk stratification.
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional, List, Dict, Any


class CVRiskLevel(Enum):
    """CV risk levels per ESC 2021 Prevention Guidelines."""
    LOW_MODERATE = "low_to_moderate"  # <5% 10-year risk (age <50) or <10% (age >=50)
    HIGH = "high"                      # 5-10% (age <50) or 10-20% (age >=50)
    VERY_HIGH = "very_high"            # >=10% (age <50) or >=20% (age >=50)


class RiskRegion(Enum):
    """European cardiovascular risk regions."""
    LOW = "low"          # France, Spain, etc.
    MODERATE = "moderate"  # Germany, UK, etc.
    HIGH = "high"        # Poland, etc.
    VERY_HIGH = "very_high"  # Eastern Europe


@dataclass
class SCORE2Result:
    """Result of SCORE2 calculation."""
    risk_percent: float
    risk_level: CVRiskLevel
    components: Dict[str, Any]
    interpretation: str
    recommendations: List[str]


def calculate_score2(
    age: int,
    sex: str,
    smoking: bool,
    systolic_bp: int,
    non_hdl_cholesterol: float,
    region: RiskRegion = RiskRegion.MODERATE,
) -> SCORE2Result:
    """
    Calculate SCORE2 10-year CV risk (for ages 40-69).

    ESC 2021 CV Prevention Guidelines.
    Estimates 10-year risk of fatal and non-fatal CV events.

    Args:
        age: Age 40-69 years
        sex: "male" or "female"
        smoking: Current smoker
        systolic_bp: Systolic blood pressure (mmHg)
        non_hdl_cholesterol: Non-HDL cholesterol (mmol/L)
        region: European risk region

    Returns:
        SCORE2Result with 10-year risk estimate
    """
    # Simplified SCORE2 estimation (actual algorithm uses complex recalibrated models)
    # This provides approximate risk based on key factors

    components = {
        "age": age,
        "sex": sex,
        "smoking": smoking,
        "systolic_bp": systolic_bp,
        "non_hdl_cholesterol": non_hdl_cholesterol,
        "region": region.value,
    }

    # Base risk by age and sex (approximate)
    base_risk = 0.0
    if sex.lower() == "male":
        if age < 50:
            base_risk = 2.0
        elif age < 55:
            base_risk = 3.5
        elif age < 60:
            base_risk = 5.5
        elif age < 65:
            base_risk = 8.0
        else:
            base_risk = 12.0
    else:  # female
        if age < 50:
            base_risk = 1.0
        elif age < 55:
            base_risk = 1.5
        elif age < 60:
            base_risk = 2.5
        elif age < 65:
            base_risk = 4.0
        else:
            base_risk = 6.5

    # Adjust for risk factors
    risk = base_risk

    if smoking:
        risk *= 2.0

    # BP adjustment (above 120 mmHg adds risk)
    if systolic_bp > 120:
        bp_factor = 1 + (systolic_bp - 120) * 0.01
        risk *= bp_factor

    # Cholesterol adjustment (above 4 mmol/L adds risk)
    if non_hdl_cholesterol > 4.0:
        chol_factor = 1 + (non_hdl_cholesterol - 4.0) * 0.15
        risk *= chol_factor

    # Regional adjustment
    region_multipliers = {
        RiskRegion.LOW: 0.7,
        RiskRegion.MODERATE: 1.0,
        RiskRegion.HIGH: 1.3,
        RiskRegion.VERY_HIGH: 1.6,
    }
    risk *= region_multipliers.get(region, 1.0)

    # Cap at reasonable values
    risk = min(risk, 50.0)
    risk = round(risk, 1)

    # Determine risk level based on age
    if age < 50:
        if risk < 2.5:
            risk_level = CVRiskLevel.LOW_MODERATE
        elif risk < 7.5:
            risk_level = CVRiskLevel.HIGH
        else:
            risk_level = CVRiskLevel.VERY_HIGH
    else:
        if risk < 5:
            risk_level = CVRiskLevel.LOW_MODERATE
        elif risk < 10:
            risk_level = CVRiskLevel.HIGH
        else:
            risk_level = CVRiskLevel.VERY_HIGH

    # Interpretation and recommendations
    interpretation = f"SCORE2 10-year CV risk: {risk}% ({risk_level.value})"

    recommendations = []
    if risk_level == CVRiskLevel.LOW_MODERATE:
        recommendations.append("Lifestyle advice on maintaining low risk")
        recommendations.append("Reassess CV risk periodically")
    elif risk_level == CVRiskLevel.HIGH:
        recommendations.append("Intensive lifestyle intervention")
        recommendations.append("Consider lipid-lowering and BP treatment")
        recommendations.append("LDL target: <2.6 mmol/L (100 mg/dL)")
    else:
        recommendations.append("Intensive lifestyle and pharmacological intervention")
        recommendations.append("LDL target: <1.8 mmol/L (70 mg/dL)")
        recommendations.append("Consider high-intensity statin")
        recommendations.append("Treat BP to <130/80 mmHg")

    return SCORE2Result(
        risk_percent=risk,
        risk_level=risk_level,
        components=components,
        interpretation=interpretation,
        recommendations=recommendations,
    )


def calculate_score2_op(
    age: int,
    sex: str,
    smoking: bool,
    systolic_bp: int,
    non_hdl_cholesterol: float,
    diabetes: bool = False,
    region: RiskRegion = RiskRegion.MODERATE,
) -> SCORE2Result:
    """
    Calculate SCORE2-OP for older persons (ages 70-89).

    ESC 2021 CV Prevention Guidelines.
    Adapted for older population with different risk thresholds.

    Args:
        age: Age 70-89 years
        sex: "male" or "female"
        smoking: Current smoker
        systolic_bp: Systolic blood pressure (mmHg)
        non_hdl_cholesterol: Non-HDL cholesterol (mmol/L)
        diabetes: Diabetes mellitus
        region: European risk region

    Returns:
        SCORE2Result with 10-year risk estimate
    """
    components = {
        "age": age,
        "sex": sex,
        "smoking": smoking,
        "systolic_bp": systolic_bp,
        "non_hdl_cholesterol": non_hdl_cholesterol,
        "diabetes": diabetes,
        "region": region.value,
    }

    # Higher baseline risk in elderly
    if sex.lower() == "male":
        if age < 75:
            base_risk = 15.0
        elif age < 80:
            base_risk = 20.0
        else:
            base_risk = 25.0
    else:
        if age < 75:
            base_risk = 10.0
        elif age < 80:
            base_risk = 14.0
        else:
            base_risk = 18.0

    risk = base_risk

    if smoking:
        risk *= 1.5  # Lower multiplier in elderly

    if diabetes:
        risk *= 1.5

    if systolic_bp > 140:
        risk *= 1 + (systolic_bp - 140) * 0.008

    if non_hdl_cholesterol > 4.5:
        risk *= 1 + (non_hdl_cholesterol - 4.5) * 0.1

    region_multipliers = {
        RiskRegion.LOW: 0.8,
        RiskRegion.MODERATE: 1.0,
        RiskRegion.HIGH: 1.2,
        RiskRegion.VERY_HIGH: 1.4,
    }
    risk *= region_multipliers.get(region, 1.0)

    risk = min(risk, 60.0)
    risk = round(risk, 1)

    # Risk thresholds different for elderly
    if risk < 7.5:
        risk_level = CVRiskLevel.LOW_MODERATE
    elif risk < 15:
        risk_level = CVRiskLevel.HIGH
    else:
        risk_level = CVRiskLevel.VERY_HIGH

    interpretation = f"SCORE2-OP 10-year CV risk: {risk}% ({risk_level.value})"

    recommendations = []
    if risk_level == CVRiskLevel.LOW_MODERATE:
        recommendations.append("Lifestyle advice")
        recommendations.append("Consider treatment based on individual factors")
    elif risk_level == CVRiskLevel.HIGH:
        recommendations.append("Consider lipid-lowering therapy")
        recommendations.append("BP treatment if tolerated")
        recommendations.append("Avoid over-treatment in frail patients")
    else:
        recommendations.append("Lipid-lowering and BP treatment recommended")
        recommendations.append("Individualize targets based on frailty")
        recommendations.append("Balance benefits against polypharmacy risks")

    return SCORE2Result(
        risk_percent=risk,
        risk_level=risk_level,
        components=components,
        interpretation=interpretation,
        recommendations=recommendations,
    )


def get_risk_category(
    age: int,
    diabetes: bool = False,
    diabetes_duration_years: Optional[int] = None,
    diabetes_with_target_organ_damage: bool = False,
    ckd_egfr: Optional[float] = None,
    familial_hypercholesterolemia: bool = False,
    established_cvd: bool = False,
    score2_risk: Optional[float] = None,
) -> CVRiskLevel:
    """
    Determine CV risk category based on clinical factors.

    ESC 2021 CV Prevention Guidelines - Risk categories.

    Args:
        age: Patient age
        diabetes: Has diabetes
        diabetes_duration_years: Duration of diabetes
        diabetes_with_target_organ_damage: DM with TOD
        ckd_egfr: eGFR if CKD present
        familial_hypercholesterolemia: Familial hypercholesterolemia
        established_cvd: Established cardiovascular disease
        score2_risk: SCORE2 calculated risk if available

    Returns:
        CVRiskLevel classification
    """
    # Automatic VERY HIGH risk conditions
    if established_cvd:
        return CVRiskLevel.VERY_HIGH

    if familial_hypercholesterolemia and (diabetes or established_cvd):
        return CVRiskLevel.VERY_HIGH

    if diabetes_with_target_organ_damage:
        return CVRiskLevel.VERY_HIGH

    if diabetes and diabetes_duration_years and diabetes_duration_years >= 20:
        return CVRiskLevel.VERY_HIGH

    if ckd_egfr is not None and ckd_egfr < 30:
        return CVRiskLevel.VERY_HIGH

    # HIGH risk conditions
    if ckd_egfr is not None and 30 <= ckd_egfr < 45:
        return CVRiskLevel.HIGH

    if diabetes and diabetes_duration_years and diabetes_duration_years >= 10:
        return CVRiskLevel.HIGH

    if familial_hypercholesterolemia:
        return CVRiskLevel.HIGH

    # Use SCORE2 if available
    if score2_risk is not None:
        if age < 50:
            if score2_risk >= 7.5:
                return CVRiskLevel.VERY_HIGH
            elif score2_risk >= 2.5:
                return CVRiskLevel.HIGH
        elif age < 70:
            if score2_risk >= 10:
                return CVRiskLevel.VERY_HIGH
            elif score2_risk >= 5:
                return CVRiskLevel.HIGH
        else:
            if score2_risk >= 15:
                return CVRiskLevel.VERY_HIGH
            elif score2_risk >= 7.5:
                return CVRiskLevel.HIGH

    return CVRiskLevel.LOW_MODERATE
