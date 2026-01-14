"""
CardioCode MCP Tools.

Tool definitions for exposing CardioCode functionality via MCP.

MCP passes all arguments as strings, so we need conversion helpers.
"""

from __future__ import annotations
import json
from typing import Any, Dict, List, Optional, Union

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


def _to_int(value: Union[str, int, None], default: Optional[int] = None) -> Optional[int]:
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


def _to_float(value: Union[str, float, int, None], default: Optional[float] = None) -> Optional[float]:
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


def _to_str(value: Any, default: Optional[str] = None) -> Optional[str]:
    """Convert value to string."""
    if value is None:
        return default
    return str(value)


# Core imports
from cardiocode.core.types import Patient, NYHAClass
from cardiocode.core.recommendation import RecommendationSet

# Clinical scores
from cardiocode.knowledge.scores import (
    cha2ds2_vasc,
    has_bled,
    grace_score,
    wells_pe,
)

# Guidelines
from cardiocode.guidelines.heart_failure import (
    get_hfref_treatment,
    assess_icd_indication as hf_assess_icd,
)
from cardiocode.guidelines.pulmonary_hypertension import (
    assess_pah_risk,
    get_pah_treatment,
)
from cardiocode.guidelines.ventricular_arrhythmias import (
    calculate_hcm_scd_risk,
    assess_icd_indication as va_assess_icd,
    manage_vt,
    VTType,
)
from cardiocode.guidelines.cardio_oncology import (
    calculate_hfa_icos_risk,
    get_surveillance_protocol,
    manage_ctrcd,
    CancerTherapyType,
)

# PDF ingestion
from cardiocode.ingestion.pdf_watcher import (
    GuidelineWatcher,
    check_for_new_pdfs,
)


def _rec_set_to_dict(rec_set: RecommendationSet) -> Dict[str, Any]:
    """Convert RecommendationSet to serializable dict."""
    return rec_set.to_dict()


# =============================================================================
# CLINICAL SCORES
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
        female: Female sex
        chf: Congestive heart failure
        hypertension: Hypertension
        stroke_tia: Prior stroke/TIA/thromboembolism
        vascular_disease: Vascular disease (MI, PAD, aortic plaque)
        diabetes: Diabetes mellitus
    
    Returns:
        Score result with interpretation
    """
    result = cha2ds2_vasc(
        age=_to_int(age, 65) or 65,
        sex="female" if _to_bool(female) else "male",
        has_chf=_to_bool(chf),
        has_hypertension=_to_bool(hypertension),
        has_stroke_tia_te=_to_bool(stroke_tia),
        has_vascular_disease=_to_bool(vascular_disease),
        has_diabetes=_to_bool(diabetes),
    )
    return {
        "score": result.score_value,
        "max_score": result.max_score,
        "risk_category": result.risk_category,
        "interpretation": result.interpretation,
        "recommendation": result.recommendation,
        "components": result.components,
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
        hypertension_uncontrolled: Uncontrolled hypertension (SBP > 160)
        abnormal_renal: Dialysis, transplant, Cr > 2.26 mg/dL
        abnormal_liver: Cirrhosis or bilirubin > 2x + AST/ALT > 3x
        stroke_history: Prior stroke
        bleeding_history: Prior major bleeding or predisposition
        labile_inr: Unstable/high INRs, TTR < 60%
        age_over_65: Age > 65 years
        drugs_predisposing: Antiplatelet agents or NSAIDs
        alcohol_excess: >= 8 drinks/week
    
    Returns:
        Score result with interpretation
    """
    result = has_bled(
        has_hypertension=_to_bool(hypertension_uncontrolled),
        abnormal_renal_function=_to_bool(abnormal_renal),
        abnormal_liver_function=_to_bool(abnormal_liver),
        has_stroke=_to_bool(stroke_history),
        bleeding_history=_to_bool(bleeding_history),
        labile_inr=_to_bool(labile_inr),
        age_over_65=_to_bool(age_over_65),
        drugs_predisposing=_to_bool(drugs_predisposing),
        alcohol_excess=_to_bool(alcohol_excess),
    )
    return {
        "score": result.score_value,
        "max_score": result.max_score,
        "risk_category": result.risk_category,
        "interpretation": result.interpretation,
        "recommendation": result.recommendation,
        "components": result.components,
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
        killip_class: Killip class (1-4)
        cardiac_arrest: Cardiac arrest at admission
        st_deviation: ST-segment deviation
        elevated_troponin: Elevated cardiac troponin
    
    Returns:
        GRACE score with mortality risk
    """
    result = grace_score(
        age=_to_int(age, 65) or 65,
        heart_rate=_to_int(heart_rate, 80) or 80,
        systolic_bp=_to_int(systolic_bp, 120) or 120,
        creatinine=_to_float(creatinine, 1.0) or 1.0,
        killip_class=_to_int(killip_class, 1) or 1,
        cardiac_arrest=_to_bool(cardiac_arrest),
        st_deviation=_to_bool(st_deviation),
        elevated_troponin=_to_bool(elevated_troponin),
    )
    return {
        "score": result.score_value,
        "risk_category": result.risk_category,
        "interpretation": result.interpretation,
        "recommendation": result.recommendation,
        "components": result.components,
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
        clinical_signs_dvt: Clinical signs/symptoms of DVT
        pe_most_likely: PE is #1 diagnosis or equally likely
        heart_rate_above_100: Heart rate > 100 bpm
        immobilization_surgery: Immobilization or surgery in past 4 weeks
        previous_pe_dvt: Previous PE or DVT
        hemoptysis: Hemoptysis
        malignancy: Malignancy (treatment within 6 months or palliative)
    
    Returns:
        Wells score with PE probability
    """
    result = wells_pe(
        clinical_signs_dvt=_to_bool(clinical_signs_dvt),
        pe_most_likely_diagnosis=_to_bool(pe_most_likely),
        heart_rate_above_100=_to_bool(heart_rate_above_100),
        immobilization_or_surgery=_to_bool(immobilization_surgery),
        previous_pe_dvt=_to_bool(previous_pe_dvt),
        hemoptysis=_to_bool(hemoptysis),
        malignancy=_to_bool(malignancy),
    )
    return {
        "score": result.score_value,
        "risk_category": result.risk_category,
        "risk_percentage": result.risk_percentage,
        "interpretation": result.interpretation,
        "recommendation": result.recommendation,
        "components": result.components,
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
    Calculate 5-year SCD risk in hypertrophic cardiomyopathy (HCM Risk-SCD).
    
    Args:
        age: Age 16-80 years
        max_wall_thickness: Maximum LV wall thickness (mm)
        la_diameter: Left atrial diameter (mm)
        max_lvot_gradient: Maximum LVOT gradient at rest/Valsalva (mmHg)
        family_history_scd: Family history of SCD in 1st degree relative < 40y
        nsvt: Non-sustained VT on Holter
        unexplained_syncope: Unexplained syncope
    
    Returns:
        5-year SCD risk and ICD recommendation
    """
    result = calculate_hcm_scd_risk(
        age=_to_int(age, 50) or 50,
        max_wall_thickness=_to_float(max_wall_thickness, 15.0) or 15.0,
        la_diameter=_to_float(la_diameter, 40.0) or 40.0,
        max_lvot_gradient=_to_float(max_lvot_gradient, 10.0) or 10.0,
        family_history_scd=_to_bool(family_history_scd),
        nsvt=_to_bool(nsvt),
        unexplained_syncope=_to_bool(unexplained_syncope),
    )
    return {
        "five_year_scd_risk_percent": result.five_year_risk_percent,
        "risk_category": result.risk_category.value,
        "icd_recommendation": result.icd_recommendation,
        "risk_factors": result.risk_factors,
    }


# =============================================================================
# GUIDELINE QUERIES
# =============================================================================

def tool_get_hf_recommendations(
    lvef: str,
    nyha_class: str,
    age: Optional[str] = None,
    has_af: str = "false",
    has_cad: str = "false",
    has_diabetes: str = "false",
    has_ckd: str = "false",
) -> Dict[str, Any]:
    """
    Get heart failure treatment recommendations based on ESC 2021 guidelines.
    
    Args:
        lvef: LV ejection fraction (%)
        nyha_class: NYHA functional class (1-4)
        age: Patient age
        has_af: Atrial fibrillation
        has_cad: Coronary artery disease
        has_diabetes: Diabetes mellitus
        has_ckd: Chronic kidney disease
    
    Returns:
        Treatment recommendations with evidence levels
    """
    nyha_int = _to_int(nyha_class, 2) or 2
    patient = Patient(
        age=_to_int(age) if age else None,
        lvef=_to_float(lvef, 40.0),
        nyha_class=NYHAClass(nyha_int),
    )
    
    rec_set = get_hfref_treatment(patient)
    return _rec_set_to_dict(rec_set)


def tool_assess_icd_indication(
    lvef: str,
    nyha_class: str,
    etiology: str = "ischemic",
    prior_vf_vt: str = "false",
    syncope: str = "false",
    days_post_mi: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Assess ICD indication for primary or secondary prevention.
    
    Args:
        lvef: LV ejection fraction (%)
        nyha_class: NYHA class (1-4)
        etiology: Cardiomyopathy etiology (ischemic, non_ischemic, hcm, arvc)
        prior_vf_vt: Prior VF or sustained VT
        syncope: Unexplained syncope
        days_post_mi: Days since MI (if applicable)
    
    Returns:
        ICD indication assessment with evidence class
    """
    nyha_int = _to_int(nyha_class, 2) or 2
    patient = Patient(
        lvef=_to_float(lvef, 40.0),
        nyha_class=NYHAClass(nyha_int),
    )
    
    rec_set = va_assess_icd(patient)
    result = _rec_set_to_dict(rec_set)
    
    days_post = _to_int(days_post_mi) if days_post_mi else None
    if days_post is not None and days_post < 40:
        result["timing_note"] = f"Patient is {days_post} days post-MI. ICD should be deferred until >= 40 days post-MI."
    
    return result


def tool_assess_pulmonary_hypertension(
    who_fc: str = "2",
    six_mwd: Optional[str] = None,
    nt_pro_bnp: Optional[str] = None,
    mpap: Optional[str] = None,
    pawp: Optional[str] = None,
    pvr: Optional[str] = None,
    has_left_heart_disease: str = "false",
    has_lung_disease: str = "false",
    has_chronic_pe: str = "false",
) -> Dict[str, Any]:
    """
    Assess and classify pulmonary hypertension.
    
    Args:
        who_fc: WHO functional class (1-4)
        six_mwd: 6-minute walk distance (meters)
        nt_pro_bnp: NT-proBNP (pg/mL)
        mpap: Mean pulmonary artery pressure (mmHg)
        pawp: Pulmonary artery wedge pressure (mmHg)
        pvr: Pulmonary vascular resistance (Wood units)
        has_left_heart_disease: Known left heart disease
        has_lung_disease: Significant lung disease
        has_chronic_pe: Chronic pulmonary embolism
    
    Returns:
        PH classification and treatment recommendations
    """
    who_fc_int = _to_int(who_fc, 2) or 2
    six_mwd_val = _to_float(six_mwd) if six_mwd else None
    nt_pro_bnp_val = _to_float(nt_pro_bnp) if nt_pro_bnp else None
    mpap_val = _to_float(mpap) if mpap else None
    pawp_val = _to_float(pawp) if pawp else None
    pvr_val = _to_float(pvr) if pvr else None
    
    risk_result = assess_pah_risk(
        who_fc=who_fc_int,
        six_mwd=six_mwd_val,
        nt_pro_bnp=nt_pro_bnp_val,
    )
    
    result = {
        "risk_category": risk_result.value,
        "hemodynamics": {},
        "classification": None,
    }
    
    if mpap_val is not None:
        result["hemodynamics"]["mean_pap"] = mpap_val
        result["hemodynamics"]["ph_present"] = mpap_val > 20
            
    if pawp_val is not None:
        result["hemodynamics"]["pawp"] = pawp_val
        result["hemodynamics"]["type"] = "pre-capillary" if pawp_val <= 15 else "post-capillary"
    
    if pvr_val is not None:
        result["hemodynamics"]["pvr"] = pvr_val
    
    if _to_bool(has_left_heart_disease):
        result["classification"] = "Group 2: PH due to left heart disease"
    elif _to_bool(has_lung_disease):
        result["classification"] = "Group 3: PH due to lung disease/hypoxia"
    elif _to_bool(has_chronic_pe):
        result["classification"] = "Group 4: Chronic thromboembolic PH (CTEPH)"
    elif pawp_val is not None and pawp_val <= 15 and pvr_val is not None and pvr_val > 2:
        result["classification"] = "Group 1: Pulmonary arterial hypertension (PAH)"
    
    patient = Patient()
    rec_set = get_pah_treatment(patient)
    result["recommendations"] = _rec_set_to_dict(rec_set)
    
    return result


def tool_assess_cardio_oncology_risk(
    age: str,
    planned_therapy: str,
    lvef: Optional[str] = None,
    prior_anthracycline: str = "false",
    prior_anthracycline_dose: Optional[str] = None,
    prior_chest_radiation: str = "false",
    heart_failure: str = "false",
    hypertension: str = "false",
    diabetes: str = "false",
    coronary_artery_disease: str = "false",
) -> Dict[str, Any]:
    """
    Assess cardiovascular risk before cancer therapy.
    
    Args:
        age: Patient age
        planned_therapy: Type of therapy (anthracycline, her2, checkpoint_inhibitor, vegf_inhibitor)
        lvef: Baseline LVEF (%)
        prior_anthracycline: Prior anthracycline exposure
        prior_anthracycline_dose: Cumulative dose (mg/m2 doxorubicin equivalent)
        prior_chest_radiation: Prior chest radiation
        heart_failure: History of heart failure
        hypertension: Hypertension
        diabetes: Diabetes
        coronary_artery_disease: Known CAD
    
    Returns:
        Risk assessment and surveillance recommendations
    """
    age_int = _to_int(age, 60) or 60
    lvef_val = _to_float(lvef) if lvef else None
    prior_dose = _to_float(prior_anthracycline_dose) if prior_anthracycline_dose else None
    
    baseline = calculate_hfa_icos_risk(
        age=age_int,
        heart_failure=_to_bool(heart_failure),
        hypertension=_to_bool(hypertension),
        diabetes=_to_bool(diabetes),
        mi_or_pci_cabg=_to_bool(coronary_artery_disease),
        prior_anthracycline=_to_bool(prior_anthracycline),
        prior_anthracycline_dose=prior_dose,
        prior_chest_radiation=_to_bool(prior_chest_radiation),
        lvef=lvef_val,
    )
    
    result = {
        "baseline_risk_category": baseline.risk_category.value,
        "hfa_icos_score": baseline.hfa_icos_score,
        "risk_factors": [{"name": rf.name, "present": rf.present} for rf in baseline.risk_factors],
        "cardiology_referral_needed": baseline.cardiology_referral_needed,
        "monitoring_intensity": baseline.monitoring_intensity,
        "precautions": baseline.precautions,
    }
    
    therapy_map = {
        "anthracycline": CancerTherapyType.ANTHRACYCLINE,
        "her2": CancerTherapyType.HER2_TARGETED,
        "checkpoint_inhibitor": CancerTherapyType.IMMUNE_CHECKPOINT,
        "vegf_inhibitor": CancerTherapyType.VEGF_INHIBITOR,
    }
    
    therapy_type = therapy_map.get(planned_therapy.lower())
    if therapy_type:
        patient = Patient(age=age_int, lvef=lvef_val)
        surveillance = get_surveillance_protocol(
            patient=patient,
            therapy=therapy_type,
            risk_category=baseline.risk_category,
        )
        result["surveillance"] = _rec_set_to_dict(surveillance)
    
    return result


def tool_manage_ctrcd(
    lvef_current: str,
    lvef_baseline: Optional[str] = None,
    symptomatic: str = "false",
    cancer_therapy: str = "anthracycline",
) -> Dict[str, Any]:
    """
    Manage cancer therapy-related cardiac dysfunction (CTRCD).
    
    Args:
        lvef_current: Current LVEF (%)
        lvef_baseline: Baseline LVEF (%)
        symptomatic: Heart failure symptoms present
        cancer_therapy: Type of cancer therapy
    
    Returns:
        CTRCD classification and management recommendations
    """
    lvef_curr_val = _to_float(lvef_current, 50.0) or 50.0
    lvef_base_val = _to_float(lvef_baseline) if lvef_baseline else None
    symptomatic_bool = _to_bool(symptomatic)
    
    rec_set = manage_ctrcd(
        lvef_current=lvef_curr_val,
        lvef_baseline=lvef_base_val,
        symptomatic=symptomatic_bool,
        cancer_therapy=cancer_therapy,
    )
    
    result = _rec_set_to_dict(rec_set)
    
    if lvef_curr_val < 40:
        result["ctrcd_severity"] = "very_severe" if symptomatic_bool else "severe"
    elif 40 <= lvef_curr_val < 50:
        result["ctrcd_severity"] = "moderate"
    elif lvef_base_val and (lvef_base_val - lvef_curr_val) >= 10:
        result["ctrcd_severity"] = "mild"
    else:
        result["ctrcd_severity"] = "none"
    
    return result


def tool_get_vt_management(
    vt_type: str = "monomorphic",
    hemodynamically_stable: str = "true",
    has_structural_heart_disease: str = "false",
    lvef: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get ventricular tachycardia management recommendations.
    
    Args:
        vt_type: Type of VT (monomorphic, polymorphic, electrical_storm, nsvt, idiopathic)
        hemodynamically_stable: Patient hemodynamically stable
        has_structural_heart_disease: Structural heart disease present
        lvef: LV ejection fraction
    
    Returns:
        VT management recommendations
    """
    vt_type_map = {
        "monomorphic": VTType.MONOMORPHIC_SUSTAINED,
        "polymorphic": VTType.POLYMORPHIC,
        "electrical_storm": VTType.ELECTRICAL_STORM,
        "nsvt": VTType.MONOMORPHIC_NSVT,
        "idiopathic": VTType.IDIOPATHIC_OUTFLOW,
    }
    
    vt_type_str = vt_type.lower() if vt_type else "monomorphic"
    vt = vt_type_map.get(vt_type_str, VTType.MONOMORPHIC_SUSTAINED)
    lvef_val = _to_float(lvef) if lvef else None
    patient = Patient(lvef=lvef_val)
    
    rec_set = manage_vt(patient, vt_type=vt)
    return _rec_set_to_dict(rec_set)


# =============================================================================
# VALVULAR HEART DISEASE TOOLS
# =============================================================================

def tool_assess_aortic_stenosis(
    peak_velocity: str,
    mean_gradient: str,
    ava: str,
    lvef: str = "55",
    stroke_volume_index: str = "35",
) -> Dict[str, Any]:
    """
    Assess aortic stenosis severity per ESC 2021 VHD Guidelines.
    
    Args:
        peak_velocity: Peak aortic jet velocity (m/s)
        mean_gradient: Mean transvalvular gradient (mmHg)
        ava: Aortic valve area (cm2)
        lvef: LV ejection fraction (%)
        stroke_volume_index: Stroke volume index (mL/m2)
    
    Returns:
        AS severity assessment with classification
    """
    from cardiocode.guidelines.valvular_heart_disease.aortic_stenosis import assess_aortic_stenosis_severity
    
    result = assess_aortic_stenosis_severity(
        peak_velocity=_to_float(peak_velocity),
        mean_gradient=_to_float(mean_gradient),
        ava=_to_float(ava),
        lvef=_to_int(lvef),
        stroke_volume_index=_to_float(stroke_volume_index),
    )
    
    return {
        "severity": result.severity.value,
        "classification": result.classification,
        "flow_status": result.flow_status,
        "gradient_status": result.gradient_status,
        "peak_velocity": result.peak_velocity,
        "mean_gradient": result.mean_gradient,
        "ava": result.ava,
        "recommendations": [rec.action for rec in result.recommendations],
    }


def tool_assess_mitral_regurgitation(
    eroa: str,
    regurgitant_volume: str,
    vena_contracta: str = "5",
    etiology: str = "primary",
) -> Dict[str, Any]:
    """
    Assess mitral regurgitation severity per ESC 2021 VHD Guidelines.
    
    Args:
        eroa: Effective regurgitant orifice area (mm2)
        regurgitant_volume: Regurgitant volume per beat (mL)
        vena_contracta: Vena contracta width (mm)
        etiology: Primary or secondary MR
    
    Returns:
        MR severity assessment
    """
    from cardiocode.guidelines.valvular_heart_disease.mitral_regurgitation import (
        assess_mitral_regurgitation_severity, MREtiology
    )
    
    etiology_map = {"primary": MREtiology.PRIMARY, "secondary": MREtiology.SECONDARY}
    
    result = assess_mitral_regurgitation_severity(
        eroa=_to_float(eroa),
        regurgitant_volume=_to_float(regurgitant_volume),
        vena_contracta=_to_float(vena_contracta),
        etiology=etiology_map.get(etiology.lower(), MREtiology.PRIMARY),
    )
    
    return {
        "severity": result.severity.value,
        "etiology": result.etiology.value,
        "eroa": result.eroa,
        "regurgitant_volume": result.regurgitant_volume,
        "vena_contracta": result.vena_contracta,
    }


# =============================================================================
# CHRONIC CORONARY SYNDROMES TOOLS
# =============================================================================

def tool_calculate_ptp(
    age: str,
    sex: str,
    chest_pain_type: str,
) -> Dict[str, Any]:
    """
    Calculate pre-test probability of obstructive CAD per ESC 2019 CCS Guidelines.
    
    Args:
        age: Patient age
        sex: "male" or "female"
        chest_pain_type: "typical_angina", "atypical_angina", "non_anginal"
    
    Returns:
        PTP result with diagnostic recommendation
    """
    from cardiocode.guidelines.chronic_coronary_syndromes.diagnosis import (
        calculate_pretest_probability, ChestPainType
    )
    
    pain_map = {
        "typical_angina": ChestPainType.TYPICAL_ANGINA,
        "atypical_angina": ChestPainType.ATYPICAL_ANGINA,
        "non_anginal": ChestPainType.NON_ANGINAL,
    }
    
    result = calculate_pretest_probability(
        age=_to_int(age, 50) or 50,
        sex=sex,
        chest_pain_type=pain_map.get(chest_pain_type.lower(), ChestPainType.ATYPICAL_ANGINA),
    )
    
    return {
        "ptp_percent": result.ptp_percent,
        "ptp_category": result.ptp_category,
        "diagnostic_recommendation": result.diagnostic_recommendation,
        "further_testing_needed": result.further_testing_needed,
    }


# =============================================================================
# NSTE-ACS TOOLS
# =============================================================================

def tool_calculate_nste_grace(
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
    Calculate GRACE score for NSTE-ACS risk stratification.
    
    Args:
        age: Age in years
        heart_rate: Heart rate (bpm)
        systolic_bp: Systolic blood pressure (mmHg)
        creatinine: Serum creatinine (mg/dL)
        killip_class: Killip class (1-4)
        cardiac_arrest: Cardiac arrest at admission
        st_deviation: ST-segment deviation
        elevated_troponin: Elevated cardiac troponin
    
    Returns:
        GRACE score with risk category and timing recommendations
    """
    from cardiocode.guidelines.nste_acs.risk_stratification import calculate_grace_score
    
    result = calculate_grace_score(
        age=_to_int(age, 65) or 65,
        heart_rate=_to_int(heart_rate, 80) or 80,
        systolic_bp=_to_int(systolic_bp, 120) or 120,
        creatinine=_to_float(creatinine, 1.0) or 1.0,
        killip_class=_to_int(killip_class, 1) or 1,
        cardiac_arrest=_to_bool(cardiac_arrest),
        st_deviation=_to_bool(st_deviation),
        elevated_troponin=_to_bool(elevated_troponin),
    )
    
    return {
        "grace_score": result.score,
        "mortality_risk_percent": result.mortality_risk_percent,
        "risk_category": result.risk_category.value,
        "invasive_strategy_timing": result.invasive_strategy_timing,
        "recommendations": result.recommendations,
    }


# =============================================================================
# PDF INGESTION TOOLS
# =============================================================================

def tool_check_new_pdfs(
    source_dir: str = "source_pdfs",
) -> Dict[str, Any]:
    """
    Check for new guideline PDFs and register them.
    
    Args:
        source_dir: Directory containing PDF files (default: "source_pdfs")
    
    Returns:
        Dictionary with new PDFs detected and their metadata
    """
    new_pdfs = check_for_new_pdfs(source_dir)
    
    return {
        "new_pdfs_detected": len(new_pdfs),
        "pdfs": new_pdfs,
        "source_directory": source_dir,
        "message": f"Detected {len(new_pdfs)} new PDF(s)" if new_pdfs else "No new PDFs found",
    }


def tool_get_pdf_status(
    source_dir: str = "source_pdfs",
) -> Dict[str, Any]:
    """
    Get status of all guideline PDFs (processed/unprocessed).
    
    Args:
        source_dir: Directory containing PDF files (default: "source_pdfs")
    
    Returns:
        Status report with counts and details for all PDFs
    """
    watcher = GuidelineWatcher(source_dir)
    
    # Get all registered PDFs
    all_pdfs = list(watcher.registry.guidelines.values())
    processed = [p for p in all_pdfs if p.processed]
    pending = [p for p in all_pdfs if not p.processed]
    
    # Convert to dict format for JSON serialization
    pdf_details = []
    for pdf in all_pdfs:
        pdf_details.append({
            "filename": pdf.filename,
            "guideline_type": pdf.guideline_type,
            "guideline_year": pdf.guideline_year,
            "processed": pdf.processed,
            "processing_status": pdf.processing_status,
            "detected_at": pdf.detected_at.isoformat(),
            "file_size": pdf.file_size,
            "needs_classification": pdf.guideline_type is None,
        })
    
    return {
        "total_pdfs": len(all_pdfs),
        "processed": len(processed),
        "pending": len(pending),
        "source_directory": source_dir,
        "pdfs": pdf_details,
        "report": watcher.get_status_report(),
    }


def tool_extract_pdf_recommendations(
    filename: str,
    guideline_type: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Generate extraction prompt for a specific PDF.
    
    Args:
        filename: PDF filename
        guideline_type: Optional guideline type hint
    
    Returns:
        Extraction prompt and metadata for processing the PDF
    """
    from cardiocode.ingestion.knowledge_builder import extract_recommendations_prompt
    
    prompt = extract_recommendations_prompt(filename, guideline_type)
    
    return {
        "filename": filename,
        "guideline_type": guideline_type,
        "extraction_prompt": prompt,
        "instructions": "Use this prompt with Claude/GPT to extract structured recommendations from the PDF",
        "next_steps": [
            "1. Review the PDF content",
            "2. Apply the extraction prompt to get structured recommendations",
            "3. Generate Python code using the extracted recommendations",
            "4. Validate and test the encoded guidelines",
        ],
    }


# =============================================================================
# NOTIFICATION TOOLS
# =============================================================================

def tool_get_pdf_notifications(
    hours: str = "24",
    unacknowledged_only: str = "false",
) -> Dict[str, Any]:
    """
    Get recent PDF detection notifications.
    
    Args:
        hours: Number of hours to look back (default: 24)
        unacknowledged_only: Only return unacknowledged notifications
    
    Returns:
        List of recent notifications
    """
    hours_int = _to_int(hours, 24) or 24
    unack_only = _to_bool(unacknowledged_only)
    
    watcher = GuidelineWatcher("source_pdfs")
    notifications = watcher.get_notifications(hours_int)
    
    if unack_only:
        notifications = [n for n in notifications if not n.details or not n.details.get("acknowledged", False)]
    
    # Convert to dict for JSON serialization
    notif_list = []
    for notif in notifications:
        notif_list.append({
            "event_type": notif.event_type,
            "filename": notif.filename,
            "message": notif.message,
            "timestamp": notif.timestamp.isoformat(),
            "details": notif.details,
            "acknowledged": notif.details.get("acknowledged", False) if notif.details else False,
        })
    
    return {
        "notifications": notif_list,
        "hours_searched": hours_int,
        "unacknowledged_only": unack_only,
        "total_found": len(notif_list),
        "message": f"Found {len(notif_list)} notification(s) from last {hours_int} hours" if notif_list else f"No notifications found in last {hours_int} hours",
    }


def tool_acknowledge_pdf_notification(
    filename: str,
) -> Dict[str, Any]:
    """
    Acknowledge a PDF notification.
    
    Args:
        filename: PDF filename to acknowledge
    
    Returns:
        Acknowledgment result
    """
    watcher = GuidelineWatcher("source_pdfs")
    success = watcher.acknowledge_notification(filename)
    
    return {
        "success": success,
        "filename": filename,
        "message": f"Notification for {filename} acknowledged" if success else f"No unacknowledged notification found for {filename}",
    }


# =============================================================================
# TOOL REGISTRY
# =============================================================================

TOOL_REGISTRY = {
    # Original tools
    "calculate_cha2ds2_vasc": {
        "function": tool_calculate_cha2ds2_vasc,
        "description": "Calculate CHA2DS2-VASc score for stroke risk in atrial fibrillation",
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
    "get_hf_recommendations": {
        "function": tool_get_hf_recommendations,
        "description": "Get heart failure treatment recommendations (ESC 2021)",
    },
    "assess_icd_indication": {
        "function": tool_assess_icd_indication,
        "description": "Assess ICD indication for SCD prevention (ESC 2022)",
    },
    "assess_pulmonary_hypertension": {
        "function": tool_assess_pulmonary_hypertension,
        "description": "Assess and classify pulmonary hypertension (ESC 2022)",
    },
    "assess_cardio_oncology_risk": {
        "function": tool_assess_cardio_oncology_risk,
        "description": "Assess CV risk before cancer therapy (ESC 2022)",
    },
    "manage_ctrcd": {
        "function": tool_manage_ctrcd,
        "description": "Manage cancer therapy-related cardiac dysfunction",
    },
    "get_vt_management": {
        "function": tool_get_vt_management,
        "description": "Get VT management recommendations (ESC 2022)",
    },
    # New VHD tools
    "assess_aortic_stenosis": {
        "function": tool_assess_aortic_stenosis,
        "description": "Assess aortic stenosis severity (ESC 2021 VHD Guidelines)",
    },
    "assess_mitral_regurgitation": {
        "function": tool_assess_mitral_regurgitation,
        "description": "Assess mitral regurgitation severity (ESC 2021 VHD Guidelines)",
    },
    # New CCS tools
    "calculate_ptp": {
        "function": tool_calculate_ptp,
        "description": "Calculate pre-test probability of CAD (ESC 2019 CCS Guidelines)",
    },
    # New NSTE-ACS tools
    "calculate_nste_grace": {
        "function": tool_calculate_nste_grace,
        "description": "Calculate GRACE score for NSTE-ACS (ESC 2020 Guidelines)",
    },
    # PDF ingestion tools
    "check_new_pdfs": {
        "function": tool_check_new_pdfs,
        "description": "Check for new guideline PDFs and register them",
    },
    "get_pdf_status": {
        "function": tool_get_pdf_status,
        "description": "Get status of all guideline PDFs (processed/unprocessed)",
    },
    "extract_pdf_recommendations": {
        "function": tool_extract_pdf_recommendations,
        "description": "Generate extraction prompt for a specific PDF",
    },
    # Notification tools
    "get_pdf_notifications": {
        "function": tool_get_pdf_notifications,
        "description": "Get recent PDF detection notifications",
    },
    "acknowledge_pdf_notification": {
        "function": tool_acknowledge_pdf_notification,
        "description": "Acknowledge a PDF notification",
    },
}


def get_tool_list() -> List[Dict[str, Any]]:
    """Get list of available tools with descriptions."""
    return [
        {"name": name, "description": info["description"]}
        for name, info in TOOL_REGISTRY.items()
    ]


def call_tool(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Call a tool by name with arguments."""
    if name not in TOOL_REGISTRY:
        raise ValueError(f"Unknown tool: {name}")
    
    tool_func = TOOL_REGISTRY[name]["function"]
    return tool_func(**arguments)
