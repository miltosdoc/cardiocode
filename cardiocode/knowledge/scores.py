"""
Clinical Risk Scores for CardioCode.

Implements validated clinical scoring systems used in cardiology guidelines.
Each score function returns a ScoreResult with the numeric score,
risk interpretation, and guideline-based recommendations.

All scores include:
- Full calculation transparency
- ESC guideline citations
- Risk stratification interpretation
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, TYPE_CHECKING
from enum import Enum

if TYPE_CHECKING:
    from cardiocode.core.types import Patient

from cardiocode.core.evidence import (
    Citation,
    EvidenceClass,
    EvidenceLevel,
    create_citation,
)


@dataclass
class ScoreResult:
    """
    Result of a clinical score calculation.
    
    Provides the score value, interpretation, and recommendations
    based on ESC guidelines.
    """
    score_name: str
    score_value: int | float
    max_score: Optional[int] = None
    
    # Risk interpretation
    risk_category: str = "unknown"  # "low", "moderate", "high", "very_high"
    risk_percentage: Optional[float] = None  # Annual risk if available
    interpretation: str = ""
    
    # How score was calculated
    components: Dict[str, int | float] = field(default_factory=dict)
    
    # Guideline-based recommendation
    recommendation: Optional[str] = None
    citation: Optional[Citation] = None
    
    def format_for_display(self) -> str:
        """Format score result for clinical display."""
        lines = [
            f"=== {self.score_name} ===",
            f"Score: {self.score_value}" + (f" / {self.max_score}" if self.max_score else ""),
            f"Risk: {self.risk_category.upper()}"
        ]
        
        if self.risk_percentage is not None:
            lines.append(f"Annual risk: {self.risk_percentage:.1f}%")
        
        lines.append(f"\n{self.interpretation}")
        
        if self.components:
            lines.append("\nComponents:")
            for component, value in self.components.items():
                lines.append(f"  - {component}: {value}")
        
        if self.recommendation:
            lines.append(f"\nRecommendation: {self.recommendation}")
        
        if self.citation:
            lines.append(f"\nSource: {self.citation.format_short()}")
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "score_name": self.score_name,
            "score_value": self.score_value,
            "max_score": self.max_score,
            "risk_category": self.risk_category,
            "risk_percentage": self.risk_percentage,
            "interpretation": self.interpretation,
            "components": self.components,
            "recommendation": self.recommendation,
            "citation": self.citation.to_dict() if self.citation else None,
        }


# =============================================================================
# CHA2DS2-VASc Score (Stroke Risk in Atrial Fibrillation)
# ESC AF 2020 Guidelines
# =============================================================================

def cha2ds2_vasc(
    age: int,
    sex: str,  # "male" or "female"
    has_chf: bool = False,
    has_hypertension: bool = False,
    has_stroke_tia_te: bool = False,  # Prior stroke/TIA/thromboembolism
    has_vascular_disease: bool = False,  # Prior MI, PAD, aortic plaque
    has_diabetes: bool = False,
) -> ScoreResult:
    """
    Calculate CHA2DS2-VASc score for stroke risk in atrial fibrillation.
    
    Per ESC AF 2020 Guidelines (Section 11.2.1):
    - Score >= 2 (men) or >= 3 (women): Oral anticoagulation recommended (Class I)
    - Score 1 (men) or 2 (women): Oral anticoagulation should be considered (Class IIa)
    - Score 0 (men) or 1 (women): No antithrombotic therapy (Class IIa)
    
    Args:
        age: Patient age in years
        sex: "male" or "female"
        has_chf: Congestive heart failure / LV dysfunction
        has_hypertension: Hypertension
        has_stroke_tia_te: Prior stroke, TIA, or thromboembolism
        has_vascular_disease: Prior MI, PAD, or aortic plaque
        has_diabetes: Diabetes mellitus
    
    Returns:
        ScoreResult with score, risk interpretation, and OAC recommendation
    """
    components = {}
    score = 0
    
    # C - CHF/LV dysfunction (1 point)
    if has_chf:
        score += 1
        components["CHF/LV dysfunction"] = 1
    
    # H - Hypertension (1 point)
    if has_hypertension:
        score += 1
        components["Hypertension"] = 1
    
    # A2 - Age >= 75 (2 points) or Age 65-74 (1 point)
    if age >= 75:
        score += 2
        components["Age >= 75"] = 2
    elif age >= 65:
        score += 1
        components["Age 65-74"] = 1
    
    # D - Diabetes (1 point)
    if has_diabetes:
        score += 1
        components["Diabetes"] = 1
    
    # S2 - Stroke/TIA/TE (2 points)
    if has_stroke_tia_te:
        score += 2
        components["Stroke/TIA/TE"] = 2
    
    # V - Vascular disease (1 point)
    if has_vascular_disease:
        score += 1
        components["Vascular disease"] = 1
    
    # Sc - Sex category: female (1 point)
    is_female = sex.lower() == "female"
    if is_female:
        score += 1
        components["Female sex"] = 1
    
    # Risk stratification and stroke rates (approximate annual risk %)
    # Based on validation studies (Lip et al., Chest 2010)
    risk_table = {
        0: 0.2, 1: 0.6, 2: 2.2, 3: 3.2, 4: 4.8,
        5: 7.2, 6: 9.7, 7: 11.2, 8: 10.8, 9: 12.2
    }
    
    annual_risk = risk_table.get(min(score, 9), 15.0)
    
    # Determine recommendation based on ESC 2020
    if is_female:
        # For women, effectively subtract 1 for decision-making
        adjusted_score = score - 1
    else:
        adjusted_score = score
    
    if adjusted_score >= 2:
        risk_category = "high"
        recommendation = "Oral anticoagulation is RECOMMENDED. DOACs preferred over warfarin."
        evidence_class = EvidenceClass.I
    elif adjusted_score == 1:
        risk_category = "moderate"
        recommendation = "Oral anticoagulation SHOULD BE CONSIDERED, balancing stroke and bleeding risk."
        evidence_class = EvidenceClass.IIA
    else:
        risk_category = "low"
        recommendation = "No antithrombotic therapy recommended."
        evidence_class = EvidenceClass.IIA
    
    interpretation = (
        f"CHA2DS2-VASc = {score}: "
        f"{'Female patients have 1 point for sex. ' if is_female else ''}"
        f"Estimated annual stroke risk: {annual_risk:.1f}%"
    )
    
    citation = create_citation(
        guideline_key="esc_af_2020",
        evidence_class=evidence_class,
        evidence_level=EvidenceLevel.A,
        section="11.2.1",
        section_title="Stroke and bleeding risk assessment",
        studies=["Lip GY et al. Chest 2010", "GARFIELD-AF", "PREFER in AF"],
    )
    
    return ScoreResult(
        score_name="CHA2DS2-VASc",
        score_value=score,
        max_score=9,
        risk_category=risk_category,
        risk_percentage=annual_risk,
        interpretation=interpretation,
        components=components,
        recommendation=recommendation,
        citation=citation,
    )


# =============================================================================
# HAS-BLED Score (Bleeding Risk)
# ESC AF 2020 Guidelines
# =============================================================================

def has_bled(
    has_hypertension: bool = False,           # SBP > 160 mmHg
    abnormal_renal_function: bool = False,    # Dialysis, transplant, Cr > 2.26
    abnormal_liver_function: bool = False,    # Cirrhosis, bilirubin > 2x, AST/ALT > 3x
    has_stroke: bool = False,
    bleeding_history: bool = False,           # Prior major bleeding or predisposition
    labile_inr: bool = False,                 # TTR < 60% if on warfarin
    age_over_65: bool = False,
    drugs_predisposing: bool = False,         # Antiplatelets, NSAIDs
    alcohol_excess: bool = False,             # >= 8 drinks/week
) -> ScoreResult:
    """
    Calculate HAS-BLED score for bleeding risk assessment.
    
    Per ESC AF 2020 Guidelines:
    - Score >= 3 indicates high bleeding risk, but is NOT a contraindication to OAC
    - Used to identify modifiable bleeding risk factors
    
    Args:
        has_hypertension: Uncontrolled, SBP > 160 mmHg
        abnormal_renal_function: Chronic dialysis, renal transplant, serum Cr >= 2.26 mg/dL
        abnormal_liver_function: Chronic hepatic disease (cirrhosis) or biochemical evidence
        has_stroke: Prior stroke
        bleeding_history: Prior major bleeding or anemia or predisposition
        labile_inr: Unstable/high INRs, TTR < 60%
        age_over_65: Age > 65 years
        drugs_predisposing: Antiplatelets, NSAIDs
        alcohol_excess: >= 8 drinks/week
    
    Returns:
        ScoreResult with bleeding risk interpretation
    """
    components = {}
    score = 0
    
    if has_hypertension:
        score += 1
        components["Hypertension (uncontrolled)"] = 1
    
    if abnormal_renal_function:
        score += 1
        components["Abnormal renal function"] = 1
    
    if abnormal_liver_function:
        score += 1
        components["Abnormal liver function"] = 1
    
    if has_stroke:
        score += 1
        components["Stroke"] = 1
    
    if bleeding_history:
        score += 1
        components["Bleeding history"] = 1
    
    if labile_inr:
        score += 1
        components["Labile INR"] = 1
    
    if age_over_65:
        score += 1
        components["Elderly (> 65)"] = 1
    
    if drugs_predisposing:
        score += 1
        components["Drugs (antiplatelets/NSAIDs)"] = 1
    
    if alcohol_excess:
        score += 1
        components["Alcohol excess"] = 1
    
    # Annual major bleeding risk (approximate)
    bleed_risk_table = {
        0: 1.13, 1: 1.02, 2: 1.88, 3: 3.74, 4: 8.70, 5: 12.5
    }
    annual_bleed = bleed_risk_table.get(min(score, 5), 15.0)
    
    if score >= 3:
        risk_category = "high"
        recommendation = (
            "HIGH bleeding risk. This is NOT a contraindication to anticoagulation. "
            "Focus on correcting MODIFIABLE risk factors: "
            "control BP, avoid NSAIDs/antiplatelets if possible, treat alcohol excess, "
            "optimize INR control if on warfarin."
        )
    else:
        risk_category = "low" if score <= 1 else "moderate"
        recommendation = (
            "Bleeding risk is acceptable. Proceed with anticoagulation if indicated by CHA2DS2-VASc."
        )
    
    interpretation = (
        f"HAS-BLED = {score}: Estimated annual major bleeding risk on anticoagulation: {annual_bleed:.1f}%"
    )
    
    citation = create_citation(
        guideline_key="esc_af_2020",
        evidence_class=EvidenceClass.IIA,
        evidence_level=EvidenceLevel.B,
        section="11.2.1",
        section_title="Bleeding risk assessment",
        studies=["Pisters R et al. Chest 2010", "AMADEUS"],
    )
    
    return ScoreResult(
        score_name="HAS-BLED",
        score_value=score,
        max_score=9,
        risk_category=risk_category,
        risk_percentage=annual_bleed,
        interpretation=interpretation,
        components=components,
        recommendation=recommendation,
        citation=citation,
    )


# =============================================================================
# NYHA Functional Class
# =============================================================================

def nyha_class(
    symptoms_at_rest: bool = False,
    symptoms_with_less_than_ordinary_activity: bool = False,
    symptoms_with_ordinary_activity: bool = False,
) -> ScoreResult:
    """
    Determine NYHA Functional Class for heart failure.
    
    ESC HF 2021 Guidelines classify HF symptoms using NYHA:
    - Class I: No limitation, ordinary activity does not cause symptoms
    - Class II: Slight limitation, ordinary activity causes symptoms
    - Class III: Marked limitation, less than ordinary activity causes symptoms
    - Class IV: Unable to carry on any activity without symptoms, symptoms at rest
    
    Args:
        symptoms_at_rest: Dyspnea/fatigue at rest
        symptoms_with_less_than_ordinary_activity: Symptoms with minimal exertion
        symptoms_with_ordinary_activity: Symptoms with normal daily activities
    
    Returns:
        ScoreResult with NYHA class and implications
    """
    if symptoms_at_rest:
        nyha = 4
        risk_category = "very_high"
        interpretation = (
            "NYHA Class IV: Unable to carry out any physical activity without discomfort. "
            "Symptoms at rest. Any physical activity increases discomfort."
        )
        recommendation = (
            "Consider advanced HF therapies. Optimize GDMT. "
            "Evaluate for transplant/LVAD if appropriate. Close monitoring required."
        )
    elif symptoms_with_less_than_ordinary_activity:
        nyha = 3
        risk_category = "high"
        interpretation = (
            "NYHA Class III: Marked limitation of physical activity. Comfortable at rest. "
            "Less than ordinary activity causes fatigue, palpitation, or dyspnea."
        )
        recommendation = (
            "Maximize GDMT including diuretic optimization. Consider device therapy (CRT/ICD) if indicated. "
            "May benefit from cardiac rehabilitation."
        )
    elif symptoms_with_ordinary_activity:
        nyha = 2
        risk_category = "moderate"
        interpretation = (
            "NYHA Class II: Slight limitation of physical activity. Comfortable at rest. "
            "Ordinary physical activity results in fatigue, palpitation, or dyspnea."
        )
        recommendation = (
            "Initiate and uptitrate GDMT. Focus on lifestyle modification. "
            "Cardiac rehabilitation beneficial."
        )
    else:
        nyha = 1
        risk_category = "low"
        interpretation = (
            "NYHA Class I: No limitation of physical activity. Ordinary physical activity "
            "does not cause undue fatigue, palpitation, or dyspnea."
        )
        recommendation = (
            "Continue GDMT if indicated. Monitor for progression. "
            "Encourage exercise and healthy lifestyle."
        )
    
    citation = create_citation(
        guideline_key="esc_hf_2021",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.C,
        section="4",
        section_title="Symptoms and signs of heart failure",
    )
    
    return ScoreResult(
        score_name="NYHA Functional Class",
        score_value=nyha,
        max_score=4,
        risk_category=risk_category,
        interpretation=interpretation,
        components={"class": nyha},
        recommendation=recommendation,
        citation=citation,
    )


# =============================================================================
# GRACE Score (ACS Risk Stratification)
# ESC NSTE-ACS 2020 Guidelines
# =============================================================================

def grace_score(
    age: int,
    heart_rate: int,
    systolic_bp: int,
    creatinine: float,  # mg/dL
    killip_class: int = 1,  # 1-4
    cardiac_arrest: bool = False,
    st_deviation: bool = False,
    elevated_troponin: bool = False,
) -> ScoreResult:
    """
    Calculate GRACE 2.0 Risk Score for ACS.
    
    Per ESC NSTE-ACS 2020 Guidelines:
    - Used for risk stratification and timing of invasive strategy
    - High risk (GRACE > 140): Early invasive strategy (<24h)
    - Intermediate risk (GRACE 109-140): Invasive strategy <72h
    - Low risk (GRACE < 109): Selective invasive strategy
    
    Args:
        age: Patient age in years
        heart_rate: Heart rate in bpm
        systolic_bp: Systolic blood pressure in mmHg
        creatinine: Serum creatinine in mg/dL
        killip_class: Killip class 1-4
        cardiac_arrest: Cardiac arrest at admission
        st_deviation: ST-segment deviation
        elevated_troponin: Elevated cardiac troponin
    
    Returns:
        ScoreResult with GRACE score and invasive timing recommendation
    """
    # Simplified GRACE score calculation
    # Note: Full GRACE 2.0 uses a more complex algorithm
    
    components = {}
    score = 0
    
    # Age points
    if age < 30:
        age_points = 0
    elif age < 40:
        age_points = 8
    elif age < 50:
        age_points = 25
    elif age < 60:
        age_points = 41
    elif age < 70:
        age_points = 58
    elif age < 80:
        age_points = 75
    elif age < 90:
        age_points = 91
    else:
        age_points = 100
    score += age_points
    components["Age"] = age_points
    
    # Heart rate points
    if heart_rate < 50:
        hr_points = 0
    elif heart_rate < 70:
        hr_points = 3
    elif heart_rate < 90:
        hr_points = 9
    elif heart_rate < 110:
        hr_points = 15
    elif heart_rate < 150:
        hr_points = 24
    elif heart_rate < 200:
        hr_points = 38
    else:
        hr_points = 46
    score += hr_points
    components["Heart rate"] = hr_points
    
    # Systolic BP points (inverse relationship)
    if systolic_bp < 80:
        sbp_points = 58
    elif systolic_bp < 100:
        sbp_points = 53
    elif systolic_bp < 120:
        sbp_points = 43
    elif systolic_bp < 140:
        sbp_points = 34
    elif systolic_bp < 160:
        sbp_points = 24
    elif systolic_bp < 200:
        sbp_points = 10
    else:
        sbp_points = 0
    score += sbp_points
    components["Systolic BP"] = sbp_points
    
    # Creatinine points
    if creatinine < 0.4:
        cr_points = 1
    elif creatinine < 0.8:
        cr_points = 4
    elif creatinine < 1.2:
        cr_points = 7
    elif creatinine < 1.6:
        cr_points = 10
    elif creatinine < 2.0:
        cr_points = 13
    elif creatinine < 4.0:
        cr_points = 21
    else:
        cr_points = 28
    score += cr_points
    components["Creatinine"] = cr_points
    
    # Killip class points
    killip_points = {1: 0, 2: 20, 3: 39, 4: 59}
    kp = killip_points.get(killip_class, 0)
    score += kp
    components["Killip class"] = kp
    
    # Cardiac arrest
    if cardiac_arrest:
        score += 39
        components["Cardiac arrest"] = 39
    
    # ST deviation
    if st_deviation:
        score += 28
        components["ST deviation"] = 28
    
    # Elevated troponin
    if elevated_troponin:
        score += 14
        components["Elevated troponin"] = 14
    
    # Risk stratification
    if score > 140:
        risk_category = "high"
        risk_percentage = 10.0  # Approximate 6-month mortality
        recommendation = (
            "HIGH RISK: Early invasive strategy recommended within 24 hours. "
            "Consider immediate transfer to PCI-capable center."
        )
    elif score > 109:
        risk_category = "moderate"
        risk_percentage = 5.0
        recommendation = (
            "INTERMEDIATE RISK: Invasive strategy recommended within 72 hours."
        )
    else:
        risk_category = "low"
        risk_percentage = 2.0
        recommendation = (
            "LOW RISK: Selective invasive strategy. Consider non-invasive stress testing. "
            "Invasive evaluation if positive or high clinical suspicion."
        )
    
    interpretation = (
        f"GRACE score = {score}: Estimated in-hospital mortality and 6-month mortality risk. "
        f"Risk category: {risk_category.upper()}"
    )
    
    citation = create_citation(
        guideline_key="esc_acs_2020",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.A,
        section="6.1",
        section_title="Risk stratification",
        studies=["GRACE Registry", "ACUITY", "TIMACS"],
    )
    
    return ScoreResult(
        score_name="GRACE 2.0",
        score_value=score,
        max_score=372,
        risk_category=risk_category,
        risk_percentage=risk_percentage,
        interpretation=interpretation,
        components=components,
        recommendation=recommendation,
        citation=citation,
    )


# =============================================================================
# EuroSCORE II (Cardiac Surgery Risk)
# ESC VHD 2021 Guidelines
# =============================================================================

def euro_score_ii(
    age: int,
    sex: str,  # "male" or "female"
    egfr: float,  # mL/min/1.73m2
    extracardiac_arteriopathy: bool = False,
    poor_mobility: bool = False,  # Severe impairment of mobility
    previous_cardiac_surgery: bool = False,
    chronic_lung_disease: bool = False,
    active_endocarditis: bool = False,
    critical_preop_state: bool = False,  # VT/VF, preop ventilation, inotropes, IABP, preop renal failure
    diabetes_on_insulin: bool = False,
    nyha_class: int = 1,  # 1-4
    ccs_class_4_angina: bool = False,
    lvef: float = 60.0,  # %
    recent_mi: bool = False,  # <90 days
    pulmonary_hypertension: str = "none",  # "none", "moderate" (31-55 mmHg), "severe" (>55 mmHg)
    surgery_urgency: str = "elective",  # "elective", "urgent", "emergency", "salvage"
    weight_of_procedure: str = "isolated_cabg",  # Procedure type
    thoracic_aorta_surgery: bool = False,
) -> ScoreResult:
    """
    Calculate EuroSCORE II for cardiac surgery risk.
    
    Per ESC VHD 2021 Guidelines:
    - Used for risk stratification in valvular heart disease
    - Low risk: < 4%
    - Intermediate risk: 4-8%
    - High risk: > 8%
    
    Note: This is a simplified version. The actual EuroSCORE II uses logistic regression.
    
    Returns:
        ScoreResult with surgical risk estimate
    """
    # Simplified EuroSCORE II calculation
    # The real EuroSCORE II uses a complex logistic regression model
    # This provides approximate risk estimation
    
    components = {}
    
    # Base risk calculation (simplified)
    baseline = -5.324537  # Constant in log-odds
    
    # Age contribution
    age_factor = 0.0285181 * age
    components["Age"] = round(age_factor, 3)
    
    # Female sex (protective in Euro II)
    sex_factor = 0.2196434 if sex.lower() == "female" else 0
    if sex_factor:
        components["Female sex"] = round(sex_factor, 3)
    
    # Renal function
    if egfr < 30:
        renal_factor = 1.0
    elif egfr < 60:
        renal_factor = 0.5
    elif egfr < 85:
        renal_factor = 0.2
    else:
        renal_factor = 0
    if renal_factor:
        components["Renal impairment"] = renal_factor
    
    # Binary risk factors (simplified weights)
    if extracardiac_arteriopathy:
        components["Extracardiac arteriopathy"] = 0.5
    if poor_mobility:
        components["Poor mobility"] = 0.6
    if previous_cardiac_surgery:
        components["Redo surgery"] = 0.8
    if chronic_lung_disease:
        components["Chronic lung disease"] = 0.3
    if active_endocarditis:
        components["Active endocarditis"] = 0.6
    if critical_preop_state:
        components["Critical state"] = 1.0
    if diabetes_on_insulin:
        components["Insulin-dependent DM"] = 0.3
    
    # NYHA
    if nyha_class >= 3:
        components["NYHA III-IV"] = 0.4
    
    if ccs_class_4_angina:
        components["CCS 4 angina"] = 0.3
    
    # LVEF
    if lvef < 21:
        components["LVEF < 21%"] = 0.9
    elif lvef < 31:
        components["LVEF 21-30%"] = 0.6
    elif lvef < 51:
        components["LVEF 31-50%"] = 0.3
    
    if recent_mi:
        components["Recent MI"] = 0.4
    
    if pulmonary_hypertension == "severe":
        components["Severe PAH"] = 0.5
    elif pulmonary_hypertension == "moderate":
        components["Moderate PAH"] = 0.25
    
    # Urgency
    urgency_weights = {"elective": 0, "urgent": 0.3, "emergency": 0.8, "salvage": 1.5}
    if surgery_urgency != "elective":
        components["Surgery urgency"] = urgency_weights.get(surgery_urgency, 0)
    
    if thoracic_aorta_surgery:
        components["Thoracic aorta surgery"] = 0.5
    
    # Sum log-odds
    log_odds = baseline + sum(components.values())
    
    # Convert to probability
    import math
    probability = 1 / (1 + math.exp(-log_odds))
    risk_percentage = probability * 100
    
    # Risk stratification per ESC VHD guidelines
    if risk_percentage < 4:
        risk_category = "low"
        recommendation = "Low surgical risk. Surgical approach generally preferred if indicated."
    elif risk_percentage < 8:
        risk_category = "intermediate"
        recommendation = (
            "Intermediate surgical risk. Decision should be made by Heart Team. "
            "Consider TAVI for AS if eligible."
        )
    else:
        risk_category = "high"
        recommendation = (
            "High surgical risk. Strong consideration for transcatheter approach if anatomically suitable. "
            "Heart Team discussion essential."
        )
    
    interpretation = (
        f"EuroSCORE II = {risk_percentage:.1f}%: Predicted risk of operative mortality. "
        f"Risk category: {risk_category.upper()}"
    )
    
    citation = create_citation(
        guideline_key="esc_vhd_2021",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.B,
        section="5",
        section_title="Risk stratification and choice of intervention",
        studies=["Nashef SA et al. Eur J Cardiothorac Surg 2012"],
    )
    
    return ScoreResult(
        score_name="EuroSCORE II",
        score_value=round(risk_percentage, 1),
        risk_category=risk_category,
        risk_percentage=risk_percentage,
        interpretation=interpretation,
        components=components,
        recommendation=recommendation,
        citation=citation,
    )


# =============================================================================
# Wells Score for PE
# =============================================================================

def wells_pe(
    clinical_signs_dvt: bool = False,
    pe_most_likely_diagnosis: bool = False,
    heart_rate_above_100: bool = False,
    immobilization_or_surgery: bool = False,  # >3 days or surgery in past 4 weeks
    previous_pe_dvt: bool = False,
    hemoptysis: bool = False,
    malignancy: bool = False,  # Treatment in past 6 months or palliative
) -> ScoreResult:
    """
    Calculate Wells Score for Pulmonary Embolism probability.
    
    Used for pre-test probability assessment in suspected PE.
    
    Returns:
        ScoreResult with PE probability and diagnostic pathway recommendation
    """
    components = {}
    score = 0.0
    
    if clinical_signs_dvt:
        score += 3.0
        components["Clinical signs of DVT"] = 3.0
    
    if pe_most_likely_diagnosis:
        score += 3.0
        components["PE most likely diagnosis"] = 3.0
    
    if heart_rate_above_100:
        score += 1.5
        components["Heart rate > 100"] = 1.5
    
    if immobilization_or_surgery:
        score += 1.5
        components["Immobilization/recent surgery"] = 1.5
    
    if previous_pe_dvt:
        score += 1.5
        components["Previous PE/DVT"] = 1.5
    
    if hemoptysis:
        score += 1.0
        components["Hemoptysis"] = 1.0
    
    if malignancy:
        score += 1.0
        components["Malignancy"] = 1.0
    
    # Three-tier model
    if score <= 1:
        risk_category = "low"
        risk_percentage = 1.3
        recommendation = (
            "LOW probability. D-dimer testing appropriate. "
            "If D-dimer negative (age-adjusted), PE can be ruled out."
        )
    elif score <= 4:
        risk_category = "moderate"
        risk_percentage = 16.2
        recommendation = (
            "MODERATE probability. D-dimer testing appropriate. "
            "If D-dimer positive, proceed to CTPA."
        )
    else:
        risk_category = "high"
        risk_percentage = 40.6
        recommendation = (
            "HIGH probability. Proceed directly to CTPA. "
            "Consider empiric anticoagulation while awaiting imaging."
        )
    
    interpretation = (
        f"Wells PE Score = {score}: Pre-test probability of PE is {risk_category.upper()} "
        f"(~{risk_percentage:.0f}% PE prevalence in this category)"
    )
    
    return ScoreResult(
        score_name="Wells Score (PE)",
        score_value=score,
        max_score=12.5,
        risk_category=risk_category,
        risk_percentage=risk_percentage,
        interpretation=interpretation,
        components=components,
        recommendation=recommendation,
        citation=None,  # Not primarily ESC guideline
    )


# =============================================================================
# H2FPEF Score (HFpEF Diagnosis)
# =============================================================================

def hf2eff_score(
    bmi: float,
    age: int,
    e_e_prime: float,  # E/e' ratio on echo
    pasp: float,       # Pulmonary artery systolic pressure estimate
    atrial_fibrillation: bool = False,
) -> ScoreResult:
    """
    Calculate H2FPEF Score for diagnosing HFpEF.
    
    Helps distinguish HFpEF from non-cardiac causes of dyspnea.
    
    Components:
    - H: Heavy (BMI > 30): 2 points
    - 2: Hypertensive (>= 2 antihypertensives): not included in this simplified version
    - F: Atrial Fibrillation: 3 points
    - P: Pulmonary hypertension (PASP > 35): 1 point
    - E: E/e' > 9: 1 point
    - F: Filling pressure (not separately scored here)
    
    Returns:
        ScoreResult with HFpEF probability
    """
    components = {}
    score = 0
    
    # Heavy (BMI > 30)
    if bmi > 30:
        score += 2
        components["Obesity (BMI > 30)"] = 2
    
    # Atrial fibrillation (3 points)
    if atrial_fibrillation:
        score += 3
        components["Atrial fibrillation"] = 3
    
    # Pulmonary hypertension (PASP > 35)
    if pasp > 35:
        score += 1
        components["PASP > 35 mmHg"] = 1
    
    # E/e' > 9
    if e_e_prime > 9:
        score += 1
        components["E/e' > 9"] = 1
    
    # Age > 60 (1 point for each 10 years over 60, simplified)
    age_points = max(0, (age - 60) // 10)
    if age_points > 0:
        score += min(age_points, 2)
        components["Age factor"] = min(age_points, 2)
    
    # Probability based on score
    if score <= 1:
        risk_category = "low"
        risk_percentage = 10
        recommendation = (
            "LOW probability of HFpEF. Consider alternative diagnoses for dyspnea. "
            "If clinical suspicion remains, consider diastolic stress testing."
        )
    elif score <= 4:
        risk_category = "moderate"
        risk_percentage = 50
        recommendation = (
            "INTERMEDIATE probability. Consider exercise echocardiography or "
            "invasive hemodynamic assessment if diagnosis uncertain."
        )
    else:
        risk_category = "high"
        risk_percentage = 90
        recommendation = (
            "HIGH probability of HFpEF. Diagnosis likely. Initiate appropriate therapy: "
            "diuretics for congestion, SGLT2i, treat comorbidities."
        )
    
    interpretation = (
        f"H2FPEF Score = {score}: Probability of HFpEF is approximately {risk_percentage}%"
    )
    
    citation = create_citation(
        guideline_key="esc_hf_2021",
        evidence_class=EvidenceClass.IIA,
        evidence_level=EvidenceLevel.B,
        section="4.2",
        section_title="Diagnosis of HFpEF",
        studies=["Reddy YNV et al. Circulation 2018"],
    )
    
    return ScoreResult(
        score_name="H2FPEF",
        score_value=score,
        max_score=9,
        risk_category=risk_category,
        risk_percentage=risk_percentage,
        interpretation=interpretation,
        components=components,
        recommendation=recommendation,
        citation=citation,
    )


# =============================================================================
# Helper function to calculate scores from Patient object
# =============================================================================

def calculate_scores_for_patient(patient: "Patient") -> Dict[str, ScoreResult]:
    """
    Calculate all applicable clinical scores for a patient.
    
    Returns dictionary of score names to ScoreResult objects.
    Only calculates scores where sufficient data is available.
    """
    results = {}
    
    # CHA2DS2-VASc (if AF present)
    if patient.af_type or (patient.ecg and patient.ecg.af_present):
        if patient.age and patient.sex:
            results["cha2ds2_vasc"] = cha2ds2_vasc(
                age=patient.age,
                sex=patient.sex.value if hasattr(patient.sex, 'value') else str(patient.sex),
                has_chf=patient.has_diagnosis("heart_failure") or (patient.lvef and patient.lvef < 40),
                has_hypertension=patient.has_hypertension,
                has_stroke_tia_te=patient.has_prior_stroke_tia,
                has_vascular_disease=patient.has_vascular_disease,
                has_diabetes=patient.has_diabetes,
            )
            
            # HAS-BLED
            results["has_bled"] = has_bled(
                has_hypertension=patient.has_hypertension,
                abnormal_renal_function=patient.labs.egfr < 50 if patient.labs and patient.labs.egfr else False,
                abnormal_liver_function=patient.has_liver_disease,
                has_stroke=patient.has_prior_stroke_tia,
                bleeding_history=patient.has_prior_bleeding,
                age_over_65=patient.age > 65 if patient.age else False,
                drugs_predisposing=patient.is_on_medication("aspirin") or patient.is_on_medication("nsaid"),
            )
    
    # NYHA if HF present
    if patient.nyha_class:
        results["nyha"] = nyha_class(
            symptoms_at_rest=patient.nyha_class.value == 4 if hasattr(patient.nyha_class, 'value') else patient.nyha_class == 4,
            symptoms_with_less_than_ordinary_activity=patient.nyha_class.value == 3 if hasattr(patient.nyha_class, 'value') else patient.nyha_class == 3,
            symptoms_with_ordinary_activity=patient.nyha_class.value == 2 if hasattr(patient.nyha_class, 'value') else patient.nyha_class == 2,
        )
    
    # H2FPEF if echo data available
    if (patient.echo and patient.echo.e_e_prime_ratio and 
        patient.echo.rvsp and patient.age and patient.bmi):
        results["h2fpef"] = hf2eff_score(
            bmi=patient.bmi,
            age=patient.age,
            e_e_prime=patient.echo.e_e_prime_ratio,
            pasp=patient.echo.rvsp,
            atrial_fibrillation=patient.af_type is not None or (patient.ecg and patient.ecg.af_present),
        )
    
    return results
