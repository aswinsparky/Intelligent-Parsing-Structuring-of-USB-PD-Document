# USB PD Specification Parsing and Structuring System

## Overview
This project parses a USB Power Delivery (USB PD) specification PDF and outputs structured JSONL files for the Table of Contents and all sections, plus a validation XLS report.

## How it works
- Extracts ToC from the first 10 pages using regex.
- Parses all section headers in the document.
- Outputs structured JSONL files for ToC and sections.
- Compares ToC and parsed sections, outputs XLS validation report.

## Usage
1. Place your PDF as `usb_pd_spec.pdf` in the project directory.
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the main script:
   ```
   python main.py
   ```

## Output Files
- `usb_pd_toc.jsonl`: Table of Contents entries
- `usb_pd_spec.jsonl`: All parsed section entries
- `usb_pd_metadata.jsonl`: Document metadata
- `validation_report.xlsx`: Validation report

## Customization
- Edit `toc_parser.py` and `section_parser.py` to adjust parsing logic for your document.
