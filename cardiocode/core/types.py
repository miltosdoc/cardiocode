"""
Core clinical data types for CardioCode.

These types represent the fundamental clinical entities used across all guidelines.
They are designed to be:
1. Strongly typed for validation
2. Interoperable with common EHR data formats
3. Extensible for specific guideline needs
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Optional, List, Dict, Any, Set
from decimal import Decimal


class Sex(Enum):
    """Biological sex for clinical calculations."""
    MALE = "male"
    FEMALE = "female"
    

class NYHAClass(Enum):
    """NYHA Functional Classification for Heart Failure."""
    I = 1    # No limitation of physical activity
    II = 2   # Slight limitation of physical activity
    III = 3  # Marked limitation of physical activity
    IV = 4   # Unable to carry on any physical activity without discomfort
    
    @property
    def description(self) -> str:
        descriptions = {
            1: "No limitation of physical activity. Ordinary physical activity does not cause undue fatigue, palpitation, dyspnea.",
            2: "Slight limitation of physical activity. Comfortable at rest. Ordinary physical activity results in fatigue, palpitation, dyspnea.",
            3: "Marked limitation of physical activity. Comfortable at rest. Less than ordinary activity causes fatigue, palpitation, or dyspnea.",
            4: "Unable to carry on any physical activity without discomfort. Symptoms of heart failure at rest. If any physical activity is undertaken, discomfort increases.",
        }
        return descriptions[self.value]


class RhythmType(Enum):
    """Cardiac rhythm classification."""
    SINUS = "sinus_rhythm"
    ATRIAL_FIBRILLATION = "atrial_fibrillation"
    ATRIAL_FLUTTER = "atrial_flutter"
    PACED = "paced"
    JUNCTIONAL = "junctional"
    VENTRICULAR_TACHYCARDIA = "ventricular_tachycardia"
    VENTRICULAR_FIBRILLATION = "ventricular_fibrillation"
    OTHER = "other"


class AFType(Enum):
    """Atrial Fibrillation classification per ESC 2020."""
    FIRST_DIAGNOSED = "first_diagnosed"  # First episode, regardless of duration
    PAROXYSMAL = "paroxysmal"            # Self-terminating, usually <7 days
    PERSISTENT = "persistent"             # >7 days or requiring cardioversion
    LONG_STANDING_PERSISTENT = "long_standing_persistent"  # >1 year when rhythm control adopted
    PERMANENT = "permanent"               # AF accepted by patient and physician


class ValveDisease(Enum):
    """Valvular heart disease types."""
    AORTIC_STENOSIS = "aortic_stenosis"
    AORTIC_REGURGITATION = "aortic_regurgitation"
    MITRAL_STENOSIS = "mitral_stenosis"
    MITRAL_REGURGITATION = "mitral_regurgitation"
    TRICUSPID_REGURGITATION = "tricuspid_regurgitation"
    TRICUSPID_STENOSIS = "tricuspid_stenosis"
    PULMONARY_STENOSIS = "pulmonary_stenosis"
    PULMONARY_REGURGITATION = "pulmonary_regurgitation"


class ValveSeverity(Enum):
    """Valve disease severity grading."""
    MILD = "mild"
    MODERATE = "moderate"
    MODERATE_SEVERE = "moderate_severe"
    SEVERE = "severe"


@dataclass
class VitalSigns:
    """
    Vital signs measurement.
    
    All measurements should be from a single point in time when possible.
    """
    heart_rate: Optional[int] = None          # bpm
    systolic_bp: Optional[int] = None         # mmHg
    diastolic_bp: Optional[int] = None        # mmHg
    respiratory_rate: Optional[int] = None    # breaths/min
    oxygen_saturation: Optional[float] = None # SpO2 %
    temperature: Optional[float] = None       # Celsius
    weight: Optional[float] = None            # kg
    height: Optional[float] = None            # cm
    measured_at: Optional[datetime] = None
    
    @property
    def bmi(self) -> Optional[float]:
        """Calculate BMI if height and weight available."""
        if self.weight and self.height and self.height > 0:
            height_m = self.height / 100
            return round(self.weight / (height_m ** 2), 1)
        return None
    
    @property
    def map(self) -> Optional[float]:
        """Calculate Mean Arterial Pressure."""
        if self.systolic_bp and self.diastolic_bp:
            return round(self.diastolic_bp + (self.systolic_bp - self.diastolic_bp) / 3, 1)
        return None
    
    @property
    def pulse_pressure(self) -> Optional[int]:
        """Calculate pulse pressure."""
        if self.systolic_bp and self.diastolic_bp:
            return self.systolic_bp - self.diastolic_bp
        return None


@dataclass
class LabValues:
    """
    Laboratory values relevant to cardiology.
    
    All values should include units as specified. Reference ranges may vary by lab.
    """
    # Renal function
    creatinine: Optional[float] = None           # mg/dL
    creatinine_umol: Optional[float] = None      # umol/L (European)
    egfr: Optional[float] = None                 # mL/min/1.73m2
    bun: Optional[float] = None                  # mg/dL
    
    # Electrolytes
    potassium: Optional[float] = None            # mEq/L
    sodium: Optional[float] = None               # mEq/L
    magnesium: Optional[float] = None            # mg/dL
    calcium: Optional[float] = None              # mg/dL
    
    # Cardiac biomarkers
    troponin_t: Optional[float] = None           # ng/L (high-sensitivity)
    troponin_i: Optional[float] = None           # ng/L (high-sensitivity)
    bnp: Optional[float] = None                  # pg/mL
    nt_pro_bnp: Optional[float] = None           # pg/mL
    
    # Lipids
    total_cholesterol: Optional[float] = None    # mg/dL
    ldl: Optional[float] = None                  # mg/dL
    hdl: Optional[float] = None                  # mg/dL
    triglycerides: Optional[float] = None        # mg/dL
    lp_a: Optional[float] = None                 # nmol/L
    
    # Coagulation
    inr: Optional[float] = None
    ptt: Optional[float] = None                  # seconds
    pt: Optional[float] = None                   # seconds
    d_dimer: Optional[float] = None              # ng/mL
    
    # Hematology
    hemoglobin: Optional[float] = None           # g/dL
    hematocrit: Optional[float] = None           # %
    platelets: Optional[int] = None              # x10^9/L
    wbc: Optional[float] = None                  # x10^9/L
    
    # Metabolic
    glucose: Optional[float] = None              # mg/dL
    hba1c: Optional[float] = None                # %
    
    # Liver
    ast: Optional[float] = None                  # U/L
    alt: Optional[float] = None                  # U/L
    albumin: Optional[float] = None              # g/dL
    bilirubin: Optional[float] = None            # mg/dL
    
    # Thyroid
    tsh: Optional[float] = None                  # mIU/L
    free_t4: Optional[float] = None              # ng/dL
    
    # Iron studies
    ferritin: Optional[float] = None             # ng/mL
    iron: Optional[float] = None                 # mcg/dL
    tibc: Optional[float] = None                 # mcg/dL
    transferrin_sat: Optional[float] = None      # %
    
    # Inflammatory markers
    crp: Optional[float] = None                  # mg/L
    esr: Optional[float] = None                  # mm/hr
    
    measured_at: Optional[datetime] = None
    
    def convert_creatinine_to_umol(self) -> Optional[float]:
        """Convert creatinine from mg/dL to umol/L."""
        if self.creatinine:
            return round(self.creatinine * 88.4, 1)
        return self.creatinine_umol


@dataclass 
class EchoFindings:
    """
    Echocardiography findings.
    
    Based on standard echocardiographic measurements per ASE/EACVI guidelines.
    """
    # Left ventricle
    lvef: Optional[float] = None                  # % (biplane Simpson's preferred)
    lvef_method: Optional[str] = None             # "simpson_biplane", "visual", "3d"
    lvidd: Optional[float] = None                 # mm (LV internal diameter, diastole)
    lvids: Optional[float] = None                 # mm (LV internal diameter, systole)
    lv_mass_index: Optional[float] = None         # g/m2
    gls: Optional[float] = None                   # % Global Longitudinal Strain (negative = normal)
    
    # Left atrium
    la_volume_index: Optional[float] = None       # mL/m2
    la_diameter: Optional[float] = None           # mm
    
    # Right ventricle
    tapse: Optional[float] = None                 # mm (Tricuspid Annular Plane Systolic Excursion)
    rv_s_prime: Optional[float] = None            # cm/s
    rv_fac: Optional[float] = None                # % Fractional Area Change
    rvsp: Optional[float] = None                  # mmHg (RV systolic pressure estimate)
    
    # Right atrium
    ra_pressure: Optional[int] = None             # mmHg (estimated from IVC)
    ra_area: Optional[float] = None               # cm2
    
    # Valves
    aortic_valve_area: Optional[float] = None     # cm2
    aortic_mean_gradient: Optional[float] = None  # mmHg
    aortic_peak_velocity: Optional[float] = None  # m/s
    aortic_regurgitation: Optional[ValveSeverity] = None
    
    mitral_valve_area: Optional[float] = None     # cm2
    mitral_mean_gradient: Optional[float] = None  # mmHg
    mitral_regurgitation: Optional[ValveSeverity] = None
    mitral_e_velocity: Optional[float] = None     # cm/s
    mitral_a_velocity: Optional[float] = None     # cm/s
    e_e_prime_ratio: Optional[float] = None       # E/e' ratio
    
    tricuspid_regurgitation: Optional[ValveSeverity] = None
    tricuspid_regurgitation_velocity: Optional[float] = None  # m/s
    
    # Pericardium
    pericardial_effusion: Optional[str] = None    # "none", "trivial", "small", "moderate", "large"
    
    # Other
    wall_motion_abnormalities: Optional[List[str]] = None
    ivc_diameter: Optional[float] = None          # mm
    ivc_collapsibility: Optional[float] = None    # %
    
    study_date: Optional[date] = None
    
    @property
    def lv_dysfunction_category(self) -> Optional[str]:
        """Categorize LV dysfunction per ESC guidelines."""
        if self.lvef is None:
            return None
        if self.lvef >= 50:
            return "preserved"  # HFpEF
        if self.lvef >= 41:
            return "mildly_reduced"  # HFmrEF
        return "reduced"  # HFrEF


@dataclass
class ECGFindings:
    """
    Electrocardiogram findings.
    """
    rhythm: RhythmType = RhythmType.SINUS
    heart_rate: Optional[int] = None              # bpm
    pr_interval: Optional[int] = None             # ms
    qrs_duration: Optional[int] = None            # ms
    qtc: Optional[int] = None                     # ms (corrected QT)
    qt_formula: Optional[str] = None              # "bazett", "fridericia"
    axis: Optional[int] = None                    # degrees
    
    # Conduction
    lbbb: bool = False                            # Left bundle branch block
    rbbb: bool = False                            # Right bundle branch block
    first_degree_avb: bool = False
    second_degree_avb: Optional[str] = None       # "mobitz_1", "mobitz_2"
    third_degree_avb: bool = False
    
    # Ischemia/Infarction
    st_elevation: Optional[List[str]] = None      # Leads with ST elevation
    st_depression: Optional[List[str]] = None     # Leads with ST depression
    t_wave_inversion: Optional[List[str]] = None  # Leads with T inversion
    pathological_q_waves: Optional[List[str]] = None
    
    # Hypertrophy
    lvh_voltage_criteria: bool = False
    rvh: bool = False
    
    # Arrhythmia details
    af_present: bool = False
    aflutter_present: bool = False
    pvc_count: Optional[int] = None               # Per recording period
    pac_count: Optional[int] = None
    
    study_date: Optional[date] = None


@dataclass
class Diagnosis:
    """
    Clinical diagnosis with ICD-10 mapping.
    """
    name: str
    icd10_code: Optional[str] = None
    diagnosed_date: Optional[date] = None
    is_active: bool = True
    severity: Optional[str] = None
    notes: Optional[str] = None
    
    # Common cardiology diagnoses with ICD-10 codes
    COMMON_DIAGNOSES: Dict[str, str] = field(default_factory=lambda: {
        "heart_failure": "I50.9",
        "hfref": "I50.2",
        "hfpef": "I50.3", 
        "hfmref": "I50.4",
        "atrial_fibrillation": "I48.91",
        "atrial_flutter": "I48.92",
        "hypertension": "I10",
        "coronary_artery_disease": "I25.10",
        "nstemi": "I21.4",
        "stemi": "I21.3",
        "unstable_angina": "I20.0",
        "stable_angina": "I20.9",
        "aortic_stenosis": "I35.0",
        "aortic_regurgitation": "I35.1",
        "mitral_regurgitation": "I34.0",
        "mitral_stenosis": "I34.2",
        "pulmonary_hypertension": "I27.0",
        "ventricular_tachycardia": "I47.2",
        "type_2_diabetes": "E11.9",
        "ckd_stage_3": "N18.3",
        "ckd_stage_4": "N18.4",
        "ckd_stage_5": "N18.5",
        "stroke": "I63.9",
        "tia": "G45.9",
        "peripheral_artery_disease": "I73.9",
        "dyslipidemia": "E78.5",
        "obesity": "E66.9",
    })


@dataclass
class Medication:
    """
    Medication with dosing and classification.
    """
    name: str
    generic_name: Optional[str] = None
    drug_class: Optional[str] = None
    dose: Optional[str] = None                    # e.g., "5 mg"
    frequency: Optional[str] = None               # e.g., "once daily"
    route: str = "oral"                           # "oral", "iv", "sc", "transdermal"
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_active: bool = True
    indication: Optional[str] = None
    prescriber: Optional[str] = None
    
    # Cardiology drug classes
    DRUG_CLASSES: Dict[str, List[str]] = field(default_factory=lambda: {
        "acei": ["lisinopril", "enalapril", "ramipril", "perindopril", "captopril", "quinapril", "benazepril", "fosinopril", "trandolapril"],
        "arb": ["losartan", "valsartan", "candesartan", "irbesartan", "olmesartan", "telmisartan", "azilsartan"],
        "arni": ["sacubitril/valsartan", "entresto"],
        "beta_blocker": ["metoprolol", "carvedilol", "bisoprolol", "nebivolol", "atenolol", "propranolol", "nadolol", "labetalol"],
        "mra": ["spironolactone", "eplerenone", "finerenone"],
        "sglt2i": ["empagliflozin", "dapagliflozin", "canagliflozin", "ertugliflozin", "sotagliflozin"],
        "loop_diuretic": ["furosemide", "bumetanide", "torsemide", "ethacrynic acid"],
        "thiazide": ["hydrochlorothiazide", "chlorthalidone", "indapamide", "metolazone"],
        "ccb_dihydropyridine": ["amlodipine", "nifedipine", "felodipine", "nicardipine", "clevidipine"],
        "ccb_non_dihydropyridine": ["diltiazem", "verapamil"],
        "nitrate": ["isosorbide mononitrate", "isosorbide dinitrate", "nitroglycerin"],
        "anticoagulant_doac": ["apixaban", "rivaroxaban", "edoxaban", "dabigatran"],
        "anticoagulant_vka": ["warfarin", "acenocoumarol", "phenprocoumon"],
        "antiplatelet": ["aspirin", "clopidogrel", "prasugrel", "ticagrelor", "cangrelor"],
        "statin": ["atorvastatin", "rosuvastatin", "simvastatin", "pravastatin", "pitavastatin", "fluvastatin"],
        "ezetimibe": ["ezetimibe"],
        "pcsk9i": ["evolocumab", "alirocumab", "inclisiran"],
        "antiarrhythmic_class_i": ["flecainide", "propafenone", "quinidine", "procainamide", "disopyramide", "mexiletine", "lidocaine"],
        "antiarrhythmic_class_iii": ["amiodarone", "sotalol", "dofetilide", "dronedarone", "ibutilide"],
        "digoxin": ["digoxin"],
        "ivabradine": ["ivabradine"],
        "hydralazine": ["hydralazine"],
        "inotrope": ["dobutamine", "dopamine", "milrinone", "levosimendan"],
        "vasopressor": ["norepinephrine", "epinephrine", "vasopressin", "phenylephrine"],
    })
    
    def get_drug_class(self) -> Optional[str]:
        """Determine drug class from medication name."""
        name_lower = self.name.lower()
        for drug_class, drugs in self.DRUG_CLASSES.items():
            if any(drug in name_lower for drug in drugs):
                return drug_class
        return self.drug_class


@dataclass
class Procedure:
    """
    Cardiac procedure or intervention.
    """
    name: str
    procedure_date: Optional[date] = None
    indication: Optional[str] = None
    findings: Optional[str] = None
    complications: Optional[List[str]] = None
    
    # Common cardiac procedures
    PROCEDURES: Dict[str, str] = field(default_factory=lambda: {
        "pci": "Percutaneous Coronary Intervention",
        "cabg": "Coronary Artery Bypass Grafting",
        "tavr": "Transcatheter Aortic Valve Replacement",
        "savr": "Surgical Aortic Valve Replacement",
        "mitral_repair": "Mitral Valve Repair",
        "mitral_replacement": "Mitral Valve Replacement",
        "ablation_af": "Atrial Fibrillation Ablation",
        "ablation_vt": "Ventricular Tachycardia Ablation",
        "ablation_avnrt": "AVNRT Ablation",
        "icd_implant": "ICD Implantation",
        "pacemaker_implant": "Pacemaker Implantation",
        "crt_implant": "CRT Implantation",
        "crt_d_implant": "CRT-D Implantation",
        "cardioversion": "Electrical Cardioversion",
        "laa_closure": "Left Atrial Appendage Closure",
        "pericardiocentesis": "Pericardiocentesis",
        "catheterization": "Cardiac Catheterization",
    })


@dataclass
class Device:
    """
    Implanted cardiac device.
    """
    device_type: str  # "pacemaker", "icd", "crt_p", "crt_d", "loop_recorder"
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    implant_date: Optional[date] = None
    last_interrogation: Optional[date] = None
    battery_status: Optional[str] = None
    leads: Optional[List[str]] = None  # "ra", "rv", "lv", "his", "cs"
    
    # Pacing parameters
    pacing_mode: Optional[str] = None  # "DDD", "VVI", "AAI", etc.
    lower_rate: Optional[int] = None   # bpm
    upper_rate: Optional[int] = None   # bpm
    
    # ICD parameters
    vt_zone_rate: Optional[int] = None     # bpm
    vf_zone_rate: Optional[int] = None     # bpm
    
    # Therapy history
    atp_delivered: Optional[int] = None    # Count
    shocks_delivered: Optional[int] = None # Count
    last_therapy_date: Optional[date] = None


@dataclass
class Allergy:
    """
    Drug or substance allergy.
    """
    allergen: str
    reaction: Optional[str] = None  # "anaphylaxis", "rash", "angioedema", "gi_upset"
    severity: Optional[str] = None  # "mild", "moderate", "severe"
    verified: bool = False
    documented_date: Optional[date] = None


@dataclass
class Patient:
    """
    Comprehensive patient representation for cardiology clinical decision support.
    
    This is the central data structure that guidelines query against.
    """
    # Demographics
    patient_id: Optional[str] = None
    age: Optional[int] = None
    sex: Optional[Sex] = None
    weight_kg: Optional[float] = None
    height_cm: Optional[float] = None
    
    # Current measurements
    vitals: Optional[VitalSigns] = None
    labs: Optional[LabValues] = None
    ecg: Optional[ECGFindings] = None
    echo: Optional[EchoFindings] = None
    
    # Medical history
    diagnoses: List[Diagnosis] = field(default_factory=list)
    medications: List[Medication] = field(default_factory=list)
    procedures: List[Procedure] = field(default_factory=list)
    devices: List[Device] = field(default_factory=list)
    allergies: List[Allergy] = field(default_factory=list)
    
    # Key clinical flags (derived or explicit)
    nyha_class: Optional[NYHAClass] = None
    
    # Risk factors
    has_diabetes: bool = False
    has_hypertension: bool = False
    has_ckd: bool = False
    has_cad: bool = False
    has_prior_stroke_tia: bool = False
    has_prior_bleeding: bool = False
    has_vascular_disease: bool = False  # PAD, aortic plaque
    has_liver_disease: bool = False
    is_smoker: Optional[str] = None  # "current", "former", "never"
    alcohol_use: Optional[str] = None  # "none", "moderate", "heavy"
    
    # AF-specific
    af_type: Optional[AFType] = None
    on_anticoagulation: bool = False
    
    # HF-specific
    lvef: Optional[float] = None  # Convenience accessor (also in echo)
    
    # Oncology (for cardio-oncology)
    cancer_type: Optional[str] = None
    cancer_treatment: Optional[List[str]] = None  # Chemotherapy agents
    prior_chest_radiation: bool = False
    
    def __post_init__(self):
        """Derive values from nested objects where possible."""
        if self.echo and self.echo.lvef and self.lvef is None:
            self.lvef = self.echo.lvef
        if self.vitals:
            if self.vitals.weight and self.weight_kg is None:
                self.weight_kg = self.vitals.weight
            if self.vitals.height and self.height_cm is None:
                self.height_cm = self.vitals.height
    
    @property
    def bmi(self) -> Optional[float]:
        """Calculate BMI."""
        if self.weight_kg and self.height_cm and self.height_cm > 0:
            height_m = self.height_cm / 100
            return round(self.weight_kg / (height_m ** 2), 1)
        return None
    
    @property
    def egfr(self) -> Optional[float]:
        """Get eGFR from labs."""
        return self.labs.egfr if self.labs else None
    
    @property
    def bsa(self) -> Optional[float]:
        """Calculate body surface area (Mosteller formula)."""
        if self.weight_kg and self.height_cm:
            return round(((self.weight_kg * self.height_cm) / 3600) ** 0.5, 2)
        return None
    
    def has_diagnosis(self, diagnosis_key: str) -> bool:
        """Check if patient has a specific diagnosis."""
        key_lower = diagnosis_key.lower()
        for dx in self.diagnoses:
            if dx.is_active and (
                key_lower in dx.name.lower() or 
                (dx.icd10_code and key_lower in dx.icd10_code.lower())
            ):
                return True
        return False
    
    def is_on_medication(self, medication_or_class: str) -> bool:
        """Check if patient is on a specific medication or drug class."""
        search = medication_or_class.lower()
        for med in self.medications:
            if not med.is_active:
                continue
            if search in med.name.lower():
                return True
            if med.generic_name and search in med.generic_name.lower():
                return True
            drug_class = med.get_drug_class()
            if drug_class and search in drug_class.lower():
                return True
        return False
    
    def has_allergy(self, allergen: str) -> bool:
        """Check if patient has allergy to substance."""
        allergen_lower = allergen.lower()
        for allergy in self.allergies:
            if allergen_lower in allergy.allergen.lower():
                return True
        return False
    
    def contraindication(self, drug_or_class: str) -> Optional[str]:
        """
        Check if patient has contraindication to a medication.
        
        Returns reason string if contraindicated, None otherwise.
        """
        drug_lower = drug_or_class.lower()
        
        # Check allergies first
        for allergy in self.allergies:
            if drug_lower in allergy.allergen.lower():
                return f"Allergy: {allergy.allergen} ({allergy.reaction})"
        
        # Check specific contraindications
        if drug_lower in ["acei", "arb", "arni"]:
            if self.has_allergy("angioedema"):
                return "History of angioedema"
            if self.labs and self.labs.potassium and self.labs.potassium > 5.5:
                return f"Hyperkalemia (K+ = {self.labs.potassium})"
                
        if drug_lower in ["beta_blocker"]:
            if self.vitals and self.vitals.heart_rate and self.vitals.heart_rate < 50:
                return f"Bradycardia (HR = {self.vitals.heart_rate})"
            if self.ecg and self.ecg.second_degree_avb == "mobitz_2":
                return "Mobitz II AV block"
            if self.ecg and self.ecg.third_degree_avb:
                return "Third degree AV block"
                
        if drug_lower in ["mra", "spironolactone", "eplerenone"]:
            if self.labs and self.labs.potassium and self.labs.potassium > 5.0:
                return f"Hyperkalemia risk (K+ = {self.labs.potassium})"
            if self.labs and self.labs.egfr and self.labs.egfr < 30:
                return f"Severe CKD (eGFR = {self.labs.egfr})"
                
        if drug_lower in ["doac", "anticoagulant"]:
            if self.has_diagnosis("mechanical_valve"):
                return "Mechanical heart valve (requires warfarin)"
            if self.labs and self.labs.egfr and self.labs.egfr < 15:
                return f"ESRD (eGFR = {self.labs.egfr})"
        
        if drug_lower in ["sglt2i"]:
            if self.has_diagnosis("type_1_diabetes"):
                return "Type 1 diabetes (DKA risk)"
                
        return None
    
    def get_active_medications_by_class(self, drug_class: str) -> List[Medication]:
        """Get all active medications of a specific class."""
        result = []
        for med in self.medications:
            if med.is_active and med.get_drug_class() == drug_class.lower():
                result.append(med)
        return result
    
    def hf_phenotype(self) -> Optional[str]:
        """
        Determine heart failure phenotype based on LVEF.
        
        Per ESC 2021 HF Guidelines:
        - HFrEF: LVEF <= 40%
        - HFmrEF: LVEF 41-49%  
        - HFpEF: LVEF >= 50%
        """
        if self.lvef is None:
            return None
        if self.lvef <= 40:
            return "HFrEF"
        if self.lvef <= 49:
            return "HFmrEF"
        return "HFpEF"
