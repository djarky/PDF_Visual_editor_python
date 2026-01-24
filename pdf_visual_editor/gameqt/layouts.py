import pygame
from .core import Qt
from .widgets import QWidget

class QVBoxLayout:
    def __init__(self, parent=None):
        self.items, self._parent = [], parent
        if parent and hasattr(parent, 'setLayout'): parent.setLayout(self)
    def addWidget(self, w, alignment=0):
        self.items.append(w); (w._set_parent(self._parent) if self._parent else None)
    def addLayout(self, l): self.items.append(l); l._parent = self._parent
    def addStretch(self, s=0): 
        # Add a stretchable spacer
        spacer = type('Spacer', (), {'isVisible': lambda: True, 'stretch': s})()
        self.items.append(spacer)
    def setContentsMargins(self, left, top, right, bottom): self._margins = (left, top, right, bottom)
    def setSpacing(self, s): self._spacing = s
    def arrange(self, rect):
        visible_items = [i for i in self.items if getattr(i, 'isVisible', lambda: True)()]
        if not visible_items: return
        
        # Calculate space
        total_h = rect.height
        fixed_h = 0
        expandable_count = 0
        
        for item in visible_items:
            # Check for known fixed-height widgets or spacers
            class_name = item.__class__.__name__
            if class_name in ('QPushButton', 'QLabel', 'QLineEdit'):
                fixed_h += 30 # Standard fixed height
            elif class_name == 'Spacer':
                if getattr(item, 'stretch', 0) == 0:
                    fixed_h += 10 # Fixed spacer
                else:
                    expandable_count += item.stretch
            else:
                expandable_count += 1 # Default expand
                
        remaining_h = max(0, total_h - fixed_h)
        item_h = remaining_h / expandable_count if expandable_count > 0 else 0
        
        curr_y = 0
        for i, item in enumerate(visible_items):
            class_name = item.__class__.__name__
            h = 0
            if class_name in ('QPushButton', 'QLabel', 'QLineEdit'):
                h = 30
            elif class_name == 'Spacer':
                if getattr(item, 'stretch', 0) == 0:
                    h = 10
                else:
                    h = item_h * item.stretch
            else:
                h = item_h
                
            r = pygame.Rect(rect.x, rect.y + curr_y, rect.width, h)
            
            # Apply margins/padding if reasonable? For now raw.
            if hasattr(item, '_rect'): item._rect = r
            if hasattr(item, '_layout') and item._layout: item._layout.arrange(r)
            elif hasattr(item, 'arrange'): item.arrange(r)
            
            curr_y += h

class QHBoxLayout:
    def __init__(self, parent=None):
        self.items, self._parent = [], parent
        if parent and hasattr(parent, 'setLayout'): parent.setLayout(self)
    def addWidget(self, w, alignment=0):
        self.items.append(w); (w._set_parent(self._parent) if self._parent else None)
    def addLayout(self, l): self.items.append(l); l._parent = self._parent
    def addStretch(self, s=0): 
        # Add a stretchable spacer
        spacer = type('Spacer', (), {'isVisible': lambda: True, 'stretch': s})()
        self.items.append(spacer)
    def setContentsMargins(self, left, top, right, bottom): self._margins = (left, top, right, bottom)
    def setSpacing(self, s): self._spacing = s
    def arrange(self, rect):
        visible_items = [i for i in self.items if getattr(i, 'isVisible', lambda: True)()]
        if not visible_items: return
        w = rect.width / len(visible_items)
        for i, item in enumerate(visible_items):
            r = pygame.Rect(i*w, 0, w, rect.height)
            if hasattr(item, '_rect'): item._rect = r
            if hasattr(item, '_layout') and item._layout: item._layout.arrange(r)
            elif hasattr(item, 'arrange'): item.arrange(r)

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
