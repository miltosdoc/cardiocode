"""
CardioCode ESC Guidelines Library.

Each guideline is encoded as executable Python with full evidence provenance.

Available Guidelines:
- heart_failure: ESC 2021 Heart Failure Guidelines
- atrial_fibrillation: ESC 2020 AF Guidelines
- acs_nstemi: ESC 2020 NSTE-ACS Guidelines
- valvular_heart_disease: ESC 2021 VHD Guidelines
- pulmonary_hypertension: ESC/ERS 2022 PH Guidelines
- ventricular_arrhythmias: ESC 2022 VA/SCD Guidelines
- cardio_oncology: ESC 2022 Cardio-Oncology Guidelines
"""

from cardiocode.guidelines import heart_failure
from cardiocode.guidelines import atrial_fibrillation
from cardiocode.guidelines import acs_nstemi
from cardiocode.guidelines import valvular_heart_disease
from cardiocode.guidelines import pulmonary_hypertension
from cardiocode.guidelines import ventricular_arrhythmias
from cardiocode.guidelines import cardio_oncology

__all__ = [
    "heart_failure",
    "atrial_fibrillation", 
    "acs_nstemi",
    "valvular_heart_disease",
    "pulmonary_hypertension",
    "ventricular_arrhythmias",
    "cardio_oncology",
]

# Guideline metadata registry
GUIDELINES = {
    "heart_failure": {
        "full_name": "2021 ESC Guidelines for the diagnosis and treatment of acute and chronic heart failure",
        "short_name": "ESC HF 2021",
        "year": 2021,
        "doi": "10.1093/eurheartj/ehab364",
        "pdf": "ehab364.pdf",
        "module": heart_failure,
    },
    "atrial_fibrillation": {
        "full_name": "2020 ESC Guidelines for the diagnosis and management of atrial fibrillation",
        "short_name": "ESC AF 2020",
        "year": 2020,
        "doi": "10.1093/eurheartj/ehaa612",
        "pdf": "ehaa554.pdf",
        "module": atrial_fibrillation,
    },
    "acs_nstemi": {
        "full_name": "2020 ESC Guidelines for the management of acute coronary syndromes in patients presenting without persistent ST-segment elevation",
        "short_name": "ESC NSTE-ACS 2020",
        "year": 2020,
        "doi": "10.1093/eurheartj/ehaa575",
        "pdf": "ehaa605.pdf",
        "module": acs_nstemi,
    },
    "valvular_heart_disease": {
        "full_name": "2021 ESC/EACTS Guidelines for the management of valvular heart disease",
        "short_name": "ESC VHD 2021",
        "year": 2021,
        "doi": "10.1093/eurheartj/ehab395",
        "pdf": "ehab484.pdf",
        "module": valvular_heart_disease,
    },
    "pulmonary_hypertension": {
        "full_name": "2022 ESC/ERS Guidelines for the diagnosis and treatment of pulmonary hypertension",
        "short_name": "ESC/ERS PH 2022",
        "year": 2022,
        "doi": "10.1093/eurheartj/ehac237",
        "pdf": "2022 ESC_ERS Guidelines for the diagnosis and treatment of pulmonary hypertension _ European Heart Journal _ Oxford Academic.pdf",
        "module": pulmonary_hypertension,
    },
    "ventricular_arrhythmias": {
        "full_name": "2022 ESC Guidelines for the management of patients with ventricular arrhythmias and the prevention of sudden cardiac death",
        "short_name": "ESC VA/SCD 2022",
        "year": 2022,
        "doi": "10.1093/eurheartj/ehac262",
        "pdf": "ehac262.pdf",
        "module": ventricular_arrhythmias,
    },
    "cardio_oncology": {
        "full_name": "2022 ESC Guidelines on cardio-oncology",
        "short_name": "ESC Cardio-Oncology 2022",
        "year": 2022,
        "doi": "10.1093/eurheartj/ehac244",
        "pdf": "ehac244.pdf",
        "module": cardio_oncology,
    },
}
