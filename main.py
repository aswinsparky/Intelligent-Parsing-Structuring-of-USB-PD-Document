"""
Main entry point for USB PD Specification Parsing and Structuring System.
"""
from toc_parser import parse_toc
from section_parser import parse_sections
from validation import validate_and_report
import pdfplumber
import json

# Use raw string to avoid escape sequence issues
PDF_PATH = r"C:\grl\usb_pd_parser\usb_pd_spec.pdf"
DOC_TITLE = "USB Power Delivery Specification Rev X"

def main():
    with pdfplumber.open(PDF_PATH) as pdf:
        # Extract front matter for ToC (first 10 pages)
        front_text = "\n".join(page.extract_text() or '' for page in pdf.pages[:10])
        # DEBUG: Write extracted front_text to a file for inspection
        with open("usb_pd_toc_front_text.txt", "w", encoding="utf-8") as debugf:
            debugf.write(front_text)
        toc_entries = parse_toc(front_text, DOC_TITLE)
        with open("usb_pd_toc.jsonl", "w", encoding="utf-8") as f:
            for entry in toc_entries:
                f.write(json.dumps(entry) + "\n")

        # Parse all sections in the document
        all_text = [page.extract_text() for page in pdf.pages]
        section_entries = parse_sections(all_text, DOC_TITLE)
        with open("usb_pd_spec.jsonl", "w", encoding="utf-8") as f:
            for entry in section_entries:
                f.write(json.dumps(entry) + "\n")

        # Optionally, extract metadata
        metadata = {"doc_title": DOC_TITLE, "num_pages": len(pdf.pages)}
        with open("usb_pd_metadata.jsonl", "w", encoding="utf-8") as f:
            f.write(json.dumps(metadata) + "\n")

    # Validation report
    validate_and_report("usb_pd_toc.jsonl", "usb_pd_spec.jsonl", "validation_report.xlsx")

if __name__ == "__main__":
    main()
