"""
Cardio-Oncology Assessment Tools.

Based on 2022 ESC Cardio-Oncology Guidelines.
"""

from typing import Dict, Any, Optional, List


def assess_cardio_oncology_baseline_risk(
    age: int,
    prior_hf_cardiomyopathy: bool = False,
    prior_cad: bool = False,
    prior_vhd_severe: bool = False,
    baseline_lvef: float = 60.0,
    hypertension: bool = False,
    diabetes: bool = False,
    ckd: bool = False,
    current_smoker: bool = False,
    obesity: bool = False,
    prior_anthracycline: bool = False,
    prior_chest_rt: bool = False,
    elevated_baseline_troponin: bool = False,
    elevated_baseline_np: bool = False,
    planned_treatment: str = "anthracycline",
) -> Dict[str, Any]:
    """
    Assess baseline cardiovascular risk before cardiotoxic cancer therapy.
    
    Based on HFA-ICOS risk stratification.
    
    Args:
        age: Patient age in years
        prior_hf_cardiomyopathy: Prior HF or cardiomyopathy
        prior_cad: Prior CAD (MI, PCI, CABG)
        prior_vhd_severe: Severe valvular heart disease
        baseline_lvef: Baseline LVEF (%)
        hypertension: History of hypertension
        diabetes: Diabetes mellitus
        ckd: Chronic kidney disease
        current_smoker: Current smoker
        obesity: BMI ≥30
        prior_anthracycline: Prior anthracycline exposure
        prior_chest_rt: Prior chest/mediastinal radiotherapy
        elevated_baseline_troponin: Elevated troponin at baseline
        elevated_baseline_np: Elevated natriuretic peptide at baseline
        planned_treatment: "anthracycline", "her2", "vegfi", "ici", "proteasome_inhibitor"
    
    Returns:
        Risk category and monitoring recommendations
    """
    very_high_factors = []
    high_factors = []
    moderate_factors = []
    
    # Very High risk factors
    if prior_hf_cardiomyopathy:
        very_high_factors.append("Prior HF/cardiomyopathy")
    
    # High risk factors
    if prior_cad:
        high_factors.append("Prior CAD")
    if prior_vhd_severe:
        high_factors.append("Severe VHD")
    if baseline_lvef < 50:
        high_factors.append(f"Baseline LVEF <50% ({baseline_lvef}%)")
    if age >= 80:
        high_factors.append(f"Age ≥80 years ({age})")
    if prior_anthracycline:
        high_factors.append("Prior anthracycline exposure")
    if prior_chest_rt:
        high_factors.append("Prior chest RT")
    
    # Moderate risk factors (M1/M2)
    if age >= 65 and age < 80:
        moderate_factors.append(f"Age 65-79 years ({age})")
    if baseline_lvef >= 50 and baseline_lvef < 55:
        moderate_factors.append(f"Borderline LVEF 50-54% ({baseline_lvef}%)")
    if hypertension:
        moderate_factors.append("Hypertension")
    if diabetes:
        moderate_factors.append("Diabetes")
    if ckd:
        moderate_factors.append("CKD")
    if current_smoker:
        moderate_factors.append("Current smoking")
    if obesity:
        moderate_factors.append("Obesity (BMI ≥30)")
    if elevated_baseline_troponin:
        moderate_factors.append("Elevated baseline troponin")
    if elevated_baseline_np:
        moderate_factors.append("Elevated baseline NP")
    
    # Determine risk category
    if len(very_high_factors) > 0:
        risk_category = "Very High"
    elif len(high_factors) > 0:
        risk_category = "High"
    elif len(moderate_factors) >= 2:
        risk_category = "Moderate"
    else:
        risk_category = "Low"
    
    # Baseline assessment recommendations
    baseline_assessments = {
        "ecg": {"recommended": True, "class": "I"},
        "troponin": {"recommended": risk_category in ["High", "Very High", "Moderate"], "class": "I" if risk_category in ["High", "Very High"] else "IIa"},
        "natriuretic_peptide": {"recommended": risk_category in ["High", "Very High", "Moderate"], "class": "I" if risk_category in ["High", "Very High"] else "IIa"},
        "echocardiography": {"recommended": True, "class": "I" if risk_category in ["High", "Very High"] else "IIa" if risk_category == "Moderate" else "IIb"},
        "gls": {"recommended": risk_category in ["High", "Very High", "Moderate"], "class": "I"},
    }
    
    # Monitoring protocol based on treatment and risk
    if planned_treatment == "anthracycline":
        if risk_category in ["High", "Very High"]:
            monitoring = {
                "echo_frequency": "Every 2 cycles + 3 months post-treatment",
                "biomarker_frequency": "Every cycle + 3 and 12 months post",
                "long_term": "Annual surveillance recommended"
            }
        elif risk_category == "Moderate":
            monitoring = {
                "echo_frequency": "After cumulative dose ≥250 mg/m² dox-equivalent",
                "biomarker_frequency": "Every 2 cycles + within 3 months post",
                "long_term": "12 months post-treatment, then risk-based"
            }
        else:
            monitoring = {
                "echo_frequency": "May consider after cumulative dose ≥250 mg/m²",
                "biomarker_frequency": "May consider every 2 cycles",
                "long_term": "12 months post-treatment recommended"
            }
    elif planned_treatment == "her2":
        monitoring = {
            "echo_frequency": "Every 3 months during treatment",
            "biomarker_frequency": "Every 2-3 cycles if high risk",
            "long_term": "12 months post-treatment"
        }
    elif planned_treatment == "vegfi":
        monitoring = {
            "echo_frequency": "Every 3 months (high risk) or 4 months (moderate)",
            "bp_monitoring": "Every visit + home monitoring",
            "long_term": "Every 6-12 months on long-term therapy"
        }
    else:
        monitoring = {
            "echo_frequency": "Per specific agent guidelines",
            "biomarker_frequency": "Risk-stratified approach",
            "long_term": "Annual review"
        }
    
    # Cardioprotection consideration
    cardioprotection = []
    if risk_category in ["High", "Very High"] and planned_treatment == "anthracycline":
        cardioprotection.append("Consider primary cardioprotection with ACE-I/ARB and/or beta-blocker (Class IIa)")
        cardioprotection.append("Consider dexrazoxane if cumulative dose high (Class IIa)")
    
    return {
        "risk_category": risk_category,
        "very_high_factors": very_high_factors,
        "high_factors": high_factors,
        "moderate_factors": moderate_factors,
        "baseline_assessments": baseline_assessments,
        "monitoring_protocol": monitoring,
        "cardioprotection": cardioprotection,
        "parameters": {
            "age": age,
            "baseline_lvef": baseline_lvef,
            "planned_treatment": planned_treatment
        },
        "source": "ESC 2022 Cardio-Oncology Guidelines"
    }


def assess_ctrcd_severity(
    baseline_lvef: float,
    current_lvef: float,
    gls_decline_percent: Optional[float] = None,
    troponin_elevated: bool = False,
    np_elevated: bool = False,
    symptomatic: bool = False,
    hf_hospitalization: bool = False,
    requires_inotropes: bool = False,
    treatment_type: str = "anthracycline",
) -> Dict[str, Any]:
    """
    Assess cancer therapy-related cardiac dysfunction (CTRCD) severity.
    
    Args:
        baseline_lvef: Baseline LVEF (%)
        current_lvef: Current LVEF (%)
        gls_decline_percent: Relative GLS decline from baseline (%)
        troponin_elevated: New/rising troponin
        np_elevated: Elevated natriuretic peptide
        symptomatic: HF symptoms present
        hf_hospitalization: Required HF hospitalization
        requires_inotropes: Requires inotropes/MCS
        treatment_type: "anthracycline", "her2", "vegfi", "ici"
    
    Returns:
        CTRCD severity and management recommendation
    """
    lvef_decline = baseline_lvef - current_lvef
    
    # Symptomatic severity
    if symptomatic:
        if requires_inotropes:
            severity = "Very Severe (Symptomatic)"
            description = "HF requiring inotropes, MCS, or transplant consideration"
        elif hf_hospitalization:
            severity = "Severe (Symptomatic)"
            description = "HF hospitalization required"
        elif current_lvef < 40:
            severity = "Severe (Symptomatic)"
            description = "Symptomatic with LVEF <40%"
        elif current_lvef < 50:
            severity = "Moderate (Symptomatic)"
            description = "Symptomatic with LVEF 40-49%"
        else:
            severity = "Mild (Symptomatic)"
            description = "Mild HF symptoms with preserved LVEF"
    
    # Asymptomatic severity
    else:
        if current_lvef < 40:
            severity = "Severe (Asymptomatic)"
            description = "New LVEF <40%"
        elif current_lvef < 50 and lvef_decline >= 10:
            severity = "Moderate (Asymptomatic)"
            description = f"LVEF 40-49% with ≥10% decline (decline: {lvef_decline}%)"
        elif current_lvef < 50 and (gls_decline_percent and gls_decline_percent > 15):
            severity = "Moderate (Asymptomatic)"
            description = "LVEF 40-49% with GLS decline >15%"
        elif current_lvef >= 50 and (gls_decline_percent and gls_decline_percent > 15):
            severity = "Mild (Asymptomatic)"
            description = "Preserved LVEF with subclinical GLS decline >15%"
        elif current_lvef >= 50 and (troponin_elevated or np_elevated):
            severity = "Mild (Asymptomatic)"
            description = "Preserved LVEF with elevated biomarkers"
        else:
            severity = "None"
            description = "No CTRCD criteria met"
    
    # Management recommendations
    management = []
    cancer_therapy_action = None
    
    if "Severe" in severity or "Very Severe" in severity:
        if symptomatic:
            cancer_therapy_action = "STOP cancer therapy"
            management.append("Discontinue cardiotoxic therapy")
        else:
            cancer_therapy_action = "PAUSE cancer therapy"
            management.append("Hold cardiotoxic therapy")
        management.append("Initiate HF therapy (ACE-I/ARB + beta-blocker)")
        management.append("MDT discussion before any restart")
        management.append("Cardiology review")
    
    elif "Moderate" in severity:
        if symptomatic:
            cancer_therapy_action = "PAUSE cancer therapy"
            management.append("Hold cardiotoxic therapy")
            management.append("Initiate HF therapy")
            management.append("MDT discussion")
        else:
            # Key 2022 guideline update: can continue HER2 therapy with cardioprotection
            if treatment_type == "her2":
                cancer_therapy_action = "CONTINUE with cardioprotection"
                management.append("Continue HER2 therapy (Class IIa)")
                management.append("START ACE-I/ARB + beta-blocker (Class I)")
                management.append("More frequent monitoring")
            else:
                cancer_therapy_action = "PAUSE and assess"
                management.append("Consider holding anthracycline")
                management.append("Initiate cardioprotection")
                management.append("MDT discussion")
    
    elif "Mild" in severity:
        cancer_therapy_action = "CONTINUE with monitoring"
        management.append("Continue cancer therapy")
        management.append("Consider ACE-I/ARB and/or beta-blocker (Class IIa)")
        management.append("Increased monitoring frequency")
    
    else:
        cancer_therapy_action = "CONTINUE"
        management.append("Continue as planned")
    
    return {
        "severity": severity,
        "description": description,
        "cancer_therapy_action": cancer_therapy_action,
        "management": management,
        "parameters": {
            "baseline_lvef": baseline_lvef,
            "current_lvef": current_lvef,
            "lvef_decline": lvef_decline,
            "gls_decline_percent": gls_decline_percent,
            "troponin_elevated": troponin_elevated,
            "symptomatic": symptomatic
        },
        "definitions": {
            "moderate_ctrcd": "LVEF 40-49% with ≥10% decline OR <10% decline + GLS >15% OR biomarker rise",
            "severe_ctrcd": "New LVEF <40%",
            "gls_threshold": ">15% relative decline from baseline"
        },
        "source": "ESC 2022 Cardio-Oncology Guidelines"
    }


def get_surveillance_protocol(
    treatment_type: str,
    risk_category: str,
    treatment_phase: str = "during",
) -> Dict[str, Any]:
    """
    Get surveillance protocol for cardiotoxic cancer therapy.
    
    Args:
        treatment_type: "anthracycline", "her2", "vegfi", "bcr_abl_tki", "ici", "btk_inhibitor"
        risk_category: "low", "moderate", "high", "very_high"
        treatment_phase: "during", "first_year_post", "long_term"
    
    Returns:
        Detailed surveillance protocol
    """
    protocols = {
        "anthracycline": {
            "high": {
                "during": {
                    "echo": "Every 2 cycles",
                    "biomarkers": "Every cycle",
                    "gls": "Every 2 cycles"
                },
                "first_year_post": {
                    "echo": "3 and 12 months",
                    "biomarkers": "3 and 12 months"
                },
                "long_term": {
                    "echo": "Annual if cumulative dose ≥300 mg/m²",
                    "note": "Lifelong surveillance for childhood cancer survivors"
                }
            },
            "moderate": {
                "during": {
                    "echo": "After ≥250 mg/m² cumulative dose",
                    "biomarkers": "Every 2 cycles"
                },
                "first_year_post": {
                    "echo": "Within 12 months",
                    "biomarkers": "Within 3 months"
                }
            },
            "low": {
                "during": {
                    "echo": "May consider after ≥250 mg/m²",
                    "biomarkers": "May consider every 2 cycles"
                },
                "first_year_post": {
                    "echo": "12 months"
                }
            }
        },
        "her2": {
            "high": {
                "during": {
                    "echo": "Every 3 months",
                    "biomarkers": "Every 2-3 cycles"
                },
                "first_year_post": {
                    "echo": "12 months"
                }
            },
            "moderate": {
                "during": {
                    "echo": "Every 3-4 months",
                    "biomarkers": "Baseline, every 3 months"
                }
            },
            "low": {
                "during": {
                    "echo": "Every 3-4 months (may reduce after first normal)",
                    "biomarkers": "Optional"
                }
            }
        },
        "vegfi": {
            "high": {
                "during": {
                    "bp": "Every visit + daily home monitoring first cycle",
                    "echo": "Every 3 months in first year",
                    "biomarkers": "Baseline, 4 weeks, then every 3 months"
                }
            },
            "moderate": {
                "during": {
                    "bp": "Every visit + home monitoring",
                    "echo": "Every 4 months in first year"
                }
            },
            "low": {
                "during": {
                    "bp": "Every visit",
                    "echo": "Baseline, then if symptoms"
                }
            }
        },
        "ici": {
            "high": {
                "during": {
                    "ecg_troponin": "Baseline, weeks 2, 4, 8, then every 3 months",
                    "echo": "Baseline if high CV risk"
                }
            },
            "note": "Monitor for myocarditis - urgent troponin if symptoms"
        }
    }
    
    # Get specific protocol
    treatment_protocols = protocols.get(treatment_type, {})
    risk_protocols = treatment_protocols.get(risk_category, treatment_protocols.get("moderate", {}))
    phase_protocol = risk_protocols.get(treatment_phase, {})
    
    # Add general notes
    general_notes = []
    if treatment_type == "anthracycline":
        general_notes.append("GLS decline >15% from baseline suggests subclinical dysfunction")
        general_notes.append("Consider dexrazoxane if cumulative dose high")
    elif treatment_type == "her2":
        general_notes.append("LVEF recovery possible - can rechallenge if recovered")
    elif treatment_type == "vegfi":
        general_notes.append("BP target: <130/80 if high CV risk, <140/90 otherwise")
    elif treatment_type == "ici":
        general_notes.append("ICI myocarditis has ~50% mortality - requires urgent high-dose steroids")
    
    return {
        "treatment_type": treatment_type,
        "risk_category": risk_category,
        "treatment_phase": treatment_phase,
        "protocol": phase_protocol,
        "general_notes": general_notes,
        "source": "ESC 2022 Cardio-Oncology Guidelines"
    }
