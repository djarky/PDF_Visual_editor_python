import pygame
from ..core import Signal, Qt
from ..application import QApplication
from .qwidget import QWidget

class QCheckBox(QWidget):
    def __init__(self, text="", parent=None):
        super().__init__(parent)
        self._text = text
        self._checked = False
        self.stateChanged = Signal(int)
        self._rect.height = 25
    def text(self): return self._text
    def setChecked(self, b): self._checked = b; self.stateChanged.emit(Qt.CheckState.Checked if b else Qt.CheckState.Unchecked)
    def isChecked(self): return self._checked
    def _draw(self, pos):
        screen = self._get_screen()
        if not screen: return
        box_size = 16
        box_y = pos.y + (self._rect.height - box_size)//2
        pygame.draw.rect(screen, (255, 255, 255), (pos.x, box_y, box_size, box_size))
        pygame.draw.rect(screen, (100, 100, 110), (pos.x, box_y, box_size, box_size), 1)
        if self._checked:
            pygame.draw.line(screen, (0, 150, 0), (pos.x+3, box_y+box_size//2), (pos.x+box_size//2, box_y+box_size-3), 2)
            pygame.draw.line(screen, (0, 150, 0), (pos.x+box_size//2, box_y+box_size-3), (pos.x+box_size-3, box_y+3), 2)
        font = pygame.font.SysFont(None, 18)
        txt = font.render(self._text, True, (20, 20, 20))
        screen.blit(txt, (pos.x + box_size + 8, pos.y + (self._rect.height - txt.get_height())//2))
    def mousePressEvent(self, ev):
        self.setChecked(not self._checked)
