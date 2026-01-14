"""
ICD Indications - ESC 2022 VA/SCD Guidelines.

Comprehensive ICD indication assessment beyond what's in HF guideline:
- Primary prevention across cardiomyopathies
- Secondary prevention
- Channelopathies
- Special populations
"""

from __future__ import annotations
from typing import Optional, List, TYPE_CHECKING
from dataclasses import dataclass, field
from enum import Enum

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


class ICDIndicationType(Enum):
    """Type of ICD indication."""
    PRIMARY_PREVENTION = "primary"
    SECONDARY_PREVENTION = "secondary"
    NOT_INDICATED = "not_indicated"
    CONTRAINDICATED = "contraindicated"


@dataclass
class ICDIndication:
    """Result of ICD indication assessment."""
    indication_type: ICDIndicationType
    indicated: bool
    evidence_class: Optional[EvidenceClass] = None
    evidence_level: Optional[EvidenceLevel] = None
    rationale: str = ""
    conditions: List[str] = field(default_factory=list)
    contraindications: List[str] = field(default_factory=list)
    alternatives: List[str] = field(default_factory=list)
    recommendation: Optional[Recommendation] = None


def assess_secondary_prevention_icd(
    prior_vf: bool = False,
    prior_sustained_vt: bool = False,
    hemodynamically_unstable_vt: bool = False,
    reversible_cause_identified: bool = False,
    reversible_cause_details: Optional[str] = None,
    expected_survival_1yr: bool = True,
    lvef: Optional[float] = None,
) -> ICDIndication:
    """
    Assess ICD indication for secondary prevention.
    
    Per ESC 2022 VA/SCD Guidelines Section 8.1.
    
    Class I indications:
    - Survivors of VF or hemodynamically unstable VT without reversible cause
    - Expected survival > 1 year with good functional status
    
    Class IIa:
    - Sustained VT in presence of structural heart disease
    
    Args:
        prior_vf: History of ventricular fibrillation
        prior_sustained_vt: History of sustained VT
        hemodynamically_unstable_vt: VT with hemodynamic compromise
        reversible_cause_identified: Reversible cause found (electrolyte, ischemia, drug)
        reversible_cause_details: Description of reversible cause
        expected_survival_1yr: Expected to survive > 1 year
        lvef: LV ejection fraction
    
    Returns:
        ICDIndication
    """
    contraindications = []
    
    # Check contraindications
    if not expected_survival_1yr:
        contraindications.append("Life expectancy < 1 year")
    
    if reversible_cause_identified and reversible_cause_details:
        contraindications.append(f"Reversible cause: {reversible_cause_details}")
    
    # No arrhythmia history
    if not prior_vf and not prior_sustained_vt:
        return ICDIndication(
            indication_type=ICDIndicationType.NOT_INDICATED,
            indicated=False,
            rationale="No prior VF or sustained VT - secondary prevention not applicable",
        )
    
    # VF survivor
    if prior_vf:
        if reversible_cause_identified and expected_survival_1yr:
            return ICDIndication(
                indication_type=ICDIndicationType.NOT_INDICATED,
                indicated=False,
                rationale="VF with reversible cause - ICD not indicated if cause corrected",
                contraindications=contraindications,
                alternatives=["Correct underlying cause", "ICD if recurrence despite correction"],
            )
        
        if not expected_survival_1yr:
            return ICDIndication(
                indication_type=ICDIndicationType.NOT_INDICATED,
                indicated=False,
                rationale="Life expectancy < 1 year - ICD not indicated",
                contraindications=contraindications,
            )
        
        return ICDIndication(
            indication_type=ICDIndicationType.SECONDARY_PREVENTION,
            indicated=True,
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.A,
            rationale="VF survivor without reversible cause",
            recommendation=guideline_recommendation(
                action="ICD implantation for secondary prevention of SCD",
                guideline_key="esc_va_scd_2022",
                evidence_class=EvidenceClass.I,
                evidence_level=EvidenceLevel.A,
                category=RecommendationCategory.DEVICE,
                urgency=Urgency.URGENT,
                section="8.1",
                rationale="VF survivor - ICD reduces mortality",
                studies=["AVID", "CIDS", "CASH"],
            ),
        )
    
    # Sustained VT
    if prior_sustained_vt:
        if hemodynamically_unstable_vt:
            return ICDIndication(
                indication_type=ICDIndicationType.SECONDARY_PREVENTION,
                indicated=True,
                evidence_class=EvidenceClass.I,
                evidence_level=EvidenceLevel.A,
                rationale="Hemodynamically unstable sustained VT without reversible cause",
                recommendation=guideline_recommendation(
                    action="ICD implantation for secondary prevention",
                    guideline_key="esc_va_scd_2022",
                    evidence_class=EvidenceClass.I,
                    evidence_level=EvidenceLevel.A,
                    category=RecommendationCategory.DEVICE,
                    urgency=Urgency.URGENT,
                    section="8.1",
                    rationale="Hemodynamically unstable VT",
                    studies=["AVID", "CIDS", "CASH"],
                ),
            )
        else:
            # Hemodynamically tolerated VT with structural heart disease
            return ICDIndication(
                indication_type=ICDIndicationType.SECONDARY_PREVENTION,
                indicated=True,
                evidence_class=EvidenceClass.IIA,
                evidence_level=EvidenceLevel.B,
                rationale="Sustained VT with structural heart disease",
                recommendation=guideline_recommendation(
                    action="ICD should be considered for secondary prevention",
                    guideline_key="esc_va_scd_2022",
                    evidence_class=EvidenceClass.IIA,
                    evidence_level=EvidenceLevel.B,
                    category=RecommendationCategory.DEVICE,
                    urgency=Urgency.SOON,
                    section="8.1",
                    rationale="Sustained VT may degenerate to VF",
                ),
                conditions=["Structural heart disease present"],
            )
    
    return ICDIndication(
        indication_type=ICDIndicationType.NOT_INDICATED,
        indicated=False,
        rationale="Does not meet secondary prevention criteria",
    )


def assess_channelopathy_icd(
    condition: str,  # "long_qt", "brugada", "cpvt", "short_qt"
    prior_cardiac_arrest: bool = False,
    syncope: bool = False,
    documented_polymorphic_vt: bool = False,
    on_beta_blocker: bool = False,
    high_risk_genotype: bool = False,
    qtc: Optional[int] = None,  # ms
    spontaneous_type1_brugada: bool = False,
) -> ICDIndication:
    """
    ICD indication assessment for inherited channelopathies.
    
    Per ESC 2022 VA/SCD Guidelines Section 9.
    
    Args:
        condition: Type of channelopathy
        prior_cardiac_arrest: Prior aborted SCD
        syncope: Arrhythmic syncope
        documented_polymorphic_vt: Documented polymorphic VT
        on_beta_blocker: Currently on beta-blocker
        high_risk_genotype: High-risk genetic variant
        qtc: QTc interval in ms
        spontaneous_type1_brugada: Spontaneous type 1 Brugada pattern
    
    Returns:
        ICDIndication
    """
    condition = condition.lower().replace(" ", "_")
    
    # Secondary prevention - all channelopathies
    if prior_cardiac_arrest:
        return ICDIndication(
            indication_type=ICDIndicationType.SECONDARY_PREVENTION,
            indicated=True,
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            rationale=f"Cardiac arrest survivor with {condition}",
            recommendation=guideline_recommendation(
                action="ICD for secondary prevention",
                guideline_key="esc_va_scd_2022",
                evidence_class=EvidenceClass.I,
                evidence_level=EvidenceLevel.B,
                category=RecommendationCategory.DEVICE,
                urgency=Urgency.URGENT,
                section="9",
                rationale="Channelopathy with prior cardiac arrest",
            ),
        )
    
    # LONG QT SYNDROME
    if condition in ["long_qt", "lqts", "long_qt_syndrome"]:
        if syncope and on_beta_blocker:
            return ICDIndication(
                indication_type=ICDIndicationType.PRIMARY_PREVENTION,
                indicated=True,
                evidence_class=EvidenceClass.I,
                evidence_level=EvidenceLevel.B,
                rationale="LQTS with recurrent syncope despite beta-blocker",
                recommendation=guideline_recommendation(
                    action="ICD recommended for LQTS with syncope despite beta-blocker therapy",
                    guideline_key="esc_va_scd_2022",
                    evidence_class=EvidenceClass.I,
                    evidence_level=EvidenceLevel.B,
                    category=RecommendationCategory.DEVICE,
                    urgency=Urgency.SOON,
                    section="9.1",
                    rationale="High risk of SCD despite medical therapy",
                ),
            )
        elif syncope and not on_beta_blocker:
            return ICDIndication(
                indication_type=ICDIndicationType.NOT_INDICATED,
                indicated=False,
                rationale="LQTS with syncope - first-line is beta-blocker therapy",
                alternatives=["Start beta-blocker (nadolol/propranolol preferred)", "ICD if syncope recurs on beta-blocker"],
            )
        elif qtc and qtc > 500:
            return ICDIndication(
                indication_type=ICDIndicationType.PRIMARY_PREVENTION,
                indicated=True,
                evidence_class=EvidenceClass.IIB,
                evidence_level=EvidenceLevel.C,
                rationale=f"LQTS with QTc {qtc}ms > 500ms",
                recommendation=guideline_recommendation(
                    action="ICD may be considered in LQTS with QTc > 500ms despite therapy",
                    guideline_key="esc_va_scd_2022",
                    evidence_class=EvidenceClass.IIB,
                    evidence_level=EvidenceLevel.C,
                    category=RecommendationCategory.DEVICE,
                    urgency=Urgency.ROUTINE,
                    section="9.1",
                    rationale="Very prolonged QTc is high-risk marker",
                ),
                conditions=["On maximally tolerated beta-blocker", "Consider left cardiac sympathetic denervation first"],
            )
        else:
            return ICDIndication(
                indication_type=ICDIndicationType.NOT_INDICATED,
                indicated=False,
                rationale="LQTS without high-risk features - beta-blocker is primary therapy",
                alternatives=["Beta-blocker therapy (Class I)", "Avoid QT-prolonging drugs"],
            )
    
    # BRUGADA SYNDROME
    if condition in ["brugada", "brugada_syndrome"]:
        if syncope and spontaneous_type1_brugada:
            return ICDIndication(
                indication_type=ICDIndicationType.PRIMARY_PREVENTION,
                indicated=True,
                evidence_class=EvidenceClass.IIA,
                evidence_level=EvidenceLevel.B,
                rationale="Brugada syndrome with syncope and spontaneous type 1 pattern",
                recommendation=guideline_recommendation(
                    action="ICD should be considered for Brugada with syncope and spontaneous type 1 ECG",
                    guideline_key="esc_va_scd_2022",
                    evidence_class=EvidenceClass.IIA,
                    evidence_level=EvidenceLevel.B,
                    category=RecommendationCategory.DEVICE,
                    urgency=Urgency.SOON,
                    section="9.2",
                    rationale="Combination of symptoms and diagnostic ECG indicates high risk",
                ),
            )
        elif spontaneous_type1_brugada and documented_polymorphic_vt:
            return ICDIndication(
                indication_type=ICDIndicationType.PRIMARY_PREVENTION,
                indicated=True,
                evidence_class=EvidenceClass.IIA,
                evidence_level=EvidenceLevel.B,
                rationale="Brugada with spontaneous type 1 and documented VT/VF",
                recommendation=guideline_recommendation(
                    action="ICD should be considered",
                    guideline_key="esc_va_scd_2022",
                    evidence_class=EvidenceClass.IIA,
                    evidence_level=EvidenceLevel.B,
                    category=RecommendationCategory.DEVICE,
                    urgency=Urgency.SOON,
                    section="9.2",
                ),
            )
        elif spontaneous_type1_brugada:
            return ICDIndication(
                indication_type=ICDIndicationType.NOT_INDICATED,
                indicated=False,
                evidence_class=EvidenceClass.IIB,
                rationale="Asymptomatic Brugada - ICD benefit uncertain",
                alternatives=["Avoid triggers (fever, drugs)", "Consider EPS in selected cases", "Quinidine in some patients"],
            )
        else:
            return ICDIndication(
                indication_type=ICDIndicationType.NOT_INDICATED,
                indicated=False,
                rationale="Drug-induced Brugada pattern without spontaneous type 1 - low risk",
            )
    
    # CPVT
    if condition in ["cpvt", "catecholaminergic_polymorphic_vt"]:
        if syncope or documented_polymorphic_vt:
            if not on_beta_blocker:
                return ICDIndication(
                    indication_type=ICDIndicationType.NOT_INDICATED,
                    indicated=False,
                    rationale="CPVT - first line is beta-blocker +/- flecainide",
                    alternatives=["Maximally tolerated beta-blocker", "Add flecainide", "Consider left cardiac sympathetic denervation"],
                )
            else:
                return ICDIndication(
                    indication_type=ICDIndicationType.PRIMARY_PREVENTION,
                    indicated=True,
                    evidence_class=EvidenceClass.I,
                    evidence_level=EvidenceLevel.B,
                    rationale="CPVT with syncope/VT despite beta-blocker",
                    recommendation=guideline_recommendation(
                        action="ICD + beta-blocker in CPVT with recurrent syncope/VT on therapy",
                        guideline_key="esc_va_scd_2022",
                        evidence_class=EvidenceClass.I,
                        evidence_level=EvidenceLevel.B,
                        category=RecommendationCategory.DEVICE,
                        urgency=Urgency.SOON,
                        section="9.3",
                        rationale="High arrhythmic risk despite medical therapy",
                        conditions=["Continue beta-blocker", "Program ICD to minimize inappropriate shocks"],
                    ),
                )
        else:
            return ICDIndication(
                indication_type=ICDIndicationType.NOT_INDICATED,
                indicated=False,
                rationale="CPVT without symptoms - beta-blocker primary therapy",
                alternatives=["Beta-blocker (nadolol preferred)", "Flecainide if breakthrough", "Exercise restriction"],
            )
    
    # SHORT QT
    if condition in ["short_qt", "sqts", "short_qt_syndrome"]:
        if syncope or documented_polymorphic_vt:
            return ICDIndication(
                indication_type=ICDIndicationType.PRIMARY_PREVENTION,
                indicated=True,
                evidence_class=EvidenceClass.IIA,
                evidence_level=EvidenceLevel.C,
                rationale="Short QT syndrome with symptoms",
                recommendation=guideline_recommendation(
                    action="ICD should be considered for SQTS with syncope or documented VT/VF",
                    guideline_key="esc_va_scd_2022",
                    evidence_class=EvidenceClass.IIA,
                    evidence_level=EvidenceLevel.C,
                    category=RecommendationCategory.DEVICE,
                    urgency=Urgency.SOON,
                    section="9.4",
                    rationale="Limited data but high arrhythmic risk",
                ),
                conditions=["Consider quinidine as adjunct"],
            )
        else:
            return ICDIndication(
                indication_type=ICDIndicationType.NOT_INDICATED,
                indicated=False,
                rationale="Asymptomatic SQTS - individualized assessment needed",
                alternatives=["Quinidine may normalize QT", "Family screening"],
            )
    
    return ICDIndication(
        indication_type=ICDIndicationType.NOT_INDICATED,
        indicated=False,
        rationale=f"Unknown channelopathy type: {condition}",
    )


def assess_icd_indication(patient: "Patient") -> RecommendationSet:
    """
    Comprehensive ICD indication assessment.
    
    Evaluates all potential ICD indications based on patient's conditions.
    
    Args:
        patient: Patient object
    
    Returns:
        RecommendationSet with ICD recommendations
    """
    rec_set = RecommendationSet(
        title="ICD Indication Assessment",
        description="Per ESC 2022 VA/SCD Guidelines",
        primary_guideline="ESC VA/SCD 2022",
    )
    
    # Check for secondary prevention indication first
    has_vf = patient.has_diagnosis("ventricular_fibrillation") or patient.has_diagnosis("cardiac_arrest")
    has_vt = patient.has_diagnosis("ventricular_tachycardia")
    
    if has_vf or has_vt:
        indication = assess_secondary_prevention_icd(
            prior_vf=has_vf,
            prior_sustained_vt=has_vt,
            hemodynamically_unstable_vt=True,  # Assume unstable if VT documented
            lvef=patient.lvef,
        )
        if indication.recommendation:
            rec_set.add(indication.recommendation)
            return rec_set
    
    # Check for channelopathies
    channelopathies = ["long_qt", "brugada", "cpvt", "short_qt"]
    for channel in channelopathies:
        if patient.has_diagnosis(channel):
            indication = assess_channelopathy_icd(
                condition=channel,
                prior_cardiac_arrest=has_vf,
            )
            if indication.recommendation:
                rec_set.add(indication.recommendation)
            else:
                rec_set.description += f"\n{channel}: {indication.rationale}"
            return rec_set
    
    # Primary prevention based on LVEF
    if patient.lvef is not None and patient.lvef <= 35:
        nyha = patient.nyha_class.value if patient.nyha_class else 2
        
        if nyha in [2, 3]:
            rec_set.add(guideline_recommendation(
                action="ICD for primary prevention of SCD",
                guideline_key="esc_va_scd_2022",
                evidence_class=EvidenceClass.I if patient.has_diagnosis("coronary_artery_disease") else EvidenceClass.IIA,
                evidence_level=EvidenceLevel.A,
                category=RecommendationCategory.DEVICE,
                urgency=Urgency.ROUTINE,
                section="8.2",
                rationale=f"LVEF {patient.lvef}% with NYHA Class {nyha}",
                conditions=["On optimal medical therapy >= 3 months", "Expected survival > 1 year"],
            ))
    
    if rec_set.count == 0:
        rec_set.description = "No ICD indication identified based on current data"
    
    return rec_set
