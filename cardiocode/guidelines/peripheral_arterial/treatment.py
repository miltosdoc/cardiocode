"""
Peripheral Arterial Disease Treatment (ESC 2024).

Treatment recommendations for PAD, AAA, and carotid disease.
"""

from __future__ import annotations
from typing import Optional, List

from cardiocode.core.recommendation import (
    RecommendationSet,
    RecommendationCategory,
    Urgency,
    guideline_recommendation,
)
from cardiocode.core.evidence import EvidenceClass, EvidenceLevel

from cardiocode.guidelines.peripheral_arterial.diagnosis import (
    PADFontaineStage,
    AAASize,
)


def get_pad_treatment(
    fontaine_stage: PADFontaineStage,
    cli_present: bool = False,
    abi: Optional[float] = None,
    diabetes: bool = False,
    ckd: bool = False,
    concomitant_cad: bool = False,
) -> RecommendationSet:
    """
    Get PAD treatment recommendations.

    ESC 2024 PAD Guidelines.

    Args:
        fontaine_stage: Fontaine classification
        cli_present: Critical limb ischemia
        abi: Ankle-brachial index
        diabetes: Has diabetes
        ckd: Has CKD
        concomitant_cad: Concomitant coronary artery disease

    Returns:
        RecommendationSet with treatment recommendations
    """
    rec_set = RecommendationSet(
        title="PAD Treatment Recommendations",
        description=f"ESC 2024 PAD Guidelines - {fontaine_stage.value}",
        primary_guideline="ESC PAD 2024",
    )

    # CRITICAL LIMB ISCHEMIA - Urgent
    if cli_present:
        rec_set.add(guideline_recommendation(
            action="Urgent vascular specialist referral within 24-48 hours",
            guideline_key="esc_pad_2024",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.REFERRAL,
            urgency=Urgency.EMERGENT,
            rationale="CLI has high risk of limb loss and mortality",
        ))

        rec_set.add(guideline_recommendation(
            action="Revascularization is recommended to prevent limb loss",
            guideline_key="esc_pad_2024",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PROCEDURE,
            urgency=Urgency.URGENT,
            rationale="Revascularization improves limb salvage rates",
        ))

        rec_set.add(guideline_recommendation(
            action="Pain management and wound care",
            guideline_key="esc_pad_2024",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.PHARMACOTHERAPY,
            urgency=Urgency.URGENT,
        ))

    # ALL PAD PATIENTS - CV Risk Modification
    rec_set.add(guideline_recommendation(
        action="Smoking cessation is essential - most important modifiable risk factor",
        guideline_key="esc_pad_2024",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.A,
        category=RecommendationCategory.LIFESTYLE,
        urgency=Urgency.URGENT,
        rationale="Smoking cessation reduces amputation risk and improves walking distance",
    ))

    rec_set.add(guideline_recommendation(
        action="Antiplatelet therapy with aspirin 75-100mg or clopidogrel 75mg daily",
        guideline_key="esc_pad_2024",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.A,
        category=RecommendationCategory.PHARMACOTHERAPY,
        urgency=Urgency.URGENT,
        rationale="Reduces MACE; clopidogrel may be preferred in PAD",
    ))

    rec_set.add(guideline_recommendation(
        action="Statin therapy to LDL-C <1.4 mmol/L (55 mg/dL)",
        guideline_key="esc_pad_2024",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.A,
        category=RecommendationCategory.PHARMACOTHERAPY,
        urgency=Urgency.URGENT,
        rationale="PAD is very high CV risk; aggressive LDL lowering indicated",
    ))

    rec_set.add(guideline_recommendation(
        action="Blood pressure control to <130/80 mmHg",
        guideline_key="esc_pad_2024",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.A,
        category=RecommendationCategory.PHARMACOTHERAPY,
        urgency=Urgency.URGENT,
        rationale="ACEi/ARB preferred; avoid excessive lowering in CLI",
    ))

    if diabetes:
        rec_set.add(guideline_recommendation(
            action="SGLT2 inhibitor for CV and limb protection in diabetes with PAD",
            guideline_key="esc_pad_2024",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.A,
            category=RecommendationCategory.PHARMACOTHERAPY,
            urgency=Urgency.URGENT,
            rationale="SGLT2i reduce MACE and may reduce limb events",
        ))

    # Consider rivaroxaban + aspirin for high risk
    if concomitant_cad or (abi is not None and abi < 0.9):
        rec_set.add(guideline_recommendation(
            action="Consider rivaroxaban 2.5mg BID + aspirin for high-risk PAD",
            guideline_key="esc_pad_2024",
            evidence_class=EvidenceClass.IIA,
            evidence_level=EvidenceLevel.A,
            category=RecommendationCategory.PHARMACOTHERAPY,
            urgency=Urgency.ROUTINE,
            rationale="COMPASS trial showed MACE and MALE reduction",
            conditions=["Low bleeding risk", "No oral anticoagulation indication"],
        ))

    # CLAUDICATION - Exercise and symptom management
    if fontaine_stage in [PADFontaineStage.IIA, PADFontaineStage.IIB]:
        rec_set.add(guideline_recommendation(
            action="Supervised exercise therapy (SET) is first-line treatment for claudication",
            guideline_key="esc_pad_2024",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.A,
            category=RecommendationCategory.LIFESTYLE,
            urgency=Urgency.ROUTINE,
            rationale="SET improves walking distance by 100-200% over 3-6 months",
        ))

        rec_set.add(guideline_recommendation(
            action="Home-based exercise if SET not available",
            guideline_key="esc_pad_2024",
            evidence_class=EvidenceClass.IIA,
            evidence_level=EvidenceLevel.A,
            category=RecommendationCategory.LIFESTYLE,
            urgency=Urgency.ROUTINE,
        ))

        rec_set.add(guideline_recommendation(
            action="Revascularization for lifestyle-limiting claudication despite exercise therapy",
            guideline_key="esc_pad_2024",
            evidence_class=EvidenceClass.IIA,
            evidence_level=EvidenceLevel.A,
            category=RecommendationCategory.PROCEDURE,
            urgency=Urgency.ROUTINE,
            conditions=["Failed exercise therapy", "Favorable anatomy"],
        ))

    return rec_set


def get_aaa_management(
    diameter_cm: float,
    size_category: AAASize,
    male: bool = True,
    symptomatic: bool = False,
    fit_for_surgery: bool = True,
) -> RecommendationSet:
    """
    Get AAA management recommendations.

    ESC 2024 Aortic Guidelines.

    Args:
        diameter_cm: AAA diameter in cm
        size_category: AAA size category
        male: Male patient
        symptomatic: Symptomatic AAA
        fit_for_surgery: Fit for surgical/endovascular repair

    Returns:
        RecommendationSet with management recommendations
    """
    rec_set = RecommendationSet(
        title="AAA Management Recommendations",
        description=f"ESC 2024 Aortic Guidelines - {diameter_cm} cm AAA",
        primary_guideline="ESC Aortic 2024",
    )

    repair_threshold = 5.5 if male else 5.0

    # SYMPTOMATIC - Always urgent
    if symptomatic:
        rec_set.add(guideline_recommendation(
            action="Emergency repair for symptomatic AAA",
            guideline_key="esc_aortic_2024",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.PROCEDURE,
            urgency=Urgency.EMERGENT,
            rationale="Symptomatic AAA indicates impending rupture",
        ))
        return rec_set

    # CV RISK MODIFICATION - All patients
    rec_set.add(guideline_recommendation(
        action="Smoking cessation - reduces growth rate and rupture risk",
        guideline_key="esc_aortic_2024",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.B,
        category=RecommendationCategory.LIFESTYLE,
        urgency=Urgency.URGENT,
    ))

    rec_set.add(guideline_recommendation(
        action="Statin therapy for all AAA patients",
        guideline_key="esc_aortic_2024",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.B,
        category=RecommendationCategory.PHARMACOTHERAPY,
        urgency=Urgency.ROUTINE,
        rationale="Statins may reduce growth rate and improve perioperative outcomes",
    ))

    rec_set.add(guideline_recommendation(
        action="Blood pressure control (avoid very high BP)",
        guideline_key="esc_aortic_2024",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.C,
        category=RecommendationCategory.PHARMACOTHERAPY,
        urgency=Urgency.ROUTINE,
    ))

    # SIZE-BASED MANAGEMENT
    if diameter_cm >= repair_threshold or size_category in [AAASize.LARGE, AAASize.VERY_LARGE]:
        rec_set.add(guideline_recommendation(
            action=f"Elective AAA repair recommended (diameter >{repair_threshold} cm)",
            guideline_key="esc_aortic_2024",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.A,
            category=RecommendationCategory.PROCEDURE,
            urgency=Urgency.SOON,
            rationale="Rupture risk exceeds procedural risk at this size",
        ))

        if fit_for_surgery:
            rec_set.add(guideline_recommendation(
                action="EVAR preferred if anatomy suitable; otherwise open repair",
                guideline_key="esc_aortic_2024",
                evidence_class=EvidenceClass.I,
                evidence_level=EvidenceLevel.A,
                category=RecommendationCategory.PROCEDURE,
                urgency=Urgency.SOON,
                rationale="EVAR has lower perioperative mortality but requires lifelong surveillance",
            ))
        else:
            rec_set.add(guideline_recommendation(
                action="Consider EVAR even if unfit for open surgery if anatomy suitable",
                guideline_key="esc_aortic_2024",
                evidence_class=EvidenceClass.IIA,
                evidence_level=EvidenceLevel.B,
                category=RecommendationCategory.PROCEDURE,
                urgency=Urgency.ROUTINE,
            ))

    elif size_category == AAASize.MEDIUM:
        rec_set.add(guideline_recommendation(
            action="Surveillance imaging every 6-12 months",
            guideline_key="esc_aortic_2024",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.MONITORING,
            urgency=Urgency.ROUTINE,
        ))

        rec_set.add(guideline_recommendation(
            action="Consider repair if rapid growth (>1 cm/year)",
            guideline_key="esc_aortic_2024",
            evidence_class=EvidenceClass.IIA,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.PROCEDURE,
            urgency=Urgency.ROUTINE,
        ))

    else:  # SMALL
        rec_set.add(guideline_recommendation(
            action="Surveillance imaging every 1-3 years based on size",
            guideline_key="esc_aortic_2024",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.A,
            category=RecommendationCategory.MONITORING,
            urgency=Urgency.ROUTINE,
            rationale="Most small AAAs grow slowly; annual rupture risk <1%",
        ))

    return rec_set


def get_carotid_management(
    stenosis_percent: int,
    symptomatic: bool = False,
    symptoms_within_14_days: bool = False,
    fit_for_intervention: bool = True,
) -> RecommendationSet:
    """
    Get carotid stenosis management recommendations.

    ESC 2024 Guidelines.

    Args:
        stenosis_percent: Degree of carotid stenosis (%)
        symptomatic: TIA/stroke referable to carotid territory
        symptoms_within_14_days: Recent symptoms
        fit_for_intervention: Fit for CEA/CAS

    Returns:
        RecommendationSet with management recommendations
    """
    rec_set = RecommendationSet(
        title="Carotid Stenosis Management",
        description=f"ESC 2024 Guidelines - {stenosis_percent}% stenosis",
        primary_guideline="ESC PAD 2024",
    )

    # MEDICAL THERAPY - All patients
    rec_set.add(guideline_recommendation(
        action="Intensive medical therapy: antiplatelet, statin, BP control, smoking cessation",
        guideline_key="esc_pad_2024",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.A,
        category=RecommendationCategory.PHARMACOTHERAPY,
        urgency=Urgency.URGENT,
    ))

    # SYMPTOMATIC CAROTID STENOSIS
    if symptomatic and stenosis_percent >= 50:
        if symptoms_within_14_days and fit_for_intervention:
            rec_set.add(guideline_recommendation(
                action="Urgent carotid revascularization (CEA or CAS) within 14 days of symptoms",
                guideline_key="esc_pad_2024",
                evidence_class=EvidenceClass.I,
                evidence_level=EvidenceLevel.A,
                category=RecommendationCategory.PROCEDURE,
                urgency=Urgency.URGENT,
                rationale="Benefit greatest when performed within 2 weeks of symptoms",
            ))

            rec_set.add(guideline_recommendation(
                action="CEA preferred over CAS in most patients; CAS reasonable alternative",
                guideline_key="esc_pad_2024",
                evidence_class=EvidenceClass.I,
                evidence_level=EvidenceLevel.A,
                category=RecommendationCategory.PROCEDURE,
                urgency=Urgency.URGENT,
            ))
        elif fit_for_intervention:
            rec_set.add(guideline_recommendation(
                action="Carotid revascularization recommended for symptomatic 50-99% stenosis",
                guideline_key="esc_pad_2024",
                evidence_class=EvidenceClass.I,
                evidence_level=EvidenceLevel.A,
                category=RecommendationCategory.PROCEDURE,
                urgency=Urgency.SOON,
            ))

    # ASYMPTOMATIC CAROTID STENOSIS
    elif not symptomatic and stenosis_percent >= 60:
        rec_set.add(guideline_recommendation(
            action="Revascularization may be considered for asymptomatic 60-99% stenosis in selected patients",
            guideline_key="esc_pad_2024",
            evidence_class=EvidenceClass.IIB,
            evidence_level=EvidenceLevel.A,
            category=RecommendationCategory.PROCEDURE,
            urgency=Urgency.ROUTINE,
            conditions=[
                "High stroke risk features (silent infarcts, progression, contralateral occlusion)",
                "Low procedural risk (<3% stroke/death)",
                "Life expectancy >5 years",
            ],
        ))

        rec_set.add(guideline_recommendation(
            action="Medical therapy alone is acceptable for most asymptomatic stenosis",
            guideline_key="esc_pad_2024",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.A,
            category=RecommendationCategory.PHARMACOTHERAPY,
            urgency=Urgency.ROUTINE,
            rationale="Modern medical therapy has reduced stroke risk in asymptomatic stenosis",
        ))

    else:  # <50% symptomatic or <60% asymptomatic
        rec_set.add(guideline_recommendation(
            action="Medical therapy; revascularization not indicated",
            guideline_key="esc_pad_2024",
            evidence_class=EvidenceClass.III,
            evidence_level=EvidenceLevel.A,
            category=RecommendationCategory.PHARMACOTHERAPY,
            urgency=Urgency.ROUTINE,
        ))

    return rec_set
