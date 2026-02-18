import pygame
from ..core import Signal, Qt
from ..application import QApplication
from .qwidget import QWidget

class QPushButton(QWidget):
    def __init__(self, text="", parent=None): 
        super().__init__(parent)
        self._text = text
        self._pressed = False
        self.clicked = Signal()
        
    def setText(self, text): self._text = text; self.update()
    def text(self): return self._text
    
    def sizeHint(self):
        from ..core import QSize
        return QSize(100, 35)
        
    def mousePressEvent(self, ev):
        if ev.button() == Qt.MouseButton.LeftButton:
            self._pressed = True
            self.update()
    
    def mouseReleaseEvent(self, ev):
        if self._pressed:
            self._pressed = False
            self.update()
            # Emit clicked if release is inside bounds
            abs_pos = self.mapToGlobal((0,0))
            rect = pygame.Rect(abs_pos.x(), abs_pos.y(), self._rect.width, self._rect.height)
            if rect.collidepoint(pygame.mouse.get_pos()):
                self.clicked.emit()
    
    def _draw(self, pos):
        # 1. Base QSS drawing (Background/Border) handles pseudo-states automatically
        super()._draw(pos)
        
        screen = self._get_screen()
        if not screen: return
        
        # Determine current pseudo for text
        abs_pos = self.mapToGlobal((0,0))
        is_hovered = pygame.Rect(abs_pos.x(), abs_pos.y(), self._rect.width, self._rect.height).collidepoint(pygame.mouse.get_pos())
        pseudo = "pressed" if self._pressed else ("hover" if is_hovered else None)
        
        # 2. Resolve Text Color
        text_color_str = self._get_style_property('color', pseudo)
        
        from ..gui import QColor
        text_color = (255, 255, 255) # Default
        if text_color_str:
            try: text_color = QColor(text_color_str).to_pygame()
            except: pass
        else:
            # Fallback if NO QSS: dark text on light, white on dark
            bg = self._get_style_property('background-color', pseudo)
            if bg and bg.startswith('#'):
                 c = QColor(bg)
                 if (c.red()*0.299 + c.green()*0.587 + c.blue()*0.114) > 128:
                     text_color = (30, 30, 35)
            elif not bg:
                 # Default fallback look if no QSS at all
                 text_color = (30, 30, 35)
                 # If no QSS BG was drawn, draw a default button face
                 rect = pygame.Rect(pos.x, pos.y, self._rect.width, self._rect.height)
                 pygame.draw.rect(screen, (225, 225, 230), rect, border_radius=2)
                 pygame.draw.rect(screen, (160, 160, 170), rect, 1, border_radius=2)

        # 3. Draw Text
        f = self.font()
        from ..utils.text_renderer import render_text
        txt = render_text(str(self._text), f.family(), f.pointSize(), text_color, f.bold(), f.italic())
        screen.blit(txt, (pos.x + (self._rect.width - txt.get_width())//2, pos.y + (self._rect.height - txt.get_height())//2))
