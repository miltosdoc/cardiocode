"""
CardioCode PDF Ingestion and Knowledge Expansion System.

DEPRECATED: This module is superseded by cardiocode.knowledge.extractor.
Use cardiocode_process_pdfs() MCP tool or:

    from cardiocode.knowledge.extractor import process_all_pdfs
    process_all_pdfs()

The new system:
- Stores extracted knowledge in cardiocode/knowledge/chapters/
- Uses cardiocode/knowledge/guidelines.json as the index
- Is cross-platform compatible (no Windows path issues)
- Is connected to MCP tools (search_knowledge, get_chapter, etc.)

This module is kept for backward compatibility but may be removed in future versions.
"""
import warnings
warnings.warn(
    "cardiocode.ingestion is deprecated. Use cardiocode.knowledge.extractor instead.",
    DeprecationWarning,
    stacklevel=2
)

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
