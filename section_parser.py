import re

"""
Functions to parse all sections from the document text.
"""
# Placeholder for section parsing logic

def parse_sections(all_text, doc_title):
    """
    Parses all section headers in the document.
    Returns a list of dicts for each section entry.
    """
    section_entries = []
    # Flatten all text into lines
    lines = []
    page_map = []  # (line_idx, page_num)
    for page_num, page_text in enumerate(all_text, 1):
        if not page_text:
            continue
        for line in page_text.splitlines():
            lines.append(line)
            page_map.append(page_num)
    # Regex: section_id, whitespace, title
    section_re = re.compile(r"^(\d+(?:\.\d+)*)(?:\s+)([^.\n]+)")
    for idx, line in enumerate(lines):
        m = section_re.match(line.strip())
        if m:
            section_id = m.group(1)
            title = m.group(2).strip()
            page = page_map[idx]
            level = section_id.count('.') + 1
            parent_id = '.'.join(section_id.split('.')[:-1]) if '.' in section_id else None
            full_path = f"{section_id} {title}"
            section_entries.append({
                "doc_title": doc_title,
                "section_id": section_id,
                "title": title,
                "full_path": full_path,
                "page": page,
                "level": level,
                "parent_id": parent_id,
                "tags": []
            })
    return section_entries
