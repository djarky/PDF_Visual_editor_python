from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTImage, LTFigure, LTTextBoxHorizontal
from typing import List, Dict, Any

class LayoutAnalyzer:
    """
    Uses pdfminer.six to analyze the layout of a PDF page and extract elements.
    """
    def __init__(self, file_path: str):
        self.file_path = file_path

    def analyze_page(self, page_num: int) -> List[Dict[str, Any]]:
        """
        Analyzes a specific page and returns a list of elements (text, images).
        Note: pdfminer.six uses 0-based indexing for pages in extract_pages if specified,
        but usually iterates all. We will iterate and pick the matching page.
        """
        elements = []
        
        # extract_pages yields LTPage objects
        # We need to find the specific page_num (0-indexed)
        current_page = 0
        for page_layout in extract_pages(self.file_path):
            if current_page == page_num:
                for element in page_layout:
                    if isinstance(element, LTTextContainer):
                        elements.append({
                            'type': 'text',
                            'bbox': element.bbox,  # (x0, y0, x1, y1) - PDF coordinates (bottom-left origin)
                            'text': element.get_text(),
                            'font_size': self._get_avg_font_size(element)
                        })
                    elif isinstance(element, (LTImage, LTFigure)):
                        elements.append({
                            'type': 'image',
                            'bbox': element.bbox
                        })
                break
            current_page += 1
            
        return elements

    def _get_avg_font_size(self, element: LTTextContainer) -> float:
        """Helper to estimate font size from a text container."""
        sizes = []
        for text_line in element:
            if isinstance(text_line, LTTextBoxHorizontal): 
                 for char in text_line:
                     if hasattr(char, 'size'):
                         sizes.append(char.size)
            elif hasattr(text_line, 'size'): # LTChar
                 sizes.append(text_line.size)
            elif hasattr(text_line, '_objs'): # Recursive check for lines
                for char in text_line._objs:
                    if hasattr(char, 'size'):
                        sizes.append(char.size)
                        
        if not sizes:
            return 12.0 # Default
        return sum(sizes) / len(sizes)
