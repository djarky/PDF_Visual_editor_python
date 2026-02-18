import pygame
from ..core import Signal, Qt
from ..application import QApplication
from .qwidget import QWidget

class QLineEdit(QWidget):
    def __init__(self, contents="", parent=None):
        if isinstance(contents, QWidget):
            parent = contents
            contents = ""
        super().__init__(parent)
        self._text = contents
        self._focused = False
        self._read_only = False
        self._cursor_index = len(contents)
        self._selection_start = -1
        self._selection_end = -1
        self.returnPressed = Signal()
        self.textChanged = Signal(str)
        self._rect.height = 30 # Default height
        self._placeholder = ""
    def setReadOnly(self, b): self._read_only = b
    def isReadOnly(self): return self._read_only
    def setText(self, text): self._text = text; self.textChanged.emit(text)
    def text(self): return self._text
    def setPlaceholderText(self, text): self._placeholder = text
    def _draw(self, pos):
        # 1. Base QSS drawing (Background/Border) handles :focus pseudo-state
        super()._draw(pos)
        
        screen = self._get_screen()
        if not screen: return
        
        from ..gui import QColor
        pseudo = "focus" if self._focused else None
        
        display_text = str(self._text) if self._text else ""
        text_color_str = self._get_style_property('color', pseudo)
        text_color = (20, 20, 20) # Default dark text
        
        if text_color_str:
            try: text_color = QColor(text_color_str).to_pygame()
            except: pass
        else:
            # Fallback based on BG
            bg = self._get_style_property('background-color', pseudo)
            if bg and bg.startswith('#'):
                 c = QColor(bg)
                 if (c.red()*0.299 + c.green()*0.587 + c.blue()*0.114) < 128:
                     text_color = (220, 220, 225)

        is_placeholder = False
        if not display_text and self._placeholder and not self._focused:
            display_text = str(self._placeholder)
            text_color = (150, 150, 150)
            is_placeholder = True
            
        font = pygame.font.SysFont(None, 18)
        
        # Draw selection
        if self._focused and self._selection_start != -1 and self._selection_end != -1:
            s1, s2 = min(self._selection_start, self._selection_end), max(self._selection_start, self._selection_end)
            if s1 != s2:
                x1 = pos.x + 5 + font.size(display_text[:s1])[0]
                x2 = pos.x + 5 + font.size(display_text[:s2])[0]
                pygame.draw.rect(screen, (180, 210, 255), (x1, pos.y + 4, x2 - x1, self._rect.height - 8))

        txt = font.render(display_text, True, text_color)
        screen.blit(txt, (pos.x + 5, pos.y + (self._rect.height - txt.get_height())//2))
        
        if self._focused and not is_placeholder and (pygame.time.get_ticks() // 500) % 2 == 0:
            cursor_x = pos.x + 5 + font.size(display_text[:self._cursor_index])[0]
            pygame.draw.line(screen, text_color, (cursor_x, pos.y + 5), (cursor_x, pos.y + self._rect.height - 5), 1)
    def mousePressEvent(self, ev):
        self._focused = True
        font = pygame.font.SysFont(None, 18)
        local_x = ev.pos().x() - 5
        # Find cursor index based on click
        best_idx = 0
        min_diff = abs(local_x)
        for i in range(len(self._text) + 1):
            w = font.size(self._text[:i])[0]
            diff = abs(local_x - w)
            if diff < min_diff:
                min_diff = diff
                best_idx = i
        self._cursor_index = best_idx
        if not (pygame.key.get_mods() & pygame.KMOD_SHIFT):
            self._selection_start = -1
            self._selection_end = -1
        else:
            if self._selection_start == -1:
                self._selection_start = self._cursor_index
            self._selection_end = self._cursor_index

    def mouseMoveEvent(self, ev):
        if pygame.mouse.get_pressed()[0] and self._focused:
            font = pygame.font.SysFont(None, 18)
            local_x = ev.pos().x() - 5
            best_idx = 0
            min_diff = 1000000
            for i in range(len(self._text) + 1):
                w = font.size(self._text[:i])[0]
                diff = abs(local_x - w)
                if diff < min_diff:
                    min_diff = diff
                    best_idx = i
            if self._selection_start == -1:
                self._selection_start = self._cursor_index
            self._cursor_index = best_idx
            self._selection_end = self._cursor_index
    def _handle_event(self, event, offset):
        super()._handle_event(event, offset)
        if event.type == pygame.MOUSEBUTTONDOWN:
            my_pos = offset + pygame.Vector2(self._rect.topleft)
            mouse_rect = pygame.Rect(my_pos.x, my_pos.y, self._rect.width, self._rect.height)
            if not mouse_rect.collidepoint(pygame.mouse.get_pos()):
                self._focused = False
        if self._focused and event.type == pygame.KEYDOWN and not self._read_only:
            mods = pygame.key.get_mods()
            is_ctrl = mods & (pygame.KMOD_CTRL | pygame.KMOD_META)
            
            if event.key == pygame.K_BACKSPACE:
                if self._selection_start != -1 and self._selection_end != -1:
                    s1, s2 = min(self._selection_start, self._selection_end), max(self._selection_start, self._selection_end)
                    self._text = self._text[:s1] + self._text[s2:]
                    self._cursor_index = s1
                    self._selection_start = self._selection_end = -1
                elif self._cursor_index > 0:
                    self._text = self._text[:self._cursor_index-1] + self._text[self._cursor_index:]
                    self._cursor_index -= 1
                self.textChanged.emit(self._text)
            elif event.key == pygame.K_DELETE:
                 if self._selection_start != -1 and self._selection_end != -1:
                    s1, s2 = min(self._selection_start, self._selection_end), max(self._selection_start, self._selection_end)
                    self._text = self._text[:s1] + self._text[s2:]
                    self._cursor_index = s1
                    self._selection_start = self._selection_end = -1
                 elif self._cursor_index < len(self._text):
                     self._text = self._text[:self._cursor_index] + self._text[self._cursor_index+1:]
                 self.textChanged.emit(self._text)
            elif event.key == pygame.K_LEFT:
                if self._cursor_index > 0: self._cursor_index -= 1
                if not (mods & pygame.KMOD_SHIFT): self._selection_start = self._selection_end = -1
            elif event.key == pygame.K_RIGHT:
                if self._cursor_index < len(self._text): self._cursor_index += 1
                if not (mods & pygame.KMOD_SHIFT): self._selection_start = self._selection_end = -1
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.returnPressed.emit()
            elif event.key == pygame.K_v and is_ctrl:
                try:
                    pasted = QApplication.clipboard().text()
                    if pasted:
                         self._text = self._text[:self._cursor_index] + pasted + self._text[self._cursor_index:]
                         self._cursor_index += len(pasted)
                         self.textChanged.emit(self._text)
                except: pass
            elif event.key == pygame.K_c and is_ctrl:
                if self._selection_start != -1 and self._selection_end != -1:
                    s1, s2 = min(self._selection_start, self._selection_end), max(self._selection_start, self._selection_end)
                    QApplication.clipboard().setText(self._text[s1:s2])
            elif event.key == pygame.K_a and is_ctrl:
                self._selection_start = 0
                self._selection_end = len(self._text)
                self._cursor_index = len(self._text)
            elif event.unicode and event.unicode.isprintable():
                # Replace selection if any
                if self._selection_start != -1 and self._selection_end != -1:
                    s1, s2 = min(self._selection_start, self._selection_end), max(self._selection_start, self._selection_end)
                    self._text = self._text[:s1] + event.unicode + self._text[s2:]
                    self._cursor_index = s1 + 1
                    self._selection_start = self._selection_end = -1
                else:
                    self._text = self._text[:self._cursor_index] + event.unicode + self._text[self._cursor_index:]
                    self._cursor_index += 1
                self.textChanged.emit(self._text)
        elif self._focused and event.type == pygame.KEYDOWN and self._read_only:
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.returnPressed.emit()
