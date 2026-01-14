# CardioCode Agent Usage Guide

## Overview

CardioCode is a clinical decision support system that provides:
- **Clinical calculators** (risk scores like CHA2DS2-VASc, HAS-BLED, GRACE, Wells, HCM-SCD)
- **Clinical assessments** (aortic stenosis severity, ICD indication)
- **Knowledge search** (search across 11 pre-extracted ESC guideline PDFs)

## Available Tools

### Clinical Calculators

#### `cardiocode_calculate_cha2ds2_vasc`
Calculate stroke risk in atrial fibrillation.
```
cardiocode_calculate_cha2ds2_vasc(
    age="75",
    female="true",
    chf="false",
    hypertension="true",
    stroke_tia="false",
    vascular_disease="false",
    diabetes="true"
)
```

#### `cardiocode_calculate_has_bled`
Calculate bleeding risk for anticoagulation decisions.
```
cardiocode_calculate_has_bled(
    hypertension_uncontrolled="false",
    abnormal_renal="false",
    abnormal_liver="false",
    stroke_history="false",
    bleeding_history="false",
    labile_inr="false",
    age_over_65="true",
    drugs_predisposing="true",
    alcohol_excess="false"
)
```

#### `cardiocode_calculate_grace_score`
Calculate ACS risk stratification.
```
cardiocode_calculate_grace_score(
    age="68",
    heart_rate="88",
    systolic_bp="130",
    creatinine="1.2",
    killip_class="1",
    cardiac_arrest="false",
    st_deviation="true",
    elevated_troponin="true"
)
```

#### `cardiocode_calculate_wells_pe`
Calculate pulmonary embolism probability.
```
cardiocode_calculate_wells_pe(
    clinical_signs_dvt="true",
    pe_most_likely="true",
    heart_rate_above_100="true",
    immobilization_surgery="false",
    previous_pe_dvt="false",
    hemoptysis="false",
    malignancy="false"
)
```

#### `cardiocode_calculate_hcm_scd_risk`
Calculate 5-year sudden cardiac death risk in HCM.
```
cardiocode_calculate_hcm_scd_risk(
    age="45",
    max_wall_thickness="22",
    la_diameter="45",
    max_lvot_gradient="30",
    family_history_scd="true",
    nsvt="true",
    unexplained_syncope="false"
)
```

### Clinical Assessments

#### `cardiocode_assess_aortic_stenosis`
Assess AS severity and intervention indication.
```
cardiocode_assess_aortic_stenosis(
    peak_velocity="4.5",
    mean_gradient="45",
    ava="0.8",
    lvef="55",
    stroke_volume_index="32"
)
```

#### `cardiocode_assess_icd_indication`
Assess ICD indication for SCD prevention.
```
cardiocode_assess_icd_indication(
    lvef="30",
    nyha_class="2",
    etiology="ischemic",
    prior_vf_vt="false",
    syncope="false",
    days_post_mi="90"
)
```

### Knowledge Base Tools

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

Returns ranked results with:
- Guideline and chapter information
- Content preview
- Matched keywords
- Relevance score
- Table count

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

Use this after adding new guideline PDFs to extract chapters, tables, and keywords.

## Clinical Question Workflow

### 1. For Calculations
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

### 3. For Severity Assessments
Use the assessment tools:
```
cardiocode_assess_aortic_stenosis(peak_velocity="4.5", mean_gradient="45", ava="0.8")
```

## Example Session

```
User: "72-year-old woman with AF, hypertension, diabetes. What's her stroke risk?"

Agent:
1. Use cardiocode_calculate_cha2ds2_vasc(
       age="72", female="true", hypertension="true", diabetes="true"
   )
2. Result: Score 5 (High risk) - Anticoagulation recommended

User: "What about bleeding risk? She's on aspirin."

Agent:
1. Use cardiocode_calculate_has_bled(
       age_over_65="true", hypertension_uncontrolled="false", drugs_predisposing="true"
   )
2. Result: Score 2 (Moderate) - Address modifiable factors, anticoagulation still indicated
```

## Best Practices

1. **Use calculators for specific scores** - more reliable than searching
2. **Search knowledge for narrative questions** - treatment recommendations, diagnostic criteria
3. **Cite guideline sources** when providing recommendations
4. **Check knowledge status** to see available guidelines

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
