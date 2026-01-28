import pygame
from ..core import Signal, Qt
from ..application import QApplication
from .qwidget import QWidget

class QLineEdit(QWidget):
    def __init__(self, contents="", parent=None):
        super().__init__(parent)
        self._text = contents
        self._focused = False
        self._read_only = False
        self.returnPressed = Signal()
        self.textChanged = Signal(str)
        self._rect.height = 30 # Default height
    def setReadOnly(self, b): self._read_only = b
    def isReadOnly(self): return self._read_only
    def setText(self, text): self._text = text; self.textChanged.emit(text)
    def text(self): return self._text
    def setPlaceholderText(self, text): self._placeholder = text
    def _draw(self, pos):
        screen = self._get_screen()
        if not screen: return
        bg_color = (255, 255, 255)
        border_color = (100, 150, 240) if self._focused else (180, 180, 180)
        pygame.draw.rect(screen, bg_color, (pos.x, pos.y, self._rect.width, self._rect.height))
        pygame.draw.rect(screen, border_color, (pos.x, pos.y, self._rect.width, self._rect.height), 1)
        font = pygame.font.SysFont(None, 18)
        
        display_text = str(self._text) if self._text else ""
        text_color = (20, 20, 20)
        if not display_text and hasattr(self, '_placeholder') and not self._focused:
            display_text = str(self._placeholder) if hasattr(self, '_placeholder') else ""
            text_color = (150, 150, 150)
            
        txt = font.render(display_text, True, text_color)
        screen.blit(txt, (pos.x + 5, pos.y + (self._rect.height - txt.get_height())//2))
        
        if self._focused and (pygame.time.get_ticks() // 500) % 2 == 0:
            cursor_x = pos.x + 5 + font.size(self._text)[0]
            pygame.draw.line(screen, (0, 0, 0), (cursor_x, pos.y + 5), (cursor_x, pos.y + self._rect.height - 5), 1)
    def mousePressEvent(self, ev):
        self._focused = True
    def _handle_event(self, event, offset):
        super()._handle_event(event, offset)
        if event.type == pygame.MOUSEBUTTONDOWN:
            my_pos = offset + pygame.Vector2(self._rect.topleft)
            mouse_rect = pygame.Rect(my_pos.x, my_pos.y, self._rect.width, self._rect.height)
            if not mouse_rect.collidepoint(pygame.mouse.get_pos()):
                self._focused = False
        if self._focused and event.type == pygame.KEYDOWN and not self._read_only:
            if event.key == pygame.K_BACKSPACE:
                self._text = self._text[:-1]
                self.textChanged.emit(self._text)
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.returnPressed.emit()
            elif event.key == pygame.K_v and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                try:
                    pasted = pygame.scrap.get(pygame.SCRAP_TEXT).decode('utf-8').replace('\0', '')
                    self._text += pasted; self.textChanged.emit(self._text)
                except: pass
            elif event.unicode and event.unicode.isprintable():
                self._text += event.unicode
                self.textChanged.emit(self._text)
        elif self._focused and event.type == pygame.KEYDOWN and self._read_only:
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.returnPressed.emit()
