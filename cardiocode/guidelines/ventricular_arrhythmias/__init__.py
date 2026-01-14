"""
ESC 2022 Ventricular Arrhythmias/SCD Guidelines.

Source: 2022 ESC Guidelines for the management of patients with ventricular arrhythmias 
        and the prevention of sudden cardiac death
DOI: 10.1093/eurheartj/ehac262
PDF: ehac262.pdf

Modules:
- risk_stratification: SCD risk assessment for various cardiomyopathies
- icd_indications: ICD indication assessment (primary/secondary prevention, channelopathies)
- vt_management: Acute and chronic VT management, ablation, antiarrhythmics
"""

from cardiocode.guidelines.ventricular_arrhythmias.risk_stratification import (
    SCDRiskCategory,
    SCDRiskAssessment,
    Cardiomyopathy,
    calculate_hcm_scd_risk,
    calculate_arvc_risk,
    stratify_scd_risk_dcm,
    stratify_scd_risk_ischemic,
    stratify_scd_risk,
)
from cardiocode.guidelines.ventricular_arrhythmias.icd_indications import (
    ICDIndicationType,
    ICDIndication,
    assess_secondary_prevention_icd,
    assess_channelopathy_icd,
    assess_icd_indication,
)
from cardiocode.guidelines.ventricular_arrhythmias.vt_management import (
    VTType,
    HemodynamicStatus,
    VTManagementPlan,
    manage_acute_vt,
    assess_vt_ablation_indication,
    get_antiarrhythmic_for_vt,
    manage_vt,
)

GUIDELINE_INFO = {
    "name": "2022 ESC Guidelines for the management of patients with ventricular arrhythmias and the prevention of sudden cardiac death",
    "short_name": "ESC VA/SCD 2022",
    "year": 2022,
    "doi": "10.1093/eurheartj/ehac262",
    "pdf": "ehac262.pdf",
    "status": "complete",
}

__all__ = [
    "GUIDELINE_INFO",
    # Risk stratification
    "SCDRiskCategory",
    "SCDRiskAssessment",
    "Cardiomyopathy",
    "calculate_hcm_scd_risk",
    "calculate_arvc_risk",
    "stratify_scd_risk_dcm",
    "stratify_scd_risk_ischemic",
    "stratify_scd_risk",
    # ICD indications
    "ICDIndicationType",
    "ICDIndication",
    "assess_secondary_prevention_icd",
    "assess_channelopathy_icd",
    "assess_icd_indication",
    # VT management
    "VTType",
    "HemodynamicStatus",
    "VTManagementPlan",
    "manage_acute_vt",
    "assess_vt_ablation_indication",
    "get_antiarrhythmic_for_vt",
    "manage_vt",
]
