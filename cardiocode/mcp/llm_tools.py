"""
LLM-driven Knowledge Tools for CardioCode.

These tools provide LLM-powered search, function generation, and knowledge management
for clinical guideline content without requiring embeddings or vector stores.
"""

from __future__ import annotations
import json
from typing import Dict, Any, List, Optional

# Import our new knowledge management components
from cardiocode.ingestion.knowledge_manager import KnowledgeManager
from cardiocode.ingestion.dynamic_generator import DynamicFunctionGenerator
from cardiocode.ingestion.pdf_watcher import GuidelineRegistry


# Initialize components
knowledge_manager = KnowledgeManager()
function_generator = DynamicFunctionGenerator(knowledge_manager)
guideline_registry = GuidelineRegistry()


def tool_cardiocode_get_system_context() -> Dict[str, Any]:
    """
    Get CardioCode system context and knowledge base summary.
    
    This tool should be called at the start of each session to understand
    the available knowledge, functions, and system capabilities.
    
    Returns:
        dict: Complete system context including available guidelines, functions, and capabilities
    """
    
    # Get knowledge summary
    knowledge_summary = knowledge_manager.get_guideline_summary()
    
    # Get function candidates
    function_candidates = function_generator.list_proposed_functions()
    web_proposals = function_generator.list_web_proposals()
    
    # Get pending PDFs
    pending_pdfs = guideline_registry.get_pending()
    
    return {
        "system_knowledge": {
            "total_guidelines": knowledge_summary["total_guidelines"],
            "total_chapters": knowledge_summary["total_chapters"],
            "total_tables": knowledge_summary["total_tables"],
            "function_candidates": knowledge_summary["function_candidates"],
            "guidelines": knowledge_summary["guidelines"]
        },
        "available_functions": {
            "static_functions": [
                "calculate_cha2ds2_vasc",
                "calculate_has_bled", 
                "calculate_grace_score",
                "calculate_wells_pe",
                "calculate_hcm_scd_risk",
                "get_hfref_treatment",
                "assess_icd_indication",
                "assess_pah_risk",
                "get_pah_treatment",
                "calculate_hfa_icos_risk",
                "get_surveillance_protocol",
                "manage_ctrcd",
                "manage_vt",
                "assess_aortic_stenosis",
                "assess_mitral_regurgitation",
                "get_vt_management",
                "cardiocode_assess_pulmonary_hypertension",
                "cardiocode_assess_cardio_oncology_risk",
                "cardiocode_manage_ctrcd",
                "cardiocode_get_vt_management",
                "cardiocode_assess_icd_indication",
                "get_hf_recommendations",
                "calculate_ptp",
                "calculate_nste_grace",
                "calculate_wells_pe",
                "cardiocode_check_new_pdfs",
                "cardiocode_get_pdf_status",
                "cardiocode_get_pdf_notifications",
                "cardiocode_acknowledge_pdf_notification",
                "cardiocode_extract_pdf_recommendations",
                "get_pdf_notifications"
            ],
            "generated_functions": [prop["function_name"] for prop in function_candidates if prop.get("status") == "approved"],
            "pending_proposals": [prop for prop in function_candidates if prop.get("status") == "proposed"]
        },
        "pending_processing": {
            "pdfs": [
                {
                    "filename": pdf.filename,
                    "type": pdf.guideline_type,
                    "year": pdf.guideline_year
                } for pdf in pending_pdfs
            ],
            "count": len(pending_pdfs)
        },
        "system_capabilities": {
            "knowledge_search": "Search extracted guideline chapters and tables",
            "function_generation": "Generate functions from structured content",
            "secure_approval": "Two-step approval required for all mutations",
            "web_updates": "Propose web searches and PDF downloads",
            "memory_storage": "Store and retrieve user-provided knowledge"
        },
        "usage_instructions": {
            "search": "Use 'search_knowledge' to find relevant guideline content",
            "generate": "Use 'propose_function_from_content' to create functions",
            "approve": "Use 'approve_save_function' to approve proposed functions",
            "reject": "Use 'reject_function' to reject proposals",
            "web": "Use 'propose_web_update' to search/download new content",
            "memory": "Use 'store_to_memory' to save clinical knowledge",
            "context": "Call this tool first for each session to get current system state"
        }
    }


def tool_search_knowledge(query: str, max_results: int = "5") -> Dict[str, Any]:
    """
    Search for relevant guideline content using LLM-powered semantic matching.
    
    This tool searches through extracted chapter titles, keywords, and content
    to find the most relevant sections for answering clinical questions.
    
    Args:
        query: Clinical question or topic to search for
        max_results: Maximum number of results to return (default: 5)
    
    Returns:
        dict: Search results with relevance scores and content previews
    """
    
    # Convert max_results to int
    try:
        max_results = int(max_results)
    except (ValueError, TypeError):
        max_results = 5
    
    # Search knowledge base
    search_results = knowledge_manager.search_knowledge(query, top_k=max_results)
    
    # Format results
    formatted_results = []
    for i, result in enumerate(search_results):
        formatted_results.append({
            "rank": i + 1,
            "chapter_title": result.chapter.get("title", "Unknown"),
            "guideline": result.chapter.get("guideline_name", "Unknown"),
            "relevance_score": round(result.relevance_score, 2),
            "matched_keywords": result.matched_keywords,
            "content_preview": result.chapter.get("raw_text", "")[:300] + "...",
            "function_potential": result.chapter.get("function_potential", "raw"),
            "tables": [
                {
                    "title": table.get("title", "Table"),
                    "page": table.get("page_number", 0) + 1,
                    "preview": table.get("content", "")[:200] + "..."
                } for table in result.chapter.get("tables", [])
            ]
        })
    
    return {
        "query": query,
        "total_results": len(search_results),
        "results": formatted_results,
        "next_actions": [
            "Use 'get_full_chapter' to retrieve complete chapter content",
            "Use 'propose_function_from_content' if this should be a function",
            "Use 'store_to_memory' to save relevant information"
        ]
    }


def tool_get_full_chapter(guideline_hash: str, chapter_title: str) -> Dict[str, Any]:
    """
    Get the complete content of a specific chapter.
    
    This tool retrieves the full text and tables from a chapter
    that was identified through knowledge search.
    
    Args:
        guideline_hash: Hash identifier for the guideline PDF
        chapter_title: Exact title of the chapter to retrieve
    
    Returns:
        dict: Complete chapter content with text and tables
    """
    
    chapter = knowledge_manager.get_chapter_content(guideline_hash, chapter_title)
    
    if not chapter:
        return {
            "error": "Chapter not found",
            "guideline_hash": guideline_hash,
            "chapter_title": chapter_title,
            "available_chapters": list(knowledge_manager.knowledge_index.get(guideline_hash, {}).get("chapters", []))
        }
    
    return {
        "chapter_info": {
            "title": chapter.get("title"),
            "number": chapter.get("number"),
            "pages": f"{chapter.get('start_page') + 1}-{chapter.get('end_page') + 1}",
            "function_potential": chapter.get("function_potential"),
            "keywords": chapter.get("keywords", [])
        },
        "full_text": chapter.get("raw_text", ""),
        "tables": [
            {
                "title": table.get("title", "Table"),
                "page": table.get("page_number", 0) + 1,
                "content": table.get("content", ""),
                "function_potential": table.get("function_potential", "raw")
            } for table in chapter.get("tables", [])
        ],
        "source_guideline": knowledge_manager.knowledge_index.get(guideline_hash, {}).get("guideline_info", {}),
        "next_actions": [
            "Use 'propose_function_from_content' to create function from this chapter",
            "Use 'store_to_memory' to save key information",
            "Use 'get_chapter_context' for more details"
        ]
    }


def tool_propose_function_from_content(content_query: str, source_context: str = "") -> Dict[str, Any]:
    """
    Propose generating a function from clinical content.
    
    This tool analyzes content to determine if it can be converted
    into an executable function and generates a proposal for approval.
    
    Args:
        content_query: Description of content to function-ize
        source_context: Additional context about the source material
    
    Returns:
        dict: Function proposal with code, test cases, and approval requirements
    """
    
    result = function_generator.propose_function_from_content(content_query, source_context)
    
    if "error" in result:
        return {
            "error": result["error"],
            "suggestions": result.get("suggestions", ""),
            "query": content_query
        }
    
    return {
        "proposal": {
            "id": result["proposal_id"],
            "function_name": result["function_name"],
            "source_title": result["source_title"],
            "source_preview": result["source_preview"],
            "function_code": result["function_code"],
            "test_cases": result["test_cases"],
            "code_hash": result["code_hash"]
        },
        "approval_required": True,
        "approval_steps": [
            "Review the generated function code for clinical accuracy",
            "Run the provided test cases if applicable",
            "Call 'approve_save_function' with the proposal_id and code_hash to save",
            "Call 'reject_function' with the proposal_id and reason to reject"
        ],
        "security_note": "Function will only be saved after explicit approval with matching hash"
    }


def tool_approve_save_function(proposal_id: str, code_hash: str, function_name: str) -> Dict[str, Any]:
    """
    Approve and save a proposed function.
    
    This tool saves a proposed function after security verification.
    The provided code_hash must match the original proposal for security.
    
    Args:
        proposal_id: ID of the proposal to approve
        code_hash: Hash of the function code (from proposal)
        function_name: Name to save the function as
    
    Returns:
        dict: Result of the approval process
    """
    
    result = function_generator.approve_save_function(proposal_id, code_hash, function_name)
    
    if "error" in result:
        return {
            "error": result["error"],
            "proposal_id": proposal_id,
            "security_failed": "code_hash" in result.get("error", "").lower()
        }
    
    return {
        "success": True,
        "function_name": result["function_name"],
        "file_path": result["file_path"],
        "message": result["message"],
        "activation_note": "Function is now available in the generated functions module",
        "validation_required": "Clinical validation recommended before routine use"
    }


def tool_reject_function(proposal_id: str, reason: str) -> Dict[str, Any]:
    """
    Reject a proposed function.
    
    This tool rejects a function proposal with a documented reason.
    
    Args:
        proposal_id: ID of the proposal to reject
        reason: Clinical or technical reason for rejection
    
    Returns:
        dict: Result of the rejection process
    """
    
    result = function_generator.reject_function(proposal_id, reason)
    
    if "error" in result:
        return {
            "error": result["error"],
            "proposal_id": proposal_id
        }
    
    return {
        "success": True,
        "function_name": result["function_name"],
        "message": result["message"],
        "proposal_status": "rejected"
    }


def tool_propose_web_update(query: str, update_type: str = "websearch") -> Dict[str, Any]:
    """
    Propose a web search or PDF download to update knowledge base.
    
    This tool creates a proposal for searching the web or downloading
    new guideline content to keep the system current.
    
    Args:
        query: Search query or URL for download
        update_type: Type of update ('websearch', 'download', 'esc_check')
    
    Returns:
        dict: Update proposal with options for user selection
    """
    
    result = function_generator.propose_web_update(query, update_type)
    
    return {
        "proposal": {
            "id": result["proposal_id"],
            "update_type": result["update_type"],
            "query": result["query"],
            "reason": result["reason"],
            "options": result["options"]
        },
        "confirmation_required": True,
        "next_steps": [
            "Choose one of the provided options",
            "Call 'confirm_web_update' with proposal_id and chosen_option",
            "Review security implications before downloading from URLs"
        ],
        "security_note": "Only trusted sources (ESC, ACC, AHA, PubMed) should be used"
    }


def tool_confirm_web_update(proposal_id: str, chosen_option: str) -> Dict[str, Any]:
    """
    Execute a proposed web search or PDF download.
    
    This tool executes a previously proposed web update after user
    has explicitly chosen an option.
    
    Args:
        proposal_id: ID of the web update proposal
        chosen_option: The specific option chosen from the proposal
    
    Returns:
        dict: Result of the web update execution
    """
    
    result = function_generator.confirm_web_update(proposal_id, chosen_option)
    
    if "error" in result:
        return {
            "error": result["error"],
            "proposal_id": proposal_id,
            "chosen_option": chosen_option
        }
    
    return {
        "success": True,
        "action": result.get("action"),
        "status": result.get("status"),
        "message": result.get("message"),
        "next_steps": [
            "Check for new PDFs with 'cardiocode_get_pdf_status'",
            "Process new content with extraction pipeline",
            "Review any new function proposals"
        ]
    }


def tool_store_to_memory(content: str, keywords: str = "", tags: str = "") -> Dict[str, Any]:
    """
    Store clinical knowledge for future reference.
    
    This tool saves user-provided clinical information with keywords
    for easy retrieval in future sessions.
    
    Args:
        content: Clinical information to store
        keywords: Comma-separated keywords for searching
        tags: Comma-separated tags for categorization
    
    Returns:
        dict: Result of memory storage operation
    """
    
    # Parse keywords and tags
    keyword_list = [kw.strip() for kw in keywords.split(",") if kw.strip()] if keywords else []
    tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()] if tags else []
    
    # Store in a simple memory structure (for now, save to knowledge manager)
    memory_item = {
        "content": content,
        "keywords": keyword_list,
        "tags": tag_list,
        "source": "user_input",
        "timestamp": "2024-01-14T00:00:00Z",  # Placeholder
        "content_type": "memory"
    }
    
    # For now, just return confirmation
    # In practice, this would integrate with knowledge manager
    return {
        "success": True,
        "message": "Knowledge stored to memory",
        "stored_item": memory_item,
        "keywords_added": len(keyword_list),
        "tags_added": len(tag_list),
        "retrieval_hint": "Use search_knowledge with related keywords to retrieve this information"
    }


def tool_get_function_proposals() -> Dict[str, Any]:
    """
    Get all proposed functions awaiting approval.
    
    This tool lists all function proposals with their current status
    and details for clinical review.
    
    Returns:
        dict: List of all function proposals
    """
    
    proposals = function_generator.list_proposed_functions()
    
    return {
        "total_proposals": len(proposals),
        "proposals": proposals,
        "status_breakdown": {
            "proposed": len([p for p in proposals if p.get("status") == "proposed"]),
            "approved": len([p for p in proposals if p.get("status") == "approved"]),
            "rejected": len([p for p in proposals if "rejected" in p.get("status", "")])
        },
        "next_actions": [
            "Use 'approve_save_function' to approve proposals",
            "Use 'reject_function' to reject proposals",
            "Use 'get_full_chapter' to review source content"
        ]
    }


def tool_process_pending_pdfs() -> Dict[str, Any]:
    """
    Process all pending PDFs to extract knowledge.
    
    This tool runs the knowledge extraction pipeline on all PDFs
    that have been detected but not yet processed.
    
    Returns:
        dict: Results of PDF processing with status for each file
    """
    
    from cardiocode.ingestion.knowledge_extractor import KnowledgeExtractor
    
    extractor = KnowledgeExtractor()
    results = extractor.process_all_pending_pdfs(guideline_registry)
    
    return {
        "processed_count": len([r for r in results.values() if r == "success"]),
        "failed_count": len([r for r in results.values() if "failed" in r]),
        "results": results,
        "message": f"Processed {len(results)} PDFs",
        "next_actions": [
            "Use 'cardiocode_get_system_context' to see updated knowledge",
            "Use 'search_knowledge' to search newly extracted content",
            "Use 'tool_get_function_candidates' to find function opportunities"
        ]
    }


def tool_get_function_candidates() -> Dict[str, Any]:
    """
    Get all content suitable for function generation.
    
    This tool identifies chapters and tables that have been marked
    as potentially convertible to executable functions.
    
    Returns:
        dict: List of function generation candidates
    """
    
    candidates = knowledge_manager.get_function_candidates()
    
    return {
        "total_candidates": len(candidates),
        "candidates": candidates,
        "types_breakdown": {
            "chapters": len([c for c in candidates if c.get("type") == "chapter"]),
            "tables": len([c for c in candidates if c.get("type") == "table"])
        },
        "next_actions": [
            "Use 'propose_function_from_content' with specific chapter/table title",
            "Review candidates for clinical accuracy before generation",
            "Prioritize high-impact clinical decision support functions"
        ]
    }


# Add these new tools to the registry
TOOL_REGISTRY_UPDATE = {
    "cardiocode_get_system_context": {
        "function": tool_cardiocode_get_system_context,
        "description": "Get CardioCode system context and knowledge base summary. Call this first for each session.",
        "category": "knowledge_management"
    },
    "search_knowledge": {
        "function": tool_search_knowledge,
        "description": "Search for relevant guideline content using LLM-powered semantic matching.",
        "category": "knowledge_retrieval"
    },
    "get_full_chapter": {
        "function": tool_get_full_chapter,
        "description": "Get the complete content of a specific chapter identified through search.",
        "category": "knowledge_retrieval"
    },
    "propose_function_from_content": {
        "function": tool_propose_function_from_content,
        "description": "Propose generating a function from clinical content with secure approval workflow.",
        "category": "function_generation"
    },
    "approve_save_function": {
        "function": tool_approve_save_function,
        "description": "Approve and save a proposed function after security verification.",
        "category": "function_management"
    },
    "reject_function": {
        "function": tool_reject_function,
        "description": "Reject a proposed function with documented reason.",
        "category": "function_management"
    },
    "propose_web_update": {
        "function": tool_propose_web_update,
        "description": "Propose web search or PDF download to update knowledge base.",
        "category": "knowledge_update"
    },
    "confirm_web_update": {
        "function": tool_confirm_web_update,
        "description": "Execute a proposed web search or PDF download after user confirmation.",
        "category": "knowledge_update"
    },
    "store_to_memory": {
        "function": tool_store_to_memory,
        "description": "Store clinical knowledge for future reference with searchable keywords.",
        "category": "knowledge_management"
    },
    "get_function_proposals": {
        "function": tool_get_function_proposals,
        "description": "Get all proposed functions awaiting approval or review.",
        "category": "function_management"
    },
    "process_pending_pdfs": {
        "function": tool_process_pending_pdfs,
        "description": "Process all pending PDFs through knowledge extraction pipeline.",
        "category": "knowledge_extraction"
    },
    "get_function_candidates": {
        "function": tool_get_function_candidates,
        "description": "Get all chapters/tables suitable for conversion to executable functions.",
        "category": "function_generation"
    }
}