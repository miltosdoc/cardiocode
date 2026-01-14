"""
CardioCode Usage Examples

This file demonstrates how to use the CardioCode framework
for clinical decision support.

IMPORTANT: This is decision SUPPORT, not decision MAKING.
All recommendations require clinical judgment and should be
validated by qualified healthcare providers.
"""

import sys
sys.path.insert(0, '.')

from cardiocode.core.types import (
    Patient, 
    Sex, 
    NYHAClass, 
    VitalSigns, 
    LabValues, 
    EchoFindings,
    ECGFindings,
    RhythmType,
    AFType,
)
from cardiocode.knowledge.scores import cha2ds2_vasc, has_bled, grace_score


# =============================================================================
# EXAMPLE 1: Heart Failure Patient with AF
# =============================================================================

def example_hf_af_patient():
    """
    Example: 72-year-old male with HFrEF and new atrial fibrillation
    """
    print("\n" + "="*60)
    print("EXAMPLE 1: HFrEF with new Atrial Fibrillation")
    print("="*60)
    
    # Create patient
    patient = Patient(
        patient_id="HF001",
        age=72,
        sex=Sex.MALE,
        weight_kg=85,
        height_cm=175,
        
        # Vitals
        vitals=VitalSigns(
            heart_rate=88,
            systolic_bp=118,
            diastolic_bp=72,
            oxygen_saturation=94,
        ),
        
        # Labs
        labs=LabValues(
            creatinine=1.4,
            egfr=48,
            potassium=4.2,
            sodium=138,
            bnp=850,
            hemoglobin=12.5,
        ),
        
        # Echo
        echo=EchoFindings(
            lvef=32,
            lvidd=62,
            la_volume_index=42,
            e_e_prime_ratio=18,
        ),
        
        # ECG
        ecg=ECGFindings(
            rhythm=RhythmType.ATRIAL_FIBRILLATION,
            af_present=True,
            heart_rate=88,
            qrs_duration=110,
        ),
        
        # Clinical flags
        nyha_class=NYHAClass.III,
        has_diabetes=True,
        has_hypertension=True,
        has_cad=True,
        af_type=AFType.FIRST_DIAGNOSED,
        lvef=32,
    )
    
    print(f"\nPatient: {patient.age}yo {patient.sex.value}")
    print(f"LVEF: {patient.lvef}%")
    print(f"NYHA: Class {patient.nyha_class.value}")
    print(f"eGFR: {patient.labs.egfr} mL/min")
    print(f"BNP: {patient.labs.bnp} pg/mL")
    print(f"Rhythm: {patient.ecg.rhythm.value}")
    
    # Calculate CHA2DS2-VASc
    print("\n--- Stroke Risk Assessment ---")
    chads = cha2ds2_vasc(
        age=patient.age,
        sex="male",
        has_chf=True,
        has_hypertension=patient.has_hypertension,
        has_stroke_tia_te=False,
        has_vascular_disease=patient.has_cad,
        has_diabetes=patient.has_diabetes,
    )
    print(chads.format_for_display())
    
    # Calculate HAS-BLED
    print("\n--- Bleeding Risk Assessment ---")
    bled = has_bled(
        has_hypertension=patient.has_hypertension,
        abnormal_renal_function=patient.labs.egfr < 50,
        has_stroke=False,
        age_over_65=patient.age > 65,
    )
    print(bled.format_for_display())
    
    # Get HF treatment recommendations
    print("\n--- HF Treatment Recommendations ---")
    from cardiocode.guidelines.heart_failure.treatment import get_hfref_treatment
    hf_recs = get_hfref_treatment(patient)
    print(hf_recs.format_for_display())
    
    # Get AF anticoagulation recommendations
    print("\n--- AF Anticoagulation Recommendations ---")
    from cardiocode.guidelines.atrial_fibrillation.stroke_prevention import (
        get_anticoagulation_recommendation
    )
    af_recs = get_anticoagulation_recommendation(patient)
    print(af_recs.format_for_display())


# =============================================================================
# EXAMPLE 2: Acute Chest Pain - Suspected ACS
# =============================================================================

def example_acs_patient():
    """
    Example: 65-year-old female with chest pain and elevated troponin
    """
    print("\n" + "="*60)
    print("EXAMPLE 2: Suspected NSTE-ACS")
    print("="*60)
    
    patient = Patient(
        age=65,
        sex=Sex.FEMALE,
        
        vitals=VitalSigns(
            heart_rate=92,
            systolic_bp=145,
            diastolic_bp=88,
        ),
        
        labs=LabValues(
            troponin_t=85,  # ng/L - elevated
            creatinine=1.0,
            egfr=62,
        ),
        
        ecg=ECGFindings(
            rhythm=RhythmType.SINUS,
            st_depression=["V4", "V5", "V6"],  # Ischemic changes
        ),
        
        has_diabetes=True,
        has_hypertension=True,
    )
    
    print(f"\nPatient: {patient.age}yo {patient.sex.value}")
    print(f"Troponin T: {patient.labs.troponin_t} ng/L")
    print(f"ECG: ST depression in {patient.ecg.st_depression}")
    
    # Diagnose ACS
    print("\n--- ACS Diagnosis ---")
    from cardiocode.guidelines.acs_nstemi.diagnosis import diagnose_nste_acs
    dx = diagnose_nste_acs(patient)
    print(f"Diagnosis: {dx.diagnosis}")
    print(f"Troponin outcome: {dx.troponin_outcome.value}")
    for rec in dx.recommendations:
        print(f"\n{rec.format_for_display()}")
    
    # Risk stratification
    print("\n--- Risk Stratification ---")
    from cardiocode.guidelines.acs_nstemi.risk_stratification import stratify_risk
    risk = stratify_risk(patient)
    print(f"Risk category: {risk.risk_category.upper()}")
    print(f"Invasive timing: {risk.invasive_timing}")
    if risk.grace_score:
        print(f"GRACE score: {risk.grace_score}")
    for rec in risk.recommendations:
        print(f"\n{rec.format_for_display()}")


# =============================================================================
# EXAMPLE 3: Check for New Guidelines
# =============================================================================

def example_check_new_pdfs():
    """
    Example: Check for new guideline PDFs and generate expansion prompts
    """
    print("\n" + "="*60)
    print("EXAMPLE 3: Knowledge Expansion System")
    print("="*60)
    
    from cardiocode.ingestion import check_for_new_pdfs
    
    print("\nChecking for new PDFs in source_pdfs/...")
    new_pdfs = check_for_new_pdfs("source_pdfs")
    
    if new_pdfs:
        print(f"\nFound {len(new_pdfs)} new PDF(s):")
        for pdf in new_pdfs:
            print(f"  - {pdf['filename']}")
            if pdf['guideline_type']:
                print(f"    Identified as: {pdf['guideline_type']}")
            else:
                print(f"    Type: Unknown (needs manual classification)")
    else:
        print("\nNo new PDFs detected.")
    
    # Show watcher status
    from cardiocode.ingestion.pdf_watcher import GuidelineWatcher
    watcher = GuidelineWatcher("source_pdfs")
    print("\n" + watcher.get_status_report())


# =============================================================================
# EXAMPLE 4: Multi-Guideline Query (Synthesis)
# =============================================================================

def example_synthesis():
    """
    Example: Patient with multiple conditions requiring guideline synthesis
    """
    print("\n" + "="*60)
    print("EXAMPLE 4: Multi-Guideline Synthesis")
    print("="*60)
    
    # Patient with HF, AF, and recent ACS
    patient = Patient(
        age=70,
        sex=Sex.MALE,
        lvef=35,
        nyha_class=NYHAClass.II,
        af_type=AFType.PERSISTENT,
        has_cad=True,
        has_diabetes=True,
        has_hypertension=True,
        on_anticoagulation=True,  # Already on DOAC for AF
    )
    
    print(f"\nComplex patient: HFrEF + AF + recent ACS")
    print(f"LVEF: {patient.lvef}%, NYHA: {patient.nyha_class.value}")
    print(f"On anticoagulation: {patient.on_anticoagulation}")
    
    # This patient needs guidance from:
    # 1. HF guideline (GDMT)
    # 2. AF guideline (anticoagulation)
    # 3. ACS guideline (antiplatelets post-PCI)
    
    print("\n--- Integrated Recommendations ---")
    print("NOTE: This requires multi-guideline synthesis")
    
    # HF treatment
    from cardiocode.guidelines.heart_failure.treatment import get_hfref_treatment
    hf_recs = get_hfref_treatment(patient)
    print(f"\nFrom ESC HF 2021:")
    print(f"  - {hf_recs.count} recommendations")
    
    # AF anticoagulation - already on OAC
    print(f"\nFrom ESC AF 2020:")
    print(f"  - Continue DOAC for stroke prevention")
    print(f"  - If recent PCI: Use clopidogrel (not ticagrelor/prasugrel) with OAC")
    
    # The real synthesis happens here
    from cardiocode.reasoning.synthesizer import ClinicalReasoner
    reasoner = ClinicalReasoner()
    result = reasoner.reason(
        patient=patient,
        question="What is the optimal antithrombotic regimen for this patient with HFrEF, AF on DOAC, and recent PCI?",
    )
    print(f"\n{result.format_for_display()}")


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                     CARDIOCODE                            ║
    ║         ESC Guidelines as Executable Code                 ║
    ╠═══════════════════════════════════════════════════════════╣
    ║  DISCLAIMER: This is decision SUPPORT, not MAKING.        ║
    ║  All recommendations require clinical validation.         ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    # Run examples
    example_hf_af_patient()
    example_acs_patient()
    example_check_new_pdfs()
    example_synthesis()
    
    print("\n" + "="*60)
    print("Examples complete. See code for implementation details.")
    print("="*60)
