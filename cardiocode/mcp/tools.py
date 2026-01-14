"""
CardioCode MCP Tools.

Merges original clinical tools with new LLM-powered knowledge management tools.
"""

from __future__ import annotations
import json
from typing import Dict, Any, List, Optional, Union

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

# LLM-powered knowledge tools
from cardiocode.mcp.llm_tools import TOOL_REGISTRY_UPDATE


def _rec_set_to_dict(rec_set: RecommendationSet) -> Dict[str, Any]:
    """Convert RecommendationSet to serializable dict."""
    if rec_set is None:
        return {"error": "No recommendations available"}
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
        "max_score": result.max_score,
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
        5-year SCD risk percentage
    """
    result = calculate_hcm_scd_risk(
        age=_to_int(age, 50) or 50,
        max_wall_thickness=_to_float(max_wall_thickness, 15) or 15.0,
        la_diameter=_to_float(la_diameter, 40) or 40.0,
        max_lvot_gradient=_to_float(max_lvot_gradient, 30) or 30.0,
        family_history_scd=_to_bool(family_history_scd),
        nsvt=_to_bool(nsvt),
        unexplained_syncope=_to_bool(unexplained_syncope),
    )
    return {
        "score": result.score_value,
        "risk_percentage": result.risk_percentage,
        "interpretation": result.interpretation,
        "recommendation": result.recommendation,
        "components": result.components,
    }


# =============================================================================
# GUIDELINE-BASED TOOLS
# =============================================================================

def tool_get_hfref_treatment(
    lvef: str,
    nyha_class: str,
    age: str = "",
    has_af: str = "false",
    has_cad: str = "false",
    has_diabetes: str = "false",
    has_ckd: str = "false",
) -> Dict[str, Any]:
    """
    Get heart failure treatment recommendations (ESC 2021).
    
    Args:
        lvef: LV ejection fraction (%)
        nyha_class: NYHA functional class (1-4)
        age: Patient age
        has_af: Atrial fibrillation
        has_cad: Coronary artery disease
        has_diabetes: Diabetes mellitus
        has_ckd: Chronic kidney disease
    
    Returns:
        Treatment recommendations
    """
    result = get_hfref_treatment(
        lvef=_to_float(lvef, 40) or 40.0,
        nyha_class=NYHAClass(_to_int(nyha_class, 1) or 1),
        age=_to_int(age, 70) or 70,
        has_af=_to_bool(has_af),
        has_cad=_to_bool(has_cad),
        has_diabetes=_to_bool(has_diabetes),
        has_ckd=_to_bool(has_ckd),
    )
    return _rec_set_to_dict(result)


def tool_assess_icd_indication(
    lvef: str,
    nyha_class: str,
    etiology: str = "ischemic",
    prior_vf_vt: str = "false",
    syncope: str = "false",
    days_post_mi: str = "",
) -> Dict[str, Any]:
    """
    Assess ICD indication for SCD prevention (ESC 2022).
    
    Args:
        lvef: LV ejection fraction (%)
        nyha_class: NYHA class (1-4)
        etiology: Cardiomyopathy etiology (ischemic, non_ischemic, hcm, arvc)
        prior_vf_vt: Prior VF or sustained VT
        syncope: Unexplained syncope
        days_post_mi: Days since MI (if applicable)
    
    Returns:
        ICD indication assessment
    """
    result = hf_assess_icd(
        lvef=_to_float(lvef, 35) or 35.0,
        nyha_class=NYHAClass(_to_int(nyha_class, 1) or 1),
        etiology=etiology,
        prior_vf_vt=_to_bool(prior_vf_vt),
        syncope=_to_bool(syncope),
        days_post_mi=_to_int(days_post_mi, 40) or None,
    )
    return _rec_set_to_dict(result)


def tool_assess_aortic_stenosis(
    peak_velocity: str,
    mean_gradient: str,
    ava: str,
    lvef: str = "",
    stroke_volume_index: str = "",
) -> Dict[str, Any]:
    """
    Assess aortic stenosis severity (ESC 2021 VHD Guidelines).
    
    Args:
        peak_velocity: Peak aortic jet velocity (m/s)
        mean_gradient: Mean transvalvular gradient (mmHg)
        ava: Aortic valve area (cm2)
        lvef: LV ejection fraction (%)
        stroke_volume_index: Stroke volume index (mL/m2)
    
    Returns:
        AS severity assessment
    """
    from cardiocode.guidelines.valvular_heart_disease.aortic_stenosis import assess_aortic_stenosis
    
    result = assess_aortic_stenosis(
        peak_velocity=_to_float(peak_velocity, 4.0) or 4.0,
        mean_gradient=_to_float(mean_gradient, 40) or 40.0,
        ava=_to_float(ava, 1.0) or 1.0,
        lvef=_to_float(lvef, 60) or 60.0,
        stroke_volume_index=_to_float(stroke_volume_index, 35) or 35.0,
    )
    return _rec_set_to_dict(result)


# =============================================================================
# PDF MANAGEMENT TOOLS
# =============================================================================

def tool_cardiocode_check_new_pdfs() -> Dict[str, Any]:
    """
    Check for new guideline PDFs in source_pdfs directory.
    
    Returns:
        Detection results with any new PDFs found
    """
    results = check_for_new_pdfs()
    
    return {
        "new_pdfs": results.get("new_pdfs", []),
        "updated_pdfs": results.get("updated_pdfs", []),
        "total_pdfs": results.get("total_pdfs", 0),
        "message": results.get("message", "")
    }


def tool_cardiocode_get_pdf_status() -> Dict[str, Any]:
    """
    Get status of all guideline PDFs (processed/unprocessed).
    
    Returns:
        Status of all PDFs with processing details
    """
    from cardiocode.ingestion.pdf_watcher import cardiocode_get_pdf_status
    
    return cardiocode_get_pdf_status()


# =============================================================================
# FINAL TOOL REGISTRY MERGE
# =============================================================================

# Merge all tools including LLM-powered knowledge tools
TOOL_REGISTRY = {}

# Add existing clinical tools
CLINICAL_TOOLS = {
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
    "get_hfref_treatment": {
        "function": tool_get_hfref_treatment,
        "description": "Get heart failure treatment recommendations (ESC 2021)",
    },
    "assess_icd_indication": {
        "function": tool_assess_icd_indication,
        "description": "Assess ICD indication for SCD prevention (ESC 2022)",
    },
    "assess_aortic_stenosis": {
        "function": tool_assess_aortic_stenosis,
        "description": "Assess aortic stenosis severity (ESC 2021 VHD Guidelines)",
    },
    "cardiocode_check_new_pdfs": {
        "function": tool_cardiocode_check_new_pdfs,
        "description": "Check for new guideline PDFs in source_pdfs directory",
    },
    "cardiocode_get_pdf_status": {
        "function": tool_cardiocode_get_pdf_status,
        "description": "Get status of all guideline PDFs (processed/unprocessed)",
    },
}

# Add LLM-powered tools
TOOL_REGISTRY.update(CLINICAL_TOOLS)
TOOL_REGISTRY.update(TOOL_REGISTRY_UPDATE)


def call_tool(name: str, arguments: Dict[str, Any]) -> Any:
    """Call a tool by name with arguments."""
    if name not in TOOL_REGISTRY:
        raise ValueError(f"Unknown tool: {name}")
    
    tool_info = TOOL_REGISTRY[name]
    func = tool_info["function"]
    
    # Call the function with arguments
    return func(**arguments)