import fitz  # PyMuPDF
from qt_compat import QImage, QPixmap, QT_API

class PDFLoader:
    """
    Handles loading of PDF files and rendering pages to images using PyMuPDF.
    """
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.doc = fitz.open(file_path)

    def get_page_count(self) -> int:
        return len(self.doc)

    def get_page_pixmap(self, page_num: int, scale: float = 1.0) -> QPixmap:
        """
        Renders a page to a QPixmap.
        """
        if page_num < 0 or page_num >= len(self.doc):
            raise ValueError(f"Page number {page_num} out of range.")

        page = self.doc.load_page(page_num)
        matrix = fitz.Matrix(scale, scale)
        pix = page.get_pixmap(matrix=matrix)
        
        # Convert to QImage with explicit data copy for PySide2 compatibility
        # Create Python bytes object to ensure proper memory ownership
        img_data = bytes(pix.samples)
        
        # Use correct enum syntax based on Qt framework
        if QT_API == "PyQt6":
            img_format = QImage.Format.Format_RGB888
        else:  # PySide2
            img_format = QImage.Format_RGB888
        
        bytes_per_line = pix.width * 3  # RGB888 = 3 bytes per pixel
        qimage = QImage(img_data, pix.width, pix.height, bytes_per_line, img_format)
        
        # Convert to QPixmap
        return QPixmap.fromImage(qimage)

    def get_page_size(self, page_num: int):
        """Returns (width, height) of the page."""
        page = self.doc.load_page(page_num)
        rect = page.rect
        return rect.width, rect.height

    def get_image_from_rect(self, page_num: int, bbox: tuple, scale: float = 2.0) -> QPixmap:
        """
        Extracts an image from the specified bounding box on the page.
        bbox is (x0, y0, x1, y1) in PDF coordinates (bottom-left origin).
        """
        page = self.doc.load_page(page_num)
        # PyMuPDF uses top-left origin for rects usually, but let's check.
        # Actually fitz.Rect is (x0, y0, x1, y1).
        # If the bbox comes from pdfminer, it's bottom-left origin.
        # We need to convert it to PyMuPDF's expected coordinate system if they differ.
        # However, fitz usually handles PDF coordinates correctly if we use the page rect.
        
        # Wait, pdfminer bbox is (x0, bottom, x1, top).
        # fitz.Page.rect is (0, 0, width, height) where 0,0 is top-left.
        # We need to convert pdfminer bbox to fitz rect.
        
        page_height = page.rect.height
        x0, y0, x1, y1 = bbox
        
        # Convert to top-left origin for fitz clip
        # pdfminer y0 is distance from bottom.
        # fitz y0 is distance from top.
        # new_y0 = height - y1
        # new_y1 = height - y0
        
        # Ensure coordinates are valid floats
        x0, y0, x1, y1 = map(float, [x0, y0, x1, y1])
        
        # Create rect and normalize it (handles x0 > x1 etc)
        rect = fitz.Rect(x0, page_height - y1, x1, page_height - y0)
        rect.normalize()
        
        # Intersect with page rect to avoid errors if bbox is out of bounds
        rect = rect & page.rect
        
        if rect.is_empty:
             # Fallback or return empty pixmap
             raise ValueError("Empty rect for image extraction")
        
        # Get pixmap of this area
        mat = fitz.Matrix(scale, scale)
        pix = page.get_pixmap(matrix=mat, clip=rect)
        
        # Convert to QPixmap with explicit data copy for PySide2 compatibility
        # Create Python bytes object to ensure proper memory ownership
        img_data = bytes(pix.samples)
        
        # Use correct enum syntax based on Qt framework
        if QT_API == "PyQt6":
            img_format = QImage.Format.Format_RGBA8888 if pix.alpha else QImage.Format.Format_RGB888
        else:  # PySide2
            img_format = QImage.Format_RGBA8888 if pix.alpha else QImage.Format_RGB888
        
        bytes_per_line = pix.width * (4 if pix.alpha else 3)  # RGBA = 4, RGB = 3 bytes per pixel
        qimage = QImage(img_data, pix.width, pix.height, bytes_per_line, img_format)
        
        return QPixmap.fromImage(qimage)

    def close(self):
        if self.doc:
            self.doc.close()
