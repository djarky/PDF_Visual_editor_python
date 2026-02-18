import pygame
import os
from ..core import Qt, Signal
from ..application import QApplication
from .qwidget import QWidget

class QLabel(QWidget):
    def __init__(self, text="", parent=None): 
        super().__init__(parent); self._text = str(text) if text is not None else ""
        self._alignment = Qt.AlignmentFlag.AlignCenter # Default? usually left but for about dialog it seems center
        self._margin = 0
        self._word_wrap = False
    def setText(self, text): 
        self._text = str(text) if text is not None else ""
        self._calculate_natural_size()
    def update(self):
        super().update()
        self._calculate_natural_size()
    def text(self): return self._text
    def sizeHint(self):
        if not hasattr(self, '_total_h'): self._calculate_natural_size()
        from ..core import QSize
        mw = self._total_w if hasattr(self, '_total_w') else 0
        return QSize(mw + self._margin * 2, self._total_h)
    def setAlignment(self, align): self._alignment = align
    def setMargin(self, m): self._margin = m
    def setWordWrap(self, on): self._word_wrap = on
    def setTextFormat(self, fmt):
        self._text_format = fmt
        self._calculate_natural_size()
    def setOpenExternalLinks(self, open): self._open_external_links = open
    def _calculate_natural_size(self):
        text = self._text
        self._img_surf = None
        if getattr(self, '_text_format', 0) == Qt.TextFormat.RichText:
             import re
             # Try to find an image tag (separate from main text flow for now)
             img_match = re.search(r'<img src="file:///([^"]+)"', text)
             if img_match:
                 path = img_match.group(1)
                 if path.startswith("file:"): path = path[5:]
                 while path.startswith("//"): path = path[1:] # Strip leading slashes to find root
                 path = "/" + path if not path.startswith("/") else path
                 path = path.replace("/", os.sep)
                 if os.path.exists(path):
                     try:
                         self._img_surf = pygame.image.load(path)
                         if self._img_surf.get_width() > 200:
                             ratio = 200 / self._img_surf.get_width()
                             self._img_surf = pygame.transform.scale(self._img_surf, (200, int(self._img_surf.get_height() * ratio)))
                     except: pass
             
             # Check for <center> tag
             if "<center>" in text.lower() or "align=\"center\"" in text.lower():
                 self._alignment = Qt.AlignmentFlag.AlignCenter
             
             # Use RichTextParser from qtextedit for consistent parsing
             from .qtextedit import RichTextParser
             parser = RichTextParser()
             parser.feed(text)
             self._doc_lines = parser.lines
             text = "".join(["".join([s['text'] for s in l]) + "\n" for l in self._doc_lines])
        
        from ..utils.text_renderer import render_text, get_text_metrics
        f = self.font()
        w, h, asc, desc = get_text_metrics(text, f.family(), f.pointSize(), f.bold(), f.italic())
        raw_lines = [l.strip() for l in text.split('\n') if l.strip()]
        self._display_lines = raw_lines if raw_lines else [""]
        
        # Word wrap (simplified: just check width of each line)
        if self._word_wrap and self._rect.width > 20:
             # Full word wrapping would need a more complex loop, keeping it simple for now
             pass

        from ..gui import QColor
        text_color_str = self._get_style_property('color')
        
        # Default text color based on theme if NOT specified in QSS or local
        text_color = (30, 30, 30) # Default dark color for light theme
        if not text_color_str:
             app_style = QApplication._global_style
             # Simple heuristic: if QMainWindow has a dark bg, default to light text
             if app_style and 'QMainWindow' in app_style:
                 mw_bg = app_style['QMainWindow'].get('background-color', '')
                 if mw_bg.startswith('#'):
                     try:
                         c = QColor(mw_bg)
                         # If background is dark, use light text
                         if (c.red()*0.299 + c.green()*0.587 + c.blue()*0.114) < 128:
                             text_color = (220, 220, 225)
                     except: pass
        else:
            try: text_color = QColor(text_color_str).to_pygame()
            except: pass

        from ..utils.text_renderer import render_text
        f = self.font()
        self._line_surfs = [render_text(l, f.family(), f.pointSize(), text_color, f.bold(), f.italic()) for l in self._display_lines]
        
        spacing = 5
        self._total_h = sum(surf.get_height() + spacing for surf in self._line_surfs)
        self._total_w = max([s.get_width() for s in self._line_surfs]) if self._line_surfs else 0
        if self._img_surf: 
            self._total_h += self._img_surf.get_height() + 10
            self._total_w = max(self._total_w, self._img_surf.get_width())
        
        # We don't force self.resize here to stay layout-friendly, 
        # but we ensure sizeHint has the latest data.
        
    def _draw(self, pos):
        if not hasattr(self, '_line_surfs'): self._calculate_natural_size()
        
        y = pos.y + self._margin
        if self._alignment == Qt.AlignmentFlag.AlignCenter:
             y = pos.y + (self._rect.height - self._total_h) // 2
        
        screen = self._get_screen()
        if not screen: return
        
        if self._img_surf:
            ix = pos.x + (self._rect.width - self._img_surf.get_width()) // 2
            screen.blit(self._img_surf, (ix, y))
            y += self._img_surf.get_height() + 10
            
        for surf in self._line_surfs:
            x = pos.x + self._margin
            if self._alignment == Qt.AlignmentFlag.AlignCenter:
                x = pos.x + (self._rect.width - surf.get_width()) // 2
            screen.blit(surf, (x, y))
            y += surf.get_height() + 5
