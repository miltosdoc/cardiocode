"""
CardioCode Clinical Calculators.

Validated clinical risk scores and calculators.
"""

from .pe_scores import (
    calculate_pesi,
    calculate_spesi,
    calculate_geneva_pe,
    calculate_age_adjusted_ddimer,
)
from .pah_risk import (
    calculate_pah_baseline_risk,
    calculate_pah_followup_risk,
    classify_ph_hemodynamics,
)
from .hf_prognosis import (
    calculate_maggic_score,
    assess_iron_deficiency_hf,
    classify_hf_phenotype,
)
from .arrhythmia_risk import (
    calculate_lmna_risk,
    calculate_lqts_risk,
    calculate_brugada_risk,
)

__all__ = [
    # PE Scores
    "calculate_pesi",
    "calculate_spesi", 
    "calculate_geneva_pe",
    "calculate_age_adjusted_ddimer",
    # PAH Risk
    "calculate_pah_baseline_risk",
    "calculate_pah_followup_risk",
    "classify_ph_hemodynamics",
    # HF Prognosis
    "calculate_maggic_score",
    "assess_iron_deficiency_hf",
    "classify_hf_phenotype",
    # Arrhythmia Risk
    "calculate_lmna_risk",
    "calculate_lqts_risk",
    "calculate_brugada_risk",
]
