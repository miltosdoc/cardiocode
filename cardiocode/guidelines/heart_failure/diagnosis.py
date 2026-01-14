"""
Heart Failure Diagnosis - ESC 2021 Guidelines.

Implements diagnostic algorithms from ESC HF 2021:
- Algorithm for diagnosis of HF (Figure 1)
- HF phenotype classification (HFrEF, HFmrEF, HFpEF)
- Congestion and perfusion assessment
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, List, TYPE_CHECKING
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


class HFPhenotype(Enum):
    """Heart Failure phenotype classification per ESC 2021."""
    HFREF = "HFrEF"      # LVEF <= 40%
    HFMREF = "HFmrEF"    # LVEF 41-49%
    HFPEF = "HFpEF"      # LVEF >= 50%
    UNKNOWN = "Unknown"


class CongestionStatus(Enum):
    """Congestion status for clinical profiling."""
    DRY = "dry"          # No congestion
    WET = "wet"          # Congested


class PerfusionStatus(Enum):
    """Perfusion status for clinical profiling."""
    WARM = "warm"        # Adequate perfusion
    COLD = "cold"        # Hypoperfused


@dataclass
class HFDiagnosisResult:
    """Result of heart failure diagnostic evaluation."""
    has_heart_failure: bool
    phenotype: HFPhenotype
    confidence: str  # "definite", "probable", "possible", "unlikely"
    
    # Supporting findings
    symptoms_present: List[str]
    signs_present: List[str]
    structural_abnormalities: List[str]
    functional_abnormalities: List[str]
    
    # Biomarkers
    natriuretic_peptide_elevated: Optional[bool] = None
    bnp_value: Optional[float] = None
    nt_pro_bnp_value: Optional[float] = None
    
    # Recommendations
    recommendations: List[Recommendation] = None
    
    def __post_init__(self):
        if self.recommendations is None:
            self.recommendations = []


def classify_hf_phenotype(lvef: Optional[float]) -> HFPhenotype:
    """
    Classify HF phenotype based on LVEF.
    
    Per ESC 2021 HF Guidelines Table 1:
    - HFrEF: LVEF <= 40%
    - HFmrEF: LVEF 41-49%
    - HFpEF: LVEF >= 50%
    
    Args:
        lvef: Left ventricular ejection fraction (%)
    
    Returns:
        HFPhenotype classification
    """
    if lvef is None:
        return HFPhenotype.UNKNOWN
    
    if lvef <= 40:
        return HFPhenotype.HFREF
    elif lvef <= 49:
        return HFPhenotype.HFMREF
    else:
        return HFPhenotype.HFPEF


def diagnose_heart_failure(patient: "Patient") -> HFDiagnosisResult:
    """
    Apply ESC 2021 HF diagnostic algorithm.
    
    Based on Figure 1: Algorithm for the diagnosis of heart failure
    
    Requires:
    1. Symptoms and/or signs of HF
    2. Elevated natriuretic peptides (BNP >= 35 pg/mL or NT-proBNP >= 125 pg/mL)
    3. Objective evidence of cardiac structural/functional abnormality
    
    Args:
        patient: Patient object with clinical data
    
    Returns:
        HFDiagnosisResult with diagnosis and recommendations
    """
    symptoms = []
    signs = []
    structural = []
    functional = []
    recommendations = []
    
    # Step 1: Assess symptoms of HF
    # Per Table 3: Symptoms and signs typical of heart failure
    typical_symptoms = [
        "breathlessness", "orthopnoea", "paroxysmal_nocturnal_dyspnoea",
        "reduced_exercise_tolerance", "fatigue", "ankle_swelling"
    ]
    
    less_typical_symptoms = [
        "nocturnal_cough", "wheezing", "bloated_feeling", "loss_of_appetite",
        "confusion", "depression", "palpitations", "dizziness", "syncope", "bendopnoea"
    ]
    
    # Check NYHA class as proxy for symptoms
    if patient.nyha_class:
        if patient.nyha_class.value >= 2:
            symptoms.append("Reduced exercise tolerance (NYHA >= II)")
        if patient.nyha_class.value >= 3:
            symptoms.append("Dyspnea with less than ordinary activity")
        if patient.nyha_class.value == 4:
            symptoms.append("Symptoms at rest")
    
    # Step 2: Assess signs of HF
    # Per Table 3: Signs more specific for HF
    if patient.vitals:
        if patient.vitals.heart_rate and patient.vitals.heart_rate > 90:
            signs.append(f"Elevated heart rate ({patient.vitals.heart_rate} bpm)")
    
    if patient.ecg:
        if patient.ecg.af_present:
            signs.append("Atrial fibrillation")
        if patient.ecg.lbbb:
            signs.append("Left bundle branch block")
    
    # Step 3: Check natriuretic peptides
    np_elevated = None
    bnp_val = None
    nt_pro_bnp_val = None
    
    if patient.labs:
        if patient.labs.bnp is not None:
            bnp_val = patient.labs.bnp
            np_elevated = patient.labs.bnp >= 35
            if np_elevated:
                signs.append(f"Elevated BNP ({patient.labs.bnp} pg/mL)")
        
        if patient.labs.nt_pro_bnp is not None:
            nt_pro_bnp_val = patient.labs.nt_pro_bnp
            np_elevated = patient.labs.nt_pro_bnp >= 125
            if np_elevated:
                signs.append(f"Elevated NT-proBNP ({patient.labs.nt_pro_bnp} pg/mL)")
    
    # Step 4: Assess structural/functional abnormalities on Echo
    if patient.echo:
        # Structural abnormalities
        if patient.echo.lvidd and patient.echo.lvidd > 56:
            structural.append(f"LV dilation (LVIDd {patient.echo.lvidd} mm)")
        
        if patient.echo.la_volume_index and patient.echo.la_volume_index > 34:
            structural.append(f"LA enlargement (LAVI {patient.echo.la_volume_index} mL/m2)")
        
        if patient.echo.lv_mass_index:
            # LVH cutoffs: >95 g/m2 women, >115 g/m2 men
            lvh_threshold = 95 if (patient.sex and patient.sex.value == "female") else 115
            if patient.echo.lv_mass_index > lvh_threshold:
                structural.append(f"LV hypertrophy (LVMI {patient.echo.lv_mass_index} g/m2)")
        
        # Functional abnormalities
        if patient.echo.lvef is not None:
            if patient.echo.lvef < 50:
                functional.append(f"Reduced LVEF ({patient.echo.lvef}%)")
        
        if patient.echo.gls and patient.echo.gls > -16:  # GLS is negative, less negative = worse
            functional.append(f"Reduced GLS ({patient.echo.gls}%)")
        
        if patient.echo.e_e_prime_ratio and patient.echo.e_e_prime_ratio > 14:
            functional.append(f"Elevated filling pressures (E/e' {patient.echo.e_e_prime_ratio})")
        
        if patient.echo.tricuspid_regurgitation_velocity and patient.echo.tricuspid_regurgitation_velocity > 2.8:
            functional.append(f"Elevated PASP (TR velocity {patient.echo.tricuspid_regurgitation_velocity} m/s)")
    
    # Determine diagnosis confidence
    has_symptoms = len(symptoms) > 0 or (patient.nyha_class and patient.nyha_class.value >= 2)
    has_objective_evidence = len(structural) > 0 or len(functional) > 0
    
    if has_symptoms and np_elevated and has_objective_evidence:
        confidence = "definite"
        has_hf = True
    elif has_symptoms and has_objective_evidence:
        confidence = "probable"
        has_hf = True
        recommendations.append(guideline_recommendation(
            action="Obtain natriuretic peptides (BNP or NT-proBNP) to support diagnosis",
            guideline_key="esc_hf_2021",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.DIAGNOSTIC,
            section="4.1",
            studies=["MONICA", "Breathing Not Properly"],
        ))
    elif has_symptoms and np_elevated:
        confidence = "possible"
        has_hf = True
        recommendations.append(guideline_recommendation(
            action="Obtain echocardiogram to assess cardiac structure and function",
            guideline_key="esc_hf_2021",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.DIAGNOSTIC,
            urgency=Urgency.SOON,
            section="4.1",
        ))
    elif has_symptoms:
        confidence = "possible"
        has_hf = False
        recommendations.append(guideline_recommendation(
            action="Check natriuretic peptides. If BNP < 35 pg/mL or NT-proBNP < 125 pg/mL, HF unlikely",
            guideline_key="esc_hf_2021",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.DIAGNOSTIC,
            section="4.1",
            rationale="Normal natriuretic peptides make HF diagnosis unlikely (high negative predictive value)",
        ))
    else:
        confidence = "unlikely"
        has_hf = False
    
    # Determine phenotype
    lvef = patient.lvef or (patient.echo.lvef if patient.echo else None)
    phenotype = classify_hf_phenotype(lvef)
    
    # Add phenotype-specific recommendations
    if has_hf and phenotype != HFPhenotype.UNKNOWN:
        if phenotype == HFPhenotype.HFPEF:
            recommendations.append(guideline_recommendation(
                action="Confirm HFpEF diagnosis using HFA-PEFF score or exercise hemodynamics if uncertain",
                guideline_key="esc_hf_2021",
                evidence_class=EvidenceClass.IIA,
                evidence_level=EvidenceLevel.B,
                category=RecommendationCategory.DIAGNOSTIC,
                section="4.2.2",
                rationale="HFpEF diagnosis can be challenging; additional workup may be needed",
            ))
    
    return HFDiagnosisResult(
        has_heart_failure=has_hf,
        phenotype=phenotype,
        confidence=confidence,
        symptoms_present=symptoms,
        signs_present=signs,
        structural_abnormalities=structural,
        functional_abnormalities=functional,
        natriuretic_peptide_elevated=np_elevated,
        bnp_value=bnp_val,
        nt_pro_bnp_value=nt_pro_bnp_val,
        recommendations=recommendations,
    )


def assess_congestion(patient: "Patient") -> CongestionStatus:
    """
    Assess congestion status for clinical profiling.
    
    Per ESC 2021 Table 4: Signs and symptoms of congestion and hypoperfusion.
    
    Congestion signs:
    - Orthopnoea/PND
    - Pulmonary rales
    - Peripheral edema
    - JVD
    - Hepatomegaly
    - Ascites
    """
    congestion_points = 0
    
    # NYHA class suggests congestion
    if patient.nyha_class:
        if patient.nyha_class.value >= 3:
            congestion_points += 2
        elif patient.nyha_class.value >= 2:
            congestion_points += 1
    
    # Elevated natriuretic peptides
    if patient.labs:
        if patient.labs.bnp and patient.labs.bnp > 100:
            congestion_points += 2
        elif patient.labs.nt_pro_bnp and patient.labs.nt_pro_bnp > 300:
            congestion_points += 2
    
    # Echo signs
    if patient.echo:
        if patient.echo.ivc_diameter and patient.echo.ivc_diameter > 21:
            congestion_points += 1
        if patient.echo.ivc_collapsibility and patient.echo.ivc_collapsibility < 50:
            congestion_points += 1
        if patient.echo.e_e_prime_ratio and patient.echo.e_e_prime_ratio > 14:
            congestion_points += 1
    
    return CongestionStatus.WET if congestion_points >= 2 else CongestionStatus.DRY


def assess_perfusion(patient: "Patient") -> PerfusionStatus:
    """
    Assess perfusion status for clinical profiling.
    
    Per ESC 2021 Table 4: Signs of hypoperfusion:
    - Cold, clammy extremities
    - Oliguria
    - Mental confusion
    - Dizziness
    - Low pulse pressure
    """
    hypoperfusion_points = 0
    
    if patient.vitals:
        # Low systolic BP
        if patient.vitals.systolic_bp and patient.vitals.systolic_bp < 90:
            hypoperfusion_points += 2
        
        # Narrow pulse pressure
        if patient.vitals.pulse_pressure and patient.vitals.pulse_pressure < 25:
            hypoperfusion_points += 1
    
    # Renal dysfunction (may indicate renal hypoperfusion)
    if patient.labs:
        if patient.labs.creatinine and patient.labs.creatinine > 2.0:
            hypoperfusion_points += 1
        if patient.labs.egfr and patient.labs.egfr < 30:
            hypoperfusion_points += 1
    
    return PerfusionStatus.COLD if hypoperfusion_points >= 2 else PerfusionStatus.WARM


def get_clinical_profile(patient: "Patient") -> str:
    """
    Determine clinical profile for acute HF (warm-wet, cold-wet, etc.).
    
    Per ESC 2021 Figure 5: Clinical profiles in acute HF.
    
    Returns:
        Clinical profile string ("warm-wet", "warm-dry", "cold-wet", "cold-dry")
    """
    congestion = assess_congestion(patient)
    perfusion = assess_perfusion(patient)
    
    return f"{perfusion.value}-{congestion.value}"
