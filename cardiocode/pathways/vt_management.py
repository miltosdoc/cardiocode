"""
Ventricular Tachycardia Management Pathways.

Based on 2022 ESC Ventricular Arrhythmias and SCD Guidelines.
"""

from typing import Dict, Any, Optional, List


def pathway_vt_acute_management(
    hemodynamically_stable: bool,
    structural_heart_disease: bool = False,
    suspected_etiology: str = "unknown",
    vt_morphology: str = "monomorphic",
    current_medications: Optional[List[str]] = None,
    lvef: Optional[float] = None,
    qt_prolonged: bool = False,
) -> Dict[str, Any]:
    """
    Acute VT management pathway.
    
    Args:
        hemodynamically_stable: Patient is hemodynamically stable
        structural_heart_disease: Known or suspected SHD
        suspected_etiology: "ischemic", "idiopathic", "rvot", "fascicular", "unknown"
        vt_morphology: "monomorphic", "polymorphic", "torsades"
        current_medications: Current antiarrhythmic medications
        lvef: LV ejection fraction if known
        qt_prolonged: QTc prolonged at baseline
    
    Returns:
        Management pathway steps
    """
    if current_medications is None:
        current_medications = []
    
    steps = []
    
    # Unstable VT - immediate cardioversion
    if not hemodynamically_stable:
        steps.append({
            "step": 1,
            "action": "Synchronized DC cardioversion",
            "class": "I",
            "details": "Immediate cardioversion for hemodynamically unstable VT",
            "energy": "Biphasic 150-200J, escalate if unsuccessful"
        })
        steps.append({
            "step": 2,
            "action": "If pulseless or VF: Defibrillation",
            "details": "Unsynchronized shock, follow ACLS protocol"
        })
        return {
            "pathway": "Unstable VT",
            "steps": steps,
            "post_cardioversion": [
                "Identify and treat reversible causes",
                "12-lead ECG",
                "Echocardiography",
                "Consider ICU admission",
                "Antiarrhythmic therapy and ICD evaluation"
            ],
            "source": "ESC 2022 VA/SCD Guidelines"
        }
    
    # Stable VT management
    steps.append({
        "step": 1,
        "action": "12-lead ECG during tachycardia if possible",
        "details": "Document morphology for diagnosis and ablation planning"
    })
    
    # Polymorphic VT / Torsades
    if vt_morphology in ["polymorphic", "torsades"]:
        if qt_prolonged or vt_morphology == "torsades":
            steps.append({
                "step": 2,
                "action": "IV Magnesium sulfate",
                "class": "I",
                "details": "2g IV over 10 min for Torsades de Pointes"
            })
            steps.append({
                "step": 3,
                "action": "Increase heart rate",
                "details": "Temporary pacing or isoproterenol to prevent pause-dependent TdP"
            })
            steps.append({
                "step": 4,
                "action": "Correct electrolytes",
                "details": "Target K+ >4.0, Mg++ >2.0"
            })
            steps.append({
                "step": 5,
                "action": "Discontinue QT-prolonging drugs",
                "details": "Review all medications"
            })
        else:
            # Polymorphic without QT prolongation - likely ischemia
            steps.append({
                "step": 2,
                "action": "Evaluate for ischemia",
                "class": "I",
                "details": "Urgent coronary angiography if ischemia suspected"
            })
            steps.append({
                "step": 3,
                "action": "IV beta-blocker",
                "class": "I",
                "details": "If no contraindications"
            })
        
        return {
            "pathway": f"Polymorphic VT / {'Torsades' if qt_prolonged else 'Non-TdP'}",
            "steps": steps,
            "source": "ESC 2022 VA/SCD Guidelines"
        }
    
    # Monomorphic VT
    if not structural_heart_disease:
        # Idiopathic VT
        if suspected_etiology in ["rvot", "idiopathic"]:
            steps.append({
                "step": 2,
                "action": "IV beta-blocker or verapamil",
                "class": "I",
                "details": "Beta-blocker for RVOT VT; Verapamil for fascicular VT"
            })
        elif suspected_etiology == "fascicular":
            steps.append({
                "step": 2,
                "action": "IV Verapamil",
                "class": "I",
                "details": "First-line for fascicular (Belhassen) VT"
            })
        else:
            steps.append({
                "step": 2,
                "action": "IV beta-blocker",
                "class": "IIa",
                "details": "If suspected idiopathic VT"
            })
    else:
        # Structural heart disease
        steps.append({
            "step": 2,
            "action": "IV Procainamide",
            "class": "IIa",
            "details": "Preferred over amiodarone for stable monomorphic VT with SHD; 10-15 mg/kg at 20-50 mg/min"
        })
        steps.append({
            "step": 3,
            "action": "IV Amiodarone (alternative)",
            "class": "IIb",
            "details": "150 mg over 10 min, then infusion; less effective than procainamide but safer in severe LV dysfunction"
        })
    
    # Additional steps
    steps.append({
        "step": "Final",
        "action": "If pharmacological therapy fails",
        "details": "Proceed to synchronized cardioversion"
    })
    
    # Long-term considerations
    long_term = []
    if structural_heart_disease:
        long_term.append("ICD evaluation")
        long_term.append("Consider catheter ablation for recurrent VT")
        long_term.append("Optimize HF therapy")
    else:
        long_term.append("Catheter ablation (curative for most idiopathic VT)")
        long_term.append("Beta-blocker or CCB for rate control")
    
    return {
        "pathway": f"Stable Monomorphic VT - {'SHD' if structural_heart_disease else 'No SHD'}",
        "steps": steps,
        "avoid": [
            "IV verapamil in wide-complex tachycardia of unknown mechanism (Class III)",
            "IV verapamil if structural heart disease suspected"
        ],
        "long_term_considerations": long_term,
        "source": "ESC 2022 VA/SCD Guidelines"
    }


def pathway_electrical_storm(
    current_step: int = 1,
    icd_in_place: bool = False,
    on_amiodarone: bool = False,
    on_beta_blocker: bool = False,
    lvef: Optional[float] = None,
    vt_morphology: str = "monomorphic",
    response_to_previous: str = "none",
) -> Dict[str, Any]:
    """
    Electrical storm management pathway.
    
    Electrical storm = ≥3 episodes of sustained VT/VF in 24 hours.
    
    Args:
        current_step: Current step in management (1-5)
        icd_in_place: Patient has ICD
        on_amiodarone: Currently on amiodarone
        on_beta_blocker: Currently on beta-blocker
        lvef: LV ejection fraction
        vt_morphology: "monomorphic", "polymorphic"
        response_to_previous: "none", "partial", "refractory"
    
    Returns:
        Step-wise management recommendations
    """
    all_steps = []
    
    # Step 1: Immediate stabilization
    all_steps.append({
        "step": 1,
        "name": "Immediate Stabilization",
        "actions": [
            "Mild-to-moderate sedation (Class I)",
            "Correct electrolytes: K+ >4.0, Mg++ >2.0 (Class I)",
            "Treat underlying triggers (ischemia, infection, drug toxicity)",
            "Reprogram ICD if in place (extend detection, ATP optimization)"
        ],
        "class": "I"
    })
    
    # Step 2: First-line pharmacotherapy
    all_steps.append({
        "step": 2,
        "name": "First-Line Pharmacotherapy",
        "actions": [
            "IV beta-blocker (non-selective preferred: propranolol, esmolol) - Class I",
            "IV amiodarone (150mg bolus, then 1mg/min x 6h, then 0.5mg/min) - Class I",
            "Combination beta-blocker + amiodarone preferred"
        ],
        "class": "I",
        "note": "Non-selective beta-blockers (propranolol, nadolol) may be more effective than selective"
    })
    
    # Step 3: Catheter ablation
    all_steps.append({
        "step": 3,
        "name": "Catheter Ablation",
        "actions": [
            "Urgent catheter ablation for recurrent monomorphic VT (Class I)",
            "Should be performed at experienced center",
            "Particularly effective for scar-related VT"
        ],
        "class": "I",
        "indication": "Refractory to antiarrhythmic drugs or as early strategy"
    })
    
    # Step 4: Autonomic modulation
    all_steps.append({
        "step": 4,
        "name": "Autonomic Modulation (Refractory Cases)",
        "actions": [
            "Stellate ganglion block (Class IIb)",
            "Thoracic epidural anesthesia",
            "Cardiac sympathetic denervation (for truly refractory cases)"
        ],
        "class": "IIb",
        "indication": "Refractory to drugs and ablation"
    })
    
    # Step 5: Mechanical support
    all_steps.append({
        "step": 5,
        "name": "Mechanical Circulatory Support",
        "actions": [
            "Deep sedation/intubation if needed (Class IIa)",
            "Consider MCS (ECMO, Impella) for hemodynamic support during ablation",
            "LVAD/transplant evaluation if appropriate"
        ],
        "class": "IIb",
        "indication": "Hemodynamic compromise or bridge to definitive therapy"
    })
    
    # Specific guidance based on VT type
    if vt_morphology == "polymorphic":
        specific_guidance = [
            "Investigate and treat ischemia urgently",
            "IV magnesium for all polymorphic VT",
            "If pause-dependent (TdP): pacing to increase HR",
            "Isoproterenol may help if TdP"
        ]
    else:
        specific_guidance = [
            "Ablation highly effective for monomorphic VT storm",
            "Identify and target clinical VT morphology",
            "Substrate-based ablation if multiple morphologies"
        ]
    
    # Current recommendation
    if current_step <= len(all_steps):
        current_recommendation = all_steps[current_step - 1]
    else:
        current_recommendation = all_steps[-1]
    
    return {
        "definition": "≥3 episodes of sustained VT/VF within 24 hours requiring intervention",
        "current_step": current_step,
        "current_recommendation": current_recommendation,
        "all_steps": all_steps,
        "morphology_specific_guidance": specific_guidance,
        "key_principles": [
            "Sedation reduces sympathetic drive",
            "Beta-blockers are cornerstone of therapy",
            "Early ablation improves outcomes in monomorphic VT storm",
            "Address reversible causes (ischemia, electrolytes, drugs)"
        ],
        "avoid": [
            "Excessive ICD shocks without reprogramming",
            "Single-agent therapy when combination needed"
        ],
        "source": "ESC 2022 VA/SCD Guidelines"
    }


def pathway_vt_chronic_management(
    etiology: str,
    lvef: float,
    prior_vt_vf: bool = False,
    icd_in_place: bool = False,
    recurrent_vt_on_therapy: bool = False,
    current_aad: Optional[str] = None,
    ablation_performed: bool = False,
) -> Dict[str, Any]:
    """
    Chronic VT management pathway.
    
    Args:
        etiology: "ischemic", "dcm", "idiopathic", "hcm", "arvc"
        lvef: LV ejection fraction (%)
        prior_vt_vf: Prior sustained VT or VF
        icd_in_place: ICD already implanted
        recurrent_vt_on_therapy: VT recurring despite current therapy
        current_aad: Current antiarrhythmic drug
        ablation_performed: Prior ablation performed
    
    Returns:
        Long-term management strategy
    """
    recommendations = []
    
    # ICD indication
    if prior_vt_vf and not icd_in_place:
        recommendations.append({
            "intervention": "ICD implantation",
            "class": "I",
            "rationale": "Secondary prevention after sustained VT/VF"
        })
    
    # Antiarrhythmic drugs
    if recurrent_vt_on_therapy or prior_vt_vf:
        if etiology == "ischemic":
            if current_aad is None:
                recommendations.append({
                    "intervention": "Beta-blocker (first-line)",
                    "class": "I",
                    "rationale": "Reduces VT recurrence and ICD shocks"
                })
            if current_aad == "beta_blocker" and recurrent_vt_on_therapy:
                recommendations.append({
                    "intervention": "Add amiodarone or sotalol",
                    "class": "IIa",
                    "rationale": "For recurrent VT despite beta-blocker"
                })
                recommendations.append({
                    "intervention": "Catheter ablation",
                    "class": "IIa",
                    "rationale": "May be preferred over AAD escalation"
                })
            if current_aad == "amiodarone" and recurrent_vt_on_therapy:
                recommendations.append({
                    "intervention": "Catheter ablation",
                    "class": "I",
                    "rationale": "Recurrent VT despite amiodarone - ablation recommended"
                })
        
        elif etiology == "idiopathic":
            recommendations.append({
                "intervention": "Catheter ablation",
                "class": "I",
                "rationale": "First-line therapy for idiopathic VT - high cure rate"
            })
            if not ablation_performed:
                recommendations.append({
                    "intervention": "Beta-blocker or CCB as alternative",
                    "class": "I",
                    "rationale": "If ablation not desired or not available"
                })
        
        elif etiology in ["dcm", "hcm", "arvc"]:
            recommendations.append({
                "intervention": "Beta-blocker",
                "class": "I",
                "rationale": "First-line for all cardiomyopathies"
            })
            if recurrent_vt_on_therapy:
                recommendations.append({
                    "intervention": "Amiodarone or sotalol",
                    "class": "IIa",
                    "rationale": "For recurrent VT"
                })
                recommendations.append({
                    "intervention": "Catheter ablation at specialized center",
                    "class": "IIa",
                    "rationale": "For drug-refractory VT in cardiomyopathy"
                })
    
    # Substrate treatment
    substrate_treatment = []
    if etiology == "ischemic":
        substrate_treatment.append("Optimize coronary revascularization")
        substrate_treatment.append("Optimize HF therapy")
    elif etiology == "dcm":
        substrate_treatment.append("Optimize HF therapy (quadruple therapy)")
        substrate_treatment.append("Consider genetic testing for risk stratification")
    elif etiology == "arvc":
        substrate_treatment.append("Exercise restriction")
        substrate_treatment.append("Beta-blocker regardless of VT history")
    
    return {
        "etiology": etiology,
        "recommendations": recommendations,
        "substrate_treatment": substrate_treatment,
        "monitoring": [
            "Regular ICD interrogation (every 3-6 months)",
            "Annual echocardiography",
            "Monitor antiarrhythmic drug levels and toxicity",
            "QTc monitoring if on sotalol or amiodarone"
        ],
        "source": "ESC 2022 VA/SCD Guidelines"
    }
