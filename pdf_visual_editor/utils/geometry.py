class CoordinateConverter:
    """
    Helper class to convert between PDF coordinates (bottom-left origin)
    and Qt coordinates (top-left origin).
    """
    
    @staticmethod
    def pdf_to_qt(x, y, page_height, scale=1.0):
        """
        Converts a point from PDF coordinates to Qt coordinates.
        
        Args:
            x (float): X coordinate in PDF space.
            y (float): Y coordinate in PDF space.
            page_height (float): Height of the PDF page.
            scale (float): Scale factor applied to the Qt view.
            
        Returns:
            tuple: (x, y) in Qt space.
        """
        qt_x = x * scale
        qt_y = (page_height - y) * scale
        return qt_x, qt_y

    @staticmethod
    def qt_to_pdf(x, y, page_height, scale=1.0):
        """
        Converts a point from Qt coordinates to PDF coordinates.
        
        Args:
            x (float): X coordinate in Qt space.
            y (float): Y coordinate in Qt space.
            page_height (float): Height of the PDF page.
            scale (float): Scale factor applied to the Qt view.
            
        Returns:
            tuple: (x, y) in PDF space.
        """
        pdf_x = x / scale
        pdf_y = page_height - (y / scale)
        return pdf_x, pdf_y

    @staticmethod
    def pdf_rect_to_qt_rect(bbox, page_height, scale=1.0):
        """
        Converts a PDF bounding box (x0, y0, x1, y1) to a Qt rect (x, y, w, h).
        
        Args:
            bbox (tuple): (x0, y0, x1, y1) in PDF space.
            page_height (float): Height of the PDF page.
            scale (float): Scale factor.
            
        Returns:
            tuple: (x, y, w, h) in Qt space.
        """
        x0, y0, x1, y1 = bbox
        
        # PDF: y0 is bottom, y1 is top.
        # Qt: y is distance from top.
        
        # Top-Left in PDF (x0, y1) -> Qt (x, y)
        # But wait, in PDF y1 is > y0.
        # So the top of the rect in PDF is y1.
        # Distance from top of page to y1 is (page_height - y1).
        
        qt_x = x0 * scale
        qt_y = (page_height - y1) * scale
        
        w = (x1 - x0) * scale
        h = (y1 - y0) * scale
        
        return qt_x, qt_y, w, h

    @staticmethod
    def qt_rect_to_pdf_rect(x, y, w, h, page_height, scale=1.0):
        """
        Converts a Qt rect (x, y, w, h) to a PDF bounding box (x0, y0, x1, y1).
        
        Args:
            x, y, w, h (float): Rect in Qt space.
            page_height (float): Height of the PDF page.
            scale (float): Scale factor.
            
        Returns:
            tuple: (x0, y0, x1, y1) in PDF space.
        """
        # Qt y is top-left.
        # PDF y1 (top) = page_height - (qt_y / scale)
        # PDF y0 (bottom) = y1 - (h / scale)
        
        x0 = x / scale
        y1 = page_height - (y / scale)
        y0 = y1 - (h / scale)
        x1 = x0 + (w / scale)
        
        return x0, y0, x1, y1

    @staticmethod
    def apply_rotation_to_pdf_rect(bbox, angle, page_width, page_height):
        """
        Applies rotation transformation to a PDF rectangle.
        
        Args:
            bbox (tuple): (x0, y0, x1, y1) in PDF space.
            angle (float): Rotation angle in degrees (counter-clockwise).
            page_width (float): Width of the PDF page.
            page_height (float): Height of the PDF page.
            
        Returns:
            tuple: Rotated rectangle information for PDF operations.
        """
        import math
        
        x0, y0, x1, y1 = bbox
        center_x = (x0 + x1) / 2
        center_y = (y0 + y1) / 2
        
        # Convert angle to radians
        rad = math.radians(angle)
        
        # Return center and angle for PDF transformations
        return {
            'center_x': center_x,
            'center_y': center_y,
            'angle': angle,
            'bbox': bbox
        }

    @staticmethod
    def get_transform_matrix(scale_x=1.0, scale_y=1.0, rotation=0.0):
        """
        Creates a transformation matrix for PDF operations.
        
        Args:
            scale_x (float): Scale factor in X direction.
            scale_y (float): Scale factor in Y direction.
            rotation (float): Rotation angle in degrees.
            
        Returns:
            tuple: (a, b, c, d, e, f) transformation matrix.
        """
        import math
        
        rad = math.radians(rotation)
        cos_r = math.cos(rad)
        sin_r = math.sin(rad)
        
        # Create combined scale and rotation matrix
        a = scale_x * cos_r
        b = scale_x * sin_r
        c = -scale_y * sin_r
        d = scale_y * cos_r
        e = 0
        f = 0
        
        return (a, b, c, d, e, f)
