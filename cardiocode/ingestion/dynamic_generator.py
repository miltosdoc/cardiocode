"""
Dynamic Function Generator for CardioCode.

Generates clinical functions from guideline content when LLM determines it's appropriate.
Implements secure two-step approval workflow for safety.
"""

from __future__ import annotations
import json
import hashlib
import uuid
import ast
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime

from cardiocode.ingestion.knowledge_manager import KnowledgeManager
from cardiocode.ingestion.knowledge_extractor import Chapter, Table


@dataclass
class FunctionProposal:
    """Represents a proposed function for user approval."""
    proposal_id: str
    function_name: str
    function_code: str
    source_type: str  # "chapter" or "table"
    source_title: str
    source_content_preview: str
    evidence_sources: List[str]
    test_cases: List[Dict[str, Any]]
    code_hash: str
    created_at: datetime = field(default_factory=datetime.now)
    status: str = "proposed"  # "proposed", "approved", "rejected", "replaced"


@dataclass
class WebUpdateProposal:
    """Represents a proposed web update."""
    proposal_id: str
    update_type: str  # "websearch", "download", "esc_check"
    query_or_url: str
    reason: str
    options: List[str]
    created_at: datetime = field(default_factory=datetime.now)


class DynamicFunctionGenerator:
    """Generates and manages dynamic clinical functions."""
    
    def __init__(self, knowledge_manager: KnowledgeManager):
        self.knowledge_manager = knowledge_manager
        self.proposals_path = Path("cardiocode/function_proposals.json")
        self.generated_path = Path("cardiocode/guidelines/generated")
        self.proposals: Dict[str, FunctionProposal] = {}
        self.web_proposals: Dict[str, WebUpdateProposal] = {}
        self._load_proposals()
        
        # Ensure directories exist
        self.generated_path.mkdir(parents=True, exist_ok=True)
        self._ensure_generated_init()
    
    def _load_proposals(self):
        """Load existing proposals from disk."""
        if self.proposals_path.exists():
            with open(self.proposals_path, 'r') as f:
                data = json.load(f)
                
                # Load function proposals
                for prop_id, prop_data in data.get("function_proposals", {}).items():
                    prop_data["created_at"] = datetime.fromisoformat(prop_data["created_at"])
                    self.proposals[prop_id] = FunctionProposal(**prop_data)
                
                # Load web proposals
                for prop_id, prop_data in data.get("web_proposals", {}).items():
                    prop_data["created_at"] = datetime.fromisoformat(prop_data["created_at"])
                    self.web_proposals[prop_id] = WebUpdateProposal(**prop_data)
    
    def _save_proposals(self):
        """Save proposals to disk."""
        self.proposals_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "function_proposals": {
                prop_id: {
                    "proposal_id": prop.proposal_id,
                    "function_name": prop.function_name,
                    "function_code": prop.function_code,
                    "source_type": prop.source_type,
                    "source_title": prop.source_title,
                    "source_content_preview": prop.source_content_preview,
                    "evidence_sources": prop.evidence_sources,
                    "test_cases": prop.test_cases,
                    "code_hash": prop.code_hash,
                    "created_at": prop.created_at.isoformat(),
                    "status": prop.status,
                } for prop_id, prop in self.proposals.items()
            },
            "web_proposals": {
                prop_id: {
                    "proposal_id": prop.proposal_id,
                    "update_type": prop.update_type,
                    "query_or_url": prop.query_or_url,
                    "reason": prop.reason,
                    "options": prop.options,
                    "created_at": prop.created_at.isoformat(),
                } for prop_id, prop in self.web_proposals.items()
            }
        }
        
        with open(self.proposals_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def _ensure_generated_init(self):
        """Ensure generated module has __init__.py."""
        init_path = self.generated_path / "__init__.py"
        if not init_path.exists():
            init_path.write_text('"""Generated clinical functions.\n\nThese functions are automatically generated from guideline content and require clinical validation before use.\n"""\n')
    
    def propose_function_from_content(
        self, 
        content_query: str,
        source_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a function proposal from content query."""
        
        # Search for relevant content
        search_results = self.knowledge_manager.search_knowledge(content_query, top_k=3)
        
        if not search_results:
            return {
                "error": "No relevant content found for function generation",
                "suggestions": "Try searching for specific topics like 'risk score' or 'recommendation table'"
            }
        
        # Use the most relevant result
        best_result = search_results[0]
        chapter = best_result.chapter
        
        # Generate function using LLM (this would call the LLM)
        function_code = self._generate_function_code(
            chapter.get("title", ""),
            chapter.get("raw_text", ""),
            chapter.get("tables", [])
        )
        
        if not function_code:
            return {
                "error": "Content is not suitable for function generation",
                "reason": "Could not identify clear input/output structure",
                "chapter_preview": chapter.get("title", "")
            }
        
        # Create proposal
        proposal_id = str(uuid.uuid4())[:8]
        code_hash = hashlib.sha256(function_code.encode()).hexdigest()[:16]
        
        proposal = FunctionProposal(
            proposal_id=proposal_id,
            function_name=self._suggest_function_name(chapter.get("title", "")),
            function_code=function_code,
            source_type="chapter",
            source_title=chapter.get("title", ""),
            source_content_preview=chapter.get("raw_text", "")[:500] + "...",
            evidence_sources=[chapter.get("title", "")],
            test_cases=self._generate_test_cases(function_code),
            code_hash=code_hash
        )
        
        self.proposals[proposal_id] = proposal
        self._save_proposals()
        
        return {
            "proposal_id": proposal_id,
            "function_name": proposal.function_name,
            "function_code": function_code,
            "source_title": proposal.source_title,
            "source_preview": proposal.source_content_preview,
            "test_cases": proposal.test_cases,
            "code_hash": proposal.code_hash,
            "next_step": "To save this function, call: approve_save_function with the proposal_id and code_hash"
        }
    
    def _generate_function_code(self, title: str, content: str, tables: List[Dict]) -> Optional[str]:
        """Generate function code from content (placeholder for LLM call)."""
        
        # This is a simplified version - in practice would call LLM
        # For now, generate based on patterns detected in content
        
        content_lower = content.lower()
        
        # Check if it's a risk score
        if re.search(r'score|risk.*calculator|points.*add', content_lower):
            return self._generate_risk_score_template(title, content)
        
        # Check if it's a recommendation table
        if re.search(r'recommendation|indication|contraindication', content_lower):
            return self._generate_recommendation_template(title, content)
        
        # Check if it's a classification system
        if re.search(r'classification|category.*[i-iii]|class.*[a-c]', content_lower):
            return self._generate_classification_template(title, content)
        
        # Not suitable for automatic generation
        return None
    
    def _generate_risk_score_template(self, title: str, content: str) -> str:
        """Generate a risk score function template."""
        
        function_name = self._suggest_function_name(title)
        
        template = f'''def {function_name}(**kwargs):
    """
    Calculate {title}.
    
    This function was generated from guideline content and requires clinical validation.
    
    Args:
        **kwargs: Risk factors and patient parameters
    
    Returns:
        dict: Score result with calculation details
    """
    
    # Extract parameters
    score = 0
    components = {{}}
    
    # TODO: Implement specific scoring logic based on guideline content
    # Example pattern:
    # if kwargs.get('age_over_65'):
    #     score += 1
    #     components['age_over_65'] = 1
    
    return {{
        "score_name": "{title}",
        "score_value": score,
        "components": components,
        "interpretation": "TODO: Add interpretation logic",
        "guideline_source": "Generated from guideline content",
        "requires_validation": True
    }}'''
        
        return template
    
    def _generate_recommendation_template(self, title: str, content: str) -> str:
        """Generate a recommendation function template."""
        
        function_name = self._suggest_function_name(title)
        
        template = f'''def {function_name}(patient_data):
    """
    Get recommendations for {title}.
    
    This function was generated from guideline content and requires clinical validation.
    
    Args:
        patient_data: dict with patient characteristics
    
    Returns:
        list: Recommendation objects with action, evidence_class, etc.
    """
    
    recommendations = []
    
    # TODO: Implement recommendation logic based on guideline content
    # Example pattern:
    # if patient_data.get('condition') == 'severe_as':
    #     recommendations.append({{
    #         "action": "Aortic valve replacement indicated",
    #         "evidence_class": "I",
    #         "evidence_level": "A",
    #         "section": "5.2"
    #     }})
    
    return {{
        "recommendations": recommendations,
        "guideline_source": "Generated from guideline content", 
        "requires_validation": True
    }}'''
        
        return template
    
    def _generate_classification_template(self, title: str, content: str) -> str:
        """Generate a classification function template."""
        
        function_name = self._suggest_function_name(title)
        
        template = f'''def {function_name}(patient_data):
    """
    Classify patients according to {title}.
    
    This function was generated from guideline content and requires clinical validation.
    
    Args:
        patient_data: dict with patient characteristics
    
    Returns:
        dict: Classification result with category and criteria
    """
    
    # TODO: Implement classification logic based on guideline content
    # Example pattern:
    # criteria = {{
    #     "major": [],
    #     "minor": [],
    #     "exclusion": []
    # }}
    
    return {{
        "classification": "{title}",
        "category": "TODO: Implement logic",
        "criteria_met": [],
        "guideline_source": "Generated from guideline content",
        "requires_validation": True
    }}'''
        
        return template
    
    def _suggest_function_name(self, title: str) -> str:
        """Suggest a function name from title."""
        # Clean up title to make valid function name
        name = title.lower()
        name = re.sub(r'[^a-z0-9\s]', '', name)
        name = re.sub(r'\s+', '_', name.strip())
        
        # Add prefix for uniqueness
        return f"generated_{name}"
    
    def _generate_test_cases(self, function_code: str) -> List[Dict[str, Any]]:
        """Generate test cases for the function."""
        
        # Basic test cases based on function type
        test_cases = []
        
        if "score" in function_code.lower():
            test_cases.append({
                "name": "Basic functionality",
                "input": {"test_parameter": "test_value"},
                "expected": "score calculation result"
            })
        
        if "recommendation" in function_code.lower():
            test_cases.append({
                "name": "Severe case",
                "input": {"condition": "severe"},
                "expected": "strong recommendation"
            })
        
        return test_cases
    
    def get_proposal(self, proposal_id: str) -> Optional[FunctionProposal]:
        """Get a specific proposal by ID."""
        return self.proposals.get(proposal_id)
    
    def approve_save_function(self, proposal_id: str, code_hash: str, function_name: str) -> Dict[str, Any]:
        """Approve and save a proposed function."""
        
        proposal = self.proposals.get(proposal_id)
        if not proposal:
            return {"error": "Proposal not found", "proposal_id": proposal_id}
        
        # Security: Verify hash matches
        if proposal.code_hash != code_hash:
            return {"error": "Code hash mismatch - proposal may have been modified"}
        
        # Validate function syntax
        try:
            ast.parse(proposal.function_code)
        except SyntaxError as e:
            return {"error": f"Syntax error in function code: {e}"}
        
        # Save function
        function_file = self.generated_path / f"{function_name}.py"
        function_file.write_text(proposal.function_code)
        
        # Update proposal status
        proposal.status = "approved"
        self._save_proposals()
        
        return {
            "success": True,
            "function_name": function_name,
            "file_path": str(function_file),
            "message": f"Function {function_name} has been saved and is ready for use"
        }
    
    def reject_function(self, proposal_id: str, reason: str) -> Dict[str, Any]:
        """Reject a proposed function."""
        
        proposal = self.proposals.get(proposal_id)
        if not proposal:
            return {"error": "Proposal not found", "proposal_id": proposal_id}
        
        proposal.status = f"rejected: {reason}"
        self._save_proposals()
        
        return {
            "success": True,
            "function_name": proposal.function_name,
            "message": f"Function {proposal.function_name} has been rejected: {reason}"
        }
    
    def propose_web_update(self, query: str, update_type: str = "websearch") -> Dict[str, Any]:
        """Propose a web search or PDF download."""
        
        proposal_id = str(uuid.uuid4())[:8]
        
        if update_type == "websearch":
            options = [
                "Search ESC website for official guidelines",
                "Search PubMed Central for peer-reviewed articles",
                "Search ESC journal (European Heart Journal)",
                "Search ACC/AHA guideline repository",
                "Custom web search (guidelines优先)"
            ]
            reason = f"Search for official guidelines and articles about: {query}"
        
        elif update_type == "download":
            options = [
                "Download from ESC website",
                "Download from provided URL",
                "Download from PubMed Central"
            ]
            reason = f"Download guidelines about: {query}"
        
        else:
            options = ["websearch", "download", "esc_check"]
            reason = f"Update information about: {query}"
        
        proposal = WebUpdateProposal(
            proposal_id=proposal_id,
            update_type=update_type,
            query_or_url=query,
            reason=reason,
            options=options
        )
        
        self.web_proposals[proposal_id] = proposal
        self._save_proposals()
        
        return {
            "proposal_id": proposal_id,
            "update_type": update_type,
            "query": query,
            "reason": reason,
            "options": options,
            "next_step": "To proceed, call: confirm_web_update with proposal_id and chosen option"
        }
    
    def confirm_web_update(self, proposal_id: str, chosen_option: str) -> Dict[str, Any]:
        """Execute a proposed web update."""
        
        proposal = self.web_proposals.get(proposal_id)
        if not proposal:
            return {"error": "Proposal not found", "proposal_id": proposal_id}
        
        if chosen_option not in proposal.options:
            return {"error": "Invalid option", "valid_options": proposal.options}
        
        # Execute the update (placeholder for actual implementation)
        result = self._execute_web_update(proposal.update_type, proposal.query_or_url, chosen_option)
        
        # Remove proposal after execution
        del self.web_proposals[proposal_id]
        self._save_proposals()
        
        return result
    
    def _execute_web_update(self, update_type: str, query: str, option: str) -> Dict[str, Any]:
        """Execute actual web update."""
        
        # Validate document type preference during web search
        def is_guideline_preference(option: str) -> bool:
            """Check if option prioritizes guidelines over presentations."""
            guideline_keywords = ["guideline", "article", "journal", "official", "peer-reviewed", "ESC", "AHA", "ACC"]
            presentation_keywords = ["powerpoint", "slide", "presentation", "ppt"]
            
            option_lower = option.lower()
            has_guideline = any(keyword in option_lower for keyword in guideline_keywords)
            has_presentation = any(keyword in option_lower for keyword in presentation_keywords)
            
            return has_guideline and not has_presentation
        
        # Placeholder implementation
        if update_type == "websearch":
            return {
                "action": "web_search",
                "query": query,
                "source": option,
                "status": "would_execute_search",
                "message": f"Would search for: {query} using {option}",
                "prioritizes_guidelines": is_guideline_preference(option)
            }
        
        elif update_type == "download":
            return {
                "action": "download",
                "url": query if query.startswith("http") else None,
                "source": option,
                "status": "would_download",
                "message": f"Would download from: {option}"
            }
        
        return {"error": "Unknown update type", "update_type": update_type}
    
    def list_proposed_functions(self) -> List[Dict[str, Any]]:
        """List all proposed functions."""
        
        return [
            {
                "proposal_id": prop.proposal_id,
                "function_name": prop.function_name,
                "source_title": prop.source_title,
                "status": prop.status,
                "created_at": prop.created_at.isoformat(),
                "preview": prop.source_content_preview[:200] + "..."
            }
            for prop in self.proposals.values()
        ]
    
    def list_web_proposals(self) -> List[Dict[str, Any]]:
        """List all web update proposals."""
        
        return [
            {
                "proposal_id": prop.proposal_id,
                "update_type": prop.update_type,
                "query": prop.query_or_url,
                "reason": prop.reason,
                "options": prop.options,
                "created_at": prop.created_at.isoformat()
            }
            for prop in self.web_proposals.values()
        ]