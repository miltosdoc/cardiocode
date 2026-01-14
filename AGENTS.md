"""
Update AGENTS.md with CardioCode LLM-driven knowledge management.

This document explains how agents should use CardioCode with the new LLM-powered
knowledge search and function generation capabilities.
"""

# CardioCode Agent Usage Guide

## Overview

CardioCode is now an LLM-driven clinical decision support system that combines:
- **Static clinical functions** (risk scores, guideline assessments)
- **Dynamic knowledge extraction** (chapter/keyword search without embeddings)
- **Secure function generation** (two-step approval workflow)

## Session Initialization

**MUST CALL FIRST**:
```
cardiocode_get_system_context()
```

This returns:
- Available guidelines and their current processing status
- All static functions (risk scores, assessments)
- Generated functions awaiting approval
- System capabilities and usage instructions

## Clinical Question Answering Workflow

### 1. Try Static Functions First
For specific clinical calculations:
```
tool_calculate_cha2ds2_vasc(age="75", female="true", ...)
tool_assess_aortic_stenosis(peak_velocity="4.5", ...)
```

### 2. Search Knowledge Base
For guideline content or narrative questions:
```
tool_search_knowledge(query="aortic stenosis management")
```

Returns ranked chapters/tables with relevance scores.

### 3. Retrieve Full Content
For detailed chapter information:
```
tool_get_full_chapter(guideline_hash="...", chapter_title="...")
```

## Function Generation Workflow

### 1. Propose Function
When content appears suitable for automation:
```
tool_propose_function_from_content(content_query="risk score calculator")
```

Returns function proposal with:
- Generated Python code
- Test cases
- Security hash
- Approval requirements

### 2. Approve Function
After clinical review:
```
tool_approve_save_function(
    proposal_id="abc123", 
    code_hash="f8c9a...",
    function_name="generated_as_risk_score"
)
```

### 3. Reject Function
If function is inadequate:
```
tool_reject_function(
    proposal_id="abc123",
    reason="Missing contraindication checks"
)
```

## System Maintenance Commands

### Process New PDFs
When new guidelines are added to `source_pdfs/`:
```
tool_process_pending_pdfs()
```

### Update Knowledge Base
For web searches or new guideline downloads:
```
tool_propose_web_update(query="2025 ESC aortic stenosis", update_type="websearch")
tool_confirm_web_update(proposal_id="def456", chosen_option="Search ESC website")
```

### Memory Management
Store user-provided clinical knowledge:
```
tool_store_to_memory(
    content="Hospital protocol for anticoagulation bridging",
    keywords="bridging, warfarin, doac",
    tags="protocol, anticoagulation"
)
```

## Security and Safety

### Two-Step Approval
- **No auto-saving** functions without explicit approval
- **Hash verification**: `approve_save_function` requires matching `code_hash`
- **Audit trail**: All proposals and approvals are logged
- **Version control**: Functions are versioned, not overwritten

### Clinical Validation
- All generated functions marked `requires_validation: True`
- Test cases provided with each function proposal
- Source content included for clinical verification

### Trusted Sources
Web updates restricted to:
- ESC (European Society of Cardiology)
- ACC/AHA (American College of Cardiology/American Heart Association)
- PubMed Central
- Peer-reviewed journals

## Knowledge Retrieval Strategy

### No Embeddings Required
- Full guideline content fits in modern context windows
- LLM selects relevant chapters based on:
  - Chapter title matching
  - Keyword matching
  - Semantic similarity scoring
  - Recency weighting

### Content Organization
```
Guideline PDF → Chapters (with titles, keywords, tables)
├── Raw narrative content
├── Structured tables
├── Auto-generable sections (marked)
└── User-provided memory items
```

## Error Handling and Fallbacks

### When Search Fails
- Return error with suggestions for refined query
- Offer to search all chapters if no matches found
- Provide available chapter list for manual selection

### When Function Generation Fails
- Explain why content isn't suitable (e.g., narrative vs structured)
- Suggest breaking down into smaller, structured components
- Offer to try specific table/section instead

## Example Sessions

### Scenario 1: Clinical Question
```
User: "What are the recommendations for severe asymptomatic AS?"

Agent:
1. cardiocode_get_system_context()
2. tool_search_knowledge(query="severe asymptomatic aortic stenosis")
3. tool_get_full_chapter(...) for most relevant chapter
4. Generate answer with source citations
```

### Scenario 2: Function Generation
```
User: "This risk table should be a function"

Agent:
1. cardiocode_get_system_context()
2. tool_propose_function_from_content(content_query="risk table")
3. [Reviews proposal with clinician]
4. tool_approve_save_function(proposal_id="...", code_hash="...", function_name="...")
5. Function becomes available in system
```

### Scenario 3: System Update
```
User: "Check for latest aortic stenosis guidelines"

Agent:
1. tool_propose_web_update(query="aortic stenosis guidelines 2024 2025")
2. [Presents options: ESC website, PubMed, custom URL]
3. tool_confirm_web_update(...)
4. tool_process_pending_pdfs() if new PDF downloaded
```

## Best Practices

1. **Always call `cardiocode_get_system_context()` first**
2. **Use specific functions when available** (more reliable than search)
3. **Cite sources** when using searched content
4. **Validate function logic** before approving
5. **Keep audit trail** by using proper approval workflow
6. **Check for function conflicts** before generating new ones

## Troubleshooting

### If tools aren't found:
- Verify LLM tools loaded properly
- Check that `cardiocode/mcp/tools.py` was updated
- Restart MCP server if needed

### If PDF processing fails:
- Check PyMuPDF installation: `pip install pymupdf`
- Verify PDF path and permissions
- Check PDF isn't corrupted

### If function generation fails:
- Ensure content has clear input/output structure
- Try more specific content description
- Check for malformatted tables or complex algorithms

This LLM-driven approach makes CardioCode more flexible while maintaining clinical safety through the secure approval workflow.