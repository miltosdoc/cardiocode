"""
Heart Failure Prognostic Calculators.

Based on 2021 ESC Heart Failure Guidelines.
"""

from typing import Dict, Any, Optional
import math


def calculate_maggic_score(
    age: int,
    male: bool,
    lvef: float,
    nyha_class: int,
    systolic_bp: int,
    bmi: float,
    creatinine: float,
    current_smoker: bool = False,
    diabetes: bool = False,
    copd: bool = False,
    hf_diagnosis_18_months: bool = True,
    on_beta_blocker: bool = False,
    on_acei_arb: bool = False,
) -> Dict[str, Any]:
    """
    Calculate MAGGIC (Meta-Analysis Global Group in Chronic Heart Failure) score.
    
    Predicts 1-year and 3-year mortality in heart failure patients.
    
    Args:
        age: Patient age in years
        male: Male sex
        lvef: Left ventricular ejection fraction (%)
        nyha_class: NYHA functional class (1-4)
        systolic_bp: Systolic blood pressure (mmHg)
        bmi: Body mass index (kg/m²)
        creatinine: Serum creatinine (mg/dL)
        current_smoker: Current smoking status
        diabetes: Diabetes mellitus
        copd: Chronic obstructive pulmonary disease
        hf_diagnosis_18_months: HF diagnosed ≤18 months ago (vs >18 months)
        on_beta_blocker: Currently on beta-blocker therapy
        on_acei_arb: Currently on ACE-I or ARB therapy
    
    Returns:
        MAGGIC score with mortality estimates
    """
    score = 0
    components = {}
    
    # Age points (varies by EF)
    if lvef < 30:
        if age < 55:
            age_points = 0
        elif age < 60:
            age_points = 1
        elif age < 65:
            age_points = 2
        elif age < 70:
            age_points = 4
        elif age < 75:
            age_points = 6
        elif age < 80:
            age_points = 8
        else:
            age_points = 10
    elif lvef < 40:
        if age < 55:
            age_points = 0
        elif age < 60:
            age_points = 2
        elif age < 65:
            age_points = 4
        elif age < 70:
            age_points = 6
        elif age < 75:
            age_points = 8
        elif age < 80:
            age_points = 10
        else:
            age_points = 13
    else:  # EF >= 40
        if age < 55:
            age_points = 0
        elif age < 60:
            age_points = 3
        elif age < 65:
            age_points = 5
        elif age < 70:
            age_points = 7
        elif age < 75:
            age_points = 9
        elif age < 80:
            age_points = 12
        else:
            age_points = 15
    
    score += age_points
    components["age"] = age_points
    
    # LVEF points
    if lvef < 20:
        ef_points = 7
    elif lvef < 25:
        ef_points = 6
    elif lvef < 30:
        ef_points = 5
    elif lvef < 35:
        ef_points = 3
    elif lvef < 40:
        ef_points = 2
    else:
        ef_points = 0
    
    score += ef_points
    components["lvef"] = ef_points
    
    # Systolic BP points (inverse relationship in HF)
    if systolic_bp < 110:
        bp_points = 5
    elif systolic_bp < 120:
        bp_points = 4
    elif systolic_bp < 130:
        bp_points = 3
    elif systolic_bp < 140:
        bp_points = 2
    elif systolic_bp < 150:
        bp_points = 1
    else:
        bp_points = 0
    
    score += bp_points
    components["systolic_bp"] = bp_points
    
    # BMI points (U-shaped relationship)
    if bmi < 15:
        bmi_points = 6
    elif bmi < 20:
        bmi_points = 5
    elif bmi < 25:
        bmi_points = 3
    elif bmi < 30:
        bmi_points = 2
    else:
        bmi_points = 0
    
    score += bmi_points
    components["bmi"] = bmi_points
    
    # Creatinine points
    if creatinine < 0.9:
        cr_points = 0
    elif creatinine < 1.1:
        cr_points = 1
    elif creatinine < 1.3:
        cr_points = 2
    elif creatinine < 1.5:
        cr_points = 3
    elif creatinine < 1.7:
        cr_points = 4
    elif creatinine < 1.9:
        cr_points = 5
    elif creatinine < 2.1:
        cr_points = 6
    elif creatinine < 2.3:
        cr_points = 7
    elif creatinine < 2.5:
        cr_points = 8
    else:
        cr_points = 9
    
    score += cr_points
    components["creatinine"] = cr_points
    
    # NYHA class points
    nyha_points = {1: 0, 2: 2, 3: 6, 4: 8}.get(nyha_class, 0)
    score += nyha_points
    components["nyha_class"] = nyha_points
    
    # Male sex
    if male:
        score += 1
        components["male"] = 1
    
    # Current smoker
    if current_smoker:
        score += 1
        components["current_smoker"] = 1
    
    # Diabetes
    if diabetes:
        score += 3
        components["diabetes"] = 3
    
    # COPD
    if copd:
        score += 2
        components["copd"] = 2
    
    # HF first diagnosed >18 months ago (protective)
    if not hf_diagnosis_18_months:
        score += 2
        components["hf_duration_over_18mo"] = 2
    
    # Not on beta-blocker (adds risk)
    if not on_beta_blocker:
        score += 3
        components["no_beta_blocker"] = 3
    
    # Not on ACE-I/ARB (adds risk)
    if not on_acei_arb:
        score += 1
        components["no_acei_arb"] = 1
    
    # Mortality estimation (approximate from MAGGIC curves)
    # These are approximations based on published data
    if score <= 10:
        mortality_1yr = "2-5%"
        mortality_3yr = "5-10%"
        risk_category = "Low"
    elif score <= 15:
        mortality_1yr = "5-10%"
        mortality_3yr = "15-25%"
        risk_category = "Low-Intermediate"
    elif score <= 20:
        mortality_1yr = "10-15%"
        mortality_3yr = "25-35%"
        risk_category = "Intermediate"
    elif score <= 25:
        mortality_1yr = "15-25%"
        mortality_3yr = "35-50%"
        risk_category = "Intermediate-High"
    elif score <= 30:
        mortality_1yr = "25-35%"
        mortality_3yr = "50-65%"
        risk_category = "High"
    else:
        mortality_1yr = ">35%"
        mortality_3yr = ">65%"
        risk_category = "Very High"
    
    return {
        "score": score,
        "max_score": 50,
        "risk_category": risk_category,
        "mortality_1_year": mortality_1yr,
        "mortality_3_year": mortality_3yr,
        "components": components,
        "interpretation": f"MAGGIC score {score} indicates {risk_category.lower()} risk with estimated 1-year mortality of {mortality_1yr}",
        "note": "Consider intensification of HF therapy and close follow-up for higher risk patients",
        "source": "MAGGIC Meta-Analysis, referenced in ESC 2021 HF Guidelines"
    }


def assess_iron_deficiency_hf(
    ferritin: float,
    transferrin_saturation: float,
    hemoglobin: Optional[float] = None,
    symptomatic_hf: bool = True,
    lvef: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Assess iron deficiency in heart failure patients.
    
    Based on ESC 2021 HF Guidelines definition.
    
    Args:
        ferritin: Serum ferritin in µg/L (ng/mL)
        transferrin_saturation: TSAT in %
        hemoglobin: Hemoglobin in g/dL (optional)
        symptomatic_hf: Patient has symptomatic HF
        lvef: LVEF % (optional)
    
    Returns:
        Iron deficiency diagnosis and IV iron recommendation
    """
    # ESC definition of iron deficiency
    iron_deficient = ferritin < 100 or (ferritin < 300 and transferrin_saturation < 20)
    
    # Absolute vs functional iron deficiency
    if ferritin < 100:
        deficiency_type = "Absolute iron deficiency"
    elif ferritin < 300 and transferrin_saturation < 20:
        deficiency_type = "Functional iron deficiency"
    else:
        deficiency_type = "No iron deficiency by ESC criteria"
    
    # Anemia assessment
    if hemoglobin:
        anemic = hemoglobin < 13.0 if True else hemoglobin < 12.0  # Male vs female threshold simplified
    else:
        anemic = None
    
    # IV iron indication
    if iron_deficient and symptomatic_hf:
        if lvef and lvef < 50:
            iv_iron_recommendation = "Class IIa"
            iv_iron_text = "IV iron (FCM or iron derisomaltose) should be considered to improve symptoms, exercise capacity, and quality of life"
        else:
            iv_iron_recommendation = "Class IIa"
            iv_iron_text = "IV iron should be considered in symptomatic HF with iron deficiency"
    else:
        iv_iron_recommendation = "Not indicated"
        iv_iron_text = "Iron deficiency criteria not met or patient asymptomatic"
    
    # Hospitalization consideration
    if iron_deficient:
        hospitalization_note = "IV iron (FCM) should be considered in patients hospitalized for acute HF to reduce risk of HF hospitalization (Class IIa)"
    else:
        hospitalization_note = None
    
    return {
        "iron_deficient": iron_deficient,
        "deficiency_type": deficiency_type,
        "parameters": {
            "ferritin": ferritin,
            "transferrin_saturation": transferrin_saturation,
            "hemoglobin": hemoglobin,
        },
        "criteria": {
            "ferritin_threshold": "<100 µg/L (absolute) or <300 µg/L with TSAT <20% (functional)",
            "met": iron_deficient
        },
        "anemic": anemic,
        "iv_iron_recommendation": iv_iron_recommendation,
        "iv_iron_text": iv_iron_text,
        "hospitalization_note": hospitalization_note,
        "preferred_agents": ["Ferric carboxymaltose (FCM)", "Iron derisomaltose (iron isomaltoside)"],
        "source": "ESC 2021 HF Guidelines"
    }


def classify_hf_phenotype(
    lvef: float,
    bnp: Optional[float] = None,
    nt_probnp: Optional[float] = None,
    structural_abnormality: bool = False,
    diastolic_dysfunction: bool = False,
) -> Dict[str, Any]:
    """
    Classify heart failure phenotype by LVEF.
    
    Args:
        lvef: Left ventricular ejection fraction (%)
        bnp: BNP in pg/mL (optional)
        nt_probnp: NT-proBNP in pg/mL (optional)
        structural_abnormality: Evidence of structural heart disease
        diastolic_dysfunction: Evidence of diastolic dysfunction
    
    Returns:
        HF phenotype classification
    """
    # LVEF-based classification
    if lvef <= 40:
        phenotype = "HFrEF"
        full_name = "Heart Failure with Reduced Ejection Fraction"
        treatment_pillars = [
            "ACE-I/ARNI (Class I)",
            "Beta-blocker (Class I)", 
            "MRA (Class I)",
            "SGLT2 inhibitor (Class I)",
            "Loop diuretics for congestion",
            "Consider ICD/CRT based on criteria"
        ]
    elif lvef <= 49:
        phenotype = "HFmrEF"
        full_name = "Heart Failure with Mildly Reduced Ejection Fraction"
        treatment_pillars = [
            "SGLT2 inhibitor (Class IIa)",
            "ACE-I/ARB/ARNI (Class IIb)",
            "Beta-blocker (Class IIb)",
            "MRA (Class IIb)",
            "Diuretics for congestion",
            "Treat underlying etiology"
        ]
    else:
        phenotype = "HFpEF"
        full_name = "Heart Failure with Preserved Ejection Fraction"
        treatment_pillars = [
            "SGLT2 inhibitor (Class IIa)",
            "Diuretics for congestion (Class I)",
            "Treat underlying causes and comorbidities (Class I)",
            "Screen for specific etiologies (amyloidosis, HCM)",
            "Exercise rehabilitation"
        ]
    
    # Natriuretic peptide assessment
    np_elevated = False
    if bnp and bnp > 35:
        np_elevated = True
    if nt_probnp and nt_probnp > 125:
        np_elevated = True
    
    # Diagnostic criteria notes
    if phenotype == "HFpEF":
        diagnostic_notes = [
            "HFpEF diagnosis requires: symptoms/signs + LVEF ≥50% + elevated NPs + objective evidence of cardiac dysfunction",
            "Consider H2FPEF or HFA-PEFF scores for diagnostic uncertainty",
            "Rule out non-cardiac causes of symptoms"
        ]
    else:
        diagnostic_notes = [
            f"{phenotype} diagnosis: symptoms/signs + LVEF {'≤40%' if phenotype == 'HFrEF' else '41-49%'}",
            "Elevated natriuretic peptides support diagnosis but not required if clear structural abnormality"
        ]
    
    return {
        "phenotype": phenotype,
        "full_name": full_name,
        "lvef": lvef,
        "natriuretic_peptides_elevated": np_elevated,
        "treatment_pillars": treatment_pillars,
        "diagnostic_notes": diagnostic_notes,
        "thresholds": {
            "HFrEF": "LVEF ≤40%",
            "HFmrEF": "LVEF 41-49%",
            "HFpEF": "LVEF ≥50%"
        },
        "source": "ESC 2021 HF Guidelines"
    }
