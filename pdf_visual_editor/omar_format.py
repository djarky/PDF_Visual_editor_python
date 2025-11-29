"""
OMAR Project File Format Handler

Handles serialization and deserialization of PDF Visual Editor project files (.omar).
.omar files are JSON-based and store all project state including:
- Source PDF reference or embedded data
- All page elements (text, images, shapes)
- Element transforms, opacity, visibility
- Inspector tree structure and organization
- Application settings (theme, etc.)
"""

import json
import base64
import os
from typing import Dict, List, Any, Optional
from qt_compat import QGraphicsItem, QGraphicsTextItem, QGraphicsPixmapItem, QBuffer, QIODevice


class OmarFormat:
    """Handler for .omar project file format."""
    
    VERSION = "1.0"
    
    @staticmethod
    def save_project(filepath: str, project_data: Dict[str, Any]) -> None:
        """
        Save project data to .omar file.
        
        Args:
            filepath: Path to save .omar file
            project_data: Complete project data dictionary
        """
        # Add version and app identifier
        project_data["version"] = OmarFormat.VERSION
        project_data["app"] = "PDF Visual Editor"
        
        # Write to file with indentation for readability
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(project_data, f, indent=2, ensure_ascii=False)
    
    @staticmethod
    def load_project(filepath: str) -> Dict[str, Any]:
        """
        Load project data from .omar file.
        
        Args:
            filepath: Path to .omar file
            
        Returns:
            Project data dictionary
            
        Raises:
            ValueError: If file format is invalid
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            project_data = json.load(f)
        
        # Validate format
        if not OmarFormat.validate_project(project_data):
            raise ValueError("Invalid .omar file format")
        
        return project_data
    
    @staticmethod
    def validate_project(project_data: Dict[str, Any]) -> bool:
        """
        Validate project data structure.
        
        Args:
            project_data: Project data to validate
            
        Returns:
            True if valid, False otherwise
        """
        required_keys = ["version", "app", "source_pdf", "pages"]
        return all(key in project_data for key in required_keys)
    
    @staticmethod
    def serialize_graphics_item(item: QGraphicsItem) -> Optional[Dict[str, Any]]:
        """
        Serialize a QGraphicsItem to dictionary.
        
        Args:
            item: Graphics item to serialize
            
        Returns:
            Dictionary with item data, or None if item should be skipped
        """
        # Get transform matrix
        t = item.transform()
        transform_matrix = [t.m11(), t.m12(), t.m21(), t.m22(), t.dx(), t.dy()]
        
        # Get position
        pos = item.pos()
        
        # Get common properties
        base_data = {
            "x": pos.x(),
            "y": pos.y(),
            "transform_matrix": transform_matrix,
            "opacity": item.opacity(),
            "visible": item.isVisible(),
            "z_value": item.zValue()
        }
        
        # Serialize based on type
        if isinstance(item, QGraphicsTextItem):
            return {
                **base_data,
                "type": "text",
                "text": item.toPlainText(),
                "font_family": item.font().family(),
                "font_size": item.font().pointSize(),
                "font_bold": item.font().bold(),
                "font_italic": item.font().italic()
            }
        
        elif isinstance(item, QGraphicsPixmapItem):
            # Encode pixmap as base64
            pixmap = item.pixmap()
            buffer = QBuffer()
            buffer.open(QIODevice.OpenModeFlag.ReadWrite)
            pixmap.save(buffer, "PNG")
            image_data = base64.b64encode(buffer.data().data()).decode('utf-8')
            
            return {
                **base_data,
                "type": "image",
                "image_data": image_data,
                "width": pixmap.width(),
                "height": pixmap.height()
            }
        
        else:
            # Generic shape/rect
            rect = item.boundingRect()
            return {
                **base_data,
                "type": "shape",
                "width": rect.width(),
                "height": rect.height()
            }
    
    @staticmethod
    def embed_pdf(pdf_path: str) -> str:
        """
        Embed PDF file as base64 string.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Base64 encoded PDF data
        """
        with open(pdf_path, 'rb') as f:
            pdf_data = f.read()
        return base64.b64encode(pdf_data).decode('utf-8')
    
    @staticmethod
    def extract_embedded_pdf(pdf_data: str, output_path: str) -> None:
        """
        Extract embedded PDF data to file.
        
        Args:
            pdf_data: Base64 encoded PDF data
            output_path: Where to save extracted PDF
        """
        pdf_bytes = base64.b64decode(pdf_data)
        with open(output_path, 'wb') as f:
            f.write(pdf_bytes)
    
    @staticmethod
    def create_empty_project(source_pdf_path: str) -> Dict[str, Any]:
        """
        Create empty project structure for a new PDF.
        
        Args:
            source_pdf_path: Path to source PDF
            
        Returns:
            Empty project data structure
        """
        return {
            "version": OmarFormat.VERSION,
            "app": "PDF Visual Editor",
            "source_pdf": {
                "path": source_pdf_path,
                "embedded": False,
                "data": None
            },
            "settings": {
                "theme": "light",
                "current_page": 0
            },
            "pages": [],
            "page_order": []
        }
