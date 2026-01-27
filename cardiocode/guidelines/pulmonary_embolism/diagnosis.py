"""
Pulmonary Embolism Diagnosis (ESC 2019).

Clinical probability scores and risk stratification for PE.
"""

from __future__ import annotations
from dataclasses import dataclass, field
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


class PEProbability(Enum):
    """PE clinical probability categories."""
    LOW = "low"
    INTERMEDIATE = "intermediate"
    HIGH = "high"


class PESIRiskClass(Enum):
    """PESI risk stratification classes."""
    CLASS_I = "I"      # Very low risk (0-65 points)
    CLASS_II = "II"    # Low risk (66-85 points)
    CLASS_III = "III"  # Intermediate risk (86-105 points)
    CLASS_IV = "IV"    # High risk (106-125 points)
    CLASS_V = "V"      # Very high risk (>125 points)


@dataclass
class WellsPEResult:
    """Result of Wells PE score calculation."""
    score: float
    probability: PEProbability
    components: Dict[str, float]
    interpretation: str
    recommendation: str


@dataclass
class GenevaResult:
    """Result of revised Geneva score calculation."""
    score: int
    probability: PEProbability
    components: Dict[str, int]
    interpretation: str
    recommendation: str


@dataclass
class PESIResult:
    """Result of PESI score calculation."""
    score: int
    risk_class: PESIRiskClass
    mortality_risk: str
    components: Dict[str, int]
    interpretation: str
    can_treat_outpatient: bool


@dataclass
class SimplifiedPESIResult:
    """Result of simplified PESI score calculation."""
    score: int
    high_risk: bool
    mortality_30_day: str
    components: Dict[str, int]
    interpretation: str
    can_treat_outpatient: bool


def calculate_wells_pe_score(
    clinical_signs_dvt: bool = False,
    pe_most_likely_diagnosis: bool = False,
    heart_rate_above_100: bool = False,
    immobilization_or_surgery: bool = False,
    previous_pe_dvt: bool = False,
    hemoptysis: bool = False,
    malignancy: bool = False,
) -> WellsPEResult:
    """
    Calculate Wells score for PE probability.

    ESC 2019 PE Guidelines - Table 4.

    Args:
        clinical_signs_dvt: Clinical signs/symptoms of DVT (leg swelling, pain)
        pe_most_likely_diagnosis: PE is #1 diagnosis or equally likely
        heart_rate_above_100: Heart rate > 100 bpm
        immobilization_or_surgery: Immobilization >= 3 days or surgery in past 4 weeks
        previous_pe_dvt: Previous PE or DVT
        hemoptysis: Hemoptysis
        malignancy: Active malignancy (treatment within 6 months or palliative)

    Returns:
        WellsPEResult with score, probability, and recommendations
    """
    components = {}
    score = 0.0

    if clinical_signs_dvt:
        components["Clinical signs/symptoms of DVT"] = 3.0
        score += 3.0

    if pe_most_likely_diagnosis:
        components["PE most likely diagnosis"] = 3.0
        score += 3.0

    if heart_rate_above_100:
        components["Heart rate > 100 bpm"] = 1.5
        score += 1.5

    if immobilization_or_surgery:
        components["Immobilization/surgery"] = 1.5
        score += 1.5

    if previous_pe_dvt:
        components["Previous PE or DVT"] = 1.5
        score += 1.5

    if hemoptysis:
        components["Hemoptysis"] = 1.0
        score += 1.0

    if malignancy:
        components["Active malignancy"] = 1.0
        score += 1.0

    # Three-level interpretation (original Wells)
    if score <= 1:
        probability = PEProbability.LOW
        interpretation = f"Wells score = {score}: LOW probability (~3% PE prevalence)"
        recommendation = "D-dimer testing recommended. If negative, PE can be ruled out."
    elif score <= 4:
        probability = PEProbability.INTERMEDIATE
        interpretation = f"Wells score = {score}: INTERMEDIATE probability (~28% PE prevalence)"
        recommendation = "D-dimer testing recommended. If positive or high clinical suspicion, proceed to CTPA."
    else:
        probability = PEProbability.HIGH
        interpretation = f"Wells score = {score}: HIGH probability (~78% PE prevalence)"
        recommendation = "CTPA recommended. D-dimer not useful for ruling out PE."

    return WellsPEResult(
        score=score,
        probability=probability,
        components=components,
        interpretation=interpretation,
        recommendation=recommendation,
    )


def calculate_revised_geneva_score(
    age_over_65: bool = False,
    previous_pe_dvt: bool = False,
    surgery_or_fracture: bool = False,
    active_malignancy: bool = False,
    unilateral_leg_pain: bool = False,
    hemoptysis: bool = False,
    heart_rate_75_94: bool = False,
    heart_rate_95_plus: bool = False,
    leg_pain_on_palpation_and_edema: bool = False,
) -> GenevaResult:
    """
    Calculate revised Geneva score for PE probability.

    ESC 2019 PE Guidelines - Table 4.

    Args:
        age_over_65: Age > 65 years
        previous_pe_dvt: Previous PE or DVT
        surgery_or_fracture: Surgery or fracture within 1 month
        active_malignancy: Active malignancy (or cured < 1 year)
        unilateral_leg_pain: Unilateral lower limb pain
        hemoptysis: Hemoptysis
        heart_rate_75_94: Heart rate 75-94 bpm
        heart_rate_95_plus: Heart rate >= 95 bpm
        leg_pain_on_palpation_and_edema: Pain on leg palpation and unilateral edema

    Returns:
        GenevaResult with score, probability, and recommendations
    """
    components = {}
    score = 0

    if age_over_65:
        components["Age > 65"] = 1
        score += 1

    if previous_pe_dvt:
        components["Previous PE or DVT"] = 3
        score += 3

    if surgery_or_fracture:
        components["Surgery/fracture within 1 month"] = 2
        score += 2

    if active_malignancy:
        components["Active malignancy"] = 2
        score += 2

    if unilateral_leg_pain:
        components["Unilateral lower limb pain"] = 3
        score += 3

    if hemoptysis:
        components["Hemoptysis"] = 2
        score += 2

    if heart_rate_75_94:
        components["Heart rate 75-94 bpm"] = 3
        score += 3
    elif heart_rate_95_plus:
        components["Heart rate >= 95 bpm"] = 5
        score += 5

    if leg_pain_on_palpation_and_edema:
        components["Leg pain + unilateral edema"] = 4
        score += 4

    # Three-level interpretation
    if score <= 3:
        probability = PEProbability.LOW
        interpretation = f"Revised Geneva = {score}: LOW probability (~8% PE prevalence)"
        recommendation = "D-dimer testing recommended. If negative, PE can be ruled out."
    elif score <= 10:
        probability = PEProbability.INTERMEDIATE
        interpretation = f"Revised Geneva = {score}: INTERMEDIATE probability (~29% PE prevalence)"
        recommendation = "D-dimer testing recommended. If positive, proceed to CTPA."
    else:
        probability = PEProbability.HIGH
        interpretation = f"Revised Geneva = {score}: HIGH probability (~74% PE prevalence)"
        recommendation = "CTPA recommended. D-dimer not useful for ruling out PE."

    return GenevaResult(
        score=score,
        probability=probability,
        components=components,
        interpretation=interpretation,
        recommendation=recommendation,
    )


def calculate_pesi_score(
    age: int,
    male: bool = True,
    cancer: bool = False,
    heart_failure: bool = False,
    chronic_lung_disease: bool = False,
    heart_rate_110_plus: bool = False,
    systolic_bp_below_100: bool = False,
    respiratory_rate_30_plus: bool = False,
    temperature_below_36: bool = False,
    altered_mental_status: bool = False,
    spo2_below_90: bool = False,
) -> PESIResult:
    """
    Calculate Pulmonary Embolism Severity Index (PESI).

    ESC 2019 PE Guidelines - Table 5.
    Predicts 30-day mortality in acute PE.

    Args:
        age: Patient age (points = age in years)
        male: Male sex (+10 points)
        cancer: Active cancer (+30 points)
        heart_failure: Chronic heart failure (+10 points)
        chronic_lung_disease: Chronic lung disease (+10 points)
        heart_rate_110_plus: Heart rate >= 110 bpm (+20 points)
        systolic_bp_below_100: SBP < 100 mmHg (+30 points)
        respiratory_rate_30_plus: RR >= 30/min (+20 points)
        temperature_below_36: Temperature < 36°C (+20 points)
        altered_mental_status: Altered mental status (+60 points)
        spo2_below_90: O2 saturation < 90% (+20 points)

    Returns:
        PESIResult with risk class and 30-day mortality
    """
    components = {"Age": age}
    score = age

    if male:
        components["Male sex"] = 10
        score += 10

    if cancer:
        components["Cancer"] = 30
        score += 30

    if heart_failure:
        components["Heart failure"] = 10
        score += 10

    if chronic_lung_disease:
        components["Chronic lung disease"] = 10
        score += 10

    if heart_rate_110_plus:
        components["Heart rate >= 110"] = 20
        score += 20

    if systolic_bp_below_100:
        components["SBP < 100"] = 30
        score += 30

    if respiratory_rate_30_plus:
        components["RR >= 30"] = 20
        score += 20

    if temperature_below_36:
        components["Temp < 36°C"] = 20
        score += 20

    if altered_mental_status:
        components["Altered mental status"] = 60
        score += 60

    if spo2_below_90:
        components["SpO2 < 90%"] = 20
        score += 20

    # Risk class determination
    if score <= 65:
        risk_class = PESIRiskClass.CLASS_I
        mortality_risk = "0-1.6%"
        can_treat_outpatient = True
        interpretation = "PESI Class I (very low risk): 30-day mortality 0-1.6%. Consider outpatient treatment."
    elif score <= 85:
        risk_class = PESIRiskClass.CLASS_II
        mortality_risk = "1.7-3.5%"
        can_treat_outpatient = True
        interpretation = "PESI Class II (low risk): 30-day mortality 1.7-3.5%. Consider outpatient treatment."
    elif score <= 105:
        risk_class = PESIRiskClass.CLASS_III
        mortality_risk = "3.2-7.1%"
        can_treat_outpatient = False
        interpretation = "PESI Class III (intermediate risk): 30-day mortality 3.2-7.1%. Hospital admission recommended."
    elif score <= 125:
        risk_class = PESIRiskClass.CLASS_IV
        mortality_risk = "4.0-11.4%"
        can_treat_outpatient = False
        interpretation = "PESI Class IV (high risk): 30-day mortality 4.0-11.4%. Hospital admission required."
    else:
        risk_class = PESIRiskClass.CLASS_V
        mortality_risk = "10.0-24.5%"
        can_treat_outpatient = False
        interpretation = "PESI Class V (very high risk): 30-day mortality 10.0-24.5%. ICU admission may be needed."

    return PESIResult(
        score=score,
        risk_class=risk_class,
        mortality_risk=mortality_risk,
        components=components,
        interpretation=interpretation,
        can_treat_outpatient=can_treat_outpatient,
    )


def calculate_simplified_pesi(
    age_over_80: bool = False,
    cancer: bool = False,
    chronic_cardiopulmonary_disease: bool = False,
    heart_rate_110_plus: bool = False,
    systolic_bp_below_100: bool = False,
    spo2_below_90: bool = False,
) -> SimplifiedPESIResult:
    """
    Calculate Simplified PESI (sPESI).

    ESC 2019 PE Guidelines - Table 5.
    Simplified version with 6 equally weighted criteria.

    Args:
        age_over_80: Age > 80 years (1 point)
        cancer: Active cancer (1 point)
        chronic_cardiopulmonary_disease: Chronic heart or lung disease (1 point)
        heart_rate_110_plus: Heart rate >= 110 bpm (1 point)
        systolic_bp_below_100: SBP < 100 mmHg (1 point)
        spo2_below_90: O2 saturation < 90% (1 point)

    Returns:
        SimplifiedPESIResult with risk assessment
    """
    components = {}
    score = 0

    if age_over_80:
        components["Age > 80"] = 1
        score += 1

    if cancer:
        components["Cancer"] = 1
        score += 1

    if chronic_cardiopulmonary_disease:
        components["Chronic cardiopulmonary disease"] = 1
        score += 1

    if heart_rate_110_plus:
        components["Heart rate >= 110"] = 1
        score += 1

    if systolic_bp_below_100:
        components["SBP < 100"] = 1
        score += 1

    if spo2_below_90:
        components["SpO2 < 90%"] = 1
        score += 1

    if score == 0:
        high_risk = False
        mortality_30_day = "1.0%"
        can_treat_outpatient = True
        interpretation = "sPESI = 0: LOW RISK. 30-day mortality ~1.0%. Outpatient treatment may be appropriate."
    else:
        high_risk = True
        mortality_30_day = "10.9%"
        can_treat_outpatient = False
        interpretation = f"sPESI = {score}: HIGH RISK. 30-day mortality ~10.9%. Hospital admission recommended."

    return SimplifiedPESIResult(
        score=score,
        high_risk=high_risk,
        mortality_30_day=mortality_30_day,
        components=components,
        interpretation=interpretation,
        can_treat_outpatient=can_treat_outpatient,
    )


def assess_pe_probability(
    wells_score: Optional[float] = None,
    geneva_score: Optional[int] = None,
    d_dimer_negative: Optional[bool] = None,
    hemodynamically_unstable: bool = False,
) -> RecommendationSet:
    """
    Assess PE probability and recommend diagnostic pathway.

    ESC 2019 PE Guidelines - Figure 4 (hemodynamically stable)
    and Figure 3 (hemodynamically unstable).

    Args:
        wells_score: Wells PE score if calculated
        geneva_score: Revised Geneva score if calculated
        d_dimer_negative: D-dimer result (True = negative, False = positive)
        hemodynamically_unstable: Shock or hypotension

    Returns:
        RecommendationSet with diagnostic recommendations
    """
    rec_set = RecommendationSet(
        title="PE Diagnostic Pathway",
        description="ESC 2019 PE Guidelines diagnostic algorithm",
        primary_guideline="ESC PE 2019",
    )

    if hemodynamically_unstable:
        rec_set.add(guideline_recommendation(
            action="Perform bedside echocardiography immediately",
            guideline_key="esc_pe_2019",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.DIAGNOSTIC,
            urgency=Urgency.EMERGENT,
            rationale="RV dysfunction on echo supports PE diagnosis in unstable patients",
        ))

        rec_set.add(guideline_recommendation(
            action="If echo shows RV overload and CTPA not immediately available, consider reperfusion therapy",
            guideline_key="esc_pe_2019",
            evidence_class=EvidenceClass.IIA,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.PROCEDURE,
            urgency=Urgency.EMERGENT,
            rationale="High-risk PE with hemodynamic instability warrants immediate treatment",
        ))

        return rec_set

    # Hemodynamically stable pathway
    probability = None
    if wells_score is not None:
        if wells_score <= 1:
            probability = PEProbability.LOW
        elif wells_score <= 4:
            probability = PEProbability.INTERMEDIATE
        else:
            probability = PEProbability.HIGH
    elif geneva_score is not None:
        if geneva_score <= 3:
            probability = PEProbability.LOW
        elif geneva_score <= 10:
            probability = PEProbability.INTERMEDIATE
        else:
            probability = PEProbability.HIGH

    if probability in [PEProbability.LOW, PEProbability.INTERMEDIATE]:
        if d_dimer_negative is None:
            rec_set.add(guideline_recommendation(
                action="Obtain D-dimer (high-sensitivity assay preferred)",
                guideline_key="esc_pe_2019",
                evidence_class=EvidenceClass.I,
                evidence_level=EvidenceLevel.A,
                category=RecommendationCategory.DIAGNOSTIC,
                urgency=Urgency.URGENT,
                rationale="Negative D-dimer can safely rule out PE in low/intermediate probability",
            ))
        elif d_dimer_negative:
            rec_set.add(guideline_recommendation(
                action="PE ruled out - no further imaging required",
                guideline_key="esc_pe_2019",
                evidence_class=EvidenceClass.I,
                evidence_level=EvidenceLevel.A,
                category=RecommendationCategory.DIAGNOSTIC,
                urgency=Urgency.ROUTINE,
                rationale="Negative D-dimer with low/intermediate probability safely excludes PE",
            ))
        else:
            rec_set.add(guideline_recommendation(
                action="Perform CTPA",
                guideline_key="esc_pe_2019",
                evidence_class=EvidenceClass.I,
                evidence_level=EvidenceLevel.A,
                category=RecommendationCategory.DIAGNOSTIC,
                urgency=Urgency.URGENT,
                rationale="Positive D-dimer requires imaging to confirm/exclude PE",
            ))

    elif probability == PEProbability.HIGH:
        rec_set.add(guideline_recommendation(
            action="Perform CTPA directly (D-dimer not recommended)",
            guideline_key="esc_pe_2019",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.A,
            category=RecommendationCategory.DIAGNOSTIC,
            urgency=Urgency.URGENT,
            rationale="High clinical probability - D-dimer cannot reliably rule out PE",
        ))

    return rec_set
