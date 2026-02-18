import unittest
from unittest.mock import MagicMock, patch
import sys
from PyQt6.QtWidgets import QApplication, QGraphicsPixmapItem
from PyQt6.QtGui import QPixmap

# Mock QApplication to avoid GUI issues in headless environment
if not QApplication.instance():
    app = QApplication(sys.argv)

# Mock modules that might be missing or cause issues
sys.modules['pikepdf'] = MagicMock()
sys.modules['pdfminer'] = MagicMock()
sys.modules['pdfminer.high_level'] = MagicMock()
sys.modules['pdfminer.layout'] = MagicMock()

from gui.main_window import MainWindow

class TestBackgroundOpacity(unittest.TestCase):
    @patch('gui.main_window.PDFLoader')
    @patch('gui.main_window.LayoutAnalyzer')
    def test_background_opacity(self, MockLayoutAnalyzer, MockPDFLoader):
        # Setup mocks
        mock_loader = MockPDFLoader.return_value
        mock_loader.get_page_count.return_value = 1
        mock_loader.get_page_pixmap.return_value = QPixmap(100, 100)
        mock_loader.get_page_size.return_value = (100, 100)
        
        mock_analyzer = MockLayoutAnalyzer.return_value
        mock_analyzer.analyze_page.return_value = []

        # Initialize MainWindow
        window = MainWindow()
        
        # Load a dummy PDF
        window.load_pdf("dummy.pdf")
        
        # Check the scene
        scene = window.page_scenes[0]
        
        # Find the background item (zValue == -100)
        bg_item = None
        for item in scene.items():
            if item.zValue() == -100:
                bg_item = item
                break
        
        self.assertIsNotNone(bg_item, "Background item not found")
        self.assertIsInstance(bg_item, QGraphicsPixmapItem)
        self.assertEqual(bg_item.opacity(), 0.5, "Background opacity should be 0.5")

if __name__ == '__main__':
    unittest.main()
