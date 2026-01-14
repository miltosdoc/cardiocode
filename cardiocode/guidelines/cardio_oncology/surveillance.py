"""
Surveillance Protocols - ESC 2022 Cardio-Oncology Guidelines.

Cardiac monitoring during and after cancer therapy:
- Imaging protocols
- Biomarker monitoring
- Agent-specific schedules
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
from cardiocode.guidelines.cardio_oncology.baseline_risk import (
    CardiotoxicityRisk,
    CancerTherapyType,
)


class SurveillanceIntensity(Enum):
    """Intensity of cardiac surveillance."""
    STANDARD = "standard"      # Standard protocol
    ENHANCED = "enhanced"      # More frequent monitoring
    INTENSIVE = "intensive"    # Very frequent, often inpatient


@dataclass
class SurveillanceSchedule:
    """Cardiac surveillance schedule."""
    therapy_type: CancerTherapyType
    risk_category: CardiotoxicityRisk
    intensity: SurveillanceIntensity
    echo_frequency: str  # e.g., "every 3 months"
    biomarker_frequency: str  # e.g., "before each cycle"
    ecg_frequency: str
    additional_monitoring: List[str] = field(default_factory=list)
    recommendations: List[Recommendation] = field(default_factory=list)


def get_anthracycline_surveillance(
    risk_category: CardiotoxicityRisk,
    cumulative_dose: float,  # mg/m2 doxorubicin equivalent
    baseline_lvef: Optional[float] = None,
    baseline_gls: Optional[float] = None,
) -> SurveillanceSchedule:
    """
    Get surveillance protocol for anthracycline therapy.
    
    Per ESC 2022 Section 5.1.
    
    Monitoring approach:
    - LVEF and GLS at baseline and during/after treatment
    - Biomarkers (troponin, BNP) can detect early injury
    - GLS decline >15% relative is early marker
    
    Args:
        risk_category: Baseline cardiotoxicity risk
        cumulative_dose: Planned cumulative dose
        baseline_lvef: Baseline LVEF
        baseline_gls: Baseline GLS
    
    Returns:
        SurveillanceSchedule
    """
    recommendations = []
    additional = []
    
    # Determine intensity based on risk and dose
    if risk_category in [CardiotoxicityRisk.HIGH, CardiotoxicityRisk.VERY_HIGH]:
        intensity = SurveillanceIntensity.INTENSIVE
        echo_freq = "Every 2 cycles (6 weeks) or after cumulative dose of 200-250 mg/m2"
        biomarker_freq = "Before each cycle"
    elif risk_category == CardiotoxicityRisk.MODERATE or cumulative_dose >= 300:
        intensity = SurveillanceIntensity.ENHANCED
        echo_freq = "Every 3 cycles or after cumulative dose of 250-300 mg/m2"
        biomarker_freq = "Every 2-3 cycles"
    else:
        intensity = SurveillanceIntensity.STANDARD
        echo_freq = "At treatment completion; consider mid-treatment if dose > 300 mg/m2"
        biomarker_freq = "At baseline; consider during treatment"
    
    # Core recommendations
    recommendations.append(guideline_recommendation(
        action="Echocardiogram with LVEF and GLS during anthracycline therapy",
        guideline_key="esc_cardio_onc_2022",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.B,
        category=RecommendationCategory.MONITORING,
        urgency=Urgency.ROUTINE,
        section="5.1",
        rationale=f"Schedule: {echo_freq}",
    ))
    
    # GLS monitoring
    if baseline_gls is not None:
        recommendations.append(guideline_recommendation(
            action=f"Monitor for GLS decline >15% from baseline ({baseline_gls}%) - indicates subclinical cardiotoxicity",
            guideline_key="esc_cardio_onc_2022",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.MONITORING,
            urgency=Urgency.ROUTINE,
            section="5.1",
            rationale="GLS decline predicts subsequent LVEF decline",
        ))
        additional.append("GLS decline >15% relative: consider cardioprotection and cardiology referral")
    
    # Biomarkers
    recommendations.append(guideline_recommendation(
        action="Troponin monitoring during anthracycline therapy",
        guideline_key="esc_cardio_onc_2022",
        evidence_class=EvidenceClass.IIA,
        evidence_level=EvidenceLevel.B,
        category=RecommendationCategory.MONITORING,
        urgency=Urgency.ROUTINE,
        section="5.1",
        rationale=f"Schedule: {biomarker_freq}",
    ))
    
    # Post-treatment surveillance
    recommendations.append(guideline_recommendation(
        action="Echocardiogram 3-6 months after completing anthracycline therapy",
        guideline_key="esc_cardio_onc_2022",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.B,
        category=RecommendationCategory.MONITORING,
        urgency=Urgency.ROUTINE,
        section="5.1",
    ))
    
    # Long-term survivors
    if cumulative_dose >= 300:
        recommendations.append(guideline_recommendation(
            action="Long-term surveillance: echo every 2-5 years depending on dose and risk factors",
            guideline_key="esc_cardio_onc_2022",
            evidence_class=EvidenceClass.IIA,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.MONITORING,
            urgency=Urgency.ROUTINE,
            section="5.1",
            rationale="Anthracycline cardiotoxicity can manifest years later",
        ))
        additional.append("Survivors of high-dose anthracyclines need lifelong CV surveillance")
    
    return SurveillanceSchedule(
        therapy_type=CancerTherapyType.ANTHRACYCLINE,
        risk_category=risk_category,
        intensity=intensity,
        echo_frequency=echo_freq,
        biomarker_frequency=biomarker_freq,
        ecg_frequency="Baseline and as clinically indicated",
        additional_monitoring=additional,
        recommendations=recommendations,
    )


def get_her2_surveillance(
    risk_category: CardiotoxicityRisk,
    concurrent_anthracycline: bool = False,
    baseline_lvef: Optional[float] = None,
) -> SurveillanceSchedule:
    """
    Get surveillance protocol for HER2-targeted therapy.
    
    Per ESC 2022 Section 5.2.
    
    Key points:
    - LVEF every 3 months during therapy (standard)
    - More frequent if high risk or concurrent anthracycline
    - Can continue/resume if LVEF recovers
    
    Args:
        risk_category: Baseline cardiotoxicity risk
        concurrent_anthracycline: Concurrent anthracycline
        baseline_lvef: Baseline LVEF
    
    Returns:
        SurveillanceSchedule
    """
    recommendations = []
    additional = []
    
    # Determine intensity
    if concurrent_anthracycline or risk_category == CardiotoxicityRisk.VERY_HIGH:
        intensity = SurveillanceIntensity.INTENSIVE
        echo_freq = "Every 6 weeks during concurrent anthracycline, then every 3 months"
    elif risk_category == CardiotoxicityRisk.HIGH:
        intensity = SurveillanceIntensity.ENHANCED
        echo_freq = "Every 2 months"
    else:
        intensity = SurveillanceIntensity.STANDARD
        echo_freq = "Every 3 months"
    
    # Core recommendations
    recommendations.append(guideline_recommendation(
        action=f"Echocardiogram {echo_freq} during HER2 therapy",
        guideline_key="esc_cardio_onc_2022",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.B,
        category=RecommendationCategory.MONITORING,
        urgency=Urgency.ROUTINE,
        section="5.2",
        rationale="HER2 therapy requires regular LVEF monitoring",
    ))
    
    # LVEF thresholds
    if baseline_lvef:
        recommendations.append(guideline_recommendation(
            action=f"If LVEF drops >10% to below 50%: hold HER2 therapy, start HF treatment, reassess in 2-4 weeks",
            guideline_key="esc_cardio_onc_2022",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.MONITORING,
            urgency=Urgency.URGENT,
            section="5.2",
            rationale=f"Baseline LVEF {baseline_lvef}%. LVEF decline is key trigger for intervention.",
        ))
    
    additional.append("LVEF drop >10% to <50%: hold therapy, start ACE-I + BB")
    additional.append("If LVEF recovers to >= 50%: can rechallenge with close monitoring")
    additional.append("If LVEF <40% or symptomatic HF: cardiology consultation required")
    
    # Biomarkers less useful for HER2
    recommendations.append(guideline_recommendation(
        action="Consider troponin if symptomatic or LVEF declining",
        guideline_key="esc_cardio_onc_2022",
        evidence_class=EvidenceClass.IIB,
        evidence_level=EvidenceLevel.C,
        category=RecommendationCategory.MONITORING,
        urgency=Urgency.ROUTINE,
        section="5.2",
    ))
    
    return SurveillanceSchedule(
        therapy_type=CancerTherapyType.HER2_TARGETED,
        risk_category=risk_category,
        intensity=intensity,
        echo_frequency=echo_freq,
        biomarker_frequency="As clinically indicated",
        ecg_frequency="Baseline",
        additional_monitoring=additional,
        recommendations=recommendations,
    )


def get_vegf_inhibitor_surveillance(
    risk_category: CardiotoxicityRisk,
    agent: str = "general",  # bevacizumab, sunitinib, etc.
    baseline_bp: Optional[tuple] = None,  # (systolic, diastolic)
    baseline_lvef: Optional[float] = None,
) -> SurveillanceSchedule:
    """
    Get surveillance for VEGF inhibitor therapy.
    
    Per ESC 2022 Section 5.3.
    
    Main concerns:
    - Hypertension (most common)
    - Arterial thromboembolism
    - LV dysfunction (less common)
    - QTc prolongation (some agents)
    
    Args:
        risk_category: Baseline CV risk
        agent: Specific VEGF inhibitor
        baseline_bp: Baseline blood pressure
        baseline_lvef: Baseline LVEF
    
    Returns:
        SurveillanceSchedule
    """
    recommendations = []
    additional = []
    
    # VEGF inhibitors - BP monitoring is key
    intensity = SurveillanceIntensity.ENHANCED if risk_category != CardiotoxicityRisk.LOW else SurveillanceIntensity.STANDARD
    
    # Blood pressure monitoring - critical
    recommendations.append(guideline_recommendation(
        action="Weekly blood pressure monitoring during first cycle, then every 2-3 weeks",
        guideline_key="esc_cardio_onc_2022",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.B,
        category=RecommendationCategory.MONITORING,
        urgency=Urgency.SOON,
        section="5.3",
        rationale="VEGF inhibitor-induced hypertension is common and requires aggressive management",
    ))
    
    if baseline_bp:
        recommendations.append(guideline_recommendation(
            action=f"Target BP < 140/90 mmHg (baseline {baseline_bp[0]}/{baseline_bp[1]}). Start/uptitrate antihypertensives promptly if elevated.",
            guideline_key="esc_cardio_onc_2022",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.MONITORING,
            urgency=Urgency.ROUTINE,
            section="5.3",
            rationale="Prefer ACE-I/ARB or dihydropyridine CCB. Avoid diltiazem/verapamil with TKIs.",
        ))
    
    additional.append("Home BP monitoring recommended")
    additional.append("Target BP < 140/90; < 130/80 if tolerated")
    additional.append("ACE-I/ARB preferred; avoid non-DHP CCBs with TKIs (drug interactions)")
    
    # Echo - periodic
    echo_freq = "Every 3-4 months" if risk_category != CardiotoxicityRisk.LOW else "Every 6 months"
    recommendations.append(guideline_recommendation(
        action=f"Echocardiogram {echo_freq} during VEGF inhibitor therapy",
        guideline_key="esc_cardio_onc_2022",
        evidence_class=EvidenceClass.IIA,
        evidence_level=EvidenceLevel.C,
        category=RecommendationCategory.MONITORING,
        urgency=Urgency.ROUTINE,
        section="5.3",
    ))
    
    # ECG for QTc
    recommendations.append(guideline_recommendation(
        action="Baseline ECG and periodic QTc monitoring (especially with sunitinib, vandetanib)",
        guideline_key="esc_cardio_onc_2022",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.C,
        category=RecommendationCategory.MONITORING,
        urgency=Urgency.ROUTINE,
        section="5.3",
    ))
    
    additional.append("QTc prolongation: correct electrolytes, avoid other QT-prolonging drugs")
    
    return SurveillanceSchedule(
        therapy_type=CancerTherapyType.VEGF_INHIBITOR,
        risk_category=risk_category,
        intensity=intensity,
        echo_frequency=echo_freq,
        biomarker_frequency="As clinically indicated",
        ecg_frequency="Baseline and every 2-4 weeks for first 3 months",
        additional_monitoring=additional,
        recommendations=recommendations,
    )


def get_checkpoint_inhibitor_surveillance(
    risk_category: CardiotoxicityRisk,
    combination_ici: bool = False,  # PD-1/CTLA-4 combination
) -> SurveillanceSchedule:
    """
    Get surveillance for immune checkpoint inhibitor therapy.
    
    Per ESC 2022 Section 5.4.
    
    Key concerns:
    - Myocarditis (rare but fulminant)
    - Pericarditis
    - Arrhythmias
    - Often occurs early (within first 3 months)
    
    Args:
        risk_category: Baseline CV risk
        combination_ici: Dual checkpoint inhibitor therapy
    
    Returns:
        SurveillanceSchedule
    """
    recommendations = []
    additional = []
    
    # Combination therapy = higher risk
    if combination_ici:
        intensity = SurveillanceIntensity.INTENSIVE
        additional.append("Combination ICI therapy: higher risk of immune-related adverse events including myocarditis")
    else:
        intensity = SurveillanceIntensity.ENHANCED if risk_category != CardiotoxicityRisk.LOW else SurveillanceIntensity.STANDARD
    
    # Baseline
    recommendations.append(guideline_recommendation(
        action="Baseline ECG, troponin, and BNP before checkpoint inhibitor therapy",
        guideline_key="esc_cardio_onc_2022",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.C,
        category=RecommendationCategory.DIAGNOSTIC,
        urgency=Urgency.SOON,
        section="5.4",
        rationale="Baseline values help identify incident myocarditis",
    ))
    
    # Troponin monitoring
    troponin_freq = "Before each cycle for first 4 cycles, then every 3 cycles" if combination_ici else "Consider before each cycle for first 3 cycles"
    recommendations.append(guideline_recommendation(
        action=f"Troponin monitoring: {troponin_freq}",
        guideline_key="esc_cardio_onc_2022",
        evidence_class=EvidenceClass.IIA if combination_ici else EvidenceClass.IIB,
        evidence_level=EvidenceLevel.C,
        category=RecommendationCategory.MONITORING,
        urgency=Urgency.ROUTINE,
        section="5.4",
        rationale="Troponin elevation is early marker of ICI myocarditis",
    ))
    
    # ECG
    recommendations.append(guideline_recommendation(
        action="ECG before each cycle for first 4 cycles",
        guideline_key="esc_cardio_onc_2022",
        evidence_class=EvidenceClass.IIA,
        evidence_level=EvidenceLevel.C,
        category=RecommendationCategory.MONITORING,
        urgency=Urgency.ROUTINE,
        section="5.4",
        rationale="New conduction abnormalities may indicate myocarditis",
    ))
    
    # Clinical vigilance
    recommendations.append(guideline_recommendation(
        action="Educate patient about symptoms: chest pain, dyspnea, palpitations, syncope - seek immediate evaluation",
        guideline_key="esc_cardio_onc_2022",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.C,
        category=RecommendationCategory.MONITORING,
        urgency=Urgency.ROUTINE,
        section="5.4",
        rationale="ICI myocarditis can progress rapidly",
    ))
    
    additional.append("ICI myocarditis: median onset 34 days after first dose")
    additional.append("Any new cardiac symptoms: urgent troponin, ECG, consider echo and CMR")
    additional.append("Concurrent myositis (CK elevation) common with ICI myocarditis")
    
    return SurveillanceSchedule(
        therapy_type=CancerTherapyType.IMMUNE_CHECKPOINT,
        risk_category=risk_category,
        intensity=intensity,
        echo_frequency="If symptoms or biomarker elevation; not routine",
        biomarker_frequency=troponin_freq,
        ecg_frequency="Before each cycle for first 4 cycles",
        additional_monitoring=additional,
        recommendations=recommendations,
    )


def get_surveillance_protocol(
    patient: "Patient", 
    therapy: CancerTherapyType,
    risk_category: CardiotoxicityRisk = CardiotoxicityRisk.MODERATE,
) -> RecommendationSet:
    """
    Get surveillance protocol for a specific cancer therapy.
    
    Args:
        patient: Patient object
        therapy: Type of cancer therapy
        risk_category: Baseline risk category
    
    Returns:
        RecommendationSet with surveillance recommendations
    """
    rec_set = RecommendationSet(
        title=f"Cardiac Surveillance Protocol - {therapy.value}",
        description="Per ESC 2022 Cardio-Oncology Guidelines",
        primary_guideline="ESC Cardio-Oncology 2022",
    )
    
    if therapy == CancerTherapyType.ANTHRACYCLINE:
        schedule = get_anthracycline_surveillance(
            risk_category=risk_category,
            cumulative_dose=300,  # Default moderate dose
            baseline_lvef=patient.lvef,
        )
    elif therapy == CancerTherapyType.HER2_TARGETED:
        schedule = get_her2_surveillance(
            risk_category=risk_category,
            baseline_lvef=patient.lvef,
        )
    elif therapy == CancerTherapyType.VEGF_INHIBITOR:
        schedule = get_vegf_inhibitor_surveillance(
            risk_category=risk_category,
            baseline_lvef=patient.lvef,
        )
    elif therapy == CancerTherapyType.IMMUNE_CHECKPOINT:
        schedule = get_checkpoint_inhibitor_surveillance(
            risk_category=risk_category,
        )
    else:
        # Generic surveillance
        rec_set.add(guideline_recommendation(
            action="Baseline cardiac evaluation (ECG, echo, biomarkers) before cancer therapy",
            guideline_key="esc_cardio_onc_2022",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.DIAGNOSTIC,
            urgency=Urgency.SOON,
            section="4",
        ))
        return rec_set
    
    rec_set.add_all(schedule.recommendations)
    rec_set.description += f"\n\nIntensity: {schedule.intensity.value}"
    rec_set.description += f"\nEcho: {schedule.echo_frequency}"
    rec_set.description += f"\nBiomarkers: {schedule.biomarker_frequency}"
    rec_set.description += f"\nECG: {schedule.ecg_frequency}"
    
    if schedule.additional_monitoring:
        rec_set.description += "\n\nKey Points:\n- " + "\n- ".join(schedule.additional_monitoring)
    
    return rec_set
