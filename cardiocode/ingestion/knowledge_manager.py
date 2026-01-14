"""
Knowledge Manager for CardioCode.

Provides LLM-driven search and retrieval from extracted guideline content.
Manages the knowledge index and provides content selection capabilities.
"""

from __future__ import annotations
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

from cardiocode.ingestion.knowledge_extractor import Chapter, Table


@dataclass
class SearchResult:
    """Result of searching for content."""
    chapter: Dict[str, Any]
    relevance_score: float
    matched_keywords: List[str]
    selected_sections: List[str] = None


class KnowledgeManager:
    """Manages and searches extracted guideline knowledge."""
    
    def __init__(self, index_path: str = "cardiocode/knowledge_index.json"):
        self.index_path = Path(index_path)
        self.knowledge_index: Dict[str, Dict[str, Any]] = {}
        self._load_index()
    
    def _load_index(self):
        """Load knowledge index from disk."""
        if self.index_path.exists():
            with open(self.index_path, 'r') as f:
                self.knowledge_index = json.load(f)
    
    def _save_index(self):
        """Save knowledge index to disk."""
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.index_path, 'w') as f:
            json.dump(self.knowledge_index, f, indent=2, default=str)
    
    def search_knowledge(self, query: str, top_k: int = 5) -> List[SearchResult]:
        """Search for relevant content across all guidelines."""
        
        query_lower = query.lower()
        query_terms = self._extract_query_terms(query_lower)
        
        results = []
        
        # Search through all guidelines
        for file_hash, guideline_data in self.knowledge_index.items():
            guideline_name = guideline_data.get("guideline_info", {}).get("filename", "Unknown")
            
            # Search chapters
            for chapter in guideline_data.get("chapters", []):
                score = self._calculate_relevance_score(
                    chapter, query_lower, query_terms, guideline_name
                )
                
                if score > 0:
                    results.append(SearchResult(
                        chapter=chapter,
                        relevance_score=score,
                        matched_keywords=self._get_matched_keywords(chapter, query_terms)
                    ))
        
        # Sort by relevance score
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return results[:top_k]
    
    def _extract_query_terms(self, query: str) -> List[str]:
        """Extract key terms from user query."""
        # Split on common stop words and punctuation
        stop_words = {'the', 'and', 'or', 'for', 'with', 'in', 'of', 'to', 'what', 'how', 'when', 'should'}
        
        terms = []
        for word in re.findall(r'\b\w+\b', query):
            if word not in stop_words and len(word) > 2:
                terms.append(word)
        
        return terms
    
    def _calculate_relevance_score(
        self, 
        chapter: Dict[str, Any], 
        query_lower: str, 
        query_terms: List[str],
        guideline_name: str
    ) -> float:
        """Calculate relevance score for a chapter."""
        
        score = 0.0
        
        # Chapter title matching (highest weight)
        title = chapter.get("title", "").lower()
        title_match = self._text_similarity(title, query_lower)
        if title_match > 0.5:
            score += 10.0 * title_match
        
        # Keyword matching
        keywords = chapter.get("keywords", [])
        keyword_matches = sum(1 for kw in keywords if kw in query_terms)
        if keyword_matches > 0:
            score += 5.0 * (keyword_matches / len(keywords))
        
        # Content matching
        content = chapter.get("raw_text", "").lower()
        content_matches = query_lower.count(content)  # Exact phrase matches
        if content_matches > 0:
            score += 2.0 * content_matches
        
        # Term frequency in content
        term_matches = sum(content.count(term) for term in query_terms)
        if term_matches > 0:
            score += 1.0 * (term_matches / len(query_terms))
        
        # Boost recent guidelines slightly
        year = self.knowledge_index.get(guideline_name, {}).get("guideline_info", {}).get("year", 2020)
        if year >= 2022:
            score *= 1.1
        
        return score
    
    def _text_similarity(self, text1: str, text2: str) -> float:
        """Simple text similarity based on word overlap."""
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    def _get_matched_keywords(self, chapter: Dict[str, Any], query_terms: List[str]) -> List[str]:
        """Get list of keywords that matched the query."""
        keywords = chapter.get("keywords", [])
        return [kw for kw in keywords if kw in query_terms]
    
    def get_chapter_content(self, guideline_hash: str, chapter_title: str) -> Optional[Dict[str, Any]]:
        """Get full content of a specific chapter."""
        if guideline_hash not in self.knowledge_index:
            return None
        
        chapters = self.knowledge_index[guideline_hash].get("chapters", [])
        
        for chapter in chapters:
            if chapter.get("title", "").lower() == chapter_title.lower():
                return chapter
        
        return None
    
    def get_guideline_summary(self) -> Dict[str, Any]:
        """Get summary of all indexed guidelines."""
        summary = {
            "total_guidelines": len(self.knowledge_index),
            "guidelines": {},
            "total_chapters": 0,
            "total_tables": 0,
            "function_candidates": 0
        }
        
        for file_hash, data in self.knowledge_index.items():
            guideline_info = data.get("guideline_info", {})
            chapters = data.get("chapters", [])
            tables = data.get("tables", [])
            
            # Count function candidates
            function_candidates = sum(
                1 for ch in chapters 
                if ch.get("function_potential") == "auto_generate"
            )
            function_candidates += sum(
                1 for t in tables 
                if t.get("function_potential") == "auto_generate"
            )
            
            summary["guidelines"][file_hash] = {
                "name": guideline_info.get("filename", "Unknown"),
                "type": guideline_info.get("type", "Unknown"),
                "year": guideline_info.get("year"),
                "chapters": len(chapters),
                "tables": len(tables),
                "function_candidates": function_candidates
            }
            
            summary["total_chapters"] += len(chapters)
            summary["total_tables"] += len(tables)
            summary["function_candidates"] += function_candidates
        
        return summary
    
    def get_function_candidates(self) -> List[Dict[str, Any]]:
        """Get all chapters/tables marked for auto-generation."""
        candidates = []
        
        for file_hash, data in self.knowledge_index.items():
            guideline_info = data.get("guideline_info", {})
            
            # Check chapters
            for chapter in data.get("chapters", []):
                if chapter.get("function_potential") == "auto_generate":
                    candidates.append({
                        "guideline_hash": file_hash,
                        "guideline_name": guideline_info.get("filename"),
                        "type": "chapter",
                        "title": chapter.get("title"),
                        "content": chapter.get("raw_text")[:500] + "...",  # Preview
                    })
            
            # Check tables
            for table in data.get("tables", []):
                if table.get("function_potential") == "auto_generate":
                    candidates.append({
                        "guideline_hash": file_hash,
                        "guideline_name": guideline_info.get("filename"),
                        "type": "table",
                        "title": table.get("title"),
                        "content": table.get("content")[:300] + "...",  # Preview
                    })
        
        return candidates