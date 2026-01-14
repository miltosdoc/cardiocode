"""
Knowledge Builder for CardioCode.

Provides tools and prompts for LLM-assisted guideline extraction.
When a new PDF is detected, these tools help structure the extraction process.
"""

from __future__ import annotations
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime


def generate_guideline_template(
    guideline_name: str,
    guideline_key: str,  # e.g., "heart_failure"
    year: int,
    doi: str,
    pdf_filename: str,
) -> str:
    """
    Generate a Python module template for a new guideline.
    
    This creates the boilerplate structure that can be filled in
    by LLM-assisted extraction.
    
    Args:
        guideline_name: Full name of the guideline
        guideline_key: Short key (snake_case)
        year: Publication year
        doi: DOI of the guideline
        pdf_filename: PDF filename in source_pdfs/
    
    Returns:
        Python code template as string
    """
    template = f'''"""
{guideline_name} - Encoded as Executable Clinical Logic.

Source: {guideline_name}
DOI: {doi}
PDF: {pdf_filename}
Generated: {datetime.now().isoformat()}

This module was generated using CardioCode knowledge builder.
It requires review and validation by a clinical expert.
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
)
from cardiocode.core.evidence import EvidenceClass, EvidenceLevel


# Guideline metadata
GUIDELINE_INFO = {{
    "name": "{guideline_name}",
    "short_name": "ESC {guideline_key.upper().replace('_', ' ')} {year}",
    "year": {year},
    "doi": "{doi}",
    "pdf": "{pdf_filename}",
    "generated_at": "{datetime.now().isoformat()}",
    "validated": False,  # Set to True after clinical review
}}


# =============================================================================
# DIAGNOSTIC ALGORITHMS
# =============================================================================

def diagnose(patient: "Patient") -> RecommendationSet:
    """
    Diagnostic algorithm for this condition.
    
    TODO: Implement based on guideline content
    """
    rec_set = RecommendationSet(
        title="Diagnostic Evaluation",
        primary_guideline=GUIDELINE_INFO["short_name"],
    )
    
    # Add diagnostic recommendations here
    # Example:
    # rec_set.add(guideline_recommendation(
    #     action="...",
    #     guideline_key="{guideline_key}",
    #     evidence_class=EvidenceClass.I,
    #     evidence_level=EvidenceLevel.B,
    #     category=RecommendationCategory.DIAGNOSTIC,
    #     section="...",
    #     studies=["..."],
    # ))
    
    return rec_set


# =============================================================================
# TREATMENT ALGORITHMS
# =============================================================================

def get_treatment(patient: "Patient") -> RecommendationSet:
    """
    Treatment recommendations based on patient characteristics.
    
    TODO: Implement based on guideline content
    """
    rec_set = RecommendationSet(
        title="Treatment Recommendations",
        primary_guideline=GUIDELINE_INFO["short_name"],
    )
    
    # Add treatment recommendations here
    
    return rec_set


# =============================================================================
# MONITORING AND FOLLOW-UP
# =============================================================================

def get_monitoring(patient: "Patient") -> RecommendationSet:
    """
    Monitoring and follow-up recommendations.
    
    TODO: Implement based on guideline content
    """
    rec_set = RecommendationSet(
        title="Monitoring Recommendations",
        primary_guideline=GUIDELINE_INFO["short_name"],
    )
    
    return rec_set


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "GUIDELINE_INFO",
    "diagnose",
    "get_treatment",
    "get_monitoring",
]
'''
    return template


def extract_recommendations_prompt(
    pdf_filename: str,
    guideline_type: Optional[str] = None,
) -> str:
    """
    Generate a prompt for LLM-assisted guideline extraction.
    
    This prompt instructs an LLM how to extract structured
    recommendations from a guideline PDF.
    
    Args:
        pdf_filename: Name of the PDF file
        guideline_type: Identified guideline type (optional)
    
    Returns:
        Prompt string for LLM
    """
    prompt = f"""
# Task: Extract Structured Recommendations from ESC Guideline

You are helping encode the ESC guideline "{pdf_filename}" into executable clinical code.

## Instructions

1. **Identify Key Sections**: Look for:
   - Recommendation tables (usually color-coded by evidence class)
   - Diagnostic algorithms (flowcharts)
   - Treatment algorithms
   - Monitoring/follow-up schedules

2. **For Each Recommendation, Extract**:
   - **Action**: What is recommended (exact wording from guideline)
   - **Evidence Class**: I, IIa, IIb, or III
   - **Evidence Level**: A, B, or C
   - **Section**: Section number in the guideline
   - **Page**: Page number for reference
   - **Supporting Studies**: Named trials supporting the recommendation
   - **Conditions**: When this applies
   - **Contraindications**: When NOT to apply

3. **Output Format**:
   For each recommendation, provide:
   ```python
   guideline_recommendation(
       action="[exact recommendation text]",
       guideline_key="[guideline_key]",
       evidence_class=EvidenceClass.[I/IIA/IIB/III],
       evidence_level=EvidenceLevel.[A/B/C],
       category=RecommendationCategory.[PHARMACOTHERAPY/DIAGNOSTIC/PROCEDURE/etc],
       section="[section number]",
       page=[page number],
       studies=["Study1", "Study2"],
       rationale="[brief explanation]",
       conditions=["condition1", "condition2"],
       contraindications=["contraindication1"],
   )
   ```

4. **Prioritize**:
   - Class I recommendations (must-do)
   - Key diagnostic algorithms
   - Treatment decision trees
   - High-risk patient identification

5. **Flag Uncertainties**:
   - If recommendation is ambiguous, note it
   - If evidence class is unclear, mark as needing verification
   - If multiple guidelines cover same topic, note potential conflicts

## Output Structure

Organize extracted content as:

### 1. Guideline Metadata
- Full title
- Year
- DOI
- Key authors

### 2. Diagnostic Recommendations
[List of diagnosis-related recommendations]

### 3. Treatment Recommendations  
[List of treatment recommendations, organized by patient subgroups]

### 4. Device/Procedure Recommendations
[If applicable]

### 5. Monitoring/Follow-up
[Timing and parameters]

### 6. Special Populations
[Elderly, CKD, pregnancy, etc.]

---

**IMPORTANT**: 
- Every recommendation MUST include evidence class and level
- Always cite the source section/page
- When guideline is ambiguous, flag for clinical review rather than guessing
- The goal is to make guidelines queryable by code, not to replace clinical judgment

Begin extraction from the PDF "{pdf_filename}".
"""
    return prompt


def generate_expansion_instructions() -> str:
    """
    Generate instructions for expanding the CardioCode knowledge base.
    
    These instructions are for use by LLM agents or developers
    when adding new guidelines to the system.
    """
    return """
# CardioCode Knowledge Expansion Guide

## Adding a New Guideline

### Step 1: Detect New PDF
```python
from cardiocode.ingestion import check_for_new_pdfs
new_pdfs = check_for_new_pdfs("source_pdfs/")
```

### Step 2: Generate Template
```python
from cardiocode.ingestion import generate_guideline_template
template = generate_guideline_template(
    guideline_name="2024 ESC Guidelines on Chronic Coronary Syndromes",
    guideline_key="chronic_coronary",
    year=2024,
    doi="10.1093/eurheartj/xxx",
    pdf_filename="new_guideline.pdf",
)
# Save template to guidelines/chronic_coronary/__init__.py
```

### Step 3: Extract Recommendations
```python
from cardiocode.ingestion import extract_recommendations_prompt
prompt = extract_recommendations_prompt("new_guideline.pdf", "chronic_coronary")
# Use this prompt with Claude/GPT to extract structured content
```

### Step 4: Implement and Validate
1. Fill in the generated template with extracted recommendations
2. Ensure every recommendation has:
   - Evidence class (I, IIa, IIb, III)
   - Evidence level (A, B, C)
   - Source section/page
   - Supporting studies
3. Add clinical logic for patient-specific recommendations
4. Mark `validated: True` after clinical expert review

### Step 5: Register in Guidelines Registry
Update `cardiocode/guidelines/__init__.py` to include the new module.

### Step 6: Test
```python
from cardiocode.guidelines import chronic_coronary
from cardiocode.core.types import Patient

patient = Patient(age=65, has_cad=True, ...)
recs = chronic_coronary.get_treatment(patient)
print(recs.format_for_display())
```

## Quality Checklist

Before marking a guideline as validated:

- [ ] All Class I recommendations encoded
- [ ] Key diagnostic algorithms implemented
- [ ] Treatment pathways cover main patient subgroups
- [ ] Evidence citations complete with section/page
- [ ] Supporting study names included
- [ ] Contraindications specified
- [ ] Follow-up/monitoring guidance included
- [ ] Tested with representative patient cases
- [ ] Reviewed by clinical expert

## Handling Updates

When a guideline is updated:
1. Create new version (e.g., `heart_failure_2025/`)
2. Keep old version with deprecation notice
3. Update registry to point to newest version
4. Log changes between versions

## Synthesis Rules

When patient scenarios span multiple guidelines:
1. Always flag as SYNTHESIS in output
2. List all guidelines consulted
3. Provide lower confidence score
4. Recommend specialist consultation for complex cases
"""


def create_clinical_review_checklist(guideline_key: str) -> str:
    """
    Generate a clinical review checklist for a newly encoded guideline.
    
    This should be completed by a clinical expert before marking
    the guideline as validated.
    """
    return f"""
# Clinical Review Checklist: {guideline_key}

## Reviewer Information
- Reviewer Name: _______________________
- Credentials: _______________________
- Review Date: _______________________

## Completeness Review

### Diagnostic Algorithms
- [ ] All major diagnostic pathways captured
- [ ] Correct decision thresholds
- [ ] Appropriate test sequences
- [ ] Risk stratification accurate

### Treatment Recommendations
- [ ] All Class I recommendations present
- [ ] Class IIa recommendations appropriately included
- [ ] Drug dosing accurate
- [ ] Contraindications complete
- [ ] Drug interactions considered

### Special Populations
- [ ] Elderly considerations
- [ ] CKD dose adjustments
- [ ] Pregnancy/lactation guidance
- [ ] Comorbidity interactions

### Follow-up Guidance
- [ ] Monitoring intervals appropriate
- [ ] Parameters to monitor complete
- [ ] Escalation criteria clear

## Accuracy Review

### Evidence Classifications
- [ ] All evidence classes match source guideline
- [ ] Evidence levels accurate
- [ ] Study citations correct

### Clinical Logic
- [ ] Decision trees follow guideline intent
- [ ] No dangerous omissions
- [ ] No contradictory recommendations
- [ ] Appropriate flagging of low-evidence areas

## Validation Testing

Tested with case scenarios:
- [ ] Typical presentation
- [ ] Complex comorbidities  
- [ ] Edge cases
- [ ] Contraindicated scenarios

## Sign-off

I have reviewed this encoded guideline and confirm it accurately represents 
the source ESC guideline for clinical decision support purposes.

I understand this is decision SUPPORT and does not replace clinical judgment.

Signature: _______________________
Date: _______________________

## Notes/Corrections Needed
_________________________________________
_________________________________________
_________________________________________
"""
