"""
Heart Failure Monitoring and Follow-up - ESC 2021 Guidelines.

Implements monitoring recommendations from ESC HF 2021:
- Follow-up intervals
- Parameters to monitor
- Titration guidance
"""

from __future__ import annotations
from typing import Optional, List, Dict, TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from cardiocode.core.types import Patient

from cardiocode.core.recommendation import (
    Recommendation,
    RecommendationSet,
    RecommendationCategory,
    Urgency,
    guideline_recommendation,
)
from cardiocode.core.evidence import EvidenceClass, EvidenceLevel


@dataclass
class FollowUpSchedule:
    """Recommended follow-up schedule for HF patient."""
    next_visit_weeks: int
    visit_type: str  # "clinic", "phone", "remote_monitoring"
    parameters_to_check: List[str]
    actions_to_consider: List[str]
    rationale: str


def get_followup_schedule(patient: "Patient", recent_event: Optional[str] = None) -> FollowUpSchedule:
    """
    Determine appropriate follow-up schedule.
    
    Per ESC 2021 recommendations on HF follow-up.
    
    Args:
        patient: Patient object
        recent_event: Recent clinical event ("hospitalization", "med_change", "stable")
    
    Returns:
        FollowUpSchedule with timing and parameters
    """
    parameters = ["Symptoms/NYHA class", "Weight", "BP", "HR"]
    
    if recent_event == "hospitalization":
        # Post-discharge follow-up
        return FollowUpSchedule(
            next_visit_weeks=1,
            visit_type="clinic",
            parameters_to_check=parameters + [
                "Renal function (Cr, BUN)",
                "Electrolytes (K+, Na+)",
                "Volume status assessment",
                "Medication reconciliation",
            ],
            actions_to_consider=[
                "Uptitrate GDMT if tolerated",
                "Adjust diuretics based on volume status",
                "Ensure follow-up cardiology within 2 weeks",
                "Consider cardiac rehabilitation referral",
            ],
            rationale="Early post-discharge follow-up reduces readmission risk. ESC recommends visit within 1-2 weeks.",
        )
    
    elif recent_event == "med_change":
        # Recent medication initiation or dose change
        return FollowUpSchedule(
            next_visit_weeks=2,
            visit_type="clinic",
            parameters_to_check=parameters + [
                "Renal function",
                "Electrolytes (especially K+ if on ACEi/ARB/ARNI/MRA)",
                "Tolerance of new medication",
                "Side effects assessment",
            ],
            actions_to_consider=[
                "Assess tolerance of dose change",
                "Check labs 1-2 weeks after ACEi/ARB/ARNI/MRA change",
                "Continue uptitration if tolerated",
            ],
            rationale="Monitor for adverse effects after medication changes. Recheck labs 1-2 weeks after RAAS modulator changes.",
        )
    
    else:
        # Stable patient on optimized therapy
        nyha = patient.nyha_class.value if patient.nyha_class else 2
        
        if nyha <= 2:
            interval = 12  # NYHA I-II: every 3 months reasonable
        else:
            interval = 4  # NYHA III-IV: more frequent
        
        return FollowUpSchedule(
            next_visit_weeks=interval,
            visit_type="clinic",
            parameters_to_check=parameters + [
                "Labs (renal function, electrolytes, CBC) every 6-12 months",
                "Natriuretic peptides if symptoms change",
                "Device interrogation if applicable",
            ],
            actions_to_consider=[
                "Review and optimize GDMT",
                "Assess need for additional therapies",
                "Annual flu vaccine",
                "Screen for comorbidities (depression, sleep apnea, iron deficiency)",
            ],
            rationale=f"Stable NYHA {nyha}: follow-up every {interval} weeks appropriate.",
        )


def get_monitoring_parameters(patient: "Patient") -> RecommendationSet:
    """
    Get recommended monitoring parameters for HF patient.
    
    Per ESC 2021 Section 14: Organization of care.
    """
    rec_set = RecommendationSet(
        title="HF Monitoring Recommendations",
        description="Parameters and frequency for monitoring chronic HF",
        primary_guideline="ESC HF 2021",
    )
    
    # Weight monitoring
    rec_set.add(guideline_recommendation(
        action="Daily weight monitoring. Contact provider if weight increases > 2 kg in 3 days.",
        guideline_key="esc_hf_2021",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.C,
        category=RecommendationCategory.MONITORING,
        section="14",
        rationale="Early detection of fluid retention allows timely intervention",
    ))
    
    # Lab monitoring
    rec_set.add(guideline_recommendation(
        action="Check renal function and electrolytes 1-2 weeks after ACEi/ARB/ARNI/MRA initiation or dose change",
        guideline_key="esc_hf_2021",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.C,
        category=RecommendationCategory.MONITORING,
        section="11",
    ))
    
    # Natriuretic peptides
    rec_set.add(guideline_recommendation(
        action="Natriuretic peptide measurement at baseline. Repeat measurement may guide intensification of therapy.",
        guideline_key="esc_hf_2021",
        evidence_class=EvidenceClass.IIA,
        evidence_level=EvidenceLevel.B,
        category=RecommendationCategory.MONITORING,
        section="4.1",
        studies=["GUIDE-IT (neutral)", "PRIMA II"],
    ))
    
    # Iron studies
    rec_set.add(guideline_recommendation(
        action="Screen for iron deficiency (ferritin, TSAT) periodically. IV iron if ferritin < 100 or ferritin 100-299 with TSAT < 20%.",
        guideline_key="esc_hf_2021",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.A,
        category=RecommendationCategory.MONITORING,
        section="11.5",
        studies=["FAIR-HF", "AFFIRM-AHF"],
    ))
    
    # Echo
    rec_set.add(guideline_recommendation(
        action="Repeat echocardiography if clinical status changes or to evaluate response to therapy (e.g., 3-6 months after GDMT optimization)",
        guideline_key="esc_hf_2021",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.C,
        category=RecommendationCategory.DIAGNOSTIC,
        section="4.2",
    ))
    
    return rec_set


# Target doses for uptitration reference
TARGET_DOSES: Dict[str, Dict[str, str]] = {
    "acei": {
        "enalapril": "10-20 mg BID",
        "lisinopril": "20-35 mg daily",
        "ramipril": "5 mg BID or 10 mg daily",
        "captopril": "50 mg TID",
    },
    "arb": {
        "candesartan": "32 mg daily",
        "losartan": "150 mg daily",
        "valsartan": "160 mg BID",
    },
    "arni": {
        "sacubitril/valsartan": "97/103 mg BID",
    },
    "beta_blocker": {
        "bisoprolol": "10 mg daily",
        "carvedilol": "25 mg BID (50 mg BID if > 85 kg)",
        "metoprolol_succinate": "200 mg daily",
        "nebivolol": "10 mg daily",
    },
    "mra": {
        "spironolactone": "25-50 mg daily",
        "eplerenone": "50 mg daily",
    },
    "sglt2i": {
        "dapagliflozin": "10 mg daily",
        "empagliflozin": "10 mg daily",
    },
}


def get_uptitration_guidance(drug_class: str, current_dose: Optional[str] = None) -> str:
    """
    Get uptitration guidance for a specific drug class.
    
    Args:
        drug_class: Drug class (e.g., "beta_blocker", "acei")
        current_dose: Current dose if known
    
    Returns:
        String with uptitration guidance
    """
    if drug_class not in TARGET_DOSES:
        return f"No specific uptitration guidance for {drug_class}"
    
    targets = TARGET_DOSES[drug_class]
    target_str = ", ".join(f"{drug}: {dose}" for drug, dose in targets.items())
    
    guidance = [
        f"Target doses for {drug_class}:",
        target_str,
        "",
        "Uptitration guidance:",
        "- Double dose every 2-4 weeks if tolerated",
        "- Monitor BP, HR, renal function, and electrolytes",
        "- Some benefit even at sub-target doses if target not tolerated",
    ]
    
    return "\n".join(guidance)
