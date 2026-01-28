import pygame
from ..core import Signal
from .qwidget import QWidget

class QTextEdit(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._html = ""; self._plain_text = ""; self._lines = []; self._focused = False; self._read_only = False
        self._scroll_y = 0
        self.textChanged = Signal()
        
        # Cursor support
        self._cursor_pos = 0
        class QDoc:
            def __init__(self, text_getter): self._getter = text_getter
            def toPlainText(self): return self._getter()
        self._document = QDoc(self.toPlainText)

    def textCursor(self):
        from ..gui import QTextCursor
        cursor = QTextCursor()
        cursor._document = self._document
        cursor._pos = self._cursor_pos
        return cursor

    def setPlainText(self, t): self._plain_text = t; self._lines = t.split('\n'); self.textChanged.emit(); self._cursor_pos = len(t)
    def toPlainText(self): return self._plain_text
    def setText(self, t): self.setPlainText(t)
    def setHtml(self, h): 
        self._html = h
        from html.parser import HTMLParser
        
        class RichTextParser(HTMLParser):
            def __init__(self):
                super().__init__()
                self.lines = [[]]
                self.style_stack = [{'bold': False, 'italic': False, 'color': (0,0,0), 'size': 14}]
                
            def _parse_color(self, c):
                if not c: return (0,0,0)
                if c.startswith('#'):
                    try:
                        if len(c) == 7: return (int(c[1:3],16), int(c[3:5],16), int(c[5:7],16))
                        elif len(c) == 4: return (int(c[1]*2,16), int(c[2]*2,16), int(c[3]*2,16))
                    except: pass
                elif c.lower() == 'red': return (255, 0, 0)
                elif c.lower() == 'blue': return (0, 0, 255)
                elif c.lower() == 'green': return (0, 128, 0)
                return (0, 0, 0)

            def _ensure_new_line(self):
                if self.lines and self.lines[-1]: self.lines.append([])

            def handle_starttag(self, tag, attrs):
                attrs_dict = dict(attrs)
                new_style = self.style_stack[-1].copy()
                
                if tag in ('h1', 'h2', 'h3'):
                    new_style['bold'] = True
                    new_style['size'] = 18 if tag == 'h1' else 16
                    self._ensure_new_line()
                elif tag in ('b', 'strong'): new_style['bold'] = True
                elif tag in ('i', 'em'): new_style['italic'] = True
                elif tag == 'font':
                    if 'color' in attrs_dict: new_style['color'] = self._parse_color(attrs_dict['color'])
                elif tag == 'br': self.lines.append([])
                elif tag in ('p', 'div', 'tr', 'ul'): self._ensure_new_line()
                elif tag == 'li':
                    self._ensure_new_line()
                    self.lines[-1].append({'text': '  • ', 'bold': False, 'italic': False, 'color': (100,100,100), 'size': 14})
                
                self.style_stack.append(new_style)
                    
            def handle_endtag(self, tag):
                if len(self.style_stack) > 1: self.style_stack.pop()
                if tag in ('p', 'div', 'table', 'h1', 'h2', 'h3', 'ul', 'li'): self._ensure_new_line()

            def handle_data(self, data):
                if not data.strip() and not ' ' in data: return
                style = self.style_stack[-1]
                self.lines[-1].append({
                    'text': data,
                    'bold': style['bold'],
                    'italic': style['italic'],
                    'color': style['color'],
                    'size': style['size']
                })

        parser = RichTextParser()
        parser.feed(h)
        # Remove trailing empty lines
        while len(parser.lines) > 1 and not parser.lines[-1]: parser.lines.pop()
        self._doc_lines = parser.lines
        self._plain_text = "".join(["".join([s['text'] for s in l]) + "\n" for l in self._doc_lines])
        self._lines = self._plain_text.split('\n')

    def setReadOnly(self, b): self._read_only = b
    def _draw(self, pos):
        from ..application import QApplication
        if not QApplication._instance or not QApplication._instance._windows: return
        screen = self._get_screen()
        # Clear background for rich text
        pygame.draw.rect(screen, (255, 255, 255), (pos.x, pos.y, self._rect.width, self._rect.height))
        pygame.draw.rect(screen, (170, 170, 180), (pos.x, pos.y, self._rect.width, self._rect.height), 1)
        
        if not hasattr(self, '_doc_lines') or not self._doc_lines:
            self._doc_lines = [[{'text': line, 'bold': False, 'italic': False, 'color': (0,0,0), 'size': 14}] for line in self._lines]
            
        y = pos.y + 5 - self._scroll_y
        line_height = 18
        old_clip = screen.get_clip()
        screen.set_clip(pygame.Rect(pos.x, pos.y, self._rect.width, self._rect.height))
        
        for line_spans in self._doc_lines:
            if y + 25 > pos.y and y < pos.y + self._rect.height:
                curr_x = pos.x + 5
                max_h = line_height
                for span in line_spans:
                    f_size = span.get('size', 14)
                    font = pygame.font.SysFont("Arial", f_size, bold=span.get('bold', False), italic=span.get('italic',False))
                    txt = font.render(span['text'], True, span.get('color', (0,0,0)))
                    screen.blit(txt, (curr_x, y))
                    curr_x += txt.get_width()
                    max_h = max(max_h, txt.get_height())
                y += max_h
            else:
                y += line_height # Approximation for skipped lines
            
        screen.set_clip(old_clip)

    def wheelEvent(self, ev):
        delta = ev.angleDelta().y()
        line_height = 18
        content_h = len(getattr(self, '_doc_lines', [])) * line_height
        max_scroll = max(0, content_h - self._rect.height + 20)
        self._scroll_y = max(0, min(max_scroll, self._scroll_y - (delta / 120.0) * 40))
        ev.accept()
    def mousePressEvent(self, ev): self._focused = True
    def _handle_event(self, event, offset):
        if super()._handle_event(event, offset): return True
        if self._focused and not self._read_only and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                if self._plain_text:
                    self._plain_text = self._plain_text[:-1]
                    self._lines = self._plain_text.split('\n'); self.textChanged.emit()
                    self._doc_lines = [[{'text': line, 'bold': False, 'italic': False, 'color': (0,0,0), 'size': 14}] for line in self._lines]
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self._plain_text += '\n'; self._lines = self._plain_text.split('\n'); self.textChanged.emit()
                self._doc_lines = [[{'text': line, 'bold': False, 'italic': False, 'color': (0,0,0), 'size': 14}] for line in self._lines]
            elif event.key == pygame.K_v and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                # Paste from clipboard if possible
                try:
                    pasted = pygame.scrap.get(pygame.SCRAP_TEXT).decode('utf-8').replace('\0', '')
                    self._plain_text += pasted; self._lines = self._plain_text.split('\n'); self.textChanged.emit()
                    self._doc_lines = [[{'text': line, 'bold': False, 'italic': False, 'color': (0,0,0), 'size': 14}] for line in self._lines]
                except: pass
            elif event.unicode and event.unicode.isprintable():
                self._plain_text += event.unicode; self._lines = self._plain_text.split('\n'); self.textChanged.emit()
                self._doc_lines = [[{'text': line, 'bold': False, 'italic': False, 'color': (0,0,0), 'size': 14}] for line in self._lines]
        return False
