"""
Peripheral Arterial Disease Diagnosis (ESC 2024).

Diagnosis and classification of PAD, AAA, and carotid disease.
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional, List, Dict


class PADFontaineStage(Enum):
    """Fontaine classification of PAD."""
    I = "stage_I"        # Asymptomatic
    IIA = "stage_IIa"    # Intermittent claudication >200m
    IIB = "stage_IIb"    # Intermittent claudication <200m
    III = "stage_III"    # Rest pain
    IV = "stage_IV"      # Ulceration or gangrene


class PADRutherfordCategory(Enum):
    """Rutherford classification of PAD."""
    ZERO = "0"      # Asymptomatic
    ONE = "1"       # Mild claudication
    TWO = "2"       # Moderate claudication
    THREE = "3"     # Severe claudication
    FOUR = "4"      # Ischemic rest pain
    FIVE = "5"      # Minor tissue loss
    SIX = "6"       # Major tissue loss


class AAASize(Enum):
    """AAA size classification."""
    SMALL = "small"              # 3.0-4.4 cm
    MEDIUM = "medium"            # 4.5-5.4 cm
    LARGE = "large"              # >=5.5 cm (men) or >=5.0 cm (women)
    VERY_LARGE = "very_large"    # >=6.5 cm


@dataclass
class ABIResult:
    """Ankle-brachial index result."""
    abi_right: Optional[float]
    abi_left: Optional[float]
    interpretation: str
    pad_present: bool
    severity: Optional[str]
    recommendations: List[str]


@dataclass
class PADDiagnosis:
    """PAD diagnosis result."""
    fontaine_stage: PADFontaineStage
    rutherford_category: PADRutherfordCategory
    abi: Optional[float]
    cli_present: bool  # Critical limb ischemia
    interpretation: str
    urgency: str


@dataclass
class AAADiagnosis:
    """AAA diagnosis and surveillance."""
    diameter_cm: float
    size_category: AAASize
    growth_rate_cm_year: Optional[float]
    intervention_threshold: bool
    surveillance_interval: str
    recommendations: List[str]


def calculate_abi(
    ankle_systolic_right: Optional[int] = None,
    ankle_systolic_left: Optional[int] = None,
    brachial_systolic: int = 120,
) -> ABIResult:
    """
    Calculate ankle-brachial index (ABI).

    ESC 2024 PAD Guidelines.

    Args:
        ankle_systolic_right: Right ankle systolic pressure (mmHg)
        ankle_systolic_left: Left ankle systolic pressure (mmHg)
        brachial_systolic: Higher arm systolic pressure (mmHg)

    Returns:
        ABIResult with interpretation
    """
    abi_right = None
    abi_left = None
    pad_present = False
    severity = None
    recommendations = []

    if brachial_systolic <= 0:
        return ABIResult(
            abi_right=None,
            abi_left=None,
            interpretation="Invalid brachial pressure",
            pad_present=False,
            severity=None,
            recommendations=["Repeat measurement with valid brachial pressure"],
        )

    if ankle_systolic_right:
        abi_right = round(ankle_systolic_right / brachial_systolic, 2)

    if ankle_systolic_left:
        abi_left = round(ankle_systolic_left / brachial_systolic, 2)

    # Use lower ABI for interpretation
    abi_values = [v for v in [abi_right, abi_left] if v is not None]
    if not abi_values:
        return ABIResult(
            abi_right=None,
            abi_left=None,
            interpretation="No valid ABI calculated",
            pad_present=False,
            severity=None,
            recommendations=["Measure ankle systolic pressures"],
        )

    min_abi = min(abi_values)

    if min_abi > 1.40:
        interpretation = f"ABI {min_abi}: Non-compressible arteries (medial calcification)"
        severity = "non_compressible"
        recommendations = [
            "ABI unreliable due to calcification",
            "Use toe-brachial index (TBI) or other modalities",
            "Consider TBI <0.70 as abnormal",
        ]
    elif min_abi >= 1.00:
        interpretation = f"ABI {min_abi}: Normal"
        severity = "normal"
        recommendations = [
            "No PAD by ABI criteria",
            "If symptoms present, consider exercise ABI or other testing",
        ]
    elif min_abi >= 0.91:
        interpretation = f"ABI {min_abi}: Borderline"
        severity = "borderline"
        recommendations = [
            "Borderline ABI - consider exercise ABI",
            "Assess CV risk factors",
        ]
    elif min_abi >= 0.70:
        interpretation = f"ABI {min_abi}: Mild-moderate PAD"
        severity = "mild_moderate"
        pad_present = True
        recommendations = [
            "PAD confirmed",
            "Cardiovascular risk modification essential",
            "Supervised exercise therapy",
            "Antiplatelet therapy",
            "Statin therapy",
        ]
    elif min_abi >= 0.50:
        interpretation = f"ABI {min_abi}: Moderate-severe PAD"
        severity = "moderate_severe"
        pad_present = True
        recommendations = [
            "Significant PAD",
            "Vascular specialist referral",
            "Aggressive risk factor modification",
            "Consider revascularization if symptomatic",
        ]
    elif min_abi >= 0.40:
        interpretation = f"ABI {min_abi}: Severe PAD"
        severity = "severe"
        pad_present = True
        recommendations = [
            "Severe PAD - high risk of CLI",
            "Urgent vascular assessment",
            "Revascularization often required",
        ]
    else:
        interpretation = f"ABI {min_abi}: Critical limb ischemia likely"
        severity = "critical"
        pad_present = True
        recommendations = [
            "Critical limb ischemia",
            "Emergency vascular referral",
            "Limb salvage intervention needed",
        ]

    return ABIResult(
        abi_right=abi_right,
        abi_left=abi_left,
        interpretation=interpretation,
        pad_present=pad_present,
        severity=severity,
        recommendations=recommendations,
    )


def diagnose_pad(
    claudication_distance_meters: Optional[int] = None,
    rest_pain: bool = False,
    tissue_loss: bool = False,
    gangrene: bool = False,
    abi: Optional[float] = None,
) -> PADDiagnosis:
    """
    Diagnose and classify PAD severity.

    ESC 2024 PAD Guidelines.

    Args:
        claudication_distance_meters: Walking distance before claudication
        rest_pain: Ischemic rest pain
        tissue_loss: Ulceration or minor tissue loss
        gangrene: Gangrene present
        abi: Ankle-brachial index if measured

    Returns:
        PADDiagnosis with classification
    """
    cli_present = False

    # Determine Fontaine and Rutherford stages
    if gangrene:
        fontaine = PADFontaineStage.IV
        rutherford = PADRutherfordCategory.SIX
        cli_present = True
        interpretation = "Stage IV PAD with gangrene - Critical limb ischemia"
        urgency = "Emergency"
    elif tissue_loss:
        fontaine = PADFontaineStage.IV
        rutherford = PADRutherfordCategory.FIVE
        cli_present = True
        interpretation = "Stage IV PAD with tissue loss - Critical limb ischemia"
        urgency = "Urgent"
    elif rest_pain:
        fontaine = PADFontaineStage.III
        rutherford = PADRutherfordCategory.FOUR
        cli_present = True
        interpretation = "Stage III PAD with rest pain - Critical limb ischemia"
        urgency = "Urgent"
    elif claudication_distance_meters is not None:
        if claudication_distance_meters < 50:
            fontaine = PADFontaineStage.IIB
            rutherford = PADRutherfordCategory.THREE
            interpretation = f"Stage IIb PAD - Severe claudication ({claudication_distance_meters}m)"
            urgency = "Soon"
        elif claudication_distance_meters < 200:
            fontaine = PADFontaineStage.IIB
            rutherford = PADRutherfordCategory.TWO
            interpretation = f"Stage IIb PAD - Moderate claudication ({claudication_distance_meters}m)"
            urgency = "Routine"
        else:
            fontaine = PADFontaineStage.IIA
            rutherford = PADRutherfordCategory.ONE
            interpretation = f"Stage IIa PAD - Mild claudication ({claudication_distance_meters}m)"
            urgency = "Routine"
    else:
        fontaine = PADFontaineStage.I
        rutherford = PADRutherfordCategory.ZERO
        interpretation = "Stage I PAD - Asymptomatic"
        urgency = "Routine"

    return PADDiagnosis(
        fontaine_stage=fontaine,
        rutherford_category=rutherford,
        abi=abi,
        cli_present=cli_present,
        interpretation=interpretation,
        urgency=urgency,
    )


def classify_aaa(
    diameter_cm: float,
    male: bool = True,
    growth_rate_cm_year: Optional[float] = None,
    symptomatic: bool = False,
) -> AAADiagnosis:
    """
    Classify AAA and determine surveillance/intervention.

    ESC 2024 Aortic Guidelines.

    Args:
        diameter_cm: Maximum aortic diameter (cm)
        male: Male patient
        growth_rate_cm_year: Growth rate if known
        symptomatic: Symptomatic AAA

    Returns:
        AAADiagnosis with management recommendations
    """
    recommendations = []
    intervention_threshold = False

    # Symptomatic always needs urgent evaluation
    if symptomatic:
        recommendations.append("Urgent vascular surgery evaluation")
        recommendations.append("Consider emergency repair")
        intervention_threshold = True
        return AAADiagnosis(
            diameter_cm=diameter_cm,
            size_category=AAASize.LARGE,
            growth_rate_cm_year=growth_rate_cm_year,
            intervention_threshold=True,
            surveillance_interval="Immediate evaluation",
            recommendations=recommendations,
        )

    # Size-based classification (thresholds differ by sex)
    repair_threshold = 5.5 if male else 5.0

    if diameter_cm < 3.0:
        # Not an aneurysm
        return AAADiagnosis(
            diameter_cm=diameter_cm,
            size_category=AAASize.SMALL,
            growth_rate_cm_year=growth_rate_cm_year,
            intervention_threshold=False,
            surveillance_interval="Not an AAA (diameter <3.0 cm)",
            recommendations=["Normal aortic diameter"],
        )

    elif diameter_cm < 4.0:
        size_category = AAASize.SMALL
        surveillance_interval = "Every 3 years"
        recommendations = [
            "Small AAA - surveillance",
            "CV risk factor modification",
            "Smoking cessation critical",
            "Repeat imaging in 3 years",
        ]

    elif diameter_cm < 4.5:
        size_category = AAASize.SMALL
        surveillance_interval = "Every 2 years"
        recommendations = [
            "Small AAA - surveillance",
            "CV risk factor modification",
            "Repeat imaging in 2 years",
        ]

    elif diameter_cm < repair_threshold:
        size_category = AAASize.MEDIUM
        surveillance_interval = "Every 6-12 months"
        recommendations = [
            "Medium AAA approaching intervention threshold",
            "Close surveillance",
            "Vascular surgery consultation",
            "Optimize fitness for potential repair",
        ]

    elif diameter_cm < 6.5:
        size_category = AAASize.LARGE
        intervention_threshold = True
        surveillance_interval = "Intervention indicated"
        recommendations = [
            f"AAA >{repair_threshold} cm - repair recommended",
            "Vascular surgery referral for repair planning",
            "EVAR or open repair based on anatomy and fitness",
        ]

    else:
        size_category = AAASize.VERY_LARGE
        intervention_threshold = True
        surveillance_interval = "Urgent intervention"
        recommendations = [
            "Very large AAA - high rupture risk",
            "Urgent repair recommended",
            "Annual rupture risk >20%",
        ]

    # Rapid growth increases urgency
    if growth_rate_cm_year and growth_rate_cm_year >= 1.0:
        recommendations.insert(0, f"Rapid growth ({growth_rate_cm_year} cm/year) - consider earlier repair")
        if not intervention_threshold:
            surveillance_interval = "Every 3-6 months (rapid growth)"

    return AAADiagnosis(
        diameter_cm=diameter_cm,
        size_category=size_category,
        growth_rate_cm_year=growth_rate_cm_year,
        intervention_threshold=intervention_threshold,
        surveillance_interval=surveillance_interval,
        recommendations=recommendations,
    )
