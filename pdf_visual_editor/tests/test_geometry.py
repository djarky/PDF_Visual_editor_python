import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.geometry import CoordinateConverter

class TestGeometry(unittest.TestCase):
    def test_pdf_to_qt(self):
        # PDF: (0, 0) is bottom-left.
        # Page height: 100.
        # Qt: (0, 100) should be bottom-left.
        x, y = CoordinateConverter.pdf_to_qt(0, 0, 100, scale=1.0)
        self.assertEqual((x, y), (0, 100))
        
        # PDF: (0, 100) is top-left.
        # Qt: (0, 0) should be top-left.
        x, y = CoordinateConverter.pdf_to_qt(0, 100, 100, scale=1.0)
        self.assertEqual((x, y), (0, 0))

    def test_qt_to_pdf(self):
        # Qt: (0, 0) is top-left.
        # Page height: 100.
        # PDF: (0, 100).
        x, y = CoordinateConverter.qt_to_pdf(0, 0, 100, scale=1.0)
        self.assertEqual((x, y), (0, 100))

    def test_pdf_rect_to_qt_rect(self):
        # PDF Rect: (10, 10, 20, 20) -> x0, y0, x1, y1
        # Width: 10, Height: 10
        # y0=10 (bottom), y1=20 (top)
        # Page height: 100
        
        # Qt y = (100 - 20) = 80 (top of rect)
        # Qt x = 10
        
        bbox = (10, 10, 20, 20)
        x, y, w, h = CoordinateConverter.pdf_rect_to_qt_rect(bbox, 100, scale=1.0)
        
        self.assertEqual(x, 10)
        self.assertEqual(y, 80)
        self.assertEqual(w, 10)
        self.assertEqual(h, 10)

if __name__ == '__main__':
    unittest.main()
