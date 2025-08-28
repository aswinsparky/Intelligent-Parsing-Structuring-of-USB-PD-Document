"""
Unit tests for USB PD document parsing modules.
"""
import unittest
import os
import json
import tempfile
from unittest.mock import patch, MagicMock

from models import Section, DocumentMetadata
from pdf_utils import PDFProcessor
from toc_parser import TOCParser
from section_parser import SectionParser
from validation import DocumentValidator


class TestModels(unittest.TestCase):
    """Test model classes."""
    
    def test_section_model(self):
        """Test Section model."""
        section = Section(
            doc_title="Test Doc",
            section_id="1.2.3",
            title="Test Section",
            page=42,
            level=3
        )
        
        self.assertEqual(section.doc_title, "Test Doc")
        self.assertEqual(section.section_id, "1.2.3")
        self.assertEqual(section.title, "Test Section")
        self.assertEqual(section.page, 42)
        self.assertEqual(section.level, 3)
        self.assertEqual(section.full_path, "1.2.3 Test Section")
        self.assertEqual(section.tags, [])
        
    def test_metadata_model(self):
        """Test DocumentMetadata model."""
        metadata = DocumentMetadata(
            doc_title="Test Doc",
            num_pages=100,
            author="Test Author"
        )
        
        self.assertEqual(metadata.doc_title, "Test Doc")
        self.assertEqual(metadata.num_pages, 100)
        self.assertEqual(metadata.author, "Test Author")
        self.assertIsNone(metadata.creation_date)


class TestTOCParser(unittest.TestCase):
    """Test TOC parsing."""
    
    def test_parse_toc(self):
        """Test TOC parsing with valid input."""
        doc_title = "Test USB PD Spec"
        toc_text = """
        1 Introduction 5
        2 Overview 10
        2.1 Features 12
        2.2 Components 15
        3 Electrical Requirements 20
        """
        
        parser = TOCParser(doc_title)
        sections = parser.parse(toc_text)
        
        self.assertEqual(len(sections), 5)
        self.assertEqual(sections[0].section_id, "1")
        self.assertEqual(sections[0].title, "Introduction")
        self.assertEqual(sections[0].page, 5)
        self.assertEqual(sections[0].level, 1)
        
        self.assertEqual(sections[2].section_id, "2.1")
        self.assertEqual(sections[2].parent_id, "2")
        self.assertEqual(sections[2].level, 2)


class TestSectionParser(unittest.TestCase):
    """Test section parsing."""
    
    def test_parse_sections(self):
        """Test section parsing with valid input."""
        doc_title = "Test USB PD Spec"
        page_texts = [
            "Page 1\n\n1 Introduction\nThis is an introduction.",
            "Page 2\n\n2 Overview\nOverview text.",
            "Page 3\n\n2.1 Features\nFeatures text."
        ]
        
        parser = SectionParser(doc_title)
        sections = parser.parse(page_texts)
        
        self.assertEqual(len(sections), 3)
        self.assertEqual(sections[0].section_id, "1")
        self.assertEqual(sections[0].title, "Introduction")
        self.assertEqual(sections[0].page, 1)
        
        self.assertEqual(sections[2].section_id, "2.1")
        self.assertEqual(sections[2].parent_id, "2")


class TestDocumentValidator(unittest.TestCase):
    """Test document validation."""
    
    def setUp(self):
        """Set up test data."""
        self.validator = DocumentValidator()
        
        # Create test sections
        self.toc_sections = [
            Section(doc_title="Test", section_id="1", title="Intro", page=1, level=1),
            Section(doc_title="Test", section_id="2", title="Overview", page=5, level=1),
            Section(doc_title="Test", section_id="2.1", title="Features", page=7, level=2, parent_id="2"),
            Section(doc_title="Test", section_id="3", title="Electrical", page=10, level=1)
        ]
        
        self.parsed_sections = [
            Section(doc_title="Test", section_id="1", title="Intro", page=1, level=1),
            Section(doc_title="Test", section_id="2", title="Overview", page=5, level=1),
            Section(doc_title="Test", section_id="2.2", title="Extra", page=8, level=2, parent_id="2"),
            Section(doc_title="Test", section_id="3", title="Electrical", page=10, level=1)
        ]
        
        # Create temporary files
        self.temp_dir = tempfile.mkdtemp()
        self.toc_file = os.path.join(self.temp_dir, "toc.jsonl")
        self.spec_file = os.path.join(self.temp_dir, "spec.jsonl")
        self.report_file = os.path.join(self.temp_dir, "report.xlsx")
        
        # Write test data to files
        with open(self.toc_file, "w", encoding="utf-8") as f:
            for section in self.toc_sections:
                f.write(json.dumps(section.to_dict()) + "\n")
                
        with open(self.spec_file, "w", encoding="utf-8") as f:
            for section in self.parsed_sections:
                f.write(json.dumps(section.to_dict()) + "\n")
    
    def tearDown(self):
        """Clean up temporary files."""
        for file in [self.toc_file, self.spec_file, self.report_file]:
            if os.path.exists(file):
                os.remove(file)
        os.rmdir(self.temp_dir)
    
    def test_validation(self):
        """Test validation logic."""
        result = self.validator.validate(self.toc_file, self.spec_file)
        
        self.assertEqual(len(result.missing_in_parsed), 1)
        self.assertEqual(result.missing_in_parsed[0].section_id, "2.1")
        
        self.assertEqual(len(result.extra_in_parsed), 1)
        self.assertEqual(result.extra_in_parsed[0].section_id, "2.2")
        
        self.assertEqual(result.toc_count, 4)
        self.assertEqual(result.parsed_count, 4)
        self.assertEqual(result.coverage_percentage, 75.0)
    
    def test_report_generation(self):
        """Test report generation."""
        self.validator.validate(self.toc_file, self.spec_file)
        self.validator.generate_report(self.report_file)
        
        self.assertTrue(os.path.exists(self.report_file))


if __name__ == "__main__":
    unittest.main()
