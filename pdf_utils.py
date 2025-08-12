"""
PDF utility functions for text extraction and metadata.
"""
import pdfplumber

def extract_text_from_pages(pdf_path, page_range=None):
	"""
	Extracts text from specified pages of a PDF.
	Args:
		pdf_path (str): Path to the PDF file.
		page_range (tuple or list, optional): (start, end) page numbers (1-based, inclusive start, exclusive end).
			If None, extracts all pages.
	Returns:
		List of strings, one per page.
	"""
	with pdfplumber.open(pdf_path) as pdf:
		if page_range:
			start, end = page_range
			pages = pdf.pages[start-1:end-1]
		else:
			pages = pdf.pages
		return [page.extract_text() for page in pages]

def extract_metadata(pdf_path):
	"""
	Extracts basic metadata from a PDF file.
	Args:
		pdf_path (str): Path to the PDF file.
	Returns:
		dict: Metadata dictionary.
	"""
	with pdfplumber.open(pdf_path) as pdf:
		meta = pdf.metadata or {}
		meta['num_pages'] = len(pdf.pages)
		return meta
