import pygame

class QSpacerItem:
    def __init__(self, w, h, hPolicy=None, vPolicy=None):
        self._rect = pygame.Rect(0, 0, w, h)
    def isVisible(self): return True
    def _set_parent(self, p): pass
    @property
    def stretch(self): return 0
