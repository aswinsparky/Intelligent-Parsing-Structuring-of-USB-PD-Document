"""
Functions to parse the Table of Contents from extracted text.
"""
import re
import logging
from typing import List, Dict, Any, Optional
from models import Section

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TOCParser:
    """Class to handle Table of Contents parsing."""
    
    def __init__(self, doc_title: str):
        """
        Initialize with document title.
        
        Args:
            doc_title (str): Document title
        """
        self.doc_title = doc_title
        # Regex patterns for matching TOC entries
        # Pattern 1: section_id, whitespace, title, whitespace, page number at end
        self.toc_patterns = [
            re.compile(r"^(\d+(?:\.\d+)*)(?:\s+)([^.\n]+?)(?:\s+)(\d+)$"),
            # Additional patterns for different TOC formats can be added here
            re.compile(r"^(\d+(?:\.\d+)*)\s+([^0-9\n]+?)\s*\.{2,}\s*(\d+)$")
        ]
    
    def parse(self, text: str) -> List[Section]:
        """
        Parse Table of Contents from text.
        
        Args:
            text (str): Text content to parse
            
        Returns:
            List[Section]: List of parsed TOC sections
        """
        toc_entries = []
        lines = text.splitlines()
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Try all patterns
            for pattern in self.toc_patterns:
                match = pattern.match(line)
                if match:
                    try:
                        section_id = match.group(1)
                        title = match.group(2).strip()
                        page = int(match.group(3))
                        
                        # Calculate level and parent_id
                        level = section_id.count('.') + 1
                        parent_id = '.'.join(section_id.split('.')[:-1]) if '.' in section_id else None
                        
                        # Create section object
                        section = Section(
                            doc_title=self.doc_title,
                            section_id=section_id,
                            title=title,
                            page=page,
                            level=level,
                            parent_id=parent_id
                        )
                        toc_entries.append(section)
                        break  # Found a match, move to next line
                    except Exception as e:
                        logger.warning(f"Error parsing TOC line '{line}': {str(e)}")
        
        # Sort entries by section_id numerically
        toc_entries.sort(key=lambda x: [int(part) for part in x.section_id.split('.')])
        
        return toc_entries

# For backward compatibility
def parse_toc(front_text: str, doc_title: str) -> List[Dict[str, Any]]:
    """
    Parses the Table of Contents from the front matter text.
    Returns a list of dicts for each ToC entry.
    """
    parser = TOCParser(doc_title)
    sections = parser.parse(front_text)
    return [section.to_dict() for section in sections]
