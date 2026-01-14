"""
Knowledge Search for CardioCode.

Provides search across extracted guideline content.
No embeddings - uses keyword and content matching.
"""

from __future__ import annotations
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class SearchResult:
    """A search result with relevance score."""
    guideline_slug: str
    guideline_title: str
    guideline_type: str
    guideline_year: Optional[int]
    chapter_title: str
    chapter_number: str
    content_preview: str
    keywords: List[str]
    matched_terms: List[str]
    score: float
    tables: List[Dict[str, Any]]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "guideline": {
                "slug": self.guideline_slug,
                "title": self.guideline_title,
                "type": self.guideline_type,
                "year": self.guideline_year,
            },
            "chapter": {
                "title": self.chapter_title,
                "number": self.chapter_number,
            },
            "preview": self.content_preview,
            "keywords": self.keywords,
            "matched_terms": self.matched_terms,
            "score": round(self.score, 2),
            "tables_count": len(self.tables),
        }


class KnowledgeSearch:
    """Search across extracted guideline knowledge."""
    
    def __init__(self, base_path: Path = None):
        if base_path is None:
            base_path = Path(__file__).parent.parent
        
        self.base_path = Path(base_path)
        self.knowledge_dir = self.base_path / "knowledge" / "chapters"
        self.index_file = self.base_path / "knowledge" / "guidelines.json"
        
        # Cache loaded guidelines
        self._guidelines_cache: Dict[str, Dict[str, Any]] = {}
        self._index: Optional[Dict[str, Any]] = None
    
    def _load_index(self) -> Dict[str, Any]:
        """Load the guidelines index."""
        if self._index is not None:
            return self._index
        
        if self.index_file.exists():
            with open(self.index_file, 'r', encoding='utf-8') as f:
                self._index = json.load(f)
        else:
            self._index = {"guidelines": {}, "last_scan": None}
        
        return self._index
    
    def _load_guideline(self, slug: str) -> Optional[Dict[str, Any]]:
        """Load a specific guideline's chapter data."""
        if slug in self._guidelines_cache:
            return self._guidelines_cache[slug]
        
        chapter_file = self.knowledge_dir / f"{slug}.json"
        if not chapter_file.exists():
            return None
        
        with open(chapter_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self._guidelines_cache[slug] = data
            return data
    
    def get_status(self) -> Dict[str, Any]:
        """Get status of knowledge base."""
        index = self._load_index()
        guidelines = index.get("guidelines", {})
        
        return {
            "total_guidelines": len(guidelines),
            "last_scan": index.get("last_scan"),
            "guidelines": [
                {
                    "slug": info.get("slug"),
                    "title": info.get("title"),
                    "type": info.get("type"),
                    "year": info.get("year"),
                    "chapters": info.get("chapters_count", 0),
                }
                for info in guidelines.values()
            ]
        }
    
    def search(self, query: str, max_results: int = 5) -> List[SearchResult]:
        """Search for relevant content across all guidelines."""
        index = self._load_index()
        
        # Extract query terms
        query_lower = query.lower()
        query_terms = self._extract_terms(query_lower)
        
        results = []
        
        # Search each guideline
        for file_hash, info in index.get("guidelines", {}).items():
            slug = info.get("slug")
            if not slug:
                continue
            
            guideline = self._load_guideline(slug)
            if not guideline:
                continue
            
            # Search chapters
            for chapter in guideline.get("chapters", []):
                score, matched = self._score_chapter(chapter, query_lower, query_terms)
                
                if score > 0:
                    results.append(SearchResult(
                        guideline_slug=slug,
                        guideline_title=guideline.get("title", "Unknown"),
                        guideline_type=guideline.get("type", "unknown"),
                        guideline_year=guideline.get("year"),
                        chapter_title=chapter.get("title", ""),
                        chapter_number=chapter.get("number", ""),
                        content_preview=chapter.get("content", "")[:500] + "...",
                        keywords=chapter.get("keywords", []),
                        matched_terms=matched,
                        score=score,
                        tables=chapter.get("tables", []),
                    ))
        
        # Sort by score
        results.sort(key=lambda x: x.score, reverse=True)
        
        return results[:max_results]
    
    def _extract_terms(self, query: str) -> List[str]:
        """Extract searchable terms from query."""
        # Remove common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'for', 'with', 'in', 'of', 'to', 
                      'what', 'how', 'when', 'should', 'is', 'are', 'can', 'do', 'does'}
        
        terms = []
        for word in re.findall(r'\b\w+\b', query):
            if word not in stop_words and len(word) > 2:
                terms.append(word)
        
        return terms
    
    def _score_chapter(self, chapter: Dict, query: str, terms: List[str]) -> tuple[float, List[str]]:
        """Calculate relevance score for a chapter."""
        score = 0.0
        matched = []
        
        title = chapter.get("title", "").lower()
        content = chapter.get("content", "").lower()
        keywords = [k.lower() for k in chapter.get("keywords", [])]
        
        # Title matching (highest weight)
        for term in terms:
            if term in title:
                score += 10.0
                matched.append(term)
        
        # Exact phrase in title
        if query in title:
            score += 20.0
        
        # Keyword matching
        for term in terms:
            if term in keywords:
                score += 5.0
                if term not in matched:
                    matched.append(term)
        
        # Content matching
        for term in terms:
            count = content.count(term)
            if count > 0:
                score += min(count * 0.5, 5.0)  # Cap at 5 points per term
                if term not in matched:
                    matched.append(term)
        
        # Exact phrase in content
        if query in content:
            score += 3.0
        
        return score, matched
    
    def get_chapter(self, guideline_slug: str, chapter_title: str) -> Optional[Dict[str, Any]]:
        """Get full chapter content."""
        guideline = self._load_guideline(guideline_slug)
        if not guideline:
            return None
        
        for chapter in guideline.get("chapters", []):
            if chapter.get("title", "").lower() == chapter_title.lower():
                return {
                    "guideline": {
                        "slug": guideline_slug,
                        "title": guideline.get("title"),
                        "type": guideline.get("type"),
                        "year": guideline.get("year"),
                    },
                    "chapter": chapter,
                }
        
        # Try partial match
        for chapter in guideline.get("chapters", []):
            if chapter_title.lower() in chapter.get("title", "").lower():
                return {
                    "guideline": {
                        "slug": guideline_slug,
                        "title": guideline.get("title"),
                        "type": guideline.get("type"),
                        "year": guideline.get("year"),
                    },
                    "chapter": chapter,
                }
        
        return None
    
    def get_all_chapters(self, guideline_slug: str) -> Optional[Dict[str, Any]]:
        """Get all chapters for a guideline."""
        guideline = self._load_guideline(guideline_slug)
        if not guideline:
            return None
        
        return {
            "guideline": {
                "slug": guideline_slug,
                "title": guideline.get("title"),
                "type": guideline.get("type"),
                "year": guideline.get("year"),
            },
            "chapters": [
                {
                    "number": ch.get("number"),
                    "title": ch.get("title"),
                    "pages": f"{ch.get('start_page')}-{ch.get('end_page')}",
                    "keywords": ch.get("keywords", []),
                    "tables_count": len(ch.get("tables", [])),
                }
                for ch in guideline.get("chapters", [])
            ]
        }


# Convenience functions
def search_knowledge(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """Search the knowledge base."""
    searcher = KnowledgeSearch()
    results = searcher.search(query, max_results)
    return [r.to_dict() for r in results]


def get_knowledge_status() -> Dict[str, Any]:
    """Get knowledge base status."""
    return KnowledgeSearch().get_status()


def get_chapter_content(guideline_slug: str, chapter_title: str) -> Optional[Dict[str, Any]]:
    """Get full chapter content."""
    return KnowledgeSearch().get_chapter(guideline_slug, chapter_title)
