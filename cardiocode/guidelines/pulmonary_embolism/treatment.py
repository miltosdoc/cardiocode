"""
Pulmonary Embolism Treatment (ESC 2019).

Treatment recommendations for acute PE including anticoagulation and reperfusion.
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


class PERiskCategory(Enum):
    """PE risk stratification categories."""
    HIGH = "high"                    # Hemodynamic instability
    INTERMEDIATE_HIGH = "intermediate_high"  # sPESI >= 1 + RV dysfunction + elevated troponin
    INTERMEDIATE_LOW = "intermediate_low"    # sPESI >= 1 + RV dysfunction OR elevated troponin
    LOW = "low"                      # sPESI = 0


def get_pe_treatment_recommendations(
    risk_category: PERiskCategory,
    hemodynamically_unstable: bool = False,
    rv_dysfunction: bool = False,
    elevated_troponin: bool = False,
    bleeding_risk_high: bool = False,
    renal_impairment: bool = False,
    pregnancy: bool = False,
    cancer_associated: bool = False,
) -> RecommendationSet:
    """
    Get PE treatment recommendations based on risk stratification.

    ESC 2019 PE Guidelines - Section 6.

    Args:
        risk_category: PE risk category (high, intermediate-high, intermediate-low, low)
        hemodynamically_unstable: Shock or persistent hypotension
        rv_dysfunction: RV dysfunction on echo or CT
        elevated_troponin: Elevated cardiac troponin
        bleeding_risk_high: High bleeding risk
        renal_impairment: Significant renal impairment (eGFR < 30)
        pregnancy: Patient is pregnant
        cancer_associated: Cancer-associated VTE

    Returns:
        RecommendationSet with treatment recommendations
    """
    rec_set = RecommendationSet(
        title="PE Treatment Recommendations",
        description=f"ESC 2019 PE Guidelines - {risk_category.value} risk",
        primary_guideline="ESC PE 2019",
    )

    # HIGH RISK PE
    if risk_category == PERiskCategory.HIGH or hemodynamically_unstable:
        rec_set.add(guideline_recommendation(
            action="Initiate anticoagulation with unfractionated heparin (UFH) immediately",
            guideline_key="esc_pe_2019",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.PHARMACOTHERAPY,
            urgency=Urgency.EMERGENT,
            rationale="UFH preferred in high-risk PE due to short half-life and reversibility",
            monitoring="aPTT target 1.5-2.5x control",
        ))

        rec_set.add(guideline_recommendation(
            action="Primary reperfusion therapy (systemic thrombolysis) is recommended",
            guideline_key="esc_pe_2019",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PROCEDURE,
            urgency=Urgency.EMERGENT,
            rationale="High-risk PE with hemodynamic instability has high mortality without reperfusion",
            contraindications=["Active bleeding", "Recent major surgery", "Recent stroke", "Intracranial disease"],
        ))

        rec_set.add(guideline_recommendation(
            action="If thrombolysis contraindicated/failed, consider surgical embolectomy or catheter-directed therapy",
            guideline_key="esc_pe_2019",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.PROCEDURE,
            urgency=Urgency.EMERGENT,
            rationale="Alternative reperfusion strategies when systemic thrombolysis not possible",
        ))

        return rec_set

    # INTERMEDIATE-HIGH RISK PE
    if risk_category == PERiskCategory.INTERMEDIATE_HIGH:
        rec_set.add(guideline_recommendation(
            action="Initiate anticoagulation immediately (LMWH or fondaparinux preferred)",
            guideline_key="esc_pe_2019",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.A,
            category=RecommendationCategory.PHARMACOTHERAPY,
            urgency=Urgency.EMERGENT,
            rationale="Parenteral anticoagulation should not be delayed",
        ))

        rec_set.add(guideline_recommendation(
            action="Monitor closely for hemodynamic decompensation",
            guideline_key="esc_pe_2019",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.MONITORING,
            urgency=Urgency.URGENT,
            rationale="Intermediate-high risk patients may deteriorate and require escalation",
        ))

        rec_set.add(guideline_recommendation(
            action="Consider rescue thrombolysis if hemodynamic deterioration occurs",
            guideline_key="esc_pe_2019",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PROCEDURE,
            urgency=Urgency.URGENT,
            rationale="Rescue reperfusion for patients who deteriorate despite anticoagulation",
        ))

        return rec_set

    # INTERMEDIATE-LOW RISK PE
    if risk_category == PERiskCategory.INTERMEDIATE_LOW:
        rec_set.add(guideline_recommendation(
            action="Initiate anticoagulation (LMWH, fondaparinux, or DOAC)",
            guideline_key="esc_pe_2019",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.A,
            category=RecommendationCategory.PHARMACOTHERAPY,
            urgency=Urgency.URGENT,
            rationale="Prompt anticoagulation reduces mortality and recurrence",
        ))

        rec_set.add(guideline_recommendation(
            action="Hospital admission for monitoring",
            guideline_key="esc_pe_2019",
            evidence_class=EvidenceClass.IIA,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.MONITORING,
            urgency=Urgency.URGENT,
            rationale="Intermediate risk warrants observation for potential deterioration",
        ))

        return rec_set

    # LOW RISK PE
    if risk_category == PERiskCategory.LOW:
        rec_set.add(guideline_recommendation(
            action="Consider early discharge and home treatment if appropriate criteria met",
            guideline_key="esc_pe_2019",
            evidence_class=EvidenceClass.IIA,
            evidence_level=EvidenceLevel.A,
            category=RecommendationCategory.MONITORING,
            urgency=Urgency.ROUTINE,
            rationale="Low-risk PE can be safely treated at home with proper anticoagulation",
            conditions=["sPESI = 0", "Adequate home support", "No high bleeding risk", "No severe comorbidities"],
        ))

    # Anticoagulation recommendations (all risk categories)
    if cancer_associated:
        rec_set.add(guideline_recommendation(
            action="LMWH or edoxaban/rivaroxaban for cancer-associated PE",
            guideline_key="esc_pe_2019",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.A,
            category=RecommendationCategory.PHARMACOTHERAPY,
            urgency=Urgency.URGENT,
            rationale="LMWH preferred; DOACs alternative except with GI/GU cancers (higher bleeding)",
            monitoring="Monitor for bleeding, especially with GI/GU malignancies",
        ))
    elif pregnancy:
        rec_set.add(guideline_recommendation(
            action="LMWH is the anticoagulant of choice in pregnancy",
            guideline_key="esc_pe_2019",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PHARMACOTHERAPY,
            urgency=Urgency.URGENT,
            rationale="DOACs and warfarin are contraindicated in pregnancy",
            monitoring="Weight-based dosing, may need anti-Xa monitoring",
        ))
    elif renal_impairment:
        rec_set.add(guideline_recommendation(
            action="Use UFH or dose-adjusted LMWH for severe renal impairment",
            guideline_key="esc_pe_2019",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.PHARMACOTHERAPY,
            urgency=Urgency.URGENT,
            rationale="DOACs and standard LMWH doses may accumulate with eGFR < 30",
        ))
    else:
        rec_set.add(guideline_recommendation(
            action="DOAC (rivaroxaban, apixaban, edoxaban, or dabigatran) recommended over VKA",
            guideline_key="esc_pe_2019",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.A,
            category=RecommendationCategory.PHARMACOTHERAPY,
            urgency=Urgency.URGENT,
            rationale="DOACs have better safety profile and no INR monitoring required",
        ))

    return rec_set


def assess_thrombolysis_indication(
    hemodynamically_unstable: bool = False,
    rv_dysfunction: bool = False,
    elevated_troponin: bool = False,
    deteriorating: bool = False,
    absolute_contraindication: bool = False,
    relative_contraindication: bool = False,
) -> RecommendationSet:
    """
    Assess indication for thrombolytic therapy in PE.

    ESC 2019 PE Guidelines - Section 6.2.

    Args:
        hemodynamically_unstable: Shock or persistent hypotension
        rv_dysfunction: RV dysfunction on imaging
        elevated_troponin: Elevated cardiac biomarkers
        deteriorating: Clinical deterioration on anticoagulation
        absolute_contraindication: Absolute contraindication to lysis
        relative_contraindication: Relative contraindication to lysis

    Returns:
        RecommendationSet with thrombolysis recommendations
    """
    rec_set = RecommendationSet(
        title="Thrombolysis Assessment in PE",
        description="ESC 2019 PE Guidelines",
        primary_guideline="ESC PE 2019",
    )

    if absolute_contraindication:
        rec_set.add(guideline_recommendation(
            action="Systemic thrombolysis is contraindicated",
            guideline_key="esc_pe_2019",
            evidence_class=EvidenceClass.III,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.CONTRAINDICATION,
            urgency=Urgency.EMERGENT,
            rationale="Absolute contraindications include recent hemorrhagic stroke, active bleeding, intracranial neoplasm",
            alternatives=["Surgical embolectomy", "Catheter-directed therapy"],
        ))
        return rec_set

    if hemodynamically_unstable:
        rec_set.add(guideline_recommendation(
            action="Systemic thrombolysis is RECOMMENDED",
            guideline_key="esc_pe_2019",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PROCEDURE,
            urgency=Urgency.EMERGENT,
            rationale="High-risk PE with hemodynamic instability has mortality benefit from thrombolysis",
        ))
    elif rv_dysfunction and elevated_troponin and deteriorating:
        rec_set.add(guideline_recommendation(
            action="Rescue thrombolysis RECOMMENDED for hemodynamic deterioration",
            guideline_key="esc_pe_2019",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PROCEDURE,
            urgency=Urgency.EMERGENT,
            rationale="Intermediate-high risk patients deteriorating on anticoagulation benefit from rescue lysis",
        ))
    elif rv_dysfunction and elevated_troponin:
        rec_set.add(guideline_recommendation(
            action="Thrombolysis NOT routinely recommended; monitor for deterioration",
            guideline_key="esc_pe_2019",
            evidence_class=EvidenceClass.III,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PROCEDURE,
            urgency=Urgency.ROUTINE,
            rationale="Routine thrombolysis in intermediate-high risk PE did not show net benefit (PEITHO trial)",
        ))
    else:
        rec_set.add(guideline_recommendation(
            action="Thrombolysis NOT recommended",
            guideline_key="esc_pe_2019",
            evidence_class=EvidenceClass.III,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.CONTRAINDICATION,
            urgency=Urgency.ROUTINE,
            rationale="No evidence of benefit in intermediate-low or low-risk PE",
        ))

    return rec_set


def get_anticoagulation_recommendations(
    duration_months: Optional[int] = None,
    provoked: bool = False,
    unprovoked: bool = False,
    major_transient_risk: bool = False,
    minor_transient_risk: bool = False,
    cancer_active: bool = False,
    recurrent_vte: bool = False,
    antiphospholipid_syndrome: bool = False,
) -> RecommendationSet:
    """
    Get anticoagulation duration recommendations for PE.

    ESC 2019 PE Guidelines - Section 7.

    Args:
        duration_months: Current duration of anticoagulation
        provoked: PE provoked by major/minor risk factor
        unprovoked: Unprovoked PE
        major_transient_risk: Major transient risk factor (surgery, trauma, immobilization)
        minor_transient_risk: Minor transient risk factor (estrogen, pregnancy, travel)
        cancer_active: Active cancer
        recurrent_vte: Recurrent VTE
        antiphospholipid_syndrome: Antiphospholipid syndrome

    Returns:
        RecommendationSet with duration recommendations
    """
    rec_set = RecommendationSet(
        title="Anticoagulation Duration for PE",
        description="ESC 2019 PE Guidelines",
        primary_guideline="ESC PE 2019",
    )

    # All patients need minimum 3 months
    rec_set.add(guideline_recommendation(
        action="Minimum 3 months of anticoagulation for all PE patients",
        guideline_key="esc_pe_2019",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.A,
        category=RecommendationCategory.PHARMACOTHERAPY,
        urgency=Urgency.ROUTINE,
        rationale="Three months is the minimum effective treatment duration",
    ))

    # Specific duration recommendations
    if major_transient_risk:
        rec_set.add(guideline_recommendation(
            action="3 months of anticoagulation, then discontinue",
            guideline_key="esc_pe_2019",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PHARMACOTHERAPY,
            urgency=Urgency.ROUTINE,
            rationale="Low recurrence risk after major transient risk factor resolves",
        ))

    elif minor_transient_risk:
        rec_set.add(guideline_recommendation(
            action="3 months minimum; consider extended therapy based on bleeding risk",
            guideline_key="esc_pe_2019",
            evidence_class=EvidenceClass.IIA,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.PHARMACOTHERAPY,
            urgency=Urgency.ROUTINE,
            rationale="Intermediate recurrence risk; individualize duration",
        ))

    elif unprovoked or recurrent_vte:
        rec_set.add(guideline_recommendation(
            action="Extended/indefinite anticoagulation recommended if bleeding risk acceptable",
            guideline_key="esc_pe_2019",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.A,
            category=RecommendationCategory.PHARMACOTHERAPY,
            urgency=Urgency.ROUTINE,
            rationale="High recurrence risk with unprovoked or recurrent VTE",
            monitoring="Reassess annually for bleeding risk vs recurrence risk",
        ))

    if cancer_active:
        rec_set.add(guideline_recommendation(
            action="Extended anticoagulation for duration of active cancer",
            guideline_key="esc_pe_2019",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.A,
            category=RecommendationCategory.PHARMACOTHERAPY,
            urgency=Urgency.ROUTINE,
            rationale="High recurrence risk while cancer is active",
        ))

    if antiphospholipid_syndrome:
        rec_set.add(guideline_recommendation(
            action="Indefinite VKA anticoagulation (DOACs not recommended)",
            guideline_key="esc_pe_2019",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PHARMACOTHERAPY,
            urgency=Urgency.ROUTINE,
            rationale="DOACs showed higher recurrence in APS; VKA preferred",
        ))

    return rec_set
