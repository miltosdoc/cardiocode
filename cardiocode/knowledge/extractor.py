"""
PDF Knowledge Extractor for CardioCode.

Extracts chapters, tables, and recommendations from ESC guideline PDFs.
Stores everything in searchable JSON files - no embeddings needed.
"""

from __future__ import annotations
import json
import hashlib
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False


class PDFExtractor:
    """Extracts and stores knowledge from guideline PDFs."""
    
    def __init__(self, base_path: Path = None):
        if base_path is None:
            # Find the cardiocode package directory
            base_path = Path(__file__).parent.parent
        
        self.base_path = Path(base_path)
        self.source_dir = self.base_path.parent / "source_pdfs"
        self.knowledge_dir = self.base_path / "knowledge" / "chapters"
        self.index_file = self.base_path / "knowledge" / "guidelines.json"
        
        # Ensure directories exist
        self.knowledge_dir.mkdir(parents=True, exist_ok=True)
        
        # Load or create index
        self.index = self._load_index()
    
    def _load_index(self) -> Dict[str, Any]:
        """Load the guidelines index."""
        if self.index_file.exists():
            with open(self.index_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"guidelines": {}, "last_scan": None}
    
    def _save_index(self):
        """Save the guidelines index."""
        self.index_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(self.index, f, indent=2, ensure_ascii=False)
    
    def scan_and_process_all(self) -> Dict[str, Any]:
        """Scan source_pdfs and process any new/changed PDFs."""
        if not HAS_PYMUPDF:
            return {"error": "PyMuPDF not installed. Run: pip install pymupdf"}
        
        if not self.source_dir.exists():
            return {"error": f"Source directory not found: {self.source_dir}"}
        
        results = {"processed": [], "skipped": [], "failed": []}
        
        for pdf_path in self.source_dir.glob("*.pdf"):
            file_hash = self._compute_hash(pdf_path)
            
            # Check if already processed
            if file_hash in self.index["guidelines"]:
                results["skipped"].append(pdf_path.name)
                continue
            
            # Process new PDF
            try:
                guideline_data = self._extract_pdf(pdf_path)
                
                # Save chapter data
                slug = self._make_slug(pdf_path.name, guideline_data.get("year"))
                chapter_file = self.knowledge_dir / f"{slug}.json"
                
                with open(chapter_file, 'w', encoding='utf-8') as f:
                    json.dump(guideline_data, f, indent=2, ensure_ascii=False)
                
                # Update index
                self.index["guidelines"][file_hash] = {
                    "filename": pdf_path.name,
                    "slug": slug,
                    "type": guideline_data.get("type"),
                    "year": guideline_data.get("year"),
                    "title": guideline_data.get("title"),
                    "chapters_count": len(guideline_data.get("chapters", [])),
                    "processed_at": datetime.now().isoformat(),
                }
                
                results["processed"].append(pdf_path.name)
                print(f"[CardioCode] Processed: {pdf_path.name}")
                
            except Exception as e:
                results["failed"].append({"file": pdf_path.name, "error": str(e)})
                print(f"[CardioCode] Failed: {pdf_path.name} - {e}")
        
        self.index["last_scan"] = datetime.now().isoformat()
        self._save_index()
        
        return results
    
    def _compute_hash(self, filepath: Path) -> str:
        """Compute SHA-256 hash of file."""
        sha256 = hashlib.sha256()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        return sha256.hexdigest()[:16]  # Short hash is enough
    
    def _make_slug(self, filename: str, year: Optional[int]) -> str:
        """Create a URL-safe slug from filename."""
        # Remove extension and clean
        name = filename.lower().replace('.pdf', '')
        name = re.sub(r'[^a-z0-9]+', '_', name)
        name = re.sub(r'_+', '_', name).strip('_')
        
        # Add year if available
        if year:
            if str(year) not in name:
                name = f"{name}_{year}"
        
        return name[:50]  # Limit length
    
    def _extract_pdf(self, pdf_path: Path) -> Dict[str, Any]:
        """Extract all content from a PDF."""
        with fitz.open(str(pdf_path)) as doc:
            # Get metadata
            metadata = doc.metadata or {}
            total_pages = len(doc)
            
            # Try to identify guideline type and year
            first_pages_text = ""
            for i in range(min(3, total_pages)):
                first_pages_text += doc[i].get_text()
            
            guideline_type = self._identify_type(pdf_path.name, first_pages_text)
            year = self._extract_year(pdf_path.name, first_pages_text)
            title = self._extract_title(metadata, first_pages_text)
            
            # Get table of contents
            toc = doc.get_toc()
            
            # Extract chapters
            chapters = self._extract_chapters(doc, toc)
            
            return {
                "filename": pdf_path.name,
                "title": title,
                "type": guideline_type,
                "year": year,
                "total_pages": total_pages,
                "extracted_at": datetime.now().isoformat(),
                "chapters": chapters,
            }
    
    def _identify_type(self, filename: str, content: str) -> str:
        """Identify guideline type from filename/content."""
        text = (filename + " " + content[:2000]).lower()
        
        type_patterns = {
            "valvular_heart_disease": ["valvular", "vhd", "aortic stenosis", "mitral"],
            "atrial_fibrillation": ["atrial fibrillation", " af ", "afib"],
            "heart_failure": ["heart failure", " hf ", "hfref", "hfpef"],
            "ventricular_arrhythmias": ["ventricular arrhythmia", "vt ", "sudden cardiac death"],
            "pulmonary_hypertension": ["pulmonary hypertension", " ph ", " pah "],
            "pulmonary_embolism": ["pulmonary embolism", " pe "],
            "acs_nstemi": ["acute coronary", "nste-acs", "nstemi", "unstable angina"],
            "stemi": ["st-elevation", "stemi"],
            "chronic_coronary": ["chronic coronary", "ccs", "stable angina"],
            "cardio_oncology": ["cardio-oncology", "cancer therapy", "oncology"],
            "cardiac_pacing": ["pacing", "crt", "device"],
            "infective_endocarditis": ["endocarditis"],
            "peripheral_arterial": ["peripheral arter", "pad"],
            "aortic_disease": ["aortic disease", "aortic aneurysm"],
        }
        
        for gtype, patterns in type_patterns.items():
            if any(p in text for p in patterns):
                return gtype
        
        return "other"
    
    def _extract_year(self, filename: str, content: str) -> Optional[int]:
        """Extract publication year."""
        text = filename + " " + content[:500]
        match = re.search(r'20[12][0-9]', text)
        if match:
            return int(match.group())
        return None
    
    def _extract_title(self, metadata: Dict, content: str) -> str:
        """Extract guideline title."""
        if metadata.get('title'):
            return metadata['title']
        
        # Try to find title in first lines
        lines = content.split('\n')[:10]
        for line in lines:
            line = line.strip()
            if len(line) > 30 and ('guideline' in line.lower() or 'esc' in line.lower()):
                return line[:200]
        
        return "Unknown Guideline"
    
    def _extract_chapters(self, doc, toc: List) -> List[Dict[str, Any]]:
        """Extract chapters from PDF."""
        chapters = []
        
        if toc:
            # Use TOC to find chapters
            chapters = self._extract_chapters_from_toc(doc, toc)
        else:
            # Fallback: extract by page with heading detection
            chapters = self._extract_chapters_by_pages(doc)
        
        # Generate keywords for each chapter
        for chapter in chapters:
            chapter["keywords"] = self._generate_keywords(chapter.get("title", ""), chapter.get("content", ""))
        
        return chapters
    
    def _extract_chapters_from_toc(self, doc, toc: List) -> List[Dict[str, Any]]:
        """Extract chapters using table of contents."""
        chapters = []
        
        # Filter TOC to major sections (level 1 or 2)
        major_items = []
        for item in toc:
            level, title, page = item[0], item[1], item[2] if len(item) > 2 else 1
            if level <= 2 and len(title.strip()) > 5:
                major_items.append({"title": title.strip(), "page": page, "level": level})
        
        # Extract content for each section
        for i, item in enumerate(major_items):
            start_page = max(0, item["page"] - 1)  # 0-indexed
            
            # End page is start of next chapter or +15 pages max
            if i + 1 < len(major_items):
                end_page = min(major_items[i + 1]["page"], start_page + 15)
            else:
                end_page = min(len(doc), start_page + 15)
            
            # Extract text
            content = ""
            for p in range(start_page, end_page):
                if p < len(doc):
                    content += doc[p].get_text() + "\n\n"
            
            # Extract tables from these pages
            tables = self._extract_tables(doc, start_page, end_page)
            
            chapters.append({
                "number": str(i + 1),
                "title": item["title"],
                "start_page": start_page + 1,  # 1-indexed for display
                "end_page": end_page,
                "content": content.strip(),
                "tables": tables,
            })
        
        return chapters
    
    def _extract_chapters_by_pages(self, doc) -> List[Dict[str, Any]]:
        """Extract chapters by splitting PDF into page chunks."""
        chapters = []
        
        # Simple approach: chunk by ~10 pages
        chunk_size = 10
        for start in range(0, len(doc), chunk_size):
            end = min(start + chunk_size, len(doc))
            
            content = ""
            for p in range(start, end):
                content += doc[p].get_text() + "\n\n"
            
            # Try to find a heading in first 500 chars
            first_lines = content[:500].split('\n')
            title = f"Pages {start + 1}-{end}"
            for line in first_lines:
                line = line.strip()
                if len(line) > 10 and len(line) < 100:
                    title = line
                    break
            
            tables = self._extract_tables(doc, start, end)
            
            chapters.append({
                "number": str(len(chapters) + 1),
                "title": title,
                "start_page": start + 1,
                "end_page": end,
                "content": content.strip(),
                "tables": tables,
            })
        
        return chapters
    
    def _extract_tables(self, doc, start_page: int, end_page: int) -> List[Dict[str, Any]]:
        """Extract tables from page range."""
        tables = []
        
        for page_num in range(start_page, end_page):
            if page_num >= len(doc):
                break
            
            page = doc[page_num]
            
            try:
                page_tables = page.find_tables()
                for i, table in enumerate(page_tables):
                    if table.row_count > 1:  # Skip single-row "tables"
                        # Convert to text
                        rows = []
                        for row in table.extract():
                            row_text = " | ".join([str(cell) if cell else "" for cell in row])
                            rows.append(row_text)
                        
                        table_content = "\n".join(rows)
                        
                        # Try to find table title (text above table)
                        table_title = f"Table on page {page_num + 1}"
                        
                        tables.append({
                            "title": table_title,
                            "page": page_num + 1,
                            "content": table_content,
                            "rows": table.row_count,
                            "cols": table.col_count,
                        })
            except Exception:
                pass  # Some pages may not have tables
        
        return tables
    
    def _generate_keywords(self, title: str, content: str) -> List[str]:
        """Generate searchable keywords from content."""
        text = (title + " " + content[:3000]).lower()
        
        # Clinical terms to look for
        clinical_terms = [
            # Conditions
            "aortic stenosis", "mitral regurgitation", "heart failure", "atrial fibrillation",
            "pulmonary hypertension", "myocardial infarction", "cardiomyopathy",
            "tricuspid regurgitation", "aortic regurgitation", "mitral stenosis",
            # Interventions
            "tavi", "tavr", "savr", "surgery", "intervention", "anticoagulation",
            "pci", "cabg", "ablation", "pacemaker", "icd", "crt",
            # Concepts
            "diagnosis", "treatment", "recommendation", "indication", "contraindication",
            "risk", "prognosis", "monitoring", "follow-up", "imaging",
            "echocardiography", "echo", "ct", "mri", "catheterization",
            # Drug classes
            "beta blocker", "ace inhibitor", "arb", "diuretic", "antiplatelet",
            "doac", "warfarin", "statin", "sglt2",
            # Classification
            "class i", "class ii", "class iii", "severe", "moderate", "mild",
            "symptomatic", "asymptomatic",
        ]
        
        found = []
        for term in clinical_terms:
            if term in text:
                found.append(term)
        
        # Also add significant words from title
        title_words = re.findall(r'\b[a-z]{4,}\b', title.lower())
        found.extend([w for w in title_words if w not in ['with', 'from', 'this', 'that', 'these']])
        
        return list(set(found))[:20]  # Limit to 20 keywords


# Convenience function
def process_all_pdfs() -> Dict[str, Any]:
    """Process all PDFs in source_pdfs directory."""
    extractor = PDFExtractor()
    return extractor.scan_and_process_all()


def get_extractor() -> PDFExtractor:
    """Get a PDFExtractor instance."""
    return PDFExtractor()
