"""
Device Therapy for Heart Failure - ESC 2021 Guidelines.

Implements device indications from ESC HF 2021:
- ICD for primary and secondary prevention
- CRT-P and CRT-D indications
- Device selection algorithm
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
)
from cardiocode.core.evidence import EvidenceClass, EvidenceLevel


@dataclass
class ICDAssessment:
    """Result of ICD indication assessment."""
    indicated: bool
    indication_type: Optional[str] = None  # "primary", "secondary"
    recommendation: Optional[Recommendation] = None
    contraindications: List[str] = None
    considerations: List[str] = None
    
    def __post_init__(self):
        if self.contraindications is None:
            self.contraindications = []
        if self.considerations is None:
            self.considerations = []


@dataclass
class CRTAssessment:
    """Result of CRT indication assessment."""
    indicated: bool
    device_type: Optional[str] = None  # "CRT-P", "CRT-D"
    recommendation: Optional[Recommendation] = None
    qrs_duration: Optional[int] = None
    qrs_morphology: Optional[str] = None  # "LBBB", "non-LBBB"
    considerations: List[str] = None
    
    def __post_init__(self):
        if self.considerations is None:
            self.considerations = []


def assess_icd_indication(patient: "Patient") -> ICDAssessment:
    """
    Assess ICD indication per ESC 2021 HF Guidelines.
    
    Per Section 10.1: Implantable cardioverter-defibrillator
    
    PRIMARY PREVENTION (Class I, Level A):
    - Symptomatic HF (NYHA II-III)
    - LVEF <= 35% despite >= 3 months of OMT
    - Expected survival > 1 year with good functional status
    - Ischemic etiology OR
    - Non-ischemic DCM
    
    SECONDARY PREVENTION (Class I, Level A):
    - Survivors of VF or hemodynamically unstable VT
    - Without reversible cause
    - Expected survival > 1 year
    
    Args:
        patient: Patient object
    
    Returns:
        ICDAssessment with indication and recommendations
    """
    contraindications = []
    considerations = []
    
    # Check life expectancy consideration
    if patient.age and patient.age > 80:
        considerations.append("Age > 80: carefully consider life expectancy and quality of life")
    
    # Check for existing device
    for device in patient.devices:
        if device.device_type in ["icd", "crt_d"]:
            return ICDAssessment(
                indicated=False,
                considerations=["Patient already has ICD/CRT-D in place"],
            )
    
    # SECONDARY PREVENTION - highest priority
    if patient.has_diagnosis("ventricular_fibrillation") or patient.has_diagnosis("sudden_cardiac_arrest"):
        # Survivor of VF/VT arrest
        return ICDAssessment(
            indicated=True,
            indication_type="secondary",
            recommendation=guideline_recommendation(
                action="ICD implantation for secondary prevention of sudden cardiac death",
                guideline_key="esc_hf_2021",
                evidence_class=EvidenceClass.I,
                evidence_level=EvidenceLevel.A,
                category=RecommendationCategory.DEVICE,
                urgency=Urgency.URGENT,
                section="10.1",
                studies=["AVID", "CIDS", "CASH"],
                rationale="SCD survivor without reversible cause. ICD reduces mortality.",
                conditions=["No reversible cause", "Expected survival > 1 year"],
            ),
            considerations=considerations,
        )
    
    if patient.has_diagnosis("ventricular_tachycardia"):
        considerations.append("Evaluate if VT was hemodynamically tolerated and if reversible cause present")
    
    # PRIMARY PREVENTION
    if patient.lvef is None:
        return ICDAssessment(
            indicated=False,
            considerations=["LVEF required to assess ICD indication"],
        )
    
    # Check LVEF criterion
    if patient.lvef > 35:
        return ICDAssessment(
            indicated=False,
            considerations=[f"LVEF {patient.lvef}% > 35%. ICD generally not indicated for primary prevention."],
        )
    
    # LVEF <= 35%
    # Check NYHA class
    if patient.nyha_class is None:
        considerations.append("NYHA class needed for complete assessment")
    elif patient.nyha_class.value == 1:
        considerations.append("NYHA Class I: ICD benefit less established. Reassess if symptoms progress.")
        return ICDAssessment(
            indicated=False,
            indication_type="primary",
            considerations=considerations + ["Consider ICD if additional risk factors present"],
        )
    elif patient.nyha_class.value == 4:
        considerations.append("NYHA Class IV: ICD generally not recommended unless CRT or transplant candidate")
        return ICDAssessment(
            indicated=False,
            indication_type="primary",
            considerations=considerations,
        )
    
    # NYHA II-III with LVEF <= 35%
    # Check etiology
    is_ischemic = patient.has_diagnosis("coronary_artery_disease") or patient.has_diagnosis("mi")
    
    if is_ischemic:
        return ICDAssessment(
            indicated=True,
            indication_type="primary",
            recommendation=guideline_recommendation(
                action="ICD for primary prevention of sudden cardiac death (ischemic cardiomyopathy, LVEF <= 35%, NYHA II-III)",
                guideline_key="esc_hf_2021",
                evidence_class=EvidenceClass.I,
                evidence_level=EvidenceLevel.A,
                category=RecommendationCategory.DEVICE,
                urgency=Urgency.ROUTINE,
                section="10.1",
                studies=["MADIT-II", "SCD-HeFT"],
                rationale="Ischemic HFrEF with persistent LVEF <= 35% despite >= 3 months OMT",
                conditions=["On optimal medical therapy >= 3 months", "Expected survival > 1 year", "Good functional status"],
            ),
            considerations=considerations,
        )
    else:
        # Non-ischemic
        return ICDAssessment(
            indicated=True,
            indication_type="primary",
            recommendation=guideline_recommendation(
                action="ICD for primary prevention of sudden cardiac death (non-ischemic cardiomyopathy, LVEF <= 35%, NYHA II-III)",
                guideline_key="esc_hf_2021",
                evidence_class=EvidenceClass.IIA,
                evidence_level=EvidenceLevel.A,
                category=RecommendationCategory.DEVICE,
                urgency=Urgency.ROUTINE,
                section="10.1",
                studies=["SCD-HeFT", "DEFINITE", "DANISH"],
                rationale="Non-ischemic DCM with LVEF <= 35%. DANISH showed no mortality benefit but SCD reduction. Consider individual risk factors.",
                conditions=["On optimal medical therapy >= 3 months", "Expected survival > 1 year"],
            ),
            considerations=considerations + ["DANISH trial showed no overall mortality benefit in non-ischemic DCM - discuss with patient"],
        )


def assess_crt_indication(patient: "Patient") -> CRTAssessment:
    """
    Assess CRT (Cardiac Resynchronization Therapy) indication per ESC 2021.
    
    Per Section 10.2: Cardiac resynchronization therapy
    
    KEY CRITERIA:
    1. Symptomatic HF (NYHA II-IV ambulatory) despite OMT
    2. LVEF <= 35%
    3. QRS duration and morphology:
       - LBBB with QRS >= 150ms: Class I
       - LBBB with QRS 130-149ms: Class I
       - Non-LBBB with QRS >= 150ms: Class IIa
       - Non-LBBB with QRS 130-149ms: Class IIb
    4. Sinus rhythm (AF with CRT is Class IIa)
    
    Args:
        patient: Patient object
    
    Returns:
        CRTAssessment with indication and device recommendation
    """
    considerations = []
    
    # Check LVEF
    if patient.lvef is None:
        return CRTAssessment(
            indicated=False,
            considerations=["LVEF required to assess CRT indication"],
        )
    
    if patient.lvef > 35:
        return CRTAssessment(
            indicated=False,
            considerations=[f"LVEF {patient.lvef}% > 35%. CRT generally not indicated."],
        )
    
    # Check QRS
    if patient.ecg is None or patient.ecg.qrs_duration is None:
        return CRTAssessment(
            indicated=False,
            considerations=["QRS duration required to assess CRT indication. Obtain ECG."],
        )
    
    qrs = patient.ecg.qrs_duration
    has_lbbb = patient.ecg.lbbb
    
    if qrs < 130:
        return CRTAssessment(
            indicated=False,
            qrs_duration=qrs,
            considerations=["QRS < 130ms. CRT not indicated."],
        )
    
    # Check NYHA
    if patient.nyha_class is None:
        considerations.append("NYHA class needed for complete assessment")
    elif patient.nyha_class.value == 1:
        return CRTAssessment(
            indicated=False,
            qrs_duration=qrs,
            considerations=["NYHA Class I. CRT generally not indicated unless upgrading pacemaker."],
        )
    
    # Determine indication strength based on QRS and morphology
    qrs_morphology = "LBBB" if has_lbbb else "non-LBBB"
    
    # Determine evidence class
    if has_lbbb and qrs >= 150:
        evidence_class = EvidenceClass.I
        evidence_level = EvidenceLevel.A
        strength = "strong"
    elif has_lbbb and qrs >= 130:
        evidence_class = EvidenceClass.I
        evidence_level = EvidenceLevel.B
        strength = "strong"
    elif not has_lbbb and qrs >= 150:
        evidence_class = EvidenceClass.IIA
        evidence_level = EvidenceLevel.B
        strength = "moderate"
    else:  # non-LBBB, QRS 130-149
        evidence_class = EvidenceClass.IIB
        evidence_level = EvidenceLevel.B
        strength = "weak"
        considerations.append("Non-LBBB with QRS 130-149ms has weakest evidence for CRT benefit")
    
    # Check rhythm
    has_af = patient.af_type or (patient.ecg and patient.ecg.af_present)
    if has_af:
        considerations.append("AF present: CRT may be considered (Class IIa) if rate control allows BiV pacing >90%")
        if evidence_class == EvidenceClass.I:
            evidence_class = EvidenceClass.IIA
    
    # Determine device type (CRT-P vs CRT-D)
    icd_assessment = assess_icd_indication(patient)
    if icd_assessment.indicated:
        device_type = "CRT-D"
        device_rationale = "CRT-D recommended as patient also meets ICD criteria"
    else:
        device_type = "CRT-P"
        device_rationale = "CRT-P recommended (no ICD indication)"
    
    return CRTAssessment(
        indicated=True,
        device_type=device_type,
        qrs_duration=qrs,
        qrs_morphology=qrs_morphology,
        recommendation=guideline_recommendation(
            action=f"{device_type} implantation for symptomatic HFrEF with {qrs_morphology} and QRS {qrs}ms",
            guideline_key="esc_hf_2021",
            evidence_class=evidence_class,
            evidence_level=evidence_level,
            category=RecommendationCategory.DEVICE,
            urgency=Urgency.ROUTINE,
            section="10.2",
            studies=["COMPANION", "CARE-HF", "MADIT-CRT", "RAFT"],
            rationale=f"{device_rationale}. {strength.capitalize()} indication based on QRS morphology/duration.",
            conditions=["On optimal medical therapy", "LVEF <= 35%", f"QRS >= 130ms ({qrs}ms)"],
        ),
        considerations=considerations,
    )


def get_device_recommendations(patient: "Patient") -> RecommendationSet:
    """
    Get comprehensive device therapy recommendations for HF patient.
    
    Combines ICD and CRT assessments.
    """
    rec_set = RecommendationSet(
        title="Device Therapy Assessment",
        description="ICD and CRT indication assessment per ESC 2021 HF Guidelines",
        primary_guideline="ESC HF 2021",
    )
    
    # ICD assessment
    icd = assess_icd_indication(patient)
    if icd.recommendation:
        rec_set.add(icd.recommendation)
    for consideration in icd.considerations:
        rec_set.description += f"\n- ICD: {consideration}"
    
    # CRT assessment
    crt = assess_crt_indication(patient)
    if crt.recommendation:
        rec_set.add(crt.recommendation)
    for consideration in crt.considerations:
        rec_set.description += f"\n- CRT: {consideration}"
    
    return rec_set
