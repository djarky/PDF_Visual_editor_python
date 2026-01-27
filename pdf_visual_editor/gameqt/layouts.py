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
        self.items.append(w); (w._set_parent(self._parent) if self._parent else None)
    def addLayout(self, l): self.items.append(l); l._parent = self._parent
    def addItem(self, i): 
        self.items.append(i)
        if hasattr(i, '_set_parent'): i._set_parent(self._parent)
    def addStretch(self, s=0): 
        # Add a stretchable spacer
        spacer = type('Spacer', (), {'isVisible': lambda self: True, 'stretch': s})()
        self.items.append(spacer)
    def setContentsMargins(self, left, top, right, bottom): self._margins = (left, top, right, bottom)
    def setSpacing(self, s): self._spacing = s
    def arrange(self, rect):
        visible_items = [i for i in self.items if getattr(i, 'isVisible', lambda: True)()]
        if not visible_items: return
        
        margins = getattr(self, '_margins', (0,0,0,0))
        spacing = getattr(self, '_spacing', 0)
        
        fixed_h = 0
        expandable_count = 0
        for item in visible_items:
            class_name = item.__class__.__name__
            if class_name in ('QPushButton', 'QLabel', 'QLineEdit'): fixed_h += 30 
            elif class_name == 'Spacer':
                if getattr(item, 'stretch', 0) == 0: fixed_h += 10
                else: expandable_count += item.stretch
            else: expandable_count += 1
        
        remaining_h = max(0, rect.height - margins[1] - margins[3] - fixed_h - (len(visible_items)-1)*spacing)
        item_h = remaining_h / expandable_count if expandable_count > 0 else 0
        
        curr_y = rect.y + margins[1]
        content_w = rect.width - margins[0] - margins[2]
        
        for item in visible_items:
            class_name = item.__class__.__name__
            h = 30 if class_name in ('QPushButton', 'QLabel', 'QLineEdit', 'QCheckBox', 'QRadioButton', 'QComboBox', 'QSpinBox') else (int(item_h * item.stretch) if class_name == 'Spacer' and getattr(item, 'stretch', 0) > 0 else (10 if class_name == 'Spacer' else int(item_h)))
            
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
            
            # Pass this rect to nested layouts so they know where to start
            if hasattr(item, '_layout') and item._layout: item._layout.arrange(item_rect)
            elif hasattr(item, 'arrange'): item.arrange(item_rect)
            
            curr_y += h + spacing

class QHBoxLayout:
    def __init__(self, parent=None):
        self.items, self._parent = [], parent
        if parent and hasattr(parent, 'setLayout'): parent.setLayout(self)
    def addWidget(self, w, alignment=0):
        w._layout_alignment = alignment
        self.items.append(w); (w._set_parent(self._parent) if self._parent else None)
    def addLayout(self, l): self.items.append(l); l._parent = self._parent
    def addItem(self, i):
        self.items.append(i)
        if hasattr(i, '_set_parent'): i._set_parent(self._parent)
    def addStretch(self, s=0): 
        # Add a stretchable spacer
        spacer = type('Spacer', (), {'isVisible': lambda self: True, 'stretch': s})()
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
                if getattr(item, 'stretch', 0) == 0: fixed_w += 10
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
                w = int(unit_w * item.stretch) if item.stretch > 0 else 10
                
            y = rect.y + margins[1]
            h = content_h
            
            # Vertical alignment within the row (simple)
            item_rect = pygame.Rect(curr_x, y, w, h)
            item._rect = item_rect
            if hasattr(item, '_layout') and item._layout: item._layout.arrange(item_rect)
            elif hasattr(item, 'arrange'): item.arrange(item_rect)
            
            curr_x += w + spacing

class QGridLayout:
    def __init__(self, parent=None):
        self.items = {} # (row, col) -> item
        self._parent = parent
        if parent and hasattr(parent, 'setLayout'): parent.setLayout(self)
        self._margins = (0, 0, 0, 0)
        self._spacing = 5
    def addWidget(self, w, row, col, rowSpan=1, colSpan=1, alignment=0):
        w._layout_alignment = alignment
        self.items[(row, col)] = {'widget': w, 'rs': rowSpan, 'cs': colSpan}
        (w._set_parent(self._parent) if self._parent else None)
    def addItem(self, i):
        # Grid addItem is tricky without row/col. Assume next available? 
        # For now just append to internal list for generic layout logic if needed
        if not hasattr(self, '_generic_items'): self._generic_items = []
        self._generic_items.append(i)
        if hasattr(i, '_set_parent'): i._set_parent(self._parent)
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
        
        cell_w = available_w / cols if cols > 0 else available_w
        cell_h = available_h / rows if rows > 0 else available_h
        
        for (r, c), info in self.items.items():
            w = info['widget']
            if not w.isVisible(): continue
            
            x = rect.x + margins[0] + c * (cell_w + spacing)
            y = rect.y + margins[1] + r * (cell_h + spacing)
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
        (w._set_parent(self._parent) if self._parent else None)
        w.hide()
        if self._current_index == -1: self.setCurrentIndex(0)
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
        self._label_width = 100

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

    def setContentsMargins(self, left, top, right, bottom): self._margins = (left, top, right, bottom)
    def setSpacing(self, s): self._spacing = s

    def arrange(self, rect):
        if not self.rows: return
        
        margins = self._margins
        spacing = self._spacing
        label_w = self._label_width
        
        curr_y = rect.y + margins[1]
        field_w = rect.width - margins[0] - margins[2] - label_w - spacing
        
        for label, field in self.rows:
            h = 30 # Fixed row height for now
            
            # Label rect
            if label:
                label_rect = pygame.Rect(rect.x + margins[0], curr_y, label_w, h)
                label._rect = label_rect
                if label.isVisible():
                    if hasattr(label, '_layout') and label._layout: label._layout.arrange(label_rect)
                    elif hasattr(label, 'arrange'): label.arrange(label_rect)
            
            # Field rect
            if field:
                field_rect = pygame.Rect(rect.x + margins[0] + label_w + spacing, curr_y, field_w, h)
                field._rect = field_rect
                if field.isVisible():
                    if hasattr(field, '_layout') and field._layout: field._layout.arrange(field_rect)
                    elif hasattr(field, 'arrange'): field.arrange(field_rect)
            
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
