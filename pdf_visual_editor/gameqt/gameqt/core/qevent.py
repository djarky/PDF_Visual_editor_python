from .qt_enums import Qt
from .qrect import QPoint, QPointF

class QMouseEvent:
    def __init__(self, pos, button=Qt.MouseButton.NoButton, buttons=None, modifiers=Qt.KeyboardModifier.NoModifier):
        self._pos = QPointF(pos)
        self._button = button
        self._buttons = buttons if buttons is not None else button
        self._modifiers = modifiers
        self._accepted = True
    def pos(self): return self._pos
    def button(self): return self._button
    def position(self): return self._pos
    def buttons(self): return self._buttons
    def modifiers(self): return self._modifiers
    def accept(self): self._accepted = True
    def ignore(self): self._accepted = False
    def isAccepted(self): return self._accepted

class QWheelEvent:
    def __init__(self, pos, angleDelta, modifiers=Qt.KeyboardModifier.NoModifier):
        self._pos = QPointF(pos)
        self._angleDelta = QPoint(angleDelta.x(), angleDelta.y())
        self._modifiers = modifiers
        self._accepted = True
    def pos(self): return self._pos
    def angleDelta(self): return self._angleDelta
    def pixelDelta(self): return self._angleDelta 
    def modifiers(self): return self._modifiers
    def accept(self): self._accepted = True
    def ignore(self): self._accepted = False
    def isAccepted(self): return self._accepted
