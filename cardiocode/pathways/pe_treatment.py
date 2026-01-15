"""
Pulmonary Embolism Treatment Pathways.

Based on 2019 ESC Pulmonary Embolism Guidelines.
"""

from typing import Dict, Any, Optional, List


def pathway_pe_treatment(
    risk_category: str,
    hemodynamic_status: str = "stable",
    renal_function: str = "normal",
    active_cancer: bool = False,
    gi_bleeding_risk: bool = False,
    pregnancy: bool = False,
    body_weight: Optional[float] = None,
    creatinine_clearance: Optional[float] = None,
    contraindication_to_anticoagulation: bool = False,
) -> Dict[str, Any]:
    """
    PE treatment pathway - acute phase management.
    
    Args:
        risk_category: "high", "intermediate_high", "intermediate_low", "low"
        hemodynamic_status: "stable", "hypotensive", "shock"
        renal_function: "normal", "mild_impairment", "moderate_impairment", "severe_impairment"
        active_cancer: Has active cancer
        gi_bleeding_risk: High GI bleeding risk
        pregnancy: Currently pregnant
        body_weight: Body weight in kg
        creatinine_clearance: CrCl in mL/min
    
    Returns:
        Treatment pathway
    """
    steps = []
    anticoagulation_options = []
    
    # High-risk PE
    if risk_category == "high" or hemodynamic_status in ["hypotensive", "shock"]:
        steps.append({
            "step": 1,
            "action": "IV UFH bolus",
            "details": "80 IU/kg bolus, then 18 IU/kg/h infusion",
            "class": "I",
            "rationale": "Immediate anticoagulation; UFH preferred due to short half-life and reversibility"
        })
        steps.append({
            "step": 2,
            "action": "Systemic thrombolysis",
            "details": "Alteplase 100mg over 2h (or 0.6mg/kg over 15min if accelerated needed)",
            "class": "I",
            "rationale": "High-risk PE with hemodynamic instability"
        })
        steps.append({
            "step": 3,
            "action": "If thrombolysis contraindicated/failed",
            "details": "Surgical embolectomy or catheter-directed therapy",
            "class": "I" 
        })
        steps.append({
            "step": 4,
            "action": "ICU admission",
            "details": "Continuous monitoring, vasopressor support if needed"
        })
        
        return {
            "pathway": "High-Risk PE",
            "steps": steps,
            "reperfusion_indicated": True,
            "monitoring": "ICU level care",
            "source": "ESC 2019 PE Guidelines"
        }
    
    # Intermediate-high risk
    if risk_category == "intermediate_high":
        steps.append({
            "step": 1,
            "action": "Anticoagulation",
            "details": "LMWH, fondaparinux, or UFH initially; consider DOAC transition",
            "class": "I"
        })
        steps.append({
            "step": 2,
            "action": "Close monitoring",
            "details": "Intermediate care or monitored bed; watch for deterioration",
            "class": "I"
        })
        steps.append({
            "step": 3,
            "action": "Rescue reperfusion if deterioration",
            "details": "Thrombolysis if hemodynamic decompensation occurs",
            "class": "I"
        })
    
    # Intermediate-low and low risk
    else:
        steps.append({
            "step": 1,
            "action": "Anticoagulation",
            "details": "DOAC preferred; or LMWH/fondaparinux with VKA transition",
            "class": "I"
        })
        
        if risk_category == "low":
            steps.append({
                "step": 2,
                "action": "Consider early discharge",
                "details": "If Hestia criteria met and adequate outpatient support",
                "class": "IIa"
            })
    
    # Anticoagulation selection
    if contraindication_to_anticoagulation:
        anticoagulation_options.append({
            "option": "IVC filter",
            "indication": "Absolute contraindication to anticoagulation",
            "note": "Retrieve when anticoagulation becomes possible"
        })
    elif pregnancy:
        anticoagulation_options.append({
            "option": "LMWH (weight-adjusted)",
            "indication": "Pregnancy - DOACs contraindicated",
            "details": "Continue through pregnancy and postpartum"
        })
    elif active_cancer:
        anticoagulation_options.append({
            "option": "DOAC (edoxaban or rivaroxaban) or LMWH",
            "indication": "Cancer-associated VTE",
            "details": "DOAC preferred unless high GI bleeding risk; LMWH if GI/GU cancer",
            "class": "I"
        })
    elif creatinine_clearance and creatinine_clearance < 30:
        anticoagulation_options.append({
            "option": "UFH or dose-adjusted LMWH",
            "indication": "Severe renal impairment (CrCl <30)",
            "details": "DOACs not recommended; monitor anti-Xa if using LMWH"
        })
    else:
        anticoagulation_options.append({
            "option": "Rivaroxaban",
            "details": "15mg BID x 21 days, then 20mg daily",
            "class": "I"
        })
        anticoagulation_options.append({
            "option": "Apixaban", 
            "details": "10mg BID x 7 days, then 5mg BID",
            "class": "I"
        })
        anticoagulation_options.append({
            "option": "Edoxaban",
            "details": "60mg daily (after ≥5 days parenteral); 30mg if CrCl 30-50 or weight <60kg",
            "class": "I"
        })
        anticoagulation_options.append({
            "option": "Dabigatran",
            "details": "150mg BID (after ≥5 days parenteral)",
            "class": "I"
        })
        anticoagulation_options.append({
            "option": "LMWH → Warfarin",
            "details": "Continue LMWH until INR 2-3 for ≥24h",
            "class": "I"
        })
    
    return {
        "pathway": f"{risk_category.replace('_', '-').title()} Risk PE",
        "steps": steps,
        "anticoagulation_options": anticoagulation_options,
        "reperfusion_indicated": risk_category == "high",
        "minimum_duration": "3 months for all PE",
        "source": "ESC 2019 PE Guidelines"
    }


def pathway_pe_anticoagulation_duration(
    first_vte: bool = True,
    provoked: bool = True,
    provoking_factor: str = "none",
    bleeding_risk: str = "low",
    pe_severity: str = "low",
    patient_preference_extended: bool = False,
    d_dimer_after_stopping: Optional[str] = None,
) -> Dict[str, Any]:
    """
    PE anticoagulation duration pathway.
    
    Args:
        first_vte: First VTE episode
        provoked: VTE was provoked (had identifiable risk factor)
        provoking_factor: "major_transient", "minor_transient", "persistent", "cancer", "none"
        bleeding_risk: "low", "moderate", "high"
        pe_severity: "low", "intermediate", "high"
        patient_preference_extended: Patient prefers extended anticoagulation
        d_dimer_after_stopping: "negative", "positive", or None
    
    Returns:
        Duration recommendation
    """
    # All patients get minimum 3 months
    minimum_duration = "3 months"
    
    # Decision framework
    if provoking_factor == "major_transient":
        # Surgery, major trauma, prolonged immobilization
        duration = "3 months"
        extended_recommendation = "Not routinely recommended"
        recurrence_risk = "Low (<3% per year after stopping)"
        rationale = "Major transient risk factor identified and resolved"
    
    elif provoking_factor == "cancer":
        duration = "Extended (minimum 6 months, often indefinite)"
        extended_recommendation = "Strongly recommended while cancer active (Class I)"
        recurrence_risk = "High (>8% per year)"
        rationale = "Active cancer - continue until cured or risk outweighs benefit"
    
    elif provoking_factor == "minor_transient":
        # Estrogen, pregnancy, minor surgery, travel
        duration = "3 months minimum, consider extended"
        extended_recommendation = "Should be considered (Class IIa)"
        recurrence_risk = "Intermediate (3-8% per year)"
        rationale = "Minor transient factor - individualized decision"
    
    elif provoking_factor == "persistent" or provoking_factor == "none":
        # Unprovoked or persistent risk factor
        duration = "Extended anticoagulation should be considered"
        extended_recommendation = "Should be considered (Class IIa)"
        recurrence_risk = "Intermediate to high without anticoagulation"
        rationale = "No transient provoking factor - high recurrence risk"
    
    else:
        duration = "3 months minimum, reassess"
        extended_recommendation = "Individualized assessment"
        recurrence_risk = "Requires assessment"
        rationale = "Further risk stratification needed"
    
    # Factors favoring extended
    favoring_extended = []
    if not provoked or provoking_factor in ["none", "persistent", "minor_transient"]:
        favoring_extended.append("Unprovoked or persistent risk factor")
    if not first_vte:
        favoring_extended.append("Recurrent VTE")
    if pe_severity in ["intermediate", "high"]:
        favoring_extended.append("More severe initial PE")
    if d_dimer_after_stopping == "positive":
        favoring_extended.append("Positive D-dimer after stopping (suggests ongoing risk)")
    if patient_preference_extended:
        favoring_extended.append("Patient preference")
    
    # Factors favoring stopping
    favoring_stopping = []
    if provoked and provoking_factor == "major_transient":
        favoring_stopping.append("Major transient provoking factor")
    if bleeding_risk == "high":
        favoring_stopping.append("High bleeding risk")
    if first_vte and provoked:
        favoring_stopping.append("First provoked VTE")
    if d_dimer_after_stopping == "negative":
        favoring_stopping.append("Negative D-dimer after stopping")
    
    # Extended dosing options
    if "extended" in duration.lower() or len(favoring_extended) >= 2:
        extended_options = [
            {
                "option": "Continue full-dose DOAC",
                "details": "Standard dosing throughout"
            },
            {
                "option": "Reduced-dose DOAC after 6 months",
                "details": "Apixaban 2.5mg BID or Rivaroxaban 10mg daily",
                "class": "IIa",
                "rationale": "Reduces major bleeding while maintaining efficacy"
            },
            {
                "option": "Aspirin",
                "details": "If anticoagulation stopped and no contraindication",
                "class": "IIb",
                "rationale": "Less effective than anticoagulation but some protection"
            }
        ]
    else:
        extended_options = []
    
    return {
        "minimum_duration": minimum_duration,
        "recommended_duration": duration,
        "extended_recommendation": extended_recommendation,
        "recurrence_risk_without_anticoagulation": recurrence_risk,
        "rationale": rationale,
        "factors_favoring_extended": favoring_extended,
        "factors_favoring_stopping": favoring_stopping,
        "extended_dose_options": extended_options,
        "bleeding_risk_category": bleeding_risk,
        "decision_framework": [
            "1. All patients: minimum 3 months anticoagulation",
            "2. Major transient factor: 3 months usually sufficient",
            "3. Active cancer: Extended/indefinite",
            "4. Unprovoked/recurrent: Favor extended anticoagulation",
            "5. Balance recurrence vs bleeding risk for individual decision"
        ],
        "source": "ESC 2019 PE Guidelines"
    }
