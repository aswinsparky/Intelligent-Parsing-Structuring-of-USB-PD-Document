"""
Functions to parse all sections from the document text.
"""
import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from models import Section

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SectionParser:
    """Class to handle section parsing from document text."""
    
    def __init__(self, doc_title: str):
        """
        Initialize with document title.
        
        Args:
            doc_title (str): Document title
        """
        self.doc_title = doc_title
        # Primary regex for section headers
        self.section_pattern = re.compile(r"^(\d+(?:\.\d+)*)(?:\s+)([^.\n]+)")
        # Additional patterns for different section formats
        self.alt_patterns = [
            re.compile(r"^(?:Section|Chapter)\s+(\d+(?:\.\d+)*)\s+([^.\n]+)", re.IGNORECASE)
        ]
        
    def _extract_section_content(self, 
                                text_lines: List[str], 
                                start_idx: int, 
                                end_idx: Optional[int] = None) -> str:
        """
        Extract text content between section headers.
        
        Args:
            text_lines: List of text lines
            start_idx: Starting line index (inclusive)
            end_idx: Ending line index (exclusive), or None for end of document
            
        Returns:
            Extracted text content
        """
        if end_idx is None:
            end_idx = len(text_lines)
            
        content_lines = text_lines[start_idx:end_idx]
        return "\n".join(content_lines)
    
    def parse(self, page_texts: List[str]) -> List[Section]:
        """
        Parse all section headers and content from document text.
        
        Args:
            page_texts: List of text content for each page
            
        Returns:
            List of Section objects
        """
        section_entries = []
        # Flatten all text into lines with page mapping
        lines = []
        page_map = []  # (line_idx, page_num)
        
        for page_num, page_text in enumerate(page_texts, 1):
            if not page_text:
                continue
                
            for line in page_text.splitlines():
                lines.append(line.strip())
                page_map.append(page_num)
        
        # Find all section headers
        section_indices = []  # [(line_idx, section_id, title), ...]
        
        for idx, line in enumerate(lines):
            # Try main pattern
            match = self.section_pattern.match(line)
            if match:
                section_id = match.group(1)
                title = match.group(2).strip()
                section_indices.append((idx, section_id, title))
                continue
                
            # Try alternative patterns
            for pattern in self.alt_patterns:
                match = pattern.match(line)
                if match:
                    section_id = match.group(1)
                    title = match.group(2).strip()
                    section_indices.append((idx, section_id, title))
                    break
        
        # Create section entries with content
        for i, (idx, section_id, title) in enumerate(section_indices):
            try:
                page = page_map[idx]
                level = section_id.count('.') + 1
                parent_id = '.'.join(section_id.split('.')[:-1]) if '.' in section_id else None
                
                # Determine content range
                content_start = idx + 1  # Start after the header
                content_end = section_indices[i+1][0] if i < len(section_indices) - 1 else None
                
                # Extract content
                content = self._extract_section_content(lines, content_start, content_end)
                
                section = Section(
                    doc_title=self.doc_title,
                    section_id=section_id,
                    title=title,
                    page=page,
                    level=level,
                    parent_id=parent_id,
                    text_content=content
                )
                section_entries.append(section)
            except Exception as e:
                logger.error(f"Error processing section {section_id}: {str(e)}")
        
        # Sort entries by section_id numerically
        section_entries.sort(key=lambda x: [int(part) for part in x.section_id.split('.')])
        
        return section_entries

# For backward compatibility
def parse_sections(all_text: List[str], doc_title: str) -> List[Dict[str, Any]]:
    """
    Parses all section headers in the document.
    Returns a list of dicts for each section entry.
    """
    parser = SectionParser(doc_title)
    sections = parser.parse(all_text)
    return [section.to_dict() for section in sections]
