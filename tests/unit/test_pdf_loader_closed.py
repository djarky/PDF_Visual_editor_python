
import sys
import os
import unittest
from unittest.mock import MagicMock

# Mock gameqt
sys.modules['gameqt'] = MagicMock()
sys.modules['gameqt.core'] = MagicMock()
sys.modules['qt_compat'] = MagicMock()
sys.modules['gameqt.error_handler'] = MagicMock()

# Mock fitz
sys.modules['fitz'] = MagicMock()

# Now import PDFLoader
# We need to mock fitz.open to return a mock doc
mock_doc = MagicMock()
mock_doc.is_closed = False
mock_doc.__len__.return_value = 5
sys.modules['fitz'].open.return_value = mock_doc

# Add path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from pdf_loader import PDFLoader

class TestPDFLoaderClosed(unittest.TestCase):
    def test_closed_doc_access(self):
        loader = PDFLoader("dummy.pdf")
        
        # Verify normal access
        self.assertEqual(loader.get_page_count(), 5)
        
        # Simulate closing
        loader.doc.is_closed = True
        
        # Verify safeguarded access
        self.assertEqual(loader.get_page_count(), 0)
        
        with self.assertRaises(ValueError) as cm:
            loader.get_page_pixmap(0)
        
        self.assertIn("closed", str(cm.exception).lower())
        print("Test passed: Closed document handled correctly")

if __name__ == '__main__':
    unittest.main()
