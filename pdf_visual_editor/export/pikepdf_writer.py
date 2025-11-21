import pikepdf
from typing import List, Dict, Any, Optional
from utils.geometry import CoordinateConverter
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import QBuffer, QIODevice
import io

class PikePDFWriter:
    """
    Handles saving modified PDFs using pikepdf to preserve all PDF features.
    This replaces the PyMuPDF-based PDFWriter for better PDF preservation.
    """
    def __init__(self, source_path: str):
        """
        Initialize the writer with a source PDF.
        
        Args:
            source_path: Path to the source PDF file
        """
        self.source_path = source_path
        self.pdf = pikepdf.open(source_path)
    
    def save(self, output_path: str, pages_data: Dict[int, List[Dict[str, Any]]], 
             page_order: Optional[List[int]] = None):
        """
        Saves the PDF with modifications.
        
        Args:
            output_path: Path where the output PDF should be saved
            pages_data: Dict mapping page_num (int) to list of element modifications
            page_order: Optional list of page numbers for reordering pages
        """
        # Create a new PDF for output
        out_pdf = pikepdf.new()
        
        # Determine page order
        if page_order is None:
            page_order = list(range(len(self.pdf.pages)))
        
        # Process each page in order
        for page_num in page_order:
            if page_num >= len(self.pdf.pages):
                continue
                
            # Copy the original page
            page = self.pdf.pages[page_num]
            out_pdf.pages.append(page)
            
            # Get the last added page to modify it
            current_page = out_pdf.pages[-1]
            
            # Get page dimensions
            mediabox = current_page.MediaBox
            page_width = float(mediabox[2] - mediabox[0])
            page_height = float(mediabox[3] - mediabox[1])
            
            # Get elements for this page
            elements = pages_data.get(page_num, [])
            
            # Track elements to remove (by marking them)
            # pikepdf doesn't have a simple "remove element" API,
            # so we'll overlay new content on top
            
            # Apply modifications
            for el in elements:
                el_type = el.get('type')
                
                if el_type == 'text':
                    self._add_text_element(current_page, el, page_height)
                elif el_type == 'image':
                    self._add_image_element(current_page, el, page_height, out_pdf)
        
        # Save the output PDF
        out_pdf.save(output_path)
        out_pdf.close()
    
    def _add_text_element(self, page, element: Dict[str, Any], page_height: float):
        """
        Adds a text element to a page.
        
        Args:
            page: pikepdf Page object
            element: Element dictionary with text, position, and formatting
            page_height: Height of the page for coordinate conversion
        """
        text = element.get('text', '')
        x = element.get('x', 0)
        y = element.get('y', 0)
        font_size = element.get('font_size', 12)
        
        # Convert Qt coordinates to PDF coordinates
        pdf_x, pdf_y = CoordinateConverter.qt_to_pdf(x, y, page_height, scale=1.0)
        
        # Adjust for baseline (85% offset as in pdf_writer.py)
        baseline_offset = font_size * 0.85
        pdf_y_baseline = pdf_y - baseline_offset
        
        # Create content stream for text
        # This is a simplified version - for production, consider using reportlab or similar
        content = f"""
        BT
        /F1 {font_size} Tf
        {pdf_x} {pdf_y_baseline} Td
        ({self._escape_pdf_string(text)}) Tj
        ET
        """.encode('latin-1')
        
        # Append to page content stream
        if '/Contents' in page:
            # Get existing content
            existing_content = page.Contents.read_bytes()
            # Append new content
            new_content = existing_content + b'\n' + content
            page.Contents = pikepdf.Stream(page.pdf, new_content)
        else:
            # Create new content stream
            page.Contents = pikepdf.Stream(page.pdf, content)
    
    def _add_image_element(self, page, element: Dict[str, Any], page_height: float, pdf: pikepdf.Pdf):
        """
        Adds an image element to a page.
        
        Args:
            page: pikepdf Page object
            element: Element dictionary with image data and position
            page_height: Height of the page for coordinate conversion
            pdf: The output PDF document
        """
        image_data = element.get('image_data')
        x = element.get('x', 0)
        y = element.get('y', 0)
        w = element.get('w', 100)
        h = element.get('h', 100)
        
        if not image_data:
            return
        
        # Convert Qt rect to PDF rect
        pdf_x0, pdf_y0, pdf_x1, pdf_y1 = CoordinateConverter.qt_rect_to_pdf_rect(
            x, y, w, h, page_height, scale=1.0
        )
        
        # Create image XObject from bytes
        try:
            # Convert image bytes to PIL Image first
            from PIL import Image
            img_buffer = io.BytesIO(image_data)
            pil_image = Image.open(img_buffer)
            
            # Convert to RGB if necessary
            if pil_image.mode not in ('RGB', 'L'):
                pil_image = pil_image.convert('RGB')
            
            # Create pikepdf image
            img_obj = pikepdf.PdfImage(pil_image)
            
            # Generate a unique name for this image
            img_name = f'/Im{len(page.get("/Resources", {}).get("/XObject", {}))}'
            
            # Add to page resources
            if '/Resources' not in page:
                page.Resources = pikepdf.Dictionary()
            if '/XObject' not in page.Resources:
                page.Resources.XObject = pikepdf.Dictionary()
            
            page.Resources.XObject[img_name] = img_obj
            
            # Create content stream to place the image
            # PDF uses: cm (concat matrix), Do (invoke XObject)
            # [a b c d e f] cm: transformation matrix
            # For placing at (x, y) with size (w, h):
            # scale: w, 0, 0, h; translate: x, y
            content = f"""
            q
            {pdf_x1 - pdf_x0} 0 0 {pdf_y1 - pdf_y0} {pdf_x0} {pdf_y0} cm
            {img_name} Do
            Q
            """.encode('latin-1')
            
            # Append to page content
            if '/Contents' in page:
                existing_content = page.Contents.read_bytes()
                new_content = existing_content + b'\n' + content
                page.Contents = pikepdf.Stream(pdf, new_content)
            else:
                page.Contents = pikepdf.Stream(pdf, content)
                
        except Exception as e:
            print(f"Failed to add image: {e}")
    
    def _escape_pdf_string(self, text: str) -> str:
        """
        Escapes special characters in PDF strings.
        
        Args:
            text: Input text
            
        Returns:
            Escaped text suitable for PDF string literals
        """
        # Escape backslashes and parentheses
        text = text.replace('\\', '\\\\')
        text = text.replace('(', '\\(')
        text = text.replace(')', '\\)')
        return text
    
    def close(self):
        """Close the PDF document."""
        if self.pdf:
            self.pdf.close()
