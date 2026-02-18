import pygame
from ..core import Qt, QSize
from ..widgets import QWidget

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
            
            # Enforce minimum size if set
            min_size = getattr(item, '_min_size', None)
            if min_size:
                w = max(w, min_size[0])
                h = max(h, min_size[1])
            
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
            
            # Enforce minimum size if set
            min_size = getattr(item, '_min_size', None)
            if min_size:
                w = max(w, min_size[0])
                h = max(h, min_size[1])
            
            # Vertical alignment within the row (simple)
            item_rect = pygame.Rect(curr_x, y, w, h)
            item._rect = item_rect
            # Pass relative rect to nested layouts
            if hasattr(item, '_layout') and item._layout: item._layout.arrange(pygame.Rect(0, 0, item_rect.width, item_rect.height))
            elif hasattr(item, 'arrange'): item.arrange(item_rect)
            
            curr_x += w + spacing
