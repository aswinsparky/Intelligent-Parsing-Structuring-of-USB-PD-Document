"""
PDF utility functions for text extraction and metadata.
"""
import pdfplumber
from models import DocumentMetadata
import logging
from typing import List, Dict, Any, Optional, Tuple, Union

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PDFProcessor:
    """Class to handle PDF processing operations."""
    
    def __init__(self, pdf_path: str):
        """
        Initialize with the path to the PDF file.
        
        Args:
            pdf_path (str): Path to the PDF file
        """
        self.pdf_path = pdf_path
        self._pdf = None
        
    def __enter__(self):
        """Context manager entry."""
        try:
            self._pdf = pdfplumber.open(self.pdf_path)
            return self
        except Exception as e:
            logger.error(f"Error opening PDF {self.pdf_path}: {str(e)}")
            raise
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self._pdf:
            self._pdf.close()
    
    def extract_text_from_pages(self, page_range: Optional[Tuple[int, int]] = None) -> List[str]:
        """
        Extracts text from specified pages of a PDF.
        
        Args:
            page_range (tuple, optional): (start, end) page numbers (1-based, inclusive start, exclusive end).
                If None, extracts all pages.
                
        Returns:
            List of strings, one per page.
        """
        if not self._pdf:
            raise ValueError("PDF not opened. Use with context manager.")
            
        try:
            if page_range:
                start, end = page_range
                # Adjust for 0-based indexing
                pages = self._pdf.pages[start-1:end-1]
            else:
                pages = self._pdf.pages
                
            return [page.extract_text() or "" for page in pages]
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            return []
    
    def extract_metadata(self) -> DocumentMetadata:
        """
        Extracts metadata from the PDF file.
        
        Returns:
            DocumentMetadata: Structured metadata object
        """
        if not self._pdf:
            raise ValueError("PDF not opened. Use with context manager.")
            
        try:
            meta = self._pdf.metadata or {}
            
            # Determine document title from metadata or filename
            doc_title = meta.get('Title', None)
            if not doc_title:
                # Extract filename without extension
                doc_title = self.pdf_path.split('/')[-1].split('\\')[-1].rsplit('.', 1)[0]
                doc_title = f"{doc_title} Specification"
            
            return DocumentMetadata(
                doc_title=doc_title,
                num_pages=len(self._pdf.pages),
                author=meta.get('Author', None),
                creation_date=meta.get('CreationDate', None),
                producer=meta.get('Producer', None),
                version=meta.get('Version', None)
            )
        except Exception as e:
            logger.error(f"Error extracting metadata: {str(e)}")
            # Return minimal metadata
            return DocumentMetadata(
                doc_title="USB Power Delivery Specification",
                num_pages=0
            )
    
    def extract_tables(self, page_numbers: List[int]) -> Dict[int, List[List[str]]]:
        """
        Extract tables from specified pages.
        
        Args:
            page_numbers: List of page numbers (1-based) to extract tables from
            
        Returns:
            Dictionary mapping page numbers to lists of tables
        """
        if not self._pdf:
            raise ValueError("PDF not opened. Use with context manager.")
            
        tables_by_page = {}
        for page_num in page_numbers:
            try:
                # Adjust for 0-based indexing
                page = self._pdf.pages[page_num - 1]
                tables = page.extract_tables()
                if tables:
                    tables_by_page[page_num] = tables
            except Exception as e:
                logger.error(f"Error extracting tables from page {page_num}: {str(e)}")
                
        return tables_by_page
        
# Module-level functions for backward compatibility
def extract_text_from_pages(pdf_path: str, page_range: Optional[Tuple[int, int]] = None) -> List[str]:
    """
    Extracts text from specified pages of a PDF.
    
    Args:
        pdf_path (str): Path to the PDF file.
        page_range (tuple, optional): (start, end) page numbers (1-based, inclusive start, exclusive end).
            If None, extracts all pages.
            
    Returns:
        List of strings, one per page.
    """
    with PDFProcessor(pdf_path) as processor:
        return processor.extract_text_from_pages(page_range)

def extract_metadata(pdf_path: str) -> Dict[str, Any]:
    """
    Extracts basic metadata from a PDF file.
    
    Args:
        pdf_path (str): Path to the PDF file.
        
    Returns:
        dict: Metadata dictionary.
    """
    with PDFProcessor(pdf_path) as processor:
        metadata = processor.extract_metadata()
        return metadata.to_dict()
