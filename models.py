"""
Object-oriented models for USB PD document parsing and structuring.
"""
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any


@dataclass
class Section:
    """Represents a section in the USB PD document."""
    doc_title: str
    section_id: str
    title: str
    page: int
    level: int
    parent_id: Optional[str] = None
    full_path: Optional[str] = None
    text_content: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if self.full_path is None:
            self.full_path = f"{self.section_id} {self.title}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class DocumentMetadata:
    """Represents metadata about the USB PD document."""
    doc_title: str
    num_pages: int
    author: Optional[str] = None
    creation_date: Optional[str] = None
    producer: Optional[str] = None
    version: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class ValidationResult:
    """Represents the result of validation between ToC and parsed sections."""
    missing_in_parsed: List[Section] = field(default_factory=list)
    extra_in_parsed: List[Section] = field(default_factory=list)
    order_mismatches: List[Dict[str, Any]] = field(default_factory=list)
    toc_count: int = 0
    parsed_count: int = 0
    coverage_percentage: float = 0.0
