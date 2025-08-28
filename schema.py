"""
JSON schema definitions for ToC and section entries.
"""
from typing import Dict, Any

# Section schema (JSONL format validation)
SECTION_SCHEMA = {
    "type": "object",
    "required": [
        "doc_title",
        "section_id",
        "title",
        "page",
        "level",
        "full_path"
    ],
    "properties": {
        "doc_title": {"type": "string"},
        "section_id": {"type": "string"},
        "title": {"type": "string"},
        "full_path": {"type": "string"},
        "page": {"type": "integer"},
        "level": {"type": "integer"},
        "parent_id": {"type": ["string", "null"]},
        "text_content": {"type": ["string", "null"]},
        "tags": {
            "type": "array",
            "items": {"type": "string"}
        }
    }
}

# Metadata schema
METADATA_SCHEMA = {
    "type": "object",
    "required": [
        "doc_title",
        "num_pages"
    ],
    "properties": {
        "doc_title": {"type": "string"},
        "num_pages": {"type": "integer"},
        "author": {"type": ["string", "null"]},
        "creation_date": {"type": ["string", "null"]},
        "producer": {"type": ["string", "null"]},
        "version": {"type": ["string", "null"]}
    }
}

def validate_section_json(section_data: Dict[str, Any]) -> bool:
    """
    Validate section data against schema.
    
    Args:
        section_data: Section data to validate
        
    Returns:
        True if valid, False otherwise
    """
    # Simple validation - check required fields exist
    for field in SECTION_SCHEMA["required"]:
        if field not in section_data:
            return False
            
    # Type validation for critical fields
    if not isinstance(section_data.get("page"), int):
        return False
    if not isinstance(section_data.get("level"), int):
        return False
        
    return True

def validate_metadata_json(metadata: Dict[str, Any]) -> bool:
    """
    Validate metadata against schema.
    
    Args:
        metadata: Metadata to validate
        
    Returns:
        True if valid, False otherwise
    """
    # Simple validation - check required fields exist
    for field in METADATA_SCHEMA["required"]:
        if field not in metadata:
            return False
            
    # Type validation for critical fields
    if not isinstance(metadata.get("num_pages"), int):
        return False
        
    return True
