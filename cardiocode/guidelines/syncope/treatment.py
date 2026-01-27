"""
Syncope Treatment (ESC 2018).

Management recommendations for different syncope etiologies.
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

from cardiocode.guidelines.syncope.diagnosis import SyncopeType, SyncopeRisk


def get_syncope_management(
    syncope_type: SyncopeType,
    risk_level: SyncopeRisk,
    recurrent: bool = False,
    injury_from_syncope: bool = False,
) -> RecommendationSet:
    """
    Get syncope management recommendations.

    ESC 2018 Syncope Guidelines.

    Args:
        syncope_type: Classified syncope type
        risk_level: Risk stratification result
        recurrent: Recurrent episodes
        injury_from_syncope: History of injury from syncope

    Returns:
        RecommendationSet with management recommendations
    """
    rec_set = RecommendationSet(
        title="Syncope Management",
        description=f"ESC 2018 Syncope Guidelines - {syncope_type.value}",
        primary_guideline="ESC Syncope 2018",
    )

    # HIGH RISK - Cardiac workup
    if risk_level == SyncopeRisk.HIGH:
        rec_set.add(guideline_recommendation(
            action="Admission for telemetry monitoring and urgent cardiac evaluation",
            guideline_key="esc_syncope_2018",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.MONITORING,
            urgency=Urgency.URGENT,
            rationale="High-risk features warrant inpatient evaluation",
        ))

        rec_set.add(guideline_recommendation(
            action="Echocardiography to assess structural heart disease",
            guideline_key="esc_syncope_2018",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.DIAGNOSTIC,
            urgency=Urgency.URGENT,
        ))

    # TYPE-SPECIFIC MANAGEMENT
    if syncope_type == SyncopeType.CARDIAC_ARRHYTHMIC:
        rec_set.add(guideline_recommendation(
            action="Identify and treat underlying arrhythmia",
            guideline_key="esc_syncope_2018",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.DIAGNOSTIC,
            urgency=Urgency.URGENT,
        ))

        rec_set.add(guideline_recommendation(
            action="Consider ICD for documented VT/VF or high SCD risk",
            guideline_key="esc_syncope_2018",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.DEVICE,
            urgency=Urgency.URGENT,
        ))

        rec_set.add(guideline_recommendation(
            action="Pacemaker for documented symptomatic bradycardia",
            guideline_key="esc_syncope_2018",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.DEVICE,
            urgency=Urgency.URGENT,
        ))

    elif syncope_type == SyncopeType.CARDIAC_STRUCTURAL:
        rec_set.add(guideline_recommendation(
            action="Treat underlying structural heart disease",
            guideline_key="esc_syncope_2018",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.PROCEDURE,
            urgency=Urgency.URGENT,
            rationale="E.g., aortic valve replacement for severe AS with syncope",
        ))

    elif syncope_type in [SyncopeType.REFLEX_VASOVAGAL, SyncopeType.REFLEX_SITUATIONAL]:
        rec_set = get_reflex_syncope_treatment(recurrent, injury_from_syncope)

    elif syncope_type == SyncopeType.ORTHOSTATIC_HYPOTENSION:
        rec_set.add(guideline_recommendation(
            action="Review and reduce/discontinue hypotensive medications if possible",
            guideline_key="esc_syncope_2018",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.PHARMACOTHERAPY,
            urgency=Urgency.ROUTINE,
        ))

        rec_set.add(guideline_recommendation(
            action="Non-pharmacological measures: adequate hydration (2-3L/day), salt intake (10g/day if no HTN), compression stockings, physical countermaneuvers",
            guideline_key="esc_syncope_2018",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.LIFESTYLE,
            urgency=Urgency.ROUTINE,
        ))

        rec_set.add(guideline_recommendation(
            action="Sleep with head elevated (10-20 degrees)",
            guideline_key="esc_syncope_2018",
            evidence_class=EvidenceClass.IIA,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.LIFESTYLE,
            urgency=Urgency.ROUTINE,
        ))

        rec_set.add(guideline_recommendation(
            action="Consider midodrine if non-pharmacological measures insufficient",
            guideline_key="esc_syncope_2018",
            evidence_class=EvidenceClass.IIA,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PHARMACOTHERAPY,
            urgency=Urgency.ROUTINE,
            contraindications=["Supine hypertension", "Urinary retention", "Heart failure"],
        ))

        rec_set.add(guideline_recommendation(
            action="Consider fludrocortisone if volume expansion needed",
            guideline_key="esc_syncope_2018",
            evidence_class=EvidenceClass.IIB,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.PHARMACOTHERAPY,
            urgency=Urgency.ROUTINE,
            contraindications=["Heart failure", "Hypertension"],
        ))

    elif syncope_type == SyncopeType.REFLEX_CAROTID_SINUS:
        rec_set.add(guideline_recommendation(
            action="Pacemaker for cardioinhibitory or mixed carotid sinus syndrome with recurrent syncope",
            guideline_key="esc_syncope_2018",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.DEVICE,
            urgency=Urgency.ROUTINE,
            rationale="DDD pacing reduces syncope recurrence by 90%",
        ))

    elif syncope_type == SyncopeType.UNEXPLAINED:
        if recurrent:
            rec_set.add(guideline_recommendation(
                action="Implantable loop recorder (ILR) for recurrent unexplained syncope",
                guideline_key="esc_syncope_2018",
                evidence_class=EvidenceClass.I,
                evidence_level=EvidenceLevel.A,
                category=RecommendationCategory.DIAGNOSTIC,
                urgency=Urgency.ROUTINE,
                rationale="ILR provides diagnosis in 35-50% of cases",
            ))
        else:
            rec_set.add(guideline_recommendation(
                action="Consider ILR early if single unexplained syncope with high-risk features",
                guideline_key="esc_syncope_2018",
                evidence_class=EvidenceClass.IIA,
                evidence_level=EvidenceLevel.B,
                category=RecommendationCategory.DIAGNOSTIC,
                urgency=Urgency.ROUTINE,
            ))

    # Driving advice for all
    rec_set.add(guideline_recommendation(
        action="Provide driving advice per local regulations",
        guideline_key="esc_syncope_2018",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.C,
        category=RecommendationCategory.LIFESTYLE,
        urgency=Urgency.ROUTINE,
        rationale="Syncope of unknown cause or cardiac cause typically requires driving restriction",
    ))

    return rec_set


def get_reflex_syncope_treatment(
    recurrent: bool = False,
    injury_from_syncope: bool = False,
    prodrome_sufficient: bool = True,
) -> RecommendationSet:
    """
    Get treatment recommendations for reflex (vasovagal) syncope.

    ESC 2018 Syncope Guidelines.

    Args:
        recurrent: Recurrent episodes
        injury_from_syncope: History of injury
        prodrome_sufficient: Adequate warning symptoms

    Returns:
        RecommendationSet with treatment recommendations
    """
    rec_set = RecommendationSet(
        title="Reflex Syncope Management",
        description="ESC 2018 Syncope Guidelines - Vasovagal/Reflex",
        primary_guideline="ESC Syncope 2018",
    )

    # Education and reassurance - ALL PATIENTS
    rec_set.add(guideline_recommendation(
        action="Education and reassurance: explain benign nature, triggers, and warning symptoms",
        guideline_key="esc_syncope_2018",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.B,
        category=RecommendationCategory.LIFESTYLE,
        urgency=Urgency.ROUTINE,
        rationale="Patient education alone reduces syncope recurrence",
    ))

    rec_set.add(guideline_recommendation(
        action="Trigger avoidance: avoid prolonged standing, hot environments, dehydration",
        guideline_key="esc_syncope_2018",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.C,
        category=RecommendationCategory.LIFESTYLE,
        urgency=Urgency.ROUTINE,
    ))

    rec_set.add(guideline_recommendation(
        action="Physical counterpressure maneuvers: leg crossing, hand grip, arm tensing when prodrome occurs",
        guideline_key="esc_syncope_2018",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.B,
        category=RecommendationCategory.LIFESTYLE,
        urgency=Urgency.ROUTINE,
        rationale="Can abort syncope in 30-50% if applied during prodrome",
    ))

    rec_set.add(guideline_recommendation(
        action="Adequate fluid intake (2-3L/day) and moderate salt intake",
        guideline_key="esc_syncope_2018",
        evidence_class=EvidenceClass.IIA,
        evidence_level=EvidenceLevel.C,
        category=RecommendationCategory.LIFESTYLE,
        urgency=Urgency.ROUTINE,
    ))

    # For recurrent or severe cases
    if recurrent or injury_from_syncope:
        rec_set.add(guideline_recommendation(
            action="Tilt training (repeated tilt table sessions) may be considered",
            guideline_key="esc_syncope_2018",
            evidence_class=EvidenceClass.IIB,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.LIFESTYLE,
            urgency=Urgency.ROUTINE,
            rationale="May reduce recurrence but evidence limited; compliance is challenging",
        ))

        rec_set.add(guideline_recommendation(
            action="Midodrine may be considered for refractory cases",
            guideline_key="esc_syncope_2018",
            evidence_class=EvidenceClass.IIB,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PHARMACOTHERAPY,
            urgency=Urgency.ROUTINE,
            rationale="Some evidence for short-term benefit",
        ))

    # Pacing for specific subgroup
    if recurrent and not prodrome_sufficient:
        rec_set.add(guideline_recommendation(
            action="Pacemaker may be considered for recurrent unpredictable syncope with documented asystole",
            guideline_key="esc_syncope_2018",
            evidence_class=EvidenceClass.IIA,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.DEVICE,
            urgency=Urgency.ROUTINE,
            conditions=[
                "Age >40 years",
                "Recurrent, unpredictable syncope",
                "Documented asystole >3 seconds on ILR",
                "No or very short prodrome",
            ],
        ))

    # NOT recommended
    rec_set.add(guideline_recommendation(
        action="Beta-blockers are NOT recommended for vasovagal syncope",
        guideline_key="esc_syncope_2018",
        evidence_class=EvidenceClass.III,
        evidence_level=EvidenceLevel.A,
        category=RecommendationCategory.CONTRAINDICATION,
        urgency=Urgency.ROUTINE,
        rationale="Multiple RCTs show no benefit over placebo",
    ))

    return rec_set
