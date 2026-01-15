"""
Cardiac Device Assessment Tools.

ICD, CRT, and Pacemaker indication assessments.
Based on 2021 ESC Cardiac Pacing/CRT and 2022 ESC VA/SCD Guidelines.
"""

from typing import Dict, Any, Optional, List


def assess_crt_indication(
    lvef: float,
    qrs_duration: int,
    qrs_morphology: str,
    rhythm: str = "sinus",
    nyha_class: int = 2,
    on_optimal_medical_therapy: bool = True,
    av_block_pacing_indication: bool = False,
    expected_rv_pacing_percent: Optional[float] = None,
    has_icd_indication: bool = False,
) -> Dict[str, Any]:
    """
    Assess CRT indication based on ESC guidelines.
    
    Args:
        lvef: Left ventricular ejection fraction (%)
        qrs_duration: QRS duration in ms
        qrs_morphology: "lbbb", "rbbb", "non_specific"
        rhythm: "sinus" or "af"
        nyha_class: NYHA functional class (1-4)
        on_optimal_medical_therapy: On OMT for ≥3 months
        av_block_pacing_indication: Has indication for ventricular pacing (AVB)
        expected_rv_pacing_percent: Expected RV pacing percentage
        has_icd_indication: Has concurrent ICD indication
    
    Returns:
        CRT indication class and device recommendation
    """
    indication_class = None
    evidence_level = None
    rationale = []
    device_recommendation = None
    
    # QRS < 130 ms - no CRT indication
    if qrs_duration < 130:
        indication_class = "III"
        rationale.append("QRS <130 ms - CRT not indicated")
        return {
            "crt_indicated": False,
            "indication_class": indication_class,
            "rationale": rationale,
            "device_recommendation": "ICD only if indicated; no CRT",
            "source": "ESC 2021 Pacing/CRT Guidelines"
        }
    
    # Main CRT indications (sinus rhythm)
    if rhythm == "sinus" and lvef <= 35 and nyha_class in [2, 3, 4]:
        if qrs_morphology == "lbbb":
            if qrs_duration >= 150:
                indication_class = "I"
                evidence_level = "A"
                rationale.append("LBBB with QRS ≥150 ms, LVEF ≤35%, NYHA II-IV")
            elif qrs_duration >= 130:
                indication_class = "IIa"
                evidence_level = "B"
                rationale.append("LBBB with QRS 130-149 ms, LVEF ≤35%, NYHA II-IV")
        else:  # Non-LBBB
            if qrs_duration >= 150:
                indication_class = "IIa"
                evidence_level = "B"
                rationale.append("Non-LBBB with QRS ≥150 ms, LVEF ≤35%, NYHA II-IV")
            elif qrs_duration >= 130:
                indication_class = "IIb"
                evidence_level = "B"
                rationale.append("Non-LBBB with QRS 130-149 ms, LVEF ≤35%")
    
    # NYHA IV ambulatory
    if nyha_class == 4:
        rationale.append("NYHA IV patients should be ambulatory and not dependent on IV inotropes")
    
    # AF with HF
    if rhythm == "af" and lvef <= 35 and qrs_duration >= 130:
        if nyha_class in [3, 4]:
            indication_class = "IIa"
            evidence_level = "C"
            rationale.append("Permanent AF with HF, LVEF ≤35%, QRS ≥130 ms, NYHA III-IV")
            rationale.append("Strategy to ensure biventricular capture required (rate control or AVJ ablation)")
    
    # Pacing indication with HF
    if av_block_pacing_indication and lvef < 40:
        indication_class = "I"
        evidence_level = "A"
        rationale.append("AVB with pacing indication + LVEF <40% - CRT rather than RV pacing")
    
    # Upgrade consideration
    if expected_rv_pacing_percent and expected_rv_pacing_percent > 40 and lvef < 40:
        if indication_class is None:
            indication_class = "IIa"
            evidence_level = "B"
        rationale.append(f"High expected RV pacing ({expected_rv_pacing_percent}%) with reduced LVEF - consider CRT")
    
    # OMT requirement
    if not on_optimal_medical_therapy and indication_class in ["I", "IIa"]:
        rationale.append("Note: Should be on OMT for ≥3 months before CRT unless urgent")
    
    # Device selection
    if indication_class in ["I", "IIa", "IIb"]:
        if has_icd_indication:
            device_recommendation = "CRT-D"
            rationale.append("Concurrent ICD indication - CRT-D recommended")
        else:
            device_recommendation = "CRT-P or CRT-D based on individual assessment"
            rationale.append("CRT-D may be considered based on ischemic etiology, age, comorbidities")
    
    crt_indicated = indication_class in ["I", "IIa", "IIb"]
    
    return {
        "crt_indicated": crt_indicated,
        "indication_class": indication_class,
        "evidence_level": evidence_level,
        "device_recommendation": device_recommendation,
        "rationale": rationale,
        "parameters": {
            "lvef": lvef,
            "qrs_duration": qrs_duration,
            "qrs_morphology": qrs_morphology,
            "rhythm": rhythm,
            "nyha_class": nyha_class
        },
        "key_thresholds": {
            "qrs_minimum": "≥130 ms",
            "lvef_maximum": "≤35%",
            "lbbb_strong_benefit": "QRS ≥150 ms"
        },
        "source": "ESC 2021 Cardiac Pacing/CRT Guidelines"
    }


def assess_dcm_icd_indication(
    lvef: float,
    nyha_class: int,
    months_on_omt: int = 3,
    lmna_mutation: bool = False,
    pln_mutation: bool = False,
    flnc_mutation: bool = False,
    rbm20_mutation: bool = False,
    syncope: bool = False,
    lge_on_cmr: bool = False,
    nsvt: bool = False,
    inducible_smvt_pes: bool = False,
    prior_vt_vf: bool = False,
    av_conduction_delay: bool = False,
) -> Dict[str, Any]:
    """
    Assess ICD indication in dilated cardiomyopathy (DCM/HNDCM).
    
    Based on ESC 2022 VA/SCD Guidelines with genetic risk factors.
    
    Args:
        lvef: LV ejection fraction (%)
        nyha_class: NYHA functional class (1-4)
        months_on_omt: Months on optimal medical therapy
        lmna_mutation: LMNA mutation carrier
        pln_mutation: PLN mutation carrier
        flnc_mutation: FLNC mutation carrier
        rbm20_mutation: RBM20 mutation carrier
        syncope: Unexplained syncope
        lge_on_cmr: Late gadolinium enhancement on CMR
        nsvt: Non-sustained VT documented
        inducible_smvt_pes: Inducible sustained monomorphic VT at PES
        prior_vt_vf: Prior sustained VT or VF (secondary prevention)
        av_conduction_delay: AV conduction delay (PR >200ms or QRS >120ms)
    
    Returns:
        ICD indication assessment
    """
    indication = None
    indication_class = None
    rationale = []
    
    # Count risk factors for genetic risk assessment
    high_risk_genes = []
    if lmna_mutation:
        high_risk_genes.append("LMNA")
    if pln_mutation:
        high_risk_genes.append("PLN")
    if flnc_mutation:
        high_risk_genes.append("FLNC")
    if rbm20_mutation:
        high_risk_genes.append("RBM20")
    
    additional_risk_factors = []
    if syncope:
        additional_risk_factors.append("Unexplained syncope")
    if lge_on_cmr:
        additional_risk_factors.append("LGE on CMR")
    if inducible_smvt_pes:
        additional_risk_factors.append("Inducible SMVT at PES")
    if nsvt:
        additional_risk_factors.append("NSVT")
    
    # Secondary prevention (Class I)
    if prior_vt_vf:
        indication = "secondary_prevention"
        indication_class = "I"
        rationale.append("Prior sustained VT/VF - secondary prevention ICD")
    
    # LMNA-specific pathway
    elif lmna_mutation:
        # Calculate approximate LMNA risk
        lmna_risk_factors = sum([
            lvef < 50,
            nsvt,
            not av_conduction_delay,  # Actually, presence adds risk
            True  # male adds risk - simplified
        ])
        
        if nsvt or lvef < 50 or av_conduction_delay:
            indication = "primary_prevention"
            indication_class = "IIa"
            rationale.append("LMNA mutation with risk factors (NSVT, LVEF <50%, or AV delay)")
            rationale.append("Consider formal LMNA risk calculator for 5-year risk ≥10%")
    
    # Standard DCM primary prevention
    elif lvef <= 35 and nyha_class in [2, 3] and months_on_omt >= 3:
        indication = "primary_prevention"
        indication_class = "IIa"
        rationale.append("DCM with LVEF ≤35%, NYHA II-III, ≥3 months OMT")
    
    # High-risk genetic variants with additional risk factors
    elif len(high_risk_genes) > 0 and lvef < 50:
        risk_factor_count = len(additional_risk_factors)
        if risk_factor_count >= 2:
            indication = "primary_prevention"
            indication_class = "IIa"
            rationale.append(f"High-risk gene ({', '.join(high_risk_genes)}) + LVEF <50% + ≥2 risk factors")
        elif risk_factor_count >= 1:
            indication = "consider"
            indication_class = "IIb"
            rationale.append(f"High-risk gene ({', '.join(high_risk_genes)}) + LVEF <50% + 1 risk factor")
    
    # Unexplained syncope with reduced EF
    elif syncope and lvef <= 40:
        indication = "consider"
        indication_class = "IIa"
        rationale.append("Unexplained syncope with LVEF ≤40%")
    
    # OMT duration check
    if months_on_omt < 3 and indication == "primary_prevention":
        rationale.append(f"Note: Currently {months_on_omt} months on OMT - reassess LVEF at 3+ months")
    
    # No indication
    if indication is None:
        indication = "not_indicated"
        rationale.append("ICD not indicated based on current criteria")
    
    return {
        "indication": indication,
        "indication_class": indication_class,
        "rationale": rationale,
        "high_risk_genes": high_risk_genes,
        "additional_risk_factors": additional_risk_factors,
        "parameters": {
            "lvef": lvef,
            "nyha_class": nyha_class,
            "months_on_omt": months_on_omt,
            "genetic_mutations": high_risk_genes,
            "syncope": syncope,
            "lge_on_cmr": lge_on_cmr,
            "nsvt": nsvt,
            "prior_vt_vf": prior_vt_vf
        },
        "recommendations": [
            "CMR with LGE assessment recommended for risk stratification",
            "Genetic testing and family screening if DCM etiology unclear",
            "Ensure OMT optimized for ≥3 months before primary prevention ICD"
        ],
        "source": "ESC 2022 VA/SCD Guidelines"
    }


def assess_arvc_icd_indication(
    definite_arvc: bool,
    rv_dysfunction: str = "none",
    lv_dysfunction: str = "none",
    syncope: bool = False,
    nsvt: bool = False,
    inducible_smvt_pes: bool = False,
    prior_vt_vf: bool = False,
    hemodynamic_tolerance: str = "unknown",
    family_history_scd: bool = False,
) -> Dict[str, Any]:
    """
    Assess ICD indication in arrhythmogenic right ventricular cardiomyopathy (ARVC).
    
    Args:
        definite_arvc: Meets definite ARVC diagnostic criteria
        rv_dysfunction: "none", "mild", "moderate", "severe"
        lv_dysfunction: "none", "mild", "moderate", "severe"
        syncope: Unexplained syncope
        nsvt: Non-sustained VT documented
        inducible_smvt_pes: Inducible sustained monomorphic VT at PES
        prior_vt_vf: Prior sustained VT or VF
        hemodynamic_tolerance: "tolerated", "not_tolerated", "unknown"
        family_history_scd: Family history of SCD
    
    Returns:
        ICD indication assessment
    """
    indication_class = None
    rationale = []
    
    # Secondary prevention (Class I)
    if prior_vt_vf:
        if hemodynamic_tolerance == "not_tolerated":
            indication_class = "I"
            rationale.append("Hemodynamically not-tolerated VT/VF")
        else:
            indication_class = "IIa"
            rationale.append("Hemodynamically tolerated sustained VT")
    
    # Primary prevention - definite ARVC with risk factors
    elif definite_arvc:
        # Moderate or severe dysfunction
        if rv_dysfunction in ["moderate", "severe"] or lv_dysfunction in ["moderate", "severe"]:
            indication_class = "IIa"
            rationale.append("ARVC with moderate/severe ventricular dysfunction")
        
        # Symptomatic with risk factors
        if syncope:
            if indication_class is None:
                indication_class = "IIa"
            rationale.append("Unexplained syncope in definite ARVC")
        
        if nsvt:
            if rv_dysfunction in ["mild", "moderate", "severe"] or lv_dysfunction in ["mild", "moderate", "severe"]:
                if indication_class is None:
                    indication_class = "IIa"
                rationale.append("NSVT with ventricular dysfunction")
            else:
                if indication_class is None:
                    indication_class = "IIb"
                rationale.append("NSVT without significant dysfunction - may consider")
        
        if inducible_smvt_pes:
            if indication_class is None:
                indication_class = "IIb"
            rationale.append("Inducible SMVT at PES")
    
    # No clear indication
    if indication_class is None:
        rationale.append("No clear ICD indication - close monitoring recommended")
    
    return {
        "indication_class": indication_class,
        "rationale": rationale,
        "parameters": {
            "definite_arvc": definite_arvc,
            "rv_dysfunction": rv_dysfunction,
            "lv_dysfunction": lv_dysfunction,
            "syncope": syncope,
            "nsvt": nsvt,
            "inducible_smvt_pes": inducible_smvt_pes,
            "prior_vt_vf": prior_vt_vf
        },
        "notes": [
            "Competitive sports and high-intensity exercise should be avoided",
            "Family screening with ECG, imaging, and genetic testing recommended",
            "Catheter ablation may reduce ICD shocks but does not obviate ICD need"
        ],
        "source": "ESC 2022 VA/SCD Guidelines"
    }


def assess_sarcoidosis_icd_indication(
    lvef: float,
    lge_extent: str = "none",
    acute_inflammation_resolved: bool = True,
    sustained_vt: bool = False,
    aborted_cardiac_arrest: bool = False,
    inducible_smvt_pes: bool = False,
    syncope: bool = False,
) -> Dict[str, Any]:
    """
    Assess ICD indication in cardiac sarcoidosis.
    
    Args:
        lvef: LV ejection fraction (%)
        lge_extent: "none", "minor", "significant"
        acute_inflammation_resolved: Acute inflammation has resolved
        sustained_vt: History of sustained VT
        aborted_cardiac_arrest: Survived cardiac arrest
        inducible_smvt_pes: Inducible sustained VT at PES
        syncope: Unexplained syncope
    
    Returns:
        ICD indication assessment
    """
    indication_class = None
    rationale = []
    
    # Class I indications
    if aborted_cardiac_arrest:
        indication_class = "I"
        rationale.append("Aborted cardiac arrest")
    
    if sustained_vt:
        indication_class = "I"
        rationale.append("Documented sustained VT")
    
    if lvef <= 35:
        indication_class = "I"
        rationale.append(f"LVEF ≤35% ({lvef}%)")
    
    # Class IIa - significant LGE with preserved EF
    if lvef > 35 and lge_extent == "significant" and acute_inflammation_resolved:
        indication_class = "IIa"
        rationale.append("LVEF >35% with significant LGE (after acute inflammation resolved)")
    
    # Class IIa - intermediate EF with LGE + inducible
    if 35 < lvef <= 50 and lge_extent in ["minor", "significant"]:
        if inducible_smvt_pes:
            indication_class = "IIa"
            rationale.append("LVEF 35-50% with LGE and inducible SMVT at PES")
        else:
            if indication_class is None:
                indication_class = "IIb"
            rationale.append("LVEF 35-50% with LGE - consider PES for risk stratification")
    
    # Syncope
    if syncope and indication_class is None:
        indication_class = "IIb"
        rationale.append("Unexplained syncope - evaluate for ICD")
    
    # No indication
    if indication_class is None:
        rationale.append("No clear ICD indication - monitor for disease progression")
    
    return {
        "indication_class": indication_class,
        "rationale": rationale,
        "parameters": {
            "lvef": lvef,
            "lge_extent": lge_extent,
            "acute_inflammation_resolved": acute_inflammation_resolved,
            "sustained_vt": sustained_vt,
            "aborted_cardiac_arrest": aborted_cardiac_arrest,
            "inducible_smvt_pes": inducible_smvt_pes
        },
        "notes": [
            "Immunosuppression should be optimized before ICD decision if active inflammation",
            "PET may help assess disease activity",
            "Re-evaluate LVEF after immunosuppressive therapy"
        ],
        "source": "ESC 2022 VA/SCD Guidelines"
    }


def assess_pacing_indication(
    avb_degree: str,
    snd_documented: bool = False,
    symptoms_correlated: bool = False,
    symptoms: Optional[List[str]] = None,
    sinus_pause_seconds: Optional[float] = None,
    reversible_cause: bool = False,
    hv_interval_ms: Optional[int] = None,
    bifascicular_block: bool = False,
    alternating_bbb: bool = False,
) -> Dict[str, Any]:
    """
    Assess pacemaker indication.
    
    Args:
        avb_degree: "none", "first", "second_type1", "second_type2", "third", "high_degree"
        snd_documented: Sinus node dysfunction documented
        symptoms_correlated: Symptoms clearly correlated with bradycardia
        symptoms: List of symptoms (syncope, presyncope, fatigue, dyspnea)
        sinus_pause_seconds: Duration of documented sinus pause
        reversible_cause: Reversible/transient cause present
        hv_interval_ms: HV interval at EPS (if performed)
        bifascicular_block: Bifascicular block present
        alternating_bbb: Alternating bundle branch block
    
    Returns:
        Pacing indication assessment
    """
    if symptoms is None:
        symptoms = []
    
    indication_class = None
    rationale = []
    
    # Reversible causes
    if reversible_cause:
        rationale.append("Reversible cause present - treat underlying cause first")
        return {
            "pacing_indicated": False,
            "indication_class": "III",
            "rationale": rationale,
            "source": "ESC 2021 Cardiac Pacing Guidelines"
        }
    
    # AV Block indications
    if avb_degree == "third":
        indication_class = "I"
        rationale.append("Third-degree (complete) AV block")
    elif avb_degree == "second_type2":
        indication_class = "I"
        rationale.append("Second-degree type 2 (Mobitz II) AV block")
    elif avb_degree == "high_degree":
        indication_class = "I"
        rationale.append("High-degree AV block")
    elif avb_degree == "second_type1" and symptoms_correlated:
        indication_class = "IIa"
        rationale.append("Symptomatic second-degree type 1 (Wenckebach) AV block")
    elif avb_degree == "first" and symptoms_correlated:
        # PR > 300ms with symptoms
        indication_class = "IIa"
        rationale.append("First-degree AV block with symptoms (likely pacemaker syndrome)")
    
    # Alternating BBB
    if alternating_bbb:
        indication_class = "IIa"
        rationale.append("Alternating bundle branch block")
    
    # Sinus node dysfunction
    if snd_documented and symptoms_correlated:
        if indication_class is None:
            indication_class = "I"
        rationale.append("Sinus node dysfunction with documented symptom correlation")
    
    # Sinus pause assessment
    if sinus_pause_seconds:
        if sinus_pause_seconds > 6 and not symptoms_correlated:
            if indication_class is None:
                indication_class = "IIb"
            rationale.append(f"Asymptomatic sinus pause >6 seconds ({sinus_pause_seconds}s)")
        elif sinus_pause_seconds > 3 and symptoms_correlated:
            if indication_class is None:
                indication_class = "I"
            rationale.append(f"Symptomatic sinus pause >3 seconds ({sinus_pause_seconds}s)")
    
    # Bifascicular block with syncope
    if bifascicular_block and "syncope" in symptoms:
        if hv_interval_ms and hv_interval_ms > 70:
            indication_class = "I"
            rationale.append("Bifascicular block with syncope and HV >70 ms")
        else:
            indication_class = "IIa"
            rationale.append("Bifascicular block with unexplained syncope - consider EPS")
    
    pacing_indicated = indication_class in ["I", "IIa", "IIb"]
    
    return {
        "pacing_indicated": pacing_indicated,
        "indication_class": indication_class,
        "rationale": rationale,
        "parameters": {
            "avb_degree": avb_degree,
            "snd_documented": snd_documented,
            "symptoms_correlated": symptoms_correlated,
            "symptoms": symptoms,
            "sinus_pause_seconds": sinus_pause_seconds,
            "bifascicular_block": bifascicular_block
        },
        "source": "ESC 2021 Cardiac Pacing Guidelines"
    }


def select_pacing_mode(
    primary_indication: str,
    rhythm: str = "sinus",
    av_conduction_intact: bool = True,
    chronotropic_incompetence: bool = False,
    lvef: float = 55.0,
    expected_pacing_percent: Optional[float] = None,
    frail_elderly: bool = False,
) -> Dict[str, Any]:
    """
    Select appropriate pacing mode.
    
    Args:
        primary_indication: "snd", "avb", "syncope", "af_slow"
        rhythm: "sinus" or "af"
        av_conduction_intact: AV conduction is intact
        chronotropic_incompetence: Chronotropic incompetence present
        lvef: LV ejection fraction (%)
        expected_pacing_percent: Expected ventricular pacing percentage
        frail_elderly: Frail/elderly with limited mobility
    
    Returns:
        Recommended pacing mode
    """
    mode = None
    rationale = []
    programming_notes = []
    
    # AF with slow ventricular response
    if rhythm == "af" or primary_indication == "af_slow":
        mode = "VVIR"
        rationale.append("Permanent AF - single chamber ventricular pacing")
        if lvef < 40:
            rationale.append("Consider CRT rather than VVIR if high pacing burden expected")
    
    # Sinus node dysfunction
    elif primary_indication == "snd":
        if av_conduction_intact:
            mode = "DDD" if not chronotropic_incompetence else "DDDR"
            rationale.append("SND with intact AV conduction - DDD with algorithms to minimize VP")
            programming_notes.append("Enable MVP or AAI-DDD algorithm to minimize ventricular pacing")
        else:
            mode = "DDDR" if chronotropic_incompetence else "DDD"
            rationale.append("SND with AV conduction disease")
    
    # AV block
    elif primary_indication == "avb":
        if frail_elderly:
            mode = "VVI"
            rationale.append("Frail/elderly - VVI may be acceptable")
        else:
            mode = "DDD"
            rationale.append("AV block - DDD preferred over VVI")
            programming_notes.append("DDD reduces risk of pacemaker syndrome")
        
        # Consider CRT
        if lvef < 40 and expected_pacing_percent and expected_pacing_percent > 40:
            rationale.append("Consider CRT rather than RV pacing with LVEF <40% and high pacing burden")
    
    # Syncope (neurocardiogenic)
    elif primary_indication == "syncope":
        mode = "DDD"
        rationale.append("Neurocardiogenic syncope - DDD with rate-drop response")
        programming_notes.append("Consider rate-drop response or closed-loop stimulation")
    
    # Rate response
    if chronotropic_incompetence and "R" not in (mode or ""):
        mode = mode + "R" if mode else "DDDR"
        rationale.append("Chronotropic incompetence - rate-responsive mode")
    
    return {
        "recommended_mode": mode,
        "rationale": rationale,
        "programming_notes": programming_notes,
        "parameters": {
            "primary_indication": primary_indication,
            "rhythm": rhythm,
            "av_conduction_intact": av_conduction_intact,
            "chronotropic_incompetence": chronotropic_incompetence,
            "lvef": lvef,
            "expected_pacing_percent": expected_pacing_percent
        },
        "source": "ESC 2021 Cardiac Pacing Guidelines"
    }
