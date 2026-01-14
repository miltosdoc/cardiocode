"""
PDF Watcher for New Guidelines.

Monitors the source_pdfs/ directory for new guideline documents.
When detected, triggers the knowledge extraction pipeline.
"""

from __future__ import annotations
import os
import json
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class PDFNotification:
    """Notification event for PDF changes."""
    event_type: str  # "new_pdf", "status_change", "classification_updated"
    filename: str
    message: str
    timestamp: datetime
    details: Optional[Dict[str, Any]] = None


@dataclass
class PDFMetadata:
    """Metadata for a guideline PDF."""
    filename: str
    filepath: str
    file_hash: str
    file_size: int
    detected_at: datetime
    processed: bool = False
    guideline_type: Optional[str] = None  # "heart_failure", "af", etc.
    guideline_year: Optional[int] = None
    processing_status: str = "pending"  # "pending", "processing", "completed", "failed"
    notes: Optional[str] = None
    last_notification: Optional[datetime] = None


class NotificationManager:
    """Manages PDF notifications and history."""
    
    def __init__(self, notification_path: str = "cardiocode/pdf_notifications.json"):
        self.notification_path = Path(notification_path)
        self.notifications: List[PDFNotification] = []
        self._load()
    
    def _load(self):
        """Load notifications from disk."""
        if self.notification_path.exists():
            with open(self.notification_path, 'r') as f:
                data = json.load(f)
                for notif_data in data:
                    self.notifications.append(PDFNotification(
                        event_type=notif_data["event_type"],
                        filename=notif_data["filename"],
                        message=notif_data["message"],
                        timestamp=datetime.fromisoformat(notif_data["timestamp"]),
                        details=notif_data.get("details"),
                    ))
    
    def _save(self):
        """Save notifications to disk."""
        self.notification_path.parent.mkdir(parents=True, exist_ok=True)
        data = []
        for notif in self.notifications:
            data.append({
                "event_type": notif.event_type,
                "filename": notif.filename,
                "message": notif.message,
                "timestamp": notif.timestamp.isoformat(),
                "details": notif.details,
            })
        with open(self.notification_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def add_notification(self, event_type: str, filename: str, message: str, details: Optional[Dict[str, Any]] = None):
        """Add a new notification."""
        notification = PDFNotification(
            event_type=event_type,
            filename=filename,
            message=message,
            timestamp=datetime.now(),
            details=details,
        )
        self.notifications.append(notification)
        self._save()
        
        # Also print to console for immediate feedback
        print(f"[CardioCode Notification] {message}")
    
    def get_recent_notifications(self, hours: int = 24) -> List[PDFNotification]:
        """Get notifications from the last N hours."""
        cutoff = datetime.now() - timedelta(hours=hours)
        return [n for n in self.notifications if n.timestamp >= cutoff]
    
    def get_unacknowledged(self) -> List[PDFNotification]:
        """Get notifications that haven't been acknowledged."""
        return [n for n in self.notifications if not n.details or not n.details.get("acknowledged", False)]


class GuidelineRegistry:
    """
    Registry of known and processed guidelines.
    
    Persists to JSON for tracking across sessions.
    """
    
    def __init__(self, registry_path: str = "cardiocode/guideline_registry.json"):
        self.registry_path = Path(registry_path)
        self.guidelines: Dict[str, PDFMetadata] = {}
        self.notification_manager = NotificationManager()
        self._load()
    
    def _load(self):
        """Load registry from disk."""
        if self.registry_path.exists():
            with open(self.registry_path, 'r') as f:
                data = json.load(f)
                for hash_key, meta in data.items():
                    self.guidelines[hash_key] = PDFMetadata(
                        filename=meta["filename"],
                        filepath=meta["filepath"],
                        file_hash=meta["file_hash"],
                        file_size=meta["file_size"],
                        detected_at=datetime.fromisoformat(meta["detected_at"]),
                        processed=meta.get("processed", False),
                        guideline_type=meta.get("guideline_type"),
                        guideline_year=meta.get("guideline_year"),
                        processing_status=meta.get("processing_status", "pending"),
                        notes=meta.get("notes"),
                    )
    
    def _save(self):
        """Save registry to disk."""
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        data = {}
        for hash_key, meta in self.guidelines.items():
            data[hash_key] = {
                "filename": meta.filename,
                "filepath": meta.filepath,
                "file_hash": meta.file_hash,
                "file_size": meta.file_size,
                "detected_at": meta.detected_at.isoformat(),
                "processed": meta.processed,
                "guideline_type": meta.guideline_type,
                "guideline_year": meta.guideline_year,
                "processing_status": meta.processing_status,
                "notes": meta.notes,
            }
        with open(self.registry_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def register(self, metadata: PDFMetadata) -> bool:
        """
        Register a new PDF. Returns True if new, False if already known.
        """
        if metadata.file_hash in self.guidelines:
            return False
        
        # Add to registry
        self.guidelines[metadata.file_hash] = metadata
        self._save()
        
        # Send notification
        self.notification_manager.add_notification(
            event_type="new_pdf",
            filename=metadata.filename,
            message=f"New guideline PDF detected: {metadata.filename}",
            details={
                "guideline_type": metadata.guideline_type,
                "guideline_year": metadata.guideline_year,
                "file_size": metadata.file_size,
                "acknowledged": False,
            }
        )
        
        return True
    
    def update(self, file_hash: str, **kwargs):
        """Update metadata for a registered PDF."""
        if file_hash in self.guidelines:
            meta = self.guidelines[file_hash]
            for key, value in kwargs.items():
                if hasattr(meta, key):
                    setattr(meta, key, value)
            self._save()
    
    def get_pending(self) -> List[PDFMetadata]:
        """Get PDFs that haven't been processed."""
        return [m for m in self.guidelines.values() if not m.processed]
    
    def is_known(self, file_hash: str) -> bool:
        """Check if a PDF is already registered."""
        return file_hash in self.guidelines


def compute_file_hash(filepath: str) -> str:
    """Compute SHA-256 hash of file."""
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            sha256.update(chunk)
    return sha256.hexdigest()


def identify_guideline_from_pdf(filepath: str) -> tuple[Optional[str], Optional[str], Optional[int]]:
    """
    Extract title, identify type, and year from PDF content.
    
    Returns:
        tuple of (title, guideline_type, year)
    """
    try:
        import fitz  # PyMuPDF
        with fitz.open(filepath) as doc:
            metadata = doc.metadata
            
            # Get title from metadata or first page
            title = metadata.get('title', '')
            if not title and len(doc) > 0:
                first_page = doc[0].get_text()[:200]
                # Look for title in first few lines
                lines = first_page.split('\n')[:5]
                for line in lines:
                    line = line.strip()
                    if len(line) > 20 and ('guidelines' in line.lower() or 'esc' in line.lower()):
                        title = line
                        break
            
            # Get content for type identification
            content = ""
            if len(doc) > 0:
                content = doc[0].get_text() + doc[1].get_text() if len(doc) > 1 else doc[0].get_text()
            
            # Identify type
            guideline_type = identify_guideline_type(filepath, content)
            
            # Extract year from title or content
            year = extract_year_from_filename(filepath)
            if not year and title:
                import re
                year_match = re.search(r'20[0-2][0-9]', title)
                if year_match:
                    year = int(year_match.group())
            
            return title, guideline_type, year
            
    except ImportError:
        # Fallback if PyMuPDF not available
        return None, identify_guideline_type(filepath), extract_year_from_filename(filepath)
    except Exception as e:
        print(f"Error reading PDF {filepath}: {e}")
        return None, identify_guideline_type(filepath), extract_year_from_filename(filepath)


def identify_guideline_type(filename: str, pdf_content: Optional[str] = None) -> Optional[str]:
    """
    Attempt to identify guideline type from filename or PDF content.
    
    Returns guideline key if identified, None otherwise.
    """
    filename_lower = filename.lower()
    
    # Mapping of keywords to guideline types
    keyword_map = {
        "heart failure": "heart_failure",
        "hf ": "heart_failure",
        "atrial fibrillation": "atrial_fibrillation",
        " af ": "atrial_fibrillation",
        "acute coronary": "acs_nstemi",
        "nste-acs": "acs_nstemi",
        "nstemi": "acs_nstemi",
        "valvular": "valvular_heart_disease",
        "vhd": "valvular_heart_disease",
        "pulmonary hypertension": "pulmonary_hypertension",
        "pulmonary embolism": "pulmonary_embolism",
        "ventricular arrhythmia": "ventricular_arrhythmias",
        "sudden cardiac death": "ventricular_arrhythmias",
        "scd": "ventricular_arrhythmias",
        "cardio-oncology": "cardio_oncology",
        "cardiooncology": "cardio_oncology",
        "congenital heart": "congenital_heart_disease",
        "sports cardiology": "sports_cardiology",
        "cardiac pacing": "cardiac_pacing",
        "cardiovascular disease prevention": "cardiovascular_prevention",
        "acute and chronic heart failure": "heart_failure",
    }
    
    # First try filename
    for keyword, guideline_type in keyword_map.items():
        if keyword in filename_lower:
            return guideline_type
    
    # If content is provided, try content-based identification
    if pdf_content:
        content_lower = pdf_content.lower()
        for keyword, guideline_type in keyword_map.items():
            if keyword in content_lower:
                return guideline_type
    
    return None


def extract_year_from_filename(filename: str) -> Optional[int]:
    """Extract publication year from filename."""
    import re
    # Look for 4-digit year starting with 20
    match = re.search(r'20[0-2][0-9]', filename)
    if match:
        return int(match.group())
    return None


class GuidelineWatcher:
    """
    Watches a directory for new guideline PDFs.
    
    Usage:
        watcher = GuidelineWatcher("source_pdfs/")
        new_pdfs = watcher.check()  # Returns list of new PDFs
        
        # Or continuous monitoring
        watcher.start(callback=process_pdf)
    """
    
    def __init__(self, watch_dir: str = "source_pdfs"):
        self.watch_dir = Path(watch_dir)
        self.registry = GuidelineRegistry()
    
    def get_notifications(self, hours: int = 24) -> List[PDFNotification]:
        """Get recent notifications."""
        return self.registry.notification_manager.get_recent_notifications(hours)
    
    def acknowledge_notification(self, filename: str) -> bool:
        """Mark a notification as acknowledged."""
        for notif in self.registry.notification_manager.notifications:
            if notif.filename == filename:
                if notif.details is None:
                    notif.details = {}
                notif.details["acknowledged"] = True
                self.registry.notification_manager._save()
                return True
        return False
    
    def scan(self) -> List[PDFMetadata]:
        """
        Scan directory and identify all PDFs.
        
        Returns list of all PDFs (new and known).
        """
        pdfs = []
        
        if not self.watch_dir.exists():
            return pdfs
        
        for filepath in self.watch_dir.glob("*.pdf"):
            file_hash = compute_file_hash(str(filepath))
            
            if self.registry.is_known(file_hash):
                # Already registered
                continue
            
            # Enhanced PDF detection
            title, guideline_type, guideline_year = identify_guideline_from_pdf(str(filepath))
            
            # New PDF detected
            metadata = PDFMetadata(
                filename=filepath.name,
                filepath=str(filepath),
                file_hash=file_hash,
                file_size=filepath.stat().st_size,
                detected_at=datetime.now(),
                guideline_type=guideline_type,
                guideline_year=guideline_year,
            )
            
            pdfs.append(metadata)
        
        return pdfs
    
    def check(self) -> List[PDFMetadata]:
        """
        Check for new PDFs and register them.
        
        Returns list of newly detected PDFs.
        """
        new_pdfs = self.scan()
        
        for pdf in new_pdfs:
            self.registry.register(pdf)
            print(f"[CardioCode] New guideline detected: {pdf.filename}")
            if pdf.guideline_type:
                print(f"  -> Identified as: {pdf.guideline_type}")
            else:
                print(f"  -> Type unknown - manual classification needed")
        
        return new_pdfs
    
    def get_status_report(self) -> str:
        """Get human-readable status of all guidelines."""
        lines = [
            "CardioCode Guideline Status Report",
            "=" * 50,
            f"Watch directory: {self.watch_dir}",
            f"Total registered: {len(self.registry.guidelines)}",
            "",
        ]
        
        for meta in self.registry.guidelines.values():
            status_icon = "+" if meta.processed else "o" if meta.processing_status == "processing" else "-"
            lines.append(f"[{status_icon}] {meta.filename}")
            lines.append(f"    Type: {meta.guideline_type or 'Unknown'}")
            lines.append(f"    Year: {meta.guideline_year or 'Unknown'}")
            lines.append(f"    Status: {meta.processing_status}")
            lines.append("")
        
        pending = self.registry.get_pending()
        if pending:
            lines.append("-" * 50)
            lines.append(f"ACTION NEEDED: {len(pending)} guidelines pending processing")
            for p in pending:
                lines.append(f"  - {p.filename}")
        
        return "\n".join(lines)


def check_for_new_pdfs(source_dir: str = "source_pdfs") -> List[Dict[str, Any]]:
    """
    Convenience function to check for new PDFs.
    
    Returns list of dictionaries with info about new PDFs.
    Suitable for use by LLM agents.
    """
    watcher = GuidelineWatcher(source_dir)
    new_pdfs = watcher.check()
    
    return [
        {
            "filename": pdf.filename,
            "filepath": pdf.filepath,
            "guideline_type": pdf.guideline_type,
            "guideline_year": pdf.guideline_year,
            "needs_classification": pdf.guideline_type is None,
            "action_required": "Use extract_recommendations_prompt() to begin encoding",
        }
        for pdf in new_pdfs
    ]
