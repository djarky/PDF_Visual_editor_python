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

class QKeyEvent:
    def __init__(self, key, modifiers=0, text=""):
        self._key = key
        self._modifiers = modifiers
        self._text = text
        self._accepted = True
    def key(self): return self._key
    def modifiers(self): return self._modifiers
    def text(self): return self._text
    def accept(self): self._accepted = True
    def ignore(self): self._accepted = False
    def isAccepted(self): return self._accepted
    def matches(self, sequence_key):
        import pygame
        # Check against QKeySequence.StandardKey or an actual QKeySequence
        # StandardKey constants are expected to be ints: Cut=1, Copy=2, Paste=3
        relevant_mods = self._modifiers & (pygame.KMOD_CTRL | pygame.KMOD_ALT | pygame.KMOD_SHIFT | pygame.KMOD_META)
        is_ctrl_only = (relevant_mods == pygame.KMOD_CTRL) or (relevant_mods == pygame.KMOD_META)
        
        if sequence_key == 1: # Cut
            return self._key == pygame.K_x and is_ctrl_only
        elif sequence_key == 2: # Copy
            return self._key == pygame.K_c and is_ctrl_only
        elif sequence_key == 3: # Paste
            return self._key == pygame.K_v and is_ctrl_only
        elif hasattr(sequence_key, 'matches'):
            return sequence_key.matches(self._key, self._modifiers)
        return False
