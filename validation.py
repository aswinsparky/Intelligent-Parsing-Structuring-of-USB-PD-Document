"""
Validation and reporting functions for comparing ToC and parsed sections.
"""
# Placeholder for validation logic

import json
import openpyxl

def validate_and_report(toc_jsonl, spec_jsonl, report_xlsx):
    """
    Compares ToC and parsed sections, outputs XLS report.
    """
    with open(toc_jsonl, encoding="utf-8") as f:
        toc = [json.loads(line) for line in f if line.strip()]
    with open(spec_jsonl, encoding="utf-8") as f:
        spec = [json.loads(line) for line in f if line.strip()]

    toc_ids = [entry["section_id"] for entry in toc]
    spec_ids = [entry["section_id"] for entry in spec]

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Validation"
    ws.append(["Type", "Section ID", "Title", "Page", "Comment"])

    # Sections in ToC but not in parsed
    for entry in toc:
        if entry["section_id"] not in spec_ids:
            ws.append(["Missing in Parsed", entry["section_id"], entry["title"], entry["page"], "In ToC, not in parsed"])
    # Sections in parsed but not in ToC
    for entry in spec:
        if entry["section_id"] not in toc_ids:
            ws.append(["Extra in Parsed", entry["section_id"], entry["title"], entry["page"], "In parsed, not in ToC"])
    # Order errors
    min_len = min(len(toc_ids), len(spec_ids))
    for i in range(min_len):
        if toc_ids[i] != spec_ids[i]:
            ws.append(["Order Mismatch", toc_ids[i], '', '', f"Expected {toc_ids[i]}, got {spec_ids[i]}"])
    # Summary
    ws.append([])
    ws.append(["Total in ToC", len(toc_ids)])
    ws.append(["Total in Parsed", len(spec_ids)])

    wb.save(report_xlsx)
