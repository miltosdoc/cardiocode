"""
CardioCode MCP Tools.

All tools exposed via the MCP server.
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


def _to_int(value: Union[str, int, None], default: int = 0) -> int:
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


def _to_float(value: Union[str, float, int, None], default: float = 0.0) -> float:
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
    # Clinical Scores
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
    
    # Clinical Assessments
    "assess_aortic_stenosis": {
        "function": tool_assess_aortic_stenosis,
        "description": "Assess aortic stenosis severity and intervention indication",
    },
    "assess_icd_indication": {
        "function": tool_assess_icd_indication,
        "description": "Assess ICD indication for sudden cardiac death prevention",
    },
    
    # Knowledge Base
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
