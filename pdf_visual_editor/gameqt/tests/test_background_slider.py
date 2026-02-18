import unittest
from unittest.mock import MagicMock, patch
import sys
from PyQt6.QtWidgets import QApplication, QSlider, QLabel
from PyQt6.QtCore import Qt

# Mock QApplication
if not QApplication.instance():
    app = QApplication(sys.argv)

# Mock dependencies
sys.modules['pikepdf'] = MagicMock()
sys.modules['pdfminer'] = MagicMock()
sys.modules['pdfminer.high_level'] = MagicMock()
sys.modules['pdfminer.layout'] = MagicMock()

from gui.inspector_panel import InspectorPanel
from gui.main_window import MainWindow

class TestBackgroundSlider(unittest.TestCase):
    def test_slider_emit_signal(self):
        panel = InspectorPanel()
        
        # Mock signal connection
        mock_slot = MagicMock()
        panel.backgroundOpacityChanged.connect(mock_slot)
        
        # Change slider value
        panel.bg_slider.setValue(75)
        
        # Check signal emitted with correct value (0.75)
        mock_slot.assert_called_with(0.75)
        self.assertEqual(panel.bg_label.text(), "75%")

    @patch('gui.main_window.PDFLoader')
    @patch('gui.main_window.LayoutAnalyzer')
    def test_mainwindow_integration(self, MockLayoutAnalyzer, MockPDFLoader):
        # Setup mocks
        mock_loader = MockPDFLoader.return_value
        mock_loader.get_page_count.return_value = 1
        from PyQt6.QtGui import QPixmap
        mock_loader.get_page_pixmap.return_value = QPixmap(100, 100)
        mock_loader.get_page_size.return_value = (100, 100)
        
        mock_analyzer = MockLayoutAnalyzer.return_value
        mock_analyzer.analyze_page.return_value = []

        window = MainWindow()
        window.load_pdf("dummy.pdf")
        
        # Check initial slider value
        self.assertEqual(window.inspector_panel.bg_slider.value(), 50)
        
        # Simulate slider change
        window.inspector_panel.bg_slider.setValue(25)
        
        # Check if background item opacity updated
        bg_item = window.canvas.current_page_item
        self.assertEqual(bg_item.opacity(), 0.25)

if __name__ == '__main__':
    unittest.main()
