import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from utils.geometry import CoordinateConverter

class TestCoordinateIntegration(unittest.TestCase):
    """Integration tests for end-to-end coordinate conversion."""
    
    def test_round_trip_point_conversion(self):
        """Test converting Qt->PDF->Qt preserves coordinates."""
        page_height = 792  # Standard letter page
        qt_x, qt_y = 100, 200
        
        # Convert Qt to PDF
        pdf_x, pdf_y = CoordinateConverter.qt_to_pdf(qt_x, qt_y, page_height, scale=1.0)
        
        # Convert back to Qt
        result_x, result_y = CoordinateConverter.pdf_to_qt(pdf_x, pdf_y, page_height, scale=1.0)
        
        self.assertAlmostEqual(result_x, qt_x, places=5)
        self.assertAlmostEqual(result_y, qt_y, places=5)
    
    def test_round_trip_rect_conversion(self):
        """Test converting PDF rect->Qt rect->PDF rect preserves dimensions."""
        page_height = 792
        original_bbox = (50, 50, 150, 150)  # PDF coordinates
        
        # Convert to Qt rect
        qt_x, qt_y, w, h = CoordinateConverter.pdf_rect_to_qt_rect(original_bbox, page_height, scale=1.0)
        
        # Convert back to PDF
        result_bbox = CoordinateConverter.qt_rect_to_pdf_rect(qt_x, qt_y, w, h, page_height, scale=1.0)
        
        x0, y0, x1, y1 = result_bbox
        
        self.assertAlmostEqual(x0, original_bbox[0], places=5)
        self.assertAlmostEqual(y0, original_bbox[1], places=5)
        self.assertAlmostEqual(x1, original_bbox[2], places=5)
        self.assertAlmostEqual(y1, original_bbox[3], places=5)
    
    def test_scale_factor_consistency(self):
        """Test that scale factor is consistently applied."""
        page_height = 792
        scale = 1.5
        pdf_x, pdf_y = 100, 200
        
        # Convert with scale
        qt_x, qt_y = CoordinateConverter.pdf_to_qt(pdf_x, pdf_y, page_height, scale=scale)
        
        # Qt coordinates should be scaled
        self.assertEqual(qt_x, pdf_x * scale)
        # Y conversion: (page_height - pdf_y) * scale
        expected_qt_y = (page_height - pdf_y) * scale
        self.assertEqual(qt_y, expected_qt_y)
    
    def test_rect_dimensions_preserved(self):
        """Test that rectangle dimensions are correctly scaled."""
        page_height = 792
        scale = 2.0
        # PDF rect: 100x100 square
        bbox = (50, 50, 150, 150)
        
        qt_x, qt_y, w, h = CoordinateConverter.pdf_rect_to_qt_rect(bbox, page_height, scale=scale)
        
        # Width and height should be scaled
        expected_w = (150 - 50) * scale
        expected_h = (150 - 50) * scale
        
        self.assertEqual(w, expected_w)
        self.assertEqual(h, expected_h)
    
    def test_corner_cases_page_boundaries(self):
        """Test conversion at page boundaries."""
        page_height = 792
        
        # Top-left in Qt (0, 0) should map to top-left in PDF (0, page_height)
        pdf_x, pdf_y = CoordinateConverter.qt_to_pdf(0, 0, page_height)
        self.assertEqual(pdf_x, 0)
        self.assertEqual(pdf_y, page_height)
        
        # Bottom-left in Qt (0, page_height) should map to bottom-left in PDF (0, 0)
        pdf_x, pdf_y = CoordinateConverter.qt_to_pdf(0, page_height, page_height)
        self.assertEqual(pdf_x, 0)
        self.assertEqual(pdf_y, 0)
    
    def test_rotation_matrix_generation(self):
        """Test transformation matrix generation."""
        # No rotation, no scale
        matrix = CoordinateConverter.get_transform_matrix(1.0, 1.0, 0.0)
        self.assertEqual(matrix, (1.0, 0.0, 0.0, 1.0, 0, 0))
        
        # 90 degree rotation
        import math
        matrix = CoordinateConverter.get_transform_matrix(1.0, 1.0, 90.0)
        a, b, c, d, e, f = matrix
        
        # At 90 degrees: cos(90)=0, sin(90)=1
        self.assertAlmostEqual(a, 0.0, places=5)
        self.assertAlmostEqual(b, 1.0, places=5)
        self.assertAlmostEqual(c, -1.0, places=5)
        self.assertAlmostEqual(d, 0.0, places=5)
    
    def test_apply_rotation_to_rect(self):
        """Test rotation application to PDF rectangles."""
        bbox = (100, 100, 200, 200)
        page_width = 612
        page_height = 792
        
        rotation_info = CoordinateConverter.apply_rotation_to_pdf_rect(
            bbox, 45, page_width, page_height
        )
        
        # Check center point calculation
        self.assertEqual(rotation_info['center_x'], 150)
        self.assertEqual(rotation_info['center_y'], 150)
        self.assertEqual(rotation_info['angle'], 45)
        self.assertEqual(rotation_info['bbox'], bbox)

if __name__ == '__main__':
    unittest.main()
