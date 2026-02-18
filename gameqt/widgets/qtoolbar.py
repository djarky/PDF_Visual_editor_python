import pygame
from ..application import QApplication
from .qwidget import QWidget
from .qpushbutton import QPushButton

class QToolBar(QWidget):
    def __init__(self, title="", parent=None):
        super().__init__(parent); self._actions = []
        self._rect.height = 40
    def addAction(self, action):
        self._actions.append(action)
        btn = QPushButton(action.text, self)
        btn.clicked.connect(action.triggered.emit)
        # Layout? For now manual
        btn._rect = pygame.Rect(len(self._children)*85 - 80, 5, 80, 30)
    def _draw(self, pos):
        screen = QApplication.instance()._windows[0]._screen
        pygame.draw.rect(screen, (210, 210, 215), (pos.x, pos.y, self._rect.width, self._rect.height))
        pygame.draw.line(screen, (160, 160, 170), (pos.x, pos.y + self._rect.height - 1), (pos.x + self._rect.width, pos.y + self._rect.height - 1))
