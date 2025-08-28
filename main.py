"""
Main entry point for USB PD Specification Parsing and Structuring System.
"""
import os
import json
import logging
import argparse
from typing import Dict, List, Any, Optional

from toc_parser import TOCParser
from section_parser import SectionParser
from validation import DocumentValidator
from pdf_utils import PDFProcessor
from models import Section, DocumentMetadata

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

DEFAULT_PDF_PATH = "usb_pd_spec.pdf"
DEFAULT_OUTPUT_DIR = "."

class USBPDParser:
    """Main class for USB PD document parsing."""
    
    def __init__(self, pdf_path: str, output_dir: str = DEFAULT_OUTPUT_DIR):
        """
        Initialize with PDF path and output directory.
        
        Args:
            pdf_path: Path to the PDF file
            output_dir: Directory for output files
        """
        self.pdf_path = pdf_path
        self.output_dir = output_dir
        self.doc_title = None
        self.metadata = None
        
    def _ensure_output_dir(self) -> None:
        """Ensure output directory exists."""
        os.makedirs(self.output_dir, exist_ok=True)
        
    def _output_path(self, filename: str) -> str:
        """Get full path for output file."""
        return os.path.join(self.output_dir, filename)
        
    def _write_jsonl(self, data: List[Dict[str, Any]], filename: str) -> None:
        """
        Write data to JSONL file.
        
        Args:
            data: List of dictionaries to write
            filename: Output filename
        """
        output_path = self._output_path(filename)
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                for item in data:
                    f.write(json.dumps(item) + "\n")
            logger.info(f"Wrote {len(data)} entries to {output_path}")
        except Exception as e:
            logger.error(f"Error writing to {output_path}: {str(e)}")
    
    def extract_metadata(self) -> DocumentMetadata:
        """
        Extract metadata from PDF.
        
        Returns:
            DocumentMetadata object
        """
        try:
            with PDFProcessor(self.pdf_path) as processor:
                self.metadata = processor.extract_metadata()
                # Set document title for use in other methods
                self.doc_title = self.metadata.doc_title
                logger.info(f"Extracted metadata: {self.doc_title}, {self.metadata.num_pages} pages")
                return self.metadata
        except Exception as e:
            logger.error(f"Error extracting metadata: {str(e)}")
            # Create default metadata
            self.metadata = DocumentMetadata(
                doc_title="USB Power Delivery Specification",
                num_pages=0
            )
            self.doc_title = self.metadata.doc_title
            return self.metadata
    
    def parse_toc(self) -> List[Section]:
        """
        Parse Table of Contents.
        
        Returns:
            List of Section objects
        """
        try:
            # Extract front matter (first 15 pages)
            with PDFProcessor(self.pdf_path) as processor:
                front_text = "\n".join(processor.extract_text_from_pages((1, 16)))
                
            # Debug: save front text for inspection
            with open(self._output_path("usb_pd_toc_front_text.txt"), "w", encoding="utf-8") as f:
                f.write(front_text)
                
            # Parse ToC
            parser = TOCParser(self.doc_title)
            toc_entries = parser.parse(front_text)
            logger.info(f"Parsed {len(toc_entries)} ToC entries")
            
            return toc_entries
        except Exception as e:
            logger.error(f"Error parsing ToC: {str(e)}")
            return []
    
    def parse_sections(self) -> List[Section]:
        """
        Parse all sections from document.
        
        Returns:
            List of Section objects
        """
        try:
            # Extract all text
            with PDFProcessor(self.pdf_path) as processor:
                all_text = processor.extract_text_from_pages()
                
            # Parse sections
            parser = SectionParser(self.doc_title)
            section_entries = parser.parse(all_text)
            logger.info(f"Parsed {len(section_entries)} section entries")
            
            return section_entries
        except Exception as e:
            logger.error(f"Error parsing sections: {str(e)}")
            return []
    
    def validate(self, toc_file: str, spec_file: str, report_file: str) -> None:
        """
        Validate ToC against parsed sections.
        
        Args:
            toc_file: Path to ToC JSONL file
            spec_file: Path to parsed sections JSONL file
            report_file: Path to output report file
        """
        try:
            validator = DocumentValidator()
            result = validator.validate(toc_file, spec_file)
            validator.generate_report(report_file)
            
            logger.info(f"Validation complete: {result.coverage_percentage:.2f}% coverage")
            logger.info(f"Missing sections: {len(result.missing_in_parsed)}")
            logger.info(f"Extra sections: {len(result.extra_in_parsed)}")
            logger.info(f"Order mismatches: {len(result.order_mismatches)}")
        except Exception as e:
            logger.error(f"Error validating: {str(e)}")
    
    def run(self) -> None:
        """Run the complete parsing process."""
        self._ensure_output_dir()
        
        # Step 1: Extract metadata
        self.extract_metadata()
        metadata_dict = self.metadata.to_dict()
        self._write_jsonl([metadata_dict], "usb_pd_metadata.jsonl")
        
        # Step 2: Parse ToC
        toc_entries = self.parse_toc()
        toc_dicts = [entry.to_dict() for entry in toc_entries]
        self._write_jsonl(toc_dicts, "usb_pd_toc.jsonl")
        
        # Step 3: Parse sections
        section_entries = self.parse_sections()
        section_dicts = [entry.to_dict() for entry in section_entries]
        self._write_jsonl(section_dicts, "usb_pd_spec.jsonl")
        
        # Step 4: Validate
        self.validate(
            self._output_path("usb_pd_toc.jsonl"),
            self._output_path("usb_pd_spec.jsonl"),
            self._output_path("validation_report.xlsx")
        )
        
        logger.info("USB PD document parsing complete!")

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Parse USB PD specification PDF")
    parser.add_argument("--pdf", "-p", default=DEFAULT_PDF_PATH,
                       help=f"Path to USB PD PDF file (default: {DEFAULT_PDF_PATH})")
    parser.add_argument("--output", "-o", default=DEFAULT_OUTPUT_DIR,
                       help=f"Output directory (default: {DEFAULT_OUTPUT_DIR})")
    return parser.parse_args()

def main():
    """Main entry point."""
    args = parse_args()
    
    logger.info(f"Starting USB PD parsing: {args.pdf}")
    parser = USBPDParser(args.pdf, args.output)
    parser.run()

if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()
