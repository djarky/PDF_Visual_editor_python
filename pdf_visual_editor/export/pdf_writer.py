import fitz
from typing import List, Dict, Any
from utils.geometry import CoordinateConverter

class PDFWriter:
    """
    Handles saving the modified PDF using PyMuPDF (fitz).
    """
    def __init__(self, source_path: str, output_path: str):
        self.source_path = source_path
        self.output_path = output_path
        self.doc = fitz.open(source_path)

    def save(self, pages_data: Dict[int, List[Dict[str, Any]]], page_order: List[int]):
        """
        Saves the PDF with modifications.
        
        Args:
            pages_data: Dict mapping page_num (int) to list of elements.
            page_order: List of page numbers representing the new order.
        """
        # Create a new PDF for output to handle reordering easily
        out_doc = fitz.open()
        
        for page_num in page_order:
            # Copy page from source
            out_doc.insert_pdf(self.doc, from_page=page_num, to_page=page_num)
            
            # Get the new page (it's the last one added)
            page = out_doc[-1]
            page_height = page.rect.height
            
            # Get elements for this page
            elements = pages_data.get(page_num, [])
            
            for el in elements:
                el_type = el.get('type')
                
                if el_type == 'text':
                    text = el.get('text', '')
                    x = el.get('x', 0)
                    y = el.get('y', 0)
                    font_size = el.get('font_size', 12)
                    
                    # Convert Qt (top-left) to PDF (bottom-left)
                    # Qt (x, y) represents the top-left corner of the text bounding box
                    # We need to convert this to the baseline position for fitz.insert_text
                    
                    # First, convert top-left from Qt to PDF coordinates
                    pdf_x, pdf_y = CoordinateConverter.qt_to_pdf(x, y, page_height, scale=1.0)
                    
                    # pdf_y now represents the TOP of the text in PDF coordinates
                    # insert_text expects the baseline position (bottom of the text)
                    # In PDF coordinates, Y increases upward, so baseline = top - font_size
                    # We use 0.85 * font_size as a better approximation for the baseline offset
                    # (this accounts for typical font metrics where baseline is ~85% from top)
                    baseline_offset = font_size * 0.85
                    insert_pt = fitz.Point(pdf_x, pdf_y - baseline_offset)
                    
                    page.insert_text(insert_pt, text, fontsize=font_size, color=(0, 0, 0))
                    
                elif el_type == 'image':
                    pixmap = el.get('pixmap') # Expecting QPixmap or bytes?
                    # We will pass QPixmap from GUI, but we need bytes here.
                    # Or we can save QPixmap to bytes in GUI.
                    # Let's assume we get bytes or a path.
                    
                    # Actually, let's handle QPixmap in GUI and pass bytes here to keep logic pure?
                    # Or just pass the bytes.
                    image_data = el.get('image_data') # bytes
                    
                    x = el.get('x', 0)
                    y = el.get('y', 0)
                    w = el.get('w', 0)
                    h = el.get('h', 0)
                    
                    # Convert Rect to PDF
                    pdf_x0, pdf_y0, pdf_x1, pdf_y1 = CoordinateConverter.qt_rect_to_pdf_rect(x, y, w, h, page_height, scale=1.0)
                    
                    # fitz expects rect as (x0, y0, x1, y1)
                    # But wait, our utility returns (x0, y0, x1, y1) where y0 is bottom, y1 is top.
                    # fitz.Rect(x0, y0, x1, y1) works fine.
                    
                    rect = fitz.Rect(pdf_x0, pdf_y0, pdf_x1, pdf_y1)
                    
                    if image_data:
                        page.insert_image(rect, stream=image_data)

        out_doc.save(self.output_path)
        out_doc.close()
        self.doc.close()
