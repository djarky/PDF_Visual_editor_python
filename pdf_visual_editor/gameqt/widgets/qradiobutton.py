import pygame
from ..core import Signal
from .qwidget import QWidget

class QRadioButton(QWidget):
    def __init__(self, text="", parent=None):
        super().__init__(parent)
        self._text = text
        self._checked = False
        self.toggled = Signal(bool)
        self._rect.height = 25
    def text(self): return self._text
    def setChecked(self, b):
        if self._checked == b: return
        self._checked = b
        if b and self._parent:
            for child in self._parent._children:
                if isinstance(child, QRadioButton) and child != self:
                    child.setChecked(False)
        self.toggled.emit(b)
    def isChecked(self): return self._checked
    def _draw(self, pos):
        from ..application import QApplication
        screen = self._get_screen()
        if not screen: return
        radius = 8
        center_x = pos.x + radius
        center_y = pos.y + self._rect.height // 2
        pygame.draw.circle(screen, (255, 255, 255), (center_x, center_y), radius)
        pygame.draw.circle(screen, (100, 100, 110), (center_x, center_y), radius, 1)
        if self._checked:
            pygame.draw.circle(screen, (100, 150, 240), (center_x, center_y), radius - 3)
        font = pygame.font.SysFont(None, 18)
        txt = font.render(self._text, True, (20, 20, 20))
        screen.blit(txt, (pos.x + radius*2 + 8, pos.y + (self._rect.height - txt.get_height())//2))
    def mousePressEvent(self, ev):
        self.setChecked(True)
