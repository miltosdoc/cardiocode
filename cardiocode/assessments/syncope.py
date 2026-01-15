"""
Syncope Assessment Tools.

Based on 2018 ESC Syncope Guidelines.
"""

from typing import Dict, Any, Optional, List


def assess_syncope_risk(
    # History features
    syncope_during_exertion: bool = False,
    syncope_supine: bool = False,
    syncope_without_prodrome: bool = False,
    palpitations_before_syncope: bool = False,
    family_history_scd_under_40: bool = False,
    
    # Cardiovascular history
    structural_heart_disease: bool = False,
    known_coronary_disease: bool = False,
    heart_failure: bool = False,
    low_lvef: bool = False,
    prior_mi: bool = False,
    
    # ECG findings
    sinus_bradycardia_under_40: bool = False,
    sinus_pause_over_3s: bool = False,
    mobitz_ii_or_complete_avb: bool = False,
    alternating_bbb: bool = False,
    vt_or_rapid_svt: bool = False,
    pacemaker_icd_malfunction: bool = False,
    brugada_pattern: bool = False,
    long_qt: bool = False,
    short_qt: bool = False,
    arvc_pattern: bool = False,
    bifascicular_block: bool = False,
    other_ivcd: bool = False,
    
    # Low risk features
    long_history_similar_episodes: bool = False,
    typical_vasovagal_prodrome: bool = False,
    triggered_by_pain_fear_standing: bool = False,
    situational_trigger: bool = False,
    absence_of_heart_disease: bool = True,
    
    # Injury
    significant_injury: bool = False,
) -> Dict[str, Any]:
    """
    Assess syncope risk based on ESC guideline criteria.
    
    Returns risk category and disposition recommendation.
    """
    high_risk_major = []
    high_risk_minor = []
    low_risk_features = []
    
    # Major high-risk features - underlying disease
    if structural_heart_disease or heart_failure or low_lvef:
        high_risk_major.append("Structural heart disease/HF/low LVEF")
    if known_coronary_disease or prior_mi:
        high_risk_major.append("Known CAD/prior MI")
    if syncope_during_exertion:
        high_risk_major.append("Syncope during exertion")
    if syncope_supine:
        high_risk_major.append("Syncope while supine")
    if palpitations_before_syncope:
        high_risk_major.append("Sudden palpitations immediately before syncope")
    
    # Major high-risk features - ECG
    if sinus_bradycardia_under_40:
        high_risk_major.append("Sinus bradycardia <40 bpm (awake, non-athlete)")
    if sinus_pause_over_3s:
        high_risk_major.append("Sinus pause >3 seconds")
    if mobitz_ii_or_complete_avb:
        high_risk_major.append("Mobitz II or complete AV block")
    if alternating_bbb:
        high_risk_major.append("Alternating BBB")
    if vt_or_rapid_svt:
        high_risk_major.append("VT or rapid paroxysmal SVT")
    if pacemaker_icd_malfunction:
        high_risk_major.append("Pacemaker/ICD malfunction with pauses")
    
    # Minor high-risk features - history
    if syncope_without_prodrome:
        high_risk_minor.append("Syncope without prodrome or <5 seconds prodrome")
    if family_history_scd_under_40:
        high_risk_minor.append("Family history of SCD <40 years")
    
    # Minor high-risk features - ECG
    if bifascicular_block:
        high_risk_minor.append("Bifascicular block")
    if other_ivcd:
        high_risk_minor.append("Other intraventricular conduction delay (QRS >120ms)")
    if brugada_pattern:
        high_risk_minor.append("Brugada pattern")
    if long_qt or short_qt:
        high_risk_minor.append("Long or short QT interval")
    if arvc_pattern:
        high_risk_minor.append("ARVC pattern (T-wave inversion right precordial, epsilon waves)")
    
    # Low-risk features
    if long_history_similar_episodes:
        low_risk_features.append("Long history of recurrent similar episodes")
    if typical_vasovagal_prodrome:
        low_risk_features.append("Typical vasovagal prodrome (pallor, sweating, nausea)")
    if triggered_by_pain_fear_standing:
        low_risk_features.append("Triggered by pain, fear, or prolonged standing")
    if situational_trigger:
        low_risk_features.append("Situational trigger (micturition, defecation, cough)")
    if absence_of_heart_disease:
        low_risk_features.append("Absence of structural heart disease")
    
    # Determine risk category and disposition
    if len(high_risk_major) > 0:
        risk_category = "High"
        if significant_injury or vt_or_rapid_svt or mobitz_ii_or_complete_avb:
            disposition = "Hospital admission"
        else:
            disposition = "ED observation unit or hospital admission"
        urgent_evaluation = True
    elif len(high_risk_minor) > 0:
        risk_category = "Intermediate"
        disposition = "ED observation or Syncope Unit; may consider early discharge with urgent outpatient evaluation"
        urgent_evaluation = True
    elif len(low_risk_features) >= 2 and len(high_risk_major) == 0 and len(high_risk_minor) == 0:
        risk_category = "Low"
        disposition = "May be discharged with outpatient follow-up"
        urgent_evaluation = False
    else:
        risk_category = "Intermediate (uncertain)"
        disposition = "ED observation recommended for risk stratification"
        urgent_evaluation = True
    
    # Recommended investigations
    investigations = ["12-lead ECG (if not done)"]
    if risk_category in ["High", "Intermediate"]:
        investigations.extend([
            "Continuous ECG monitoring",
            "Echocardiography",
            "Laboratory tests (troponin if cardiac suspected)"
        ])
        if structural_heart_disease or palpitations_before_syncope:
            investigations.append("Consider electrophysiology study")
    
    return {
        "risk_category": risk_category,
        "disposition": disposition,
        "urgent_evaluation_needed": urgent_evaluation,
        "high_risk_major_features": high_risk_major,
        "high_risk_minor_features": high_risk_minor,
        "low_risk_features": low_risk_features,
        "recommended_investigations": investigations,
        "notes": [
            "Risk scores (EGSYS, San Francisco Rule, OESIL) have not shown better performance than clinical judgment",
            "Clinical assessment based on high/low risk features is recommended"
        ],
        "source": "ESC 2018 Syncope Guidelines"
    }


def classify_syncope_etiology(
    # Triggers and circumstances
    triggered_by_pain_fear: bool = False,
    triggered_by_prolonged_standing: bool = False,
    triggered_by_crowded_hot_place: bool = False,
    triggered_by_meal: bool = False,
    triggered_by_cough: bool = False,
    triggered_by_defecation_micturition: bool = False,
    triggered_by_head_rotation_pressure: bool = False,
    post_exercise: bool = False,
    
    # Prodrome
    pallor_sweating_nausea: bool = False,
    lightheadedness: bool = False,
    palpitations_prodrome: bool = False,
    no_prodrome: bool = False,
    
    # Context
    age_over_40: bool = False,
    standing_at_onset: bool = False,
    supine_at_onset: bool = False,
    exertional: bool = False,
    
    # Recovery
    rapid_recovery: bool = True,
    prolonged_confusion: bool = False,
    
    # Orthostatic data
    orthostatic_bp_drop: bool = False,
    on_vasodilators: bool = False,
    
    # Cardiac history
    structural_heart_disease: bool = False,
    abnormal_ecg: bool = False,
) -> Dict[str, Any]:
    """
    Classify likely syncope etiology based on clinical features.
    
    Returns most likely diagnosis and diagnostic certainty.
    """
    diagnoses = []
    
    # Vasovagal syncope
    vasovagal_score = 0
    if triggered_by_pain_fear or triggered_by_prolonged_standing or triggered_by_crowded_hot_place:
        vasovagal_score += 2
    if pallor_sweating_nausea:
        vasovagal_score += 2
    if rapid_recovery:
        vasovagal_score += 1
    if standing_at_onset:
        vasovagal_score += 1
    
    if vasovagal_score >= 4:
        diagnoses.append({
            "diagnosis": "Vasovagal syncope",
            "certainty": "Confirmed" if vasovagal_score >= 5 else "Highly probable",
            "class": "I"
        })
    
    # Situational syncope
    if triggered_by_cough or triggered_by_defecation_micturition or triggered_by_meal or post_exercise:
        trigger_name = []
        if triggered_by_cough:
            trigger_name.append("cough")
        if triggered_by_defecation_micturition:
            trigger_name.append("micturition/defecation")
        if triggered_by_meal:
            trigger_name.append("post-prandial")
        if post_exercise:
            trigger_name.append("post-exercise")
        
        diagnoses.append({
            "diagnosis": f"Situational syncope ({', '.join(trigger_name)})",
            "certainty": "Confirmed",
            "class": "I"
        })
    
    # Carotid sinus syndrome
    if triggered_by_head_rotation_pressure and age_over_40:
        diagnoses.append({
            "diagnosis": "Carotid sinus syndrome",
            "certainty": "Probable - confirm with carotid sinus massage",
            "class": "IIa"
        })
    
    # Orthostatic hypotension
    if orthostatic_bp_drop:
        diagnoses.append({
            "diagnosis": "Orthostatic hypotension",
            "certainty": "Confirmed",
            "class": "I"
        })
    elif standing_at_onset and on_vasodilators:
        diagnoses.append({
            "diagnosis": "Orthostatic hypotension",
            "certainty": "Probable - perform orthostatic BP measurement",
            "class": "IIa"
        })
    
    # Cardiac syncope indicators
    cardiac_indicators = []
    if structural_heart_disease:
        cardiac_indicators.append("Structural heart disease")
    if abnormal_ecg:
        cardiac_indicators.append("Abnormal ECG")
    if exertional:
        cardiac_indicators.append("Exertional")
    if supine_at_onset:
        cardiac_indicators.append("Supine at onset")
    if no_prodrome:
        cardiac_indicators.append("No prodrome")
    if palpitations_prodrome:
        cardiac_indicators.append("Palpitations before syncope")
    
    if len(cardiac_indicators) >= 2:
        diagnoses.append({
            "diagnosis": "Cardiac syncope (arrhythmic or structural)",
            "certainty": "Suspected - requires cardiac workup",
            "class": "Requires investigation",
            "indicators": cardiac_indicators
        })
    
    # No clear diagnosis
    if len(diagnoses) == 0:
        diagnoses.append({
            "diagnosis": "Unexplained syncope",
            "certainty": "Requires further evaluation",
            "class": "N/A"
        })
    
    return {
        "likely_diagnoses": diagnoses,
        "primary_diagnosis": diagnoses[0] if diagnoses else None,
        "reflex_syncope_features": vasovagal_score,
        "cardiac_indicators": cardiac_indicators,
        "source": "ESC 2018 Syncope Guidelines"
    }


def diagnose_orthostatic_hypotension(
    supine_sbp: int,
    supine_dbp: int,
    standing_sbp_1min: int,
    standing_dbp_1min: int,
    standing_sbp_3min: Optional[int] = None,
    standing_dbp_3min: Optional[int] = None,
    standing_hr_1min: Optional[int] = None,
    standing_hr_3min: Optional[int] = None,
    supine_hr: Optional[int] = None,
    symptoms_on_standing: bool = False,
) -> Dict[str, Any]:
    """
    Diagnose orthostatic hypotension based on BP measurements.
    
    Args:
        supine_sbp/dbp: Supine blood pressure
        standing_sbp/dbp_1min: Standing BP at 1 minute
        standing_sbp/dbp_3min: Standing BP at 3 minutes (optional)
        standing_hr_1min/3min: Standing heart rate (optional)
        supine_hr: Supine heart rate (optional)
        symptoms_on_standing: Symptoms reproduced on standing
    
    Returns:
        OH diagnosis and classification
    """
    # Calculate drops
    sbp_drop_1min = supine_sbp - standing_sbp_1min
    dbp_drop_1min = supine_dbp - standing_dbp_1min
    
    if standing_sbp_3min is not None:
        sbp_drop_3min = supine_sbp - standing_sbp_3min
        dbp_drop_3min = supine_dbp - standing_dbp_3min
    else:
        sbp_drop_3min = None
        dbp_drop_3min = None
    
    # HR change for POTS assessment
    if standing_hr_1min and supine_hr:
        hr_increase = standing_hr_1min - supine_hr
    else:
        hr_increase = None
    
    # Classical OH criteria
    classical_oh = (
        sbp_drop_1min >= 20 or 
        dbp_drop_1min >= 10 or 
        standing_sbp_1min < 90 or
        (sbp_drop_3min is not None and (sbp_drop_3min >= 20 or dbp_drop_3min >= 10))
    )
    
    # Initial OH (within first 15-30 seconds - would need beat-to-beat monitoring)
    # Delayed OH (after 3 minutes)
    delayed_oh = False
    if sbp_drop_3min is not None and not classical_oh:
        if sbp_drop_3min >= 20 or dbp_drop_3min >= 10:
            delayed_oh = True
    
    # POTS assessment
    pots = False
    if hr_increase and hr_increase >= 30 and not classical_oh:
        # HR increase ≥30 bpm within 10 min of standing without OH
        if standing_hr_1min >= 120 or hr_increase >= 30:
            pots = True
    
    # Determine diagnosis
    if classical_oh:
        if symptoms_on_standing:
            diagnosis = "Classical orthostatic hypotension (confirmed)"
            diagnostic_class = "I"
        else:
            diagnosis = "Classical orthostatic hypotension (asymptomatic)"
            diagnostic_class = "IIa"
    elif delayed_oh:
        diagnosis = "Delayed orthostatic hypotension"
        diagnostic_class = "IIa"
    elif pots:
        diagnosis = "Postural orthostatic tachycardia syndrome (POTS)"
        diagnostic_class = "IIa"
    else:
        diagnosis = "No orthostatic hypotension"
        diagnostic_class = "N/A"
    
    return {
        "diagnosis": diagnosis,
        "diagnostic_class": diagnostic_class,
        "criteria_met": {
            "classical_oh": classical_oh,
            "delayed_oh": delayed_oh,
            "pots": pots
        },
        "measurements": {
            "supine_bp": f"{supine_sbp}/{supine_dbp}",
            "standing_1min_bp": f"{standing_sbp_1min}/{standing_dbp_1min}",
            "standing_3min_bp": f"{standing_sbp_3min}/{standing_dbp_3min}" if standing_sbp_3min else None,
            "sbp_drop_1min": sbp_drop_1min,
            "dbp_drop_1min": dbp_drop_1min,
            "hr_increase": hr_increase
        },
        "definitions": {
            "classical_oh": "SBP drop ≥20 mmHg OR DBP drop ≥10 mmHg OR SBP <90 mmHg within 3 min of standing",
            "delayed_oh": "OH criteria met after 3 minutes",
            "pots": "HR increase ≥30 bpm (or ≥120 bpm) within 10 min of standing without OH"
        },
        "symptoms_reproduced": symptoms_on_standing,
        "source": "ESC 2018 Syncope Guidelines"
    }


def assess_tilt_test_indication(
    suspected_reflex_syncope: bool = False,
    reflex_not_confirmed_by_history: bool = False,
    suspected_oh: bool = False,
    suspected_delayed_oh: bool = False,
    suspected_pots: bool = False,
    suspected_psychogenic: bool = False,
    differentiate_convulsive_syncope_epilepsy: bool = False,
    risk_category: str = "low",
) -> Dict[str, Any]:
    """
    Assess indication for tilt table testing.
    
    Args:
        suspected_reflex_syncope: Reflex syncope suspected
        reflex_not_confirmed_by_history: History alone not confirmatory
        suspected_oh: Orthostatic hypotension suspected
        suspected_delayed_oh: Delayed OH suspected
        suspected_pots: POTS suspected
        suspected_psychogenic: Psychogenic pseudosyncope suspected
        differentiate_convulsive_syncope_epilepsy: Need to differentiate from epilepsy
        risk_category: "low", "intermediate", "high"
    
    Returns:
        Tilt test indication and expected yield
    """
    indications = []
    
    if suspected_reflex_syncope and reflex_not_confirmed_by_history:
        indications.append("Suspected reflex syncope not confirmed by initial evaluation")
    
    if suspected_oh or suspected_delayed_oh:
        indications.append("Suspected orthostatic hypotension (especially delayed)")
    
    if suspected_pots:
        indications.append("Suspected POTS")
    
    if suspected_psychogenic:
        indications.append("Suspected psychogenic pseudosyncope")
    
    if differentiate_convulsive_syncope_epilepsy:
        indications.append("Differentiation of convulsive syncope from epilepsy")
    
    # Indication class
    if len(indications) > 0:
        indication_class = "IIa"
        recommended = True
    else:
        indication_class = "IIb"
        recommended = False
    
    # Expected diagnostic yield
    if suspected_reflex_syncope:
        expected_yield = "61-66% positivity rate in suspected reflex syncope"
    else:
        expected_yield = "Lower yield if no clinical suspicion"
    
    return {
        "tilt_test_indicated": recommended,
        "indication_class": indication_class,
        "indications": indications,
        "expected_yield": expected_yield,
        "protocols": [
            "Italian protocol: 20 min passive + nitroglycerin provocation",
            "Westminster protocol: 20 min passive + isoproterenol"
        ],
        "interpretation_notes": [
            "Positive cardioinhibitory response predicts asystole during spontaneous syncope",
            "Positive vasodepressor response does NOT exclude asystole during spontaneous syncope",
            "Negative test does NOT exclude reflex syncope",
            "Useful for patient education and reassurance"
        ],
        "source": "ESC 2018 Syncope Guidelines"
    }
