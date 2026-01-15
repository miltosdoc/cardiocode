"""
CardioCode Clinical Pathways.

Multi-step decision algorithms for clinical management.
"""

from .hf_treatment import (
    pathway_hfref_treatment,
    pathway_hf_device_therapy,
    get_hf_medication_targets,
)
from .vt_management import (
    pathway_vt_acute_management,
    pathway_electrical_storm,
    pathway_vt_chronic_management,
)
from .pe_treatment import (
    pathway_pe_treatment,
    pathway_pe_anticoagulation_duration,
)
from .syncope_pathway import (
    pathway_syncope_evaluation,
    pathway_syncope_disposition,
)

__all__ = [
    # HF Treatment
    "pathway_hfref_treatment",
    "pathway_hf_device_therapy",
    "get_hf_medication_targets",
    # VT Management
    "pathway_vt_acute_management",
    "pathway_electrical_storm",
    "pathway_vt_chronic_management",
    # PE Treatment
    "pathway_pe_treatment",
    "pathway_pe_anticoagulation_duration",
    # Syncope
    "pathway_syncope_evaluation",
    "pathway_syncope_disposition",
]
