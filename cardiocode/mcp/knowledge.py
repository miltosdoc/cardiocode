"""
CardioCode Knowledge Base.

Comprehensive clinical knowledge from ESC Guidelines (2018-2024).
This module provides structured knowledge for MCP resources.

All content is derived from official ESC guidelines and includes:
- Heart Failure (ESC 2021)
- Atrial Fibrillation (ESC 2020/2024)
- Ventricular Arrhythmias & SCD (ESC 2022)
- Valvular Heart Disease (ESC 2021)
- Chronic Coronary Syndromes (ESC 2019)
- NSTE-ACS (ESC 2020)
- STEMI (ESC 2023)
- Pulmonary Hypertension (ESC 2022)
- Cardio-Oncology (ESC 2022)
- Pulmonary Embolism (ESC 2019)
- Hypertension (ESC 2024)
- CV Prevention (ESC 2021)
- Peripheral Arterial Disease (ESC 2024)
- Syncope (ESC 2018)
"""

# =============================================================================
# HEART FAILURE KNOWLEDGE (ESC 2021)
# =============================================================================

HEART_FAILURE_KNOWLEDGE = """# Heart Failure Guidelines (ESC 2021)

## Classification by LVEF

| Phenotype | LVEF | Description |
|-----------|------|-------------|
| HFrEF | <= 40% | Heart failure with reduced ejection fraction |
| HFmrEF | 41-49% | Heart failure with mildly reduced ejection fraction |
| HFpEF | >= 50% | Heart failure with preserved ejection fraction |

## HFrEF Treatment - The Four Pillars (Class I, Level A)

### 1. ACEi/ARB/ARNI
- **ARNI (sacubitril/valsartan)**: Preferred over ACEi in eligible patients
- **ACEi**: If ARNI not tolerated/available
- **ARB**: If ACEi not tolerated (cough, angioedema)
- **Key trials**: PARADIGM-HF, CONSENSUS, SOLVD

### 2. Beta-Blockers
- **Carvedilol, bisoprolol, metoprolol succinate, nebivolol**
- Start low, titrate to maximum tolerated dose
- Contraindicated: HR <50, SBP <90, acute decompensation
- **Key trials**: COPERNICUS, MERIT-HF, CIBIS-II

### 3. MRA (Mineralocorticoid Receptor Antagonists)
- **Spironolactone** or **Eplerenone**
- Contraindicated: K+ >5.0, eGFR <30
- Monitor K+ within 1 week of initiation
- **Key trials**: RALES, EMPHASIS-HF

### 4. SGLT2 Inhibitors
- **Dapagliflozin** or **Empagliflozin**
- Benefit regardless of diabetes status
- Can be started in hospital
- **Key trials**: DAPA-HF, EMPEROR-Reduced

## Additional Therapies

### Diuretics
- Loop diuretics for congestion relief
- Not mortality benefit, but symptom improvement
- Adjust based on volume status

### Ivabradine
- If HR >= 70 despite maximum beta-blocker
- Must be in sinus rhythm
- **Key trial**: SHIFT

### Hydralazine + Nitrates
- Alternative to ACEi/ARB if both contraindicated
- Particularly beneficial in Black patients
- **Key trial**: A-HeFT

## Device Therapy

### ICD (Primary Prevention)
- LVEF <= 35% despite >= 3 months OMT
- NYHA II-III
- Expected survival >1 year
- Wait >= 40 days post-MI

### CRT
- LVEF <= 35%
- QRS >= 150ms (or 130-149ms with LBBB)
- NYHA II-IV despite OMT
- Sinus rhythm

## HFmrEF Treatment
- Similar to HFrEF, slightly less evidence
- SGLT2i shown beneficial (DELIVER)
- Treat underlying etiology

## HFpEF Treatment
- SGLT2i now Class I (EMPEROR-Preserved, DELIVER)
- Treat comorbidities aggressively
- Diuretics for congestion
- Weight loss if obese

## Monitoring Parameters
- Renal function and electrolytes at baseline and after dose changes
- NT-proBNP for prognostication
- Echo q6-12 months or with clinical change

## Key Clinical Pearls
1. Start all four pillars simultaneously when possible
2. SGLT2i can be started in-hospital during decompensation
3. Don't delay therapy waiting for dose optimization
4. ICD timing: wait 40 days post-MI, 3 months post-revascularization
"""

# =============================================================================
# ATRIAL FIBRILLATION KNOWLEDGE (ESC 2020/2024)
# =============================================================================

ATRIAL_FIBRILLATION_KNOWLEDGE = """# Atrial Fibrillation Guidelines (ESC 2020/2024)

## AF Classification

| Type | Definition |
|------|------------|
| First diagnosed | First episode, regardless of duration |
| Paroxysmal | Self-terminating, usually <7 days |
| Persistent | >7 days or requiring cardioversion |
| Long-standing persistent | >1 year when rhythm control adopted |
| Permanent | AF accepted by patient and physician |

## The CC-to-ABC Pathway

### Confirm AF
- ECG documentation required
- Single-lead ECG >= 30 seconds
- 12-lead ECG preferred

### Characterize AF (4 S's)
1. **Stroke risk** - CHA2DS2-VASc
2. **Symptom severity** - EHRA score
3. **Severity of AF burden** - Paroxysmal vs persistent
4. **Substrate severity** - LA size, comorbidities

### Treat - ABC Pathway
- **A**: Anticoagulation/Avoid stroke
- **B**: Better symptom control (rate/rhythm)
- **C**: Comorbidity management

## CHA2DS2-VASc Score

| Risk Factor | Points |
|-------------|--------|
| Congestive heart failure | 1 |
| Hypertension | 1 |
| Age >= 75 | 2 |
| Diabetes | 1 |
| Stroke/TIA/TE | 2 |
| Vascular disease | 1 |
| Age 65-74 | 1 |
| Sex (female) | 1 |

### Anticoagulation Recommendations
- Score >= 2 (men) or >= 3 (women): OAC recommended (Class I)
- Score = 1 (men) or = 2 (women): OAC should be considered (Class IIa)
- Score = 0 (men) or = 1 (women): OAC not recommended

### DOAC vs Warfarin
- DOACs preferred over VKA (Class I)
- Apixaban, dabigatran, edoxaban, rivaroxaban
- VKA required for mechanical valves, moderate-severe MS

## HAS-BLED Score (Bleeding Risk)

| Factor | Points |
|--------|--------|
| Hypertension (uncontrolled, >160) | 1 |
| Abnormal renal function | 1 |
| Abnormal liver function | 1 |
| Stroke history | 1 |
| Bleeding history/predisposition | 1 |
| Labile INR (TTR <60%) | 1 |
| Elderly (>65) | 1 |
| Drugs (antiplatelet, NSAIDs) | 1 |
| Alcohol excess (>=8/week) | 1 |

- Score >= 3: High bleeding risk
- Address modifiable risk factors
- NOT a reason to withhold anticoagulation

## Rate Control

### Target Heart Rate
- Lenient: <110 bpm at rest (initial target)
- Strict: <80 bpm if symptoms persist

### Medications
- **Beta-blockers**: First-line
- **Non-DHP CCBs**: Diltiazem, verapamil (avoid in HFrEF)
- **Digoxin**: Adjunct, or if sedentary
- **Amiodarone**: Last resort for rate control

## Rhythm Control

### When to Prefer Rhythm Control
- Symptomatic AF
- Younger patients
- First episode
- Tachycardia-mediated cardiomyopathy
- Patient preference

### Antiarrhythmic Drugs
- **Flecainide/Propafenone**: No structural heart disease
- **Amiodarone**: HF, structural heart disease (toxicity concerns)
- **Dronedarone**: Alternative to amiodarone, avoid in HF
- **Sotalol**: Avoid in HFrEF, QT prolongation risk

### Cardioversion
- If AF <48h or adequately anticoagulated: Can cardiovert
- If AF >48h and not anticoagulated: TEE to exclude LAA thrombus OR 3 weeks anticoagulation
- Continue anticoagulation 4 weeks post-cardioversion (longer if high stroke risk)

## Ablation (Catheter or Surgical)

### Indications (Class I)
- Symptomatic paroxysmal AF refractory to antiarrhythmic
- As first-line alternative to AAD (Class IIa)
- Tachycardia-mediated cardiomyopathy

### Success Rates
- Paroxysmal AF: 70-80% single procedure
- Persistent AF: 50-70% single procedure
- May need repeat procedures

## Upstream Therapy
- Treat hypertension
- Weight loss if obese
- OSA treatment
- Alcohol reduction
- Exercise (moderate)
"""

# =============================================================================
# VENTRICULAR ARRHYTHMIAS KNOWLEDGE (ESC 2022)
# =============================================================================

VENTRICULAR_ARRHYTHMIAS_KNOWLEDGE = """# Ventricular Arrhythmias & SCD Prevention (ESC 2022)

## VT Classification

| Type | Characteristics |
|------|-----------------|
| Monomorphic sustained VT | >30s or hemodynamic compromise, uniform QRS |
| Polymorphic VT | Changing QRS morphology |
| Electrical storm | >= 3 VT/VF episodes in 24 hours |
| NSVT | >= 3 beats, <30s, self-terminating |
| Idiopathic VT | No structural heart disease |

## Acute VT Management

### Hemodynamically Unstable
- **Immediate DC cardioversion** (synchronized if organized rhythm)
- Sedation if conscious and time permits

### Hemodynamically Stable Monomorphic VT
1. **Amiodarone IV**: 150mg over 10 min, then infusion
2. **Procainamide IV**: Alternative
3. **Lidocaine IV**: Ischemic VT
4. **DC cardioversion** if drugs fail

### Electrical Storm
- Amiodarone IV + beta-blocker
- Deep sedation/intubation if refractory
- Consider catheter ablation
- ECMO/mechanical support if cardiogenic shock

## ICD Indications

### Secondary Prevention (Class I)
- Survived VF/sustained VT with hemodynamic compromise
- NOT due to reversible cause
- Expected survival >1 year

### Primary Prevention

#### Ischemic Cardiomyopathy
- LVEF <= 35% despite >= 3 months OMT
- NYHA II-III
- >= 40 days post-MI
- >= 3 months post-revascularization

#### Non-Ischemic Cardiomyopathy
- LVEF <= 35% despite >= 3 months OMT
- NYHA II-III
- Selected etiologies (LMNA, etc.) may have lower thresholds

### Special Populations

#### HCM (Hypertrophic Cardiomyopathy)
- Use HCM Risk-SCD calculator
- >= 6% 5-year risk: ICD recommended
- 4-6% 5-year risk: ICD should be considered
- <4%: ICD may be considered with risk modifiers

#### ARVC
- High-risk features: sustained VT, severe RV dysfunction
- Consider ICD even with preserved function if high-risk genotype

## HCM Risk-SCD Calculator Variables
- Age (16-80)
- Max LV wall thickness (mm)
- LA diameter (mm)
- Max LVOT gradient (mmHg)
- Family history of SCD
- NSVT
- Unexplained syncope

## Catheter Ablation for VT

### Indications
- Recurrent monomorphic VT despite AAD
- Electrical storm not controlled medically
- Incessant VT
- To reduce ICD shocks

### Success Rates
- 70-80% for scar-related VT (single procedure)
- May reduce VT recurrence by 50%
- Does not eliminate need for ICD

## Antiarrhythmic Drugs for VT

### Chronic Suppression
- **Amiodarone**: Most effective, significant toxicity
- **Sotalol**: If no HFrEF, watch QTc
- **Mexiletine**: Adjunct to amiodarone

### Long QT Syndrome
- Beta-blockers (nadolol, propranolol)
- Avoid QT-prolonging drugs
- ICD if high-risk or breakthrough events

### Brugada Syndrome
- Quinidine for arrhythmic storms
- Ablation for epicardial substrate
- ICD for survivors of VF
"""

# =============================================================================
# VALVULAR HEART DISEASE KNOWLEDGE (ESC 2021)
# =============================================================================

VALVULAR_DISEASE_KNOWLEDGE = """# Valvular Heart Disease Guidelines (ESC 2021)

## Aortic Stenosis (AS)

### Severity Grading

| Parameter | Mild | Moderate | Severe |
|-----------|------|----------|--------|
| Peak velocity (m/s) | <3.0 | 3.0-4.0 | >4.0 |
| Mean gradient (mmHg) | <20 | 20-40 | >40 |
| AVA (cm2) | >1.5 | 1.0-1.5 | <1.0 |
| Indexed AVA (cm2/m2) | >0.85 | 0.6-0.85 | <0.6 |

### Special AS Patterns

#### Low-Flow, Low-Gradient (LVEF <50%)
- Classic paradox: severe AVA but low gradient
- Dobutamine stress echo to differentiate true-severe vs pseudo-severe
- True severe: AVA remains <1.0, velocity increases

#### Low-Flow, Low-Gradient (LVEF preserved)
- Paradoxical low-flow: small LV, low SVI (<35 mL/m2)
- CT calcium scoring helpful (Agatston score)
- Men: >2000, Women: >1200 suggests severe

### Intervention Indications

#### Symptomatic Severe AS
- Symptoms: Angina, syncope, heart failure
- TAVI or SAVR based on Heart Team assessment (Class I)

#### Asymptomatic Severe AS (Class I indications)
- LVEF <50%
- Symptoms on exercise testing
- Very severe AS (Vmax >5.5 m/s) with low surgical risk

#### Choice: TAVI vs SAVR
- Age <75, low surgical risk: SAVR preferred
- Age >= 75 or high surgical risk: TAVI preferred
- Intermediate risk: Heart Team decision

## Mitral Regurgitation (MR)

### Etiology Classification
- **Primary (organic)**: Leaflet/chordal disease (prolapse, flail, rheumatic)
- **Secondary (functional)**: LV dilation/dysfunction, LA dilation

### Severity Criteria

| Parameter | Mild | Moderate | Severe |
|-----------|------|----------|--------|
| EROA (mm2) - Primary | <20 | 20-39 | >=40 |
| EROA (mm2) - Secondary | <20 | 20-29 | >=30 |
| Regurgitant volume (mL) | <30 | 30-59 | >=60 (primary), >=45 (secondary) |
| Vena contracta (mm) | <3 | 3-6 | >=7 |

### Primary MR - Intervention

#### Symptomatic
- Surgery recommended (Class I)
- Repair preferred over replacement

#### Asymptomatic Severe Primary MR
- LVEF <60% or LVESD >40mm: Surgery (Class I)
- AF onset or PASP >50: Surgery should be considered
- Flail leaflet + LVESD >=40mm: Surgery should be considered

### Secondary MR
- Optimize HF therapy first
- Cardiac resynchronization if indicated
- Surgery: Combined with revascularization or LV reverse remodeling expected
- Transcatheter edge-to-edge repair: If symptomatic despite OMT

## Aortic Regurgitation (AR)

### Severity Criteria

| Parameter | Mild | Moderate | Severe |
|-----------|------|----------|--------|
| Vena contracta (mm) | <3 | 3-6 | >6 |
| Regurgitant volume (mL) | <30 | 30-59 | >=60 |
| EROA (mm2) | <10 | 10-29 | >=30 |
| PHT (ms) | >500 | 200-500 | <200 |

### Intervention Indications
- Symptomatic severe AR: Surgery (Class I)
- Asymptomatic severe AR with LVEF <50%: Surgery (Class I)
- Asymptomatic severe AR with LVEF >50% but LVESD >50mm or LVEDV index >20mm/m2: Surgery (Class IIa)

## Mitral Stenosis (MS)

### Severity
- Mild: MVA >1.5 cm2
- Moderate: MVA 1.0-1.5 cm2
- Severe: MVA <1.0 cm2

### Intervention
- PMC (balloon valvotomy) preferred if anatomy favorable
- Surgery if unfavorable anatomy or significant MR

## General Principles
- All patients need endocarditis prophylaxis education
- Anticoagulation for AF regardless of valve type
- Mechanical valves: lifelong VKA (INR target based on valve position/type)
- Bioprosthetic: Consider anticoagulation first 3 months
"""

# =============================================================================
# CORONARY SYNDROMES KNOWLEDGE (ESC 2019-2020)
# =============================================================================

CORONARY_SYNDROMES_KNOWLEDGE = """# Coronary Syndromes Guidelines (ESC 2019-2020)

## Chronic Coronary Syndromes (ESC 2019)

### Pre-Test Probability of CAD

Clinical PTP based on age, sex, and chest pain characteristics:

| Age | Typical Angina (M/F) | Atypical (M/F) | Non-anginal (M/F) |
|-----|----------------------|----------------|-------------------|
| 30-39 | 3%/5% | 4%/3% | 1%/1% |
| 40-49 | 22%/10% | 10%/6% | 3%/2% |
| 50-59 | 32%/13% | 17%/6% | 11%/3% |
| 60-69 | 44%/16% | 26%/11% | 22%/6% |
| 70+ | 52%/27% | 34%/19% | 24%/10% |

### Chest Pain Classification

#### Typical Angina (3 of 3)
1. Substernal chest discomfort
2. Provoked by exertion or emotional stress
3. Relieved by rest or nitroglycerin

#### Atypical Angina
- 2 of 3 criteria

#### Non-Anginal Chest Pain
- 0-1 of 3 criteria

### Diagnostic Pathway Based on PTP

| PTP | Recommendation |
|-----|----------------|
| <5% | CAD unlikely, consider other diagnoses |
| 5-15% | Functional imaging OR CCTA |
| 15-85% | Non-invasive testing recommended |
| >85% | CAD highly likely, consider direct ICA |

### Non-Invasive Testing Options
- **Exercise ECG**: If able to exercise, no baseline ECG abnormalities
- **Stress imaging**: Preferred for intermediate PTP
  - Stress echo
  - SPECT/PET MPI
  - Stress CMR
- **CCTA**: Excellent negative predictive value

## NSTE-ACS (ESC 2020)

### Diagnosis
- Symptoms of myocardial ischemia
- Troponin rise and/or fall (hs-cTn)
- No persistent ST-elevation

### GRACE Score for Risk Stratification

| Variable | Points |
|----------|--------|
| Age (per decade) | Variable |
| Heart rate | Variable |
| Systolic BP | Variable |
| Creatinine | Variable |
| Killip class | Variable |
| Cardiac arrest | 39 |
| ST deviation | 28 |
| Elevated troponin | 14 |

### Risk Categories
- Low risk: GRACE <109
- Intermediate: GRACE 109-140
- High risk: GRACE >140

### Invasive Strategy Timing

| Risk Category | Timing |
|---------------|--------|
| Very high risk | <2 hours (immediate) |
| High risk | <24 hours |
| Intermediate risk | <72 hours |
| Low risk | Non-invasive testing first |

### Very High Risk Criteria (Immediate Invasive)
- Hemodynamic instability/cardiogenic shock
- Recurrent/refractory angina despite medical therapy
- Life-threatening arrhythmias
- Mechanical complications of MI
- Acute heart failure related to ACS
- ST depression >1mm in >=6 leads + ST elevation aVR/V1

### Antithrombotic Therapy

#### Antiplatelet
- Aspirin: All patients, loading 150-300mg
- P2Y12 inhibitor: Ticagrelor or prasugrel preferred over clopidogrel
- Prasugrel: Not before anatomy known, avoid if prior stroke

#### Anticoagulation
- Fondaparinux preferred (lower bleeding)
- Enoxaparin alternative
- UFH if urgent invasive planned

### Post-PCI Antithrombotic
- DAPT duration based on bleeding vs ischemic risk
- Standard: 12 months
- Short DAPT (3-6 months): High bleeding risk
- Extended DAPT (>12 months): High ischemic risk, low bleeding risk

## STEMI (ESC 2023)

### Diagnosis
- Symptoms of myocardial ischemia
- Persistent ST-elevation >=1mm in 2 contiguous leads
- Or new LBBB with clinical suspicion

### Time Targets
- First medical contact to diagnosis: <10 minutes
- FMC to wire crossing (primary PCI): <90 minutes (preferably <60)
- If no PCI capability: Fibrinolysis within 10 minutes of diagnosis

### Primary PCI
- Preferred reperfusion strategy if timely
- Radial access preferred
- DES preferred over BMS
- Complete revascularization during index procedure or staged

### Adjunctive Therapy
- Aspirin + P2Y12 inhibitor (prasugrel or ticagrelor)
- Anticoagulation: UFH standard, bivalirudin alternative
- GP IIb/IIIa inhibitors: Bailout only
"""

# =============================================================================
# PULMONARY HYPERTENSION KNOWLEDGE (ESC 2022)
# =============================================================================

PULMONARY_HYPERTENSION_KNOWLEDGE = """# Pulmonary Hypertension Guidelines (ESC 2022)

## Hemodynamic Definition

Pulmonary Hypertension: mPAP >20 mmHg at rest

### Classification by Hemodynamics

| Type | PAWP | PVR |
|------|------|-----|
| Pre-capillary | <=15 mmHg | >2 WU |
| Isolated post-capillary (IpcPH) | >15 mmHg | <=2 WU |
| Combined pre/post-capillary (CpcPH) | >15 mmHg | >2 WU |

## Clinical Classification (5 Groups)

### Group 1: Pulmonary Arterial Hypertension (PAH)
- Idiopathic PAH
- Heritable PAH
- Drug/toxin-induced
- Associated PAH (CTD, HIV, portal hypertension, CHD)

### Group 2: PH due to Left Heart Disease
- HFpEF, HFrEF
- Valvular disease
- Most common cause of PH

### Group 3: PH due to Lung Disease/Hypoxia
- COPD
- ILD
- Sleep-disordered breathing
- Chronic high altitude

### Group 4: Chronic Thromboembolic PH (CTEPH)
- Unresolved PE leading to organized thrombi
- Potentially curable with pulmonary endarterectomy

### Group 5: Multifactorial/Unclear Mechanisms
- Hematologic disorders
- Systemic disorders
- Metabolic disorders

## PAH Risk Assessment

### Low Risk (<5% 1-year mortality)
- WHO FC I-II
- 6MWD >440m
- NT-proBNP <300 pg/mL
- RA area <18 cm2
- No pericardial effusion
- CI >=2.5 L/min/m2
- SvO2 >65%

### Intermediate Risk (5-20% 1-year mortality)
- WHO FC III
- 6MWD 165-440m
- NT-proBNP 300-1400 pg/mL

### High Risk (>20% 1-year mortality)
- WHO FC IV
- 6MWD <165m
- NT-proBNP >1400 pg/mL
- RA area >26 cm2
- Pericardial effusion present
- CI <2.0 L/min/m2
- SvO2 <60%

## PAH Treatment Algorithm

### General Measures
- Avoid pregnancy
- Vaccinations (influenza, pneumococcal, COVID-19)
- Supervised rehabilitation
- Psychosocial support

### Supportive Therapy
- Diuretics for RV failure/fluid retention
- Oxygen if hypoxemic
- Anticoagulation: Consider in IPAH (controversial)

### PAH-Specific Therapy

#### Calcium Channel Blockers
- Only for acute vasoreactivity positive patients
- High doses: nifedipine 120-240mg, diltiazem 240-720mg
- <10% of PAH patients are responders

#### Endothelin Receptor Antagonists (ERA)
- Ambrisentan, bosentan, macitentan
- Oral therapy
- Monitor liver function (bosentan)

#### PDE-5 Inhibitors
- Sildenafil, tadalafil
- Oral therapy
- Synergistic with ERA

#### Prostacyclin Pathway Agonists
- Epoprostenol (IV): Most potent, for severe PAH
- Treprostinil (IV, SC, inhaled, oral)
- Iloprost (inhaled)
- Selexipag (oral): IP receptor agonist

#### Soluble Guanylate Cyclase Stimulator
- Riociguat
- Also approved for CTEPH

### Treatment Strategy
- Low/intermediate risk: Initial combination therapy (ERA + PDE5i)
- High risk: Include parenteral prostacyclin
- Reassess at 3-6 months
- Escalate if not achieving low-risk profile

## CTEPH Management
- Lifelong anticoagulation
- Pulmonary endarterectomy (PEA): Potentially curative
- Balloon pulmonary angioplasty (BPA): If inoperable
- Riociguat: Medical therapy for inoperable/persistent PH
"""

# =============================================================================
# CARDIO-ONCOLOGY KNOWLEDGE (ESC 2022)
# =============================================================================

CARDIO_ONCOLOGY_KNOWLEDGE = """# Cardio-Oncology Guidelines (ESC 2022)

## Baseline CV Risk Assessment

### HFA-ICOS Risk Factors

#### Patient Factors
- Age >65 (or <18)
- Female sex
- Obesity (BMI >30)
- Smoking
- Hypertension
- Diabetes
- Hyperlipidemia
- Prior CV disease (HF, CAD, PAD, stroke)
- Prior cardiotoxic therapy

#### Cancer Treatment Factors
- Anthracycline dose
- Chest/mediastinal radiation
- Combination cardiotoxic therapies

### Risk Categories
- **Low risk**: 0 risk factors
- **Moderate risk**: 1-2 minor risk factors
- **High risk**: >= 3 risk factors OR prior CV disease OR prior cardiotoxicity
- **Very high risk**: LVEF <50% or symptomatic HF

## Cancer Therapy-Related Cardiac Dysfunction (CTRCD)

### Definition (2022)
- Symptomatic CTRCD: New cardiomyopathy + HF symptoms
- Asymptomatic CTRCD:
  - Severe: LVEF <40%
  - Moderate: LVEF 40-49% OR drop >=10% to <50%
  - Mild: LVEF >=50% + drop >=10% OR GLS drop >15%

### High-Risk Cancer Therapies

#### Anthracyclines (Type I - Irreversible)
- Doxorubicin, epirubicin, daunorubicin
- Dose-dependent risk
- >400 mg/m2 doxorubicin: high risk
- Subclinical damage may occur at any dose

#### HER2-Targeted Therapy (Type II - Often Reversible)
- Trastuzumab, pertuzumab
- Often reversible with drug cessation
- Higher risk if combined with anthracyclines

#### Immune Checkpoint Inhibitors
- Myocarditis: Rare but often fulminant
- May occur early in therapy
- PD-1/PD-L1 and CTLA-4 inhibitors

#### VEGF Inhibitors
- Hypertension (very common)
- Arterial thromboembolism
- QT prolongation (some agents)

#### Radiation
- Coronary artery disease (accelerated)
- Valvular disease
- Pericardial disease
- Cardiomyopathy

## Surveillance Protocols

### Anthracycline Therapy
| Risk | Before | During | After |
|------|--------|--------|-------|
| Low | Echo + ECG | Echo q3 months | Echo at 12 months |
| Moderate | Echo + ECG + biomarkers | Echo q2 months | Echo q6 months x2 years |
| High | Echo + ECG + biomarkers + cardiology | Echo q1-2 months | Echo q3-6 months x5 years |

### HER2-Targeted Therapy
- Echo q3 months during therapy
- More frequent if LVEF decline

### Immune Checkpoint Inhibitors
- Baseline ECG + troponin
- Weekly troponin x6 weeks
- Monitor for myocarditis symptoms

## Management of CTRCD

### Asymptomatic LVEF Decline
- Continue cancer therapy if LVEF >40% and drop <10%
- Hold if LVEF <40% or drop >=10%
- Start ACEi/ARB + beta-blocker
- Consider cardioprotection: dexrazoxane

### Symptomatic HF
- Standard HF therapy
- Multidisciplinary decision on cancer therapy continuation
- May need to discontinue cardiotoxic agent

### Cardioprotective Strategies
- Dexrazoxane: FDA-approved for anthracycline >300 mg/m2
- ACEi/beta-blocker: Some evidence for primary prevention in high-risk
- Statins: Possible benefit

## Specific Situations

### Trastuzumab + Anthracycline
- Highest risk combination
- Sequential preferred over concurrent
- Close monitoring essential

### Radiation + Anthracycline
- Additive cardiotoxicity
- Consider dose reduction
- Lifelong CV surveillance

## Long-Term Survivorship
- Cardiovascular disease is leading non-cancer cause of death in survivors
- Aggressive risk factor management
- Annual CV assessment for high-risk survivors
- Education on symptoms and lifestyle
"""

# =============================================================================
# PULMONARY EMBOLISM KNOWLEDGE (ESC 2019)
# =============================================================================

PULMONARY_EMBOLISM_KNOWLEDGE = """# Pulmonary Embolism Guidelines (ESC 2019)

## Clinical Probability Assessment

### Wells Score for PE

| Criteria | Points |
|----------|--------|
| Clinical signs/symptoms of DVT | 3.0 |
| PE is #1 diagnosis or equally likely | 3.0 |
| Heart rate > 100 bpm | 1.5 |
| Immobilization >= 3 days or surgery in past 4 weeks | 1.5 |
| Previous PE or DVT | 1.5 |
| Hemoptysis | 1.0 |
| Active malignancy (treatment within 6 months) | 1.0 |

#### Score Interpretation (Original)
- Low probability: <2 points
- Intermediate probability: 2-6 points
- High probability: >6 points

#### Score Interpretation (Simplified)
- PE unlikely: <=4 points
- PE likely: >4 points

### Revised Geneva Score

| Criteria | Original | Simplified |
|----------|----------|------------|
| Age > 65 | 1 | 1 |
| Previous PE or DVT | 3 | 1 |
| Surgery or fracture within 1 month | 2 | 1 |
| Active malignancy | 2 | 1 |
| Unilateral lower limb pain | 3 | 1 |
| Hemoptysis | 2 | 1 |
| Heart rate 75-94 | 3 | 1 |
| Heart rate >= 95 | 5 | 2 |
| Pain on leg palpation + unilateral edema | 4 | 1 |

## D-Dimer Testing

### Age-Adjusted D-Dimer
- Age <= 50: Standard cutoff (500 ng/mL)
- Age > 50: Cutoff = Age x 10 ng/mL
- Increases specificity without sacrificing sensitivity

### When D-Dimer is Useful
- Low or intermediate clinical probability
- NOT useful if high probability (proceed to imaging)

## Risk Stratification

### PESI Score (Pulmonary Embolism Severity Index)

| Variable | Points |
|----------|--------|
| Age | Age in years |
| Male sex | +10 |
| Cancer | +30 |
| Chronic heart failure | +10 |
| Chronic lung disease | +10 |
| Heart rate >= 110 | +20 |
| SBP < 100 mmHg | +30 |
| RR >= 30/min | +20 |
| Temperature < 36°C | +20 |
| Altered mental status | +60 |
| SpO2 < 90% | +20 |

#### PESI Risk Classes
| Class | Score | 30-day Mortality |
|-------|-------|------------------|
| I | <= 65 | 0-1.6% |
| II | 66-85 | 1.7-3.5% |
| III | 86-105 | 3.2-7.1% |
| IV | 106-125 | 4.0-11.4% |
| V | > 125 | 10.0-24.5% |

### Simplified PESI (sPESI)

| Variable | Points |
|----------|--------|
| Age > 80 | 1 |
| Cancer | 1 |
| Chronic cardiopulmonary disease | 1 |
| Heart rate >= 110 | 1 |
| SBP < 100 mmHg | 1 |
| SpO2 < 90% | 1 |

- Score = 0: Low risk (1% 30-day mortality)
- Score >= 1: High risk (10.9% 30-day mortality)

## Risk-Adapted Treatment

### High-Risk PE (Hemodynamically Unstable)
- Definition: SBP < 90 mmHg or drop >= 40 mmHg for > 15 min
- Treatment: Primary reperfusion (systemic thrombolysis or surgical embolectomy)
- Anticoagulation: UFH (allows rapid reversal if bleeding)

### Intermediate-High Risk PE
- Normotensive BUT:
  - PESI III-IV or sPESI >= 1
  - RV dysfunction on imaging
  - Elevated troponin
- Treatment: Hospitalize, monitor closely
- Consider rescue thrombolysis if deterioration

### Intermediate-Low Risk PE
- Normotensive, PESI III-IV or sPESI >= 1
- No RV dysfunction OR normal troponin
- Treatment: Hospitalize, anticoagulation

### Low-Risk PE
- PESI I-II or sPESI = 0
- No RV dysfunction, normal troponin
- Consider outpatient treatment if:
  - Reliable, compliant patient
  - Good social support
  - No bleeding risk
  - Can access follow-up

## Anticoagulation

### Initial Therapy
- DOACs preferred for most patients
- Apixaban or rivaroxaban: No lead-in parenteral needed
- Dabigatran or edoxaban: Require 5 days of parenteral first
- LMWH + VKA: Traditional approach

### Duration
| Scenario | Duration |
|----------|----------|
| Provoked (surgery, trauma) | 3 months |
| First unprovoked | At least 3 months, then reassess |
| Second unprovoked | Indefinite if low bleeding risk |
| Cancer-associated | LMWH or DOAC, often indefinite |

## Thrombolysis

### Absolute Contraindications
- Prior intracranial hemorrhage
- Ischemic stroke within 6 months
- CNS neoplasm
- Major trauma/surgery/head injury within 3 weeks
- GI bleeding within 1 month
- Active bleeding

### Regimens
- Alteplase: 100 mg over 2 hours (or 0.6 mg/kg over 15 min if arrest)
- Tenecteplase: Weight-based single bolus

## Special Situations

### Pregnancy
- LMWH is treatment of choice
- DOACs contraindicated
- Consider IVC filter if anticoagulation contraindicated

### Cancer
- LMWH or edoxaban/rivaroxaban
- Extended anticoagulation while cancer active

### Renal Impairment
- Apixaban or VKA if severe CKD
- Avoid edoxaban if CrCl > 95 mL/min
"""

# =============================================================================
# HYPERTENSION KNOWLEDGE (ESC 2024)
# =============================================================================

HYPERTENSION_KNOWLEDGE = """# Hypertension Guidelines (ESC 2024)

## Blood Pressure Classification

| Category | Systolic (mmHg) | Diastolic (mmHg) |
|----------|-----------------|------------------|
| Optimal | < 120 | < 80 |
| Normal | 120-129 | 80-84 |
| High-Normal | 130-139 | 85-89 |
| Grade 1 HTN | 140-159 | 90-99 |
| Grade 2 HTN | 160-179 | 100-109 |
| Grade 3 HTN | >= 180 | >= 110 |
| Isolated Systolic HTN | >= 140 | < 90 |

## BP Measurement

### Office BP
- Use automated oscillometric device
- Patient seated, relaxed for 5 minutes
- Arm supported at heart level
- Average of 2-3 readings
- Confirm with out-of-office measurements

### Out-of-Office BP
- **ABPM**: Preferred method
  - HTN: Daytime >= 135/85 or 24h >= 130/80
  - Measures nocturnal dipping
- **HBPM**: Alternative
  - HTN: Average >= 135/85
  - 7 consecutive days, morning and evening

### White-Coat vs Masked HTN
- White-coat: High office, normal out-of-office
- Masked: Normal office, high out-of-office
- Both require out-of-office confirmation

## CV Risk Stratification

### Risk Categories
- **Low-Moderate**: <5% 10-year CVD risk
- **High**: 5-10% risk or Grade 2 HTN
- **Very High**: >10% risk, established CVD, CKD stage 3+, diabetes with TOD

### Hypertension-Mediated Organ Damage (HMOD)
- LVH (echo or ECG)
- Microalbuminuria (30-300 mg/24h)
- eGFR 30-59 mL/min
- Carotid IMT > 0.9 mm or plaque
- PWV > 10 m/s
- ABI < 0.9
- Grade 3-4 retinopathy

## Treatment Thresholds

| Population | Office BP Threshold |
|------------|---------------------|
| Grade 1 HTN + low-moderate risk | >= 140/90 (after 3-6 months lifestyle) |
| Grade 1 HTN + high/very high risk | >= 140/90 (immediate) |
| Grade 2-3 HTN | >= 160/100 (immediate) |
| High-normal + very high risk | >= 130-139/85-89 (consider) |
| Age >= 80 | >= 160/90 |

## Treatment Targets

| Population | Target (mmHg) |
|------------|---------------|
| General (< 65 years) | < 130/80 (not < 120/70) |
| Age >= 65 | 130-139/70-79 |
| Diabetes | < 130/80 |
| CKD (diabetic) | < 130/80 |
| CKD (non-diabetic) | < 130/80 (tolerate < 120) |
| Post-stroke | < 130/80 |
| CAD | < 130/80 |

## Drug Classes

### First-Line Options (Single-Pill Combinations Preferred)
- ACE inhibitors (ACEi)
- Angiotensin receptor blockers (ARB)
- Calcium channel blockers (CCB)
- Thiazide-like diuretics

### Preferred Combinations
- ACEi/ARB + CCB
- ACEi/ARB + thiazide-like diuretic
- DO NOT combine ACEi + ARB

### Second-Line/Add-On
- Spironolactone 25-50 mg (resistant HTN)
- Beta-blockers (if compelling indication)
- Alpha-blockers
- Loop diuretics (if eGFR < 30 or volume overload)

## Treatment Algorithm

### Step 1: Initial Therapy
- Most patients: Start with dual combination
- Grade 1 HTN + low risk or frail elderly: May start monotherapy

### Step 2: Triple Combination
- If uncontrolled on dual therapy
- ACEi/ARB + CCB + thiazide-like diuretic

### Step 3: Resistant Hypertension
- Add spironolactone 25-50 mg
- If K+ > 4.5 or eGFR < 45: Consider other agents

### Step 4: Specialist Referral
- Consider secondary causes
- Device-based therapy trials

## Special Populations

### Diabetes
- Target < 130/80 if tolerated
- ACEi/ARB first-line (renoprotection)
- Consider SGLT2i for CV/renal benefit

### CKD
- Target < 130/80
- ACEi/ARB for proteinuria
- Loop diuretics if eGFR < 30
- Monitor K+ closely

### Heart Failure
- ACEi/ARB/ARNI + beta-blocker + diuretic
- Avoid non-DHP CCBs in HFrEF
- Target lowest tolerated BP

### CAD
- ACEi and beta-blocker for secondary prevention
- Avoid short-acting nifedipine
- Target < 130/80

### Pregnancy
- Labetalol, methyldopa, nifedipine are safe
- ACEi/ARB contraindicated
- Target < 140/90 (chronic HTN) or < 135/85 (gestational)

## Secondary Hypertension

### When to Suspect
- Young onset (< 30 years)
- Resistant hypertension
- Severe/malignant HTN
- Sudden worsening of previously controlled BP
- Suggestive clinical features

### Common Causes
- Primary aldosteronism: Hypokalemia, adrenal mass
- Renovascular: Resistant HTN, renal bruit, flash pulmonary edema
- Pheochromocytoma: Paroxysmal HTN, headaches, sweating
- Cushing's: Central obesity, striae, glucose intolerance
- OSA: Obesity, snoring, daytime somnolence

## Hypertensive Emergencies

### Definition
- Severely elevated BP + acute HMOD
- Requires immediate BP reduction

### Target Organs
- Brain: Encephalopathy, stroke
- Heart: ACS, acute HF, aortic dissection
- Kidney: Acute kidney injury
- Eyes: Papilledema, hemorrhages

### Management
- IV therapy preferred
- Reduce BP by 20-25% in first hour
- Then gradually to 160/100 in next 2-6 hours
- Then to normal over 24-48 hours
- Exception: Aortic dissection (SBP < 120 immediately)
"""

# =============================================================================
# CV PREVENTION KNOWLEDGE (ESC 2021)
# =============================================================================

CV_PREVENTION_KNOWLEDGE = """# CV Prevention Guidelines (ESC 2021)

## SCORE2 Risk Assessment

### What SCORE2 Predicts
- 10-year risk of fatal and non-fatal CV events
- MI, stroke, CV death
- For ages 40-69 years

### SCORE2-OP
- For ages >= 70 years
- Accounts for competing mortality risk

### Risk Factors in SCORE2
- Age
- Sex
- Smoking status
- Systolic blood pressure
- Non-HDL cholesterol (or total cholesterol)

### European Risk Regions
- **Low risk**: France, Spain, Belgium, Luxembourg
- **Moderate risk**: Germany, UK, Denmark, Finland, Norway, Sweden, Iceland
- **High risk**: Poland, Czech Republic, Hungary, Slovenia
- **Very high risk**: Lithuania, Latvia, Estonia, Russia, Ukraine, Romania, Bulgaria

## Risk Categories

| Category | Age < 50 | Age 50-69 | Age >= 70 |
|----------|----------|-----------|-----------|
| Low-Moderate | < 2.5% | < 5% | < 7.5% |
| High | 2.5-7.5% | 5-10% | 7.5-15% |
| Very High | >= 7.5% | >= 10% | >= 15% |

### Automatic Very High Risk
- Established ASCVD
- Diabetes with TOD or >= 3 risk factors or T1DM > 20 years
- Severe CKD (eGFR < 30)
- Familial hypercholesterolemia with ASCVD or risk factor

### Automatic High Risk
- Markedly elevated single risk factor:
  - TC > 8 mmol/L or LDL > 4.9 mmol/L
  - BP >= 180/110 mmHg
- Diabetes (not in very high risk)
- Moderate CKD (eGFR 30-59)
- Familial hypercholesterolemia without other risk factors

## LDL-C Targets

| Risk Category | LDL-C Target | Additional Goal |
|---------------|--------------|-----------------|
| Very High | < 1.4 mmol/L (55 mg/dL) | AND >= 50% reduction |
| High | < 1.8 mmol/L (70 mg/dL) | AND >= 50% reduction |
| Moderate | < 2.6 mmol/L (100 mg/dL) | - |
| Low | < 3.0 mmol/L (116 mg/dL) | - |

### Secondary Prevention
- Very high risk: < 1.4 mmol/L
- If second event within 2 years: Consider < 1.0 mmol/L

## Lipid-Lowering Therapy

### Statins
- First-line therapy
- High-intensity: Atorvastatin 40-80 mg, Rosuvastatin 20-40 mg
- Moderate-intensity: Atorvastatin 10-20 mg, Simvastatin 20-40 mg

### Ezetimibe
- Add if statin alone insufficient
- Reduces LDL by additional 15-20%

### PCSK9 Inhibitors
- Evolocumab, alirocumab
- If target not reached on max statin + ezetimibe
- Very high risk with recurrent events

### Bempedoic Acid
- For statin-intolerant patients
- Add to ezetimibe or other therapy

### Inclisiran
- siRNA therapy, twice yearly injection
- After statin + ezetimibe insufficient

## Other Targets

### Blood Pressure
- < 130/80 mmHg for most high-risk patients
- See Hypertension guidelines for details

### Glycemic Control
- HbA1c individualized (generally < 7%)
- SGLT2i and GLP-1RA for CV benefit

### Lifestyle
- Smoking cessation (most important)
- Mediterranean-style diet
- Physical activity: 150-300 min/week moderate
- Weight management: BMI 20-25 kg/m2
- Alcohol: < 100 g/week

## Antiplatelet Therapy

### Primary Prevention
- NOT routinely recommended
- May consider in high-risk diabetes (individualized)

### Secondary Prevention
- Aspirin 75-100 mg daily for all with ASCVD
- DAPT duration based on ischemic vs bleeding risk
- Consider adding low-dose rivaroxaban if high ischemic risk

## Diabetes and CV Risk

### Cardiovascular Protection
- SGLT2 inhibitors: CV and renal protection
  - Empagliflozin, dapagliflozin, canagliflozin
- GLP-1 receptor agonists: CV benefit
  - Liraglutide, semaglutide, dulaglutide

### Treatment Algorithm
1. Metformin (if tolerated, eGFR allows)
2. Add SGLT2i or GLP-1RA based on CV/renal profile
3. Individualize additional agents

## CKD and CV Risk

### eGFR Categories
- G3a: 45-59 (moderate decrease)
- G3b: 30-44 (moderate-severe decrease)
- G4: 15-29 (severe decrease)
- G5: < 15 (kidney failure)

### Management
- ACEi/ARB for proteinuria
- SGLT2i for renal/CV protection (eGFR > 20)
- Statins reduce CV events in CKD
- Avoid NSAIDs

## Imaging for Risk Reclassification

### When to Consider
- Intermediate risk by SCORE2
- Treatment decision uncertain

### Options
- Coronary artery calcium (CAC) score
  - CAC = 0: Low risk
  - CAC > 100 or > 75th percentile: Higher risk
- Carotid ultrasound (plaque detection)
- Femoral artery ultrasound
"""

# =============================================================================
# PERIPHERAL ARTERIAL DISEASE KNOWLEDGE (ESC 2024)
# =============================================================================

PERIPHERAL_ARTERIAL_DISEASE_KNOWLEDGE = """# Peripheral Arterial Disease Guidelines (ESC 2024)

## Ankle-Brachial Index (ABI)

### Measurement
- Highest ankle systolic pressure (PT or DP) / Highest arm systolic pressure
- Measure both legs

### Interpretation
| ABI | Interpretation |
|-----|----------------|
| > 1.40 | Non-compressible (calcification) |
| 1.00-1.40 | Normal |
| 0.91-0.99 | Borderline |
| 0.70-0.90 | Mild-moderate PAD |
| 0.50-0.69 | Moderate-severe PAD |
| 0.40-0.49 | Severe PAD |
| < 0.40 | Critical limb ischemia likely |

### If ABI > 1.40 (Non-Compressible)
- Use toe-brachial index (TBI)
- TBI < 0.70 is abnormal
- Or use pulse volume recording, Doppler waveforms

## PAD Classification

### Fontaine Classification
| Stage | Description |
|-------|-------------|
| I | Asymptomatic |
| IIa | Claudication > 200m |
| IIb | Claudication < 200m |
| III | Ischemic rest pain |
| IV | Ulceration or gangrene |

### Rutherford Classification
| Category | Description |
|----------|-------------|
| 0 | Asymptomatic |
| 1 | Mild claudication |
| 2 | Moderate claudication |
| 3 | Severe claudication |
| 4 | Ischemic rest pain |
| 5 | Minor tissue loss |
| 6 | Major tissue loss |

## Critical Limb Ischemia (CLI)

### Definition
- Rest pain requiring regular analgesia >= 2 weeks
- OR ulceration/gangrene attributed to PAD
- WITH objective evidence of PAD (ABI, toe pressure, transcutaneous oximetry)

### Management
- Urgent vascular referral (within 24-48 hours)
- Limb salvage revascularization
- Pain control
- Wound care
- High CV risk - aggressive secondary prevention

## PAD Treatment

### All Patients - CV Risk Modification
1. **Smoking cessation** - Most important modifiable factor
2. **Antiplatelet therapy** - Aspirin 75-100 mg or clopidogrel 75 mg
3. **Statin therapy** - LDL-C target < 1.4 mmol/L (55 mg/dL)
4. **BP control** - Target < 130/80 mmHg
5. **Diabetes management** - SGLT2i for CV/limb protection

### COMPASS Trial Implications
- Rivaroxaban 2.5 mg BID + aspirin
- Consider in high-risk PAD without high bleeding risk
- Reduces MACE and MALE (major adverse limb events)

### Claudication Management
1. **Supervised exercise therapy (SET)** - First-line
   - 30-45 min sessions, 3x/week, >= 12 weeks
   - Improves walking distance 100-200%
2. **Home-based exercise** - If SET unavailable
3. **Revascularization** - If lifestyle-limiting despite SET

### Revascularization Indications
- Critical limb ischemia
- Lifestyle-limiting claudication despite exercise
- Favorable anatomy and acceptable risk

## Abdominal Aortic Aneurysm (AAA)

### Definition
- Aortic diameter >= 3.0 cm
- Or >= 50% larger than adjacent normal aorta

### Screening
- One-time ultrasound for men aged 65+
- Consider for women with CV risk factors

### Size Categories

| Category | Diameter (cm) |
|----------|---------------|
| Small | 3.0-4.4 |
| Medium | 4.5-5.4 |
| Large | >= 5.5 (men) / >= 5.0 (women) |
| Very Large | >= 6.5 |

### Surveillance Intervals
| Size | Interval |
|------|----------|
| 3.0-3.9 cm | Every 3 years |
| 4.0-4.4 cm | Every 2 years |
| 4.5-5.4 cm | Every 6-12 months |
| >= 5.5 cm | Intervention threshold |

### Repair Thresholds
- Men: >= 5.5 cm (Class I)
- Women: >= 5.0 cm (earlier due to higher rupture risk)
- Rapid growth: >= 1 cm/year
- Symptomatic: Any size (urgent/emergent)

### Treatment Options
- **EVAR** (Endovascular repair): Lower perioperative mortality, requires lifelong surveillance
- **Open repair**: More durable, preferred in younger patients with suitable anatomy

### Medical Management (All AAA)
- Smoking cessation (slows growth)
- Statin therapy
- BP control
- Antiplatelet therapy for CV protection

## Carotid Stenosis

### Measurement
- NASCET criteria: (1 - stenosis diameter / distal ICA diameter) x 100%
- Duplex ultrasound is initial test

### Symptomatic Carotid Stenosis
- Definition: TIA or stroke referable to carotid territory
- **50-99% stenosis**: Revascularization recommended (Class I)
- **Within 14 days of symptoms**: Urgent intervention (highest benefit)

### Asymptomatic Carotid Stenosis
- **60-99% stenosis**: May consider revascularization in selected patients
- Best medical therapy alone is acceptable for most
- Consider revascularization if:
  - High-risk features (silent infarcts, progression)
  - Low procedural risk (< 3% stroke/death)
  - Life expectancy > 5 years

### CEA vs CAS
- CEA (Carotid endarterectomy): Preferred in most patients
- CAS (Carotid artery stenting): Alternative if unfavorable CEA anatomy
- Both require intensive medical therapy

## Multivascular Disease

### Definition
- PAD affecting >= 2 vascular beds
- Examples: Lower extremity PAD + carotid stenosis + CAD

### Implications
- Very high CV risk
- More aggressive risk factor control
- Consider intensified antithrombotic therapy
- Multidisciplinary management
"""

# =============================================================================
# SYNCOPE KNOWLEDGE (ESC 2018)
# =============================================================================

SYNCOPE_KNOWLEDGE = """# Syncope Guidelines (ESC 2018)

## Definition
- Transient loss of consciousness (TLOC)
- Due to cerebral hypoperfusion
- Rapid onset, short duration, spontaneous complete recovery

## Syncope Classification

### Reflex (Neurally-Mediated) Syncope
Most common type
- **Vasovagal**: Emotional trigger, prolonged standing, orthostatic stress
- **Situational**: Micturition, defecation, cough, swallowing
- **Carotid sinus syndrome**: Carotid sinus hypersensitivity

### Orthostatic Hypotension
- Primary autonomic failure (Parkinson's, MSA, pure autonomic failure)
- Secondary autonomic failure (diabetes, amyloid)
- Drug-induced (vasodilators, diuretics, antidepressants)
- Volume depletion

### Cardiac Syncope
Highest risk - requires urgent evaluation
- **Arrhythmic**:
  - Bradycardia (SND, AV block)
  - Tachycardia (VT, SVT with rapid rate)
  - Inherited syndromes (LQTS, Brugada)
- **Structural**:
  - Aortic stenosis
  - HCM
  - Cardiac masses
  - Pericardial disease
  - Pulmonary embolism
  - Aortic dissection

## Initial Evaluation

### Key Questions (History)
1. Circumstances before the event?
2. Prodromal symptoms (nausea, warmth, sweating)?
3. Position at onset (standing, sitting, supine)?
4. Witnessed observations (jerking, duration, color)?
5. Recovery characteristics (confusion, injuries)?
6. Cardiac history and family history of SCD?

### Physical Examination
- Orthostatic vital signs
- Cardiac examination (murmurs, S3, S4)
- Carotid examination (bruits, CSM if appropriate)
- Neurological examination

### 12-Lead ECG
Essential for all syncope patients.
High-risk ECG findings:
- Sustained VT or VF
- Sinus bradycardia < 40 bpm
- Sinus pause > 3 seconds
- Mobitz II or complete heart block
- Alternating LBBB/RBBB
- Long or short QT
- Brugada pattern
- Preexcitation
- Q waves suggesting MI
- ARVC pattern (epsilon waves, T inversion V1-V3)

## Risk Stratification

### High-Risk Features (Admission/Urgent Evaluation)
- **Major structural heart disease**
- **Heart failure**
- **Syncope during exertion**
- **Syncope while supine**
- **Palpitations immediately before syncope**
- **Family history of SCD < 40 years**
- **High-risk ECG abnormalities**
- **Severe anemia or electrolyte disturbance**

### Low-Risk Features
- Age < 40 without cardiac history
- Typical vasovagal prodrome
- Triggered by pain, fear, emotional stress
- Prolonged standing
- Occurred during or after meal
- No cardiac disease

### Risk Scores
- **San Francisco Syncope Rule**: CHF, Hct < 30%, abnormal ECG, SOB, SBP < 90
- **OESIL**: Age > 65, abnormal ECG, no prodrome, cardiac history
- **EGSYS**: Palpitations, ECG abnormality, syncope during effort, supine onset, prodromal symptoms

## Diagnostic Tests

### Echocardiography
- If cardiac disease known or suspected
- If high-risk clinical features
- If abnormal ECG

### ECG Monitoring
- If suspected arrhythmic syncope
- **Duration based on frequency**:
  - Daily: 24-48 hour Holter
  - Weekly: 7-14 day external monitor
  - Monthly or less: Implantable loop recorder (ILR)

### Tilt Table Testing
- Suspected reflex syncope when diagnosis uncertain
- Recurrent unexplained syncope
- Suspected orthostatic hypotension

### Electrophysiology Study
- If structural heart disease with suspected arrhythmic cause
- Bundle branch block with unexplained syncope
- NOT indicated for low-risk reflex syncope

### Carotid Sinus Massage
- Age > 40 with unexplained syncope
- Positive if asystole > 3 seconds or SBP drop > 50 mmHg

## Management by Type

### Vasovagal Syncope
1. **Education and reassurance**
   - Explain mechanism
   - Identify and avoid triggers
2. **Physical counterpressure maneuvers**
   - Leg crossing, hand grip, arm tensing
   - Abort or delay syncope
3. **Tilt training** - Progressively longer standing
4. **Medications** (limited evidence)
   - Midodrine (alpha-agonist)
   - Fludrocortisone (volume expansion)
5. **Pacing** - Only for cardioinhibitory syncope documented by ILR

### Orthostatic Hypotension
1. **Eliminate aggravating factors** - Reduce/stop offending drugs
2. **Volume expansion** - Salt and fluid intake 2-3 L/day
3. **Physical counterpressure**
4. **Abdominal binders, compression stockings**
5. **Sleep with head elevated**
6. **Medications**:
   - Midodrine
   - Fludrocortisone
   - Droxidopa (neurogenic OH)

### Cardiac Syncope
- **Bradycardia**: Pacemaker
- **Tachycardia**: ICD, ablation, antiarrhythmics
- **Structural**: Treat underlying condition (valve surgery, revascularization)

## Driving Recommendations

### Private Vehicle
- Reflex syncope (treated): 1-4 weeks
- Unexplained syncope: Until diagnosis/treatment
- Cardiac syncope: Until effective treatment established

### Professional Drivers
- More stringent restrictions
- Often permanently disqualified if high-risk cardiac cause
- Specialist evaluation required

## Key Clinical Pearls

1. **ECG is mandatory** - Can reveal high-risk diagnoses
2. **History is most important** - 50% diagnosed by history alone
3. **Cardiac syncope = high risk** - Always exclude
4. **ILR is valuable** - For recurrent unexplained syncope
5. **Young + typical vasovagal = low risk** - Reassurance often sufficient
6. **Syncope during exercise = always evaluate**
7. **Family history of SCD = always investigate**
"""

# =============================================================================
# TOOLS REFERENCE
# =============================================================================

TOOLS_REFERENCE = """# CardioCode MCP Tools Reference

## Clinical Scores (9 tools)

### calculate_cha2ds2_vasc
Calculate CHA2DS2-VASc stroke risk in atrial fibrillation.
```
Parameters:
- age (required): Patient age in years
- female (required): Female sex (true/false)
- chf: Congestive heart failure
- hypertension: Hypertension
- stroke_tia: Prior stroke/TIA
- vascular_disease: Vascular disease (MI, PAD)
- diabetes: Diabetes mellitus
```

### calculate_has_bled
Calculate HAS-BLED bleeding risk score.
```
Parameters:
- hypertension_uncontrolled: SBP >160
- abnormal_renal: Dialysis, transplant, Cr >2.26
- abnormal_liver: Cirrhosis or elevated LFTs
- stroke_history: Prior stroke
- bleeding_history: Prior major bleeding
- labile_inr: TTR <60%
- age_over_65: Age >65 years
- drugs_predisposing: Antiplatelets, NSAIDs
- alcohol_excess: >=8 drinks/week
```

### calculate_grace_score
Calculate GRACE score for ACS risk stratification.
```
Parameters:
- age (required): Age in years
- heart_rate (required): HR in bpm
- systolic_bp (required): SBP in mmHg
- creatinine (required): Creatinine in mg/dL
- killip_class: Killip class 1-4
- cardiac_arrest: Arrest at admission
- st_deviation: ST changes
- elevated_troponin: Positive troponin
```

### calculate_wells_pe
Calculate Wells score for PE probability.
```
Parameters:
- clinical_signs_dvt: Signs/symptoms of DVT
- pe_most_likely: PE is #1 diagnosis
- heart_rate_above_100: HR >100
- immobilization_surgery: Recent immobilization
- previous_pe_dvt: Prior PE/DVT
- hemoptysis: Hemoptysis present
- malignancy: Active malignancy
```

### calculate_hcm_scd_risk
Calculate 5-year SCD risk in HCM.
```
Parameters:
- age (required): Age 16-80
- max_wall_thickness (required): Max LV wall thickness (mm)
- la_diameter (required): LA diameter (mm)
- max_lvot_gradient (required): Max LVOT gradient (mmHg)
- family_history_scd: Family SCD <40y
- nsvt: NSVT on Holter
- unexplained_syncope: Unexplained syncope
```

## Heart Failure Tools (2 tools)

### get_hf_recommendations
Get HF treatment recommendations per ESC 2021.
```
Parameters:
- lvef (required): LV ejection fraction (%)
- nyha_class (required): NYHA class 1-4
- age: Patient age
- has_af: Atrial fibrillation
- has_cad: Coronary artery disease
- has_diabetes: Diabetes mellitus
- has_ckd: Chronic kidney disease
```

### assess_icd_indication
Assess ICD indication for SCD prevention.
```
Parameters:
- lvef (required): LVEF (%)
- nyha_class (required): NYHA class
- etiology: ischemic, non_ischemic, hcm, arvc
- prior_vf_vt: Prior VF/VT
- syncope: Unexplained syncope
- days_post_mi: Days since MI
```

## Arrhythmia Tools (1 tool)

### get_vt_management
Get VT management recommendations.
```
Parameters:
- vt_type: monomorphic, polymorphic, electrical_storm, nsvt, idiopathic
- hemodynamically_stable: Stable (true/false)
- has_structural_heart_disease: Structural heart disease
- lvef: LVEF (%)
```

## Pulmonary Hypertension Tools (1 tool)

### assess_pulmonary_hypertension
Assess and classify pulmonary hypertension.
```
Parameters:
- who_fc: WHO functional class 1-4
- six_mwd: 6-minute walk distance (m)
- nt_pro_bnp: NT-proBNP (pg/mL)
- mpap: Mean PAP (mmHg)
- pawp: PAWP (mmHg)
- pvr: PVR (Wood units)
- has_left_heart_disease: Left heart disease
- has_lung_disease: Lung disease
- has_chronic_pe: Chronic PE
```

## Cardio-Oncology Tools (2 tools)

### assess_cardio_oncology_risk
Assess CV risk before cancer therapy.
```
Parameters:
- age (required): Patient age
- planned_therapy (required): anthracycline, her2, checkpoint_inhibitor, vegf_inhibitor
- lvef: Baseline LVEF
- prior_anthracycline: Prior anthracycline
- prior_anthracycline_dose: Cumulative dose (mg/m2)
- prior_chest_radiation: Prior chest RT
- heart_failure: HF history
- hypertension: HTN
- diabetes: DM
- coronary_artery_disease: CAD
```

### manage_ctrcd
Manage cancer therapy-related cardiac dysfunction.
```
Parameters:
- lvef_current (required): Current LVEF (%)
- lvef_baseline: Baseline LVEF (%)
- symptomatic: HF symptoms present
- cancer_therapy: Type of therapy
```

## Valvular Heart Disease Tools (2 tools)

### assess_aortic_stenosis
Assess AS severity per ESC 2021.
```
Parameters:
- peak_velocity (required): Peak Vmax (m/s)
- mean_gradient (required): Mean gradient (mmHg)
- ava (required): AVA (cm2)
- lvef: LVEF (%)
- stroke_volume_index: SVI (mL/m2)
```

### assess_mitral_regurgitation
Assess MR severity per ESC 2021.
```
Parameters:
- eroa (required): EROA (mm2)
- regurgitant_volume (required): RegVol (mL)
- vena_contracta: VC width (mm)
- etiology: primary or secondary
```

## Coronary Syndromes Tools (2 tools)

### calculate_ptp
Calculate pre-test probability of CAD.
```
Parameters:
- age (required): Patient age
- sex (required): male or female
- chest_pain_type (required): typical_angina, atypical_angina, non_anginal
```

### calculate_nste_grace
Calculate GRACE for NSTE-ACS with timing.
```
Parameters:
- age (required): Age in years
- heart_rate (required): HR in bpm
- systolic_bp (required): SBP in mmHg
- creatinine (required): Creatinine (mg/dL)
- killip_class: Killip class 1-4
- cardiac_arrest: Arrest at admission
- st_deviation: ST changes
- elevated_troponin: Positive troponin
```

## Pulmonary Embolism Tools (4 tools)

### calculate_pesi
Calculate PESI score for 30-day mortality risk.
```
Parameters:
- age (required): Patient age
- male: Male sex
- cancer: Active cancer
- heart_failure: Chronic HF
- chronic_lung_disease: Chronic lung disease
- heart_rate_110_plus: HR >= 110
- systolic_bp_below_100: SBP < 100
- respiratory_rate_30_plus: RR >= 30
- temperature_below_36: Temp < 36°C
- altered_mental_status: AMS
- o2_saturation_below_90: SpO2 < 90%
```

### calculate_spesi
Calculate Simplified PESI score.
```
Parameters:
- age_over_80: Age > 80
- cancer: Active cancer
- chronic_cardiopulmonary_disease: Chronic cardiopulmonary disease
- pulse_over_110: HR >= 110
- systolic_bp_under_100: SBP < 100
- o2_saturation_under_90: SpO2 < 90%
```

### calculate_geneva_pe
Calculate Revised Geneva Score for PE probability.
```
Parameters:
- age_over_65: Age > 65
- previous_pe_dvt: Prior PE/DVT
- surgery_fracture_past_month: Recent surgery/fracture
- active_cancer: Active malignancy
- unilateral_leg_pain: Unilateral leg pain
- hemoptysis: Hemoptysis
- heart_rate: Heart rate (determines 75-94 vs >=95)
- dvt_signs: Pain on palpation + edema
- simplified: Use simplified version
```

### calculate_age_adjusted_ddimer
Calculate age-adjusted D-dimer cutoff.
```
Parameters:
- age (required): Patient age
- baseline_cutoff: Standard cutoff (default 500)
```

## Hypertension Tools (2 tools)

### classify_blood_pressure
Classify BP per ESC 2024.
```
Parameters:
- systolic (required): SBP in mmHg
- diastolic (required): DBP in mmHg
```

### assess_hypertension_risk
Assess CV risk in hypertension.
```
Parameters:
- systolic (required): SBP
- diastolic (required): DBP
- age (required): Patient age
- male: Male sex
- smoking: Current smoker
- diabetes: Diabetes
- dyslipidemia: Dyslipidemia
- obesity: BMI >= 30
- family_history_cvd: Family CVD history
- lvh: LVH on echo/ECG
- ckd: CKD stage 3+
- established_cvd: Established CVD
```

## CV Prevention Tools (2 tools)

### calculate_score2
Calculate SCORE2 10-year CV risk.
```
Parameters:
- age (required): Age 40-69
- sex (required): male or female
- smoking: Current smoker
- systolic_bp: SBP in mmHg
- non_hdl_cholesterol: Non-HDL (mmol/L)
- region: low, moderate, high, very_high
```

### get_lipid_targets
Get LDL-C targets by risk level.
```
Parameters:
- risk_level (required): low_to_moderate, high, very_high
```

## Peripheral Arterial Disease Tools (2 tools)

### calculate_abi
Calculate Ankle-Brachial Index.
```
Parameters:
- ankle_systolic_right: Right ankle SBP
- ankle_systolic_left: Left ankle SBP
- brachial_systolic: Arm SBP
```

### assess_aaa
Assess AAA management.
```
Parameters:
- diameter_cm (required): AAA diameter
- male: Male patient
- growth_rate_cm_year: Growth rate
- symptomatic: Symptomatic AAA
```

## Syncope Tools (2 tools)

### assess_syncope_risk
Risk stratify syncope (ESC 2018).
```
Parameters:
- age (required): Patient age
- known_heart_disease: Structural heart disease
- heart_failure: Heart failure
- abnormal_ecg: ECG abnormalities
- syncope_during_exertion: Exertional syncope
- syncope_supine: Supine syncope
- palpitations_before: Pre-syncope palpitations
- family_history_scd: Family SCD
- systolic_bp: SBP
- heart_rate: HR
```

### classify_syncope
Classify syncope etiology.
```
Parameters:
- prodrome_autonomic: Autonomic prodrome
- trigger_standing: Triggered by standing
- trigger_emotion_pain: Triggered by emotion/pain
- trigger_situational: Situational trigger
- exertional: Exertional
- supine_onset: Supine onset
- palpitations_before: Pre-syncope palpitations
- known_heart_disease: Structural heart disease
- abnormal_ecg: Abnormal ECG
```

## PDF Management Tools (5 tools)

### check_new_pdfs
Check for new guideline PDFs.

### get_pdf_status
Get status of all PDFs.

### extract_pdf_recommendations
Generate extraction prompts.

### get_pdf_notifications
Get PDF detection notifications.

### acknowledge_pdf_notification
Acknowledge notification.
"""

# =============================================================================
# COMPLETE KNOWLEDGE BASE
# =============================================================================

CARDIOCODE_KNOWLEDGE = f"""# CardioCode Complete Knowledge Base

## Overview

CardioCode is a comprehensive cardiology clinical decision support system encoding ESC Guidelines (2018-2024) as executable logic. This knowledge base contains all guideline content implemented in CardioCode.

## Guidelines Included

1. **Heart Failure** (ESC 2021) - HFrEF/HFmrEF/HFpEF management
2. **Atrial Fibrillation** (ESC 2020/2024) - Stroke prevention, rate/rhythm control
3. **Ventricular Arrhythmias** (ESC 2022) - VT management, SCD prevention
4. **Valvular Heart Disease** (ESC 2021) - AS, MR, AR assessment
5. **Chronic Coronary Syndromes** (ESC 2019) - Pre-test probability
6. **NSTE-ACS** (ESC 2020) - GRACE score, invasive timing
7. **STEMI** (ESC 2023) - Reperfusion timing
8. **Pulmonary Hypertension** (ESC 2022) - Classification, PAH treatment
9. **Cardio-Oncology** (ESC 2022) - CV risk assessment, CTRCD
10. **Pulmonary Embolism** (ESC 2019) - Wells, Geneva, PESI, treatment
11. **Hypertension** (ESC 2024) - BP classification, CV risk, targets
12. **CV Prevention** (ESC 2021) - SCORE2, lipid targets, lifestyle
13. **Peripheral Arterial Disease** (ESC 2024) - ABI, PAD, AAA, carotid
14. **Syncope** (ESC 2018) - Classification, risk stratification, management

## Available Tools

CardioCode provides 32 MCP tools for clinical decision support:
- 9 clinical risk calculators
- 23 guideline-based assessment tools

---

{HEART_FAILURE_KNOWLEDGE}

---

{ATRIAL_FIBRILLATION_KNOWLEDGE}

---

{VENTRICULAR_ARRHYTHMIAS_KNOWLEDGE}

---

{VALVULAR_DISEASE_KNOWLEDGE}

---

{CORONARY_SYNDROMES_KNOWLEDGE}

---

{PULMONARY_HYPERTENSION_KNOWLEDGE}

---

{CARDIO_ONCOLOGY_KNOWLEDGE}

---

{PULMONARY_EMBOLISM_KNOWLEDGE}

---

{HYPERTENSION_KNOWLEDGE}

---

{CV_PREVENTION_KNOWLEDGE}

---

{PERIPHERAL_ARTERIAL_DISEASE_KNOWLEDGE}

---

{SYNCOPE_KNOWLEDGE}

---

{TOOLS_REFERENCE}

---

## Evidence Classification

### Classes of Recommendation
- **Class I**: Is recommended (strong evidence/agreement)
- **Class IIa**: Should be considered (moderate evidence)
- **Class IIb**: May be considered (weak evidence)
- **Class III**: Is not recommended (harmful or no benefit)

### Levels of Evidence
- **Level A**: Multiple RCTs or meta-analyses
- **Level B**: Single RCT or large non-randomized studies
- **Level C**: Expert consensus or small studies

## Disclaimer

CardioCode is a clinical decision support tool. All recommendations should be validated by qualified healthcare professionals. Individual patient circumstances may require deviation from guideline recommendations.

For the most current guidelines, consult:
- European Society of Cardiology: https://www.escardio.org/Guidelines
- Source PDFs available in the source_pdfs directory
"""


def get_guideline_summaries() -> dict:
    """Return summary information about each guideline."""
    return {
        "heart_failure": {
            "name": "ESC Heart Failure Guidelines 2021",
            "key_topics": ["HFrEF", "HFmrEF", "HFpEF", "GDMT", "ICD/CRT"],
            "tools": ["get_hf_recommendations", "assess_icd_indication"],
        },
        "atrial_fibrillation": {
            "name": "ESC Atrial Fibrillation Guidelines 2020/2024",
            "key_topics": ["CHA2DS2-VASc", "HAS-BLED", "Anticoagulation", "Rate/Rhythm Control"],
            "tools": ["calculate_cha2ds2_vasc", "calculate_has_bled"],
        },
        "ventricular_arrhythmias": {
            "name": "ESC VA/SCD Guidelines 2022",
            "key_topics": ["VT Management", "ICD Indication", "HCM-SCD Risk"],
            "tools": ["get_vt_management", "calculate_hcm_scd_risk", "assess_icd_indication"],
        },
        "valvular_disease": {
            "name": "ESC VHD Guidelines 2021",
            "key_topics": ["Aortic Stenosis", "Mitral Regurgitation", "Intervention Timing"],
            "tools": ["assess_aortic_stenosis", "assess_mitral_regurgitation"],
        },
        "coronary_syndromes": {
            "name": "ESC CCS/NSTE-ACS Guidelines 2019-2020",
            "key_topics": ["Pre-test Probability", "GRACE Score", "Invasive Strategy"],
            "tools": ["calculate_ptp", "calculate_nste_grace", "calculate_grace_score"],
        },
        "pulmonary_hypertension": {
            "name": "ESC/ERS PH Guidelines 2022",
            "key_topics": ["PH Classification", "PAH Risk", "Treatment Algorithm"],
            "tools": ["assess_pulmonary_hypertension"],
        },
        "cardio_oncology": {
            "name": "ESC Cardio-Oncology Guidelines 2022",
            "key_topics": ["Baseline Risk", "CTRCD", "Surveillance"],
            "tools": ["assess_cardio_oncology_risk", "manage_ctrcd"],
        },
        "pulmonary_embolism": {
            "name": "ESC Pulmonary Embolism Guidelines 2019",
            "key_topics": ["Wells Score", "Geneva Score", "PESI/sPESI", "Risk Stratification", "Anticoagulation"],
            "tools": ["calculate_wells_pe", "calculate_pesi", "calculate_spesi", "calculate_geneva_pe", "calculate_age_adjusted_ddimer"],
        },
        "hypertension": {
            "name": "ESC Hypertension Guidelines 2024",
            "key_topics": ["BP Classification", "CV Risk", "Treatment Targets", "Drug Classes"],
            "tools": ["classify_blood_pressure", "assess_hypertension_risk"],
        },
        "cv_prevention": {
            "name": "ESC CV Prevention Guidelines 2021",
            "key_topics": ["SCORE2", "Risk Categories", "LDL Targets", "Lifestyle"],
            "tools": ["calculate_score2", "get_lipid_targets"],
        },
        "peripheral_arterial": {
            "name": "ESC Peripheral Arterial Disease Guidelines 2024",
            "key_topics": ["ABI", "PAD Classification", "AAA Surveillance", "Carotid Stenosis"],
            "tools": ["calculate_abi", "assess_aaa"],
        },
        "syncope": {
            "name": "ESC Syncope Guidelines 2018",
            "key_topics": ["Classification", "Risk Stratification", "Reflex Syncope", "Cardiac Syncope"],
            "tools": ["assess_syncope_risk", "classify_syncope"],
        },
    }
