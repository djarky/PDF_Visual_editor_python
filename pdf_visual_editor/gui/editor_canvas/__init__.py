"""
gui.editor_canvas package — re-exports all public classes.

This package was refactored from a single editor_canvas.py file.
All existing imports like `from .editor_canvas import EditorCanvas` continue to work.
"""

from .editor_scene import EditorScene
from .editable_text_item import EditableTextItem
from .resizer_handle import ResizerHandle
from .resizable_mixin import ResizableMixin
from .resizable_pixmap_item import ResizablePixmapItem
from .editor_canvas import EditorCanvas

__all__ = [
    'EditorScene',
    'EditableTextItem',
    'ResizerHandle',
    'ResizableMixin',
    'ResizablePixmapItem',
    'EditorCanvas',
]
