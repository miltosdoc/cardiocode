"""
Venous Thromboembolism Assessment Tools.

Based on 2019 ESC Pulmonary Embolism Guidelines.
"""

from typing import Dict, Any, Optional, List


def assess_pe_risk_stratification(
    hemodynamic_status: str,
    pesi_class: Optional[int] = None,
    spesi_score: Optional[int] = None,
    rv_dysfunction: bool = False,
    elevated_troponin: bool = False,
    elevated_bnp: bool = False,
) -> Dict[str, Any]:
    """
    Assess PE risk stratification and determine management approach.
    
    Args:
        hemodynamic_status: "stable", "hypotensive", "shock", "cardiac_arrest"
        pesi_class: PESI class I-V (optional if sPESI provided)
        spesi_score: Simplified PESI score 0-6
        rv_dysfunction: RV dysfunction on echo/CT
        elevated_troponin: Elevated cardiac troponin
        elevated_bnp: Elevated BNP/NT-proBNP
    
    Returns:
        Risk category and management recommendation
    """
    # High-risk (hemodynamically unstable)
    if hemodynamic_status in ["hypotensive", "shock", "cardiac_arrest"]:
        risk_category = "High"
        mortality_risk = ">15%"
        management = [
            "Immediate anticoagulation with UFH (Class I)",
            "Systemic thrombolysis recommended (Class I)",
            "If thrombolysis contraindicated/failed: surgical embolectomy or catheter-directed therapy",
            "ICU admission required"
        ]
        return {
            "risk_category": risk_category,
            "mortality_risk": mortality_risk,
            "management": management,
            "hemodynamic_status": hemodynamic_status,
            "thrombolysis_indicated": True,
            "source": "ESC 2019 PE Guidelines"
        }
    
    # Determine intermediate vs low risk
    # sPESI-based assessment
    if spesi_score is not None:
        high_pesi = spesi_score >= 1
    elif pesi_class is not None:
        high_pesi = pesi_class >= 3
    else:
        high_pesi = None
    
    # Both biomarkers and imaging positive
    if high_pesi and rv_dysfunction and elevated_troponin:
        risk_category = "Intermediate-High"
        mortality_risk = "3-7%"
        management = [
            "Anticoagulation (Class I)",
            "Hospital admission with monitoring",
            "Rescue thrombolysis if hemodynamic deterioration (Class I)",
            "Consider intermediate care/step-down unit"
        ]
        reperfusion_consideration = "Rescue thrombolysis if hemodynamic deterioration"
    
    # Only one positive or PESI high but markers negative
    elif high_pesi and (rv_dysfunction or elevated_troponin):
        risk_category = "Intermediate-Low"
        mortality_risk = "1-3%"
        management = [
            "Anticoagulation (Class I)",
            "Hospital admission",
            "Monitoring for clinical deterioration"
        ]
        reperfusion_consideration = "Generally not indicated"
    
    # Low PESI/sPESI
    elif high_pesi == False or (high_pesi is None and not rv_dysfunction and not elevated_troponin):
        risk_category = "Low"
        mortality_risk = "<1%"
        management = [
            "Anticoagulation (Class I)",
            "Consider early discharge/outpatient treatment if appropriate (Class IIa)",
            "DOAC preferred over VKA"
        ]
        reperfusion_consideration = "Not indicated"
    
    else:
        risk_category = "Intermediate (further stratification needed)"
        mortality_risk = "1-7%"
        management = [
            "Complete risk assessment with biomarkers and imaging",
            "Anticoagulation while awaiting results"
        ]
        reperfusion_consideration = "Depends on full assessment"
    
    return {
        "risk_category": risk_category,
        "mortality_risk": mortality_risk,
        "management": management,
        "reperfusion_consideration": reperfusion_consideration,
        "parameters": {
            "hemodynamic_status": hemodynamic_status,
            "pesi_class": pesi_class,
            "spesi_score": spesi_score,
            "rv_dysfunction": rv_dysfunction,
            "elevated_troponin": elevated_troponin,
            "elevated_bnp": elevated_bnp
        },
        "source": "ESC 2019 PE Guidelines"
    }


def assess_pe_thrombolysis(
    risk_category: str,
    hemodynamic_status: str,
    contraindications: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Assess thrombolysis indication for PE.
    
    Args:
        risk_category: "high", "intermediate_high", "intermediate_low", "low"
        hemodynamic_status: "stable", "hypotensive", "shock", "cardiac_arrest", "deteriorating"
        contraindications: List of contraindications present
    
    Returns:
        Thrombolysis recommendation
    """
    if contraindications is None:
        contraindications = []
    
    # Define absolute contraindications
    absolute_contraindications = [
        "hemorrhagic_stroke_history",
        "ischemic_stroke_6_months",
        "cns_neoplasm",
        "major_trauma_surgery_head_injury_3_weeks",
        "bleeding_diathesis",
        "active_bleeding"
    ]
    
    # Check for absolute contraindications
    has_absolute_contraindication = any(c in absolute_contraindications for c in contraindications)
    
    # High-risk PE
    if risk_category == "high" or hemodynamic_status in ["hypotensive", "shock", "cardiac_arrest"]:
        if has_absolute_contraindication:
            recommendation = "Thrombolysis contraindicated - consider surgical embolectomy or catheter-directed therapy"
            indication_class = "III (for thrombolysis)"
        else:
            recommendation = "Systemic thrombolysis recommended"
            indication_class = "I"
        
        regimens = [
            {"agent": "Alteplase (rtPA)", "dose": "100 mg over 2 hours", "alternative": "0.6 mg/kg over 15 min (max 50 mg) for accelerated"},
            {"agent": "Streptokinase", "dose": "1.5 million IU over 2 hours (accelerated)"},
        ]
    
    # Intermediate-high with deterioration
    elif hemodynamic_status == "deteriorating" and risk_category == "intermediate_high":
        if has_absolute_contraindication:
            recommendation = "Consider catheter-directed therapy or surgical embolectomy"
            indication_class = "IIa"
        else:
            recommendation = "Rescue thrombolysis recommended"
            indication_class = "I"
        regimens = [{"agent": "Alteplase (rtPA)", "dose": "100 mg over 2 hours"}]
    
    # Stable intermediate or low risk
    else:
        recommendation = "Routine thrombolysis NOT recommended"
        indication_class = "III"
        regimens = []
    
    return {
        "thrombolysis_indicated": indication_class == "I",
        "indication_class": indication_class,
        "recommendation": recommendation,
        "regimens": regimens,
        "contraindications_present": contraindications,
        "has_absolute_contraindication": has_absolute_contraindication,
        "absolute_contraindications": [
            "History of hemorrhagic stroke or stroke of unknown origin",
            "Ischemic stroke in previous 6 months",
            "CNS neoplasm",
            "Major trauma, surgery, or head injury in previous 3 weeks",
            "Bleeding diathesis",
            "Active bleeding"
        ],
        "relative_contraindications": [
            "TIA in previous 6 months",
            "Oral anticoagulation therapy",
            "Pregnancy or first post-partum week",
            "Non-compressible puncture sites",
            "Traumatic resuscitation",
            "Refractory hypertension (SBP >180 mmHg)",
            "Advanced liver disease",
            "Infective endocarditis",
            "Active peptic ulcer"
        ],
        "source": "ESC 2019 PE Guidelines"
    }


def assess_pe_outpatient_eligibility(
    spesi_score: int,
    hemodynamically_stable: bool = True,
    o2_required: bool = False,
    high_bleeding_risk: bool = False,
    renal_impairment_severe: bool = False,
    severe_pain: bool = False,
    active_cancer_high_risk: bool = False,
    social_support_adequate: bool = True,
    follow_up_available: bool = True,
) -> Dict[str, Any]:
    """
    Assess eligibility for early discharge/outpatient PE treatment.
    
    Based on Hestia criteria and ESC guidelines.
    
    Args:
        spesi_score: Simplified PESI score
        hemodynamically_stable: Hemodynamically stable
        o2_required: Supplemental O2 required for SpO2 >90%
        high_bleeding_risk: High bleeding risk
        renal_impairment_severe: CrCl <30 mL/min
        severe_pain: Severe pain requiring IV analgesia
        active_cancer_high_risk: Active cancer requiring special management
        social_support_adequate: Adequate home support
        follow_up_available: Outpatient follow-up available
    
    Returns:
        Outpatient eligibility assessment
    """
    exclusion_criteria = []
    
    # Hestia-based exclusion criteria
    if not hemodynamically_stable:
        exclusion_criteria.append("Hemodynamically unstable")
    
    if spesi_score >= 1:
        exclusion_criteria.append(f"sPESI ≥1 (score: {spesi_score})")
    
    if o2_required:
        exclusion_criteria.append("Requires supplemental oxygen")
    
    if high_bleeding_risk:
        exclusion_criteria.append("High bleeding risk")
    
    if renal_impairment_severe:
        exclusion_criteria.append("Severe renal impairment (CrCl <30)")
    
    if severe_pain:
        exclusion_criteria.append("Severe pain requiring IV analgesia")
    
    if active_cancer_high_risk:
        exclusion_criteria.append("Active cancer requiring special management")
    
    if not social_support_adequate:
        exclusion_criteria.append("Inadequate social/home support")
    
    if not follow_up_available:
        exclusion_criteria.append("Outpatient follow-up not available")
    
    # Eligibility determination
    eligible = len(exclusion_criteria) == 0
    
    if eligible:
        recommendation = "Early discharge/outpatient treatment may be considered (Class IIa)"
        anticoagulation = "DOAC preferred (rivaroxaban or apixaban with initial loading)"
    else:
        recommendation = "Hospital admission recommended"
        anticoagulation = "Initiate anticoagulation in hospital"
    
    return {
        "eligible_for_outpatient": eligible,
        "recommendation": recommendation,
        "anticoagulation": anticoagulation,
        "exclusion_criteria_present": exclusion_criteria,
        "requirements_for_outpatient": [
            "sPESI = 0",
            "Hemodynamically stable",
            "No supplemental O2 requirement",
            "Low bleeding risk",
            "No severe pain",
            "Adequate renal function",
            "Adequate social support",
            "Outpatient follow-up available"
        ],
        "source": "ESC 2019 PE Guidelines"
    }


def calculate_vte_recurrence_risk(
    risk_factor_category: str,
    unprovoked: bool = False,
    prior_vte: bool = False,
    male: bool = False,
    residual_dvt: bool = False,
    elevated_d_dimer_after_anticoag: bool = False,
) -> Dict[str, Any]:
    """
    Calculate VTE recurrence risk and anticoagulation duration recommendation.
    
    Args:
        risk_factor_category: "major_transient", "minor_transient", "persistent_nonmalignant", 
                             "active_cancer", "antiphospholipid", "no_identifiable"
        unprovoked: No identifiable risk factor (alias for no_identifiable)
        prior_vte: Previous VTE episode
        male: Male sex
        residual_dvt: Residual DVT on imaging
        elevated_d_dimer_after_anticoag: Elevated D-dimer after stopping anticoagulation
    
    Returns:
        Recurrence risk and anticoagulation duration recommendation
    """
    # Standardize category
    if unprovoked or risk_factor_category == "no_identifiable":
        risk_factor_category = "no_identifiable"
    
    # Risk categorization
    risk_categories = {
        "major_transient": {
            "annual_recurrence": "<3%",
            "risk_level": "Low",
            "examples": ["Surgery with GA >30 min", "Hospital bedrest ≥3 days", "Major trauma with fractures"],
            "duration": "3 months",
            "extended_anticoag": "Not recommended",
            "duration_class": "I"
        },
        "minor_transient": {
            "annual_recurrence": "3-8%",
            "risk_level": "Intermediate", 
            "examples": ["Minor surgery", "Hospital <3 days", "Estrogen therapy", "Pregnancy", "Long-haul flight", "Leg injury"],
            "duration": "3 months minimum, consider extended",
            "extended_anticoag": "Should be considered (Class IIa)",
            "duration_class": "IIa"
        },
        "persistent_nonmalignant": {
            "annual_recurrence": "3-8%",
            "risk_level": "Intermediate",
            "examples": ["IBD", "Active autoimmune disease"],
            "duration": "Consider extended anticoagulation",
            "extended_anticoag": "Should be considered (Class IIa)",
            "duration_class": "IIa"
        },
        "no_identifiable": {
            "annual_recurrence": "3-8%",
            "risk_level": "Intermediate",
            "examples": ["No identifiable risk factor"],
            "duration": "Consider extended anticoagulation",
            "extended_anticoag": "Should be considered (Class IIa)",
            "duration_class": "IIa"
        },
        "active_cancer": {
            "annual_recurrence": ">8%",
            "risk_level": "High",
            "examples": ["Active malignancy"],
            "duration": "Extended (at least 6 months, often indefinite)",
            "extended_anticoag": "Recommended (Class I) - LMWH or DOAC",
            "duration_class": "I"
        },
        "antiphospholipid": {
            "annual_recurrence": ">8%",
            "risk_level": "High",
            "examples": ["Antiphospholipid syndrome"],
            "duration": "Indefinite VKA (avoid DOAC)",
            "extended_anticoag": "Recommended (Class I) - VKA only",
            "duration_class": "I"
        }
    }
    
    category_info = risk_categories.get(risk_factor_category, risk_categories["no_identifiable"])
    
    # Additional risk modifiers
    recurrence_modifiers = []
    if prior_vte:
        recurrence_modifiers.append("Prior VTE - increases recurrence risk significantly")
    if male:
        recurrence_modifiers.append("Male sex - higher recurrence risk than female")
    if residual_dvt:
        recurrence_modifiers.append("Residual DVT on imaging")
    if elevated_d_dimer_after_anticoag:
        recurrence_modifiers.append("Elevated D-dimer after stopping anticoagulation - consider extended therapy")
    
    # Extended anticoagulation dosing
    if category_info["risk_level"] in ["Intermediate", "High"]:
        extended_options = [
            "Full-dose DOAC continuation",
            "Reduced-dose apixaban (2.5 mg BID) or rivaroxaban (10 mg daily) after 6 months (Class IIa)"
        ]
    else:
        extended_options = []
    
    return {
        "risk_factor_category": risk_factor_category,
        "annual_recurrence_risk": category_info["annual_recurrence"],
        "risk_level": category_info["risk_level"],
        "examples": category_info["examples"],
        "anticoagulation_duration": category_info["duration"],
        "extended_anticoag_recommendation": category_info["extended_anticoag"],
        "recommendation_class": category_info["duration_class"],
        "recurrence_modifiers": recurrence_modifiers,
        "extended_dose_options": extended_options,
        "notes": [
            "All patients should receive minimum 3 months anticoagulation (Class I)",
            "Risk-benefit assessment should consider bleeding risk",
            "Reduced-dose DOAC after 6 months reduces major bleeding while maintaining efficacy"
        ],
        "source": "ESC 2019 PE Guidelines"
    }
