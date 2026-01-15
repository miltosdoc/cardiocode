"""
Pulmonary Embolism Risk Scores.

Includes PESI, sPESI, Geneva Score, and D-dimer adjustment.
Based on 2019 ESC Pulmonary Embolism Guidelines.
"""

from typing import Dict, Any, Optional


def calculate_pesi(
    age: int,
    male: bool = False,
    cancer: bool = False,
    heart_failure: bool = False,
    chronic_lung_disease: bool = False,
    pulse_rate: int = 80,
    systolic_bp: int = 120,
    respiratory_rate: int = 16,
    temperature: float = 37.0,
    altered_mental_status: bool = False,
    o2_saturation: float = 98.0,
) -> Dict[str, Any]:
    """
    Calculate Pulmonary Embolism Severity Index (PESI) score.
    
    Predicts 30-day mortality in patients with acute PE.
    
    Args:
        age: Patient age in years
        male: Male sex
        cancer: Active cancer (treatment within 6 months or palliative)
        heart_failure: History of heart failure
        chronic_lung_disease: History of chronic lung disease
        pulse_rate: Heart rate in bpm
        systolic_bp: Systolic blood pressure in mmHg
        respiratory_rate: Breaths per minute
        temperature: Body temperature in Celsius
        altered_mental_status: Disorientation, lethargy, stupor, or coma
        o2_saturation: Oxygen saturation (%)
    
    Returns:
        Score, risk class, and 30-day mortality estimate
    """
    score = age  # Age in years
    
    components = {"age": age}
    
    if male:
        score += 10
        components["male"] = 10
    
    if cancer:
        score += 30
        components["cancer"] = 30
    
    if heart_failure:
        score += 10
        components["heart_failure"] = 10
    
    if chronic_lung_disease:
        score += 10
        components["chronic_lung_disease"] = 10
    
    if pulse_rate >= 110:
        score += 20
        components["tachycardia"] = 20
    
    if systolic_bp < 100:
        score += 30
        components["hypotension"] = 30
    
    if respiratory_rate >= 30:
        score += 20
        components["tachypnea"] = 20
    
    if temperature < 36.0:
        score += 20
        components["hypothermia"] = 20
    
    if altered_mental_status:
        score += 60
        components["altered_mental_status"] = 60
    
    if o2_saturation < 90:
        score += 20
        components["hypoxemia"] = 20
    
    # Risk classification
    if score <= 65:
        risk_class = "I"
        mortality = "0-1.6%"
        risk_level = "Very Low"
    elif score <= 85:
        risk_class = "II"
        mortality = "1.7-3.5%"
        risk_level = "Low"
    elif score <= 105:
        risk_class = "III"
        mortality = "3.2-7.1%"
        risk_level = "Intermediate"
    elif score <= 125:
        risk_class = "IV"
        mortality = "4.0-11.4%"
        risk_level = "High"
    else:
        risk_class = "V"
        mortality = "10.0-24.5%"
        risk_level = "Very High"
    
    # Management recommendation
    if risk_class in ["I", "II"]:
        recommendation = "Consider early discharge or outpatient treatment if appropriate clinical and social conditions"
    elif risk_class == "III":
        recommendation = "Hospital admission recommended; consider intermediate-risk management"
    else:
        recommendation = "Hospital admission required; consider ICU level care"
    
    return {
        "score": score,
        "risk_class": risk_class,
        "risk_level": risk_level,
        "mortality_30_day": mortality,
        "recommendation": recommendation,
        "components": components,
        "source": "ESC 2019 PE Guidelines"
    }


def calculate_spesi(
    age_over_80: bool = False,
    cancer: bool = False,
    chronic_cardiopulmonary_disease: bool = False,
    pulse_over_110: bool = False,
    systolic_bp_under_100: bool = False,
    o2_saturation_under_90: bool = False,
) -> Dict[str, Any]:
    """
    Calculate Simplified Pulmonary Embolism Severity Index (sPESI).
    
    Simplified version of PESI for rapid risk stratification.
    
    Args:
        age_over_80: Age > 80 years
        cancer: Active cancer
        chronic_cardiopulmonary_disease: History of chronic heart or lung disease
        pulse_over_110: Heart rate > 110 bpm
        systolic_bp_under_100: Systolic BP < 100 mmHg
        o2_saturation_under_90: O2 saturation < 90%
    
    Returns:
        Score and risk category
    """
    score = 0
    components = {}
    
    if age_over_80:
        score += 1
        components["age_over_80"] = 1
    
    if cancer:
        score += 1
        components["cancer"] = 1
    
    if chronic_cardiopulmonary_disease:
        score += 1
        components["chronic_cardiopulmonary_disease"] = 1
    
    if pulse_over_110:
        score += 1
        components["tachycardia"] = 1
    
    if systolic_bp_under_100:
        score += 1
        components["hypotension"] = 1
    
    if o2_saturation_under_90:
        score += 1
        components["hypoxemia"] = 1
    
    if score == 0:
        risk_category = "Low"
        mortality = "1.0% (95% CI 0.0-2.1%)"
        recommendation = "Consider early discharge or outpatient treatment"
    else:
        risk_category = "High"
        mortality = "10.9% (95% CI 8.5-13.2%)"
        recommendation = "Hospital admission recommended"
    
    return {
        "score": score,
        "max_score": 6,
        "risk_category": risk_category,
        "mortality_30_day": mortality,
        "recommendation": recommendation,
        "components": components,
        "interpretation": f"sPESI = {score}: {'Low risk - may be suitable for outpatient treatment' if score == 0 else 'Not low risk - requires inpatient management'}",
        "source": "ESC 2019 PE Guidelines"
    }


def calculate_geneva_pe(
    previous_pe_dvt: bool = False,
    heart_rate: int = 80,
    surgery_fracture_past_month: bool = False,
    hemoptysis: bool = False,
    active_cancer: bool = False,
    unilateral_leg_pain: bool = False,
    dvt_signs: bool = False,
    age_over_65: bool = False,
    simplified: bool = True,
) -> Dict[str, Any]:
    """
    Calculate Revised Geneva Score for PE probability.
    
    Clinical prediction rule for pre-test probability of PE.
    
    Args:
        previous_pe_dvt: Previous PE or DVT
        heart_rate: Heart rate in bpm
        surgery_fracture_past_month: Surgery or fracture within past month
        hemoptysis: Hemoptysis present
        active_cancer: Active malignancy
        unilateral_leg_pain: Unilateral lower limb pain
        dvt_signs: Pain on deep venous palpation AND unilateral edema
        age_over_65: Age > 65 years
        simplified: Use simplified scoring (default True)
    
    Returns:
        Score and PE probability category
    """
    score = 0
    components = {}
    
    if simplified:
        # Simplified Geneva Score
        if previous_pe_dvt:
            score += 1
            components["previous_pe_dvt"] = 1
        
        if heart_rate >= 75 and heart_rate < 95:
            score += 1
            components["heart_rate_75_94"] = 1
        elif heart_rate >= 95:
            score += 2
            components["heart_rate_95_plus"] = 2
        
        if surgery_fracture_past_month:
            score += 1
            components["surgery_fracture"] = 1
        
        if hemoptysis:
            score += 1
            components["hemoptysis"] = 1
        
        if active_cancer:
            score += 1
            components["active_cancer"] = 1
        
        if unilateral_leg_pain:
            score += 1
            components["unilateral_leg_pain"] = 1
        
        if dvt_signs:
            score += 1
            components["dvt_signs"] = 1
        
        if age_over_65:
            score += 1
            components["age_over_65"] = 1
        
        # Three-level interpretation
        if score <= 1:
            probability = "Low"
            pe_prevalence = "~8%"
        elif score <= 4:
            probability = "Intermediate"
            pe_prevalence = "~28%"
        else:
            probability = "High"
            pe_prevalence = "~74%"
        
        # Two-level interpretation
        pe_likely = score >= 3
        
    else:
        # Original Geneva Score
        if previous_pe_dvt:
            score += 3
            components["previous_pe_dvt"] = 3
        
        if heart_rate >= 75 and heart_rate < 95:
            score += 3
            components["heart_rate_75_94"] = 3
        elif heart_rate >= 95:
            score += 5
            components["heart_rate_95_plus"] = 5
        
        if surgery_fracture_past_month:
            score += 2
            components["surgery_fracture"] = 2
        
        if hemoptysis:
            score += 2
            components["hemoptysis"] = 2
        
        if active_cancer:
            score += 2
            components["active_cancer"] = 2
        
        if unilateral_leg_pain:
            score += 3
            components["unilateral_leg_pain"] = 3
        
        if dvt_signs:
            score += 4
            components["dvt_signs"] = 4
        
        if age_over_65:
            score += 1
            components["age_over_65"] = 1
        
        # Three-level interpretation
        if score <= 3:
            probability = "Low"
            pe_prevalence = "~8%"
        elif score <= 10:
            probability = "Intermediate"
            pe_prevalence = "~28%"
        else:
            probability = "High"
            pe_prevalence = "~74%"
        
        # Two-level interpretation
        pe_likely = score >= 6
    
    # Next step recommendations
    if pe_likely:
        next_step = "PE likely - CTPA recommended"
    else:
        next_step = "PE unlikely - D-dimer testing; if negative, PE excluded"
    
    return {
        "score": score,
        "version": "Simplified" if simplified else "Original",
        "probability_three_level": probability,
        "pe_prevalence": pe_prevalence,
        "pe_likely_two_level": pe_likely,
        "next_step": next_step,
        "components": components,
        "source": "ESC 2019 PE Guidelines"
    }


def calculate_age_adjusted_ddimer(
    age: int,
    baseline_cutoff: int = 500,
) -> Dict[str, Any]:
    """
    Calculate age-adjusted D-dimer cutoff.
    
    For patients > 50 years, the cutoff is age × 10 µg/L.
    
    Args:
        age: Patient age in years
        baseline_cutoff: Standard D-dimer cutoff (default 500 µg/L)
    
    Returns:
        Age-adjusted cutoff value
    """
    if age > 50:
        adjusted_cutoff = age * 10
        adjustment_applied = True
    else:
        adjusted_cutoff = baseline_cutoff
        adjustment_applied = False
    
    return {
        "age": age,
        "standard_cutoff": baseline_cutoff,
        "adjusted_cutoff": adjusted_cutoff,
        "adjustment_applied": adjustment_applied,
        "unit": "µg/L (FEU)",
        "interpretation": f"D-dimer < {adjusted_cutoff} µg/L can be used to exclude PE in patients with low/intermediate pre-test probability",
        "note": "Age-adjusted D-dimer increases specificity in older patients without compromising sensitivity",
        "source": "ESC 2019 PE Guidelines"
    }
