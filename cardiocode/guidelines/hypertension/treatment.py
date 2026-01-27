"""
Hypertension Treatment (ESC 2024).

Treatment recommendations, BP targets, and drug therapy.
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional, List

from cardiocode.core.types import Patient
from cardiocode.core.recommendation import (
    Recommendation,
    RecommendationSet,
    RecommendationCategory,
    Urgency,
    guideline_recommendation,
)
from cardiocode.core.evidence import EvidenceClass, EvidenceLevel

from cardiocode.guidelines.hypertension.diagnosis import BPCategory, CVRiskCategory


@dataclass
class BPTargetResult:
    """Blood pressure target recommendations."""
    systolic_target: str
    diastolic_target: str
    rationale: str
    caveats: List[str]


def get_bp_target(
    age: int,
    diabetes: bool = False,
    ckd: bool = False,
    coronary_artery_disease: bool = False,
    stroke: bool = False,
    heart_failure: bool = False,
    frailty: bool = False,
) -> BPTargetResult:
    """
    Get blood pressure target based on patient characteristics.

    ESC 2024 Hypertension Guidelines - Treatment targets.

    Args:
        age: Patient age
        diabetes: Diabetes mellitus
        ckd: Chronic kidney disease
        coronary_artery_disease: CAD
        stroke: Prior stroke
        heart_failure: Heart failure
        frailty: Frail elderly patient

    Returns:
        BPTargetResult with target BP and rationale
    """
    caveats = []

    # Frail elderly - be cautious
    if frailty or age >= 80:
        return BPTargetResult(
            systolic_target="<140-150 mmHg (individualized)",
            diastolic_target="<90 mmHg",
            rationale="Frail/very elderly patients require individualized targets based on tolerability",
            caveats=["Avoid excessive BP lowering", "Monitor for orthostatic hypotension", "Prioritize quality of life"],
        )

    # Standard targets by condition
    if heart_failure:
        caveats.append("Avoid excessive lowering in HFrEF")
        return BPTargetResult(
            systolic_target="<130 mmHg",
            diastolic_target="<80 mmHg",
            rationale="Lower targets improve HF outcomes, but avoid hypotension",
            caveats=caveats,
        )

    if diabetes:
        return BPTargetResult(
            systolic_target="120-130 mmHg",
            diastolic_target="<80 mmHg",
            rationale="Tighter control reduces microvascular and macrovascular complications in diabetes",
            caveats=["Target ~130 mmHg if tolerability issues"],
        )

    if ckd:
        return BPTargetResult(
            systolic_target="<130 mmHg",
            diastolic_target="<80 mmHg",
            rationale="Lower BP slows CKD progression",
            caveats=["ACEi/ARB preferred for renoprotection", "Monitor K+ and creatinine"],
        )

    if coronary_artery_disease:
        return BPTargetResult(
            systolic_target="<130 mmHg",
            diastolic_target="70-80 mmHg",
            rationale="Lower targets reduce CV events, but avoid excessive diastolic lowering",
            caveats=["Diastolic <70 may reduce coronary perfusion"],
        )

    if stroke:
        return BPTargetResult(
            systolic_target="<130 mmHg",
            diastolic_target="<80 mmHg",
            rationale="Lower BP reduces stroke recurrence",
            caveats=["May need higher targets acutely post-stroke"],
        )

    # Age-based targets for uncomplicated hypertension
    if age < 65:
        return BPTargetResult(
            systolic_target="120-130 mmHg",
            diastolic_target="70-79 mmHg",
            rationale="Standard target for younger adults without comorbidities",
            caveats=[],
        )
    else:
        return BPTargetResult(
            systolic_target="130-139 mmHg",
            diastolic_target="70-79 mmHg",
            rationale="Slightly higher target in elderly (65-79) to balance efficacy and tolerability",
            caveats=["Individualize based on frailty and tolerability"],
        )


def get_initial_therapy(
    bp_category: BPCategory,
    cv_risk: CVRiskCategory,
    age: int,
    diabetes: bool = False,
    ckd: bool = False,
    heart_failure: bool = False,
    coronary_artery_disease: bool = False,
    atrial_fibrillation: bool = False,
    black_ethnicity: bool = False,
    pregnancy: bool = False,
    gout: bool = False,
) -> RecommendationSet:
    """
    Get initial antihypertensive therapy recommendations.

    ESC 2024 Hypertension Guidelines - Drug treatment algorithm.

    Args:
        bp_category: Blood pressure category
        cv_risk: Cardiovascular risk category
        age: Patient age
        diabetes: Diabetes mellitus
        ckd: Chronic kidney disease
        heart_failure: Heart failure
        coronary_artery_disease: CAD
        atrial_fibrillation: AF
        black_ethnicity: Black African/Caribbean ethnicity
        pregnancy: Pregnant patient
        gout: History of gout

    Returns:
        RecommendationSet with drug therapy recommendations
    """
    rec_set = RecommendationSet(
        title="Antihypertensive Therapy",
        description="ESC 2024 Hypertension Guidelines",
        primary_guideline="ESC HTN 2024",
    )

    # Pregnancy - special case
    if pregnancy:
        rec_set.add(guideline_recommendation(
            action="Use labetalol, nifedipine, or methyldopa as first-line",
            guideline_key="esc_htn_2024",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PHARMACOTHERAPY,
            urgency=Urgency.URGENT,
            rationale="ACEi, ARB, and most other antihypertensives are contraindicated in pregnancy",
            contraindications=["ACE inhibitors", "ARBs", "Direct renin inhibitors"],
        ))
        return rec_set

    # Lifestyle for all
    rec_set.add(guideline_recommendation(
        action="Lifestyle modifications for all patients: salt restriction (<5g/day), healthy diet, weight loss if overweight, regular exercise, alcohol moderation, smoking cessation",
        guideline_key="esc_htn_2024",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.A,
        category=RecommendationCategory.LIFESTYLE,
        urgency=Urgency.ROUTINE,
        rationale="Lifestyle changes can reduce SBP by 5-15 mmHg",
    ))

    # When to start drug treatment
    if bp_category in [BPCategory.OPTIMAL, BPCategory.NORMAL]:
        rec_set.add(guideline_recommendation(
            action="No drug treatment indicated at this BP level",
            guideline_key="esc_htn_2024",
            evidence_class=EvidenceClass.III,
            evidence_level=EvidenceLevel.A,
            category=RecommendationCategory.PHARMACOTHERAPY,
            urgency=Urgency.ROUTINE,
            rationale="Drug treatment not recommended for normal/optimal BP",
        ))
        return rec_set

    if bp_category == BPCategory.HIGH_NORMAL:
        if cv_risk in [CVRiskCategory.VERY_HIGH]:
            rec_set.add(guideline_recommendation(
                action="Consider drug treatment for high-normal BP in very high CV risk patients",
                guideline_key="esc_htn_2024",
                evidence_class=EvidenceClass.IIB,
                evidence_level=EvidenceLevel.B,
                category=RecommendationCategory.PHARMACOTHERAPY,
                urgency=Urgency.ROUTINE,
                rationale="May benefit very high risk patients, especially with established CVD",
            ))
        else:
            rec_set.add(guideline_recommendation(
                action="Lifestyle modification; reassess in 3-6 months",
                guideline_key="esc_htn_2024",
                evidence_class=EvidenceClass.I,
                evidence_level=EvidenceLevel.A,
                category=RecommendationCategory.LIFESTYLE,
                urgency=Urgency.ROUTINE,
                rationale="Drug treatment not routinely indicated for high-normal BP",
            ))
            return rec_set

    # Drug treatment recommendations
    # Core drug classes: ACEi/ARB, CCB, Thiazide-like diuretic

    # Step 1: Initial combination (for most patients with grade 1-2 HTN)
    if bp_category in [BPCategory.GRADE_1_HTN, BPCategory.GRADE_2_HTN, BPCategory.GRADE_3_HTN, BPCategory.ISOLATED_SYSTOLIC]:

        # Compelling indications
        if heart_failure:
            rec_set.add(guideline_recommendation(
                action="ACEi/ARB + beta-blocker + diuretic as core therapy for HTN with HF",
                guideline_key="esc_htn_2024",
                evidence_class=EvidenceClass.I,
                evidence_level=EvidenceLevel.A,
                category=RecommendationCategory.PHARMACOTHERAPY,
                urgency=Urgency.URGENT,
                rationale="RAAS inhibitors and beta-blockers are disease-modifying in HFrEF",
            ))
            rec_set.add(guideline_recommendation(
                action="Add MRA (spironolactone/eplerenone) for additional BP and HF benefit",
                guideline_key="esc_htn_2024",
                evidence_class=EvidenceClass.I,
                evidence_level=EvidenceLevel.A,
                category=RecommendationCategory.PHARMACOTHERAPY,
                urgency=Urgency.URGENT,
            ))

        elif coronary_artery_disease:
            rec_set.add(guideline_recommendation(
                action="ACEi/ARB + beta-blocker as core therapy for HTN with CAD",
                guideline_key="esc_htn_2024",
                evidence_class=EvidenceClass.I,
                evidence_level=EvidenceLevel.A,
                category=RecommendationCategory.PHARMACOTHERAPY,
                urgency=Urgency.URGENT,
                rationale="Beta-blockers for rate control and anti-ischemic effect",
            ))

        elif diabetes or ckd:
            rec_set.add(guideline_recommendation(
                action="ACEi or ARB as first-line (renoprotective)",
                guideline_key="esc_htn_2024",
                evidence_class=EvidenceClass.I,
                evidence_level=EvidenceLevel.A,
                category=RecommendationCategory.PHARMACOTHERAPY,
                urgency=Urgency.URGENT,
                rationale="RAAS blockade reduces albuminuria and slows CKD progression",
                monitoring="Monitor creatinine and potassium 1-2 weeks after initiation",
            ))
            rec_set.add(guideline_recommendation(
                action="Add CCB or thiazide-like diuretic as second agent",
                guideline_key="esc_htn_2024",
                evidence_class=EvidenceClass.I,
                evidence_level=EvidenceLevel.A,
                category=RecommendationCategory.PHARMACOTHERAPY,
                urgency=Urgency.ROUTINE,
            ))

        elif atrial_fibrillation:
            rec_set.add(guideline_recommendation(
                action="Beta-blocker or non-DHP CCB for rate control + ACEi/ARB",
                guideline_key="esc_htn_2024",
                evidence_class=EvidenceClass.I,
                evidence_level=EvidenceLevel.B,
                category=RecommendationCategory.PHARMACOTHERAPY,
                urgency=Urgency.URGENT,
                rationale="Rate control is essential in AF; RAAS blockade may reduce AF recurrence",
            ))

        elif black_ethnicity:
            rec_set.add(guideline_recommendation(
                action="CCB or thiazide-like diuretic preferred as initial therapy",
                guideline_key="esc_htn_2024",
                evidence_class=EvidenceClass.IIA,
                evidence_level=EvidenceLevel.B,
                category=RecommendationCategory.PHARMACOTHERAPY,
                urgency=Urgency.ROUTINE,
                rationale="ACEi/ARB may be less effective as monotherapy in Black patients",
            ))
            rec_set.add(guideline_recommendation(
                action="Add ACEi/ARB if compelling indication (diabetes, CKD, HF)",
                guideline_key="esc_htn_2024",
                evidence_class=EvidenceClass.I,
                evidence_level=EvidenceLevel.A,
                category=RecommendationCategory.PHARMACOTHERAPY,
                urgency=Urgency.ROUTINE,
            ))

        else:
            # Standard initial therapy
            if bp_category == BPCategory.GRADE_1_HTN and cv_risk in [CVRiskCategory.LOW, CVRiskCategory.MODERATE]:
                rec_set.add(guideline_recommendation(
                    action="Consider starting with single-drug therapy (ACEi/ARB, CCB, or thiazide-like diuretic)",
                    guideline_key="esc_htn_2024",
                    evidence_class=EvidenceClass.IIA,
                    evidence_level=EvidenceLevel.B,
                    category=RecommendationCategory.PHARMACOTHERAPY,
                    urgency=Urgency.ROUTINE,
                    rationale="Low-risk grade 1 HTN may respond to single agent",
                ))
            else:
                rec_set.add(guideline_recommendation(
                    action="Start with dual combination: ACEi/ARB + CCB or ACEi/ARB + thiazide-like diuretic",
                    guideline_key="esc_htn_2024",
                    evidence_class=EvidenceClass.I,
                    evidence_level=EvidenceLevel.A,
                    category=RecommendationCategory.PHARMACOTHERAPY,
                    urgency=Urgency.URGENT,
                    rationale="Initial combination therapy achieves BP targets faster with better adherence",
                ))

        # Cautions
        if gout:
            rec_set.add(guideline_recommendation(
                action="Avoid thiazide diuretics if history of gout",
                guideline_key="esc_htn_2024",
                evidence_class=EvidenceClass.III,
                evidence_level=EvidenceLevel.C,
                category=RecommendationCategory.CONTRAINDICATION,
                urgency=Urgency.ROUTINE,
                rationale="Thiazides increase uric acid and can precipitate gout attacks",
                alternatives=["ACEi/ARB + CCB combination preferred"],
            ))

    # Step 2: Triple therapy if needed
    rec_set.add(guideline_recommendation(
        action="If BP not controlled on dual therapy, use triple combination: ACEi/ARB + CCB + thiazide-like diuretic",
        guideline_key="esc_htn_2024",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.A,
        category=RecommendationCategory.PHARMACOTHERAPY,
        urgency=Urgency.ROUTINE,
        rationale="Standard triple combination for resistant hypertension",
    ))

    # Step 3: Resistant hypertension
    rec_set.add(guideline_recommendation(
        action="If BP uncontrolled on optimized triple therapy, add spironolactone 25-50mg or other fourth-line agent",
        guideline_key="esc_htn_2024",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.A,
        category=RecommendationCategory.PHARMACOTHERAPY,
        urgency=Urgency.ROUTINE,
        rationale="Spironolactone is most effective fourth agent per PATHWAY-2 trial",
        monitoring="Monitor K+ especially if on ACEi/ARB",
        alternatives=["Amiloride", "Doxazosin", "Clonidine", "Beta-blocker"],
    ))

    return rec_set


def get_treatment_recommendations(
    systolic: int,
    diastolic: int,
    age: int,
    cv_risk: CVRiskCategory,
    **kwargs,
) -> RecommendationSet:
    """
    Get comprehensive treatment recommendations.

    Combines BP classification, targeting, and drug therapy.

    Args:
        systolic: Systolic BP
        diastolic: Diastolic BP
        age: Patient age
        cv_risk: CV risk category
        **kwargs: Additional parameters passed to get_initial_therapy

    Returns:
        Combined RecommendationSet
    """
    from cardiocode.guidelines.hypertension.diagnosis import classify_blood_pressure

    # Classify BP
    bp_result = classify_blood_pressure(systolic, diastolic)

    # Get target
    target = get_bp_target(
        age=age,
        diabetes=kwargs.get('diabetes', False),
        ckd=kwargs.get('ckd', False),
        coronary_artery_disease=kwargs.get('coronary_artery_disease', False),
        stroke=kwargs.get('stroke', False),
        heart_failure=kwargs.get('heart_failure', False),
        frailty=kwargs.get('frailty', False),
    )

    # Get therapy
    rec_set = get_initial_therapy(
        bp_category=bp_result.category,
        cv_risk=cv_risk,
        age=age,
        **kwargs,
    )

    # Add context
    rec_set.description = f"""
BP: {systolic}/{diastolic} mmHg ({bp_result.category.value})
Target: SBP {target.systolic_target}, DBP {target.diastolic_target}
CV Risk: {cv_risk.value}
"""

    return rec_set
