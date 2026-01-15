"""
Syncope Evaluation and Management Pathways.

Based on 2018 ESC Syncope Guidelines.
"""

from typing import Dict, Any, Optional, List


def pathway_syncope_evaluation(
    age: int,
    history_features: Dict[str, bool],
    ecg_findings: Dict[str, bool],
    vital_signs: Dict[str, Any],
    initial_labs_done: bool = False,
) -> Dict[str, Any]:
    """
    Syncope evaluation pathway - initial assessment.
    
    Args:
        age: Patient age
        history_features: Dict with keys like "typical_vasovagal", "exertional", "palpitations_before", etc.
        ecg_findings: Dict with keys like "normal", "avb", "lbbb", "long_qt", etc.
        vital_signs: Dict with HR, BP, orthostatic measurements
        initial_labs_done: Whether initial labs completed
    
    Returns:
        Evaluation pathway and next steps
    """
    diagnosis_established = False
    probable_diagnosis = None
    further_testing = []
    
    # Step 1: Initial evaluation (history, exam, ECG, orthostatic BP)
    initial_evaluation = {
        "components": [
            "Detailed history of the episode and circumstances",
            "Witness account if available",
            "Physical examination including orthostatic BP",
            "12-lead ECG"
        ],
        "status": "Required for all patients"
    }
    
    # Check for diagnostic features in history
    if history_features.get("typical_vasovagal"):
        if history_features.get("triggered_by_pain_fear_standing"):
            if history_features.get("pallor_sweating_nausea_prodrome"):
                diagnosis_established = True
                probable_diagnosis = "Vasovagal syncope (reflex)"
    
    if history_features.get("situational_trigger"):
        diagnosis_established = True
        probable_diagnosis = "Situational syncope (reflex)"
    
    if vital_signs.get("orthostatic_drop"):
        diagnosis_established = True
        probable_diagnosis = "Orthostatic hypotension"
    
    # Check ECG for diagnostic findings
    if ecg_findings.get("complete_avb") or ecg_findings.get("mobitz_ii"):
        diagnosis_established = True
        probable_diagnosis = "Cardiac syncope - bradyarrhythmia"
        further_testing.append({
            "test": "Urgent cardiology consultation",
            "priority": "Immediate",
            "rationale": "High-grade AV block identified"
        })
    
    if ecg_findings.get("vt") or ecg_findings.get("rapid_svt"):
        diagnosis_established = True
        probable_diagnosis = "Cardiac syncope - tachyarrhythmia"
    
    if ecg_findings.get("long_qt") or ecg_findings.get("brugada") or ecg_findings.get("arvc_pattern"):
        probable_diagnosis = "Suspected inherited arrhythmia syndrome"
        further_testing.append({
            "test": "Genetic counseling and testing",
            "priority": "High",
            "rationale": "ECG pattern suggests channelopathy or cardiomyopathy"
        })
    
    # Step 2: Further testing based on initial evaluation
    if not diagnosis_established:
        # Suspected cardiac
        if history_features.get("exertional") or history_features.get("palpitations_before") or \
           history_features.get("supine") or ecg_findings.get("abnormal"):
            further_testing.append({
                "test": "Echocardiography",
                "priority": "High",
                "rationale": "Evaluate for structural heart disease"
            })
            further_testing.append({
                "test": "Continuous ECG monitoring",
                "priority": "High",
                "rationale": "Capture arrhythmia"
            })
        
        # Suspected reflex but not confirmed
        if history_features.get("possible_vasovagal"):
            further_testing.append({
                "test": "Tilt table test",
                "priority": "Medium",
                "class": "IIa",
                "rationale": "Confirm reflex mechanism"
            })
        
        # Unexplained with normal heart
        if not ecg_findings.get("abnormal") and age < 60:
            further_testing.append({
                "test": "Implantable loop recorder",
                "priority": "Medium",
                "class": "IIa",
                "rationale": "Recurrent unexplained syncope with normal initial evaluation"
            })
        
        # Suspected arrhythmic with structural heart disease
        if history_features.get("structural_heart_disease"):
            further_testing.append({
                "test": "Electrophysiology study",
                "priority": "High",
                "class": "I",
                "rationale": "Unexplained syncope with structural heart disease"
            })
    
    return {
        "initial_evaluation": initial_evaluation,
        "diagnosis_established": diagnosis_established,
        "probable_diagnosis": probable_diagnosis,
        "further_testing": further_testing,
        "diagnostic_yield_notes": [
            "Initial evaluation establishes diagnosis in ~50% of cases",
            "History is most important component",
            "Normal ECG has high negative predictive value for cardiac syncope"
        ],
        "source": "ESC 2018 Syncope Guidelines"
    }


def pathway_syncope_disposition(
    risk_category: str,
    diagnosis_established: bool = False,
    diagnosis: Optional[str] = None,
    ecg_findings: Optional[Dict[str, bool]] = None,
    structural_heart_disease: bool = False,
    significant_injury: bool = False,
    comorbidities: Optional[List[str]] = None,
    recurrent_episodes: bool = False,
) -> Dict[str, Any]:
    """
    Syncope disposition pathway - admit vs discharge.
    
    Args:
        risk_category: "high", "intermediate", "low"
        diagnosis_established: Whether diagnosis is established
        diagnosis: Established diagnosis if any
        ecg_findings: ECG abnormalities
        structural_heart_disease: Known structural heart disease
        significant_injury: Significant injury from syncope
        comorbidities: List of relevant comorbidities
        recurrent_episodes: Frequent recurrent episodes
    
    Returns:
        Disposition recommendation
    """
    if ecg_findings is None:
        ecg_findings = {}
    if comorbidities is None:
        comorbidities = []
    
    disposition = None
    rationale = []
    required_before_discharge = []
    outpatient_plan = []
    
    # High risk - usually requires admission
    if risk_category == "high":
        if structural_heart_disease or ecg_findings.get("significant_abnormality"):
            disposition = "Hospital admission"
            rationale.append("High-risk features with structural heart disease or ECG abnormality")
        elif significant_injury:
            disposition = "Hospital admission"
            rationale.append("Significant injury requiring inpatient management")
        else:
            disposition = "ED observation unit or hospital admission"
            rationale.append("High-risk features require monitoring and workup")
        
        required_before_discharge.extend([
            "Continuous ECG monitoring",
            "Echocardiography if structural heart disease suspected",
            "Cardiology consultation",
            "Identify cause or exclude high-risk arrhythmia"
        ])
    
    # Intermediate risk
    elif risk_category == "intermediate":
        if diagnosis_established and diagnosis in ["vasovagal", "situational", "orthostatic"]:
            disposition = "Discharge with outpatient follow-up"
            rationale.append("Reflex or orthostatic mechanism established")
        else:
            disposition = "ED observation or Syncope Unit"
            rationale.append("Intermediate risk - short observation with rapid workup")
        
        required_before_discharge.extend([
            "ECG reviewed and documented",
            "Orthostatic vitals checked",
            "Structural heart disease excluded or low suspicion"
        ])
    
    # Low risk
    else:
        if diagnosis_established:
            disposition = "Discharge home"
            rationale.append("Low risk with established benign diagnosis")
        else:
            disposition = "Discharge with outpatient evaluation"
            rationale.append("Low risk - can be evaluated as outpatient")
        
        required_before_discharge.extend([
            "Normal or unchanged ECG",
            "No orthostatic hypotension (or explained and managed)",
            "Patient education provided"
        ])
    
    # Outpatient plan for discharged patients
    if "Discharge" in disposition:
        if diagnosis in ["vasovagal", "situational"]:
            outpatient_plan = [
                "Education on prodrome recognition and counterpressure maneuvers",
                "Adequate hydration and salt intake",
                "Avoid triggers",
                "Follow-up with PCP or cardiology if recurrent"
            ]
        elif diagnosis == "orthostatic":
            outpatient_plan = [
                "Review medications for causative agents",
                "Compression stockings",
                "Increase fluid and salt intake",
                "Rise slowly from sitting/lying",
                "Consider fludrocortisone or midodrine if refractory"
            ]
        else:
            outpatient_plan = [
                "Outpatient cardiology referral",
                "Event monitor or loop recorder consideration",
                "Driving restrictions per local guidelines",
                "Return if recurrent or high-risk symptoms"
            ]
    
    # Special considerations
    special_considerations = []
    if recurrent_episodes:
        special_considerations.append("Recurrent syncope - consider implantable loop recorder")
    if "pacemaker" in comorbidities or "icd" in comorbidities:
        special_considerations.append("Device interrogation required")
    if any(ecg_findings.get(finding) for finding in ["long_qt", "brugada", "arvc_pattern"]):
        special_considerations.append("Suspected inherited arrhythmia - genetics referral")
    
    return {
        "disposition": disposition,
        "rationale": rationale,
        "required_before_discharge": required_before_discharge,
        "outpatient_plan": outpatient_plan,
        "special_considerations": special_considerations,
        "driving_advice": "Advise on driving restrictions per local regulations - typically no driving until cause established/treated",
        "return_precautions": [
            "Recurrent syncope",
            "Chest pain or palpitations",
            "Dyspnea",
            "New neurological symptoms"
        ],
        "source": "ESC 2018 Syncope Guidelines"
    }
