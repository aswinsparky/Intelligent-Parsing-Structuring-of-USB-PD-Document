"""
Functions to parse the Table of Contents from extracted text.
"""
import re

def parse_toc(front_text, doc_title):
    """
    Parses the Table of Contents from the front matter text.
    Returns a list of dicts for each ToC entry.
    """
    toc_entries = []
    # Regex: section_id, whitespace, title, whitespace, page number at end
    toc_line_re = re.compile(r"^(\d+(?:\.\d+)*)(?:\s+)([^.\n]+?)(?:\s+)(\d+)$")
    for line in front_text.splitlines():
        m = toc_line_re.match(line.strip())
        if m:
            section_id = m.group(1)
            title = m.group(2).strip()
            page = int(m.group(3))
            level = section_id.count('.') + 1
            parent_id = '.'.join(section_id.split('.')[:-1]) if '.' in section_id else None
            full_path = f"{section_id} {title}"
            toc_entries.append({
                "doc_title": doc_title,
                "section_id": section_id,
                "title": title,
                "full_path": full_path,
                "page": page,
                "level": level,
                "parent_id": parent_id,
                "tags": []
            })
    return toc_entries
