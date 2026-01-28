import pygame
from ..application import QApplication
from .qwidget import QWidget

class QPushButton(QWidget):
    def __init__(self, text="", parent=None): super().__init__(parent); self._text = text
    def setText(self, text): self._text = text
    def text(self): return self._text
    def _draw(self, pos):
        if not QApplication._instance or not QApplication._instance._windows: return
        screen = self._get_screen()
        if screen:
            color = (100, 150, 240)
            if pygame.Rect(pos.x, pos.y, self._rect.width, self._rect.height).collidepoint(pygame.mouse.get_pos()): color = (120, 170, 255)
            pygame.draw.rect(screen, color, (pos.x, pos.y, self._rect.width, self._rect.height), border_radius=4)
            pygame.draw.rect(screen, (50, 80, 180), (pos.x, pos.y, self._rect.width, self._rect.height), 1, border_radius=4)
            font = pygame.font.SysFont(None, 18)
            txt = font.render(self._text, True, (255, 255, 255))
            screen.blit(txt, (pos.x + (self._rect.width - txt.get_width())//2, pos.y + (self._rect.height - txt.get_height())//2))
