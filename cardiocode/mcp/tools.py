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
# PULMONARY EMBOLISM TOOLS (ESC 2019)
# =============================================================================

def tool_calculate_pesi(
    age: str,
    male: str = "true",
    cancer: str = "false",
    heart_failure: str = "false",
    chronic_lung_disease: str = "false",
    heart_rate_110_plus: str = "false",
    systolic_bp_below_100: str = "false",
    respiratory_rate_30_plus: str = "false",
    temperature_below_36: str = "false",
    altered_mental_status: str = "false",
    o2_saturation_below_90: str = "false",
) -> Dict[str, Any]:
    """
    Calculate Pulmonary Embolism Severity Index (PESI) score for 30-day mortality.

    Args:
        age: Patient age (points = age in years)
        male: Male sex (+10 points)
        cancer: Active cancer (+30 points)
        heart_failure: Chronic heart failure (+10 points)
        chronic_lung_disease: Chronic lung disease (+10 points)
        heart_rate_110_plus: Heart rate >= 110 bpm (+20 points)
        systolic_bp_below_100: SBP < 100 mmHg (+30 points)
        respiratory_rate_30_plus: RR >= 30/min (+20 points)
        temperature_below_36: Temperature < 36°C (+20 points)
        altered_mental_status: Altered mental status (+60 points)
        o2_saturation_below_90: O2 saturation < 90% (+20 points)

    Returns:
        PESI score with risk class and 30-day mortality estimate
    """
    from cardiocode.guidelines.pulmonary_embolism.diagnosis import calculate_pesi_score

    result = calculate_pesi_score(
        age=_to_int(age, 65) or 65,
        male=_to_bool(male),
        cancer=_to_bool(cancer),
        heart_failure=_to_bool(heart_failure),
        chronic_lung_disease=_to_bool(chronic_lung_disease),
        heart_rate_110_plus=_to_bool(heart_rate_110_plus),
        systolic_bp_below_100=_to_bool(systolic_bp_below_100),
        respiratory_rate_30_plus=_to_bool(respiratory_rate_30_plus),
        temperature_below_36=_to_bool(temperature_below_36),
        altered_mental_status=_to_bool(altered_mental_status),
        spo2_below_90=_to_bool(o2_saturation_below_90),
    )

    return {
        "score": result.score,
        "risk_class": result.risk_class.value,
        "mortality_risk": result.mortality_risk,
        "interpretation": result.interpretation,
        "can_treat_outpatient": result.can_treat_outpatient,
        "components": result.components,
    }


def tool_calculate_spesi(
    age_over_80: str = "false",
    cancer: str = "false",
    chronic_cardiopulmonary_disease: str = "false",
    pulse_over_110: str = "false",
    systolic_bp_under_100: str = "false",
    o2_saturation_under_90: str = "false",
) -> Dict[str, Any]:
    """
    Calculate Simplified PESI (sPESI) score for PE risk stratification.

    Args:
        age_over_80: Age > 80 years (1 point)
        cancer: Active cancer (1 point)
        chronic_cardiopulmonary_disease: Chronic heart or lung disease (1 point)
        pulse_over_110: Heart rate >= 110 bpm (1 point)
        systolic_bp_under_100: SBP < 100 mmHg (1 point)
        o2_saturation_under_90: O2 saturation < 90% (1 point)

    Returns:
        sPESI score with risk assessment (0 = low risk, >=1 = high risk)
    """
    from cardiocode.guidelines.pulmonary_embolism.diagnosis import calculate_simplified_pesi

    result = calculate_simplified_pesi(
        age_over_80=_to_bool(age_over_80),
        cancer=_to_bool(cancer),
        chronic_cardiopulmonary_disease=_to_bool(chronic_cardiopulmonary_disease),
        heart_rate_110_plus=_to_bool(pulse_over_110),
        systolic_bp_below_100=_to_bool(systolic_bp_under_100),
        spo2_below_90=_to_bool(o2_saturation_under_90),
    )

    return {
        "score": result.score,
        "high_risk": result.high_risk,
        "mortality_30_day": result.mortality_30_day,
        "interpretation": result.interpretation,
        "can_treat_outpatient": result.can_treat_outpatient,
        "components": result.components,
    }


def tool_calculate_geneva_pe(
    age_over_65: str = "false",
    previous_pe_dvt: str = "false",
    surgery_fracture_past_month: str = "false",
    active_cancer: str = "false",
    unilateral_leg_pain: str = "false",
    hemoptysis: str = "false",
    heart_rate: str = "75",
    dvt_signs: str = "false",
    simplified: str = "false",
) -> Dict[str, Any]:
    """
    Calculate Revised Geneva Score for PE pre-test probability.

    Args:
        age_over_65: Age > 65 years
        previous_pe_dvt: Previous PE or DVT
        surgery_fracture_past_month: Surgery or fracture within 1 month
        active_cancer: Active malignancy
        unilateral_leg_pain: Unilateral lower limb pain
        hemoptysis: Hemoptysis
        heart_rate: Heart rate (bpm) - used to determine 75-94 or >=95
        dvt_signs: Pain on leg palpation and unilateral edema
        simplified: Use simplified version (all items = 1 point)

    Returns:
        Geneva score with PE probability category
    """
    from cardiocode.guidelines.pulmonary_embolism.diagnosis import calculate_revised_geneva_score

    hr = _to_int(heart_rate, 75) or 75
    hr_75_94 = 75 <= hr < 95
    hr_95_plus = hr >= 95

    result = calculate_revised_geneva_score(
        age_over_65=_to_bool(age_over_65),
        previous_pe_dvt=_to_bool(previous_pe_dvt),
        surgery_or_fracture=_to_bool(surgery_fracture_past_month),
        active_malignancy=_to_bool(active_cancer),
        unilateral_leg_pain=_to_bool(unilateral_leg_pain),
        hemoptysis=_to_bool(hemoptysis),
        heart_rate_75_94=hr_75_94,
        heart_rate_95_plus=hr_95_plus,
        leg_pain_on_palpation_and_edema=_to_bool(dvt_signs),
    )

    return {
        "score": result.score,
        "probability": result.probability.value,
        "interpretation": result.interpretation,
        "recommendation": result.recommendation,
        "components": result.components,
    }


def tool_age_adjusted_ddimer(
    age: str,
    baseline_cutoff: str = "500",
) -> Dict[str, Any]:
    """
    Calculate age-adjusted D-dimer cutoff for PE exclusion.

    Args:
        age: Patient age in years
        baseline_cutoff: Baseline D-dimer cutoff (default 500 ng/mL)

    Returns:
        Age-adjusted D-dimer cutoff
    """
    age_int = _to_int(age, 50) or 50
    baseline = _to_float(baseline_cutoff, 500.0) or 500.0

    if age_int <= 50:
        cutoff = baseline
        adjustment = "No age adjustment needed for age <= 50"
    else:
        cutoff = age_int * 10  # age x 10 ng/mL for patients > 50
        adjustment = f"Age-adjusted cutoff = age × 10 = {cutoff} ng/mL"

    return {
        "age": age_int,
        "baseline_cutoff": baseline,
        "age_adjusted_cutoff": cutoff,
        "adjustment_explanation": adjustment,
        "interpretation": f"D-dimer < {cutoff} ng/mL can help exclude PE in patients with low/intermediate clinical probability",
    }


# =============================================================================
# HYPERTENSION TOOLS (ESC 2024)
# =============================================================================

def tool_classify_blood_pressure(
    systolic: str,
    diastolic: str,
) -> Dict[str, Any]:
    """
    Classify blood pressure according to ESC 2024 guidelines.

    Args:
        systolic: Systolic blood pressure (mmHg)
        diastolic: Diastolic blood pressure (mmHg)

    Returns:
        BP category, interpretation, and recommendations
    """
    from cardiocode.guidelines.hypertension.diagnosis import classify_blood_pressure

    result = classify_blood_pressure(
        systolic=_to_int(systolic, 120) or 120,
        diastolic=_to_int(diastolic, 80) or 80,
    )

    return {
        "systolic": result.systolic,
        "diastolic": result.diastolic,
        "category": result.category.value,
        "interpretation": result.interpretation,
        "requires_confirmation": result.requires_confirmation,
        "recommendation": result.recommendation,
    }


def tool_assess_hypertension_risk(
    systolic: str,
    diastolic: str,
    age: str,
    male: str = "true",
    smoking: str = "false",
    diabetes: str = "false",
    dyslipidemia: str = "false",
    obesity: str = "false",
    family_history_cvd: str = "false",
    lvh: str = "false",
    ckd: str = "false",
    established_cvd: str = "false",
) -> Dict[str, Any]:
    """
    Assess cardiovascular risk in hypertension per ESC 2024 guidelines.

    Args:
        systolic: Systolic BP (mmHg)
        diastolic: Diastolic BP (mmHg)
        age: Patient age
        male: Male sex
        smoking: Current smoker
        diabetes: Diabetes mellitus
        dyslipidemia: Dyslipidemia
        obesity: BMI >= 30
        family_history_cvd: Family history of premature CVD
        lvh: Left ventricular hypertrophy
        ckd: Chronic kidney disease stage 3+
        established_cvd: Established cardiovascular disease

    Returns:
        CV risk category and treatment recommendations
    """
    from cardiocode.guidelines.hypertension.diagnosis import classify_blood_pressure, assess_cv_risk

    bp_result = classify_blood_pressure(
        systolic=_to_int(systolic, 140) or 140,
        diastolic=_to_int(diastolic, 90) or 90,
    )

    risk_result = assess_cv_risk(
        bp_category=bp_result.category,
        age=_to_int(age, 50) or 50,
        male=_to_bool(male),
        smoking=_to_bool(smoking),
        diabetes=_to_bool(diabetes),
        dyslipidemia=_to_bool(dyslipidemia),
        obesity=_to_bool(obesity),
        family_history_cvd=_to_bool(family_history_cvd),
        lvh=_to_bool(lvh),
        ckd_stage_3=_to_bool(ckd),
        coronary_artery_disease=_to_bool(established_cvd),
    )

    return {
        "bp_category": bp_result.category.value,
        "cv_risk_category": risk_result.risk_category.value,
        "risk_factors": risk_result.risk_factors,
        "hmod": risk_result.hmod,
        "established_cvd": risk_result.established_cvd,
        "interpretation": risk_result.interpretation,
        "treatment_threshold": risk_result.treatment_threshold,
    }


# =============================================================================
# CV PREVENTION TOOLS (ESC 2021)
# =============================================================================

def tool_calculate_score2(
    age: str,
    sex: str,
    smoking: str = "false",
    systolic_bp: str = "120",
    non_hdl_cholesterol: str = "4.0",
    region: str = "moderate",
) -> Dict[str, Any]:
    """
    Calculate SCORE2 10-year cardiovascular risk (ages 40-69).

    Args:
        age: Patient age (40-69 years)
        sex: "male" or "female"
        smoking: Current smoker
        systolic_bp: Systolic blood pressure (mmHg)
        non_hdl_cholesterol: Non-HDL cholesterol (mmol/L)
        region: European risk region (low, moderate, high, very_high)

    Returns:
        10-year CV risk percentage and risk category
    """
    from cardiocode.guidelines.cv_prevention.risk_assessment import calculate_score2, RiskRegion

    region_map = {
        "low": RiskRegion.LOW,
        "moderate": RiskRegion.MODERATE,
        "high": RiskRegion.HIGH,
        "very_high": RiskRegion.VERY_HIGH,
    }

    result = calculate_score2(
        age=_to_int(age, 50) or 50,
        sex=_to_str(sex, "male") or "male",
        smoking=_to_bool(smoking),
        systolic_bp=_to_int(systolic_bp, 120) or 120,
        non_hdl_cholesterol=_to_float(non_hdl_cholesterol, 4.0) or 4.0,
        region=region_map.get(region.lower(), RiskRegion.MODERATE),
    )

    return {
        "risk_percent": result.risk_percent,
        "risk_level": result.risk_level.value,
        "interpretation": result.interpretation,
        "recommendations": result.recommendations,
        "components": result.components,
    }


def tool_get_lipid_targets(
    risk_level: str,
) -> Dict[str, Any]:
    """
    Get LDL-C targets based on cardiovascular risk level.

    Args:
        risk_level: CV risk level (low_to_moderate, high, very_high)

    Returns:
        LDL-C targets in mmol/L and mg/dL
    """
    from cardiocode.guidelines.cv_prevention.risk_assessment import CVRiskLevel
    from cardiocode.guidelines.cv_prevention.treatment import get_lipid_targets

    level_map = {
        "low": CVRiskLevel.LOW_MODERATE,
        "low_to_moderate": CVRiskLevel.LOW_MODERATE,
        "moderate": CVRiskLevel.LOW_MODERATE,
        "high": CVRiskLevel.HIGH,
        "very_high": CVRiskLevel.VERY_HIGH,
    }

    level = level_map.get(risk_level.lower(), CVRiskLevel.LOW_MODERATE)
    result = get_lipid_targets(level)

    return {
        "risk_level": level.value,
        "ldl_target_mmol": result.ldl_target_mmol,
        "ldl_target_mg_dl": result.ldl_target_mg,
        "ldl_reduction_percent": result.ldl_reduction_percent,
        "additional_targets": result.additional_targets,
    }


# =============================================================================
# PERIPHERAL ARTERIAL DISEASE TOOLS (ESC 2024)
# =============================================================================

def tool_calculate_abi(
    ankle_systolic_right: str = "",
    ankle_systolic_left: str = "",
    brachial_systolic: str = "120",
) -> Dict[str, Any]:
    """
    Calculate Ankle-Brachial Index (ABI) for PAD diagnosis.

    Args:
        ankle_systolic_right: Right ankle systolic pressure (mmHg)
        ankle_systolic_left: Left ankle systolic pressure (mmHg)
        brachial_systolic: Higher arm systolic pressure (mmHg)

    Returns:
        ABI values with interpretation and PAD diagnosis
    """
    from cardiocode.guidelines.peripheral_arterial.diagnosis import calculate_abi

    result = calculate_abi(
        ankle_systolic_right=_to_int(ankle_systolic_right) if ankle_systolic_right else None,
        ankle_systolic_left=_to_int(ankle_systolic_left) if ankle_systolic_left else None,
        brachial_systolic=_to_int(brachial_systolic, 120) or 120,
    )

    return {
        "abi_right": result.abi_right,
        "abi_left": result.abi_left,
        "interpretation": result.interpretation,
        "pad_present": result.pad_present,
        "severity": result.severity,
        "recommendations": result.recommendations,
    }


def tool_assess_aaa(
    diameter_cm: str,
    male: str = "true",
    growth_rate_cm_year: str = "",
    symptomatic: str = "false",
) -> Dict[str, Any]:
    """
    Assess abdominal aortic aneurysm (AAA) and determine management.

    Args:
        diameter_cm: Maximum aortic diameter (cm)
        male: Male patient (females have lower intervention threshold)
        growth_rate_cm_year: Growth rate if known (cm/year)
        symptomatic: Symptomatic AAA (pain, tenderness)

    Returns:
        AAA classification, surveillance interval, and intervention recommendation
    """
    from cardiocode.guidelines.peripheral_arterial.diagnosis import classify_aaa

    result = classify_aaa(
        diameter_cm=_to_float(diameter_cm, 3.0) or 3.0,
        male=_to_bool(male),
        growth_rate_cm_year=_to_float(growth_rate_cm_year) if growth_rate_cm_year else None,
        symptomatic=_to_bool(symptomatic),
    )

    return {
        "diameter_cm": result.diameter_cm,
        "size_category": result.size_category.value,
        "growth_rate": result.growth_rate_cm_year,
        "intervention_threshold_reached": result.intervention_threshold,
        "surveillance_interval": result.surveillance_interval,
        "recommendations": result.recommendations,
    }


# =============================================================================
# SYNCOPE TOOLS (ESC 2018)
# =============================================================================

def tool_assess_syncope_risk(
    age: str,
    known_heart_disease: str = "false",
    heart_failure: str = "false",
    abnormal_ecg: str = "false",
    syncope_during_exertion: str = "false",
    syncope_supine: str = "false",
    palpitations_before: str = "false",
    family_history_scd: str = "false",
    systolic_bp: str = "",
    heart_rate: str = "",
) -> Dict[str, Any]:
    """
    Risk stratify syncope for disposition decisions (ESC 2018).

    Args:
        age: Patient age
        known_heart_disease: Structural heart disease
        heart_failure: Heart failure
        abnormal_ecg: ECG abnormalities
        syncope_during_exertion: Exertional syncope
        syncope_supine: Syncope while supine
        palpitations_before: Palpitations before event
        family_history_scd: Family SCD <40 years
        systolic_bp: Systolic BP (mmHg)
        heart_rate: Heart rate (bpm)

    Returns:
        Risk level (low/intermediate/high) and disposition recommendation
    """
    from cardiocode.guidelines.syncope.diagnosis import assess_risk

    result = assess_risk(
        age=_to_int(age, 50) or 50,
        known_heart_disease=_to_bool(known_heart_disease),
        known_heart_failure=_to_bool(heart_failure),
        abnormal_ecg=_to_bool(abnormal_ecg),
        syncope_during_exertion=_to_bool(syncope_during_exertion),
        syncope_supine=_to_bool(syncope_supine),
        palpitations_before=_to_bool(palpitations_before),
        family_history_scd=_to_bool(family_history_scd),
        systolic_bp=_to_int(systolic_bp) if systolic_bp else None,
        heart_rate=_to_int(heart_rate) if heart_rate else None,
    )

    return {
        "risk_level": result.risk_level.value,
        "high_risk_features": result.high_risk_features,
        "low_risk_features": result.low_risk_features,
        "disposition": result.disposition,
        "recommendations": result.recommendations,
    }


def tool_classify_syncope(
    prodrome_autonomic: str = "false",
    trigger_standing: str = "false",
    trigger_emotion_pain: str = "false",
    trigger_situational: str = "false",
    exertional: str = "false",
    supine_onset: str = "false",
    palpitations_before: str = "false",
    known_heart_disease: str = "false",
    abnormal_ecg: str = "false",
) -> Dict[str, Any]:
    """
    Classify syncope etiology based on clinical features.

    Args:
        prodrome_autonomic: Autonomic prodrome (nausea, warmth, sweating)
        trigger_standing: Triggered by prolonged standing
        trigger_emotion_pain: Triggered by pain, emotion, fear
        trigger_situational: Situational (micturition, cough, defecation)
        exertional: Occurred during exertion
        supine_onset: Occurred while supine
        palpitations_before: Palpitations immediately before
        known_heart_disease: Known structural heart disease
        abnormal_ecg: Abnormal ECG

    Returns:
        Likely syncope type and recommended evaluation
    """
    from cardiocode.guidelines.syncope.diagnosis import classify_syncope

    # Determine trigger type
    trigger_type = None
    if _to_bool(trigger_situational):
        trigger_type = "situational"
    elif _to_bool(trigger_standing):
        trigger_type = "standing"
    elif _to_bool(trigger_emotion_pain):
        trigger_type = "emotion"

    result = classify_syncope(
        prodrome_present=_to_bool(prodrome_autonomic),
        prodrome_type="autonomic" if _to_bool(prodrome_autonomic) else None,
        trigger_present=trigger_type is not None,
        trigger_type=trigger_type,
        position_at_onset="supine" if _to_bool(supine_onset) else "standing" if _to_bool(trigger_standing) else None,
        known_heart_disease=_to_bool(known_heart_disease),
        palpitations_before=_to_bool(palpitations_before),
        exertional=_to_bool(exertional),
        supine_onset=_to_bool(supine_onset),
        ecg_abnormal=_to_bool(abnormal_ecg),
    )

    return {
        "syncope_type": result.syncope_type.value,
        "confidence": result.confidence,
        "supporting_features": result.supporting_features,
        "against_features": result.against_features,
        "further_testing": result.further_testing,
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
    # Pulmonary Embolism tools (ESC 2019)
    "calculate_pesi": {
        "function": tool_calculate_pesi,
        "description": "Calculate Pulmonary Embolism Severity Index (PESI) score for 30-day mortality",
    },
    "calculate_spesi": {
        "function": tool_calculate_spesi,
        "description": "Calculate Simplified PESI (sPESI) score for PE risk stratification",
    },
    "calculate_geneva_pe": {
        "function": tool_calculate_geneva_pe,
        "description": "Calculate Revised Geneva Score for PE pre-test probability",
    },
    "calculate_age_adjusted_ddimer": {
        "function": tool_age_adjusted_ddimer,
        "description": "Calculate age-adjusted D-dimer cutoff for PE exclusion",
    },
    # Hypertension tools (ESC 2024)
    "classify_blood_pressure": {
        "function": tool_classify_blood_pressure,
        "description": "Classify blood pressure according to ESC 2024 guidelines",
    },
    "assess_hypertension_risk": {
        "function": tool_assess_hypertension_risk,
        "description": "Assess cardiovascular risk in hypertension (ESC 2024)",
    },
    # CV Prevention tools (ESC 2021)
    "calculate_score2": {
        "function": tool_calculate_score2,
        "description": "Calculate SCORE2 10-year cardiovascular risk (ESC 2021)",
    },
    "get_lipid_targets": {
        "function": tool_get_lipid_targets,
        "description": "Get LDL-C targets based on cardiovascular risk level (ESC 2021)",
    },
    # Peripheral Arterial Disease tools (ESC 2024)
    "calculate_abi": {
        "function": tool_calculate_abi,
        "description": "Calculate Ankle-Brachial Index (ABI) for PAD diagnosis",
    },
    "assess_aaa": {
        "function": tool_assess_aaa,
        "description": "Assess abdominal aortic aneurysm (AAA) management (ESC 2024)",
    },
    # Syncope tools (ESC 2018)
    "assess_syncope_risk": {
        "function": tool_assess_syncope_risk,
        "description": "Risk stratify syncope for disposition decisions (ESC 2018)",
    },
    "classify_syncope": {
        "function": tool_classify_syncope,
        "description": "Classify syncope etiology based on clinical features (ESC 2018)",
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
