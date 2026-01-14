"""
Cardiotoxicity Management - ESC 2022 Cardio-Oncology Guidelines.

Definition and management of cancer therapy-related cardiotoxicity:
- CTRCD definitions
- LV dysfunction management
- Myocarditis management
- Vascular toxicity
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


class CTRCDSeverity(Enum):
    """Cancer therapy-related cardiac dysfunction severity."""
    MILD = "mild"           # LVEF 50-54% or GLS decline 10-15%
    MODERATE = "moderate"   # LVEF 40-49%
    SEVERE = "severe"       # LVEF < 40%
    VERY_SEVERE = "very_severe"  # LVEF < 40% with HF symptoms


class CardiotoxicityType(Enum):
    """Types of cardiotoxicity."""
    LV_DYSFUNCTION = "lv_dysfunction"
    MYOCARDITIS = "myocarditis"
    ARRHYTHMIA = "arrhythmia"
    QT_PROLONGATION = "qt_prolongation"
    HYPERTENSION = "hypertension"
    CORONARY_VASOSPASM = "coronary_vasospasm"
    ARTERIAL_THROMBOSIS = "arterial_thrombosis"
    VENOUS_THROMBOSIS = "venous_thrombosis"
    PERICARDITIS = "pericarditis"
    PULMONARY_HYPERTENSION = "pulmonary_hypertension"


@dataclass
class CTRCDAssessment:
    """Assessment of cancer therapy-related cardiac dysfunction."""
    present: bool
    severity: Optional[CTRCDSeverity] = None
    toxicity_type: CardiotoxicityType = CardiotoxicityType.LV_DYSFUNCTION
    symptomatic: bool = False
    lvef_current: Optional[float] = None
    lvef_baseline: Optional[float] = None
    lvef_decline: Optional[float] = None  # Absolute % decline
    gls_decline_relative: Optional[float] = None  # % relative decline
    recommendations: List[Recommendation] = field(default_factory=list)
    can_continue_cancer_therapy: bool = True
    requires_cardiology_referral: bool = False


def define_ctrcd(
    lvef_current: float,
    lvef_baseline: Optional[float] = None,
    gls_current: Optional[float] = None,
    gls_baseline: Optional[float] = None,
    symptomatic: bool = False,
    troponin_elevated: bool = False,
) -> CTRCDAssessment:
    """
    Define and classify CTRCD per ESC 2022 criteria.
    
    Per ESC 2022 Table 3: Definition of CTRCD.
    
    Definitions:
    - Symptomatic CTRCD: HF symptoms + LVEF decline
    - Asymptomatic CTRCD: 
        - Severe: LVEF < 40%
        - Moderate: LVEF 40-49% with decline >= 10%
        - Mild: LVEF >= 50% but decline 10% to < 50% OR GLS relative decline > 15%
    
    Args:
        lvef_current: Current LVEF (%)
        lvef_baseline: Baseline LVEF (%)
        gls_current: Current GLS (%)
        gls_baseline: Baseline GLS (%)
        symptomatic: HF symptoms present
        troponin_elevated: Elevated troponin
    
    Returns:
        CTRCDAssessment
    """
    # Calculate declines
    lvef_decline = None
    gls_relative_decline = None
    
    if lvef_baseline:
        lvef_decline = lvef_baseline - lvef_current
    
    if gls_baseline and gls_current:
        # GLS is negative, so decline means less negative (closer to 0)
        gls_relative_decline = ((abs(gls_baseline) - abs(gls_current)) / abs(gls_baseline)) * 100
    
    # Determine severity
    severity = None
    present = False
    
    # Severe CTRCD: LVEF < 40%
    if lvef_current < 40:
        present = True
        severity = CTRCDSeverity.VERY_SEVERE if symptomatic else CTRCDSeverity.SEVERE
    
    # Moderate CTRCD: LVEF 40-49% with >= 10% decline
    elif 40 <= lvef_current < 50:
        if lvef_decline and lvef_decline >= 10:
            present = True
            severity = CTRCDSeverity.MODERATE
        elif symptomatic:
            present = True
            severity = CTRCDSeverity.MODERATE
    
    # Mild CTRCD: LVEF >= 50% but decline >= 10% OR GLS decline > 15%
    elif lvef_current >= 50:
        if lvef_decline and lvef_decline >= 10:
            present = True
            severity = CTRCDSeverity.MILD
        elif gls_relative_decline and gls_relative_decline > 15:
            present = True
            severity = CTRCDSeverity.MILD
    
    # Subclinical cardiotoxicity: GLS decline without LVEF criteria
    if not present and gls_relative_decline and gls_relative_decline > 15:
        present = True
        severity = CTRCDSeverity.MILD
    
    return CTRCDAssessment(
        present=present,
        severity=severity,
        symptomatic=symptomatic,
        lvef_current=lvef_current,
        lvef_baseline=lvef_baseline,
        lvef_decline=lvef_decline,
        gls_decline_relative=gls_relative_decline,
        requires_cardiology_referral=present,
        can_continue_cancer_therapy=lvef_current >= 50 and not symptomatic,
    )


def manage_ctrcd(
    lvef_current: float,
    lvef_baseline: Optional[float] = None,
    symptomatic: bool = False,
    cancer_therapy: str = "anthracycline",
    cancer_prognosis: str = "good",  # "good", "moderate", "poor"
) -> RecommendationSet:
    """
    Manage cancer therapy-related cardiac dysfunction.
    
    Per ESC 2022 Section 6.
    
    Key principles:
    1. Severity determines urgency of intervention
    2. Balance cardiotoxicity against cancer prognosis
    3. HF treatment with ACE-I/ARB + BB is foundation
    4. Decision to continue/hold/stop cancer therapy is multidisciplinary
    
    Args:
        lvef_current: Current LVEF
        lvef_baseline: Baseline LVEF
        symptomatic: HF symptoms
        cancer_therapy: Type of therapy causing CTRCD
        cancer_prognosis: Cancer prognosis (affects risk-benefit)
    
    Returns:
        RecommendationSet with management recommendations
    """
    rec_set = RecommendationSet(
        title="Management of Cancer Therapy-Related Cardiac Dysfunction",
        primary_guideline="ESC Cardio-Oncology 2022",
    )
    
    # Assess CTRCD
    assessment = define_ctrcd(
        lvef_current=lvef_current,
        lvef_baseline=lvef_baseline,
        symptomatic=symptomatic,
    )
    
    if not assessment.present:
        rec_set.description = f"LVEF {lvef_current}% - CTRCD criteria not met. Continue cancer therapy with standard surveillance."
        return rec_set
    
    rec_set.description = f"CTRCD {assessment.severity.value.upper()}: LVEF {lvef_current}%"
    if assessment.lvef_decline:
        rec_set.description += f" (decline {assessment.lvef_decline}% from baseline)"
    
    # SEVERE/VERY SEVERE: LVEF < 40%
    if assessment.severity in [CTRCDSeverity.SEVERE, CTRCDSeverity.VERY_SEVERE]:
        rec_set.add(guideline_recommendation(
            action="Hold cancer therapy pending cardiology evaluation",
            guideline_key="esc_cardio_onc_2022",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.PHARMACOTHERAPY,
            urgency=Urgency.URGENT,
            section="6",
            rationale=f"LVEF {lvef_current}% < 40% - severe CTRCD",
        ))
        
        rec_set.add(guideline_recommendation(
            action="Start ACE-I/ARB (e.g., ramipril, enalapril) titrated to target dose",
            guideline_key="esc_cardio_onc_2022",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PHARMACOTHERAPY,
            urgency=Urgency.URGENT,
            section="6",
            rationale="Foundation of CTRCD treatment",
        ))
        
        rec_set.add(guideline_recommendation(
            action="Start beta-blocker (carvedilol, bisoprolol, metoprolol succinate) titrated to target",
            guideline_key="esc_cardio_onc_2022",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PHARMACOTHERAPY,
            urgency=Urgency.URGENT,
            section="6",
        ))
        
        if symptomatic:
            rec_set.add(guideline_recommendation(
                action="Treat HF symptoms: diuretics as needed for congestion",
                guideline_key="esc_cardio_onc_2022",
                evidence_class=EvidenceClass.I,
                evidence_level=EvidenceLevel.C,
                category=RecommendationCategory.PHARMACOTHERAPY,
                urgency=Urgency.URGENT,
                section="6",
            ))
            
            rec_set.add(guideline_recommendation(
                action="Consider SGLT2 inhibitor (dapagliflozin, empagliflozin) per HF guidelines",
                guideline_key="esc_cardio_onc_2022",
                evidence_class=EvidenceClass.IIA,
                evidence_level=EvidenceLevel.C,
                category=RecommendationCategory.PHARMACOTHERAPY,
                urgency=Urgency.SOON,
                section="6",
                rationale="SGLT2i reduce HF hospitalizations - extrapolated to CTRCD",
            ))
        
        rec_set.add(guideline_recommendation(
            action="Cardio-oncology MDT discussion: risk-benefit of continuing cancer therapy",
            guideline_key="esc_cardio_onc_2022",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.REFERRAL,
            urgency=Urgency.URGENT,
            section="6",
        ))
        
        rec_set.add(guideline_recommendation(
            action="Repeat echo in 2-4 weeks to assess for recovery",
            guideline_key="esc_cardio_onc_2022",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.MONITORING,
            urgency=Urgency.SOON,
            section="6",
        ))
    
    # MODERATE: LVEF 40-49%
    elif assessment.severity == CTRCDSeverity.MODERATE:
        rec_set.add(guideline_recommendation(
            action="Start ACE-I/ARB if not already on",
            guideline_key="esc_cardio_onc_2022",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PHARMACOTHERAPY,
            urgency=Urgency.SOON,
            section="6",
            rationale="Early treatment may promote recovery",
        ))
        
        rec_set.add(guideline_recommendation(
            action="Start beta-blocker if not already on",
            guideline_key="esc_cardio_onc_2022",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PHARMACOTHERAPY,
            urgency=Urgency.SOON,
            section="6",
        ))
        
        # HER2 therapy specific
        if "her2" in cancer_therapy.lower() or "trastuzumab" in cancer_therapy.lower():
            rec_set.add(guideline_recommendation(
                action="Hold HER2 therapy, reassess LVEF in 2-4 weeks. If recovers to >= 50%, may rechallenge.",
                guideline_key="esc_cardio_onc_2022",
                evidence_class=EvidenceClass.I,
                evidence_level=EvidenceLevel.B,
                category=RecommendationCategory.PHARMACOTHERAPY,
                urgency=Urgency.URGENT,
                section="6.2",
                rationale="HER2 cardiotoxicity is often reversible",
            ))
        else:
            rec_set.add(guideline_recommendation(
                action="Cardio-oncology discussion: consider holding/dose-reducing cancer therapy",
                guideline_key="esc_cardio_onc_2022",
                evidence_class=EvidenceClass.IIA,
                evidence_level=EvidenceLevel.C,
                category=RecommendationCategory.REFERRAL,
                urgency=Urgency.SOON,
                section="6",
            ))
        
        rec_set.add(guideline_recommendation(
            action="Repeat echo in 3-4 weeks",
            guideline_key="esc_cardio_onc_2022",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.MONITORING,
            urgency=Urgency.ROUTINE,
            section="6",
        ))
    
    # MILD: LVEF >= 50% with decline or GLS decline
    elif assessment.severity == CTRCDSeverity.MILD:
        rec_set.add(guideline_recommendation(
            action="Consider starting ACE-I/ARB for cardioprotection",
            guideline_key="esc_cardio_onc_2022",
            evidence_class=EvidenceClass.IIA,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PHARMACOTHERAPY,
            urgency=Urgency.ROUTINE,
            section="6",
            rationale="Early treatment may prevent progression",
        ))
        
        rec_set.add(guideline_recommendation(
            action="Consider starting beta-blocker for cardioprotection",
            guideline_key="esc_cardio_onc_2022",
            evidence_class=EvidenceClass.IIA,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PHARMACOTHERAPY,
            urgency=Urgency.ROUTINE,
            section="6",
        ))
        
        rec_set.add(guideline_recommendation(
            action="Cancer therapy can generally continue with enhanced surveillance",
            guideline_key="esc_cardio_onc_2022",
            evidence_class=EvidenceClass.IIA,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.MONITORING,
            urgency=Urgency.ROUTINE,
            section="6",
        ))
        
        rec_set.add(guideline_recommendation(
            action="Increase echo frequency (every 1-2 cycles)",
            guideline_key="esc_cardio_onc_2022",
            evidence_class=EvidenceClass.IIA,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.MONITORING,
            urgency=Urgency.ROUTINE,
            section="6",
        ))
    
    return rec_set


def manage_ici_myocarditis(
    troponin_elevated: bool,
    troponin_value: Optional[float] = None,
    new_ecg_changes: bool = False,
    lvef: Optional[float] = None,
    symptomatic: bool = False,
    concurrent_myositis: bool = False,
) -> RecommendationSet:
    """
    Manage immune checkpoint inhibitor myocarditis.
    
    Per ESC 2022 Section 6.4.
    
    ICI myocarditis:
    - Rare (0.1-1%) but high mortality (25-50%)
    - Often fulminant
    - Concurrent myositis common (CK elevation)
    - Requires high-dose steroids
    
    Args:
        troponin_elevated: Troponin above ULN
        troponin_value: Actual troponin value
        new_ecg_changes: New conduction/rhythm changes
        lvef: Current LVEF
        symptomatic: Cardiac symptoms
        concurrent_myositis: Elevated CK / myositis
    
    Returns:
        RecommendationSet
    """
    rec_set = RecommendationSet(
        title="Management of ICI-Associated Myocarditis",
        primary_guideline="ESC Cardio-Oncology 2022",
    )
    
    # Definite/probable myocarditis
    if troponin_elevated and (new_ecg_changes or symptomatic or (lvef and lvef < 50)):
        rec_set.description = "PROBABLE ICI MYOCARDITIS - URGENT MANAGEMENT REQUIRED"
        
        rec_set.add(guideline_recommendation(
            action="STOP immune checkpoint inhibitor IMMEDIATELY",
            guideline_key="esc_cardio_onc_2022",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.PHARMACOTHERAPY,
            urgency=Urgency.EMERGENT,
            section="6.4",
            rationale="ICI must be held with suspected myocarditis",
        ))
        
        rec_set.add(guideline_recommendation(
            action="High-dose methylprednisolone 500-1000mg IV daily for 3-5 days",
            guideline_key="esc_cardio_onc_2022",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.PHARMACOTHERAPY,
            urgency=Urgency.EMERGENT,
            section="6.4",
            rationale="High-dose corticosteroids are cornerstone of treatment",
        ))
        
        rec_set.add(guideline_recommendation(
            action="Cardiac MRI if stable; endomyocardial biopsy if diagnostic uncertainty",
            guideline_key="esc_cardio_onc_2022",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.DIAGNOSTIC,
            urgency=Urgency.URGENT,
            section="6.4",
        ))
        
        rec_set.add(guideline_recommendation(
            action="ICU admission for continuous monitoring - high risk of arrhythmia/cardiogenic shock",
            guideline_key="esc_cardio_onc_2022",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.REFERRAL,
            urgency=Urgency.EMERGENT,
            section="6.4",
        ))
        
        rec_set.add(guideline_recommendation(
            action="Check CK - concurrent myositis is common and indicates severe irAE",
            guideline_key="esc_cardio_onc_2022",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.DIAGNOSTIC,
            urgency=Urgency.EMERGENT,
            section="6.4",
        ))
        
        if concurrent_myositis:
            rec_set.add(guideline_recommendation(
                action="Concurrent myositis: risk of respiratory failure - monitor closely",
                guideline_key="esc_cardio_onc_2022",
                evidence_class=EvidenceClass.I,
                evidence_level=EvidenceLevel.C,
                category=RecommendationCategory.MONITORING,
                urgency=Urgency.EMERGENT,
                section="6.4",
            ))
        
        # Steroid-refractory
        rec_set.add(guideline_recommendation(
            action="If no improvement in 24-48h: consider additional immunosuppression (mycophenolate, ATG, infliximab, abatacept)",
            guideline_key="esc_cardio_onc_2022",
            evidence_class=EvidenceClass.IIA,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.PHARMACOTHERAPY,
            urgency=Urgency.URGENT,
            section="6.4",
            rationale="Steroid-refractory cases may need escalation",
        ))
        
        # No rechallenge
        rec_set.add(guideline_recommendation(
            action="Permanent discontinuation of ICI therapy - do NOT rechallenge",
            guideline_key="esc_cardio_onc_2022",
            evidence_class=EvidenceClass.III,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.PHARMACOTHERAPY,
            urgency=Urgency.ROUTINE,
            section="6.4",
            rationale="ICI rechallenge after myocarditis associated with high recurrence/mortality",
        ))
    
    # Possible myocarditis - elevated troponin alone
    elif troponin_elevated:
        rec_set.description = "Elevated troponin on ICI - evaluate for myocarditis"
        
        rec_set.add(guideline_recommendation(
            action="Hold ICI pending evaluation",
            guideline_key="esc_cardio_onc_2022",
            evidence_class=EvidenceClass.IIA,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.PHARMACOTHERAPY,
            urgency=Urgency.URGENT,
            section="6.4",
        ))
        
        rec_set.add(guideline_recommendation(
            action="Urgent ECG, echocardiogram, CK",
            guideline_key="esc_cardio_onc_2022",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.DIAGNOSTIC,
            urgency=Urgency.URGENT,
            section="6.4",
        ))
        
        rec_set.add(guideline_recommendation(
            action="Consider cardiac MRI for myocardial edema/inflammation",
            guideline_key="esc_cardio_onc_2022",
            evidence_class=EvidenceClass.IIA,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.DIAGNOSTIC,
            urgency=Urgency.SOON,
            section="6.4",
        ))
        
        rec_set.add(guideline_recommendation(
            action="If other causes excluded and concern for ICI myocarditis: start steroids empirically",
            guideline_key="esc_cardio_onc_2022",
            evidence_class=EvidenceClass.IIA,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.PHARMACOTHERAPY,
            urgency=Urgency.URGENT,
            section="6.4",
        ))
    
    return rec_set


def manage_cardiotoxicity(
    patient: "Patient",
    toxicity_type: CardiotoxicityType,
    lvef: Optional[float] = None,
) -> RecommendationSet:
    """
    General cardiotoxicity management router.
    
    Args:
        patient: Patient object
        toxicity_type: Type of cardiotoxicity
        lvef: Current LVEF if applicable
    
    Returns:
        RecommendationSet
    """
    if toxicity_type == CardiotoxicityType.LV_DYSFUNCTION:
        return manage_ctrcd(
            lvef_current=lvef or patient.lvef or 50,
            lvef_baseline=55,  # Assume normal if unknown
        )
    
    elif toxicity_type == CardiotoxicityType.MYOCARDITIS:
        return manage_ici_myocarditis(
            troponin_elevated=True,
            symptomatic=True,
            lvef=lvef,
        )
    
    elif toxicity_type == CardiotoxicityType.HYPERTENSION:
        rec_set = RecommendationSet(
            title="Management of Cancer Therapy-Induced Hypertension",
            primary_guideline="ESC Cardio-Oncology 2022",
        )
        rec_set.add(guideline_recommendation(
            action="Target BP < 140/90 mmHg; < 130/80 if tolerated",
            guideline_key="esc_cardio_onc_2022",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PHARMACOTHERAPY,
            urgency=Urgency.SOON,
            section="7.1",
        ))
        rec_set.add(guideline_recommendation(
            action="First-line: ACE-I/ARB or dihydropyridine CCB (amlodipine)",
            guideline_key="esc_cardio_onc_2022",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.PHARMACOTHERAPY,
            urgency=Urgency.SOON,
            section="7.1",
            rationale="Avoid non-DHP CCBs (diltiazem/verapamil) with TKIs due to interactions",
        ))
        return rec_set
    
    elif toxicity_type == CardiotoxicityType.QT_PROLONGATION:
        rec_set = RecommendationSet(
            title="Management of Drug-Induced QT Prolongation",
            primary_guideline="ESC Cardio-Oncology 2022",
        )
        rec_set.add(guideline_recommendation(
            action="Correct electrolytes: K+ > 4.0 mEq/L, Mg2+ > 2.0 mg/dL",
            guideline_key="esc_cardio_onc_2022",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PHARMACOTHERAPY,
            urgency=Urgency.URGENT,
            section="7.2",
        ))
        rec_set.add(guideline_recommendation(
            action="Review and discontinue other QT-prolonging drugs if possible",
            guideline_key="esc_cardio_onc_2022",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PHARMACOTHERAPY,
            urgency=Urgency.URGENT,
            section="7.2",
        ))
        rec_set.add(guideline_recommendation(
            action="If QTc > 500ms or increase > 60ms: hold offending drug, cardiology consultation",
            guideline_key="esc_cardio_onc_2022",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.PHARMACOTHERAPY,
            urgency=Urgency.URGENT,
            section="7.2",
        ))
        return rec_set
    
    # Default
    rec_set = RecommendationSet(
        title=f"Management of {toxicity_type.value}",
        primary_guideline="ESC Cardio-Oncology 2022",
    )
    rec_set.add(guideline_recommendation(
        action="Cardio-oncology consultation for individualized management",
        guideline_key="esc_cardio_onc_2022",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.C,
        category=RecommendationCategory.REFERRAL,
        urgency=Urgency.SOON,
        section="6",
    ))
    return rec_set
