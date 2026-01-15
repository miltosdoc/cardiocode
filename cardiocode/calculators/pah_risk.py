"""
Pulmonary Arterial Hypertension Risk Calculators.

Based on 2022 ESC/ERS Pulmonary Hypertension Guidelines.
"""

from typing import Dict, Any, Optional, List
import math


def calculate_pah_baseline_risk(
    who_functional_class: int,
    six_min_walk_distance: Optional[int] = None,
    bnp: Optional[float] = None,
    nt_probnp: Optional[float] = None,
    ra_area: Optional[float] = None,
    tapse_spap_ratio: Optional[float] = None,
    pericardial_effusion: str = "none",
    rap: Optional[float] = None,
    cardiac_index: Optional[float] = None,
    svi: Optional[float] = None,
    svo2: Optional[float] = None,
    rv_failure_signs: bool = False,
    symptom_progression: str = "stable",
    syncope: str = "none",
) -> Dict[str, Any]:
    """
    Calculate PAH risk at baseline using 3-strata model.
    
    Estimates 1-year mortality risk at time of diagnosis.
    
    Args:
        who_functional_class: WHO-FC I-IV
        six_min_walk_distance: 6MWD in meters
        bnp: BNP in ng/L (pg/mL)
        nt_probnp: NT-proBNP in ng/L (pg/mL)
        ra_area: Right atrial area in cm²
        tapse_spap_ratio: TAPSE/sPAP ratio (mm/mmHg)
        pericardial_effusion: "none", "minimal", "moderate", "large"
        rap: Right atrial pressure in mmHg
        cardiac_index: CI in L/min/m²
        svi: Stroke volume index in mL/m²
        svo2: Mixed venous oxygen saturation (%)
        rv_failure_signs: Clinical signs of right ventricular failure
        symptom_progression: "stable", "slow", "rapid"
        syncope: "none", "occasional", "repeated"
    
    Returns:
        Risk category and 1-year mortality estimate
    """
    risk_points = []
    assessments = {}
    
    # WHO Functional Class
    if who_functional_class in [1, 2]:
        risk_points.append(1)
        assessments["who_fc"] = {"value": who_functional_class, "risk": "low"}
    elif who_functional_class == 3:
        risk_points.append(2)
        assessments["who_fc"] = {"value": who_functional_class, "risk": "intermediate"}
    elif who_functional_class == 4:
        risk_points.append(3)
        assessments["who_fc"] = {"value": who_functional_class, "risk": "high"}
    
    # 6MWD
    if six_min_walk_distance is not None:
        if six_min_walk_distance > 440:
            risk_points.append(1)
            assessments["6mwd"] = {"value": six_min_walk_distance, "risk": "low"}
        elif six_min_walk_distance >= 165:
            risk_points.append(2)
            assessments["6mwd"] = {"value": six_min_walk_distance, "risk": "intermediate"}
        else:
            risk_points.append(3)
            assessments["6mwd"] = {"value": six_min_walk_distance, "risk": "high"}
    
    # BNP
    if bnp is not None:
        if bnp < 50:
            risk_points.append(1)
            assessments["bnp"] = {"value": bnp, "risk": "low"}
        elif bnp <= 800:
            risk_points.append(2)
            assessments["bnp"] = {"value": bnp, "risk": "intermediate"}
        else:
            risk_points.append(3)
            assessments["bnp"] = {"value": bnp, "risk": "high"}
    
    # NT-proBNP
    if nt_probnp is not None:
        if nt_probnp < 300:
            risk_points.append(1)
            assessments["nt_probnp"] = {"value": nt_probnp, "risk": "low"}
        elif nt_probnp <= 1100:
            risk_points.append(2)
            assessments["nt_probnp"] = {"value": nt_probnp, "risk": "intermediate"}
        else:
            risk_points.append(3)
            assessments["nt_probnp"] = {"value": nt_probnp, "risk": "high"}
    
    # RA area
    if ra_area is not None:
        if ra_area < 18:
            risk_points.append(1)
            assessments["ra_area"] = {"value": ra_area, "risk": "low"}
        elif ra_area <= 26:
            risk_points.append(2)
            assessments["ra_area"] = {"value": ra_area, "risk": "intermediate"}
        else:
            risk_points.append(3)
            assessments["ra_area"] = {"value": ra_area, "risk": "high"}
    
    # TAPSE/sPAP ratio
    if tapse_spap_ratio is not None:
        if tapse_spap_ratio > 0.32:
            risk_points.append(1)
            assessments["tapse_spap"] = {"value": tapse_spap_ratio, "risk": "low"}
        elif tapse_spap_ratio >= 0.19:
            risk_points.append(2)
            assessments["tapse_spap"] = {"value": tapse_spap_ratio, "risk": "intermediate"}
        else:
            risk_points.append(3)
            assessments["tapse_spap"] = {"value": tapse_spap_ratio, "risk": "high"}
    
    # Pericardial effusion
    if pericardial_effusion == "none":
        risk_points.append(1)
        assessments["pericardial_effusion"] = {"value": pericardial_effusion, "risk": "low"}
    elif pericardial_effusion == "minimal":
        risk_points.append(2)
        assessments["pericardial_effusion"] = {"value": pericardial_effusion, "risk": "intermediate"}
    else:
        risk_points.append(3)
        assessments["pericardial_effusion"] = {"value": pericardial_effusion, "risk": "high"}
    
    # RAP (hemodynamic)
    if rap is not None:
        if rap < 8:
            risk_points.append(1)
            assessments["rap"] = {"value": rap, "risk": "low"}
        elif rap <= 14:
            risk_points.append(2)
            assessments["rap"] = {"value": rap, "risk": "intermediate"}
        else:
            risk_points.append(3)
            assessments["rap"] = {"value": rap, "risk": "high"}
    
    # Cardiac index
    if cardiac_index is not None:
        if cardiac_index >= 2.5:
            risk_points.append(1)
            assessments["cardiac_index"] = {"value": cardiac_index, "risk": "low"}
        elif cardiac_index >= 2.0:
            risk_points.append(2)
            assessments["cardiac_index"] = {"value": cardiac_index, "risk": "intermediate"}
        else:
            risk_points.append(3)
            assessments["cardiac_index"] = {"value": cardiac_index, "risk": "high"}
    
    # SVI
    if svi is not None:
        if svi > 38:
            risk_points.append(1)
            assessments["svi"] = {"value": svi, "risk": "low"}
        elif svi >= 31:
            risk_points.append(2)
            assessments["svi"] = {"value": svi, "risk": "intermediate"}
        else:
            risk_points.append(3)
            assessments["svi"] = {"value": svi, "risk": "high"}
    
    # SvO2
    if svo2 is not None:
        if svo2 > 65:
            risk_points.append(1)
            assessments["svo2"] = {"value": svo2, "risk": "low"}
        elif svo2 >= 60:
            risk_points.append(2)
            assessments["svo2"] = {"value": svo2, "risk": "intermediate"}
        else:
            risk_points.append(3)
            assessments["svo2"] = {"value": svo2, "risk": "high"}
    
    # RV failure signs
    if rv_failure_signs:
        risk_points.append(3)
        assessments["rv_failure_signs"] = {"value": True, "risk": "high"}
    else:
        risk_points.append(1)
        assessments["rv_failure_signs"] = {"value": False, "risk": "low"}
    
    # Symptom progression
    if symptom_progression == "stable":
        risk_points.append(1)
        assessments["symptom_progression"] = {"value": symptom_progression, "risk": "low"}
    elif symptom_progression == "slow":
        risk_points.append(2)
        assessments["symptom_progression"] = {"value": symptom_progression, "risk": "intermediate"}
    else:
        risk_points.append(3)
        assessments["symptom_progression"] = {"value": symptom_progression, "risk": "high"}
    
    # Syncope
    if syncope == "none":
        risk_points.append(1)
        assessments["syncope"] = {"value": syncope, "risk": "low"}
    elif syncope == "occasional":
        risk_points.append(2)
        assessments["syncope"] = {"value": syncope, "risk": "intermediate"}
    else:
        risk_points.append(3)
        assessments["syncope"] = {"value": syncope, "risk": "high"}
    
    # Calculate average risk score
    if risk_points:
        avg_score = sum(risk_points) / len(risk_points)
    else:
        avg_score = 2.0  # Default to intermediate if no data
    
    # Determine risk category
    if avg_score < 1.5:
        risk_category = "Low"
        mortality_1yr = "<5%"
        treatment_recommendation = "Initial dual oral combination therapy (ERA + PDE5i)"
    elif avg_score < 2.5:
        risk_category = "Intermediate"
        mortality_1yr = "5-20%"
        treatment_recommendation = "Initial dual oral combination therapy; consider triple therapy if high-intermediate"
    else:
        risk_category = "High"
        mortality_1yr = ">20%"
        treatment_recommendation = "Consider initial triple combination therapy including IV/SC prostacyclin"
    
    return {
        "average_score": round(avg_score, 2),
        "risk_category": risk_category,
        "mortality_1_year": mortality_1yr,
        "parameters_assessed": len(risk_points),
        "treatment_recommendation": treatment_recommendation,
        "assessments": assessments,
        "model": "3-strata baseline risk model",
        "source": "ESC/ERS 2022 PH Guidelines"
    }


def calculate_pah_followup_risk(
    who_functional_class: int,
    six_min_walk_distance: Optional[int] = None,
    bnp: Optional[float] = None,
    nt_probnp: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Calculate PAH risk at follow-up using simplified 4-strata model.
    
    Used for treatment response assessment during follow-up.
    
    Args:
        who_functional_class: WHO-FC I-IV
        six_min_walk_distance: 6MWD in meters
        bnp: BNP in ng/L (pg/mL)
        nt_probnp: NT-proBNP in ng/L (pg/mL)
    
    Returns:
        Risk stratum and management recommendation
    """
    scores = []
    components = {}
    
    # WHO Functional Class (4-strata)
    if who_functional_class in [1, 2]:
        scores.append(1)
        components["who_fc"] = {"value": who_functional_class, "points": 1}
    elif who_functional_class == 3:
        scores.append(3)
        components["who_fc"] = {"value": who_functional_class, "points": 3}
    elif who_functional_class == 4:
        scores.append(4)
        components["who_fc"] = {"value": who_functional_class, "points": 4}
    
    # 6MWD (4-strata)
    if six_min_walk_distance is not None:
        if six_min_walk_distance > 440:
            scores.append(1)
            components["6mwd"] = {"value": six_min_walk_distance, "points": 1}
        elif six_min_walk_distance >= 320:
            scores.append(2)
            components["6mwd"] = {"value": six_min_walk_distance, "points": 2}
        elif six_min_walk_distance >= 165:
            scores.append(3)
            components["6mwd"] = {"value": six_min_walk_distance, "points": 3}
        else:
            scores.append(4)
            components["6mwd"] = {"value": six_min_walk_distance, "points": 4}
    
    # BNP (4-strata)
    if bnp is not None:
        if bnp < 50:
            scores.append(1)
            components["bnp"] = {"value": bnp, "points": 1}
        elif bnp < 200:
            scores.append(2)
            components["bnp"] = {"value": bnp, "points": 2}
        elif bnp <= 800:
            scores.append(3)
            components["bnp"] = {"value": bnp, "points": 3}
        else:
            scores.append(4)
            components["bnp"] = {"value": bnp, "points": 4}
    
    # NT-proBNP (4-strata)
    if nt_probnp is not None:
        if nt_probnp < 300:
            scores.append(1)
            components["nt_probnp"] = {"value": nt_probnp, "points": 1}
        elif nt_probnp < 650:
            scores.append(2)
            components["nt_probnp"] = {"value": nt_probnp, "points": 2}
        elif nt_probnp <= 1100:
            scores.append(3)
            components["nt_probnp"] = {"value": nt_probnp, "points": 3}
        else:
            scores.append(4)
            components["nt_probnp"] = {"value": nt_probnp, "points": 4}
    
    # Calculate average and round
    if scores:
        avg_score = sum(scores) / len(scores)
        rounded_score = round(avg_score)
    else:
        avg_score = 2.5
        rounded_score = 3
    
    # 4-strata classification
    if rounded_score == 1:
        risk_stratum = "Low"
        mortality_1yr = "<5%"
        recommendation = "Continue current therapy; maintain low-risk status"
    elif rounded_score == 2:
        risk_stratum = "Intermediate-Low"
        mortality_1yr = "5-10%"
        recommendation = "Consider treatment escalation; add selexipag or switch PDE5i to riociguat"
    elif rounded_score == 3:
        risk_stratum = "Intermediate-High"
        mortality_1yr = "10-20%"
        recommendation = "Escalate therapy; add IV/SC prostacyclin; refer for lung transplant evaluation"
    else:
        risk_stratum = "High"
        mortality_1yr = ">20%"
        recommendation = "Urgent treatment escalation with IV/SC prostacyclin; expedite lung transplant evaluation"
    
    # REVEAL score correlation
    if rounded_score >= 3:
        reveal_note = "Consider calculating REVEAL score for transplant listing decisions (score ≥7 = evaluate, ≥10 = list)"
    else:
        reveal_note = None
    
    return {
        "average_score": round(avg_score, 2),
        "rounded_score": rounded_score,
        "risk_stratum": risk_stratum,
        "mortality_1_year": mortality_1yr,
        "parameters_used": len(scores),
        "recommendation": recommendation,
        "reveal_note": reveal_note,
        "components": components,
        "model": "4-strata follow-up risk model",
        "source": "ESC/ERS 2022 PH Guidelines"
    }


def classify_ph_hemodynamics(
    mean_pap: float,
    pawp: float,
    pvr: float,
    cardiac_output: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Classify pulmonary hypertension by hemodynamic definitions.
    
    Args:
        mean_pap: Mean pulmonary arterial pressure in mmHg
        pawp: Pulmonary artery wedge pressure in mmHg
        pvr: Pulmonary vascular resistance in Wood units
        cardiac_output: Cardiac output in L/min (optional)
    
    Returns:
        PH classification and diagnostic interpretation
    """
    has_ph = mean_pap > 20
    
    if not has_ph:
        classification = "No PH"
        description = "Mean PAP ≤20 mmHg - no pulmonary hypertension"
        group = None
        next_steps = ["No further PH workup indicated based on hemodynamics"]
    elif pawp <= 15 and pvr > 2:
        classification = "Pre-capillary PH"
        description = "Elevated mPAP with normal PAWP and elevated PVR"
        group = "Group 1 (PAH), Group 3 (Lung disease), Group 4 (CTEPH), or Group 5"
        next_steps = [
            "V/Q scan to rule out CTEPH (Group 4)",
            "PFTs and CT chest to evaluate for lung disease (Group 3)",
            "Evaluate for PAH risk factors (CTD, HIV, portal HTN, drugs) for Group 1",
            "Vasoreactivity testing if idiopathic/heritable PAH suspected"
        ]
    elif pawp > 15 and pvr <= 2:
        classification = "Isolated post-capillary PH (IpcPH)"
        description = "Elevated mPAP with elevated PAWP but normal PVR - consistent with left heart disease"
        group = "Group 2 (PH due to left heart disease)"
        next_steps = [
            "Focus on treatment of underlying left heart disease",
            "Optimize volume status and LV filling pressures",
            "Consider further evaluation for HFpEF, valvular disease, or LV dysfunction"
        ]
    elif pawp > 15 and pvr > 2:
        classification = "Combined post- and pre-capillary PH (CpcPH)"
        description = "Features of both left heart disease and pulmonary vascular disease"
        group = "Group 2 (with pulmonary vascular component)"
        next_steps = [
            "Treat underlying left heart disease",
            "Optimize volume status",
            "PAH-specific therapy generally not recommended",
            "Consider referral to PH center for complex cases"
        ]
    else:
        classification = "Indeterminate"
        description = "Hemodynamic pattern requires clinical correlation"
        group = "Requires further evaluation"
        next_steps = ["Clinical correlation and additional workup needed"]
    
    # Calculate additional hemodynamic parameters
    diastolic_pressure_gradient = None
    if cardiac_output:
        # Transpulmonary gradient
        tpg = mean_pap - pawp
    else:
        tpg = mean_pap - pawp if pawp else None
    
    return {
        "classification": classification,
        "description": description,
        "has_ph": has_ph,
        "suggested_group": group,
        "hemodynamics": {
            "mean_pap": mean_pap,
            "pawp": pawp,
            "pvr": pvr,
            "cardiac_output": cardiac_output,
            "transpulmonary_gradient": tpg,
        },
        "thresholds": {
            "ph": "mPAP > 20 mmHg",
            "pre_capillary": "PAWP ≤15 mmHg AND PVR >2 WU",
            "post_capillary": "PAWP >15 mmHg",
            "combined": "PAWP >15 mmHg AND PVR >2 WU"
        },
        "next_steps": next_steps,
        "source": "ESC/ERS 2022 PH Guidelines"
    }
