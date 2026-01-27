"""
Peripheral Arterial and Aortic Diseases Guidelines (ESC 2024).

ESC Guidelines for the management of peripheral arterial and aortic diseases.

Reference: Eur Heart J. 2024;45(36):3538-3700. doi:10.1093/eurheartj/ehae179
"""

from cardiocode.guidelines.peripheral_arterial.diagnosis import (
    diagnose_pad,
    classify_aaa,
    calculate_abi,
    PADFontaineStage,
    PADRutherfordCategory,
    AAASize,
)

from cardiocode.guidelines.peripheral_arterial.treatment import (
    get_pad_treatment,
    get_aaa_management,
    get_carotid_management,
)

__all__ = [
    "diagnose_pad",
    "classify_aaa",
    "calculate_abi",
    "PADFontaineStage",
    "PADRutherfordCategory",
    "AAASize",
    "get_pad_treatment",
    "get_aaa_management",
    "get_carotid_management",
]
