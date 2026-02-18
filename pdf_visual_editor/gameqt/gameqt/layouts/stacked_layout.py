import pygame
from ..core import Qt, QSize

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
