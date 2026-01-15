"""
Heart Failure Treatment Pathways.

Based on 2021 ESC Heart Failure Guidelines.
"""

from typing import Dict, Any, Optional, List


def pathway_hfref_treatment(
    current_medications: List[str],
    lvef: float,
    nyha_class: int,
    systolic_bp: int,
    heart_rate: int,
    potassium: float,
    egfr: float,
    rhythm: str = "sinus",
    qrs_duration: Optional[int] = None,
    qrs_morphology: Optional[str] = None,
    on_max_beta_blocker: bool = False,
    iron_deficient: bool = False,
    race_black: bool = False,
) -> Dict[str, Any]:
    """
    HFrEF treatment pathway - determine next therapy step.
    
    Args:
        current_medications: List of current meds ["acei", "arni", "bb", "mra", "sglt2i", "diuretic"]
        lvef: LV ejection fraction (%)
        nyha_class: NYHA class 1-4
        systolic_bp: Systolic blood pressure (mmHg)
        heart_rate: Heart rate (bpm)
        potassium: Serum potassium (mEq/L)
        egfr: Estimated GFR (mL/min/1.73m²)
        rhythm: "sinus" or "af"
        qrs_duration: QRS duration in ms
        qrs_morphology: "lbbb", "rbbb", "non_specific"
        on_max_beta_blocker: On maximum tolerated beta-blocker dose
        iron_deficient: Has iron deficiency
        race_black: Self-identified Black race
    
    Returns:
        Next treatment steps and recommendations
    """
    recommendations = []
    urgent_actions = []
    contraindications_to_check = []
    
    # Normalize medication list
    current_meds = [m.lower() for m in current_medications]
    has_acei = "acei" in current_meds or "ace-i" in current_meds
    has_arb = "arb" in current_meds
    has_arni = "arni" in current_meds or "sacubitril" in current_meds
    has_bb = "bb" in current_meds or "beta-blocker" in current_meds or "betablocker" in current_meds
    has_mra = "mra" in current_meds or "spironolactone" in current_meds or "eplerenone" in current_meds
    has_sglt2i = "sglt2i" in current_meds or "sglt2" in current_meds or "dapagliflozin" in current_meds or "empagliflozin" in current_meds
    
    has_raas = has_acei or has_arb or has_arni
    
    # Check for quadruple therapy
    on_quadruple = has_raas and has_bb and has_mra and has_sglt2i
    
    # STEP 1: Establish quadruple therapy
    if not on_quadruple:
        if not has_raas:
            if systolic_bp >= 100:
                recommendations.append({
                    "action": "Start ACE-I or ARNI",
                    "class": "I",
                    "level": "A",
                    "details": "ARNI preferred if tolerated; start ACE-I if naive to RAAS inhibition",
                    "contraindications": ["Angioedema history", "Bilateral renal artery stenosis", "K+ >5.5", "Pregnancy"]
                })
            else:
                contraindications_to_check.append("Hypotension - may need to defer RAAS inhibitor")
        
        if not has_bb:
            if heart_rate >= 50 and systolic_bp >= 90:
                recommendations.append({
                    "action": "Start beta-blocker",
                    "class": "I",
                    "level": "A",
                    "details": "Use bisoprolol, carvedilol, metoprolol succinate, or nebivolol",
                    "contraindications": ["Asthma (relative)", "2nd/3rd degree AV block without pacemaker", "Symptomatic bradycardia"]
                })
            else:
                contraindications_to_check.append("Bradycardia/hypotension - may need to defer beta-blocker")
        
        if not has_mra:
            if potassium <= 5.0 and egfr >= 30:
                recommendations.append({
                    "action": "Start MRA (spironolactone or eplerenone)",
                    "class": "I",
                    "level": "A",
                    "details": "Monitor K+ and creatinine within 1-2 weeks",
                    "contraindications": ["K+ >5.0", "eGFR <30"]
                })
            else:
                contraindications_to_check.append(f"K+ {potassium} or eGFR {egfr} - caution with MRA")
        
        if not has_sglt2i:
            if egfr >= 20:
                recommendations.append({
                    "action": "Start SGLT2 inhibitor (dapagliflozin or empagliflozin)",
                    "class": "I", 
                    "level": "A",
                    "details": "Can be started regardless of diabetes status",
                    "contraindications": ["eGFR <20", "Type 1 diabetes"]
                })
    
    # STEP 2: Optimize existing therapy (uptitrate)
    if has_raas and not has_arni and systolic_bp >= 100:
        recommendations.append({
            "action": "Switch ACE-I/ARB to ARNI",
            "class": "I",
            "level": "B",
            "details": "Allow 36h washout from ACE-I before starting ARNI"
        })
    
    # STEP 3: Additional therapies for persistent symptoms
    if on_quadruple and nyha_class >= 2:
        # Ivabradine
        if rhythm == "sinus" and heart_rate >= 70 and on_max_beta_blocker and lvef <= 35:
            recommendations.append({
                "action": "Add ivabradine",
                "class": "IIa",
                "level": "B",
                "details": "For patients in sinus rhythm with HR ≥70 despite max beta-blocker"
            })
        
        # Vericiguat
        if nyha_class >= 2:
            recommendations.append({
                "action": "Consider vericiguat",
                "class": "IIb",
                "level": "B",
                "details": "For worsening HF despite optimal therapy"
            })
        
        # H-ISDN for Black patients
        if race_black and nyha_class >= 3:
            recommendations.append({
                "action": "Add hydralazine + isosorbide dinitrate",
                "class": "IIa",
                "level": "B",
                "details": "Specifically beneficial in self-identified Black patients with NYHA III-IV"
            })
    
    # STEP 4: Iron replacement
    if iron_deficient:
        recommendations.append({
            "action": "IV iron replacement",
            "class": "IIa",
            "level": "A",
            "details": "Ferric carboxymaltose or iron derisomaltose to improve symptoms and reduce HF hospitalization"
        })
    
    # STEP 5: Device therapy check
    device_recommendation = None
    if lvef <= 35 and qrs_duration:
        if qrs_duration >= 130:
            device_recommendation = "Consider CRT evaluation"
        elif qrs_duration < 130:
            device_recommendation = "Consider ICD evaluation if ≥3 months on OMT"
    
    # Calculate therapy completeness
    pillars_present = sum([has_raas, has_bb, has_mra, has_sglt2i])
    
    return {
        "current_therapy_status": {
            "raas_inhibitor": "ARNI" if has_arni else ("ACE-I" if has_acei else ("ARB" if has_arb else "None")),
            "beta_blocker": has_bb,
            "mra": has_mra,
            "sglt2i": has_sglt2i,
            "pillars_present": pillars_present,
            "on_quadruple_therapy": on_quadruple
        },
        "recommendations": recommendations,
        "contraindications_to_check": contraindications_to_check,
        "device_consideration": device_recommendation,
        "parameters": {
            "lvef": lvef,
            "nyha_class": nyha_class,
            "systolic_bp": systolic_bp,
            "heart_rate": heart_rate,
            "rhythm": rhythm
        },
        "quadruple_therapy_goal": [
            "ACE-I/ARB/ARNI",
            "Beta-blocker (bisoprolol, carvedilol, metoprolol succinate, nebivolol)",
            "MRA (spironolactone or eplerenone)",
            "SGLT2i (dapagliflozin or empagliflozin)"
        ],
        "source": "ESC 2021 HF Guidelines"
    }


def pathway_hf_device_therapy(
    lvef: float,
    qrs_duration: int,
    qrs_morphology: str,
    nyha_class: int,
    rhythm: str = "sinus",
    etiology: str = "ischemic",
    months_on_omt: int = 0,
    days_post_mi: Optional[int] = None,
    prior_vt_vf: bool = False,
    high_degree_avb: bool = False,
    expected_pacing_percent: Optional[float] = None,
) -> Dict[str, Any]:
    """
    HF device therapy pathway - ICD and CRT decision support.
    
    Args:
        lvef: LV ejection fraction (%)
        qrs_duration: QRS duration in ms
        qrs_morphology: "lbbb", "rbbb", "non_specific", "normal"
        nyha_class: NYHA class 1-4
        rhythm: "sinus" or "af"
        etiology: "ischemic" or "non_ischemic"
        months_on_omt: Months on optimal medical therapy
        days_post_mi: Days since MI (if applicable)
        prior_vt_vf: Prior sustained VT/VF
        high_degree_avb: High-degree AV block requiring pacing
        expected_pacing_percent: Expected RV pacing percentage
    
    Returns:
        Device recommendation
    """
    recommendations = []
    defer_reasons = []
    
    # Secondary prevention ICD
    if prior_vt_vf:
        recommendations.append({
            "device": "ICD",
            "indication": "Secondary prevention",
            "class": "I",
            "level": "A",
            "details": "Prior VF or hemodynamically unstable VT"
        })
    
    # Timing considerations
    if days_post_mi is not None and days_post_mi < 40:
        defer_reasons.append(f"<40 days post-MI ({days_post_mi} days) - reassess LVEF at 6-12 weeks")
    
    if months_on_omt < 3 and not prior_vt_vf:
        defer_reasons.append(f"<3 months on OMT ({months_on_omt} months) - reassess after optimization")
    
    # CRT evaluation
    if lvef <= 35 and qrs_duration >= 130:
        if qrs_morphology == "lbbb":
            if qrs_duration >= 150:
                crt_class = "I"
                crt_level = "A"
            else:
                crt_class = "IIa"
                crt_level = "B"
        else:  # Non-LBBB
            if qrs_duration >= 150:
                crt_class = "IIa"
                crt_level = "B"
            else:
                crt_class = "IIb"
                crt_level = "B"
        
        recommendations.append({
            "device": "CRT",
            "indication": f"QRS {qrs_duration}ms, {qrs_morphology.upper()}, LVEF {lvef}%",
            "class": crt_class,
            "level": crt_level,
            "details": "LBBB with QRS ≥150ms has strongest evidence"
        })
    
    # Primary prevention ICD (if CRT not indicated)
    if not any(r["device"] == "CRT" for r in recommendations):
        if lvef <= 35 and months_on_omt >= 3:
            if etiology == "ischemic":
                if nyha_class in [2, 3]:
                    recommendations.append({
                        "device": "ICD",
                        "indication": "Primary prevention - ischemic",
                        "class": "I",
                        "level": "A",
                        "details": "Ischemic CM, LVEF ≤35%, NYHA II-III"
                    })
                elif nyha_class == 1 and lvef <= 30:
                    recommendations.append({
                        "device": "ICD",
                        "indication": "Primary prevention - ischemic",
                        "class": "I",
                        "level": "A",
                        "details": "Ischemic CM, LVEF ≤30%, NYHA I"
                    })
            else:  # Non-ischemic
                if nyha_class in [2, 3]:
                    recommendations.append({
                        "device": "ICD",
                        "indication": "Primary prevention - non-ischemic",
                        "class": "IIa",
                        "level": "A",
                        "details": "Non-ischemic CM, LVEF ≤35%, NYHA II-III"
                    })
    
    # CRT vs RV pacing for AVB
    if high_degree_avb and lvef < 40:
        recommendations.append({
            "device": "CRT (rather than RV pacing)",
            "indication": "AVB with reduced LVEF",
            "class": "I",
            "level": "A",
            "details": "CRT preferred over RV pacing when LVEF <40% and pacing indication exists"
        })
    
    # CRT-D vs CRT-P
    crt_recommendation = next((r for r in recommendations if "CRT" in r["device"]), None)
    if crt_recommendation:
        if etiology == "ischemic" or prior_vt_vf:
            crt_recommendation["device"] = "CRT-D"
            crt_recommendation["details"] += "; CRT-D preferred given ischemic etiology or arrhythmic risk"
        else:
            crt_recommendation["details"] += "; CRT-P vs CRT-D decision should be individualized"
    
    # Final device recommendation
    if recommendations:
        primary_recommendation = recommendations[0]
    else:
        primary_recommendation = {"device": "None currently indicated", "details": "Continue medical optimization"}
    
    return {
        "primary_recommendation": primary_recommendation,
        "all_recommendations": recommendations,
        "defer_reasons": defer_reasons,
        "parameters": {
            "lvef": lvef,
            "qrs_duration": qrs_duration,
            "qrs_morphology": qrs_morphology,
            "nyha_class": nyha_class,
            "etiology": etiology,
            "months_on_omt": months_on_omt
        },
        "source": "ESC 2021 HF Guidelines, ESC 2021 Pacing/CRT Guidelines"
    }


def get_hf_medication_targets() -> Dict[str, Any]:
    """
    Get target doses for HF medications.
    
    Returns:
        Target doses for all guideline-directed HF medications
    """
    return {
        "acei": {
            "enalapril": {"starting": "2.5 mg BID", "target": "10-20 mg BID"},
            "lisinopril": {"starting": "2.5-5 mg daily", "target": "20-40 mg daily"},
            "ramipril": {"starting": "1.25-2.5 mg daily", "target": "10 mg daily"},
            "captopril": {"starting": "6.25 mg TID", "target": "50 mg TID"},
        },
        "arb": {
            "candesartan": {"starting": "4-8 mg daily", "target": "32 mg daily"},
            "valsartan": {"starting": "40 mg BID", "target": "160 mg BID"},
            "losartan": {"starting": "25-50 mg daily", "target": "150 mg daily"},
        },
        "arni": {
            "sacubitril_valsartan": {"starting": "24/26 mg or 49/51 mg BID", "target": "97/103 mg BID"},
        },
        "beta_blocker": {
            "bisoprolol": {"starting": "1.25 mg daily", "target": "10 mg daily"},
            "carvedilol": {"starting": "3.125 mg BID", "target": "25 mg BID (50 mg BID if >85kg)"},
            "metoprolol_succinate": {"starting": "12.5-25 mg daily", "target": "200 mg daily"},
            "nebivolol": {"starting": "1.25 mg daily", "target": "10 mg daily"},
        },
        "mra": {
            "spironolactone": {"starting": "12.5-25 mg daily", "target": "25-50 mg daily"},
            "eplerenone": {"starting": "25 mg daily", "target": "50 mg daily"},
        },
        "sglt2i": {
            "dapagliflozin": {"dose": "10 mg daily"},
            "empagliflozin": {"dose": "10 mg daily"},
        },
        "ivabradine": {
            "dose": {"starting": "5 mg BID", "target": "7.5 mg BID"},
            "indication": "Sinus rhythm, HR ≥70, on max beta-blocker, LVEF ≤35%"
        },
        "hydralazine_isdn": {
            "dose": {"starting": "37.5/20 mg TID", "target": "75/40 mg TID"},
            "indication": "Self-identified Black patients with NYHA III-IV"
        },
        "uptitration_notes": [
            "Uptitrate every 2-4 weeks as tolerated",
            "Monitor BP, HR, K+, creatinine with each titration",
            "Accept modest increases in creatinine (up to 50% or 266 µmol/L)",
            "Hold/reduce if symptomatic hypotension, hyperkalemia, or AKI"
        ],
        "source": "ESC 2021 HF Guidelines"
    }
