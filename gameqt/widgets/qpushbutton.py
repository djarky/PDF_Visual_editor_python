import pygame
from ..application import QApplication
from .qwidget import QWidget

class QPushButton(QWidget):
    def __init__(self, text="", parent=None): super().__init__(parent); self._text = text
    def setText(self, text): self._text = text
    def text(self): return self._text
    def sizeHint(self):
        from ..core import QSize
        return QSize(100, 35)
    def _draw(self, pos):
        # 1. Resolve QSS background
        bg_color_str = self._get_style_property('background-color')
        
        # 2. Draw Background and Border from QSS/Defaults
        super()._draw(pos)
        
        screen = self._get_screen()
        if not screen: return
        
        # 3. Fallback if NO QSS background
        if not bg_color_str:
            rect = pygame.Rect(pos.x, pos.y, self._rect.width, self._rect.height)
            # Default button look: light gray gradient-like feel or solid light gray
            pygame.draw.rect(screen, (225, 225, 230), rect, border_radius=2)
            pygame.draw.rect(screen, (160, 160, 170), rect, 1, border_radius=2)
            
        from ..gui import QColor, QFont
        
        # Determine pseudo-state for text color
        abs_pos = self.mapToGlobal((0,0))
        is_hovered = pygame.Rect(abs_pos.x(), abs_pos.y(), self._rect.width, self._rect.height).collidepoint(pygame.mouse.get_pos())
        pseudo = "hover" if is_hovered else None
        
        # 2. Resolve Text Color
        text_color_str = self._get_style_property('color', pseudo)
        
        # Default text color based on theme if NOT specified in QSS or local
        text_color = (255, 255, 255) # Default white for buttons in blue/dark themes
        if not text_color_str:
             app_style = QApplication._global_style
             if app_style and 'QMainWindow' in app_style:
                 mw_bg = app_style['QMainWindow'].get('background-color', '')
                 if mw_bg.startswith('#'):
                     try:
                         c = QColor(mw_bg)
                         # If background is light, use dark text for buttons (complementing the fallback bg)
                         if (c.red()*0.299 + c.green()*0.587 + c.blue()*0.114) > 128:
                             text_color = (30, 30, 35)
                     except: pass
             else:
                 # Standalone/No theme logic: Dark text on our light gray fallback
                 text_color = (30, 30, 35)
        else:
            try: 
                text_color = QColor(text_color_str).to_pygame()
            except: pass
        
        # 3. Draw Text
        f = self.font()
        from ..utils.text_renderer import render_text
        txt = render_text(str(self._text), f.family(), f.pointSize(), text_color, f.bold(), f.italic())
        screen.blit(txt, (pos.x + (self._rect.width - txt.get_width())//2, pos.y + (self._rect.height - txt.get_height())//2))
