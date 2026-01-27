"""
CV Prevention Treatment Targets (ESC 2021).

Treatment targets for lipids, blood pressure, and lifestyle.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional

from cardiocode.core.recommendation import (
    RecommendationSet,
    RecommendationCategory,
    Urgency,
    guideline_recommendation,
)
from cardiocode.core.evidence import EvidenceClass, EvidenceLevel
from cardiocode.guidelines.cv_prevention.risk_assessment import CVRiskLevel


@dataclass
class LipidTarget:
    """LDL-C and lipid targets."""
    ldl_target_mmol: float
    ldl_target_mg: int
    ldl_reduction_percent: int
    additional_targets: List[str]


@dataclass
class BPTarget:
    """Blood pressure targets."""
    systolic_target: str
    diastolic_target: str
    notes: List[str]


def get_lipid_targets(risk_level: CVRiskLevel) -> LipidTarget:
    """
    Get LDL-C targets based on CV risk level.

    ESC 2021 CV Prevention Guidelines.

    Args:
        risk_level: CV risk category

    Returns:
        LipidTarget with LDL goals
    """
    if risk_level == CVRiskLevel.VERY_HIGH:
        return LipidTarget(
            ldl_target_mmol=1.4,
            ldl_target_mg=55,
            ldl_reduction_percent=50,
            additional_targets=[
                "LDL-C <1.4 mmol/L (55 mg/dL) AND >=50% reduction from baseline",
                "For recurrent events within 2 years on max statin, consider <1.0 mmol/L (40 mg/dL)",
                "Non-HDL-C <2.2 mmol/L (85 mg/dL)",
                "ApoB <65 mg/dL",
            ],
        )
    elif risk_level == CVRiskLevel.HIGH:
        return LipidTarget(
            ldl_target_mmol=1.8,
            ldl_target_mg=70,
            ldl_reduction_percent=50,
            additional_targets=[
                "LDL-C <1.8 mmol/L (70 mg/dL) AND >=50% reduction from baseline",
                "Non-HDL-C <2.6 mmol/L (100 mg/dL)",
                "ApoB <80 mg/dL",
            ],
        )
    else:  # LOW_MODERATE
        return LipidTarget(
            ldl_target_mmol=2.6,
            ldl_target_mg=100,
            ldl_reduction_percent=0,
            additional_targets=[
                "LDL-C <2.6 mmol/L (100 mg/dL)",
                "Consider <1.8 mmol/L (70 mg/dL) if high-risk features present",
                "Non-HDL-C <3.4 mmol/L (130 mg/dL)",
            ],
        )


def get_bp_targets(
    age: int,
    diabetes: bool = False,
    ckd: bool = False,
    cad: bool = False,
    stroke: bool = False,
) -> BPTarget:
    """
    Get blood pressure targets.

    ESC 2021 CV Prevention Guidelines.

    Args:
        age: Patient age
        diabetes: Has diabetes
        ckd: Has CKD
        cad: Has CAD
        stroke: Has stroke history

    Returns:
        BPTarget with BP goals
    """
    notes = []

    if age >= 70:
        systolic = "<140 mmHg (130-139 if tolerated)"
        notes.append("More cautious approach in elderly")
        notes.append("Avoid SBP <120 mmHg")
    elif diabetes or ckd or cad or stroke:
        systolic = "<130 mmHg (target 120-129)"
        notes.append("Tighter control for high-risk conditions")
    else:
        systolic = "<140 mmHg (target 130)"
        notes.append("Target <130 mmHg if tolerated in younger patients")

    diastolic = "<80 mmHg"
    notes.append("Avoid DBP <70 mmHg especially in CAD")

    return BPTarget(
        systolic_target=systolic,
        diastolic_target=diastolic,
        notes=notes,
    )


def get_prevention_recommendations(
    risk_level: CVRiskLevel,
    age: int,
    ldl_cholesterol: Optional[float] = None,
    systolic_bp: Optional[int] = None,
    smoking: bool = False,
    diabetes: bool = False,
    obesity: bool = False,
) -> RecommendationSet:
    """
    Get comprehensive CV prevention recommendations.

    ESC 2021 CV Prevention Guidelines.

    Args:
        risk_level: CV risk category
        age: Patient age
        ldl_cholesterol: Current LDL-C (mmol/L)
        systolic_bp: Current SBP
        smoking: Current smoker
        diabetes: Has diabetes
        obesity: BMI >= 30

    Returns:
        RecommendationSet with prevention recommendations
    """
    rec_set = RecommendationSet(
        title="CV Prevention Recommendations",
        description=f"ESC 2021 Prevention Guidelines - {risk_level.value} risk",
        primary_guideline="ESC Prevention 2021",
    )

    # LIFESTYLE - All patients
    rec_set.add(guideline_recommendation(
        action="Smoking cessation is the most cost-effective prevention strategy",
        guideline_key="esc_prevention_2021",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.A,
        category=RecommendationCategory.LIFESTYLE,
        urgency=Urgency.URGENT if smoking else Urgency.ROUTINE,
        rationale="Smoking cessation reduces CV risk by 50% within 1-2 years",
    ))

    rec_set.add(guideline_recommendation(
        action="Mediterranean or similar healthy diet recommended",
        guideline_key="esc_prevention_2021",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.A,
        category=RecommendationCategory.LIFESTYLE,
        urgency=Urgency.ROUTINE,
        rationale="Mediterranean diet reduces CV events by 30%",
    ))

    rec_set.add(guideline_recommendation(
        action="Regular physical activity: 150-300 min/week moderate or 75-150 min/week vigorous",
        guideline_key="esc_prevention_2021",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.A,
        category=RecommendationCategory.LIFESTYLE,
        urgency=Urgency.ROUTINE,
    ))

    if obesity:
        rec_set.add(guideline_recommendation(
            action="Weight reduction to achieve BMI 20-25 kg/m²",
            guideline_key="esc_prevention_2021",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.A,
            category=RecommendationCategory.LIFESTYLE,
            urgency=Urgency.ROUTINE,
            rationale="Weight loss improves all CV risk factors",
        ))

    # LIPID THERAPY
    lipid_targets = get_lipid_targets(risk_level)

    if risk_level == CVRiskLevel.VERY_HIGH:
        rec_set.add(guideline_recommendation(
            action=f"High-intensity statin therapy to achieve LDL-C <{lipid_targets.ldl_target_mmol} mmol/L ({lipid_targets.ldl_target_mg} mg/dL)",
            guideline_key="esc_prevention_2021",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.A,
            category=RecommendationCategory.PHARMACOTHERAPY,
            urgency=Urgency.URGENT,
            rationale="Every 1 mmol/L LDL reduction = 22% relative risk reduction",
        ))

        rec_set.add(guideline_recommendation(
            action="Add ezetimibe if target not achieved on maximum tolerated statin",
            guideline_key="esc_prevention_2021",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PHARMACOTHERAPY,
            urgency=Urgency.ROUTINE,
        ))

        rec_set.add(guideline_recommendation(
            action="Add PCSK9 inhibitor if target still not achieved on statin + ezetimibe",
            guideline_key="esc_prevention_2021",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.A,
            category=RecommendationCategory.PHARMACOTHERAPY,
            urgency=Urgency.ROUTINE,
            rationale="PCSK9i provide additional 50-60% LDL reduction",
        ))

    elif risk_level == CVRiskLevel.HIGH:
        rec_set.add(guideline_recommendation(
            action=f"Statin therapy recommended to achieve LDL-C <{lipid_targets.ldl_target_mmol} mmol/L ({lipid_targets.ldl_target_mg} mg/dL)",
            guideline_key="esc_prevention_2021",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.A,
            category=RecommendationCategory.PHARMACOTHERAPY,
            urgency=Urgency.SOON,
        ))

    else:  # LOW_MODERATE
        if ldl_cholesterol and ldl_cholesterol > 3.0:
            rec_set.add(guideline_recommendation(
                action="Consider statin if LDL-C remains >3.0 mmol/L despite lifestyle measures",
                guideline_key="esc_prevention_2021",
                evidence_class=EvidenceClass.IIA,
                evidence_level=EvidenceLevel.A,
                category=RecommendationCategory.PHARMACOTHERAPY,
                urgency=Urgency.ROUTINE,
            ))

    # BLOOD PRESSURE
    bp_targets = get_bp_targets(age, diabetes)

    if systolic_bp and systolic_bp >= 140:
        rec_set.add(guideline_recommendation(
            action=f"Antihypertensive treatment to target SBP {bp_targets.systolic_target}",
            guideline_key="esc_prevention_2021",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.A,
            category=RecommendationCategory.PHARMACOTHERAPY,
            urgency=Urgency.URGENT if systolic_bp >= 160 else Urgency.SOON,
        ))

    # DIABETES
    if diabetes:
        rec_set.add(guideline_recommendation(
            action="SGLT2 inhibitor or GLP-1 RA recommended for diabetes with CVD or high CV risk",
            guideline_key="esc_prevention_2021",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.A,
            category=RecommendationCategory.PHARMACOTHERAPY,
            urgency=Urgency.URGENT,
            rationale="CV outcome benefit independent of glucose lowering",
        ))

        rec_set.add(guideline_recommendation(
            action="HbA1c target <7% (individualized 6.5-8% based on patient factors)",
            guideline_key="esc_prevention_2021",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.A,
            category=RecommendationCategory.MONITORING,
            urgency=Urgency.ROUTINE,
        ))

    # ANTIPLATELET THERAPY
    if risk_level == CVRiskLevel.VERY_HIGH:
        rec_set.add(guideline_recommendation(
            action="Aspirin for secondary prevention in established CVD",
            guideline_key="esc_prevention_2021",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.A,
            category=RecommendationCategory.PHARMACOTHERAPY,
            urgency=Urgency.URGENT,
        ))
    else:
        rec_set.add(guideline_recommendation(
            action="Aspirin NOT routinely recommended for primary prevention",
            guideline_key="esc_prevention_2021",
            evidence_class=EvidenceClass.III,
            evidence_level=EvidenceLevel.A,
            category=RecommendationCategory.PHARMACOTHERAPY,
            urgency=Urgency.ROUTINE,
            rationale="Bleeding risk generally outweighs benefit in primary prevention",
        ))

    return rec_set
