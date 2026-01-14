"""
Stroke Prevention in Atrial Fibrillation - ESC 2020 Guidelines.

Implements stroke risk assessment and anticoagulation recommendations:
- CHA2DS2-VASc scoring
- Anticoagulation decision algorithm
- DOAC vs VKA selection
- Bleeding risk assessment integration
"""

from __future__ import annotations
from typing import Optional, List, TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from cardiocode.core.types import Patient

from cardiocode.core.recommendation import (
    Recommendation,
    RecommendationSet,
    RecommendationCategory,
    Urgency,
    guideline_recommendation,
    synthesis_recommendation,
)
from cardiocode.core.evidence import EvidenceClass, EvidenceLevel
from cardiocode.knowledge.scores import cha2ds2_vasc, has_bled, ScoreResult


@dataclass
class StrokeRiskAssessment:
    """Complete stroke risk assessment for AF patient."""
    cha2ds2_vasc_score: int
    cha2ds2_vasc_result: ScoreResult
    has_bled_score: Optional[int] = None
    has_bled_result: Optional[ScoreResult] = None
    
    anticoagulation_indicated: bool = False
    anticoagulation_strength: str = ""  # "recommended", "should_consider", "not_recommended"
    
    recommendations: List[Recommendation] = None
    
    def __post_init__(self):
        if self.recommendations is None:
            self.recommendations = []


def assess_stroke_risk(patient: "Patient") -> StrokeRiskAssessment:
    """
    Comprehensive stroke risk assessment for AF patient.
    
    Per ESC 2020 Section 11.2: Stroke prevention
    
    Algorithm:
    1. Calculate CHA2DS2-VASc
    2. Calculate HAS-BLED (to identify modifiable bleeding risks, NOT to withhold OAC)
    3. Determine anticoagulation recommendation based on score and sex
    
    Args:
        patient: Patient object
    
    Returns:
        StrokeRiskAssessment with scores and recommendations
    """
    recommendations = []
    
    # Determine sex
    sex = "male"
    if patient.sex:
        sex = patient.sex.value if hasattr(patient.sex, 'value') else str(patient.sex)
    
    # Calculate CHA2DS2-VASc
    chads_result = cha2ds2_vasc(
        age=patient.age or 65,
        sex=sex,
        has_chf=patient.has_diagnosis("heart_failure") or (patient.lvef is not None and patient.lvef < 40),
        has_hypertension=patient.has_hypertension,
        has_stroke_tia_te=patient.has_prior_stroke_tia,
        has_vascular_disease=patient.has_vascular_disease or patient.has_cad,
        has_diabetes=patient.has_diabetes,
    )
    
    # Calculate HAS-BLED
    bled_result = has_bled(
        has_hypertension=patient.has_hypertension,
        abnormal_renal_function=patient.labs.egfr < 50 if patient.labs and patient.labs.egfr else False,
        abnormal_liver_function=patient.has_liver_disease,
        has_stroke=patient.has_prior_stroke_tia,
        bleeding_history=patient.has_prior_bleeding,
        age_over_65=patient.age > 65 if patient.age else False,
        drugs_predisposing=patient.is_on_medication("aspirin") or patient.is_on_medication("nsaid"),
    )
    
    # Determine anticoagulation recommendation
    # Per ESC 2020: Use CHA2DS2-VASc adjusted for sex
    is_female = sex.lower() == "female"
    adjusted_score = chads_result.score_value - 1 if is_female else chads_result.score_value
    
    if adjusted_score >= 2:
        # Strong recommendation for OAC
        anticoagulation_indicated = True
        strength = "recommended"
        recommendations.append(guideline_recommendation(
            action="Oral anticoagulation is RECOMMENDED to prevent stroke",
            guideline_key="esc_af_2020",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.A,
            category=RecommendationCategory.PHARMACOTHERAPY,
            section="11.2.1",
            studies=["RE-LY", "ROCKET AF", "ARISTOTLE", "ENGAGE AF-TIMI 48"],
            rationale=f"CHA2DS2-VASc {chads_result.score_value} indicates high stroke risk. Annual stroke risk ~{chads_result.risk_percentage:.1f}%",
        ))
    
    elif adjusted_score == 1:
        # Should be considered
        anticoagulation_indicated = True
        strength = "should_consider"
        recommendations.append(guideline_recommendation(
            action="Oral anticoagulation SHOULD BE CONSIDERED, weighing stroke risk against bleeding risk",
            guideline_key="esc_af_2020",
            evidence_class=EvidenceClass.IIA,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PHARMACOTHERAPY,
            section="11.2.1",
            rationale=f"CHA2DS2-VASc {chads_result.score_value} (intermediate risk). Shared decision-making with patient.",
        ))
    
    else:
        # Score 0 (men) or 1 (women with only sex as risk factor)
        anticoagulation_indicated = False
        strength = "not_recommended"
        recommendations.append(guideline_recommendation(
            action="Antithrombotic therapy NOT recommended (no stroke risk factors beyond sex)",
            guideline_key="esc_af_2020",
            evidence_class=EvidenceClass.IIA,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PHARMACOTHERAPY,
            section="11.2.1",
            rationale="Low stroke risk. Reassess if risk factors develop.",
        ))
    
    # Add HAS-BLED guidance
    if bled_result.score_value >= 3:
        recommendations.append(guideline_recommendation(
            action=f"High HAS-BLED ({bled_result.score_value}): Address modifiable bleeding risk factors. This does NOT contraindicate anticoagulation.",
            guideline_key="esc_af_2020",
            evidence_class=EvidenceClass.IIA,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.MONITORING,
            section="11.2.2",
            rationale="Modifiable factors: uncontrolled HTN, labile INR, concomitant drugs, alcohol",
        ))
    
    return StrokeRiskAssessment(
        cha2ds2_vasc_score=int(chads_result.score_value),
        cha2ds2_vasc_result=chads_result,
        has_bled_score=int(bled_result.score_value),
        has_bled_result=bled_result,
        anticoagulation_indicated=anticoagulation_indicated,
        anticoagulation_strength=strength,
        recommendations=recommendations,
    )


def get_anticoagulation_recommendation(patient: "Patient") -> RecommendationSet:
    """
    Get complete anticoagulation recommendations for AF patient.
    
    Per ESC 2020 Section 11.2
    """
    assessment = assess_stroke_risk(patient)
    
    rec_set = RecommendationSet(
        title="AF Anticoagulation Recommendations",
        description=f"CHA2DS2-VASc: {assessment.cha2ds2_vasc_score}, HAS-BLED: {assessment.has_bled_score}",
        primary_guideline="ESC AF 2020",
    )
    
    for rec in assessment.recommendations:
        rec_set.add(rec)
    
    # Add anticoagulant selection if indicated
    if assessment.anticoagulation_indicated:
        selection_recs = select_anticoagulant(patient)
        rec_set.add_all(selection_recs.recommendations)
    
    return rec_set


def select_anticoagulant(patient: "Patient") -> RecommendationSet:
    """
    Select appropriate anticoagulant for AF patient.
    
    Per ESC 2020 Section 11.2.3-11.2.4
    
    DOAC preferred over VKA (Class I, Level A) unless:
    - Mechanical heart valve
    - Moderate-severe mitral stenosis
    
    Args:
        patient: Patient object
    
    Returns:
        RecommendationSet with anticoagulant recommendations
    """
    rec_set = RecommendationSet(
        title="Anticoagulant Selection",
        primary_guideline="ESC AF 2020",
    )
    
    # Check for valvular AF (requires VKA)
    has_mechanical_valve = patient.has_diagnosis("mechanical_valve")
    has_ms = False
    if patient.echo and patient.echo.mitral_valve_area:
        has_ms = patient.echo.mitral_valve_area < 1.5  # Moderate-severe MS
    
    if has_mechanical_valve:
        rec_set.add(guideline_recommendation(
            action="WARFARIN is required for mechanical heart valve. DOACs are contraindicated.",
            guideline_key="esc_af_2020",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PHARMACOTHERAPY,
            section="11.2.4",
            studies=["RE-ALIGN (stopped early - harm with dabigatran)"],
            monitoring="Target INR based on valve type and position",
            contraindications=["All DOACs contraindicated with mechanical valve"],
        ))
        return rec_set
    
    if has_ms:
        rec_set.add(guideline_recommendation(
            action="WARFARIN recommended for moderate-severe mitral stenosis (rheumatic). DOACs not well studied.",
            guideline_key="esc_af_2020",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.PHARMACOTHERAPY,
            section="11.2.4",
        ))
        return rec_set
    
    # Non-valvular AF - DOACs preferred
    rec_set.add(guideline_recommendation(
        action="DOAC (apixaban, rivaroxaban, edoxaban, or dabigatran) RECOMMENDED over warfarin",
        guideline_key="esc_af_2020",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.A,
        category=RecommendationCategory.PHARMACOTHERAPY,
        section="11.2.3",
        studies=["RE-LY", "ROCKET AF", "ARISTOTLE", "ENGAGE AF-TIMI 48"],
        rationale="DOACs have favorable risk-benefit vs warfarin: similar/better efficacy, less ICH",
    ))
    
    # DOAC selection based on patient factors
    egfr = patient.labs.egfr if patient.labs else None
    
    if egfr and egfr < 30:
        rec_set.add(guideline_recommendation(
            action="Severe CKD (eGFR 15-29): Apixaban 2.5mg BID or rivaroxaban 15mg daily may be used with caution. Avoid dabigatran.",
            guideline_key="esc_af_2020",
            evidence_class=EvidenceClass.IIB,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.PHARMACOTHERAPY,
            section="11.2.3",
            monitoring="Close monitoring of renal function required",
        ))
    elif egfr and egfr < 50:
        rec_set.add(guideline_recommendation(
            action="Moderate CKD (eGFR 30-49): Consider dose reduction per DOAC labeling. Rivaroxaban 15mg, apixaban based on criteria, dabigatran 110mg BID.",
            guideline_key="esc_af_2020",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PHARMACOTHERAPY,
            section="11.2.3",
        ))
    
    # Age considerations
    if patient.age and patient.age >= 80:
        rec_set.add(guideline_recommendation(
            action="Age >= 80: Apixaban has best safety data. Consider reduced doses per labeling.",
            guideline_key="esc_af_2020",
            evidence_class=EvidenceClass.IIA,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PHARMACOTHERAPY,
            section="11.2.3",
            studies=["ARISTOTLE (elderly subgroup)", "ELDERCARE-AF"],
        ))
    
    # Specific DOAC dosing guidance
    rec_set.add(guideline_recommendation(
        action="Standard doses: Apixaban 5mg BID, Rivaroxaban 20mg daily, Dabigatran 150mg BID, Edoxaban 60mg daily",
        guideline_key="esc_af_2020",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.A,
        category=RecommendationCategory.PHARMACOTHERAPY,
        section="11.2.3",
        rationale="Use standard doses unless specific dose reduction criteria met. Under-dosing increases stroke risk.",
    ))
    
    return rec_set


def manage_anticoagulation_around_procedures(
    patient: "Patient",
    procedure_bleed_risk: str,  # "low", "high"
    is_urgent: bool = False,
) -> RecommendationSet:
    """
    Periprocedural anticoagulation management.
    
    Per ESC 2020 Section 11.2.5
    """
    rec_set = RecommendationSet(
        title="Periprocedural Anticoagulation Management",
        primary_guideline="ESC AF 2020",
    )
    
    on_doac = patient.is_on_medication("doac")
    on_warfarin = patient.is_on_medication("warfarin")
    
    if is_urgent:
        if on_doac:
            rec_set.add(guideline_recommendation(
                action="Urgent procedure on DOAC: Check anti-Xa (apixaban/rivaroxaban/edoxaban) or dTT (dabigatran). Consider reversal agent if active bleeding.",
                guideline_key="esc_af_2020",
                evidence_class=EvidenceClass.IIA,
                evidence_level=EvidenceLevel.C,
                category=RecommendationCategory.PROCEDURE,
                urgency=Urgency.URGENT,
                section="11.2.5",
            ))
        return rec_set
    
    if procedure_bleed_risk == "low":
        rec_set.add(guideline_recommendation(
            action="Low bleeding risk procedure: May perform on uninterrupted anticoagulation or with brief omission (1-2 doses DOAC)",
            guideline_key="esc_af_2020",
            evidence_class=EvidenceClass.IIA,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PROCEDURE,
            section="11.2.5",
            studies=["BRUISE CONTROL", "COMPARE"],
        ))
    else:
        rec_set.add(guideline_recommendation(
            action="High bleeding risk procedure: Stop DOAC 24-48h before (longer for dabigatran if CKD). Bridging generally NOT recommended.",
            guideline_key="esc_af_2020",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PROCEDURE,
            section="11.2.5",
            studies=["BRIDGE (no benefit of bridging)", "PERIOP-2"],
        ))
    
    return rec_set
