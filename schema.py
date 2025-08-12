"""
JSON schema definitions for ToC and section entries.
"""
# Example schema as Python dicts (for reference/documentation)

toc_section_schema = {
    "doc_title": "string",
    "section_id": "string",
    "title": "string",
    "full_path": "string",
    "page": "integer",
    "level": "integer",
    "parent_id": "string or null",
    "tags": "list"
}
