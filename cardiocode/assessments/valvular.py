"""
Valvular Heart Disease Assessment Tools.

Based on 2025 ESC/EACTS Valvular Heart Disease Guidelines.
"""

from typing import Dict, Any, Optional, List


def assess_ar_severity(
    lvesd: float,
    lvesdi: Optional[float] = None,
    lvef: float = 60.0,
    lvesvi: Optional[float] = None,
    symptomatic: bool = False,
    undergoing_cardiac_surgery: bool = False,
    bsa: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Assess aortic regurgitation severity and intervention indication.
    
    Args:
        lvesd: Left ventricular end-systolic diameter in mm
        lvesdi: Indexed LVESD in mm/m² (calculated if BSA provided)
        lvef: Left ventricular ejection fraction (%)
        lvesvi: Indexed LVESV in mL/m² (optional)
        symptomatic: Patient has symptoms attributable to AR
        undergoing_cardiac_surgery: Undergoing CABG or ascending aorta surgery
        bsa: Body surface area in m² (optional, for indexing)
    
    Returns:
        Severity assessment and intervention recommendation
    """
    # Calculate indexed values if BSA provided
    if bsa and not lvesdi:
        lvesdi = lvesd / bsa
    
    intervention_indicated = False
    intervention_class = None
    rationale = []
    
    # Class I indications (intervention recommended)
    if symptomatic:
        intervention_indicated = True
        intervention_class = "I"
        rationale.append("Symptomatic severe AR")
    
    if lvesd > 50 or (lvesdi and lvesdi > 25):
        intervention_indicated = True
        intervention_class = "I"
        if lvesd > 50:
            rationale.append(f"LVESD >50 mm ({lvesd} mm)")
        if lvesdi and lvesdi > 25:
            rationale.append(f"LVESDi >25 mm/m² ({lvesdi:.1f} mm/m²)")
    
    if lvef <= 50:
        intervention_indicated = True
        intervention_class = "I"
        rationale.append(f"LVEF ≤50% ({lvef}%)")
    
    if undergoing_cardiac_surgery:
        intervention_indicated = True
        intervention_class = "I"
        rationale.append("Undergoing CABG or ascending aorta surgery")
    
    # Class IIb indications (may be considered if low surgical risk)
    if not intervention_indicated:
        if lvesdi and lvesdi > 22:
            intervention_class = "IIb"
            rationale.append(f"LVESDi >22 mm/m² ({lvesdi:.1f} mm/m²) - may consider if low risk")
        if lvesvi and lvesvi > 45:
            intervention_class = "IIb"
            rationale.append(f"LVESVi >45 mL/m² ({lvesvi:.1f} mL/m²) - may consider if low risk")
        if lvef <= 55 and lvef > 50:
            intervention_class = "IIb"
            rationale.append(f"LVEF 51-55% ({lvef}%) - may consider if low risk")
    
    # Determine severity
    if intervention_class == "I":
        severity = "Severe - intervention indicated"
    elif intervention_class == "IIb":
        severity = "Severe - intervention may be considered"
    else:
        severity = "Monitor with serial imaging"
    
    return {
        "severity": severity,
        "intervention_indicated": intervention_indicated,
        "intervention_class": intervention_class,
        "rationale": rationale,
        "parameters": {
            "lvesd": lvesd,
            "lvesdi": lvesdi,
            "lvef": lvef,
            "lvesvi": lvesvi,
            "symptomatic": symptomatic
        },
        "thresholds": {
            "class_I": "LVESD >50mm OR LVESDi >25mm/m² OR LVEF ≤50% OR symptomatic",
            "class_IIb": "LVESDi >22mm/m² OR LVESVi >45mL/m² OR LVEF ≤55% (if low risk)"
        },
        "follow_up": "Echo every 6-12 months for severe AR" if not intervention_indicated else "Refer for surgical evaluation",
        "source": "ESC/EACTS 2025 VHD Guidelines"
    }


def assess_mr_primary_intervention(
    lvesd: float,
    lvef: float,
    symptomatic: bool = False,
    af: bool = False,
    spap: Optional[float] = None,
    lavi: Optional[float] = None,
    la_diameter: Optional[float] = None,
    tr_moderate_or_greater: bool = False,
    lvesdi: Optional[float] = None,
    repair_likely_durable: bool = True,
    surgical_risk: str = "low",
) -> Dict[str, Any]:
    """
    Assess primary mitral regurgitation intervention indication.
    
    Args:
        lvesd: LV end-systolic diameter in mm
        lvef: LV ejection fraction (%)
        symptomatic: Patient has symptoms
        af: Atrial fibrillation present
        spap: Systolic pulmonary artery pressure at rest in mmHg
        lavi: Left atrial volume index in mL/m²
        la_diameter: Left atrial diameter in mm
        tr_moderate_or_greater: Tricuspid regurgitation ≥ moderate
        lvesdi: Indexed LVESD in mm/m²
        repair_likely_durable: Durable MV repair is likely
        surgical_risk: "low", "intermediate", "high"
    
    Returns:
        Intervention indication and recommendation
    """
    intervention_class = None
    intervention_type = None
    rationale = []
    high_risk_features = []
    
    # Count high-risk features for asymptomatic patients
    if af:
        high_risk_features.append("Atrial fibrillation")
    if spap and spap > 50:
        high_risk_features.append(f"SPAP >50 mmHg ({spap} mmHg)")
    if lavi and lavi >= 60:
        high_risk_features.append(f"LAVI ≥60 mL/m² ({lavi} mL/m²)")
    if la_diameter and la_diameter >= 55:
        high_risk_features.append(f"LA diameter ≥55 mm ({la_diameter} mm)")
    if tr_moderate_or_greater:
        high_risk_features.append("Tricuspid regurgitation ≥ moderate")
    
    # LV dysfunction criteria
    lv_dysfunction = lvesd >= 40 or (lvesdi and lvesdi >= 20) or lvef <= 60
    
    # Class I indications
    if symptomatic:
        intervention_class = "I"
        intervention_type = "Surgery (repair preferred)"
        rationale.append("Symptomatic severe PMR")
    
    if lv_dysfunction:
        intervention_class = "I"
        intervention_type = "Surgery (repair preferred)"
        if lvesd >= 40:
            rationale.append(f"LVESD ≥40 mm ({lvesd} mm)")
        if lvesdi and lvesdi >= 20:
            rationale.append(f"LVESDi ≥20 mm/m² ({lvesdi} mm/m²)")
        if lvef <= 60:
            rationale.append(f"LVEF ≤60% ({lvef}%)")
    
    # Class I for asymptomatic with ≥3 high-risk features (if durable repair likely)
    if not symptomatic and not lv_dysfunction and len(high_risk_features) >= 3:
        if repair_likely_durable and surgical_risk == "low":
            intervention_class = "I"
            intervention_type = "MV repair"
            rationale.append("Asymptomatic with ≥3 high-risk features, durable repair likely, low risk")
    
    # Class IIa for asymptomatic with some high-risk features
    if intervention_class is None and not symptomatic:
        if spap and spap > 50:
            intervention_class = "IIa"
            rationale.append(f"SPAP >50 mmHg ({spap} mmHg)")
        if af and not lv_dysfunction:
            intervention_class = "IIa"
            rationale.append("AF secondary to MR")
        if lavi and lavi >= 60 and repair_likely_durable:
            intervention_class = "IIa"
            rationale.append(f"Significant LA dilation (LAVI ≥60 mL/m²)")
    
    # High surgical risk pathway
    if surgical_risk == "high" and intervention_class:
        intervention_type = "Consider TEER if anatomy suitable"
        rationale.append("High surgical risk - consider TEER")
    
    # No intervention indicated
    if intervention_class is None:
        intervention_type = "Watchful waiting with regular follow-up"
    
    return {
        "intervention_indicated": intervention_class is not None,
        "intervention_class": intervention_class,
        "intervention_type": intervention_type,
        "rationale": rationale,
        "high_risk_features": high_risk_features,
        "high_risk_feature_count": len(high_risk_features),
        "lv_dysfunction": lv_dysfunction,
        "parameters": {
            "lvesd": lvesd,
            "lvef": lvef,
            "symptomatic": symptomatic,
            "af": af,
            "spap": spap,
            "lavi": lavi,
            "la_diameter": la_diameter,
            "tr_moderate_or_greater": tr_moderate_or_greater
        },
        "source": "ESC/EACTS 2025 VHD Guidelines"
    }


def assess_mr_secondary_teer(
    lvef: float,
    symptomatic: bool = True,
    on_gdmt: bool = True,
    crt_if_indicated: bool = True,
    hemodynamically_stable: bool = True,
    mr_severity: str = "severe",
    surgical_candidate: bool = False,
    eroa: Optional[float] = None,
    regurgitant_volume: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Assess secondary (ventricular) MR eligibility for TEER.
    
    Based on COAPT trial criteria and ESC guidelines.
    
    Args:
        lvef: LV ejection fraction (%)
        symptomatic: Patient has HF symptoms despite GDMT
        on_gdmt: On guideline-directed medical therapy
        crt_if_indicated: Has CRT if indicated
        hemodynamically_stable: Hemodynamically stable
        mr_severity: "moderate", "moderate-severe", "severe"
        surgical_candidate: Is a surgical candidate
        eroa: Effective regurgitant orifice area in cm²
        regurgitant_volume: Regurgitant volume in mL
    
    Returns:
        TEER eligibility assessment
    """
    eligible = False
    indication_class = None
    rationale = []
    concerns = []
    
    # Check core criteria
    if lvef < 50 and symptomatic and on_gdmt and hemodynamically_stable:
        if mr_severity in ["moderate-severe", "severe"]:
            eligible = True
            indication_class = "I"
            rationale.append("LVEF <50% with symptomatic severe SMR despite GDMT")
    
    # Additional checks
    if not on_gdmt:
        eligible = False
        concerns.append("Not on optimized GDMT - optimize first")
    
    if not crt_if_indicated:
        concerns.append("CRT indicated but not in place - consider CRT first")
    
    if not hemodynamically_stable:
        eligible = False
        concerns.append("Hemodynamically unstable - stabilize first")
    
    if lvef < 20:
        concerns.append("Very low LVEF (<20%) - discuss LVAD/transplant evaluation")
    
    if lvef > 50:
        eligible = False
        indication_class = None
        concerns.append("LVEF >50% - SMR likely not primary driver of symptoms")
    
    # COAPT-like criteria
    coapt_criteria_met = (
        lvef >= 20 and lvef <= 50 and
        eroa and eroa >= 0.3 and
        symptomatic and on_gdmt
    )
    
    if coapt_criteria_met:
        rationale.append("Meets COAPT-like criteria (LVEF 20-50%, EROA ≥0.3, symptomatic on GDMT)")
    
    # Alternative if not TEER candidate
    if not eligible and surgical_candidate:
        alternative = "Consider surgical MV intervention"
    elif not eligible:
        alternative = "Continue GDMT optimization; consider LVAD/transplant evaluation"
    else:
        alternative = None
    
    return {
        "teer_eligible": eligible,
        "indication_class": indication_class,
        "rationale": rationale,
        "concerns": concerns,
        "coapt_criteria_met": coapt_criteria_met,
        "alternative": alternative,
        "parameters": {
            "lvef": lvef,
            "symptomatic": symptomatic,
            "on_gdmt": on_gdmt,
            "crt_if_indicated": crt_if_indicated,
            "hemodynamically_stable": hemodynamically_stable,
            "mr_severity": mr_severity,
            "eroa": eroa,
            "regurgitant_volume": regurgitant_volume
        },
        "key_criteria": {
            "lvef": "20-50%",
            "mr_severity": "Severe (persistent despite GDMT)",
            "gdmt": "Optimized",
            "crt": "In place if indicated"
        },
        "source": "ESC/EACTS 2025 VHD Guidelines, COAPT Trial"
    }


def assess_tr_intervention(
    tr_severity: str,
    primary_or_secondary: str,
    rv_function: str = "normal",
    lv_function: str = "normal",
    pulmonary_hypertension: str = "none",
    symptomatic: bool = False,
    rv_dilatation: bool = False,
    left_sided_surgery_planned: bool = False,
    annulus_diameter: Optional[float] = None,
    surgical_risk: str = "low",
) -> Dict[str, Any]:
    """
    Assess tricuspid regurgitation intervention indication.
    
    Args:
        tr_severity: "mild", "moderate", "severe"
        primary_or_secondary: "primary" or "secondary"
        rv_function: "normal", "mild_dysfunction", "moderate_dysfunction", "severe_dysfunction"
        lv_function: "normal", "mild_dysfunction", "moderate_dysfunction", "severe_dysfunction"
        pulmonary_hypertension: "none", "mild", "moderate", "severe_precapillary"
        symptomatic: Patient has symptoms
        rv_dilatation: RV is dilated
        left_sided_surgery_planned: Undergoing left-sided valve surgery
        annulus_diameter: Tricuspid annulus diameter in mm
        surgical_risk: "low", "intermediate", "high"
    
    Returns:
        Intervention indication assessment
    """
    intervention_class = None
    intervention_type = None
    rationale = []
    contraindications = []
    
    # Annulus dilatation threshold
    annulus_dilated = annulus_diameter and (annulus_diameter >= 40 or annulus_diameter >= 21)  # 21 mm/m² indexed
    
    # Severe RV or LV dysfunction is relative contraindication
    if rv_function == "severe_dysfunction":
        contraindications.append("Severe RV dysfunction - high procedural risk")
    if lv_function in ["moderate_dysfunction", "severe_dysfunction"]:
        contraindications.append("Significant LV dysfunction - address underlying cause")
    if pulmonary_hypertension == "severe_precapillary":
        contraindications.append("Severe pre-capillary PH - TR surgery may not benefit")
    
    # Left-sided surgery context
    if left_sided_surgery_planned:
        if tr_severity == "severe":
            intervention_class = "I"
            intervention_type = "Concomitant TR surgery"
            rationale.append("Severe TR with left-sided surgery planned")
        elif tr_severity == "moderate":
            intervention_class = "IIa"
            intervention_type = "Concomitant TR surgery"
            rationale.append("Moderate TR with left-sided surgery - prevent progression")
        elif tr_severity == "mild" and annulus_dilated:
            intervention_class = "IIb"
            intervention_type = "Concomitant tricuspid annuloplasty"
            rationale.append("Mild TR with annular dilatation - may prevent progression")
    
    # Isolated TR intervention
    elif tr_severity == "severe":
        if primary_or_secondary == "primary":
            if symptomatic and rv_function != "severe_dysfunction":
                intervention_class = "I"
                intervention_type = "Surgery (repair preferred)"
                rationale.append("Symptomatic severe primary TR without severe RV dysfunction")
            elif rv_dilatation or rv_function in ["mild_dysfunction", "moderate_dysfunction"]:
                intervention_class = "IIa"
                intervention_type = "Surgery (repair preferred)"
                rationale.append("Asymptomatic severe primary TR with RV dilatation/dysfunction")
        
        elif primary_or_secondary == "secondary":
            if symptomatic and rv_function not in ["severe_dysfunction"]:
                if surgical_risk == "high":
                    intervention_class = "IIa"
                    intervention_type = "Transcatheter treatment"
                    rationale.append("Symptomatic severe secondary TR, high surgical risk")
                else:
                    intervention_class = "IIa"
                    intervention_type = "Surgery or transcatheter treatment"
                    rationale.append("Symptomatic severe secondary TR without severe RV dysfunction/PH")
    
    # No intervention
    if intervention_class is None:
        intervention_type = "Medical management and surveillance"
    
    return {
        "intervention_indicated": intervention_class is not None,
        "intervention_class": intervention_class,
        "intervention_type": intervention_type,
        "rationale": rationale,
        "contraindications": contraindications,
        "parameters": {
            "tr_severity": tr_severity,
            "primary_or_secondary": primary_or_secondary,
            "rv_function": rv_function,
            "lv_function": lv_function,
            "pulmonary_hypertension": pulmonary_hypertension,
            "symptomatic": symptomatic,
            "rv_dilatation": rv_dilatation,
            "annulus_diameter": annulus_diameter
        },
        "notes": [
            "Heart Team evaluation recommended",
            "TEER and other transcatheter options emerging for high-risk patients"
        ],
        "source": "ESC/EACTS 2025 VHD Guidelines"
    }


def assess_ms_intervention(
    mva: float,
    symptomatic: bool = False,
    favorable_anatomy_for_pmc: bool = True,
    contraindication_to_pmc: bool = False,
    af: bool = False,
    spap: Optional[float] = None,
    high_te_risk: bool = False,
    surgical_risk: str = "low",
) -> Dict[str, Any]:
    """
    Assess mitral stenosis intervention indication.
    
    Args:
        mva: Mitral valve area in cm²
        symptomatic: Patient has symptoms
        favorable_anatomy_for_pmc: Suitable for percutaneous mitral commissurotomy
        contraindication_to_pmc: Has contraindication to PMC (LA thrombus, >mild MR)
        af: Atrial fibrillation present
        spap: Systolic pulmonary artery pressure at rest in mmHg
        high_te_risk: High thromboembolic risk
        surgical_risk: "low", "intermediate", "high"
    
    Returns:
        Intervention indication and recommended approach
    """
    # Severity assessment
    if mva <= 1.0:
        severity = "Severe"
    elif mva <= 1.5:
        severity = "Moderate"
    else:
        severity = "Mild"
    
    intervention_class = None
    intervention_type = None
    rationale = []
    
    # Symptomatic severe MS
    if symptomatic and mva <= 1.5:
        if favorable_anatomy_for_pmc and not contraindication_to_pmc:
            intervention_class = "I"
            intervention_type = "Percutaneous mitral commissurotomy (PMC)"
            rationale.append("Symptomatic MS with favorable anatomy for PMC")
        elif contraindication_to_pmc or not favorable_anatomy_for_pmc:
            if surgical_risk != "high":
                intervention_class = "I"
                intervention_type = "Mitral valve surgery"
                rationale.append("Symptomatic MS not suitable for PMC")
            else:
                intervention_class = "IIa"
                intervention_type = "PMC if technically feasible"
                rationale.append("Symptomatic MS, high surgical risk - consider PMC if possible")
    
    # Asymptomatic with high-risk features
    elif not symptomatic and mva <= 1.5:
        # High thromboembolic or decompensation risk
        if high_te_risk or (spap and spap > 50) or af:
            if favorable_anatomy_for_pmc and not contraindication_to_pmc:
                intervention_class = "IIa"
                intervention_type = "PMC"
                rationale.append("Asymptomatic MS with high TE/decompensation risk, favorable PMC anatomy")
    
    # No intervention indicated
    if intervention_class is None:
        intervention_type = "Medical management with anticoagulation if AF"
    
    return {
        "severity": severity,
        "intervention_indicated": intervention_class is not None,
        "intervention_class": intervention_class,
        "intervention_type": intervention_type,
        "rationale": rationale,
        "parameters": {
            "mva": mva,
            "symptomatic": symptomatic,
            "favorable_anatomy_for_pmc": favorable_anatomy_for_pmc,
            "contraindication_to_pmc": contraindication_to_pmc,
            "af": af,
            "spap": spap
        },
        "notes": [
            "PMC contraindications: LA thrombus, >mild MR, unfavorable anatomy (heavy calcification)",
            "Consider OAC for AF or prior embolism"
        ],
        "source": "ESC/EACTS 2025 VHD Guidelines"
    }


def assess_valve_type_selection(
    age: int,
    valve_position: str,
    oac_contraindicated: bool = False,
    quality_oac_achievable: bool = True,
    high_bleeding_risk: bool = False,
    patient_preference_mechanical: bool = False,
    female_contemplating_pregnancy: bool = False,
    pre_existing_mechanical_valve: bool = False,
    life_expectancy: str = "normal",
) -> Dict[str, Any]:
    """
    Assess mechanical vs biological valve selection.
    
    Args:
        age: Patient age in years
        valve_position: "aortic", "mitral", "tricuspid"
        oac_contraindicated: Anticoagulation is contraindicated
        quality_oac_achievable: Good quality OAC monitoring achievable
        high_bleeding_risk: High bleeding risk
        patient_preference_mechanical: Patient prefers mechanical valve
        female_contemplating_pregnancy: Woman contemplating pregnancy
        pre_existing_mechanical_valve: Has mechanical valve in another position
        life_expectancy: "short", "normal", "long"
    
    Returns:
        Valve type recommendation
    """
    mhv_favored = []
    bhv_favored = []
    recommendation = None
    recommendation_class = None
    
    # Strong mechanical valve indicators
    if pre_existing_mechanical_valve:
        mhv_favored.append("Pre-existing mechanical valve in another position")
        recommendation = "Mechanical valve"
        recommendation_class = "IIa"
    
    if patient_preference_mechanical and quality_oac_achievable and not high_bleeding_risk:
        mhv_favored.append("Patient preference for mechanical valve")
    
    if life_expectancy == "long" and not oac_contraindicated:
        mhv_favored.append("Long life expectancy")
    
    # Strong biological valve indicators
    if oac_contraindicated:
        bhv_favored.append("Anticoagulation contraindicated")
        recommendation = "Biological valve"
        recommendation_class = "I"
    
    if high_bleeding_risk:
        bhv_favored.append("High bleeding risk")
    
    if female_contemplating_pregnancy:
        bhv_favored.append("Woman contemplating pregnancy")
    
    if not quality_oac_achievable:
        bhv_favored.append("Quality OAC monitoring not achievable")
    
    if life_expectancy == "short":
        bhv_favored.append("Limited life expectancy")
    
    # Age-based guidance
    if valve_position == "aortic":
        if age < 50:
            mhv_favored.append("Age <50 years - lower reop rate with MHV")
        elif age >= 65:
            bhv_favored.append("Age ≥65 years - lower bleeding risk with BHV")
        else:
            pass  # 50-64: either acceptable
    
    elif valve_position == "mitral":
        if age < 65:
            mhv_favored.append("Age <65 years for mitral position")
        else:
            bhv_favored.append("Age ≥65 years for mitral position")
    
    # Determine final recommendation
    if recommendation is None:
        if len(mhv_favored) > len(bhv_favored):
            recommendation = "Mechanical valve favored"
            recommendation_class = "IIa"
        elif len(bhv_favored) > len(mhv_favored):
            recommendation = "Biological valve favored"
            recommendation_class = "IIa"
        else:
            recommendation = "Either valve type acceptable - shared decision-making"
            recommendation_class = "Individual assessment"
    
    return {
        "recommendation": recommendation,
        "recommendation_class": recommendation_class,
        "mechanical_favored_factors": mhv_favored,
        "biological_favored_factors": bhv_favored,
        "parameters": {
            "age": age,
            "valve_position": valve_position,
            "oac_contraindicated": oac_contraindicated,
            "quality_oac_achievable": quality_oac_achievable,
            "high_bleeding_risk": high_bleeding_risk
        },
        "shared_decision_making": "Final decision should incorporate patient values and preferences after thorough discussion",
        "source": "ESC/EACTS 2025 VHD Guidelines"
    }


def calculate_inr_target_mhv(
    valve_type: str,
    valve_position: str,
    prothrombotic_factors: bool = False,
) -> Dict[str, Any]:
    """
    Calculate INR target for mechanical heart valve.
    
    Args:
        valve_type: "bileaflet", "tilting_disc", "ball_cage"
        valve_position: "aortic", "mitral", "tricuspid"
        prothrombotic_factors: Has additional factors (AF, prior TE, LA dilation, LV dysfunction, hypercoagulable)
    
    Returns:
        INR target range
    """
    # Base thrombogenicity
    if valve_type == "ball_cage":
        valve_thrombogenicity = "high"
    elif valve_type == "tilting_disc":
        valve_thrombogenicity = "medium"
    else:  # bileaflet
        valve_thrombogenicity = "low"
    
    # Position risk
    if valve_position in ["mitral", "tricuspid"]:
        position_risk = "high"
    else:
        position_risk = "standard"
    
    # Determine target
    if valve_type == "bileaflet" and valve_position == "aortic":
        if prothrombotic_factors:
            inr_target = 3.0
            inr_range = "2.5-3.5"
        else:
            inr_target = 2.5
            inr_range = "2.0-3.0"
    elif valve_type in ["tilting_disc", "ball_cage"] or valve_position in ["mitral", "tricuspid"]:
        if prothrombotic_factors:
            inr_target = 3.5
            inr_range = "3.0-4.0"
        else:
            inr_target = 3.0
            inr_range = "2.5-3.5"
    else:
        inr_target = 3.0
        inr_range = "2.5-3.5"
    
    return {
        "inr_target": inr_target,
        "inr_range": inr_range,
        "parameters": {
            "valve_type": valve_type,
            "valve_position": valve_position,
            "prothrombotic_factors": prothrombotic_factors
        },
        "prothrombotic_factors_include": [
            "Atrial fibrillation",
            "Prior thromboembolism",
            "LA dilatation",
            "LV dysfunction",
            "Hypercoagulable state"
        ],
        "notes": [
            "Self-monitoring and self-management improve TTR and outcomes",
            "Patient education on OAC is essential (Class I)"
        ],
        "source": "ESC/EACTS 2025 VHD Guidelines"
    }
