import pygame
from ..core import Qt, QSize

class QGridLayout:
    def __init__(self, parent=None):
        self.items = {} # (row, col) -> item
        self._parent = parent
        if parent and hasattr(parent, 'setLayout'): parent.setLayout(self)
        self._margins = (0, 0, 0, 0)
        self._spacing = 5
        self._next_row = 0
        self._next_col = 0
        self._col_count = 2  # Default column count for auto-insert
        self._row_heights = {}  # row -> height (optional per-row height)
        self._col_widths = {}   # col -> width (optional per-col width)
        
    def setColumnCount(self, count):
        """Set the number of columns for auto-insert mode."""
        self._col_count = count
        
    def setRowMinimumHeight(self, row, height):
        """Set minimum height for a specific row."""
        self._row_heights[row] = height
        
    def setColumnMinimumWidth(self, col, width):
        """Set minimum width for a specific column."""
        self._col_widths[col] = width
        
    def addWidget(self, w, row=None, col=None, rowSpan=1, colSpan=1, alignment=0):
        """Add widget at specified position, or auto-insert if row/col are None."""
        w._layout_alignment = alignment
        
        # Auto-insert mode
        if row is None or col is None:
            row = self._next_row
            col = self._next_col
            
        self.items[(row, col)] = {'widget': w, 'rs': rowSpan, 'cs': colSpan}
        
        # Update next position
        if row >= self._next_row and col >= self._next_col:
            self._next_col = col + colSpan
            if self._next_col >= self._col_count:
                self._next_col = 0
                self._next_row = row + 1
            if row > self._next_row:
                self._next_row = row
        
        if self._parent:
            w._set_parent(self._parent)
            if self._parent.isVisible(): w.show()
    def addItem(self, item, row=None, col=None, rowSpan=1, colSpan=1):
        """Add item (widget or layout) at specified or auto-calculated position."""
        if row is None or col is None:
            row = self._next_row
            col = self._next_col
            
        self.items[(row, col)] = {'widget': item, 'rs': rowSpan, 'cs': colSpan}
        
        # Update next position
        self._next_col = col + colSpan
        if self._next_col >= self._col_count:
            self._next_col = 0
            self._next_row = row + 1
            
        if hasattr(item, '_set_parent'): item._set_parent(self._parent)
        
    def removeWidget(self, w):
        to_del = [k for k, v in self.items.items() if v['widget'] == w]
        for k in to_del: del self.items[k]

    def _set_parent(self, p):
        self._parent = p
        for info in self.items.values():
            w = info['widget']
            if hasattr(w, '_set_parent'): w._set_parent(p)
            
    def setContentsMargins(self, left, top, right, bottom): self._margins = (left, top, right, bottom)
    def setSpacing(self, s): self._spacing = s
    
    def arrange(self, rect):
        if not self.items: return
        rows = max(r + info['rs'] for (r, c), info in self.items.items())
        cols = max(c + info['cs'] for (r, c), info in self.items.items())
        
        margins = self._margins
        spacing = self._spacing
        
        available_w = rect.width - margins[0] - margins[2] - (cols - 1) * spacing
        available_h = rect.height - margins[1] - margins[3] - (rows - 1) * spacing
        
        # Calculate cell sizes (can be customized per row/col)
        default_cell_w = available_w / cols if cols > 0 else available_w
        default_cell_h = available_h / rows if rows > 0 else available_h
        
        for (r, c), info in self.items.items():
            w = info['widget']
            if not getattr(w, 'isVisible', lambda: True)(): continue
            
            # Get cell dimensions (use custom or default)
            cell_w = self._col_widths.get(c, default_cell_w)
            cell_h = self._row_heights.get(r, default_cell_h)
            
            x = rect.x + margins[0]
            for i in range(c):
                x += self._col_widths.get(i, default_cell_w) + spacing
                
            y = rect.y + margins[1]
            for i in range(r):
                y += self._row_heights.get(i, default_cell_h) + spacing
            
            # Calculate span dimensions
            width = cell_w * info['cs'] + (info['cs'] - 1) * spacing
            height = cell_h * info['rs'] + (info['rs'] - 1) * spacing
            
            # Enforce minimum size if set
            min_size = getattr(w, '_min_size', None)
            if min_size:
                width = max(width, min_size[0])
                height = max(height, min_size[1])
            
            item_rect = pygame.Rect(x, y, width, height)
            w._rect = item_rect
            
            if hasattr(w, '_layout') and w._layout: w._layout.arrange(pygame.Rect(0, 0, width, height))
            elif hasattr(w, 'arrange'): w.arrange(item_rect)
