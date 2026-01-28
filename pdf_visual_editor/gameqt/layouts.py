import pygame
from .core import Qt, QSize
from .widgets import QWidget

def _get_text(item):
    if hasattr(item, 'text'):
        t = item.text
        return t() if callable(t) else str(t)
    return str(getattr(item, '_text', ''))

class QVBoxLayout:
    def __init__(self, parent=None):
        self.items, self._parent = [], parent
        if parent and hasattr(parent, 'setLayout'): parent.setLayout(self)
    def addWidget(self, w, alignment=0):
        w._layout_alignment = alignment
        self.items.append(w)
        if self._parent:
            w._set_parent(self._parent)
            if self._parent.isVisible(): w.show()
    def removeWidget(self, w):
        if w in self.items: self.items.remove(w)
    def _set_parent(self, p):
        self._parent = p
        for item in self.items:
            if hasattr(item, '_set_parent'): item._set_parent(p)
    def addLayout(self, l):
        self.items.append(l); l._parent = self._parent
        if self._parent and hasattr(l, '_set_parent'): l._set_parent(self._parent)
    def addItem(self, i): 
        self.items.append(i)
        if hasattr(i, '_set_parent'): i._set_parent(self._parent)
    def addStretch(self, s=0): 
        # Add a stretchable spacer
        spacer = type('Spacer', (), {'isVisible': lambda self: True, 'stretch': s, 'size': 0})()
        self.items.append(spacer)
    def addSpacing(self, size):
        # Add a fixed size spacer
        spacer = type('Spacer', (), {'isVisible': lambda self: True, 'stretch': 0, 'size': size})()
        self.items.append(spacer)

    def setContentsMargins(self, left, top, right, bottom): self._margins = (left, top, right, bottom)
    def setSpacing(self, s): self._spacing = s
    def arrange(self, rect):
        visible_items = [i for i in self.items if getattr(i, 'isVisible', lambda: True)()]
        if not visible_items: return
        
        margins = getattr(self, '_margins', (0,0,0,0))
        spacing = getattr(self, '_spacing', 5)  # Default spacing of 5
        
        fixed_h = 0
        expandable_count = 0
        for item in visible_items:
            class_name = item.__class__.__name__
            # Check if widget has explicit height set (more than default 100)
            widget_h = getattr(item, '_rect', None)
            if widget_h and hasattr(widget_h, 'height') and widget_h.height > 0 and widget_h.height != 100:
                fixed_h += widget_h.height
            elif class_name in ('QPushButton', 'QLabel', 'QLineEdit', 'QCheckBox', 'QRadioButton', 'QComboBox', 'QSpinBox'): 
                fixed_h += 35  # Slightly taller default
            elif class_name == 'Spacer':
                if getattr(item, 'stretch', 0) == 0: 
                    fixed_h += getattr(item, 'size', 15)
                else: expandable_count += item.stretch
            else: expandable_count += 1
        
        remaining_h = max(0, rect.height - margins[1] - margins[3] - fixed_h - (len(visible_items)-1)*spacing)
        item_h = remaining_h / expandable_count if expandable_count > 0 else 0
        
        curr_y = rect.y + margins[1]
        content_w = rect.width - margins[0] - margins[2]
        
        for item in visible_items:
            class_name = item.__class__.__name__
            
            # Determine height: use explicit height if set, otherwise defaults
            widget_h = getattr(item, '_rect', None)
            if widget_h and hasattr(widget_h, 'height') and widget_h.height > 0 and widget_h.height != 100:
                h = widget_h.height
            elif class_name in ('QPushButton', 'QLabel', 'QLineEdit', 'QCheckBox', 'QRadioButton', 'QComboBox', 'QSpinBox'):
                h = 35
            elif class_name == 'Spacer' and getattr(item, 'stretch', 0) > 0:
                h = int(item_h * item.stretch)
            elif class_name == 'Spacer':
                h = getattr(item, 'size', 15)
            else:
                h = int(item_h) if item_h > 0 else 50
            
            x = rect.x + margins[0]
            w = content_w
            
            align = getattr(item, '_layout_alignment', 0)
            # Horizontal alignment within the column
            if align & (Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignLeft):
                # Try to get a reasonable width for aligned items
                w = 150 # Default
                if hasattr(item, 'sizeHint'): 
                    sh = item.sizeHint()
                    if sh: w = sh.width()
                elif hasattr(item, 'text'):
                    # Heuristic for labels/buttons
                    font = pygame.font.SysFont(None, 18)
                    w = font.size(_get_text(item))[0] + 20
                
                w = min(content_w, w)
                
                if align & Qt.AlignmentFlag.AlignRight:
                    x = rect.x + rect.width - margins[2] - w
                elif align & Qt.AlignmentFlag.AlignHCenter:
                    x = rect.x + margins[0] + (content_w - w) // 2
                else: # AlignLeft
                    x = rect.x + margins[0]
            
            # Use computed absolute rect for this item
            item_rect = pygame.Rect(x, curr_y, w, h)
            item._rect = item_rect
            
            # Pass relative rect to nested layouts
            if hasattr(item, '_layout') and item._layout: item._layout.arrange(pygame.Rect(0, 0, item_rect.width, item_rect.height))
            elif hasattr(item, 'arrange'): item.arrange(item_rect)
            
            curr_y += h + spacing

class QHBoxLayout:
    def __init__(self, parent=None):
        self.items, self._parent = [], parent
        if parent and hasattr(parent, 'setLayout'): parent.setLayout(self)
    def addWidget(self, w, alignment=0):
        w._layout_alignment = alignment
        self.items.append(w)
        if self._parent:
            w._set_parent(self._parent)
            if self._parent.isVisible(): w.show()
    def removeWidget(self, w):
        if w in self.items: self.items.remove(w)
    def _set_parent(self, p):
        self._parent = p
        for item in self.items:
            if hasattr(item, '_set_parent'): item._set_parent(p)
    def addLayout(self, l):
        self.items.append(l); l._parent = self._parent
        if self._parent and hasattr(l, '_set_parent'): l._set_parent(self._parent)
    def addItem(self, i):
        self.items.append(i)
        if hasattr(i, '_set_parent'): i._set_parent(self._parent)
    def addStretch(self, s=0): 
        # Add a stretchable spacer
        spacer = type('Spacer', (), {'isVisible': lambda self: True, 'stretch': s, 'size': 0})()
        self.items.append(spacer)
    def addSpacing(self, size):
        # Add a fixed size spacer
        spacer = type('Spacer', (), {'isVisible': lambda self: True, 'stretch': 0, 'size': size})()
        self.items.append(spacer)

    def setContentsMargins(self, left, top, right, bottom): self._margins = (left, top, right, bottom)
    def setSpacing(self, s): self._spacing = s
    def arrange(self, rect):
        visible_items = [i for i in self.items if getattr(i, 'isVisible', lambda: True)()]
        if not visible_items: return
        margins = getattr(self, '_margins', (0,0,0,0))
        spacing = getattr(self, '_spacing', 0)
        
        # Sizing heuristic
        fixed_w = 0
        expandable_count = 0
        for item in visible_items:
            class_name = item.__class__.__name__
            if class_name in ('QPushButton', 'QLabel', 'QLineEdit', 'QCheckBox'): 
                 font = pygame.font.SysFont(None, 18)
                 w = font.size(_get_text(item))[0] + 20
                 fixed_w += w
            elif class_name == 'Spacer':
                if getattr(item, 'stretch', 0) == 0: 
                    fixed_w += getattr(item, 'size', 10)
                else: expandable_count += item.stretch
            else: expandable_count += 1
            
        available_w = rect.width - margins[0] - margins[2]
        remaining_w = max(0, available_w - fixed_w - (len(visible_items)-1)*spacing)
        unit_w = remaining_w / expandable_count if expandable_count > 0 else 0
        
        curr_x = rect.x + margins[0]
        content_h = rect.height - margins[1] - margins[3]
        
        for item in visible_items:
            class_name = item.__class__.__name__
            w = (int(unit_w) if expandable_count > 0 else (available_w // len(visible_items))) # fallback
            if class_name in ('QPushButton', 'QLabel', 'QLineEdit', 'QCheckBox'):
                font = pygame.font.SysFont(None, 18)
                w = font.size(_get_text(item))[0] + 20
            elif class_name == 'Spacer':
                w = int(unit_w * item.stretch) if item.stretch > 0 else getattr(item, 'size', 10)
                
            y = rect.y + margins[1]
            h = content_h
            
            # Vertical alignment within the row (simple)
            item_rect = pygame.Rect(curr_x, y, w, h)
            item._rect = item_rect
            # Pass relative rect to nested layouts
            if hasattr(item, '_layout') and item._layout: item._layout.arrange(pygame.Rect(0, 0, item_rect.width, item_rect.height))
            elif hasattr(item, 'arrange'): item.arrange(item_rect)
            
            curr_x += w + spacing

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
            
            item_rect = pygame.Rect(x, y, width, height)
            w._rect = item_rect
            
            if hasattr(w, '_layout') and w._layout: w._layout.arrange(pygame.Rect(0, 0, width, height))
            elif hasattr(w, 'arrange'): w.arrange(item_rect)

class QStackedLayout:
    def __init__(self, parent=None):
        self.items = []
        self._parent = parent
        self._current_index = -1
        if parent and hasattr(parent, 'setLayout'): parent.setLayout(self)
    def addWidget(self, w):
        self.items.append(w)
        if self._parent: w._set_parent(self._parent)
        w.hide()
        if self._current_index == -1: self.setCurrentIndex(0)
    def _set_parent(self, p):
        self._parent = p
        for item in self.items:
            if hasattr(item, '_set_parent'): item._set_parent(p)
    def setCurrentIndex(self, index):
        if 0 <= index < len(self.items):
            if 0 <= self._current_index < len(self.items):
                self.items[self._current_index].hide()
            self._current_index = index
            self.items[index].show()
    def arrange(self, rect):
        if 0 <= self._current_index < len(self.items):
            w = self.items[self._current_index]
            w._rect = rect
            if hasattr(w, '_layout') and w._layout: w._layout.arrange(pygame.Rect(0, 0, rect.width, rect.height))
            elif hasattr(w, 'arrange'): w.arrange(rect)

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
            from .widgets import QLabel
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
                field_rect = pygame.Rect(rect.x + margins[0] + label_w + self._spacing, curr_y, field_w, h)
                field._rect = field_rect
                if getattr(field, 'isVisible', lambda: True)():
                    if hasattr(field, '_layout') and field._layout: 
                        field._layout.arrange(pygame.Rect(0, 0, field_rect.width, field_rect.height))
                    elif hasattr(field, 'arrange'): 
                        field.arrange(field_rect)
            
            curr_y += h + spacing

class QSplitter(QWidget):
    def __init__(self, orientation=Qt.Orientation.Horizontal, parent=None):
        super().__init__(parent); self._items, self._orientation, self._sizes = [], orientation, None
    def addWidget(self, w): self._items.append(w); w._set_parent(self); w.show()
    def setSizes(self, sizes): self._sizes = sizes
    def _draw_recursive(self, offset=pygame.Vector2(0,0)):
        if not self.isVisible(): return
        visible_items = [i for i in self._items if i.isVisible()]
        if visible_items:
            n = len(visible_items)
            proportions = [self._sizes[self._items.index(i)] for i in visible_items] if self._sizes and len(self._sizes) == len(self._items) else [1]*n
            total = sum(proportions); curr = 0
            for i, item in enumerate(visible_items):
                p = proportions[i] / total
                if self._orientation == Qt.Orientation.Horizontal:
                    w = int(self._rect.width * p)
                    item._rect = pygame.Rect(curr, 0, w, self._rect.height); curr += w
                else:
                    h = int(self._rect.height * p)
                    item._rect = pygame.Rect(0, curr, self._rect.width, h); curr += h
        super()._draw_recursive(offset)

class QSpacerItem:
    def __init__(self, w, h, hPolicy=None, vPolicy=None):
        self._rect = pygame.Rect(0, 0, w, h)
    def isVisible(self): return True
    def _set_parent(self, p): pass
    @property
    def stretch(self): return 0
