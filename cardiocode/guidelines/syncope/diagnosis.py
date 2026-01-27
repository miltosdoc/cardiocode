"""
Syncope Diagnosis and Classification (ESC 2018).

Diagnostic evaluation and risk stratification for syncope.
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional, List, Dict


class SyncopeType(Enum):
    """Classification of syncope etiology."""
    REFLEX_VASOVAGAL = "reflex_vasovagal"
    REFLEX_SITUATIONAL = "reflex_situational"
    REFLEX_CAROTID_SINUS = "reflex_carotid_sinus"
    ORTHOSTATIC_HYPOTENSION = "orthostatic_hypotension"
    CARDIAC_ARRHYTHMIC = "cardiac_arrhythmic"
    CARDIAC_STRUCTURAL = "cardiac_structural"
    UNEXPLAINED = "unexplained"


class SyncopeRisk(Enum):
    """Risk stratification for syncope."""
    LOW = "low"           # Can be discharged for outpatient evaluation
    INTERMEDIATE = "intermediate"  # May need short observation
    HIGH = "high"         # Requires admission and urgent evaluation


@dataclass
class SyncopeClassification:
    """Result of syncope classification."""
    syncope_type: SyncopeType
    confidence: str  # "definite", "probable", "possible"
    supporting_features: List[str]
    against_features: List[str]
    further_testing: List[str]


@dataclass
class SyncopeRiskResult:
    """Result of syncope risk stratification."""
    risk_level: SyncopeRisk
    high_risk_features: List[str]
    low_risk_features: List[str]
    disposition: str
    recommendations: List[str]


def classify_syncope(
    # History
    prodrome_present: bool = False,
    prodrome_type: Optional[str] = None,  # "autonomic" (nausea, warmth), "none", "brief"
    trigger_present: bool = False,
    trigger_type: Optional[str] = None,  # "standing", "pain", "emotion", "micturition", "cough", "none"
    position_at_onset: Optional[str] = None,  # "standing", "sitting", "supine"
    witnesses_jerking: bool = False,
    duration_seconds: Optional[int] = None,
    recovery_rapid: bool = True,
    confusion_after: bool = False,
    tongue_bite: bool = False,
    incontinence: bool = False,
    # Cardiac history
    known_heart_disease: bool = False,
    family_history_scd: bool = False,
    palpitations_before: bool = False,
    exertional: bool = False,
    supine_onset: bool = False,
    # ECG
    ecg_abnormal: bool = False,
    ecg_finding: Optional[str] = None,
) -> SyncopeClassification:
    """
    Classify syncope based on clinical features.

    ESC 2018 Syncope Guidelines.

    Args:
        prodrome_present: Prodromal symptoms before syncope
        prodrome_type: Type of prodrome
        trigger_present: Identifiable trigger
        trigger_type: Type of trigger
        position_at_onset: Position when syncope occurred
        witnesses_jerking: Witnessed myoclonic jerks
        duration_seconds: Duration of unconsciousness
        recovery_rapid: Rapid recovery without confusion
        confusion_after: Prolonged confusion after event
        tongue_bite: Tongue biting (lateral suggests seizure)
        incontinence: Urinary incontinence
        known_heart_disease: Known structural heart disease
        family_history_scd: Family history of sudden death
        palpitations_before: Palpitations immediately before
        exertional: Occurred during exertion
        supine_onset: Occurred while supine
        ecg_abnormal: Abnormal ECG
        ecg_finding: Specific ECG abnormality

    Returns:
        SyncopeClassification with likely etiology
    """
    supporting = []
    against = []
    further_testing = []

    # Check for high-risk cardiac features
    cardiac_features = 0
    if known_heart_disease:
        cardiac_features += 1
        supporting.append("Known heart disease")
    if family_history_scd:
        cardiac_features += 1
        supporting.append("Family history of SCD")
    if exertional:
        cardiac_features += 1
        supporting.append("Exertional syncope")
    if supine_onset:
        cardiac_features += 1
        supporting.append("Supine onset (excludes orthostatic)")
    if palpitations_before:
        cardiac_features += 1
        supporting.append("Palpitations before syncope")
    if ecg_abnormal:
        cardiac_features += 1
        supporting.append(f"Abnormal ECG: {ecg_finding}")

    # Check for reflex (vasovagal) features
    reflex_features = 0
    if prodrome_present and prodrome_type == "autonomic":
        reflex_features += 1
        supporting.append("Autonomic prodrome (nausea, warmth, sweating)")
    if trigger_present:
        reflex_features += 1
        supporting.append(f"Trigger: {trigger_type}")
    if position_at_onset == "standing":
        reflex_features += 1
    if recovery_rapid:
        reflex_features += 1
        supporting.append("Rapid recovery")

    # Check against reflex
    if not recovery_rapid or confusion_after:
        against.append("Prolonged recovery/confusion")
    if supine_onset:
        against.append("Supine onset (unusual for reflex)")

    # Determine most likely type
    if cardiac_features >= 2 or (ecg_abnormal and ecg_finding in [
        "bifascicular_block", "brugada", "long_qt", "preexcitation",
        "sustained_vt", "avb_high_grade", "sinus_pause"
    ]):
        syncope_type = SyncopeType.CARDIAC_ARRHYTHMIC
        confidence = "probable" if cardiac_features >= 2 else "possible"
        further_testing = [
            "Echocardiography",
            "Continuous ECG monitoring",
            "Consider electrophysiology study",
        ]
        if exertional:
            further_testing.append("Exercise testing")

    elif known_heart_disease and (exertional or ecg_abnormal):
        syncope_type = SyncopeType.CARDIAC_STRUCTURAL
        confidence = "probable"
        further_testing = [
            "Echocardiography",
            "Consider cardiac MRI",
            "Exercise testing if exertional",
        ]

    elif trigger_type == "standing" or position_at_onset == "standing":
        # Could be orthostatic or vasovagal
        if prodrome_type == "autonomic" and trigger_present:
            syncope_type = SyncopeType.REFLEX_VASOVAGAL
            confidence = "probable"
            further_testing = ["Orthostatic BP measurement", "Consider tilt testing"]
        else:
            syncope_type = SyncopeType.ORTHOSTATIC_HYPOTENSION
            confidence = "possible"
            further_testing = [
                "Active standing test",
                "Review medications",
                "Consider autonomic testing",
            ]

    elif trigger_type in ["micturition", "cough", "defecation", "swallowing"]:
        syncope_type = SyncopeType.REFLEX_SITUATIONAL
        confidence = "definite"
        further_testing = ["Usually clinical diagnosis; no further testing needed"]

    elif trigger_type in ["pain", "emotion", "crowded_place", "heat"]:
        syncope_type = SyncopeType.REFLEX_VASOVAGAL
        confidence = "definite" if prodrome_type == "autonomic" else "probable"
        further_testing = ["Clinical diagnosis if typical; tilt test if recurrent"]

    elif reflex_features >= 2:
        syncope_type = SyncopeType.REFLEX_VASOVAGAL
        confidence = "probable"
        further_testing = ["Tilt testing if diagnosis uncertain"]

    else:
        syncope_type = SyncopeType.UNEXPLAINED
        confidence = "uncertain"
        further_testing = [
            "Echocardiography",
            "Prolonged ECG monitoring (loop recorder)",
            "Tilt testing",
            "Consider EP study if cardiac risk factors",
        ]

    # Add features suggesting seizure (not syncope)
    seizure_features = []
    if tongue_bite:
        seizure_features.append("Tongue biting (especially lateral)")
    if confusion_after and duration_seconds and duration_seconds > 30:
        seizure_features.append("Prolonged post-ictal confusion")
    if witnesses_jerking and duration_seconds and duration_seconds > 15:
        seizure_features.append("Prolonged jerking (>15 sec)")

    if seizure_features:
        against.extend(seizure_features)
        further_testing.append("Consider EEG/neurology if seizure suspected")

    return SyncopeClassification(
        syncope_type=syncope_type,
        confidence=confidence,
        supporting_features=supporting,
        against_features=against,
        further_testing=further_testing,
    )


def assess_risk(
    # Immediate assessment
    age: int,
    known_heart_disease: bool = False,
    known_heart_failure: bool = False,
    abnormal_ecg: bool = False,
    specific_ecg_abnormality: Optional[str] = None,
    syncope_during_exertion: bool = False,
    syncope_supine: bool = False,
    palpitations_before: bool = False,
    family_history_scd: bool = False,
    # Vital signs
    systolic_bp: Optional[int] = None,
    heart_rate: Optional[int] = None,
    # Other
    trauma_from_syncope: bool = False,
    recurrent_syncope: bool = False,
) -> SyncopeRiskResult:
    """
    Risk stratify syncope for disposition decisions.

    ESC 2018 Syncope Guidelines.

    Args:
        age: Patient age
        known_heart_disease: Structural heart disease
        known_heart_failure: Heart failure
        abnormal_ecg: ECG abnormalities
        specific_ecg_abnormality: Specific finding
        syncope_during_exertion: Exertional syncope
        syncope_supine: Syncope while supine
        palpitations_before: Palpitations before event
        family_history_scd: Family SCD <40 years
        systolic_bp: Systolic BP
        heart_rate: Heart rate
        trauma_from_syncope: Significant injury
        recurrent_syncope: Multiple episodes

    Returns:
        SyncopeRiskResult with risk level and disposition
    """
    high_risk = []
    low_risk = []
    recommendations = []

    # HIGH RISK FEATURES (Red flags)
    # Major structural heart disease
    if known_heart_disease:
        high_risk.append("Known structural heart disease")
    if known_heart_failure:
        high_risk.append("Heart failure")

    # ECG features suggesting arrhythmic cause
    high_risk_ecg = [
        "bifascicular_block", "mobitz_2", "complete_heart_block",
        "sinus_pause_3s", "sustained_vt", "brugada", "long_qt",
        "short_qt", "arvc", "preexcitation", "pacemaker_malfunction"
    ]
    if specific_ecg_abnormality and specific_ecg_abnormality.lower() in high_risk_ecg:
        high_risk.append(f"High-risk ECG: {specific_ecg_abnormality}")
    elif abnormal_ecg:
        high_risk.append("Abnormal ECG (not specified)")

    # Clinical features
    if syncope_during_exertion:
        high_risk.append("Exertional syncope")
    if syncope_supine:
        high_risk.append("Syncope while supine")
    if palpitations_before:
        high_risk.append("Palpitations immediately before syncope")
    if family_history_scd:
        high_risk.append("Family history of premature SCD")

    # Vital sign abnormalities
    if systolic_bp is not None and systolic_bp < 90:
        high_risk.append("Hypotension (SBP <90)")
    if heart_rate is not None:
        if heart_rate < 40:
            high_risk.append("Bradycardia <40 bpm")
        elif heart_rate > 150:
            high_risk.append("Tachycardia >150 bpm")

    # LOW RISK FEATURES
    if age < 40 and not known_heart_disease:
        low_risk.append("Young age without heart disease")

    typical_vasovagal = False
    # These would need to be passed in for complete assessment
    # Simplified: if no high risk features and young, likely low risk

    # DETERMINE RISK LEVEL
    if len(high_risk) >= 2:
        risk_level = SyncopeRisk.HIGH
        disposition = "Admit for monitoring and urgent evaluation"
        recommendations = [
            "Continuous telemetry monitoring",
            "Echocardiography",
            "Cardiology consultation",
            "Consider EP study",
        ]
    elif len(high_risk) == 1:
        risk_level = SyncopeRisk.INTERMEDIATE
        disposition = "ED observation or short admission for evaluation"
        recommendations = [
            "ECG monitoring (6-24 hours)",
            "Echocardiography if not recent",
            "Close follow-up if discharged",
        ]
    else:
        risk_level = SyncopeRisk.LOW
        disposition = "May be discharged with outpatient follow-up"
        recommendations = [
            "Outpatient evaluation if recurrent",
            "Return precautions for warning symptoms",
        ]

    if trauma_from_syncope:
        recommendations.insert(0, "Evaluate and treat trauma")

    if recurrent_syncope and risk_level == SyncopeRisk.LOW:
        recommendations.append("Consider loop recorder for recurrent unexplained syncope")

    return SyncopeRiskResult(
        risk_level=risk_level,
        high_risk_features=high_risk,
        low_risk_features=low_risk,
        disposition=disposition,
        recommendations=recommendations,
    )
