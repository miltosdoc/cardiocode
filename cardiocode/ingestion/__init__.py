"""
CardioCode PDF Ingestion and Knowledge Expansion System.

This module provides tools to:
1. Monitor for new PDF guidelines
2. Extract structured content from PDFs
3. Generate code templates for new guidelines
4. Track knowledge updates and versioning

Usage:
    from cardiocode.ingestion import GuidelineWatcher, process_new_pdf
    
    # Start watching for new PDFs
    watcher = GuidelineWatcher("source_pdfs/")
    watcher.start()
    
    # Or process a single PDF
    result = process_new_pdf("source_pdfs/new_guideline.pdf")
"""

from cardiocode.ingestion.pdf_watcher import GuidelineWatcher, check_for_new_pdfs
from cardiocode.ingestion.knowledge_builder import (
    generate_guideline_template,
    extract_recommendations_prompt,
)

__all__ = [
    "GuidelineWatcher",
    "check_for_new_pdfs",
    "generate_guideline_template",
    "extract_recommendations_prompt",
]
