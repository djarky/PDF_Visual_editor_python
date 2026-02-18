import pygame
from ..core import Qt, QSize

class QFormLayout:
    def __init__(self, parent=None):
        self.rows = [] # List of (label_widget, field_widget)
        self._parent = parent
        if parent and hasattr(parent, 'setLayout'): parent.setLayout(self)
        self._margins = (10, 10, 10, 10)
        self._spacing = 10
        self._label_width = 120
        self._row_heights = {}  # row_index -> height
        self._row_spacing = {}  # row_index -> spacing after this row

    def setLabelWidth(self, width):
        """Set the width for all labels."""
        self._label_width = width
        
    def setRowMinimumHeight(self, row, height):
        """Set minimum height for a specific row."""
        self._row_heights[row] = height
        
    def setRowSpacing(self, row, spacing):
        """Set custom spacing after a specific row."""
        self._row_spacing[row] = spacing

    def addRow(self, label, field):
        if isinstance(label, str):
            from ..widgets import QLabel
            label_widget = QLabel(label, self._parent)
        else:
            label_widget = label
        
        self.rows.append((label_widget, field))
        if self._parent:
            if label_widget: label_widget._set_parent(self._parent)
            if field: field._set_parent(self._parent)
            
    def removeWidget(self, w):
        self.rows = [(l, f) for l, f in self.rows if l != w and f != w]

    def _set_parent(self, p):
        self._parent = p
        for label, field in self.rows:
            if label and hasattr(label, '_set_parent'): label._set_parent(p)
            if field and hasattr(field, '_set_parent'): field._set_parent(p)

    def setContentsMargins(self, left, top, right, bottom): self._margins = (left, top, right, bottom)
    def setSpacing(self, s): self._spacing = s

    def _calculate_row_height(self, row_idx, label, field):
        """Calculate dynamic height based on content."""
        if row_idx in self._row_heights:
            return self._row_heights[row_idx]
        
        height = 35  # Default minimum
        
        # Check field type for taller widgets
        if field:
            field_class = field.__class__.__name__
            if field_class in ('QTextEdit', 'QListWidget', 'QTreeWidget'):
                height = max(height, 100)
            elif field_class in ('QComboBox', 'QSpinBox'):
                height = max(height, 32)
                
        return height

    def arrange(self, rect):
        if not self.rows: return
        
        margins = self._margins
        label_w = self._label_width
        
        curr_y = rect.y + margins[1]
        field_w = rect.width - margins[0] - margins[2] - label_w - self._spacing
        
        for idx, (label, field) in enumerate(self.rows):
            h = self._calculate_row_height(idx, label, field)
            spacing = self._row_spacing.get(idx, self._spacing)
            
            # Label rect
            if label:
                label_rect = pygame.Rect(rect.x + margins[0], curr_y, label_w, h)
                label._rect = label_rect
                if getattr(label, 'isVisible', lambda: True)():
                    if hasattr(label, '_layout') and label._layout: 
                        label._layout.arrange(pygame.Rect(0, 0, label_rect.width, label_rect.height))
                    elif hasattr(label, 'arrange'): 
                        label.arrange(label_rect)
            
            # Field rect
            if field:
                # Enforce minimum size if set
                min_size = getattr(field, '_min_size', None)
                if min_size:
                    field_w = max(field_w, min_size[0])
                    h = max(h, min_size[1])
                
                field_rect = pygame.Rect(rect.x + margins[0] + label_w + self._spacing, curr_y, field_w, h)
                field._rect = field_rect
                if getattr(field, 'isVisible', lambda: True)():
                    if hasattr(field, '_layout') and field._layout: 
                        field._layout.arrange(pygame.Rect(0, 0, field_rect.width, field_rect.height))
                    elif hasattr(field, 'arrange'): 
                        field.arrange(field_rect)
            
            curr_y += h + spacing
