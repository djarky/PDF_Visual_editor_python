import pygame
from .qwidget import QWidget
from .qlabel import QLabel

class QStatusBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._rect.height = 25
        self._message_label = QLabel("", self)
        self._message_label._rect = pygame.Rect(5, 5, 200, 15)
        
    def showMessage(self, text, timeout=0):
        self._message_label.setText(text)
        # Timeout not implemented in this simple version
        
    def addPermanentWidget(self, widget):
        widget._set_parent(self)
        widget.show()
        self._layout_widgets()
        
    def addWidget(self, widget):
        widget._set_parent(self)
        widget.show()
        self._layout_widgets()

    def _layout_widgets(self):
        # Re-calculate positions
        # Message label on left
        self._message_label._rect = pygame.Rect(5, 5, 200, 15)
        
        # Other widgets to the right
        # This is a simplification; normally permanent widgets are on far right
        current_x = 220
        for child in self._children:
            if child == self._message_label: continue
            child._rect.x = current_x
            current_x += child._rect.width + 5
        
    def _draw(self, pos):
        from ..application import QApplication
        from ..gui import QColor
        screen = self._get_screen()
        if not screen: return
        
        bg_color_str = self._get_style_property('background-color')
        bg_color = (240, 240, 245)
        if bg_color_str:
            try: bg_color = QColor(bg_color_str).to_pygame()
            except: pass
            
        border_color = (180, 180, 190)
        border_str = self._get_style_property('border-top')
        if not border_str: border_str = self._get_style_property('border')
        if border_str:
             parts = border_str.split()
             for p in parts:
                 if p.startswith('#') or p in QColor.NAMED_COLORS:
                     try: border_color = QColor(p).to_pygame()
                     except: pass

        pygame.draw.rect(screen, bg_color, (pos.x, pos.y, self._rect.width, self._rect.height))
        pygame.draw.line(screen, border_color, (pos.x, pos.y), (pos.x + self._rect.width, pos.y))
