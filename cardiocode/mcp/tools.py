"""
CardioCode MCP Tools.

All tools exposed via the MCP server.
"""

from __future__ import annotations
import json
from typing import Dict, Any, List, Optional, Union

# Import calculator modules
from cardiocode.calculators import (
    calculate_pesi,
    calculate_spesi,
    calculate_geneva_pe,
    calculate_age_adjusted_ddimer,
    calculate_pah_baseline_risk,
    calculate_pah_followup_risk,
    classify_ph_hemodynamics,
    calculate_maggic_score,
    assess_iron_deficiency_hf,
    classify_hf_phenotype,
    calculate_lmna_risk,
    calculate_lqts_risk,
    calculate_brugada_risk,
)

# Import assessment modules
from cardiocode.assessments import (
    assess_ar_severity,
    assess_mr_primary_intervention,
    assess_mr_secondary_teer,
    assess_tr_intervention,
    assess_ms_intervention,
    assess_valve_type_selection,
    calculate_inr_target_mhv,
    assess_crt_indication,
    assess_dcm_icd_indication,
    assess_arvc_icd_indication,
    assess_sarcoidosis_icd_indication,
    assess_pacing_indication,
    select_pacing_mode,
    assess_pe_risk_stratification,
    assess_pe_thrombolysis,
    assess_pe_outpatient_eligibility,
    calculate_vte_recurrence_risk,
    assess_cardio_oncology_baseline_risk,
    assess_ctrcd_severity,
    get_surveillance_protocol,
    assess_syncope_risk,
    classify_syncope_etiology,
    diagnose_orthostatic_hypotension,
    assess_tilt_test_indication,
)

# Import pathway modules
from cardiocode.pathways import (
    pathway_hfref_treatment,
    pathway_hf_device_therapy,
    get_hf_medication_targets,
    pathway_vt_acute_management,
    pathway_electrical_storm,
    pathway_vt_chronic_management,
    pathway_pe_treatment,
    pathway_pe_anticoagulation_duration,
    pathway_syncope_evaluation,
    pathway_syncope_disposition,
)

# =============================================================================
# TYPE CONVERSION HELPERS (MCP passes strings)
# =============================================================================

def _to_bool(value: Union[str, bool, None], default: bool = False) -> bool:
    """Convert string/bool to bool."""
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ("true", "1", "yes", "y")
    return bool(value)


def _to_int(value: Union[str, int, None], default: Optional[int] = 0) -> Optional[int]:
    """Convert string/int to int."""
    if value is None:
        return default
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            return default
    return default


def _to_float(value: Union[str, float, int, None], default: Optional[float] = 0.0) -> Optional[float]:
    """Convert string/float to float."""
    if value is None:
        return default
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return default
    return default


# =============================================================================
# CLINICAL SCORE TOOLS
# =============================================================================

def tool_calculate_cha2ds2_vasc(
    age: str,
    female: str,
    chf: str = "false",
    hypertension: str = "false",
    stroke_tia: str = "false",
    vascular_disease: str = "false",
    diabetes: str = "false",
) -> Dict[str, Any]:
    """
    Calculate CHA2DS2-VASc score for stroke risk in atrial fibrillation.
    
    Args:
        age: Patient age in years
        female: Female sex (true/false)
        chf: Congestive heart failure (true/false)
        hypertension: Hypertension (true/false)
        stroke_tia: Prior stroke/TIA/thromboembolism (true/false)
        vascular_disease: Vascular disease - MI, PAD, aortic plaque (true/false)
        diabetes: Diabetes mellitus (true/false)
    
    Returns:
        Score with interpretation and recommendation
    """
    age_val = _to_int(age, 65)
    is_female = _to_bool(female)
    
    score = 0
    components = {}
    
    # Age points
    if age_val >= 75:
        score += 2
        components["age_75_plus"] = 2
    elif age_val >= 65:
        score += 1
        components["age_65_74"] = 1
    
    # Sex
    if is_female:
        score += 1
        components["female"] = 1
    
    # Risk factors
    if _to_bool(chf):
        score += 1
        components["chf"] = 1
    if _to_bool(hypertension):
        score += 1
        components["hypertension"] = 1
    if _to_bool(stroke_tia):
        score += 2
        components["stroke_tia"] = 2
    if _to_bool(vascular_disease):
        score += 1
        components["vascular_disease"] = 1
    if _to_bool(diabetes):
        score += 1
        components["diabetes"] = 1
    
    # Interpretation
    if score == 0:
        risk = "Low"
        recommendation = "Anticoagulation generally not recommended"
    elif score == 1:
        risk = "Low-Moderate"
        if is_female and score == 1:
            recommendation = "Anticoagulation generally not recommended (score is 1 due to female sex alone)"
        else:
            recommendation = "Consider anticoagulation based on individual risk-benefit assessment"
    else:
        risk = "Moderate-High"
        recommendation = "Anticoagulation recommended (Class I, Level A)"
    
    return {
        "score": score,
        "max_score": 9,
        "risk_category": risk,
        "recommendation": recommendation,
        "components": components,
        "source": "ESC 2020 AF Guidelines"
    }


def tool_calculate_has_bled(
    hypertension_uncontrolled: str = "false",
    abnormal_renal: str = "false",
    abnormal_liver: str = "false",
    stroke_history: str = "false",
    bleeding_history: str = "false",
    labile_inr: str = "false",
    age_over_65: str = "false",
    drugs_predisposing: str = "false",
    alcohol_excess: str = "false",
) -> Dict[str, Any]:
    """
    Calculate HAS-BLED bleeding risk score.
    
    Args:
        hypertension_uncontrolled: Uncontrolled hypertension SBP > 160 (true/false)
        abnormal_renal: Dialysis, transplant, Cr > 2.26 mg/dL (true/false)
        abnormal_liver: Cirrhosis or bilirubin > 2x + AST/ALT > 3x (true/false)
        stroke_history: Prior stroke (true/false)
        bleeding_history: Prior major bleeding or predisposition (true/false)
        labile_inr: Unstable/high INRs, TTR < 60% (true/false)
        age_over_65: Age > 65 years (true/false)
        drugs_predisposing: Antiplatelet agents or NSAIDs (true/false)
        alcohol_excess: >= 8 drinks/week (true/false)
    
    Returns:
        Score with interpretation
    """
    score = 0
    components = {}
    
    if _to_bool(hypertension_uncontrolled):
        score += 1
        components["hypertension"] = 1
    if _to_bool(abnormal_renal):
        score += 1
        components["abnormal_renal"] = 1
    if _to_bool(abnormal_liver):
        score += 1
        components["abnormal_liver"] = 1
    if _to_bool(stroke_history):
        score += 1
        components["stroke"] = 1
    if _to_bool(bleeding_history):
        score += 1
        components["bleeding"] = 1
    if _to_bool(labile_inr):
        score += 1
        components["labile_inr"] = 1
    if _to_bool(age_over_65):
        score += 1
        components["elderly"] = 1
    if _to_bool(drugs_predisposing):
        score += 1
        components["drugs"] = 1
    if _to_bool(alcohol_excess):
        score += 1
        components["alcohol"] = 1
    
    if score >= 3:
        risk = "High"
        interpretation = "High bleeding risk - requires caution and regular review"
    elif score >= 1:
        risk = "Moderate"
        interpretation = "Moderate bleeding risk - address modifiable risk factors"
    else:
        risk = "Low"
        interpretation = "Low bleeding risk"
    
    return {
        "score": score,
        "max_score": 9,
        "risk_category": risk,
        "interpretation": interpretation,
        "recommendation": "Address modifiable risk factors. HAS-BLED >= 3 does NOT contraindicate anticoagulation.",
        "components": components,
        "source": "ESC 2020 AF Guidelines"
    }


def tool_calculate_grace_score(
    age: str,
    heart_rate: str,
    systolic_bp: str,
    creatinine: str,
    killip_class: str = "1",
    cardiac_arrest: str = "false",
    st_deviation: str = "false",
    elevated_troponin: str = "false",
) -> Dict[str, Any]:
    """
    Calculate GRACE score for ACS risk stratification.
    
    Args:
        age: Age in years
        heart_rate: Heart rate (bpm)
        systolic_bp: Systolic blood pressure (mmHg)
        creatinine: Serum creatinine (mg/dL)
        killip_class: Killip class 1-4
        cardiac_arrest: Cardiac arrest at admission (true/false)
        st_deviation: ST-segment deviation (true/false)
        elevated_troponin: Elevated cardiac troponin (true/false)
    
    Returns:
        GRACE score with mortality risk
    """
    age_val = _to_int(age, 65)
    hr = _to_int(heart_rate, 80)
    sbp = _to_int(systolic_bp, 120)
    cr = _to_float(creatinine, 1.0)
    killip = _to_int(killip_class, 1)
    
    # Simplified GRACE 2.0 calculation
    score = 0
    
    # Age component
    if age_val < 30:
        score += 0
    elif age_val < 40:
        score += 8
    elif age_val < 50:
        score += 25
    elif age_val < 60:
        score += 41
    elif age_val < 70:
        score += 58
    elif age_val < 80:
        score += 75
    else:
        score += 91
    
    # Heart rate
    if hr < 50:
        score += 0
    elif hr < 70:
        score += 3
    elif hr < 90:
        score += 9
    elif hr < 110:
        score += 15
    elif hr < 150:
        score += 24
    else:
        score += 38
    
    # Systolic BP
    if sbp < 80:
        score += 58
    elif sbp < 100:
        score += 53
    elif sbp < 120:
        score += 43
    elif sbp < 140:
        score += 34
    elif sbp < 160:
        score += 24
    else:
        score += 0
    
    # Creatinine (simplified)
    if cr < 0.4:
        score += 1
    elif cr < 0.8:
        score += 4
    elif cr < 1.2:
        score += 7
    elif cr < 2.0:
        score += 10
    elif cr < 4.0:
        score += 13
    else:
        score += 28
    
    # Killip class
    killip_scores = {1: 0, 2: 20, 3: 39, 4: 59}
    score += killip_scores.get(killip, 0)
    
    # Binary factors
    if _to_bool(cardiac_arrest):
        score += 39
    if _to_bool(st_deviation):
        score += 28
    if _to_bool(elevated_troponin):
        score += 14
    
    # Risk category
    if score <= 108:
        risk = "Low"
        mortality = "<1%"
    elif score <= 140:
        risk = "Intermediate"
        mortality = "1-3%"
    else:
        risk = "High"
        mortality = ">3%"
    
    return {
        "score": score,
        "risk_category": risk,
        "in_hospital_mortality": mortality,
        "recommendation": f"{'Early invasive strategy recommended' if risk == 'High' else 'Risk-guided approach'}",
        "source": "ESC 2020 NSTE-ACS Guidelines"
    }


def tool_calculate_wells_pe(
    clinical_signs_dvt: str = "false",
    pe_most_likely: str = "false",
    heart_rate_above_100: str = "false",
    immobilization_surgery: str = "false",
    previous_pe_dvt: str = "false",
    hemoptysis: str = "false",
    malignancy: str = "false",
) -> Dict[str, Any]:
    """
    Calculate Wells score for pulmonary embolism probability.
    
    Args:
        clinical_signs_dvt: Clinical signs/symptoms of DVT (true/false)
        pe_most_likely: PE is #1 diagnosis or equally likely (true/false)
        heart_rate_above_100: Heart rate > 100 bpm (true/false)
        immobilization_surgery: Immobilization or surgery in past 4 weeks (true/false)
        previous_pe_dvt: Previous PE or DVT (true/false)
        hemoptysis: Hemoptysis (true/false)
        malignancy: Malignancy with treatment in 6 months or palliative (true/false)
    
    Returns:
        Wells score with PE probability
    """
    score = 0.0
    components = {}
    
    if _to_bool(clinical_signs_dvt):
        score += 3.0
        components["clinical_dvt"] = 3.0
    if _to_bool(pe_most_likely):
        score += 3.0
        components["pe_likely"] = 3.0
    if _to_bool(heart_rate_above_100):
        score += 1.5
        components["tachycardia"] = 1.5
    if _to_bool(immobilization_surgery):
        score += 1.5
        components["immobilization"] = 1.5
    if _to_bool(previous_pe_dvt):
        score += 1.5
        components["previous_vte"] = 1.5
    if _to_bool(hemoptysis):
        score += 1.0
        components["hemoptysis"] = 1.0
    if _to_bool(malignancy):
        score += 1.0
        components["malignancy"] = 1.0
    
    # Two-level classification
    if score <= 4:
        probability = "PE Unlikely"
        next_step = "D-dimer testing; if negative, PE excluded"
    else:
        probability = "PE Likely"
        next_step = "CTPA recommended"
    
    return {
        "score": score,
        "max_score": 12.5,
        "probability": probability,
        "recommendation": next_step,
        "components": components,
        "source": "ESC 2019 PE Guidelines"
    }


def tool_calculate_hcm_scd_risk(
    age: str,
    max_wall_thickness: str,
    la_diameter: str,
    max_lvot_gradient: str,
    family_history_scd: str = "false",
    nsvt: str = "false",
    unexplained_syncope: str = "false",
) -> Dict[str, Any]:
    """
    Calculate 5-year sudden cardiac death risk in HCM (ESC HCM Risk-SCD).
    
    Args:
        age: Age 16-80 years
        max_wall_thickness: Maximum LV wall thickness in mm
        la_diameter: Left atrial diameter in mm
        max_lvot_gradient: Maximum LVOT gradient at rest/Valsalva in mmHg
        family_history_scd: Family history of SCD in 1st degree relative < 40y (true/false)
        nsvt: Non-sustained VT on Holter (true/false)
        unexplained_syncope: Unexplained syncope (true/false)
    
    Returns:
        5-year SCD risk percentage and ICD recommendation
    """
    import math
    
    age_val = _to_int(age, 50)
    mwt = _to_float(max_wall_thickness, 15)
    la = _to_float(la_diameter, 40)
    grad = _to_float(max_lvot_gradient, 10)
    fh = 1 if _to_bool(family_history_scd) else 0
    nsvt_val = 1 if _to_bool(nsvt) else 0
    sync = 1 if _to_bool(unexplained_syncope) else 0
    
    # HCM Risk-SCD formula
    # Prognostic index
    pi = (0.15939858 * mwt - 
          0.00294271 * mwt * mwt +
          0.0259082 * la +
          0.00446131 * grad +
          0.4583082 * fh +
          0.82639195 * nsvt_val +
          0.71650361 * sync -
          0.01799934 * age_val)
    
    # 5-year probability
    risk_5yr = 1 - (0.998 ** math.exp(pi))
    risk_percent = risk_5yr * 100
    
    # ICD recommendation
    if risk_percent >= 6:
        recommendation = "ICD should be considered (Class IIa)"
        risk_category = "High"
    elif risk_percent >= 4:
        recommendation = "ICD may be considered (Class IIb)"
        risk_category = "Intermediate"
    else:
        recommendation = "ICD generally not indicated based on risk score alone"
        risk_category = "Low"
    
    return {
        "risk_5_year_percent": round(risk_percent, 1),
        "risk_category": risk_category,
        "recommendation": recommendation,
        "components": {
            "age": age_val,
            "max_wall_thickness_mm": mwt,
            "la_diameter_mm": la,
            "max_lvot_gradient_mmHg": grad,
            "family_history_scd": bool(fh),
            "nsvt": bool(nsvt_val),
            "unexplained_syncope": bool(sync),
        },
        "source": "ESC 2014/2022 HCM Guidelines"
    }


# =============================================================================
# NEW CALCULATOR TOOLS (PE, PAH, HF, ARRHYTHMIA)
# =============================================================================

def tool_calculate_pesi(
    age: str,
    male: str = "false",
    cancer: str = "false",
    heart_failure: str = "false",
    chronic_lung_disease: str = "false",
    pulse_rate: str = "80",
    systolic_bp: str = "120",
    respiratory_rate: str = "16",
    temperature: str = "37.0",
    altered_mental_status: str = "false",
    o2_saturation: str = "98.0",
) -> Dict[str, Any]:
    """Calculate Pulmonary Embolism Severity Index (PESI) score for 30-day mortality."""
    return calculate_pesi(
        age=_to_int(age, 65),
        male=_to_bool(male),
        cancer=_to_bool(cancer),
        heart_failure=_to_bool(heart_failure),
        chronic_lung_disease=_to_bool(chronic_lung_disease),
        pulse_rate=_to_int(pulse_rate, 80),
        systolic_bp=_to_int(systolic_bp, 120),
        respiratory_rate=_to_int(respiratory_rate, 16),
        temperature=_to_float(temperature, 37.0),
        altered_mental_status=_to_bool(altered_mental_status),
        o2_saturation=_to_float(o2_saturation, 98.0),
    )


def tool_calculate_spesi(
    age_over_80: str = "false",
    cancer: str = "false",
    chronic_cardiopulmonary_disease: str = "false",
    pulse_over_110: str = "false",
    systolic_bp_under_100: str = "false",
    o2_saturation_under_90: str = "false",
) -> Dict[str, Any]:
    """Calculate Simplified PESI (sPESI) score for PE risk stratification."""
    return calculate_spesi(
        age_over_80=_to_bool(age_over_80),
        cancer=_to_bool(cancer),
        chronic_cardiopulmonary_disease=_to_bool(chronic_cardiopulmonary_disease),
        pulse_over_110=_to_bool(pulse_over_110),
        systolic_bp_under_100=_to_bool(systolic_bp_under_100),
        o2_saturation_under_90=_to_bool(o2_saturation_under_90),
    )


def tool_calculate_geneva_pe(
    previous_pe_dvt: str = "false",
    heart_rate: str = "80",
    surgery_fracture_past_month: str = "false",
    hemoptysis: str = "false",
    active_cancer: str = "false",
    unilateral_leg_pain: str = "false",
    dvt_signs: str = "false",
    age_over_65: str = "false",
    simplified: str = "true",
) -> Dict[str, Any]:
    """Calculate Revised Geneva Score for PE pre-test probability."""
    return calculate_geneva_pe(
        previous_pe_dvt=_to_bool(previous_pe_dvt),
        heart_rate=_to_int(heart_rate, 80),
        surgery_fracture_past_month=_to_bool(surgery_fracture_past_month),
        hemoptysis=_to_bool(hemoptysis),
        active_cancer=_to_bool(active_cancer),
        unilateral_leg_pain=_to_bool(unilateral_leg_pain),
        dvt_signs=_to_bool(dvt_signs),
        age_over_65=_to_bool(age_over_65),
        simplified=_to_bool(simplified),
    )


def tool_calculate_age_adjusted_ddimer(
    age: str,
    baseline_cutoff: str = "500",
) -> Dict[str, Any]:
    """Calculate age-adjusted D-dimer cutoff for PE exclusion."""
    return calculate_age_adjusted_ddimer(
        age=_to_int(age, 50),
        baseline_cutoff=_to_int(baseline_cutoff, 500),
    )


def tool_calculate_pah_baseline_risk(
    who_functional_class: str,
    six_min_walk_distance: str = "",
    bnp: str = "",
    nt_probnp: str = "",
    ra_area: str = "",
    pericardial_effusion: str = "none",
    cardiac_index: str = "",
    svo2: str = "",
    rv_failure_signs: str = "false",
    symptom_progression: str = "stable",
    syncope: str = "none",
) -> Dict[str, Any]:
    """Calculate PAH baseline risk using 3-strata model for 1-year mortality."""
    return calculate_pah_baseline_risk(
        who_functional_class=_to_int(who_functional_class, 2),
        six_min_walk_distance=_to_int(six_min_walk_distance, None) if six_min_walk_distance else None,
        bnp=_to_float(bnp, None) if bnp else None,
        nt_probnp=_to_float(nt_probnp, None) if nt_probnp else None,
        ra_area=_to_float(ra_area, None) if ra_area else None,
        pericardial_effusion=pericardial_effusion,
        cardiac_index=_to_float(cardiac_index, None) if cardiac_index else None,
        svo2=_to_float(svo2, None) if svo2 else None,
        rv_failure_signs=_to_bool(rv_failure_signs),
        symptom_progression=symptom_progression,
        syncope=syncope,
    )


def tool_calculate_pah_followup_risk(
    who_functional_class: str,
    six_min_walk_distance: str = "",
    bnp: str = "",
    nt_probnp: str = "",
) -> Dict[str, Any]:
    """Calculate PAH follow-up risk using simplified 4-strata model."""
    return calculate_pah_followup_risk(
        who_functional_class=_to_int(who_functional_class, 2),
        six_min_walk_distance=_to_int(six_min_walk_distance, None) if six_min_walk_distance else None,
        bnp=_to_float(bnp, None) if bnp else None,
        nt_probnp=_to_float(nt_probnp, None) if nt_probnp else None,
    )


def tool_classify_ph_hemodynamics(
    mean_pap: str,
    pawp: str,
    pvr: str,
    cardiac_output: str = "",
) -> Dict[str, Any]:
    """Classify pulmonary hypertension by hemodynamic definitions."""
    return classify_ph_hemodynamics(
        mean_pap=_to_float(mean_pap, 25),
        pawp=_to_float(pawp, 12),
        pvr=_to_float(pvr, 3),
        cardiac_output=_to_float(cardiac_output, None) if cardiac_output else None,
    )


def tool_calculate_maggic_score(
    age: str,
    male: str,
    lvef: str,
    nyha_class: str,
    systolic_bp: str,
    bmi: str,
    creatinine: str,
    current_smoker: str = "false",
    diabetes: str = "false",
    copd: str = "false",
    hf_diagnosis_18_months: str = "true",
    on_beta_blocker: str = "false",
    on_acei_arb: str = "false",
) -> Dict[str, Any]:
    """Calculate MAGGIC score for HF mortality prognosis."""
    return calculate_maggic_score(
        age=_to_int(age, 65),
        male=_to_bool(male),
        lvef=_to_float(lvef, 35),
        nyha_class=_to_int(nyha_class, 2),
        systolic_bp=_to_int(systolic_bp, 120),
        bmi=_to_float(bmi, 25),
        creatinine=_to_float(creatinine, 1.2),
        current_smoker=_to_bool(current_smoker),
        diabetes=_to_bool(diabetes),
        copd=_to_bool(copd),
        hf_diagnosis_18_months=_to_bool(hf_diagnosis_18_months),
        on_beta_blocker=_to_bool(on_beta_blocker),
        on_acei_arb=_to_bool(on_acei_arb),
    )


def tool_assess_iron_deficiency_hf(
    ferritin: str,
    transferrin_saturation: str,
    hemoglobin: str = "",
    symptomatic_hf: str = "true",
    lvef: str = "",
) -> Dict[str, Any]:
    """Assess iron deficiency in heart failure patients."""
    return assess_iron_deficiency_hf(
        ferritin=_to_float(ferritin, 100),
        transferrin_saturation=_to_float(transferrin_saturation, 20),
        hemoglobin=_to_float(hemoglobin, None) if hemoglobin else None,
        symptomatic_hf=_to_bool(symptomatic_hf),
        lvef=_to_float(lvef, None) if lvef else None,
    )


def tool_classify_hf_phenotype(
    lvef: str,
    bnp: str = "",
    nt_probnp: str = "",
    structural_abnormality: str = "false",
    diastolic_dysfunction: str = "false",
) -> Dict[str, Any]:
    """Classify heart failure phenotype (HFrEF, HFmrEF, HFpEF) by LVEF."""
    return classify_hf_phenotype(
        lvef=_to_float(lvef, 45),
        bnp=_to_float(bnp, None) if bnp else None,
        nt_probnp=_to_float(nt_probnp, None) if nt_probnp else None,
        structural_abnormality=_to_bool(structural_abnormality),
        diastolic_dysfunction=_to_bool(diastolic_dysfunction),
    )


def tool_calculate_lmna_risk(
    lvef: str,
    nsvt: str = "false",
    male: str = "false",
    av_conduction_delay: str = "false",
) -> Dict[str, Any]:
    """Calculate 5-year VA risk in LMNA mutation carriers."""
    return calculate_lmna_risk(
        lvef=_to_float(lvef, 50),
        nsvt=_to_bool(nsvt),
        male=_to_bool(male),
        av_conduction_delay=_to_bool(av_conduction_delay),
    )


def tool_calculate_lqts_risk(
    qtc: str,
    genotype: str = "unknown",
    male: str = "false",
    age: str = "30",
    prior_syncope: str = "false",
    prior_cardiac_arrest: str = "false",
) -> Dict[str, Any]:
    """Estimate arrhythmic risk in Long QT Syndrome."""
    return calculate_lqts_risk(
        qtc=_to_int(qtc, 450),
        genotype=genotype,
        male=_to_bool(male),
        age=_to_int(age, 30),
        prior_syncope=_to_bool(prior_syncope),
        prior_cardiac_arrest=_to_bool(prior_cardiac_arrest),
    )


def tool_calculate_brugada_risk(
    spontaneous_type1: str = "false",
    induced_type1_only: str = "false",
    prior_cardiac_arrest: str = "false",
    documented_vt_vf: str = "false",
    syncope_suspected_arrhythmic: str = "false",
    family_history_scd: str = "false",
    male: str = "false",
) -> Dict[str, Any]:
    """Risk stratification in Brugada Syndrome."""
    return calculate_brugada_risk(
        spontaneous_type1=_to_bool(spontaneous_type1),
        induced_type1_only=_to_bool(induced_type1_only),
        prior_cardiac_arrest=_to_bool(prior_cardiac_arrest),
        documented_vt_vf=_to_bool(documented_vt_vf),
        syncope_suspected_arrhythmic=_to_bool(syncope_suspected_arrhythmic),
        family_history_scd=_to_bool(family_history_scd),
        male=_to_bool(male),
    )


# =============================================================================
# ASSESSMENT TOOLS
# =============================================================================

def tool_assess_aortic_stenosis(
    peak_velocity: str,
    mean_gradient: str,
    ava: str,
    lvef: str = "",
    stroke_volume_index: str = "",
) -> Dict[str, Any]:
    """
    Assess aortic stenosis severity and intervention indication.
    
    Args:
        peak_velocity: Peak aortic jet velocity in m/s
        mean_gradient: Mean transvalvular gradient in mmHg
        ava: Aortic valve area in cm2
        lvef: LV ejection fraction in % (optional)
        stroke_volume_index: Stroke volume index in mL/m2 (optional)
    
    Returns:
        AS severity assessment with intervention recommendation
    """
    vmax = _to_float(peak_velocity, 4.0)
    mg = _to_float(mean_gradient, 40)
    valve_area = _to_float(ava, 1.0)
    ef = _to_float(lvef, 60) if lvef else None
    svi = _to_float(stroke_volume_index, 35) if stroke_volume_index else None
    
    # Determine severity
    if vmax >= 4.0 and mg >= 40 and valve_area < 1.0:
        severity = "Severe (high-gradient)"
        severity_code = "severe_high_gradient"
    elif valve_area < 1.0 and mg < 40:
        if ef and ef < 50:
            severity = "Severe (low-flow, low-gradient, reduced EF)"
            severity_code = "severe_lflg_ref"
        elif svi and svi < 35:
            severity = "Severe (paradoxical low-flow, low-gradient)"
            severity_code = "severe_paradoxical_lflg"
        else:
            severity = "Moderate (or pseudo-severe)"
            severity_code = "moderate"
    elif vmax >= 3.0 or mg >= 20:
        severity = "Moderate"
        severity_code = "moderate"
    else:
        severity = "Mild"
        severity_code = "mild"
    
    # Intervention recommendations (simplified from ESC 2021/2025 VHD)
    recommendations = []
    
    if severity_code.startswith("severe"):
        recommendations.append({
            "indication": "Symptomatic severe AS",
            "class": "I",
            "level": "B",
            "action": "AVR (TAVI or SAVR based on Heart Team assessment)"
        })
        
        if ef and ef < 50:
            recommendations.append({
                "indication": "Asymptomatic severe AS with LVEF < 50%",
                "class": "I",
                "level": "B",
                "action": "AVR recommended"
            })
        
        if vmax >= 5.0:
            recommendations.append({
                "indication": "Asymptomatic very severe AS (Vmax >= 5 m/s)",
                "class": "IIa",
                "level": "B",
                "action": "AVR should be considered if low procedural risk"
            })
    
    return {
        "severity": severity,
        "parameters": {
            "peak_velocity_m_s": vmax,
            "mean_gradient_mmHg": mg,
            "valve_area_cm2": valve_area,
            "lvef_percent": ef,
            "svi_ml_m2": svi,
        },
        "recommendations": recommendations,
        "notes": [
            "Low-flow defined as SVI < 35 mL/m2",
            "Low-gradient defined as mean gradient < 40 mmHg",
            "For low-flow low-gradient AS, dobutamine stress echo or CT calcium scoring recommended"
        ],
        "source": "ESC/EACTS 2021/2025 VHD Guidelines"
    }


def tool_assess_icd_indication(
    lvef: str,
    nyha_class: str,
    etiology: str = "ischemic",
    prior_vf_vt: str = "false",
    syncope: str = "false",
    days_post_mi: str = "",
) -> Dict[str, Any]:
    """
    Assess ICD indication for sudden cardiac death prevention.
    
    Args:
        lvef: LV ejection fraction in %
        nyha_class: NYHA functional class 1-4
        etiology: ischemic, non_ischemic, hcm, arvc
        prior_vf_vt: Prior VF or sustained VT (true/false)
        syncope: Unexplained syncope (true/false)
        days_post_mi: Days since MI (if applicable)
    
    Returns:
        ICD indication assessment
    """
    ef = _to_float(lvef, 35)
    nyha = _to_int(nyha_class, 2)
    prior_arrhythmia = _to_bool(prior_vf_vt)
    has_syncope = _to_bool(syncope)
    post_mi_days = _to_int(days_post_mi, 90) if days_post_mi else None
    
    indication = "none"
    recommendation_class = ""
    rationale = []
    
    # Secondary prevention (prior VF/VT)
    if prior_arrhythmia:
        indication = "secondary_prevention"
        recommendation_class = "I"
        rationale.append("Prior VF or sustained VT - secondary prevention ICD (Class I)")
    
    # Primary prevention - ischemic
    elif etiology == "ischemic":
        if post_mi_days and post_mi_days < 40:
            indication = "defer"
            rationale.append("< 40 days post-MI - reassess LVEF at 6-12 weeks")
        elif ef <= 35 and nyha in [2, 3]:
            indication = "primary_prevention"
            recommendation_class = "I"
            rationale.append("Ischemic CM, LVEF <= 35%, NYHA II-III - ICD recommended (Class I)")
        elif ef <= 30 and nyha == 1:
            indication = "primary_prevention"
            recommendation_class = "I"
            rationale.append("Ischemic CM, LVEF <= 30%, NYHA I - ICD recommended (Class I)")
    
    # Primary prevention - non-ischemic
    elif etiology == "non_ischemic":
        if ef <= 35 and nyha in [2, 3]:
            indication = "consider"
            recommendation_class = "IIa"
            rationale.append("Non-ischemic CM, LVEF <= 35%, NYHA II-III - ICD should be considered (Class IIa)")
    
    # Syncope consideration
    if has_syncope and ef <= 40:
        rationale.append("Unexplained syncope with reduced EF - additional indication for ICD")
        if indication == "none":
            indication = "consider"
            recommendation_class = "IIa"
    
    return {
        "indication": indication,
        "class": recommendation_class,
        "rationale": rationale,
        "parameters": {
            "lvef_percent": ef,
            "nyha_class": nyha,
            "etiology": etiology,
            "prior_vf_vt": prior_arrhythmia,
            "syncope": has_syncope,
            "days_post_mi": post_mi_days,
        },
        "notes": [
            "Ensure optimal medical therapy for >= 3 months before ICD",
            "Life expectancy > 1 year with good functional status required",
            "CRT-D may be preferred if QRS >= 130ms with LBBB"
        ],
        "source": "ESC 2022 VA/SCD Guidelines"
    }


# =============================================================================
# NEW ASSESSMENT TOOLS (VALVULAR, DEVICES, VTE, CARDIO-ONCOLOGY, SYNCOPE)
# =============================================================================

def tool_assess_ar_severity(
    lvesd: str,
    lvef: str = "60",
    symptomatic: str = "false",
    undergoing_cardiac_surgery: str = "false",
    lvesdi: str = "",
    bsa: str = "",
) -> Dict[str, Any]:
    """Assess aortic regurgitation severity and intervention indication."""
    return assess_ar_severity(
        lvesd=_to_float(lvesd, 50),
        lvef=_to_float(lvef, 60),
        symptomatic=_to_bool(symptomatic),
        undergoing_cardiac_surgery=_to_bool(undergoing_cardiac_surgery),
        lvesdi=_to_float(lvesdi, None) if lvesdi else None,
        bsa=_to_float(bsa, None) if bsa else None,
    )


def tool_assess_mr_primary_intervention(
    lvesd: str,
    lvef: str,
    symptomatic: str = "false",
    af: str = "false",
    spap: str = "",
    lavi: str = "",
    tr_moderate_or_greater: str = "false",
    repair_likely_durable: str = "true",
    surgical_risk: str = "low",
) -> Dict[str, Any]:
    """Assess primary mitral regurgitation intervention indication."""
    return assess_mr_primary_intervention(
        lvesd=_to_float(lvesd, 40),
        lvef=_to_float(lvef, 60),
        symptomatic=_to_bool(symptomatic),
        af=_to_bool(af),
        spap=_to_float(spap, None) if spap else None,
        lavi=_to_float(lavi, None) if lavi else None,
        tr_moderate_or_greater=_to_bool(tr_moderate_or_greater),
        repair_likely_durable=_to_bool(repair_likely_durable),
        surgical_risk=surgical_risk,
    )


def tool_assess_mr_secondary_teer(
    lvef: str,
    symptomatic: str = "true",
    on_gdmt: str = "true",
    crt_if_indicated: str = "true",
    hemodynamically_stable: str = "true",
    mr_severity: str = "severe",
    eroa: str = "",
) -> Dict[str, Any]:
    """Assess secondary (ventricular) MR eligibility for TEER."""
    return assess_mr_secondary_teer(
        lvef=_to_float(lvef, 35),
        symptomatic=_to_bool(symptomatic),
        on_gdmt=_to_bool(on_gdmt),
        crt_if_indicated=_to_bool(crt_if_indicated),
        hemodynamically_stable=_to_bool(hemodynamically_stable),
        mr_severity=mr_severity,
        eroa=_to_float(eroa, None) if eroa else None,
    )


def tool_assess_tr_intervention(
    tr_severity: str,
    primary_or_secondary: str,
    rv_function: str = "normal",
    symptomatic: str = "false",
    rv_dilatation: str = "false",
    left_sided_surgery_planned: str = "false",
    surgical_risk: str = "low",
) -> Dict[str, Any]:
    """Assess tricuspid regurgitation intervention indication."""
    return assess_tr_intervention(
        tr_severity=tr_severity,
        primary_or_secondary=primary_or_secondary,
        rv_function=rv_function,
        symptomatic=_to_bool(symptomatic),
        rv_dilatation=_to_bool(rv_dilatation),
        left_sided_surgery_planned=_to_bool(left_sided_surgery_planned),
        surgical_risk=surgical_risk,
    )


def tool_assess_ms_intervention(
    mva: str,
    symptomatic: str = "false",
    favorable_anatomy_for_pmc: str = "true",
    contraindication_to_pmc: str = "false",
    af: str = "false",
    spap: str = "",
) -> Dict[str, Any]:
    """Assess mitral stenosis intervention indication."""
    return assess_ms_intervention(
        mva=_to_float(mva, 1.5),
        symptomatic=_to_bool(symptomatic),
        favorable_anatomy_for_pmc=_to_bool(favorable_anatomy_for_pmc),
        contraindication_to_pmc=_to_bool(contraindication_to_pmc),
        af=_to_bool(af),
        spap=_to_float(spap, None) if spap else None,
    )


def tool_assess_valve_type_selection(
    age: str,
    valve_position: str,
    oac_contraindicated: str = "false",
    quality_oac_achievable: str = "true",
    high_bleeding_risk: str = "false",
    female_contemplating_pregnancy: str = "false",
) -> Dict[str, Any]:
    """Assess mechanical vs biological valve selection."""
    return assess_valve_type_selection(
        age=_to_int(age, 65),
        valve_position=valve_position,
        oac_contraindicated=_to_bool(oac_contraindicated),
        quality_oac_achievable=_to_bool(quality_oac_achievable),
        high_bleeding_risk=_to_bool(high_bleeding_risk),
        female_contemplating_pregnancy=_to_bool(female_contemplating_pregnancy),
    )


def tool_calculate_inr_target_mhv(
    valve_type: str,
    valve_position: str,
    prothrombotic_factors: str = "false",
) -> Dict[str, Any]:
    """Calculate INR target for mechanical heart valve."""
    return calculate_inr_target_mhv(
        valve_type=valve_type,
        valve_position=valve_position,
        prothrombotic_factors=_to_bool(prothrombotic_factors),
    )


def tool_assess_crt_indication(
    lvef: str,
    qrs_duration: str,
    qrs_morphology: str,
    rhythm: str = "sinus",
    nyha_class: str = "2",
    on_optimal_medical_therapy: str = "true",
    av_block_pacing_indication: str = "false",
    has_icd_indication: str = "false",
) -> Dict[str, Any]:
    """Assess CRT indication based on ESC guidelines."""
    return assess_crt_indication(
        lvef=_to_float(lvef, 35),
        qrs_duration=_to_int(qrs_duration, 120),
        qrs_morphology=qrs_morphology,
        rhythm=rhythm,
        nyha_class=_to_int(nyha_class, 2),
        on_optimal_medical_therapy=_to_bool(on_optimal_medical_therapy),
        av_block_pacing_indication=_to_bool(av_block_pacing_indication),
        has_icd_indication=_to_bool(has_icd_indication),
    )


def tool_assess_dcm_icd_indication(
    lvef: str,
    nyha_class: str,
    months_on_omt: str = "3",
    lmna_mutation: str = "false",
    syncope: str = "false",
    lge_on_cmr: str = "false",
    nsvt: str = "false",
    prior_vt_vf: str = "false",
) -> Dict[str, Any]:
    """Assess ICD indication in dilated cardiomyopathy."""
    return assess_dcm_icd_indication(
        lvef=_to_float(lvef, 35),
        nyha_class=_to_int(nyha_class, 2),
        months_on_omt=_to_int(months_on_omt, 3),
        lmna_mutation=_to_bool(lmna_mutation),
        syncope=_to_bool(syncope),
        lge_on_cmr=_to_bool(lge_on_cmr),
        nsvt=_to_bool(nsvt),
        prior_vt_vf=_to_bool(prior_vt_vf),
    )


def tool_assess_arvc_icd_indication(
    definite_arvc: str,
    rv_dysfunction: str = "none",
    lv_dysfunction: str = "none",
    syncope: str = "false",
    nsvt: str = "false",
    prior_vt_vf: str = "false",
) -> Dict[str, Any]:
    """Assess ICD indication in ARVC."""
    return assess_arvc_icd_indication(
        definite_arvc=_to_bool(definite_arvc),
        rv_dysfunction=rv_dysfunction,
        lv_dysfunction=lv_dysfunction,
        syncope=_to_bool(syncope),
        nsvt=_to_bool(nsvt),
        prior_vt_vf=_to_bool(prior_vt_vf),
    )


def tool_assess_sarcoidosis_icd_indication(
    lvef: str,
    lge_extent: str = "none",
    sustained_vt: str = "false",
    aborted_cardiac_arrest: str = "false",
    syncope: str = "false",
) -> Dict[str, Any]:
    """Assess ICD indication in cardiac sarcoidosis."""
    return assess_sarcoidosis_icd_indication(
        lvef=_to_float(lvef, 50),
        lge_extent=lge_extent,
        sustained_vt=_to_bool(sustained_vt),
        aborted_cardiac_arrest=_to_bool(aborted_cardiac_arrest),
        syncope=_to_bool(syncope),
    )


def tool_assess_pacing_indication(
    avb_degree: str,
    snd_documented: str = "false",
    symptoms_correlated: str = "false",
    sinus_pause_seconds: str = "",
    bifascicular_block: str = "false",
    alternating_bbb: str = "false",
) -> Dict[str, Any]:
    """Assess pacemaker indication."""
    return assess_pacing_indication(
        avb_degree=avb_degree,
        snd_documented=_to_bool(snd_documented),
        symptoms_correlated=_to_bool(symptoms_correlated),
        sinus_pause_seconds=_to_float(sinus_pause_seconds, None) if sinus_pause_seconds else None,
        bifascicular_block=_to_bool(bifascicular_block),
        alternating_bbb=_to_bool(alternating_bbb),
    )


def tool_select_pacing_mode(
    primary_indication: str,
    rhythm: str = "sinus",
    av_conduction_intact: str = "true",
    chronotropic_incompetence: str = "false",
    lvef: str = "55",
) -> Dict[str, Any]:
    """Select appropriate pacing mode."""
    return select_pacing_mode(
        primary_indication=primary_indication,
        rhythm=rhythm,
        av_conduction_intact=_to_bool(av_conduction_intact),
        chronotropic_incompetence=_to_bool(chronotropic_incompetence),
        lvef=_to_float(lvef, 55),
    )


def tool_assess_pe_risk_stratification(
    hemodynamic_status: str,
    pesi_class: str = "",
    spesi_score: str = "",
    rv_dysfunction: str = "false",
    elevated_troponin: str = "false",
) -> Dict[str, Any]:
    """Assess PE risk stratification and management approach."""
    return assess_pe_risk_stratification(
        hemodynamic_status=hemodynamic_status,
        pesi_class=_to_int(pesi_class, None) if pesi_class else None,
        spesi_score=_to_int(spesi_score, None) if spesi_score else None,
        rv_dysfunction=_to_bool(rv_dysfunction),
        elevated_troponin=_to_bool(elevated_troponin),
    )


def tool_assess_pe_thrombolysis(
    risk_category: str,
    hemodynamic_status: str,
) -> Dict[str, Any]:
    """Assess thrombolysis indication for PE."""
    return assess_pe_thrombolysis(
        risk_category=risk_category,
        hemodynamic_status=hemodynamic_status,
    )


def tool_assess_pe_outpatient_eligibility(
    spesi_score: str,
    hemodynamically_stable: str = "true",
    o2_required: str = "false",
    high_bleeding_risk: str = "false",
    social_support_adequate: str = "true",
) -> Dict[str, Any]:
    """Assess eligibility for early discharge/outpatient PE treatment."""
    return assess_pe_outpatient_eligibility(
        spesi_score=_to_int(spesi_score, 0),
        hemodynamically_stable=_to_bool(hemodynamically_stable),
        o2_required=_to_bool(o2_required),
        high_bleeding_risk=_to_bool(high_bleeding_risk),
        social_support_adequate=_to_bool(social_support_adequate),
    )


def tool_calculate_vte_recurrence_risk(
    risk_factor_category: str,
    prior_vte: str = "false",
    male: str = "false",
    elevated_d_dimer_after_anticoag: str = "false",
) -> Dict[str, Any]:
    """Calculate VTE recurrence risk and anticoagulation duration recommendation."""
    return calculate_vte_recurrence_risk(
        risk_factor_category=risk_factor_category,
        prior_vte=_to_bool(prior_vte),
        male=_to_bool(male),
        elevated_d_dimer_after_anticoag=_to_bool(elevated_d_dimer_after_anticoag),
    )


def tool_assess_cardio_oncology_baseline_risk(
    age: str,
    prior_hf_cardiomyopathy: str = "false",
    prior_cad: str = "false",
    baseline_lvef: str = "60",
    hypertension: str = "false",
    diabetes: str = "false",
    prior_anthracycline: str = "false",
    prior_chest_rt: str = "false",
    planned_treatment: str = "anthracycline",
) -> Dict[str, Any]:
    """Assess baseline CV risk before cardiotoxic cancer therapy (HFA-ICOS)."""
    return assess_cardio_oncology_baseline_risk(
        age=_to_int(age, 60),
        prior_hf_cardiomyopathy=_to_bool(prior_hf_cardiomyopathy),
        prior_cad=_to_bool(prior_cad),
        baseline_lvef=_to_float(baseline_lvef, 60),
        hypertension=_to_bool(hypertension),
        diabetes=_to_bool(diabetes),
        prior_anthracycline=_to_bool(prior_anthracycline),
        prior_chest_rt=_to_bool(prior_chest_rt),
        planned_treatment=planned_treatment,
    )


def tool_assess_ctrcd_severity(
    baseline_lvef: str,
    current_lvef: str,
    gls_decline_percent: str = "",
    troponin_elevated: str = "false",
    symptomatic: str = "false",
    treatment_type: str = "anthracycline",
) -> Dict[str, Any]:
    """Assess cancer therapy-related cardiac dysfunction (CTRCD) severity."""
    return assess_ctrcd_severity(
        baseline_lvef=_to_float(baseline_lvef, 60),
        current_lvef=_to_float(current_lvef, 50),
        gls_decline_percent=_to_float(gls_decline_percent, None) if gls_decline_percent else None,
        troponin_elevated=_to_bool(troponin_elevated),
        symptomatic=_to_bool(symptomatic),
        treatment_type=treatment_type,
    )


def tool_get_surveillance_protocol(
    treatment_type: str,
    risk_category: str,
    treatment_phase: str = "during",
) -> Dict[str, Any]:
    """Get surveillance protocol for cardiotoxic cancer therapy."""
    return get_surveillance_protocol(
        treatment_type=treatment_type,
        risk_category=risk_category,
        treatment_phase=treatment_phase,
    )


def tool_assess_syncope_risk(
    syncope_during_exertion: str = "false",
    syncope_supine: str = "false",
    syncope_without_prodrome: str = "false",
    palpitations_before_syncope: str = "false",
    structural_heart_disease: str = "false",
    known_coronary_disease: str = "false",
    mobitz_ii_or_complete_avb: str = "false",
    vt_or_rapid_svt: str = "false",
    bifascicular_block: str = "false",
    typical_vasovagal_prodrome: str = "false",
    absence_of_heart_disease: str = "true",
) -> Dict[str, Any]:
    """Assess syncope risk and disposition recommendation."""
    return assess_syncope_risk(
        syncope_during_exertion=_to_bool(syncope_during_exertion),
        syncope_supine=_to_bool(syncope_supine),
        syncope_without_prodrome=_to_bool(syncope_without_prodrome),
        palpitations_before_syncope=_to_bool(palpitations_before_syncope),
        structural_heart_disease=_to_bool(structural_heart_disease),
        known_coronary_disease=_to_bool(known_coronary_disease),
        mobitz_ii_or_complete_avb=_to_bool(mobitz_ii_or_complete_avb),
        vt_or_rapid_svt=_to_bool(vt_or_rapid_svt),
        bifascicular_block=_to_bool(bifascicular_block),
        typical_vasovagal_prodrome=_to_bool(typical_vasovagal_prodrome),
        absence_of_heart_disease=_to_bool(absence_of_heart_disease),
    )


def tool_classify_syncope_etiology(
    triggered_by_pain_fear: str = "false",
    triggered_by_prolonged_standing: str = "false",
    triggered_by_cough: str = "false",
    triggered_by_defecation_micturition: str = "false",
    pallor_sweating_nausea: str = "false",
    orthostatic_bp_drop: str = "false",
    structural_heart_disease: str = "false",
    abnormal_ecg: str = "false",
) -> Dict[str, Any]:
    """Classify likely syncope etiology based on clinical features."""
    return classify_syncope_etiology(
        triggered_by_pain_fear=_to_bool(triggered_by_pain_fear),
        triggered_by_prolonged_standing=_to_bool(triggered_by_prolonged_standing),
        triggered_by_cough=_to_bool(triggered_by_cough),
        triggered_by_defecation_micturition=_to_bool(triggered_by_defecation_micturition),
        pallor_sweating_nausea=_to_bool(pallor_sweating_nausea),
        orthostatic_bp_drop=_to_bool(orthostatic_bp_drop),
        structural_heart_disease=_to_bool(structural_heart_disease),
        abnormal_ecg=_to_bool(abnormal_ecg),
    )


def tool_diagnose_orthostatic_hypotension(
    supine_sbp: str,
    supine_dbp: str,
    standing_sbp_1min: str,
    standing_dbp_1min: str,
    standing_sbp_3min: str = "",
    standing_dbp_3min: str = "",
    symptoms_on_standing: str = "false",
) -> Dict[str, Any]:
    """Diagnose orthostatic hypotension based on BP measurements."""
    return diagnose_orthostatic_hypotension(
        supine_sbp=_to_int(supine_sbp, 120),
        supine_dbp=_to_int(supine_dbp, 80),
        standing_sbp_1min=_to_int(standing_sbp_1min, 100),
        standing_dbp_1min=_to_int(standing_dbp_1min, 70),
        standing_sbp_3min=_to_int(standing_sbp_3min, None) if standing_sbp_3min else None,
        standing_dbp_3min=_to_int(standing_dbp_3min, None) if standing_dbp_3min else None,
        symptoms_on_standing=_to_bool(symptoms_on_standing),
    )


def tool_assess_tilt_test_indication(
    suspected_reflex_syncope: str = "false",
    reflex_not_confirmed_by_history: str = "false",
    suspected_oh: str = "false",
    suspected_pots: str = "false",
) -> Dict[str, Any]:
    """Assess indication for tilt table testing."""
    return assess_tilt_test_indication(
        suspected_reflex_syncope=_to_bool(suspected_reflex_syncope),
        reflex_not_confirmed_by_history=_to_bool(reflex_not_confirmed_by_history),
        suspected_oh=_to_bool(suspected_oh),
        suspected_pots=_to_bool(suspected_pots),
    )


# =============================================================================
# PATHWAY TOOLS
# =============================================================================

def tool_pathway_hfref_treatment(
    current_medications: str,
    lvef: str,
    nyha_class: str,
    systolic_bp: str,
    heart_rate: str,
    potassium: str,
    egfr: str,
    rhythm: str = "sinus",
    qrs_duration: str = "",
    on_max_beta_blocker: str = "false",
    iron_deficient: str = "false",
) -> Dict[str, Any]:
    """HFrEF treatment pathway - determine next therapy step."""
    # Parse medications list
    meds = [m.strip() for m in current_medications.split(",")] if current_medications else []
    return pathway_hfref_treatment(
        current_medications=meds,
        lvef=_to_float(lvef, 35),
        nyha_class=_to_int(nyha_class, 2),
        systolic_bp=_to_int(systolic_bp, 110),
        heart_rate=_to_int(heart_rate, 70),
        potassium=_to_float(potassium, 4.5),
        egfr=_to_float(egfr, 60),
        rhythm=rhythm,
        qrs_duration=_to_int(qrs_duration, None) if qrs_duration else None,
        on_max_beta_blocker=_to_bool(on_max_beta_blocker),
        iron_deficient=_to_bool(iron_deficient),
    )


def tool_pathway_hf_device_therapy(
    lvef: str,
    qrs_duration: str,
    qrs_morphology: str,
    nyha_class: str,
    rhythm: str = "sinus",
    etiology: str = "ischemic",
    months_on_omt: str = "0",
    days_post_mi: str = "",
    prior_vt_vf: str = "false",
) -> Dict[str, Any]:
    """HF device therapy pathway - ICD and CRT decision support."""
    return pathway_hf_device_therapy(
        lvef=_to_float(lvef, 35),
        qrs_duration=_to_int(qrs_duration, 100),
        qrs_morphology=qrs_morphology,
        nyha_class=_to_int(nyha_class, 2),
        rhythm=rhythm,
        etiology=etiology,
        months_on_omt=_to_int(months_on_omt, 0),
        days_post_mi=_to_int(days_post_mi, None) if days_post_mi else None,
        prior_vt_vf=_to_bool(prior_vt_vf),
    )


def tool_get_hf_medication_targets() -> Dict[str, Any]:
    """Get target doses for HF medications."""
    return get_hf_medication_targets()


def tool_pathway_vt_acute_management(
    hemodynamic_status: str,
    vt_morphology: str = "unknown",
    lvef: str = "",
    structural_heart_disease: str = "false",
) -> Dict[str, Any]:
    """Acute VT management pathway."""
    return pathway_vt_acute_management(
        hemodynamic_status=hemodynamic_status,
        vt_morphology=vt_morphology,
        lvef=_to_float(lvef, None) if lvef else None,
        structural_heart_disease=_to_bool(structural_heart_disease),
    )


def tool_pathway_electrical_storm(
    hemodynamic_status: str,
    icd_present: str = "false",
    lvef: str = "",
) -> Dict[str, Any]:
    """Electrical storm management pathway."""
    return pathway_electrical_storm(
        hemodynamic_status=hemodynamic_status,
        icd_present=_to_bool(icd_present),
        lvef=_to_float(lvef, None) if lvef else None,
    )


def tool_pathway_vt_chronic_management(
    etiology: str,
    lvef: str,
    recurrent_vt: str = "false",
    icd_shocks: str = "false",
) -> Dict[str, Any]:
    """Chronic VT management pathway."""
    return pathway_vt_chronic_management(
        etiology=etiology,
        lvef=_to_float(lvef, 35),
        recurrent_vt=_to_bool(recurrent_vt),
        icd_shocks=_to_bool(icd_shocks),
    )


def tool_pathway_pe_treatment(
    risk_category: str,
    hemodynamic_status: str,
    bleeding_risk: str = "low",
    renal_function: str = "normal",
) -> Dict[str, Any]:
    """PE treatment pathway."""
    return pathway_pe_treatment(
        risk_category=risk_category,
        hemodynamic_status=hemodynamic_status,
        bleeding_risk=bleeding_risk,
        renal_function=renal_function,
    )


def tool_pathway_pe_anticoagulation_duration(
    risk_factor_category: str,
    bleeding_risk: str = "low",
    patient_preference_extended: str = "false",
) -> Dict[str, Any]:
    """PE anticoagulation duration pathway."""
    return pathway_pe_anticoagulation_duration(
        risk_factor_category=risk_factor_category,
        bleeding_risk=bleeding_risk,
        patient_preference_extended=_to_bool(patient_preference_extended),
    )


def tool_pathway_syncope_evaluation(
    initial_assessment_diagnostic: str = "false",
    structural_heart_disease: str = "false",
    abnormal_ecg: str = "false",
    exertional_syncope: str = "false",
) -> Dict[str, Any]:
    """Syncope evaluation pathway."""
    return pathway_syncope_evaluation(
        initial_assessment_diagnostic=_to_bool(initial_assessment_diagnostic),
        structural_heart_disease=_to_bool(structural_heart_disease),
        abnormal_ecg=_to_bool(abnormal_ecg),
        exertional_syncope=_to_bool(exertional_syncope),
    )


def tool_pathway_syncope_disposition(
    risk_category: str,
    diagnosis_established: str = "false",
    high_risk_occupation: str = "false",
) -> Dict[str, Any]:
    """Syncope disposition pathway."""
    return pathway_syncope_disposition(
        risk_category=risk_category,
        diagnosis_established=_to_bool(diagnosis_established),
        high_risk_occupation=_to_bool(high_risk_occupation),
    )


# =============================================================================
# KNOWLEDGE BASE TOOLS
# =============================================================================

def tool_process_pdfs() -> Dict[str, Any]:
    """
    Process all PDFs in source_pdfs directory to extract knowledge.
    
    Call this to extract chapters, tables, and keywords from guideline PDFs.
    Must be called once before searching knowledge.
    
    Returns:
        Processing results with count of processed files
    """
    from cardiocode.knowledge.extractor import process_all_pdfs
    return process_all_pdfs()


def tool_search_knowledge(query: str, max_results: str = "5") -> Dict[str, Any]:
    """
    Search the extracted guideline knowledge base.
    
    Args:
        query: Clinical question or topic to search for
        max_results: Maximum number of results (default 5)
    
    Returns:
        Ranked search results with chapter previews
    """
    from cardiocode.knowledge.search import search_knowledge
    
    results = search_knowledge(query, _to_int(max_results, 5))
    
    return {
        "query": query,
        "results_count": len(results),
        "results": results,
    }


def tool_get_knowledge_status() -> Dict[str, Any]:
    """
    Get status of the knowledge base.
    
    Returns:
        List of processed guidelines with chapter counts
    """
    from cardiocode.knowledge.search import get_knowledge_status
    return get_knowledge_status()


def tool_get_chapter(guideline_slug: str, chapter_title: str) -> Dict[str, Any]:
    """
    Get full content of a specific chapter.
    
    Args:
        guideline_slug: Slug identifier for the guideline (from search results)
        chapter_title: Title of the chapter to retrieve
    
    Returns:
        Full chapter content with tables
    """
    from cardiocode.knowledge.search import get_chapter_content
    
    result = get_chapter_content(guideline_slug, chapter_title)
    if result is None:
        return {"error": f"Chapter not found: {chapter_title} in {guideline_slug}"}
    return result


# =============================================================================
# TOOL REGISTRY
# =============================================================================

TOOL_REGISTRY = {
    # ==========================================================================
    # ORIGINAL CLINICAL SCORES
    # ==========================================================================
    "calculate_cha2ds2_vasc": {
        "function": tool_calculate_cha2ds2_vasc,
        "description": "Calculate CHA2DS2-VASc stroke risk score for atrial fibrillation",
    },
    "calculate_has_bled": {
        "function": tool_calculate_has_bled,
        "description": "Calculate HAS-BLED bleeding risk score",
    },
    "calculate_grace_score": {
        "function": tool_calculate_grace_score,
        "description": "Calculate GRACE score for ACS risk stratification",
    },
    "calculate_wells_pe": {
        "function": tool_calculate_wells_pe,
        "description": "Calculate Wells score for pulmonary embolism probability",
    },
    "calculate_hcm_scd_risk": {
        "function": tool_calculate_hcm_scd_risk,
        "description": "Calculate 5-year SCD risk in hypertrophic cardiomyopathy",
    },
    
    # ==========================================================================
    # NEW PE/VTE CALCULATORS
    # ==========================================================================
    "calculate_pesi": {
        "function": tool_calculate_pesi,
        "description": "Calculate PESI score for PE 30-day mortality prediction",
    },
    "calculate_spesi": {
        "function": tool_calculate_spesi,
        "description": "Calculate Simplified PESI (sPESI) for PE risk stratification",
    },
    "calculate_geneva_pe": {
        "function": tool_calculate_geneva_pe,
        "description": "Calculate Revised Geneva Score for PE pre-test probability",
    },
    "calculate_age_adjusted_ddimer": {
        "function": tool_calculate_age_adjusted_ddimer,
        "description": "Calculate age-adjusted D-dimer cutoff for PE exclusion",
    },
    
    # ==========================================================================
    # NEW PAH CALCULATORS
    # ==========================================================================
    "calculate_pah_baseline_risk": {
        "function": tool_calculate_pah_baseline_risk,
        "description": "Calculate PAH baseline risk using 3-strata model (1-year mortality)",
    },
    "calculate_pah_followup_risk": {
        "function": tool_calculate_pah_followup_risk,
        "description": "Calculate PAH follow-up risk using simplified 4-strata model",
    },
    "classify_ph_hemodynamics": {
        "function": tool_classify_ph_hemodynamics,
        "description": "Classify pulmonary hypertension by hemodynamic definitions",
    },
    
    # ==========================================================================
    # NEW HF CALCULATORS
    # ==========================================================================
    "calculate_maggic_score": {
        "function": tool_calculate_maggic_score,
        "description": "Calculate MAGGIC score for HF 1-year and 3-year mortality",
    },
    "assess_iron_deficiency_hf": {
        "function": tool_assess_iron_deficiency_hf,
        "description": "Assess iron deficiency in HF patients and IV iron indication",
    },
    "classify_hf_phenotype": {
        "function": tool_classify_hf_phenotype,
        "description": "Classify HF phenotype (HFrEF, HFmrEF, HFpEF) by LVEF",
    },
    
    # ==========================================================================
    # NEW ARRHYTHMIA RISK CALCULATORS
    # ==========================================================================
    "calculate_lmna_risk": {
        "function": tool_calculate_lmna_risk,
        "description": "Calculate 5-year VA risk in LMNA mutation carriers",
    },
    "calculate_lqts_risk": {
        "function": tool_calculate_lqts_risk,
        "description": "Estimate arrhythmic risk in Long QT Syndrome",
    },
    "calculate_brugada_risk": {
        "function": tool_calculate_brugada_risk,
        "description": "Risk stratification in Brugada Syndrome",
    },
    
    # ==========================================================================
    # ORIGINAL ASSESSMENTS
    # ==========================================================================
    "assess_aortic_stenosis": {
        "function": tool_assess_aortic_stenosis,
        "description": "Assess aortic stenosis severity and intervention indication",
    },
    "assess_icd_indication": {
        "function": tool_assess_icd_indication,
        "description": "Assess ICD indication for sudden cardiac death prevention",
    },
    
    # ==========================================================================
    # NEW VALVULAR ASSESSMENTS
    # ==========================================================================
    "assess_ar_severity": {
        "function": tool_assess_ar_severity,
        "description": "Assess aortic regurgitation severity and intervention indication",
    },
    "assess_mr_primary_intervention": {
        "function": tool_assess_mr_primary_intervention,
        "description": "Assess primary mitral regurgitation intervention indication",
    },
    "assess_mr_secondary_teer": {
        "function": tool_assess_mr_secondary_teer,
        "description": "Assess secondary MR eligibility for TEER (MitraClip)",
    },
    "assess_tr_intervention": {
        "function": tool_assess_tr_intervention,
        "description": "Assess tricuspid regurgitation intervention indication",
    },
    "assess_ms_intervention": {
        "function": tool_assess_ms_intervention,
        "description": "Assess mitral stenosis intervention indication",
    },
    "assess_valve_type_selection": {
        "function": tool_assess_valve_type_selection,
        "description": "Assess mechanical vs biological valve selection",
    },
    "calculate_inr_target_mhv": {
        "function": tool_calculate_inr_target_mhv,
        "description": "Calculate INR target for mechanical heart valve",
    },
    
    # ==========================================================================
    # NEW DEVICE ASSESSMENTS
    # ==========================================================================
    "assess_crt_indication": {
        "function": tool_assess_crt_indication,
        "description": "Assess CRT indication based on ESC guidelines",
    },
    "assess_dcm_icd_indication": {
        "function": tool_assess_dcm_icd_indication,
        "description": "Assess ICD indication in dilated cardiomyopathy",
    },
    "assess_arvc_icd_indication": {
        "function": tool_assess_arvc_icd_indication,
        "description": "Assess ICD indication in ARVC",
    },
    "assess_sarcoidosis_icd_indication": {
        "function": tool_assess_sarcoidosis_icd_indication,
        "description": "Assess ICD indication in cardiac sarcoidosis",
    },
    "assess_pacing_indication": {
        "function": tool_assess_pacing_indication,
        "description": "Assess pacemaker indication for bradycardia",
    },
    "select_pacing_mode": {
        "function": tool_select_pacing_mode,
        "description": "Select appropriate pacing mode (DDD, VVI, etc.)",
    },
    
    # ==========================================================================
    # NEW VTE ASSESSMENTS
    # ==========================================================================
    "assess_pe_risk_stratification": {
        "function": tool_assess_pe_risk_stratification,
        "description": "Assess PE risk stratification (high/intermediate/low)",
    },
    "assess_pe_thrombolysis": {
        "function": tool_assess_pe_thrombolysis,
        "description": "Assess thrombolysis indication for PE",
    },
    "assess_pe_outpatient_eligibility": {
        "function": tool_assess_pe_outpatient_eligibility,
        "description": "Assess eligibility for outpatient PE treatment",
    },
    "calculate_vte_recurrence_risk": {
        "function": tool_calculate_vte_recurrence_risk,
        "description": "Calculate VTE recurrence risk and anticoagulation duration",
    },
    
    # ==========================================================================
    # NEW CARDIO-ONCOLOGY ASSESSMENTS
    # ==========================================================================
    "assess_cardio_oncology_baseline_risk": {
        "function": tool_assess_cardio_oncology_baseline_risk,
        "description": "Assess baseline CV risk before cardiotoxic cancer therapy (HFA-ICOS)",
    },
    "assess_ctrcd_severity": {
        "function": tool_assess_ctrcd_severity,
        "description": "Assess cancer therapy-related cardiac dysfunction severity",
    },
    "get_surveillance_protocol": {
        "function": tool_get_surveillance_protocol,
        "description": "Get surveillance protocol for cardiotoxic cancer therapy",
    },
    
    # ==========================================================================
    # NEW SYNCOPE ASSESSMENTS
    # ==========================================================================
    "assess_syncope_risk": {
        "function": tool_assess_syncope_risk,
        "description": "Assess syncope risk and disposition recommendation",
    },
    "classify_syncope_etiology": {
        "function": tool_classify_syncope_etiology,
        "description": "Classify likely syncope etiology",
    },
    "diagnose_orthostatic_hypotension": {
        "function": tool_diagnose_orthostatic_hypotension,
        "description": "Diagnose orthostatic hypotension from BP measurements",
    },
    "assess_tilt_test_indication": {
        "function": tool_assess_tilt_test_indication,
        "description": "Assess indication for tilt table testing",
    },
    
    # ==========================================================================
    # NEW CLINICAL PATHWAYS
    # ==========================================================================
    "pathway_hfref_treatment": {
        "function": tool_pathway_hfref_treatment,
        "description": "HFrEF treatment pathway - determine next therapy step",
    },
    "pathway_hf_device_therapy": {
        "function": tool_pathway_hf_device_therapy,
        "description": "HF device therapy pathway - ICD and CRT decision support",
    },
    "get_hf_medication_targets": {
        "function": tool_get_hf_medication_targets,
        "description": "Get target doses for HF medications",
    },
    "pathway_vt_acute_management": {
        "function": tool_pathway_vt_acute_management,
        "description": "Acute VT management pathway",
    },
    "pathway_electrical_storm": {
        "function": tool_pathway_electrical_storm,
        "description": "Electrical storm management pathway",
    },
    "pathway_vt_chronic_management": {
        "function": tool_pathway_vt_chronic_management,
        "description": "Chronic VT management pathway",
    },
    "pathway_pe_treatment": {
        "function": tool_pathway_pe_treatment,
        "description": "PE treatment pathway",
    },
    "pathway_pe_anticoagulation_duration": {
        "function": tool_pathway_pe_anticoagulation_duration,
        "description": "PE anticoagulation duration pathway",
    },
    "pathway_syncope_evaluation": {
        "function": tool_pathway_syncope_evaluation,
        "description": "Syncope evaluation pathway",
    },
    "pathway_syncope_disposition": {
        "function": tool_pathway_syncope_disposition,
        "description": "Syncope disposition pathway",
    },
    
    # ==========================================================================
    # KNOWLEDGE BASE
    # ==========================================================================
    "process_pdfs": {
        "function": tool_process_pdfs,
        "description": "Process all guideline PDFs to extract searchable knowledge",
    },
    "search_knowledge": {
        "function": tool_search_knowledge,
        "description": "Search extracted guideline content for clinical questions",
    },
    "get_knowledge_status": {
        "function": tool_get_knowledge_status,
        "description": "Get status of processed guidelines in knowledge base",
    },
    "get_chapter": {
        "function": tool_get_chapter,
        "description": "Get full content of a specific guideline chapter",
    },
}


def call_tool(name: str, arguments: Dict[str, Any]) -> Any:
    """Call a tool by name with arguments."""
    if name not in TOOL_REGISTRY:
        return {"error": f"Unknown tool: {name}", "available_tools": list(TOOL_REGISTRY.keys())}
    
    tool_info = TOOL_REGISTRY[name]
    func = tool_info["function"]
    
    try:
        return func(**arguments)
    except Exception as e:
        return {"error": str(e), "tool": name}
