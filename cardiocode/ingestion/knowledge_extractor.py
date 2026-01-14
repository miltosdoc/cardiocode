"""
Knowledge Content Extractor for CardioCode.

Extracts and organizes guideline content from PDFs for LLM-driven retrieval.
Chapters and tables are stored with keywords for intelligent content selection.
"""

from __future__ import annotations
import json
import hashlib
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False
    print("Warning: PyMuPDF not installed. pip install pymupdf")

from cardiocode.ingestion.pdf_watcher import (
    GuidelineRegistry,
    PDFMetadata,
    NotificationManager,
)


@dataclass
class Chapter:
    """Represents a guideline chapter with its content."""
    number: str
    title: str
    start_page: int
    end_page: int
    raw_text: str
    keywords: List[str]
    tables: List[Dict[str, Any]]
    function_potential: str = "raw"  # "auto_generate", "raw", "flagged"


@dataclass
class Table:
    """Represents a table extracted from guideline."""
    title: str
    page_number: int
    content: str
    bbox: Optional[Tuple[float, float, float, float]] = None
    function_potential: str = "raw"


class KnowledgeExtractor:
    """Extracts and structures knowledge from guideline PDFs."""
    
    def __init__(self, registry_path: str = "cardiocode/knowledge_index.json"):
        self.registry_path = Path(registry_path)
        self.knowledge_index: Dict[str, Dict[str, Any]] = {}
        self._load_index()
    
    def _load_index(self):
        """Load knowledge index from disk."""
        if self.registry_path.exists():
            with open(self.registry_path, 'r') as f:
                self.knowledge_index = json.load(f)
    
    def _save_index(self):
        """Save knowledge index to disk."""
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.registry_path, 'w') as f:
            json.dump(self.knowledge_index, f, indent=2, default=str)
    
    def extract_from_pdf(self, pdf_path: str, metadata: PDFMetadata) -> Dict[str, Any]:
        """Extract structured content from a guideline PDF."""
        
        if not HAS_PYMUPDF:
            raise ImportError("PyMuPDF is required for PDF extraction")
        
        # Check if file exists before processing
        from pathlib import Path
        if not Path(pdf_path).exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        with fitz.open(pdf_path) as doc:
            # Get basic info
            total_pages = len(doc)
            
            # Try to get TOC first
            toc = doc.get_toc()
            
        # Extract chapters
        try:
            chapters = self._extract_chapters(doc, toc)
        except Exception as e:
            print(f"Error extracting chapters from {pdf_path}: {e}")
            chapters = []
            
            # Extract tables
            tables = self._extract_tables(doc)
            
            # Assign tables to chapters
            self._assign_tables_to_chapters(chapters, tables)
            
            # Generate keywords for each chapter
            self._generate_keywords(chapters)
            
            # Determine function potential
            self._assess_function_potential(chapters, tables)
            
            return {
                "guideline_info": {
                    "filename": metadata.filename,
                    "type": metadata.guideline_type,
                    "year": metadata.guideline_year,
                    "total_pages": total_pages,
                    "extracted_at": datetime.now().isoformat(),
                },
                "chapters": [self._chapter_to_dict(ch) for ch in chapters],
                "tables": [self._table_to_dict(t) for t in tables],
            }
    
    def _extract_chapters(self, doc, toc: List) -> List[Chapter]:
        """Extract chapters using TOC when available, falling back to heading detection."""
        chapters = []
        
        if toc:
            # Use TOC as primary source
            for i, toc_item in enumerate(toc):
                if len(toc_item) >= 2:
                    level, title = toc_item[0], toc_item[1]
                    page = toc_item[2] if len(toc_item) > 2 else 0
                    
                    # Only extract top-level chapters (level 1 or 2)
                    if level <= 2 and len(title) > 10:
                        chapter = self._create_chapter_from_toc(doc, title, page, level)
                        if chapter:
                            chapters.append(chapter)
        else:
            # Fallback to heading detection
            chapters = self._extract_chapters_by_headings(doc)
        
        return chapters
    
    def _create_chapter_from_toc(self, doc, title: str, page: int, level: int) -> Optional[Chapter]:
        """Create a chapter from TOC information."""
        # Extract text from page range (rough estimate)
        start_page = max(0, page - 1)
        
        # Estimate end page by finding next major chapter
        end_page = min(len(doc), start_page + 20)  # Default 20 pages per chapter
        
        # Try to be smarter about end page detection
        chapter_text = ""
        for p in range(start_page, end_page):
            page_text = doc[p].get_text()
            chapter_text += page_text + "\n\n"
            
            # Stop if we hit a major heading (rough heuristic)
            if p > start_page and self._is_major_heading(page_text):
                break
        
        return Chapter(
            number=str(level),
            title=title.strip(),
            start_page=start_page,
            end_page=end_page,
            raw_text=chapter_text.strip(),
            keywords=[],
            tables=[],
            function_potential="raw"
        )
    
    def _extract_chapters_by_headings(self, doc) -> List[Chapter]:
        """Extract chapters by detecting major headings in text."""
        chapters = []
        current_chapter = None
        
        for page_num in range(len(doc)):
            page = doc[page]
            blocks = page.get_text("dict")["blocks"]
            
            for block in blocks:
                if block["type"] == 0:  # Text block
                    text = block["text"].strip()
                    
                    # Detect major headings (all caps, large font, or numbered)
                    if self._is_major_heading(text):
                        # Save previous chapter
                        if current_chapter:
                            chapters.append(current_chapter)
                        
                        # Start new chapter
                        current_chapter = Chapter(
                            number=str(len(chapters) + 1),
                            title=text,
                            start_page=page_num,
                            end_page=page_num,
                            raw_text="",
                            keywords=[],
                            tables=[],
                            function_potential="raw"
                        )
                    elif current_chapter:
                        # Add text to current chapter
                        current_chapter.raw_text += text + "\n"
        
        # Don't forget the last chapter
        if current_chapter:
            chapters.append(current_chapter)
        
        return chapters
    
    def _is_major_heading(self, text: str) -> bool:
        """Heuristically detect if text is a major heading."""
        # Skip very short text
        if len(text) < 10:
            return False
        
        # All caps with reasonable length
        if text.isupper() and len(text) > 15:
            return True
        
        # Numbered headings (e.g., "1. Diagnosis", "2. Treatment")
        if re.match(r'^[0-9]+\.[0-9]*\s+[A-Z]', text):
            return True
        
        # Common ESC guideline patterns
        heading_patterns = [
            r'^\d+\s+[A-Z][a-z]',  # "1 Introduction"
            r'^[A-Z][a-z]+[^.]*:$',  # "Introduction:", "Diagnosis:"
            r'^[A-Z]{3,}$',  # "ESC", "ACS"
        ]
        
        return any(re.match(pattern, text.strip()) for pattern in heading_patterns)
    
    def _extract_tables(self, doc) -> List[Table]:
        """Extract tables from PDF."""
        tables = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # Find tables using PyMuPDF
            page_tables = page.find_tables()
            
            for i, table in enumerate(page_tables):
                # Convert table to text
                table_text = self._table_to_text(table)
                
                # Generate a title from surrounding context
                table_title = self._extract_table_title(doc, page_num, table.bbox)
                
                tables.append(Table(
                    title=table_title,
                    page_number=page_num,
                    content=table_text,
                    bbox=table.bbox
                ))
        
        return tables
    
    def _table_to_text(self, table) -> str:
        """Convert PyMuPDF table to readable text."""
        if not table:
            return ""
        
        rows = []
        for row in table:
            row_text = " | ".join([cell or "" for cell in row])
            rows.append(row_text)
        
        return "\n".join(rows)
    
    def _extract_table_title(self, doc, page_num: int, bbox: Optional[Tuple]) -> str:
        """Extract table title from text before the table."""
        if not bbox:
            return f"Table on page {page_num + 1}"
        
        # Look for text above the table bbox
        page = doc[page_num]
        text_blocks = page.get_text("dict")["blocks"]
        
        title_candidates = []
        for block in text_blocks:
            if block["type"] == 0 and block["bbox"][1] < bbox[1]:  # Above the table
                text = block["text"].strip()
                if len(text) > 5 and len(text) < 100:
                    title_candidates.append(text)
        
        return title_candidates[0] if title_candidates else f"Table on page {page_num + 1}"
    
    def _assign_tables_to_chapters(self, chapters: List[Chapter], tables: List[Table]):
        """Assign tables to appropriate chapters based on page numbers."""
        for table in tables:
            for chapter in chapters:
                if chapter.start_page <= table.page_number <= chapter.end_page:
                    chapter.tables.append(table)
                    break
    
    def _generate_keywords(self, chapters: List[Chapter]):
        """Generate keywords for each chapter using simple heuristics."""
        for chapter in chapters:
            # Extract medical terms and key phrases
            text = chapter.raw_text.lower()
            
            # Common cardiology terms to look for
            medical_terms = set()
            
            # Disease/conditions
            if re.search(r'\b(aortic stenosis|heart failure|atrial fibrillation|pulmonary hypertension|myocardial infarction)\b', text):
                medical_terms.update(re.findall(r'\b(aortic stenosis|heart failure|atrial fibrillation|pulmonary hypertension|myocardial infarction)\b', text))
            
            # Treatments/procedures
            if re.search(r'\b(tavi|savr|anticoagulation|beta blocker|ace inhibitor|icd|pci)\b', text):
                medical_terms.update(re.findall(r'\b(tavi|savr|anticoagulation|beta blocker|ace inhibitor|icd|pci)\b', text))
            
            # Clinical concepts
            if re.search(r'\b(risk stratification|diagnosis|treatment|monitoring|follow up|contraindication)\b', text):
                medical_terms.update(re.findall(r'\b(risk stratification|diagnosis|treatment|monitoring|follow up|contraindication)\b', text))
            
            # Extract unique terms from chapter title
            title_terms = re.findall(r'\b[A-Za-z]{4,}\b', chapter.title.lower())
            medical_terms.update([term for term in title_terms if len(term) > 4])
            
            chapter.keywords = list(medical_terms)[:15]  # Limit to top 15
    
    def _assess_function_potential(self, chapters: List[Chapter], tables: List[Table]):
        """Assess which chapters/tables could be converted to functions."""
        
        # Function potential patterns
        function_patterns = {
            'auto_generate': [
                r'score|risk.*calculator|classification.*system',
                r'table.*recommendation|dosing.*table',
                r'algorithm.*step.*by.*step|flowchart'
            ],
            'flagged': [
                r'decision.*tree|complex.*algorithm',
                r'multi.*factor.*risk|composite.*endpoint'
            ]
        }
        
        # Assess chapters
        for chapter in chapters:
            text = chapter.raw_text.lower()
            
            # Check for auto-generation patterns
            if any(re.search(pattern, text) for pattern in function_patterns['auto_generate']):
                chapter.function_potential = "auto_generate"
            # Check for flagged patterns
            elif any(re.search(pattern, text) for pattern in function_patterns['flagged']):
                chapter.function_potential = "flagged"
        
        # Assess tables
        for table in tables:
            text = table.content.lower()
            
            # Look for structured data patterns
            if re.search(r'parameter|factor|score|class.*[i-iii]', text):
                table.function_potential = "auto_generate"
            elif re.search(r'multi.*criteria|complex.*decision', text):
                table.function_potential = "flagged"
    
    def _chapter_to_dict(self, chapter: Chapter) -> Dict[str, Any]:
        """Convert chapter to dictionary for JSON serialization."""
        return {
            "number": chapter.number,
            "title": chapter.title,
            "start_page": chapter.start_page,
            "end_page": chapter.end_page,
            "raw_text": chapter.raw_text,
            "keywords": chapter.keywords,
            "tables": [self._table_to_dict(t) for t in chapter.tables],
            "function_potential": chapter.function_potential,
        }
    
    def _table_to_dict(self, table: Table) -> Dict[str, Any]:
        """Convert table to dictionary for JSON serialization."""
        return {
            "title": table.title,
            "page_number": table.page_number,
            "content": table.content,
            "bbox": table.bbox,
            "function_potential": table.function_potential,
        }
    
    def process_all_pending_pdfs(self, registry: GuidelineRegistry) -> Dict[str, Any]:
        """Process all pending PDFs in the registry."""
        results = {}
        
        pending_pdfs = registry.get_pending()
        
        for pdf_metadata in pending_pdfs:
            try:
                print(f"Processing: {pdf_metadata.filename}")
                
                # Normalize path for cross-platform compatibility
                from pathlib import Path
                normalized_path = Path(pdf_metadata.filepath).as_posix()
                
                # Extract content
                content = self.extract_from_pdf(str(normalized_path), pdf_metadata)
                
                # Store in index
                self.knowledge_index[pdf_metadata.file_hash] = content
                
                # Update registry status
                registry.update(pdf_metadata.file_hash, processed=True, processing_status="completed")
                
                results[pdf_metadata.filename] = "success"
                print(f"Successfully processed: {pdf_metadata.filename}")
                
            except Exception as e:
                print(f"Failed to process {pdf_metadata.filename}: {e}")
                registry.update(pdf_metadata.file_hash, processing_status="failed", notes=str(e))
                results[pdf_metadata.filename] = f"failed: {e}"
        
        # Save index
        self._save_index()
        
        return results