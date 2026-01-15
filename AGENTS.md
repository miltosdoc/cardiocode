# CardioCode Agent Usage Guide

## Overview

CardioCode is a comprehensive clinical decision support system providing:
- **50+ Clinical calculators** (risk scores for AF, PE, PAH, HF, arrhythmias, HCM)
- **25+ Clinical assessments** (valvular disease, device therapy, VTE, cardio-oncology, syncope)
- **10+ Clinical pathways** (HF treatment, VT management, PE treatment, syncope)
- **Knowledge search** (search across 11 pre-extracted ESC guideline PDFs)

---

## Clinical Calculators

### Atrial Fibrillation / Stroke Risk

#### `cardiocode_calculate_cha2ds2_vasc`
Calculate stroke risk in atrial fibrillation.
```
cardiocode_calculate_cha2ds2_vasc(
    age="75", female="true", chf="false", hypertension="true",
    stroke_tia="false", vascular_disease="false", diabetes="true"
)
```

#### `cardiocode_calculate_has_bled`
Calculate bleeding risk for anticoagulation decisions.
```
cardiocode_calculate_has_bled(
    hypertension_uncontrolled="false", abnormal_renal="false", abnormal_liver="false",
    stroke_history="false", bleeding_history="false", labile_inr="false",
    age_over_65="true", drugs_predisposing="true", alcohol_excess="false"
)
```

### Acute Coronary Syndrome

#### `cardiocode_calculate_grace_score`
Calculate GRACE score for ACS risk stratification.
```
cardiocode_calculate_grace_score(
    age="68", heart_rate="88", systolic_bp="130", creatinine="1.2",
    killip_class="1", cardiac_arrest="false", st_deviation="true", elevated_troponin="true"
)
```

### Pulmonary Embolism

#### `cardiocode_calculate_wells_pe`
Calculate Wells score for PE pre-test probability.
```
cardiocode_calculate_wells_pe(
    clinical_signs_dvt="true", pe_most_likely="true", heart_rate_above_100="true",
    immobilization_surgery="false", previous_pe_dvt="false", hemoptysis="false", malignancy="false"
)
```

#### `cardiocode_calculate_pesi`
Calculate PESI score for PE 30-day mortality prediction.
```
cardiocode_calculate_pesi(
    age="70", male="true", cancer="false", heart_failure="false", chronic_lung_disease="false",
    pulse_rate="110", systolic_bp="95", respiratory_rate="24", temperature="36.5",
    altered_mental_status="false", o2_saturation="92"
)
```

#### `cardiocode_calculate_spesi`
Calculate Simplified PESI for rapid risk stratification.
```
cardiocode_calculate_spesi(
    age_over_80="false", cancer="false", chronic_cardiopulmonary_disease="false",
    pulse_over_110="true", systolic_bp_under_100="true", o2_saturation_under_90="false"
)
```

#### `cardiocode_calculate_geneva_pe`
Calculate Revised Geneva Score for PE probability.
```
cardiocode_calculate_geneva_pe(
    previous_pe_dvt="false", heart_rate="95", surgery_fracture_past_month="false",
    hemoptysis="false", active_cancer="false", unilateral_leg_pain="true",
    dvt_signs="true", age_over_65="true", simplified="true"
)
```

#### `cardiocode_calculate_age_adjusted_ddimer`
Calculate age-adjusted D-dimer cutoff for PE exclusion.
```
cardiocode_calculate_age_adjusted_ddimer(age="72", baseline_cutoff="500")
```

### Pulmonary Arterial Hypertension

#### `cardiocode_calculate_pah_baseline_risk`
Calculate PAH baseline risk using 3-strata model (1-year mortality).
```
cardiocode_calculate_pah_baseline_risk(
    who_functional_class="3", six_min_walk_distance="350", bnp="150", nt_probnp="800",
    ra_area="22", pericardial_effusion="minimal", cardiac_index="2.3", svo2="62",
    rv_failure_signs="false", symptom_progression="slow", syncope="none"
)
```

#### `cardiocode_calculate_pah_followup_risk`
Calculate PAH follow-up risk using simplified 4-strata model.
```
cardiocode_calculate_pah_followup_risk(
    who_functional_class="2", six_min_walk_distance="420", bnp="80", nt_probnp="350"
)
```

#### `cardiocode_classify_ph_hemodynamics`
Classify pulmonary hypertension by hemodynamic definitions.
```
cardiocode_classify_ph_hemodynamics(
    mean_pap="35", pawp="12", pvr="4", cardiac_output="4.5"
)
```

### Heart Failure

#### `cardiocode_calculate_maggic_score`
Calculate MAGGIC score for HF 1-year and 3-year mortality.
```
cardiocode_calculate_maggic_score(
    age="68", male="true", lvef="28", nyha_class="3", systolic_bp="105",
    bmi="27", creatinine="1.4", current_smoker="false", diabetes="true", copd="false",
    hf_diagnosis_18_months="true", on_beta_blocker="true", on_acei_arb="true"
)
```

#### `cardiocode_assess_iron_deficiency_hf`
Assess iron deficiency in HF patients and IV iron indication.
```
cardiocode_assess_iron_deficiency_hf(
    ferritin="80", transferrin_saturation="18", hemoglobin="11.5",
    symptomatic_hf="true", lvef="35"
)
```

#### `cardiocode_classify_hf_phenotype`
Classify HF phenotype (HFrEF, HFmrEF, HFpEF) by LVEF.
```
cardiocode_classify_hf_phenotype(
    lvef="42", bnp="250", nt_probnp="1200",
    structural_abnormality="true", diastolic_dysfunction="true"
)
```

### Hypertrophic Cardiomyopathy

#### `cardiocode_calculate_hcm_scd_risk`
Calculate 5-year sudden cardiac death risk in HCM.
```
cardiocode_calculate_hcm_scd_risk(
    age="45", max_wall_thickness="22", la_diameter="45", max_lvot_gradient="30",
    family_history_scd="true", nsvt="true", unexplained_syncope="false"
)
```

### Arrhythmia Risk (Channelopathies, LMNA)

#### `cardiocode_calculate_lmna_risk`
Calculate 5-year VA risk in LMNA mutation carriers.
```
cardiocode_calculate_lmna_risk(
    lvef="45", nsvt="true", male="true", av_conduction_delay="true"
)
```

#### `cardiocode_calculate_lqts_risk`
Estimate arrhythmic risk in Long QT Syndrome.
```
cardiocode_calculate_lqts_risk(
    qtc="490", genotype="LQT2", male="false", age="25",
    prior_syncope="true", prior_cardiac_arrest="false"
)
```

#### `cardiocode_calculate_brugada_risk`
Risk stratification in Brugada Syndrome.
```
cardiocode_calculate_brugada_risk(
    spontaneous_type1="true", induced_type1_only="false", prior_cardiac_arrest="false",
    documented_vt_vf="false", syncope_suspected_arrhythmic="true",
    family_history_scd="true", male="true"
)
```

---

## Clinical Assessments

### Valvular Heart Disease

#### `cardiocode_assess_aortic_stenosis`
Assess AS severity and intervention indication.
```
cardiocode_assess_aortic_stenosis(
    peak_velocity="4.5", mean_gradient="45", ava="0.8", lvef="55", stroke_volume_index="32"
)
```

#### `cardiocode_assess_ar_severity`
Assess aortic regurgitation severity and intervention indication.
```
cardiocode_assess_ar_severity(
    lvesd="55", lvef="52", symptomatic="false",
    undergoing_cardiac_surgery="false", lvesdi="", bsa="1.9"
)
```

#### `cardiocode_assess_mr_primary_intervention`
Assess primary mitral regurgitation intervention indication.
```
cardiocode_assess_mr_primary_intervention(
    lvesd="42", lvef="58", symptomatic="false", af="true",
    spap="55", lavi="65", tr_moderate_or_greater="false",
    repair_likely_durable="true", surgical_risk="low"
)
```

#### `cardiocode_assess_mr_secondary_teer`
Assess secondary MR eligibility for TEER (MitraClip).
```
cardiocode_assess_mr_secondary_teer(
    lvef="32", symptomatic="true", on_gdmt="true", crt_if_indicated="true",
    hemodynamically_stable="true", mr_severity="severe", eroa="0.35"
)
```

#### `cardiocode_assess_tr_intervention`
Assess tricuspid regurgitation intervention indication.
```
cardiocode_assess_tr_intervention(
    tr_severity="severe", primary_or_secondary="secondary",
    rv_function="mild_dysfunction", symptomatic="true",
    rv_dilatation="true", left_sided_surgery_planned="false", surgical_risk="high"
)
```

#### `cardiocode_assess_ms_intervention`
Assess mitral stenosis intervention indication.
```
cardiocode_assess_ms_intervention(
    mva="1.2", symptomatic="true", favorable_anatomy_for_pmc="true",
    contraindication_to_pmc="false", af="true", spap="55"
)
```

#### `cardiocode_assess_valve_type_selection`
Assess mechanical vs biological valve selection.
```
cardiocode_assess_valve_type_selection(
    age="55", valve_position="aortic", oac_contraindicated="false",
    quality_oac_achievable="true", high_bleeding_risk="false",
    female_contemplating_pregnancy="false"
)
```

#### `cardiocode_calculate_inr_target_mhv`
Calculate INR target for mechanical heart valve.
```
cardiocode_calculate_inr_target_mhv(
    valve_type="bileaflet", valve_position="mitral", prothrombotic_factors="true"
)
```

### Device Therapy (ICD, CRT, Pacing)

#### `cardiocode_assess_icd_indication`
Assess ICD indication for SCD prevention.
```
cardiocode_assess_icd_indication(
    lvef="30", nyha_class="2", etiology="ischemic",
    prior_vf_vt="false", syncope="false", days_post_mi="90"
)
```

#### `cardiocode_assess_crt_indication`
Assess CRT indication based on ESC guidelines.
```
cardiocode_assess_crt_indication(
    lvef="30", qrs_duration="155", qrs_morphology="lbbb",
    rhythm="sinus", nyha_class="2", on_optimal_medical_therapy="true",
    av_block_pacing_indication="false", has_icd_indication="true"
)
```

#### `cardiocode_assess_dcm_icd_indication`
Assess ICD indication in dilated cardiomyopathy (with genetic risk factors).
```
cardiocode_assess_dcm_icd_indication(
    lvef="32", nyha_class="2", months_on_omt="4",
    lmna_mutation="true", syncope="false", lge_on_cmr="true",
    nsvt="true", prior_vt_vf="false"
)
```

#### `cardiocode_assess_arvc_icd_indication`
Assess ICD indication in ARVC.
```
cardiocode_assess_arvc_icd_indication(
    definite_arvc="true", rv_dysfunction="moderate", lv_dysfunction="none",
    syncope="true", nsvt="true", prior_vt_vf="false"
)
```

#### `cardiocode_assess_sarcoidosis_icd_indication`
Assess ICD indication in cardiac sarcoidosis.
```
cardiocode_assess_sarcoidosis_icd_indication(
    lvef="42", lge_extent="significant", sustained_vt="false",
    aborted_cardiac_arrest="false", syncope="false"
)
```

#### `cardiocode_assess_pacing_indication`
Assess pacemaker indication for bradycardia.
```
cardiocode_assess_pacing_indication(
    avb_degree="third", snd_documented="false", symptoms_correlated="true",
    sinus_pause_seconds="", bifascicular_block="false", alternating_bbb="false"
)
```

#### `cardiocode_select_pacing_mode`
Select appropriate pacing mode (DDD, VVI, etc.).
```
cardiocode_select_pacing_mode(
    primary_indication="avb", rhythm="sinus", av_conduction_intact="false",
    chronotropic_incompetence="false", lvef="38"
)
```

### Venous Thromboembolism

#### `cardiocode_assess_pe_risk_stratification`
Assess PE risk stratification (high/intermediate/low).
```
cardiocode_assess_pe_risk_stratification(
    hemodynamic_status="stable", pesi_class="", spesi_score="0",
    rv_dysfunction="false", elevated_troponin="false"
)
```

#### `cardiocode_assess_pe_thrombolysis`
Assess thrombolysis indication for PE.
```
cardiocode_assess_pe_thrombolysis(
    risk_category="high", hemodynamic_status="shock"
)
```

#### `cardiocode_assess_pe_outpatient_eligibility`
Assess eligibility for outpatient PE treatment.
```
cardiocode_assess_pe_outpatient_eligibility(
    spesi_score="0", hemodynamically_stable="true", o2_required="false",
    high_bleeding_risk="false", social_support_adequate="true"
)
```

#### `cardiocode_calculate_vte_recurrence_risk`
Calculate VTE recurrence risk and anticoagulation duration recommendation.
```
cardiocode_calculate_vte_recurrence_risk(
    risk_factor_category="no_identifiable", prior_vte="false",
    male="true", elevated_d_dimer_after_anticoag="false"
)
```

### Cardio-Oncology

#### `cardiocode_assess_cardio_oncology_baseline_risk`
Assess baseline CV risk before cardiotoxic cancer therapy (HFA-ICOS).
```
cardiocode_assess_cardio_oncology_baseline_risk(
    age="65", prior_hf_cardiomyopathy="false", prior_cad="false",
    baseline_lvef="58", hypertension="true", diabetes="false",
    prior_anthracycline="false", prior_chest_rt="false", planned_treatment="anthracycline"
)
```

#### `cardiocode_assess_ctrcd_severity`
Assess cancer therapy-related cardiac dysfunction severity.
```
cardiocode_assess_ctrcd_severity(
    baseline_lvef="60", current_lvef="48", gls_decline_percent="18",
    troponin_elevated="true", symptomatic="false", treatment_type="anthracycline"
)
```

#### `cardiocode_get_surveillance_protocol`
Get surveillance protocol for cardiotoxic cancer therapy.
```
cardiocode_get_surveillance_protocol(
    treatment_type="anthracycline", risk_category="high", treatment_phase="during"
)
```

### Syncope

#### `cardiocode_assess_syncope_risk`
Assess syncope risk and disposition recommendation.
```
cardiocode_assess_syncope_risk(
    syncope_during_exertion="false", syncope_supine="false",
    syncope_without_prodrome="false", palpitations_before_syncope="false",
    structural_heart_disease="false", known_coronary_disease="false",
    mobitz_ii_or_complete_avb="false", vt_or_rapid_svt="false",
    bifascicular_block="false", typical_vasovagal_prodrome="true",
    absence_of_heart_disease="true"
)
```

#### `cardiocode_classify_syncope_etiology`
Classify likely syncope etiology.
```
cardiocode_classify_syncope_etiology(
    triggered_by_pain_fear="true", triggered_by_prolonged_standing="true",
    triggered_by_cough="false", triggered_by_defecation_micturition="false",
    pallor_sweating_nausea="true", orthostatic_bp_drop="false",
    structural_heart_disease="false", abnormal_ecg="false"
)
```

#### `cardiocode_diagnose_orthostatic_hypotension`
Diagnose orthostatic hypotension from BP measurements.
```
cardiocode_diagnose_orthostatic_hypotension(
    supine_sbp="140", supine_dbp="85", standing_sbp_1min="115",
    standing_dbp_1min="75", standing_sbp_3min="110", standing_dbp_3min="72",
    symptoms_on_standing="true"
)
```

#### `cardiocode_assess_tilt_test_indication`
Assess indication for tilt table testing.
```
cardiocode_assess_tilt_test_indication(
    suspected_reflex_syncope="true", reflex_not_confirmed_by_history="true",
    suspected_oh="false", suspected_pots="false"
)
```

---

## Clinical Pathways

### Heart Failure Treatment

#### `cardiocode_pathway_hfref_treatment`
HFrEF treatment pathway - determine next therapy step.
```
cardiocode_pathway_hfref_treatment(
    current_medications="acei,bb,mra",
    lvef="28", nyha_class="2", systolic_bp="108", heart_rate="72",
    potassium="4.5", egfr="55", rhythm="sinus", qrs_duration="100",
    on_max_beta_blocker="false", iron_deficient="true"
)
```

#### `cardiocode_pathway_hf_device_therapy`
HF device therapy pathway - ICD and CRT decision support.
```
cardiocode_pathway_hf_device_therapy(
    lvef="30", qrs_duration="160", qrs_morphology="lbbb",
    nyha_class="2", rhythm="sinus", etiology="ischemic",
    months_on_omt="4", days_post_mi="", prior_vt_vf="false"
)
```

#### `cardiocode_get_hf_medication_targets`
Get target doses for HF medications.
```
cardiocode_get_hf_medication_targets()
```

### Ventricular Tachycardia Management

#### `cardiocode_pathway_vt_acute_management`
Acute VT management pathway.
```
cardiocode_pathway_vt_acute_management(
    hemodynamic_status="stable", vt_morphology="monomorphic",
    lvef="35", structural_heart_disease="true"
)
```

#### `cardiocode_pathway_electrical_storm`
Electrical storm management pathway.
```
cardiocode_pathway_electrical_storm(
    hemodynamic_status="unstable", icd_present="true", lvef="25"
)
```

#### `cardiocode_pathway_vt_chronic_management`
Chronic VT management pathway.
```
cardiocode_pathway_vt_chronic_management(
    etiology="ischemic", lvef="30", recurrent_vt="true", icd_shocks="true"
)
```

### Pulmonary Embolism Treatment

#### `cardiocode_pathway_pe_treatment`
PE treatment pathway.
```
cardiocode_pathway_pe_treatment(
    risk_category="intermediate_low", hemodynamic_status="stable",
    bleeding_risk="low", renal_function="normal"
)
```

#### `cardiocode_pathway_pe_anticoagulation_duration`
PE anticoagulation duration pathway.
```
cardiocode_pathway_pe_anticoagulation_duration(
    risk_factor_category="no_identifiable", bleeding_risk="low",
    patient_preference_extended="true"
)
```

### Syncope Evaluation

#### `cardiocode_pathway_syncope_evaluation`
Syncope evaluation pathway.
```
cardiocode_pathway_syncope_evaluation(
    initial_assessment_diagnostic="false", structural_heart_disease="false",
    abnormal_ecg="false", exertional_syncope="false"
)
```

#### `cardiocode_pathway_syncope_disposition`
Syncope disposition pathway.
```
cardiocode_pathway_syncope_disposition(
    risk_category="low", diagnosis_established="true",
    high_risk_occupation="false"
)
```

---

## Knowledge Base Tools

#### `cardiocode_get_knowledge_status`
Get status of available guidelines.
```
cardiocode_get_knowledge_status()
```

Returns list of 11 pre-processed ESC guidelines:
- 2025 ESC/EACTS Valvular Heart Disease
- 2022 ESC Ventricular Arrhythmias/SCD
- 2022 ESC/ERS Pulmonary Hypertension
- 2022 ESC Cardio-Oncology
- 2021 ESC Heart Failure
- 2021 ESC Cardiac Pacing/CRT
- 2021 ESC Cardiovascular Prevention
- 2020 ESC Congenital Heart Disease
- 2020 ESC Sports Cardiology
- 2019 ESC Pulmonary Embolism
- 2018 ESC Syncope

#### `cardiocode_search_knowledge`
Search across all guideline content.
```
cardiocode_search_knowledge(
    query="aortic stenosis treatment recommendations",
    max_results="5"
)
```

#### `cardiocode_get_chapter`
Get full chapter content.
```
cardiocode_get_chapter(
    guideline_slug="2025_esc_eacts_valvular_heart_disease_ehaf194",
    chapter_title="Aortic stenosis"
)
```

#### `cardiocode_process_pdfs`
Process new PDFs added to `source_pdfs/` directory.
```
cardiocode_process_pdfs()
```

---

## Clinical Question Workflow

### 1. For Specific Calculations
Use the specific calculator tool directly:
```
cardiocode_calculate_cha2ds2_vasc(age="75", female="true", hypertension="true", ...)
```

### 2. For Guideline Questions
Search the knowledge base:
```
cardiocode_search_knowledge(query="severe asymptomatic aortic stenosis management")
```

Then retrieve full chapter if needed:
```
cardiocode_get_chapter(guideline_slug="...", chapter_title="...")
```

### 3. For Severity/Intervention Assessments
Use the assessment tools:
```
cardiocode_assess_aortic_stenosis(peak_velocity="4.5", mean_gradient="45", ava="0.8")
```

### 4. For Treatment Pathways
Use pathway tools for step-by-step guidance:
```
cardiocode_pathway_hfref_treatment(current_medications="acei,bb", lvef="30", ...)
```

---

## Example Session

```
User: "68-year-old man with HFrEF (LVEF 28%), on ACE-I and beta-blocker. 
       What should we add next? Also, does he need a device?"

Agent:
1. Use cardiocode_pathway_hfref_treatment(
       current_medications="acei,bb",
       lvef="28", nyha_class="2", systolic_bp="110", heart_rate="68",
       potassium="4.2", egfr="55", rhythm="sinus"
   )
2. Result: Recommends adding MRA + SGLT2i to complete quadruple therapy.
   Also suggests switching ACE-I to ARNI.

3. Use cardiocode_pathway_hf_device_therapy(
       lvef="28", qrs_duration="100", qrs_morphology="normal",
       nyha_class="2", etiology="ischemic", months_on_omt="3"
   )
4. Result: QRS <130ms, so no CRT indication. ICD may be considered for
   primary prevention (Class I for ischemic, LVEF ≤35%, NYHA II).
```

---

## Best Practices

1. **Use calculators for specific scores** - more reliable than searching
2. **Search knowledge for narrative questions** - treatment recommendations, diagnostic criteria
3. **Use pathways for treatment optimization** - step-by-step decision support
4. **Cite guideline sources** when providing recommendations
5. **Check knowledge status** to see available guidelines

---

## Troubleshooting

### Tools not found
- Verify MCP server is running
- Check `opencode.json` configuration

### PDF processing fails
- Install PyMuPDF: `pip install pymupdf`
- Verify PDFs exist in `source_pdfs/` directory

### Search returns no results
- Try broader search terms
- Check `cardiocode_get_knowledge_status()` for available guidelines
