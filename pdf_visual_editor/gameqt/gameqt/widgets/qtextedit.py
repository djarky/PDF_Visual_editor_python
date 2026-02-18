import pygame
from ..core import Signal
from .qwidget import QWidget

from html.parser import HTMLParser

_font_cache = {}

class RichTextParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.lines = [[]]
        self.style_stack = [{'bold': False, 'italic': False, 'color': (0,0,0), 'size': 14}]
        self.column_idx = 0
        self.in_table = False
        
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
        elif c.lower() == 'gray': return (128, 128, 128)
        return (0, 0, 0)

    def _ensure_new_line(self):
        if self.lines and self.lines[-1]: self.lines.append([])

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        new_style = self.style_stack[-1].copy()
        
        if tag in ('h1', 'h2', 'h3'):
            new_style['bold'] = True
            new_style['size'] = 20 if tag == 'h1' else (18 if tag == 'h2' else 16)
            self._ensure_new_line()
        elif tag in ('b', 'strong'): 
            new_style['bold'] = True
        elif tag in ('i', 'em'): 
            new_style['italic'] = True
        elif tag == 'font':
            if 'color' in attrs_dict: new_style['color'] = self._parse_color(attrs_dict['color'])
            if 'size' in attrs_dict: 
                 try: new_style['size'] = int(attrs_dict['size'].replace('pt', ''))
                 except: pass
        elif tag == 'br': 
            self.lines.append([])
        elif tag in ('p', 'div', 'ul', 'ol'): 
            self._ensure_new_line()
        elif tag == 'li':
            self._ensure_new_line()
            self.lines[-1].append({'text': '  • ', 'bold': False, 'italic': False, 'color': (100,100,100), 'size': 14})
        elif tag == 'table':
            self.in_table = True
            self._ensure_new_line()
        elif tag == 'tr':
            self._ensure_new_line()
            self.column_idx = 0
        elif tag == 'a':
            new_style['color'] = (0, 0, 255) # Blue for links
        
        # Table cells
        if tag in ('td', 'th'):
            if tag == 'th': new_style['bold'] = True
            if self.column_idx > 0:
                # Simple tab-like spacing for columns
                self.lines[-1].append({'text': '    |    ', 'bold': False, 'italic': False, 'color': (180,180,180), 'size': 14, 'tab': True})
            self.column_idx += 1
            
        self.style_stack.append(new_style)
            
    def handle_endtag(self, tag):
        if len(self.style_stack) > 1: self.style_stack.pop()
        if tag in ('p', 'div', 'table', 'h1', 'h2', 'h3', 'ul', 'li', 'tr'): 
            self._ensure_new_line()
        if tag == 'table':
            self.in_table = False

    def handle_data(self, data):
        import re
        if self.in_table:
            data = data.strip()
            if not data: return
        else:
            data = re.sub(r'\s+', ' ', data)
            if not data or data == ' ': 
                # Keep leading space if requested
                pass
        
        style = self.style_stack[-1]
        self.lines[-1].append({
            'text': data,
            'bold': style['bold'],
            'italic': style['italic'],
            'color': style['color'],
            'size': style['size']
        })
    
    def handle_entityref(self, name):
        entities = {'nbsp': ' ', 'lt': '<', 'gt': '>', 'amp': '&', 'quot': '"', 'apos': "'"}
        self.handle_data(entities.get(name, f"&{name};"))

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
        self._doc_lines = None

    def textCursor(self):
        from ..gui import QTextCursor
        cursor = QTextCursor()
        cursor._document = self._document
        cursor._pos = self._cursor_pos
        return cursor

    def setPlainText(self, t): 
        t = str(t) if t is not None else ""
        self._plain_text = t; self._lines = t.split('\n'); self.textChanged.emit(); self._cursor_pos = len(t)
        self._doc_lines = None # Force re-calculation in _draw
    def toPlainText(self): return self._plain_text
    def setText(self, t): self.setPlainText(t)
    def setHtml(self, h): 
        self._html = h
        parser = RichTextParser()
        parser.feed(h)
        # Remove trailing empty lines
        while len(parser.lines) > 1 and not parser.lines[-1]: parser.lines.pop()
        self._doc_lines = parser.lines
        self._plain_text = "".join(["".join([s['text'] for s in l]) + "\n" for l in self._doc_lines])
        self._lines = self._plain_text.split('\n')

    def setReadOnly(self, b): self._read_only = b
    def _layout_text(self):
        if not hasattr(self, '_doc_lines') or not self._doc_lines:
            self._doc_lines = [[{'text': line, 'bold': False, 'italic': False, 'color': (0,0,0), 'size': 14}] for line in self._lines]
        
        # Calculate content height for tests
        line_height = 20
        self._last_content_h = len(self._doc_lines) * line_height

    def _draw(self, pos):
        from ..application import QApplication
        from ..gui import QColor
        if not QApplication._instance or not QApplication._instance._windows: return
        screen = self._get_screen()
        
        bg_color_str = self._get_style_property('background-color')
        bg_color = (255, 255, 255)
        if bg_color_str:
            try: bg_color = QColor(bg_color_str).to_pygame()
            except: pass
            
        border_color = (170, 170, 180)
        border_str = self._get_style_property('border')
        if border_str:
            parts = border_str.split()
            for p in parts:
                if p.startswith('#') or p in QColor.NAMED_COLORS:
                    try: border_color = QColor(p).to_pygame()
                    except: pass

        # Clear background for rich text
        pygame.draw.rect(screen, bg_color, (pos.x, pos.y, self._rect.width, self._rect.height))
        pygame.draw.rect(screen, border_color, (pos.x, pos.y, self._rect.width, self._rect.height), 1)
        
        if not hasattr(self, '_doc_lines') or not self._doc_lines:
            self._doc_lines = [[{'text': line, 'bold': False, 'italic': False, 'color': (0,0,0), 'size': 14}] for line in self._lines]
            
        y = pos.y + 5 - self._scroll_y
        line_height = 20
        old_clip = screen.get_clip()
        screen.set_clip(pygame.Rect(pos.x, pos.y, self._rect.width, self._rect.height))
        
        for line_spans in self._doc_lines:
            if y + 30 > pos.y and y < pos.y + self._rect.height:
                curr_x = pos.x + 5
                max_h = line_height
                for span in line_spans:
                    if 'surf' not in span:
                        f_size = span.get('size', 14)
                        bold = span.get('bold', False)
                        italic = span.get('italic', False)
                        f_key = ("Arial", f_size, bold, italic)
                        if f_key not in _font_cache:
                            _font_cache[f_key] = pygame.font.SysFont("Arial", f_size, bold=bold, italic=italic)
                        font = _font_cache[f_key]
                        span['surf'] = font.render(span['text'], True, span.get('color', (0,0,0)))
                    
                    txt = span['surf']
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
            elif event.key == pygame.K_v and (event.mod & (pygame.KMOD_CTRL | pygame.KMOD_META)):
                # Paste from clipboard if possible
                try:
                    from ..application import QApplication
                    pasted = QApplication.clipboard().text()
                    if pasted:
                        self._plain_text += pasted; self._lines = self._plain_text.split('\n'); self.textChanged.emit()
                        self._doc_lines = None # Force re-calculation in _draw
                except: pass
            elif event.unicode and event.unicode.isprintable():
                self._plain_text += event.unicode; self._lines = self._plain_text.split('\n'); self.textChanged.emit()
                self._doc_lines = [[{'text': line, 'bold': False, 'italic': False, 'color': (0,0,0), 'size': 14}] for line in self._lines]
        return False
