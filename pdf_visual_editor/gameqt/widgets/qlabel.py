import pygame
import os
from ..core import Qt
from ..application import QApplication
from .qwidget import QWidget

class QLabel(QWidget):
    def __init__(self, text="", parent=None): 
        super().__init__(parent); self._text = text
        self._alignment = Qt.AlignmentFlag.AlignCenter # Default? usually left but for about dialog it seems center
        self._margin = 0
        self._word_wrap = False
    def setText(self, text): 
        self._text = text
        self._calculate_natural_size()
    def text(self): return self._text
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
             # Try to find an image tag
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
             
             text = re.sub(r'<(br|/?p|/?div|/?h[1-6]|/?li)(\s+[^>]*)?>', '\n', text, flags=re.IGNORECASE)
             # Strip other tags but keep content
             text = re.sub(r'<[^>]+>', '', text)
        
        font = pygame.font.SysFont(None, 18)
        raw_lines = [l.strip() for l in text.split('\n') if l.strip()]
        
        self._display_lines = []
        if self._word_wrap and self._rect.width > 20:
            for line in raw_lines:
                words = line.split(' ')
                curr_line = ""
                for word in words:
                    test_line = curr_line + " " + word if curr_line else word
                    if font.size(test_line)[0] < self._rect.width - 20: # Margin cushion
                        curr_line = test_line
                    else:
                        self._display_lines.append(curr_line)
                        curr_line = word
                if curr_line: self._display_lines.append(curr_line)
        else:
            self._display_lines = raw_lines
            
        self._line_surfs = [font.render(l, True, (20, 20, 20)) for l in self._display_lines]
        
        spacing = 5
        self._total_h = sum(surf.get_height() + spacing for surf in self._line_surfs)
        if self._img_surf: self._total_h += self._img_surf.get_height() + 10
        
        if self._total_h > self._rect.height:
             self._rect.height = self._total_h
        
    def _draw(self, pos):
        if not hasattr(self, '_line_surfs'): self._calculate_natural_size()
        
        y = pos.y + self._margin
        if self._alignment == Qt.AlignmentFlag.AlignCenter:
             y = pos.y + (self._rect.height - self._total_h) // 2
        
        screen = self._get_screen()
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
