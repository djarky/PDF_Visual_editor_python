import pygame
from ..core import Signal
from .qwidget import QWidget

class QSpinBox(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._value = 0
        self._min = 0
        self._max = 99
        self.valueChanged = Signal(int)
        self._rect.height = 30
    def setValue(self, v):
        v = max(self._min, min(self._max, v))
        if self._value != v:
            self._value = v
            self.valueChanged.emit(v)
    def value(self): return self._value
    def setRange(self, mi, ma): self._min, self._max = mi, ma
    def _draw(self, pos):
        from ..application import QApplication
        screen = self._get_screen()
        if not screen: return
        pygame.draw.rect(screen, (255, 255, 255), (pos.x, pos.y, self._rect.width - 20, self._rect.height))
        pygame.draw.rect(screen, (180, 180, 180), (pos.x, pos.y, self._rect.width - 20, self._rect.height), 1)
        font = pygame.font.SysFont(None, 18)
        txt = font.render(str(self._value), True, (20, 20, 20))
        screen.blit(txt, (pos.x + 5, pos.y + (self._rect.height - txt.get_height())//2))
        
        # Buttons
        btn_x = pos.x + self._rect.width - 20
        pygame.draw.rect(screen, (230, 230, 235), (btn_x, pos.y, 20, self._rect.height//2))
        pygame.draw.rect(screen, (180, 180, 180), (btn_x, pos.y, 20, self._rect.height//2), 1)
        pygame.draw.rect(screen, (230, 230, 235), (btn_x, pos.y + self._rect.height//2, 20, self._rect.height//2))
        pygame.draw.rect(screen, (180, 180, 180), (btn_x, pos.y + self._rect.height//2, 20, self._rect.height//2), 1)
        
        # Arrows
        pygame.draw.polygon(screen, (50, 50, 50), [(btn_x + 5, pos.y + 10), (btn_x + 15, pos.y + 10), (btn_x + 10, pos.y + 4)])
        pygame.draw.polygon(screen, (50, 50, 50), [(btn_x + 5, pos.y + self._rect.height - 10), (btn_x + 15, pos.y + self._rect.height - 10), (btn_x + 10, pos.y + self._rect.height - 4)])

    def mousePressEvent(self, ev):
        x, y = ev.pos().x(), ev.pos().y()
        if x >= self._rect.width - 20:
            if y < self._rect.height // 2:
                self.setValue(self._value + 1)
            else:
                self.setValue(self._value - 1)
