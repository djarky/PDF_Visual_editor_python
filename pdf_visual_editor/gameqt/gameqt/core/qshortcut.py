import pygame
from .qobject import QObject, Signal

class QShortcut(QObject):
    def __init__(self, sequence, parent=None):
        super().__init__(parent)
        self._sequence = sequence
        self.activated = Signal()
        from ..application import QApplication
        if QApplication._instance:
            if not hasattr(QApplication._instance, '_shortcuts'):
                QApplication._instance._shortcuts = []
            QApplication._instance._shortcuts.append(self)
    def setKey(self, seq): self._sequence = seq
