"""
Heart Failure Treatment - ESC 2021 Guidelines.

Implements treatment algorithms from ESC HF 2021:
- HFrEF pharmacological treatment (Section 11)
- HFmrEF treatment recommendations
- HFpEF treatment recommendations
- Diuretic therapy
- GDMT optimization

Key trials referenced:
- ACEi: CONSENSUS, SOLVD-Treatment, ATLAS
- ARB: Val-HeFT, CHARM-Alternative
- ARNI: PARADIGM-HF
- Beta-blockers: CIBIS-II, COPERNICUS, MERIT-HF, SENIORS
- MRA: RALES, EMPHASIS-HF
- SGLT2i: DAPA-HF, EMPEROR-Reduced
- Ivabradine: SHIFT
- Hydralazine-nitrate: A-HeFT
"""

from __future__ import annotations
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from cardiocode.core.types import Patient

from cardiocode.core.recommendation import (
    Recommendation,
    RecommendationSet,
    RecommendationCategory,
    Urgency,
    guideline_recommendation,
    synthesis_recommendation,
)
from cardiocode.core.evidence import EvidenceClass, EvidenceLevel
from cardiocode.guidelines.heart_failure.diagnosis import classify_hf_phenotype, HFPhenotype


def get_hfref_treatment(patient: "Patient") -> RecommendationSet:
    """
    Get treatment recommendations for HFrEF (LVEF <= 40%).
    
    Per ESC 2021 Section 11.1: Pharmacological treatment of HFrEF
    
    Core Guideline-Directed Medical Therapy (GDMT):
    1. ACEi/ARNI (Class I, Level A)
    2. Beta-blocker (Class I, Level A)
    3. MRA (Class I, Level A)
    4. SGLT2i (Class I, Level A) - NEW in 2021
    
    Plus diuretics for congestion (Class I, Level C)
    
    Args:
        patient: Patient object with clinical data
    
    Returns:
        RecommendationSet with all applicable recommendations
    """
    rec_set = RecommendationSet(
        title="HFrEF Treatment Recommendations",
        description="ESC 2021 Guideline-Directed Medical Therapy for HFrEF (LVEF <= 40%)",
        primary_guideline="ESC HF 2021",
        patient_context=f"LVEF {patient.lvef}%, NYHA {patient.nyha_class.value if patient.nyha_class else 'unknown'}",
    )
    
    # =========================================================================
    # PILLAR 1: ACEi or ARNI
    # =========================================================================
    
    # Check if already on ACEi/ARB/ARNI
    on_acei = patient.is_on_medication("acei")
    on_arb = patient.is_on_medication("arb")
    on_arni = patient.is_on_medication("arni")
    
    acei_contraindication = patient.contraindication("acei")
    
    if not on_arni and not on_acei and not on_arb:
        if not acei_contraindication:
            # ARNI preferred if tolerable
            rec_set.add(guideline_recommendation(
                action="Start ARNI (sacubitril/valsartan) as first-line if tolerable, otherwise ACEi",
                guideline_key="esc_hf_2021",
                evidence_class=EvidenceClass.I,
                evidence_level=EvidenceLevel.A if on_acei else EvidenceLevel.B,
                category=RecommendationCategory.PHARMACOTHERAPY,
                page=3033,
                section="11.1.1",
                studies=["PARADIGM-HF", "PIONEER-HF"],
                rationale="ARNI reduces mortality and HF hospitalizations vs ACEi. Can be started de novo in hospitalized patients.",
                monitoring="Monitor BP, K+, creatinine within 1-2 weeks of initiation",
                conditions=["SBP >= 100 mmHg", "eGFR >= 30 mL/min", "K+ < 5.4 mEq/L"],
                contraindications=["History of angioedema", "Pregnancy", "Bilateral renal artery stenosis"],
            ))
        else:
            rec_set.add(guideline_recommendation(
                action=f"ACEi/ARNI contraindicated: {acei_contraindication}. Start ARB (candesartan or valsartan).",
                guideline_key="esc_hf_2021",
                evidence_class=EvidenceClass.I,
                evidence_level=EvidenceLevel.A,
                category=RecommendationCategory.PHARMACOTHERAPY,
                section="11.1.1",
                studies=["CHARM-Alternative", "Val-HeFT"],
            ))
    
    elif on_acei and not on_arni:
        # Already on ACEi - consider switch to ARNI
        rec_set.add(guideline_recommendation(
            action="Consider switching from ACEi to ARNI (sacubitril/valsartan) for additional mortality benefit",
            guideline_key="esc_hf_2021",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PHARMACOTHERAPY,
            section="11.1.1",
            studies=["PARADIGM-HF"],
            rationale="ARNI superior to ACEi in PARADIGM-HF. Requires 36h washout from ACEi.",
            conditions=["Patient tolerating ACEi", "No history of angioedema"],
        ))
    
    # =========================================================================
    # PILLAR 2: Beta-Blocker
    # =========================================================================
    
    on_bb = patient.is_on_medication("beta_blocker")
    bb_contraindication = patient.contraindication("beta_blocker")
    
    if not on_bb:
        if not bb_contraindication:
            rec_set.add(guideline_recommendation(
                action="Start evidence-based beta-blocker: bisoprolol, carvedilol, metoprolol succinate, or nebivolol",
                guideline_key="esc_hf_2021",
                evidence_class=EvidenceClass.I,
                evidence_level=EvidenceLevel.A,
                category=RecommendationCategory.PHARMACOTHERAPY,
                page=3034,
                section="11.1.2",
                studies=["CIBIS-II", "COPERNICUS", "MERIT-HF", "SENIORS"],
                rationale="Beta-blockers reduce mortality by ~30% in HFrEF",
                monitoring="Monitor HR and BP. Uptitrate every 2-4 weeks to target or maximally tolerated dose.",
                conditions=["Clinically stable", "Not in acute decompensation"],
                contraindications=["Second/third degree AV block without pacemaker", "Sick sinus syndrome", "HR < 50 bpm"],
            ))
        else:
            rec_set.add(guideline_recommendation(
                action=f"Beta-blocker contraindicated: {bb_contraindication}",
                guideline_key="esc_hf_2021",
                evidence_class=EvidenceClass.I,
                evidence_level=EvidenceLevel.A,
                category=RecommendationCategory.CONTRAINDICATION,
                section="11.1.2",
            ))
    else:
        # Check if at target dose
        rec_set.add(guideline_recommendation(
            action="Ensure beta-blocker is uptitrated to target or maximally tolerated dose",
            guideline_key="esc_hf_2021",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.A,
            category=RecommendationCategory.PHARMACOTHERAPY,
            section="11.1.2",
            rationale="Mortality benefit is dose-dependent. Target doses: bisoprolol 10mg, carvedilol 25mg BID, metoprolol succinate 200mg",
        ))
    
    # =========================================================================
    # PILLAR 3: MRA (Mineralocorticoid Receptor Antagonist)
    # =========================================================================
    
    on_mra = patient.is_on_medication("mra")
    mra_contraindication = patient.contraindication("mra")
    
    if not on_mra:
        if not mra_contraindication:
            rec_set.add(guideline_recommendation(
                action="Start MRA: spironolactone 25-50mg or eplerenone 25-50mg daily",
                guideline_key="esc_hf_2021",
                evidence_class=EvidenceClass.I,
                evidence_level=EvidenceLevel.A,
                category=RecommendationCategory.PHARMACOTHERAPY,
                page=3035,
                section="11.1.3",
                studies=["RALES", "EMPHASIS-HF"],
                rationale="MRA reduces mortality and HF hospitalization in symptomatic HFrEF",
                monitoring="Check K+ and creatinine within 1 week, then at 1, 2, 3 months, then every 4 months",
                conditions=["eGFR >= 30 mL/min", "K+ < 5.0 mEq/L"],
                contraindications=["eGFR < 30 mL/min", "K+ > 5.0 mEq/L", "Severe hepatic impairment"],
            ))
        else:
            rec_set.add(guideline_recommendation(
                action=f"MRA relatively contraindicated: {mra_contraindication}. Consider low-dose with close monitoring if benefit outweighs risk.",
                guideline_key="esc_hf_2021",
                evidence_class=EvidenceClass.I,
                evidence_level=EvidenceLevel.A,
                category=RecommendationCategory.PHARMACOTHERAPY,
                section="11.1.3",
            ))
    
    # =========================================================================
    # PILLAR 4: SGLT2 Inhibitor (NEW in ESC 2021)
    # =========================================================================
    
    on_sglt2i = patient.is_on_medication("sglt2i")
    sglt2i_contraindication = patient.contraindication("sglt2i")
    
    if not on_sglt2i:
        if not sglt2i_contraindication:
            rec_set.add(guideline_recommendation(
                action="Start SGLT2 inhibitor: dapagliflozin 10mg or empagliflozin 10mg daily",
                guideline_key="esc_hf_2021",
                evidence_class=EvidenceClass.I,
                evidence_level=EvidenceLevel.A,
                category=RecommendationCategory.PHARMACOTHERAPY,
                page=3036,
                section="11.1.4",
                studies=["DAPA-HF", "EMPEROR-Reduced"],
                rationale="SGLT2i reduce CV death and HF hospitalization regardless of diabetes status. NNT ~21 over 18 months.",
                conditions=["eGFR >= 20 mL/min (check latest labeling)"],
                contraindications=["Type 1 diabetes", "History of DKA"],
            ))
        else:
            rec_set.add(guideline_recommendation(
                action=f"SGLT2i contraindicated: {sglt2i_contraindication}",
                guideline_key="esc_hf_2021",
                evidence_class=EvidenceClass.I,
                evidence_level=EvidenceLevel.A,
                category=RecommendationCategory.CONTRAINDICATION,
                section="11.1.4",
            ))
    
    # =========================================================================
    # ADDITIONAL THERAPIES
    # =========================================================================
    
    # Diuretics for congestion
    if patient.nyha_class and patient.nyha_class.value >= 2:
        rec_set.add(guideline_recommendation(
            action="Loop diuretic (furosemide, bumetanide, or torsemide) for signs/symptoms of congestion",
            guideline_key="esc_hf_2021",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.PHARMACOTHERAPY,
            section="11.4",
            rationale="Diuretics relieve congestion but should be used at lowest effective dose",
            monitoring="Monitor weight, symptoms, renal function, electrolytes",
        ))
    
    # Ivabradine for HR >= 70 despite beta-blocker
    if patient.vitals and patient.vitals.heart_rate:
        if patient.vitals.heart_rate >= 70 and on_bb:
            rec_set.add(guideline_recommendation(
                action="Consider ivabradine if HR >= 70 bpm despite maximally tolerated beta-blocker dose",
                guideline_key="esc_hf_2021",
                evidence_class=EvidenceClass.IIA,
                evidence_level=EvidenceLevel.B,
                category=RecommendationCategory.PHARMACOTHERAPY,
                section="11.1.6",
                studies=["SHIFT"],
                conditions=["Sinus rhythm", "Beta-blocker at max tolerated dose", "LVEF <= 35%"],
            ))
    
    # Hydralazine + nitrate for Black patients or ACEi-intolerant
    if acei_contraindication:
        rec_set.add(guideline_recommendation(
            action="Consider hydralazine/isosorbide dinitrate combination if ACEi/ARB/ARNI not tolerated",
            guideline_key="esc_hf_2021",
            evidence_class=EvidenceClass.IIB,
            evidence_level=EvidenceLevel.B,
            category=RecommendationCategory.PHARMACOTHERAPY,
            section="11.1.7",
            studies=["V-HeFT I", "V-HeFT II"],
        ))
    
    return rec_set


def get_hfmref_treatment(patient: "Patient") -> RecommendationSet:
    """
    Get treatment recommendations for HFmrEF (LVEF 41-49%).
    
    Per ESC 2021 Section 11.2: Pharmacological treatment of HFmrEF
    
    ESC 2021 recognizes HFmrEF as a distinct entity but notes evidence is less robust.
    Treatment recommendations largely extrapolated from HFrEF trials.
    
    Args:
        patient: Patient object with clinical data
    
    Returns:
        RecommendationSet with recommendations
    """
    rec_set = RecommendationSet(
        title="HFmrEF Treatment Recommendations",
        description="ESC 2021 Treatment for HFmrEF (LVEF 41-49%). Evidence less robust than HFrEF.",
        primary_guideline="ESC HF 2021",
        patient_context=f"LVEF {patient.lvef}%",
    )
    
    # Diuretics for congestion (Class I)
    rec_set.add(guideline_recommendation(
        action="Diuretics for signs/symptoms of congestion",
        guideline_key="esc_hf_2021",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.C,
        category=RecommendationCategory.PHARMACOTHERAPY,
        section="11.2",
    ))
    
    # ACEi/ARB/ARNI (Class IIb)
    rec_set.add(guideline_recommendation(
        action="ACEi, ARB, or ARNI may be considered to reduce HF hospitalization and death",
        guideline_key="esc_hf_2021",
        evidence_class=EvidenceClass.IIB,
        evidence_level=EvidenceLevel.C,
        category=RecommendationCategory.PHARMACOTHERAPY,
        section="11.2",
        rationale="Subgroup analyses suggest benefit, but no dedicated HFmrEF trials",
    ))
    
    # Beta-blocker (Class IIb)
    rec_set.add(guideline_recommendation(
        action="Beta-blocker may be considered",
        guideline_key="esc_hf_2021",
        evidence_class=EvidenceClass.IIB,
        evidence_level=EvidenceLevel.C,
        category=RecommendationCategory.PHARMACOTHERAPY,
        section="11.2",
    ))
    
    # MRA (Class IIb)
    rec_set.add(guideline_recommendation(
        action="MRA may be considered",
        guideline_key="esc_hf_2021",
        evidence_class=EvidenceClass.IIB,
        evidence_level=EvidenceLevel.C,
        category=RecommendationCategory.PHARMACOTHERAPY,
        section="11.2",
        studies=["TOPCAT (subgroup)"],
    ))
    
    # SGLT2i - Stronger recommendation based on DELIVER/EMPEROR-Preserved
    rec_set.add(guideline_recommendation(
        action="SGLT2 inhibitor (dapagliflozin or empagliflozin) to reduce HF hospitalization and CV death",
        guideline_key="esc_hf_2021",
        evidence_class=EvidenceClass.IIA,
        evidence_level=EvidenceLevel.B,
        category=RecommendationCategory.PHARMACOTHERAPY,
        section="11.2",
        studies=["EMPEROR-Preserved (subgroup)", "DELIVER (subgroup)"],
        rationale="SGLT2i showed benefit across EF spectrum including HFmrEF",
    ))
    
    return rec_set


def get_hfpef_treatment(patient: "Patient") -> RecommendationSet:
    """
    Get treatment recommendations for HFpEF (LVEF >= 50%).
    
    Per ESC 2021 Section 11.3: Pharmacological treatment of HFpEF
    
    No treatment has been shown to reduce mortality in HFpEF.
    Treatment is focused on:
    1. Diuretics for congestion
    2. Treatment of underlying causes and comorbidities
    3. SGLT2i (based on EMPEROR-Preserved)
    
    Args:
        patient: Patient object with clinical data
    
    Returns:
        RecommendationSet with recommendations
    """
    rec_set = RecommendationSet(
        title="HFpEF Treatment Recommendations",
        description="ESC 2021 Treatment for HFpEF (LVEF >= 50%). Focus on congestion, comorbidities, and underlying causes.",
        primary_guideline="ESC HF 2021",
        patient_context=f"LVEF {patient.lvef}%",
    )
    
    # Diuretics (Class I)
    rec_set.add(guideline_recommendation(
        action="Diuretics to relieve signs/symptoms of congestion",
        guideline_key="esc_hf_2021",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.C,
        category=RecommendationCategory.PHARMACOTHERAPY,
        section="11.3",
    ))
    
    # Screen for and treat underlying causes (Class I)
    rec_set.add(guideline_recommendation(
        action="Screen for and treat underlying causes and comorbidities (HTN, CAD, AF, DM, obesity, etc.)",
        guideline_key="esc_hf_2021",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.C,
        category=RecommendationCategory.MONITORING,
        section="11.3",
    ))
    
    # SGLT2i - Now has dedicated evidence from EMPEROR-Preserved and DELIVER
    rec_set.add(guideline_recommendation(
        action="SGLT2 inhibitor (empagliflozin or dapagliflozin) to reduce HF hospitalization",
        guideline_key="esc_hf_2021",
        evidence_class=EvidenceClass.IIA,
        evidence_level=EvidenceLevel.B,
        category=RecommendationCategory.PHARMACOTHERAPY,
        section="11.3",
        studies=["EMPEROR-Preserved", "DELIVER"],
        rationale="SGLT2i reduce HF hospitalization in HFpEF. First therapy with proven benefit in this population.",
    ))
    
    # AF management if present
    if patient.af_type or (patient.ecg and patient.ecg.af_present):
        rec_set.add(guideline_recommendation(
            action="Anticoagulation for AF per stroke risk assessment. Rate/rhythm control per AF guidelines.",
            guideline_key="esc_hf_2021",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.A,
            category=RecommendationCategory.PHARMACOTHERAPY,
            section="11.3",
        ))
    
    return rec_set


def get_diuretic_recommendations(patient: "Patient") -> RecommendationSet:
    """
    Get diuretic recommendations for heart failure.
    
    Per ESC 2021 Section 11.4: Diuretics
    """
    rec_set = RecommendationSet(
        title="Diuretic Therapy Recommendations",
        description="Loop diuretic management for HF",
        primary_guideline="ESC HF 2021",
    )
    
    # Loop diuretics for congestion
    rec_set.add(guideline_recommendation(
        action="Loop diuretics are recommended for HF patients with signs/symptoms of congestion to improve symptoms and exercise capacity",
        guideline_key="esc_hf_2021",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.C,
        category=RecommendationCategory.PHARMACOTHERAPY,
        section="11.4",
        monitoring="Daily weights, renal function, electrolytes",
    ))
    
    # Dose adjustment
    rec_set.add(guideline_recommendation(
        action="Use lowest diuretic dose needed to maintain euvolemia. Adjust based on clinical status.",
        guideline_key="esc_hf_2021",
        evidence_class=EvidenceClass.I,
        evidence_level=EvidenceLevel.C,
        category=RecommendationCategory.MONITORING,
        section="11.4",
    ))
    
    # Thiazide addition for resistance
    rec_set.add(guideline_recommendation(
        action="Consider adding thiazide (metolazone) for diuretic resistance. Monitor closely for hypokalemia and hyponatremia.",
        guideline_key="esc_hf_2021",
        evidence_class=EvidenceClass.IIA,
        evidence_level=EvidenceLevel.B,
        category=RecommendationCategory.PHARMACOTHERAPY,
        section="11.4",
        conditions=["Inadequate response to high-dose loop diuretic"],
    ))
    
    return rec_set


def optimize_gdmt(patient: "Patient") -> RecommendationSet:
    """
    Generate recommendations for GDMT optimization.
    
    Assesses current medications and provides specific uptitration guidance.
    """
    phenotype = classify_hf_phenotype(patient.lvef)
    
    if phenotype == HFPhenotype.HFREF:
        base_recs = get_hfref_treatment(patient)
    elif phenotype == HFPhenotype.HFMREF:
        base_recs = get_hfmref_treatment(patient)
    elif phenotype == HFPhenotype.HFPEF:
        base_recs = get_hfpef_treatment(patient)
    else:
        # Cannot optimize without LVEF
        rec_set = RecommendationSet(
            title="GDMT Optimization",
            description="Unable to provide specific recommendations without LVEF",
        )
        rec_set.add(guideline_recommendation(
            action="Obtain echocardiogram to determine LVEF and HF phenotype",
            guideline_key="esc_hf_2021",
            evidence_class=EvidenceClass.I,
            evidence_level=EvidenceLevel.C,
            category=RecommendationCategory.DIAGNOSTIC,
            urgency=Urgency.SOON,
            section="4.1",
        ))
        return rec_set
    
    base_recs.title = f"GDMT Optimization for {phenotype.value}"
    base_recs.clinical_question = "How should we optimize guideline-directed medical therapy?"
    
    return base_recs
