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
    
    # Mapping of query concepts to relevant guideline types for boosting
    GUIDELINE_TYPE_RELEVANCE = {
        # CVD Prevention concepts
        'cvd_prevention': [
            'score2', 'score2-op', 'primary prevention', 'cardiovascular risk', 
            'risk estimation', 'ldl', 'cholesterol', 'lipid', 'statin', 
            'blood pressure', 'hypertension', 'smoking', 'lifestyle',
            'ethnicity', 'south asian', 'risk factor', 'healthy', 'screening',
            'ascvd', 'lifetime risk', '10-year risk', 'prevention',
        ],
        # Heart Failure concepts
        'heart_failure': [
            'heart failure', 'hfref', 'hfpef', 'hfmref', 'lvef', 'ejection fraction',
            'nt-probnp', 'bnp', 'nyha', 'cardiomyopathy', 'sglt2', 'arni',
            'sacubitril', 'valsartan', 'diuretic', 'congestion',
        ],
        # Syncope concepts
        'syncope': [
            'syncope', 'fainting', 'loss of consciousness', 'presyncope',
            'vasovagal', 'orthostatic', 'tilt test', 'blackout',
        ],
        # Cardiac Pacing concepts
        'cardiac_pacing': [
            'pacemaker', 'pacing', 'crt', 'resynchronization', 'bradycardia',
            'av block', 'sinus node', 'bundle branch', 'lead', 'icd',
        ],
        # Ventricular Arrhythmias concepts
        'ventricular_arrhythmias': [
            'ventricular tachycardia', 'vt', 'ventricular fibrillation', 'vf',
            'sudden cardiac death', 'scd', 'icd', 'ablation', 'arrhythmia',
            'brugada', 'long qt', 'arvc', 'hcm risk',
        ],
        # Pulmonary Embolism concepts
        'pulmonary_embolism': [
            'pulmonary embolism', 'pe', 'dvt', 'vte', 'thrombus', 'anticoagulation',
            'wells score', 'pesi', 'd-dimer', 'ctpa',
        ],
        # Pulmonary Hypertension concepts
        'pulmonary_hypertension': [
            'pulmonary hypertension', 'pah', 'right heart', 'who functional class',
            'pulmonary arterial', 'pvr', 'mpap',
        ],
        # Valvular Heart Disease concepts
        'valvular_heart_disease': [
            'aortic stenosis', 'aortic regurgitation', 'mitral regurgitation',
            'mitral stenosis', 'tricuspid', 'tavi', 'tavr', 'savr', 'valve',
            'prosthetic', 'endocarditis',
        ],
        # Cardio-Oncology concepts
        'cardio_oncology': [
            'cardio-oncology', 'cancer', 'chemotherapy', 'anthracycline',
            'trastuzumab', 'cardiotoxicity', 'radiation', 'oncology',
        ],
        # Congenital Heart Disease concepts
        'congenital_heart_disease': [
            'congenital', 'achd', 'fontan', 'tetralogy', 'asd', 'vsd',
            'eisenmenger', 'shunt', 'grown-up congenital',
        ],
        # Sports Cardiology concepts
        'sports_cardiology': [
            'sports', 'athlete', 'exercise', 'training', 'competition',
            'pre-participation', 'return to play', 'exertion',
        ],
    }
    
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
        
        # Determine which guideline types are most relevant to this query
        relevant_types = self._get_relevant_guideline_types(query_lower)
        
        results = []
        
        # Search each guideline
        for file_hash, info in index.get("guidelines", {}).items():
            slug = info.get("slug")
            if not slug:
                continue
            
            guideline = self._load_guideline(slug)
            if not guideline:
                continue
            
            guideline_type = guideline.get("type", "unknown")
            
            # Calculate guideline-type relevance boost
            type_boost = 0.0
            if guideline_type in relevant_types:
                # Higher boost for more relevant types (based on match count)
                type_boost = relevant_types[guideline_type] * 5.0  # 5 points per matched concept
            
            # Search chapters
            for chapter in guideline.get("chapters", []):
                score, matched = self._score_chapter(chapter, query_lower, query_terms)
                
                # Apply guideline type boost
                score += type_boost
                
                if score > 0:
                    results.append(SearchResult(
                        guideline_slug=slug,
                        guideline_title=guideline.get("title", "Unknown"),
                        guideline_type=guideline_type,
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
    
    def _get_relevant_guideline_types(self, query: str) -> Dict[str, int]:
        """Determine which guideline types are most relevant to the query."""
        relevant_types = {}
        
        for guideline_type, concepts in self.GUIDELINE_TYPE_RELEVANCE.items():
            match_count = 0
            for concept in concepts:
                if concept in query:
                    match_count += 1
            
            if match_count > 0:
                relevant_types[guideline_type] = match_count
        
        return relevant_types
    
    # Clinical synonyms for query expansion
    CLINICAL_SYNONYMS = {
        'cholesterol': ['lipid', 'ldl', 'hdl', 'non-hdl', 'dyslipidemia'],
        'lipid': ['cholesterol', 'ldl', 'hdl', 'triglyceride'],
        'ldl': ['cholesterol', 'lipid', 'ldl-c'],
        'blood pressure': ['hypertension', 'bp', 'sbp', 'dbp'],
        'hypertension': ['blood pressure', 'high blood pressure', 'htn'],
        'heart attack': ['myocardial infarction', 'mi', 'stemi', 'nstemi'],
        'stroke': ['cerebrovascular', 'cva', 'tia'],
        'fainting': ['syncope', 'loss of consciousness'],
        'syncope': ['fainting', 'blackout', 'collapse'],
        'pacemaker': ['pacing', 'crt', 'pm'],
        'defibrillator': ['icd', 's-icd'],
        'ethnicity': ['ethnic', 'race', 'south asian', 'african'],
        'prevention': ['preventive', 'prophylaxis', 'primary prevention'],
        'risk': ['risk factor', 'risk score', 'risk assessment'],
        'healthy': ['apparently healthy', 'asymptomatic', 'no symptoms'],
        'screening': ['check-up', 'assessment', 'evaluation'],
    }
    
    def _extract_terms(self, query: str) -> List[str]:
        """Extract searchable terms from query with synonym expansion."""
        # Remove common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'for', 'with', 'in', 'of', 'to', 
                      'what', 'how', 'when', 'should', 'is', 'are', 'can', 'do', 'does',
                      'patient', 'patients', 'person', 'people'}
        
        terms = []
        for word in re.findall(r'\b\w+\b', query):
            if word not in stop_words and len(word) > 2:
                terms.append(word)
        
        # Expand with synonyms
        expanded_terms = list(terms)  # Copy original terms
        for term in terms:
            if term in self.CLINICAL_SYNONYMS:
                for synonym in self.CLINICAL_SYNONYMS[term]:
                    if synonym not in expanded_terms:
                        expanded_terms.append(synonym)
        
        return expanded_terms
    
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
