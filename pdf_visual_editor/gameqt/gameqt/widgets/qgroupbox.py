import pygame
from ..application import QApplication
from .qwidget import QWidget

class QGroupBox(QWidget):
    def __init__(self, title="", parent=None):
        super().__init__(parent); self._title = title
    def setTitle(self, t): self._title = t
    def _draw(self, pos):
        screen = QApplication.instance()._windows[0]._screen
        pygame.draw.rect(screen, (150, 150, 160), (pos.x, pos.y + 10, self._rect.width, self._rect.height - 10), 1)
        font = pygame.font.SysFont(None, 16, bold=True)
        txt = font.render(self._title, True, (50, 50, 60))
        pygame.draw.rect(screen, (230, 230, 235), (pos.x + 10, pos.y, txt.get_width() + 4, 20))
        screen.blit(txt, (pos.x + 12, pos.y + 2))
