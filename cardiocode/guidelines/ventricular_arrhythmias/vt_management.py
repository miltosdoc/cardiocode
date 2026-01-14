"""
VT Management - ESC 2022 VA/SCD Guidelines.

Management algorithms for ventricular tachycardia:
- Acute VT management
- Chronic VT management
- Catheter ablation indications
- Antiarrhythmic drug selection
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


class VTType(Enum):
    """Types of ventricular tachycardia."""
    MONOMORPHIC_SUSTAINED = "monomorphic_sustained"      # >30s or requiring intervention
    MONOMORPHIC_NSVT = "monomorphic_nsvt"               # Non-sustained (<30s, self-terminating)
    POLYMORPHIC = "polymorphic"                          # Including TdP
    VF = "ventricular_fibrillation"
    IDIOPATHIC_OUTFLOW = "idiopathic_outflow"           # RVOT/LVOT
    FASCICULAR = "fascicular"                            # Left posterior/anterior fascicle
    BUNDLE_BRANCH_REENTRY = "bundle_branch_reentry"
    ELECTRICAL_STORM = "electrical_storm"                # >=3 VT/VF episodes in 24h


class HemodynamicStatus(Enum):
    """Hemodynamic status during VT."""
    STABLE = "stable"
    UNSTABLE = "unstable"  # Hypotension, chest pain, altered consciousness
    PULSELESS = "pulseless"


@dataclass
class VTManagementPlan:
    """VT management recommendation set."""
    vt_type: VTType
    hemodynamic_status: HemodynamicStatus
    acute_management: List[Recommendation] = field(default_factory=list)
    chronic_management: List[Recommendation] = field(default_factory=list)
    ablation_indicated: bool = False
    ablation_recommendation: Optional[Recommendation] = None
    antiarrhythmic_recommendations: List[Recommendation] = field(default_factory=list)


def manage_acute_vt(
    vt_type: VTType,
    hemodynamic_status: HemodynamicStatus,
    has_structural_heart_disease: bool = False,
    lvef: Optional[float] = None,
    has_icd: bool = False,
    qtc: Optional[int] = None,
) -> VTManagementPlan:
    """
    Acute management of VT.
    
    Per ESC 2022 VA/SCD Guidelines Section 10.
    
    Args:
        vt_type: Type of VT
        hemodynamic_status: Hemodynamic stability
        has_structural_heart_disease: Known structural heart disease
        lvef: LV ejection fraction if known
        has_icd: Patient has ICD
        qtc: QTc interval
    
    Returns:
        VTManagementPlan
    """
    acute_recs = []
    chronic_recs = []
    
    # PULSELESS VT/VF - ACLS
    if hemodynamic_status == HemodynamicStatus.PULSELESS or vt_type == VTType.VF:
        acute_recs.append(guideline_recommendation(
            action="Immediate defibrillation per ACLS protocol",
            guideline_key="esc_va_scd_2022",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PROCEDURE,
            urgency=Urgency.EMERGENT,
            section="10",
            rationale="Pulseless VT/VF requires immediate defibrillation",
        ))
        acute_recs.append(guideline_recommendation(
            action="Amiodarone 300mg IV bolus if VF/pulseless VT refractory to initial shocks",
            guideline_key="esc_va_scd_2022",
            evidence_class=EvidenceClass.IIA,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PHARMACOTHERAPY,
            urgency=Urgency.EMERGENT,
            section="10",
            rationale="Amiodarone improves return of spontaneous circulation",
        ))
        return VTManagementPlan(
            vt_type=vt_type,
            hemodynamic_status=hemodynamic_status,
            acute_management=acute_recs,
        )
    
    # UNSTABLE VT
    if hemodynamic_status == HemodynamicStatus.UNSTABLE:
        acute_recs.append(guideline_recommendation(
            action="Synchronized cardioversion",
            guideline_key="esc_va_scd_2022",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PROCEDURE,
            urgency=Urgency.EMERGENT,
            section="10.1",
            rationale="Hemodynamically unstable VT requires prompt cardioversion",
        ))
        return VTManagementPlan(
            vt_type=vt_type,
            hemodynamic_status=hemodynamic_status,
            acute_management=acute_recs,
        )
    
    # STABLE MONOMORPHIC VT
    if vt_type == VTType.MONOMORPHIC_SUSTAINED and hemodynamic_status == HemodynamicStatus.STABLE:
        # Check for ICD
        if has_icd:
            acute_recs.append(guideline_recommendation(
                action="Consider ICD interrogation and ATP if appropriate",
                guideline_key="esc_va_scd_2022",
                evidence_class=EvidenceClass.IIA,
                evidence_level=EvidenceLevel.C,
                category=RecommendationCategory.DEVICE,
                urgency=Urgency.URGENT,
                section="10.1",
            ))
        
        # Pharmacological termination
        if has_structural_heart_disease or (lvef and lvef < 40):
            acute_recs.append(guideline_recommendation(
                action="Amiodarone 150mg IV over 10 min, then infusion",
                guideline_key="esc_va_scd_2022",
                evidence_class=EvidenceClass.I,
                evidence_level=EvidenceLevel.B,
                category=RecommendationCategory.PHARMACOTHERAPY,
                urgency=Urgency.URGENT,
                section="10.1",
                rationale="Amiodarone safe in structural heart disease",
                contraindications=["Avoid procainamide, flecainide in structural heart disease"],
            ))
        else:
            # No structural heart disease
            acute_recs.append(guideline_recommendation(
                action="Consider procainamide 10mg/kg IV at 50mg/min OR amiodarone",
                guideline_key="esc_va_scd_2022",
                evidence_class=EvidenceClass.IIA,
                evidence_level=EvidenceLevel.B,
                category=RecommendationCategory.PHARMACOTHERAPY,
                urgency=Urgency.URGENT,
                section="10.1",
                rationale="Procainamide effective for stable VT without structural heart disease",
            ))
        
        acute_recs.append(guideline_recommendation(
            action="Synchronized cardioversion if pharmacological conversion fails",
            guideline_key="esc_va_scd_2022",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PROCEDURE,
            urgency=Urgency.URGENT,
            section="10.1",
        ))
    
    # POLYMORPHIC VT
    if vt_type == VTType.POLYMORPHIC:
        if qtc and qtc > 500:
            # Torsades de Pointes
            acute_recs.append(guideline_recommendation(
                action="Magnesium sulfate 2g IV over 10 min",
                guideline_key="esc_va_scd_2022",
                evidence_class=EvidenceClass.I,
                evidence_level=EvidenceLevel.B,
                category=RecommendationCategory.PHARMACOTHERAPY,
                urgency=Urgency.EMERGENT,
                section="10.2",
                rationale="Magnesium for Torsades de Pointes",
            ))
            acute_recs.append(guideline_recommendation(
                action="Stop all QT-prolonging drugs",
                guideline_key="esc_va_scd_2022",
                evidence_class=EvidenceClass.I,
                evidence_level=EvidenceLevel.B,
                category=RecommendationCategory.PHARMACOTHERAPY,
                urgency=Urgency.EMERGENT,
                section="10.2",
            ))
            acute_recs.append(guideline_recommendation(
                action="Correct K+ to > 4.5 mEq/L and Mg2+ > 2 mEq/L",
                guideline_key="esc_va_scd_2022",
                evidence_class=EvidenceClass.I,
                evidence_level=EvidenceLevel.B,
                category=RecommendationCategory.PHARMACOTHERAPY,
                urgency=Urgency.EMERGENT,
                section="10.2",
            ))
            acute_recs.append(guideline_recommendation(
                action="Consider temporary pacing or isoproterenol to increase heart rate if recurrent",
                guideline_key="esc_va_scd_2022",
                evidence_class=EvidenceClass.IIA,
                evidence_level=EvidenceLevel.C,
                category=RecommendationCategory.PROCEDURE,
                urgency=Urgency.URGENT,
                section="10.2",
                rationale="Increasing heart rate shortens QT and prevents TdP",
            ))
        else:
            # Polymorphic VT without QT prolongation - likely ischemia
            acute_recs.append(guideline_recommendation(
                action="Evaluate for acute ischemia - urgent coronary angiography if suspected",
                guideline_key="esc_va_scd_2022",
                evidence_class=EvidenceClass.I,
                evidence_level=EvidenceLevel.B,
                category=RecommendationCategory.DIAGNOSTIC,
                urgency=Urgency.EMERGENT,
                section="10.2",
                rationale="Polymorphic VT without QT prolongation often indicates ischemia",
            ))
            acute_recs.append(guideline_recommendation(
                action="Beta-blocker if ischemia suspected",
                guideline_key="esc_va_scd_2022",
                evidence_class=EvidenceClass.I,
                evidence_level=EvidenceLevel.B,
                category=RecommendationCategory.PHARMACOTHERAPY,
                urgency=Urgency.URGENT,
                section="10.2",
            ))
    
    # ELECTRICAL STORM
    if vt_type == VTType.ELECTRICAL_STORM:
        acute_recs.append(guideline_recommendation(
            action="Amiodarone IV loading + infusion",
            guideline_key="esc_va_scd_2022",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PHARMACOTHERAPY,
            urgency=Urgency.EMERGENT,
            section="10.3",
            rationale="First-line for electrical storm",
        ))
        acute_recs.append(guideline_recommendation(
            action="Beta-blocker (IV esmolol or metoprolol) if not contraindicated",
            guideline_key="esc_va_scd_2022",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PHARMACOTHERAPY,
            urgency=Urgency.EMERGENT,
            section="10.3",
            rationale="Sympathetic activation drives electrical storm",
        ))
        acute_recs.append(guideline_recommendation(
            action="Deep sedation/intubation if refractory",
            guideline_key="esc_va_scd_2022",
            evidence_class=EvidenceClass.IIA,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.PROCEDURE,
            urgency=Urgency.EMERGENT,
            section="10.3",
            rationale="Reduces sympathetic tone",
        ))
        acute_recs.append(guideline_recommendation(
            action="Urgent catheter ablation if refractory to medical therapy",
            guideline_key="esc_va_scd_2022",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PROCEDURE,
            urgency=Urgency.EMERGENT,
            section="10.3",
            rationale="Ablation effective for refractory electrical storm",
        ))
    
    return VTManagementPlan(
        vt_type=vt_type,
        hemodynamic_status=hemodynamic_status,
        acute_management=acute_recs,
        chronic_management=chronic_recs,
    )


def assess_vt_ablation_indication(
    vt_type: VTType,
    has_structural_heart_disease: bool = False,
    lvef: Optional[float] = None,
    has_icd: bool = False,
    icd_shocks: int = 0,
    antiarrhythmic_failed: bool = False,
    antiarrhythmic_intolerant: bool = False,
    electrical_storm: bool = False,
) -> VTManagementPlan:
    """
    Assess indication for VT catheter ablation.
    
    Per ESC 2022 VA/SCD Guidelines Section 11.
    
    Args:
        vt_type: Type of VT
        has_structural_heart_disease: Structural heart disease present
        lvef: LV ejection fraction
        has_icd: Patient has ICD
        icd_shocks: Number of ICD shocks
        antiarrhythmic_failed: Failed antiarrhythmic drugs
        antiarrhythmic_intolerant: Intolerant to antiarrhythmic drugs
        electrical_storm: Electrical storm history
    
    Returns:
        VTManagementPlan with ablation recommendation
    """
    plan = VTManagementPlan(
        vt_type=vt_type,
        hemodynamic_status=HemodynamicStatus.STABLE,
    )
    
    # ELECTRICAL STORM - Class I for ablation
    if electrical_storm or vt_type == VTType.ELECTRICAL_STORM:
        plan.ablation_indicated = True
        plan.ablation_recommendation = guideline_recommendation(
            action="Catheter ablation for electrical storm",
            guideline_key="esc_va_scd_2022",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PROCEDURE,
            urgency=Urgency.URGENT,
            section="11.1",
            rationale="Electrical storm is Class I indication for ablation",
            studies=["VANISH", "SMASH-VT", "VTACH"],
        )
        return plan
    
    # IDIOPATHIC VT (no structural heart disease)
    if vt_type in [VTType.IDIOPATHIC_OUTFLOW, VTType.FASCICULAR]:
        plan.ablation_indicated = True
        plan.ablation_recommendation = guideline_recommendation(
            action="Catheter ablation for idiopathic VT (first-line option)",
            guideline_key="esc_va_scd_2022",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PROCEDURE,
            urgency=Urgency.ROUTINE,
            section="11.2",
            rationale="Idiopathic VT - ablation is curative with >90% success",
            studies=["Multiple observational studies"],
        )
        return plan
    
    # BUNDLE BRANCH REENTRY VT
    if vt_type == VTType.BUNDLE_BRANCH_REENTRY:
        plan.ablation_indicated = True
        plan.ablation_recommendation = guideline_recommendation(
            action="Catheter ablation for bundle branch reentrant VT",
            guideline_key="esc_va_scd_2022",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PROCEDURE,
            urgency=Urgency.SOON,
            section="11.3",
            rationale="BBR-VT has defined substrate amenable to ablation",
        )
        return plan
    
    # VT WITH STRUCTURAL HEART DISEASE
    if has_structural_heart_disease:
        # Recurrent ICD shocks
        if has_icd and icd_shocks >= 1:
            plan.ablation_indicated = True
            if antiarrhythmic_failed or antiarrhythmic_intolerant:
                plan.ablation_recommendation = guideline_recommendation(
                    action="Catheter ablation for recurrent VT with ICD shocks despite/intolerant to antiarrhythmic",
                    guideline_key="esc_va_scd_2022",
                    evidence_class=EvidenceClass.I,
                    evidence_level=EvidenceLevel.B,
                    category=RecommendationCategory.PROCEDURE,
                    urgency=Urgency.SOON,
                    section="11.1",
                    rationale="Recurrent VT with failed/intolerant to AAD",
                    studies=["VANISH"],
                )
            else:
                plan.ablation_recommendation = guideline_recommendation(
                    action="Catheter ablation should be considered for recurrent VT with ICD shocks",
                    guideline_key="esc_va_scd_2022",
                    evidence_class=EvidenceClass.IIA,
                    evidence_level=EvidenceLevel.B,
                    category=RecommendationCategory.PROCEDURE,
                    urgency=Urgency.SOON,
                    section="11.1",
                    rationale="Recurrent VT causing ICD therapy",
                    studies=["SMASH-VT", "VTACH"],
                )
            return plan
        
        # First VT episode - ablation may be considered
        if antiarrhythmic_failed:
            plan.ablation_indicated = True
            plan.ablation_recommendation = guideline_recommendation(
                action="Catheter ablation for VT after failed antiarrhythmic therapy",
                guideline_key="esc_va_scd_2022",
                evidence_class=EvidenceClass.I,
                evidence_level=EvidenceLevel.B,
                category=RecommendationCategory.PROCEDURE,
                urgency=Urgency.SOON,
                section="11.1",
                studies=["VANISH"],
            )
        elif antiarrhythmic_intolerant:
            plan.ablation_indicated = True
            plan.ablation_recommendation = guideline_recommendation(
                action="Catheter ablation as alternative to antiarrhythmic therapy",
                guideline_key="esc_va_scd_2022",
                evidence_class=EvidenceClass.IIA,
                evidence_level=EvidenceLevel.B,
                category=RecommendationCategory.PROCEDURE,
                urgency=Urgency.ROUTINE,
                section="11.1",
            )
        else:
            # First-line option
            plan.ablation_recommendation = guideline_recommendation(
                action="Catheter ablation may be considered as first-line therapy for monomorphic VT",
                guideline_key="esc_va_scd_2022",
                evidence_class=EvidenceClass.IIB,
                evidence_level=EvidenceLevel.B,
                category=RecommendationCategory.PROCEDURE,
                urgency=Urgency.ROUTINE,
                section="11.1",
                rationale="Growing evidence supports early ablation",
            )
    
    return plan


def get_antiarrhythmic_for_vt(
    vt_type: VTType,
    has_structural_heart_disease: bool,
    lvef: Optional[float] = None,
    has_cad: bool = False,
    has_hf: bool = False,
) -> RecommendationSet:
    """
    Get antiarrhythmic drug recommendations for VT prevention.
    
    Per ESC 2022 VA/SCD Guidelines Section 12.
    
    Args:
        vt_type: Type of VT
        has_structural_heart_disease: Structural heart disease
        lvef: LV ejection fraction
        has_cad: Coronary artery disease
        has_hf: Heart failure
    
    Returns:
        RecommendationSet with AAD recommendations
    """
    rec_set = RecommendationSet(
        title="Antiarrhythmic Drug Selection for VT",
        primary_guideline="ESC VA/SCD 2022",
    )
    
    # No structural heart disease
    if not has_structural_heart_disease:
        rec_set.add(guideline_recommendation(
            action="Beta-blocker as first-line therapy for idiopathic VT",
            guideline_key="esc_va_scd_2022",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PHARMACOTHERAPY,
            urgency=Urgency.ROUTINE,
            section="12",
        ))
        if vt_type == VTType.IDIOPATHIC_OUTFLOW:
            rec_set.add(guideline_recommendation(
                action="Verapamil or diltiazem may be used for RVOT VT",
                guideline_key="esc_va_scd_2022",
                evidence_class=EvidenceClass.IIA,
                evidence_level=EvidenceLevel.C,
                category=RecommendationCategory.PHARMACOTHERAPY,
                urgency=Urgency.ROUTINE,
                section="12",
                rationale="Calcium channel blockers effective for some outflow tract VTs",
            ))
        if vt_type == VTType.FASCICULAR:
            rec_set.add(guideline_recommendation(
                action="Verapamil effective for fascicular VT",
                guideline_key="esc_va_scd_2022",
                evidence_class=EvidenceClass.IIA,
                evidence_level=EvidenceLevel.C,
                category=RecommendationCategory.PHARMACOTHERAPY,
                urgency=Urgency.ROUTINE,
                section="12",
            ))
        rec_set.add(guideline_recommendation(
            action="Flecainide or propafenone may be considered if beta-blocker ineffective",
            guideline_key="esc_va_scd_2022",
            evidence_class=EvidenceClass.IIA,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.PHARMACOTHERAPY,
            urgency=Urgency.ROUTINE,
            section="12",
            contraindications=["Contraindicated in structural heart disease"],
        ))
        return rec_set
    
    # Structural heart disease present
    # Beta-blocker
    rec_set.add(guideline_recommendation(
        action="Beta-blocker for VT in structural heart disease",
        guideline_key="esc_va_scd_2022",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.A,
        category=RecommendationCategory.PHARMACOTHERAPY,
        urgency=Urgency.ROUTINE,
        section="12",
        rationale="Reduces VT episodes and ICD shocks, mortality benefit in HF/post-MI",
    ))
    
    # Amiodarone
    rec_set.add(guideline_recommendation(
        action="Amiodarone for recurrent VT in structural heart disease",
        guideline_key="esc_va_scd_2022",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.B,
        category=RecommendationCategory.PHARMACOTHERAPY,
        urgency=Urgency.ROUTINE,
        section="12",
        rationale="Most effective antiarrhythmic for VT in structural heart disease",
        monitoring="Monitor thyroid, liver, pulmonary function",
        conditions=["Add to beta-blocker rather than replacing it"],
    ))
    
    # Sotalol - caution with low EF
    if lvef is None or lvef > 30:
        rec_set.add(guideline_recommendation(
            action="Sotalol may be considered if amiodarone not tolerated",
            guideline_key="esc_va_scd_2022",
            evidence_class=EvidenceClass.IIB,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PHARMACOTHERAPY,
            urgency=Urgency.ROUTINE,
            section="12",
            monitoring="Monitor QTc, renal function",
            contraindications=["Avoid if LVEF < 30%", "Avoid with QTc > 500ms"],
        ))
    
    # Mexiletine - adjunct
    rec_set.add(guideline_recommendation(
        action="Mexiletine may be added to amiodarone for refractory VT",
        guideline_key="esc_va_scd_2022",
        evidence_class=EvidenceClass.IIB,
        evidence_level=EvidenceLevel.C,
        category=RecommendationCategory.PHARMACOTHERAPY,
        urgency=Urgency.ROUTINE,
        section="12",
        rationale="Class IB agent can be combined with class III",
    ))
    
    # Contraindicated drugs
    rec_set.description = """
Note: The following are CONTRAINDICATED in structural heart disease:
- Flecainide (Class IC)
- Propafenone (Class IC)
- Dronedarone in NYHA III-IV HF or recent decompensation
"""
    
    return rec_set


def manage_vt(patient: "Patient", vt_type: VTType = VTType.MONOMORPHIC_SUSTAINED) -> RecommendationSet:
    """
    Comprehensive VT management for a patient.
    
    Args:
        patient: Patient object
        vt_type: Type of VT
    
    Returns:
        RecommendationSet with all VT management recommendations
    """
    rec_set = RecommendationSet(
        title="Ventricular Tachycardia Management",
        description="Per ESC 2022 VA/SCD Guidelines",
        primary_guideline="ESC VA/SCD 2022",
    )
    
    has_shd = patient.has_diagnosis("coronary_artery_disease") or \
              patient.has_diagnosis("cardiomyopathy") or \
              patient.has_diagnosis("heart_failure") or \
              (patient.lvef is not None and patient.lvef < 50)
    
    # Acute management
    acute_plan = manage_acute_vt(
        vt_type=vt_type,
        hemodynamic_status=HemodynamicStatus.STABLE,
        has_structural_heart_disease=has_shd,
        lvef=patient.lvef,
    )
    rec_set.add_all(acute_plan.acute_management)
    
    # Ablation assessment
    ablation_plan = assess_vt_ablation_indication(
        vt_type=vt_type,
        has_structural_heart_disease=has_shd,
        lvef=patient.lvef,
    )
    if ablation_plan.ablation_recommendation:
        rec_set.add(ablation_plan.ablation_recommendation)
    
    # Antiarrhythmic selection
    aad_recs = get_antiarrhythmic_for_vt(
        vt_type=vt_type,
        has_structural_heart_disease=has_shd,
        lvef=patient.lvef,
        has_cad=patient.has_diagnosis("coronary_artery_disease"),
        has_hf=patient.has_diagnosis("heart_failure"),
    )
    rec_set.add_all(aad_recs.recommendations)
    
    return rec_set
