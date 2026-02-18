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
        from ..gui import QColor
        text_color_str = self._get_style_property('color')
        text_color = (20, 20, 20)
        if text_color_str:
            try: text_color = QColor(text_color_str).to_pygame()
            except: pass
            
        f = self.font()
        from ..utils.text_renderer import render_text
        txt = render_text(self._text, f.family(), f.pointSize(), text_color, f.bold(), f.italic())
        screen.blit(txt, (pos.x + radius*2 + 8, pos.y + (self._rect.height - txt.get_height())//2))
    def mousePressEvent(self, ev):
        self.setChecked(True)
