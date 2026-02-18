
import unittest
import sys
import os

# Mock pygame before importing gameqt
from unittest.mock import MagicMock, Mock
sys.modules['pygame'] = MagicMock()

# Ensure pdf_visual_editor is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from gameqt.widgets import QWidget, QPushButton
from gameqt.core import Qt
from gameqt.gui import QPainter, QColor, QTextCursor

class TestWidgetFeatures(unittest.TestCase):
    """Test new widget features: setFrameShape, setWindowFlags, setCursor."""
    
    def test_frame_shape_storage(self):
        """Test that setFrameShape stores the value correctly."""
        widget = QWidget()
        
        # Default should be NoFrame
        self.assertEqual(widget.frameShape(), 0)
        
        # Set to Box
        widget.setFrameShape(Qt.FrameShape.Box)
        self.assertEqual(widget.frameShape(), Qt.FrameShape.Box)
        
        # Set to Panel
        widget.setFrameShape(Qt.FrameShape.Panel)
        self.assertEqual(widget.frameShape(), Qt.FrameShape.Panel)
        
        # Set to StyledPanel
        widget.setFrameShape(Qt.FrameShape.StyledPanel)
        self.assertEqual(widget.frameShape(), Qt.FrameShape.StyledPanel)
    
    def test_window_flags_storage(self):
        """Test that setWindowFlags stores the value correctly."""
        widget = QWidget()
        
        # Default should be 0
        self.assertEqual(widget.windowFlags(), 0)
        
        # Set to Dialog
        widget.setWindowFlags(Qt.WindowType.Dialog)
        self.assertEqual(widget.windowFlags(), Qt.WindowType.Dialog)
        
        # Set with multiple flags
        flags = Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.WindowTitleHint
        widget.setWindowFlags(flags)
        self.assertEqual(widget.windowFlags(), flags)
    
    def test_cursor_storage(self):
        """Test that setCursor stores the cursor correctly."""
        widget = QWidget()
        
        # Default should be None
        self.assertIsNone(widget._cursor)
        
        # Set to ArrowCursor
        widget.setCursor(Qt.CursorShape.ArrowCursor)
        self.assertEqual(widget._cursor, Qt.CursorShape.ArrowCursor)
        
        # Set to CrossCursor
        widget.setCursor(Qt.CursorShape.CrossCursor)
        self.assertEqual(widget._cursor, Qt.CursorShape.CrossCursor)
    
    def test_minimum_size_storage(self):
        """Test that setMinimumSize stores the value correctly."""
        widget = QWidget()
        
        # Default should be (0, 0)
        self.assertEqual(widget.minimumSize(), (0, 0))
        
        # Set minimum size
        widget.setMinimumSize(200, 100)
        self.assertEqual(widget.minimumSize(), (200, 100))
    
    def test_qpainter_stroke_rect_exists(self):
        """Test that QPainter.strokeRect method exists and is callable."""
        # Mock device
        device = MagicMock()
        painter = QPainter(device)
        
        # Method should exist
        self.assertTrue(hasattr(painter, 'strokeRect'))
        self.assertTrue(callable(painter.strokeRect))
    
    def test_qtext_cursor_select_document(self):
        """Test QTextCursor.select for Document type."""
        cursor = QTextCursor()
        cursor._anchor = 5
        cursor._pos = 10
        
        # Select entire document
        cursor.select(QTextCursor.SelectionType.Document)
        
        # Anchor should be 0
        self.assertEqual(cursor._anchor, 0)
        # Position should be > 0 (default fallback is 1000)
        self.assertGreater(cursor._pos, 0)

if __name__ == '__main__':
    unittest.main()
