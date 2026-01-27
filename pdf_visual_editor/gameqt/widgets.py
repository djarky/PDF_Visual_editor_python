import pygame
import os
import sys
from .core import QObject, Signal, QMouseEvent, QWheelEvent, QPoint, Qt, PyGameModalDialog
from .application import QApplication

class QWidget(QObject):
    def __init__(self, parent=None):
        super().__init__(parent); self._rect, self._visible, self._layout, self._stylesheet = pygame.Rect(0, 0, 100, 100), False, None, ""
        self._parent, self._children = parent, []
        # QObject.__init__ (via super()) already handles parent enrollment if it's a QObject
        # But we double check and initialize signals here if needed
        self.clicked = Signal(); self._accept_drops = False
    def setAcceptDrops(self, b): self._accept_drops = b
    def acceptDrops(self): return self._accept_drops
    def dragEnterEvent(self, event): pass
    def dropEvent(self, event): pass
    def setWindowTitle(self, title):
        self._window_title = title
        from .widgets import QMainWindow
        if isinstance(self, QMainWindow): pygame.display.set_caption(title)
    def resize(self, w, h): self._rect.width, self._rect.height = w, h
    def setMinimumSize(self, w, h): pass
    def setCursor(self, cursor): pass
    def viewport(self): return self # Fallback
    def mapToGlobal(self, p):
        # Simplistic: just add widget absolute position
        # We need to find absolute position
        abs_x, abs_y = 0, 0
        curr = self
        while curr:
            abs_x += curr._rect.x
            abs_y += curr._rect.y
            curr = curr._parent
        return QPointF(abs_x + p.x(), abs_y + p.y())
    def setCentralWidget(self, widget):
        widget._set_parent(self); widget.show()
        widget._rect = pygame.Rect(0, 0, self._rect.width, self._rect.height)
    def setStyleSheet(self, ss):
        self._stylesheet = ss
        # Basic parsing
        self._styles = {}
        for rule in ss.split(';'):
            if ':' in rule:
                k, v = rule.split(':', 1)
                self._styles[k.strip().lower()] = v.strip().lower()
    def show(self):
        self._visible = True
        for child in self._children:
            from .menus import QMenu
            if hasattr(child, 'show') and not isinstance(child, QMenu): child.show()
    def hide(self):
        self._visible = False
        for child in self._children:
            if hasattr(child, 'hide'): child.hide()
    def setVisible(self, v): (self.show() if v else self.hide())
    def isVisible(self): return self._visible
    def close(self): self.hide()
    def setLayout(self, layout): self._layout = layout; layout._parent = self
    def _set_parent(self, parent):
        if self._parent and self in self._parent._children: self._parent._children.remove(self)
        if not parent and QApplication._instance and self not in QApplication._instance._windows: 
            QApplication._instance._windows.append(self)
        elif parent and QApplication._instance and self in QApplication._instance._windows:
            QApplication._instance._windows.remove(self)
        self._parent = parent
        if parent and hasattr(parent, '_children'):
            if self not in parent._children:
                parent._children.append(self)
    def _handle_event(self, event, offset):
        if not self.isVisible(): return False
        my_pos = offset + pygame.Vector2(self._rect.topleft)
        
        # Special handling for QMainWindow with menu bar
        if hasattr(self, '_menu_bar') and self._menu_bar:
            if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
                menu_bar_rect = pygame.Rect(my_pos.x, my_pos.y, self._menu_bar._rect.width, self._menu_bar._rect.height)
                if menu_bar_rect.collidepoint(pygame.mouse.get_pos()) or (hasattr(self._menu_bar, '_active_menu') and self._menu_bar._active_menu):
                    return self._menu_bar._handle_event(event, my_pos)

        # 1. Deliver to children first (highest z-order)
        for child in reversed(self._children): 
            if child._handle_event(event, my_pos):
                return True
        
        # 2. Handle events for THIS widget
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
            mouse_rect = pygame.Rect(my_pos.x, my_pos.y, self._rect.width, self._rect.height)
            if mouse_rect.collidepoint(pygame.mouse.get_pos()):
                local_pos = pygame.Vector2(pygame.mouse.get_pos()) - my_pos
                btn = getattr(event, 'button', Qt.MouseButton.NoButton)
                if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
                    if btn == 1: btn = Qt.MouseButton.LeftButton
                    elif btn == 2: btn = Qt.MouseButton.MidButton
                    elif btn == 3: btn = Qt.MouseButton.RightButton
                    # Do not filter out 4/5, let them be for now if needed, but QMouseEvent doesn't have flags for them
                
                btns = 0
                if event.type == pygame.MOUSEMOTION:
                    if event.buttons[0]: btns |= Qt.MouseButton.LeftButton
                    if event.buttons[1]: btns |= Qt.MouseButton.MidButton
                    if event.buttons[2]: btns |= Qt.MouseButton.RightButton
                else: btns = btn
                
                q_event = QMouseEvent(local_pos, btn, btns, pygame.key.get_mods())
                q_event.ignore() # Not accepted by default for bubbling
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if hasattr(self, 'mousePressEvent'): 
                        self.mousePressEvent(q_event)
                        q_event.accept()
                    self.clicked.emit()
                    q_event.accept() # Buttons should accept the event
                elif event.type == pygame.MOUSEBUTTONUP:
                    if hasattr(self, 'mouseReleaseEvent'): self.mouseReleaseEvent(q_event)
                elif event.type == pygame.MOUSEMOTION:
                    if hasattr(self, 'mouseMoveEvent'): self.mouseMoveEvent(q_event)
                
                return q_event.isAccepted()
        
        if event.type == pygame.MOUSEWHEEL:
            mouse_rect = pygame.Rect(my_pos.x, my_pos.y, self._rect.width, self._rect.height)
            if mouse_rect.collidepoint(pygame.mouse.get_pos()):
                local_pos = pygame.Vector2(pygame.mouse.get_pos()) - my_pos
                px = getattr(event, 'precise_x', float(event.x))
                py = getattr(event, 'precise_y', float(event.y))
                w_event = QWheelEvent(local_pos, QPoint(int(px * 120), int(py * 120)), pygame.key.get_mods())
                w_event.ignore() # Default to ignored for bubbling
                if hasattr(self, 'wheelEvent'): self.wheelEvent(w_event)
                return w_event.isAccepted()
        
        # Legacy scroll
        if event.type == pygame.MOUSEBUTTONDOWN and event.button in (4, 5):
             mouse_rect = pygame.Rect(my_pos.x, my_pos.y, self._rect.width, self._rect.height)
             if mouse_rect.collidepoint(pygame.mouse.get_pos()):
                # We reuse mousePressEvent for legacy scroll handling in QScrollArea
                # But we should actually trigger wheelEvent or accepted mousePress
                return False # Let it bubble or be handled by specific logic
        
        return False
    
    def _handle_drop_event(self, event, offset):
        """Handle drag and drop events (DROPFILE, etc)"""
        if not self.isVisible(): return False
        my_pos = offset + pygame.Vector2(self._rect.topleft)
        
        # 1. Deliver to children first (highest z-order)
        for child in reversed(self._children): 
            if child._handle_drop_event(event, my_pos):
                return True
        
        # 2. Check if THIS widget accepts drops and mouse is over it
        if self._accept_drops:
            mouse_rect = pygame.Rect(my_pos.x, my_pos.y, self._rect.width, self._rect.height)
            if mouse_rect.collidepoint(pygame.mouse.get_pos()):
                from .application import QDragEnterEvent, QDropEvent
                if isinstance(event, QDragEnterEvent):
                    if hasattr(self, 'dragEnterEvent'): self.dragEnterEvent(event)
                elif isinstance(event, QDropEvent):
                    if hasattr(self, 'dropEvent'): self.dropEvent(event)
                return event.isAccepted()
        return False

    def _draw_recursive(self, offset=pygame.Vector2(0,0)):
        if not self.isVisible(): return
        if self._layout and hasattr(self._layout, 'arrange'): 
            # Layout arranges items relative to this widget's origin (0,0)
            self._layout.arrange(pygame.Rect(0, 0, self._rect.width, self._rect.height))
        my_pos = offset + pygame.Vector2(self._rect.topleft)
        self._draw(my_pos)
        for child in self._children: child._draw_recursive(my_pos)
    def _draw(self, pos):
        if not QApplication._instance or not QApplication._instance._windows: return
        screen = QApplication._instance._windows[0]._screen
        if screen and self.__class__.__name__ != 'QMainWindow':
            color = (220, 220, 225)
            class_name = self.__class__.__name__
            if "Thumbnail" in class_name: color = (190, 190, 200)
            elif "Inspector" in class_name: color = (200, 200, 210)
            elif "Canvas" in class_name: color = (255, 255, 255)
            elif "Splitter" in class_name: color = (230, 230, 230)
            pygame.draw.rect(screen, color, (pos.x, pos.y, self._rect.width, self._rect.height))
            pygame.draw.rect(screen, (120, 120, 130), (pos.x, pos.y, self._rect.width, self._rect.height), 1)
            if self._rect.width > 50 and self._rect.height > 20:
                font = pygame.font.SysFont(None, 18)
                txt = font.render(class_name, True, (80, 80, 90))
                screen.blit(txt, (pos.x + 4, pos.y + 4))
        
        # Apply CSS-like styles if present
        if hasattr(self, '_styles'):
            if 'background-color' in self._styles:
                try: pygame.draw.rect(screen, QColor(self._styles['background-color']).to_pygame(), (pos.x, pos.y, self._rect.width, self._rect.height))
                except: pass
            if 'border' in self._styles:
                # Simplistic border
                pygame.draw.rect(screen, (100, 100, 100), (pos.x, pos.y, self._rect.width, self._rect.height), 1)
    def statusBar(self):
        class MockStatusBar:
            def addWidget(self, w): 
                if QApplication._instance and QApplication._instance._windows:
                    w._set_parent(QApplication._instance._windows[0]); w.show()
        return MockStatusBar()
    def setAcceptDrops(self, b): 
        self._accept_drops = b
    def addAction(self, action): 
        if not hasattr(self, '_actions'):
            self._actions = []
        self._actions.append(action)
    def setContextMenuPolicy(self, policy): 
        self._context_menu_policy = policy

class QMainWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent); self._screen = None; self._central_widget = None; self._menu_bar = None
        if QApplication._instance: QApplication._instance._windows.append(self)
    def show(self):
        super().show()
        if not self._screen:
            self._screen = pygame.display.set_mode((self._rect.width, self._rect.height), pygame.RESIZABLE)
            if hasattr(QApplication.instance(), '_app_name'):
                pygame.display.set_caption(QApplication.instance()._app_name)
    def setMenuBar(self, menu_bar):
        self._menu_bar = menu_bar
        menu_bar._set_parent(self); menu_bar.show()
    def setCentralWidget(self, widget):
        self._central_widget = widget
        widget._set_parent(self); widget.show()
    def _draw_recursive(self, offset=pygame.Vector2(0,0)):
        if not self.isVisible(): return
        menu_h = 35 if self._menu_bar and self._menu_bar.isVisible() else 0
        if self._menu_bar: self._menu_bar._rect = pygame.Rect(0, 0, self._rect.width, menu_h)
        if self._central_widget: self._central_widget._rect = pygame.Rect(0, menu_h, self._rect.width, self._rect.height - menu_h)
        
        my_pos = offset + pygame.Vector2(self._rect.topleft)
        self._draw(my_pos)
        
        # Draw central widget and other children first
        if self._central_widget: self._central_widget._draw_recursive(my_pos)
        for child in self._children:
            if child not in (self._central_widget, self._menu_bar): child._draw_recursive(my_pos)
        
        # Draw menu bar LAST so dropdowns appear on top
        if self._menu_bar: self._menu_bar._draw_recursive(my_pos)
    def show(self):
        super().show()
        if not self._screen: self._screen = pygame.display.set_mode((self._rect.width, self._rect.height), pygame.RESIZABLE)
    def _draw(self, pos): (self._screen.fill((230, 230, 235)) if self._screen else None)

class QDialog(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._window_title = "Dialog"
        self.setWindowFlags(Qt.WindowType.Dialog) # Mock
        
    def exec(self):
        # Modal loop implementation for QDialog
        screen = pygame.display.get_surface()
        if not screen: return 0
        
        # Ensure all children visibility is correct BEFORE calculating layout
        self.show()
        
        # Center dialog on screen
        sw, sh = screen.get_size()
        w, h = self._rect.width, self._rect.height
        
        # If generic minimal size, expand a bit
        if w < 100: w = 600
        if h < 100: h = 500
        
        self._rect.x = (sw - w) // 2
        self._rect.y = (sh - h) // 2
        self._rect.width, self._rect.height = w, h
        
        # Adjust layout if present. Area for children is inside margins
        content_rect = pygame.Rect(0, 30, w, h - 30)
        if self._layout: self._layout.arrange(content_rect)
        
        # Ensure screen is up to date before capturing background
        if QApplication._instance and QApplication._instance._windows:
            for win in QApplication._instance._windows:
                if win.isVisible() and win != self:
                    win._draw_recursive(pygame.Vector2(0,0))
            pygame.display.flip()

        # Capture background
        bg = screen.copy()
        
        clock = pygame.time.Clock()
        self._running = True
        self._result = 0
        
        while self._running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self._running = False
                else:
                    # Pass event to this widget (tree). Offset is 0 for top-level.
                    self._handle_event(event, pygame.Vector2(0,0))
            
            # Draw
            screen.blit(bg, (0, 0))
            
            # Dim background
            overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 100))
            screen.blit(overlay, (0, 0))
            
            # Draw Dialog Background and Border
            pygame.draw.rect(screen, (240, 240, 245), self._rect, border_radius=8)
            pygame.draw.rect(screen, (100, 100, 110), self._rect, 1, border_radius=8)
            
            # Title bar
            title_rect = pygame.Rect(self._rect.x, self._rect.y, self._rect.width, 30)
            pygame.draw.rect(screen, (220, 220, 230), title_rect, border_top_left_radius=8, border_top_right_radius=8)
            pygame.draw.line(screen, (180, 180, 190), title_rect.bottomleft, title_rect.bottomright)
            
            font = pygame.font.SysFont("Arial", 16, bold=True)
            txt = font.render(getattr(self, '_window_title', "Dialog"), True, (50, 50, 60))
            screen.blit(txt, (self._rect.x + 10, self._rect.y + 5))

            # Children are already positioned relative to (0, 30) by layout arrange call
            self._draw_recursive_children(pygame.Vector2(self._rect.topleft))
            
            pygame.display.flip()
            clock.tick(60)
            
        return self._result

    def _draw_recursive_children(self, offset):
        for child in self._children:
             child._draw_recursive(offset)

    def accept(self): 
        self._result = 1
        self._running = False
        self.close()
        
    def reject(self): 
        self._result = 0
        self._running = False
        self.close()
        
    def setWindowFlags(self, flags): pass
    def setMinimumSize(self, w, h): 
        self._rect.width = max(self._rect.width, w)
        self._rect.height = max(self._rect.height, h)


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
    def setOpenExternalLinks(self, open): pass
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
        
        screen = QApplication._instance._windows[0]._screen
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


class QPushButton(QWidget):
    def __init__(self, text="", parent=None): super().__init__(parent); self._text = text
    def setText(self, text): self._text = text
    def text(self): return self._text
    def _draw(self, pos):
        if not QApplication._instance or not QApplication._instance._windows: return
        screen = QApplication._instance._windows[0]._screen
        if screen:
            color = (100, 150, 240)
            if pygame.Rect(pos.x, pos.y, self._rect.width, self._rect.height).collidepoint(pygame.mouse.get_pos()): color = (120, 170, 255)
            pygame.draw.rect(screen, color, (pos.x, pos.y, self._rect.width, self._rect.height), border_radius=4)
            pygame.draw.rect(screen, (50, 80, 180), (pos.x, pos.y, self._rect.width, self._rect.height), 1, border_radius=4)
            font = pygame.font.SysFont(None, 18)
            txt = font.render(self._text, True, (255, 255, 255))
            screen.blit(txt, (pos.x + (self._rect.width - txt.get_width())//2, pos.y + (self._rect.height - txt.get_height())//2))

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
    def _draw(self, pos):
        screen = QApplication._instance._windows[0]._screen
        if not screen: return
        bg_color = (255, 255, 255)
        border_color = (100, 150, 240) if self._focused else (180, 180, 180)
        pygame.draw.rect(screen, bg_color, (pos.x, pos.y, self._rect.width, self._rect.height))
        pygame.draw.rect(screen, border_color, (pos.x, pos.y, self._rect.width, self._rect.height), 1)
        font = pygame.font.SysFont(None, 18)
        txt = font.render(self._text, True, (20, 20, 20))
        screen.blit(txt, (pos.x + 5, pos.y + (self._rect.height - txt.get_height())//2))
        if self._focused and (pygame.time.get_ticks() // 500) % 2 == 0:
            cursor_x = pos.x + 5 + txt.get_width()
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
            elif event.unicode and event.unicode.isprintable():
                self._text += event.unicode
                self.textChanged.emit(self._text)
        elif self._focused and event.type == pygame.KEYDOWN and self._read_only:
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.returnPressed.emit()

class QCheckBox(QWidget):
    def __init__(self, text="", parent=None):
        super().__init__(parent)
        self._text = text
        self._checked = False
        self.stateChanged = Signal(int)
        self._rect.height = 25
    def text(self): return self._text
    def setChecked(self, b): self._checked = b; self.stateChanged.emit(Qt.CheckState.Checked if b else Qt.CheckState.Unchecked)
    def isChecked(self): return self._checked
    def _draw(self, pos):
        screen = QApplication._instance._windows[0]._screen
        if not screen: return
        box_size = 16
        box_y = pos.y + (self._rect.height - box_size)//2
        pygame.draw.rect(screen, (255, 255, 255), (pos.x, box_y, box_size, box_size))
        pygame.draw.rect(screen, (100, 100, 110), (pos.x, box_y, box_size, box_size), 1)
        if self._checked:
            pygame.draw.line(screen, (0, 150, 0), (pos.x+3, box_y+box_size//2), (pos.x+box_size//2, box_y+box_size-3), 2)
            pygame.draw.line(screen, (0, 150, 0), (pos.x+box_size//2, box_y+box_size-3), (pos.x+box_size-3, box_y+3), 2)
        font = pygame.font.SysFont(None, 18)
        txt = font.render(self._text, True, (20, 20, 20))
        screen.blit(txt, (pos.x + box_size + 8, pos.y + (self._rect.height - txt.get_height())//2))
    def mousePressEvent(self, ev):
        self.setChecked(not self._checked)

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
        screen = QApplication._instance._windows[0]._screen
        if not screen: return
        radius = 8
        center_x = pos.x + radius
        center_y = pos.y + self._rect.height // 2
        pygame.draw.circle(screen, (255, 255, 255), (center_x, center_y), radius)
        pygame.draw.circle(screen, (100, 100, 110), (center_x, center_y), radius, 1)
        if self._checked:
            pygame.draw.circle(screen, (100, 150, 240), (center_x, center_y), radius - 3)
        font = pygame.font.SysFont(None, 18)
        txt = font.render(self._text, True, (20, 20, 20))
        screen.blit(txt, (pos.x + radius*2 + 8, pos.y + (self._rect.height - txt.get_height())//2))
    def mousePressEvent(self, ev):
        self.setChecked(True)

class QComboBox(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._items = []
        self._current_index = -1
        self.currentIndexChanged = Signal(int)
        self._popup_visible = False
        self._rect.height = 30
    def addItem(self, text, data=None):
        self._items.append({'text': text, 'data': data})
        if self._current_index == -1: self._current_index = 0
    def addItems(self, texts):
        for t in texts: self.addItem(t)
    def currentIndex(self): return self._current_index
    def currentText(self): return self._items[self._current_index]['text'] if 0 <= self._current_index < len(self._items) else ""
    def setCurrentIndex(self, index):
        if 0 <= index < len(self._items):
            self._current_index = index
            self.currentIndexChanged.emit(index)
    def _draw(self, pos):
        screen = QApplication._instance._windows[0]._screen
        if not screen: return
        pygame.draw.rect(screen, (255, 255, 255), (pos.x, pos.y, self._rect.width, self._rect.height))
        pygame.draw.rect(screen, (180, 180, 180), (pos.x, pos.y, self._rect.width, self._rect.height), 1)
        # Arrow
        arrow_x = pos.x + self._rect.width - 20
        arrow_y = pos.y + self._rect.height // 2
        pygame.draw.polygon(screen, (80, 80, 80), [(arrow_x, arrow_y - 2), (arrow_x + 10, arrow_y - 2), (arrow_x + 5, arrow_y + 4)])
        
        txt_str = self.currentText()
        font = pygame.font.SysFont(None, 18)
        txt = font.render(txt_str, True, (20, 20, 20))
        screen.blit(txt, (pos.x + 5, pos.y + (self._rect.height - txt.get_height())//2))
        
        if self._popup_visible:
            self._draw_popup(pos)

    def _draw_popup(self, pos):
        screen = QApplication._instance._windows[0]._screen
        item_h = 25
        popup_h = len(self._items) * item_h
        popup_rect = pygame.Rect(pos.x, pos.y + self._rect.height, self._rect.width, popup_h)
        pygame.draw.rect(screen, (245, 245, 250), popup_rect)
        pygame.draw.rect(screen, (150, 150, 150), popup_rect, 1)
        font = pygame.font.SysFont(None, 18)
        for i, item in enumerate(self._items):
            iy = popup_rect.y + i * item_h
            if pygame.Rect(popup_rect.x, iy, popup_rect.width, item_h).collidepoint(pygame.mouse.get_pos()):
                pygame.draw.rect(screen, (200, 220, 255), (popup_rect.x+1, iy+1, popup_rect.width-2, item_h-2))
            txt = font.render(item['text'], True, (20, 20, 20))
            screen.blit(txt, (popup_rect.x + 5, iy + (item_h - txt.get_height())//2))

    def mousePressEvent(self, ev):
        if self._popup_visible:
            # Check which item was clicked
            local_y = ev.pos().y() - self._rect.height
            if 0 <= local_y < len(self._items) * 25:
                index = int(local_y // 25)
                self.setCurrentIndex(index)
            self._popup_visible = False
        else:
            self._popup_visible = True

    def _handle_event(self, event, offset):
        if self._popup_visible and event.type == pygame.MOUSEBUTTONDOWN:
            my_pos = offset + pygame.Vector2(self._rect.topleft)
            popup_rect = pygame.Rect(my_pos.x, my_pos.y + self._rect.height, self._rect.width, len(self._items) * 25)
            if not popup_rect.collidepoint(pygame.mouse.get_pos()):
                # Allow toggle off if clicking the combo itself again
                combo_rect = pygame.Rect(my_pos.x, my_pos.y, self._rect.width, self._rect.height)
                if not combo_rect.collidepoint(pygame.mouse.get_pos()):
                    self._popup_visible = False
        super()._handle_event(event, offset)

class QSpinBox(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._value = 0
        self._min = 0
        self._max = 99
        self.valueChanged = Signal(int)
        self._rect.height = 30
    def setValue(self, v):
        v = max(self._min, min(self._max, v))
        if self._value != v:
            self._value = v
            self.valueChanged.emit(v)
    def value(self): return self._value
    def setRange(self, mi, ma): self._min, self._max = mi, ma
    def _draw(self, pos):
        screen = QApplication._instance._windows[0]._screen
        if not screen: return
        pygame.draw.rect(screen, (255, 255, 255), (pos.x, pos.y, self._rect.width - 20, self._rect.height))
        pygame.draw.rect(screen, (180, 180, 180), (pos.x, pos.y, self._rect.width - 20, self._rect.height), 1)
        font = pygame.font.SysFont(None, 18)
        txt = font.render(str(self._value), True, (20, 20, 20))
        screen.blit(txt, (pos.x + 5, pos.y + (self._rect.height - txt.get_height())//2))
        
        # Buttons
        btn_x = pos.x + self._rect.width - 20
        pygame.draw.rect(screen, (230, 230, 235), (btn_x, pos.y, 20, self._rect.height//2))
        pygame.draw.rect(screen, (180, 180, 180), (btn_x, pos.y, 20, self._rect.height//2), 1)
        pygame.draw.rect(screen, (230, 230, 235), (btn_x, pos.y + self._rect.height//2, 20, self._rect.height//2))
        pygame.draw.rect(screen, (180, 180, 180), (btn_x, pos.y + self._rect.height//2, 20, self._rect.height//2), 1)
        
        # Arrows
        pygame.draw.polygon(screen, (50, 50, 50), [(btn_x + 5, pos.y + 10), (btn_x + 15, pos.y + 10), (btn_x + 10, pos.y + 4)])
        pygame.draw.polygon(screen, (50, 50, 50), [(btn_x + 5, pos.y + self._rect.height - 10), (btn_x + 15, pos.y + self._rect.height - 10), (btn_x + 10, pos.y + self._rect.height - 4)])

    def mousePressEvent(self, ev):
        x, y = ev.pos().x(), ev.pos().y()
        if x >= self._rect.width - 20:
            if y < self._rect.height // 2:
                self.setValue(self._value + 1)
            else:
                self.setValue(self._value - 1)

class QSlider(QWidget):
    def __init__(self, orientation=Qt.Orientation.Horizontal, parent=None):
        super().__init__(parent); self.valueChanged = Signal(int); self._val, self._min, self._max = 50, 0, 100
    def setRange(self, mi, ma): self._min, self._max = mi, ma
    def setMinimum(self, v): self._min = v
    def setMaximum(self, v): self._max = v
    def setValue(self, v): self._val = v; self.valueChanged.emit(v)
    def value(self): return self._val
    def _draw(self, pos):
        if not QApplication._instance or not QApplication._instance._windows: return
        screen = QApplication._instance._windows[0]._screen
        if screen:
            cy = pos.y + self._rect.height // 2
            pygame.draw.line(screen, (150, 150, 150), (pos.x+10, cy), (pos.x+self._rect.width-10, cy), 2)
            r = (self._val - self._min) / (self._max - self._min) if self._max > self._min else 0.5
            pygame.draw.rect(screen, (100, 150, 240), (pos.x + 10 + int((self._rect.width-20)*r)-5, cy-10, 10, 20))
    def mousePressEvent(self, ev):
        if self._rect.width > 20: 
            r = max(0, min(1, (ev.pos().x() - 10) / (self._rect.width - 20)))
            self.setValue(int(self._min + r * (self._max - self._min)))

class QTabWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._tabs = [] # list of (widget, label)
        self._current_index = 0
        
    def show(self):
        # Override to prevent recursive show from showing all tabs
        self._visible = True
        # Show only current tab
        if self._tabs and 0 <= self._current_index < len(self._tabs):
             self._tabs[self._current_index]['widget'].show()
        
    def addTab(self, w, l): 
        self._tabs.append({'widget': w, 'label': l})
        w._set_parent(self)
        # Only show current tab
        if len(self._tabs) - 1 == self._current_index:
            w.show()
        else:
            w.hide()
            
    def _draw(self, pos):
        super()._draw(pos) # Draw background
        
        # Draw Tabs Header
        if not QApplication._instance or not QApplication._instance._windows: return
        screen = QApplication._instance._windows[0]._screen
        if not screen: return
        
        font = pygame.font.SysFont("Arial", 16)
        x_offset = pos.x + 10
        tab_height = 30
        
        for i, tab in enumerate(self._tabs):
            text = font.render(tab['label'], True, (0, 0, 0) if i == self._current_index else (80, 80, 80))
            w = text.get_width() + 20
            
            # Tab Rect
            tab_rect = pygame.Rect(x_offset, pos.y, w, tab_height)
            
            # Check click (hacky here, ideally in mousePressEvent)
            # Storing rects for hit testing is better
            tab['rect'] = tab_rect
            
            color = (240, 240, 245) if i == self._current_index else (200, 200, 210)
            pygame.draw.rect(screen, color, tab_rect, border_top_left_radius=5, border_top_right_radius=5)
            pygame.draw.rect(screen, (150, 150, 150), tab_rect, 1, border_top_left_radius=5, border_top_right_radius=5)
            
            screen.blit(text, (x_offset + 10, pos.y + 5))
            x_offset += w + 2
            
        # Draw line below tabs
        pygame.draw.line(screen, (150, 150, 150), (pos.x, pos.y + tab_height), (pos.x + self._rect.width, pos.y + tab_height))

    def mousePressEvent(self, ev):
        x, y = ev.pos().x(), ev.pos().y()
        tab_h = 30
        if y > tab_h: return
        
        font = pygame.font.SysFont("Arial", 14)
        curr_x = 10
        for i, tab in enumerate(self._tabs):
            text = font.render(tab['label'], True, (0,0,0))
            tw = text.get_width() + 20
            if curr_x <= x <= curr_x + tw:
                self.setCurrentIndex(i)
                return
            curr_x += tw + 2

    def setCurrentIndex(self, index):
        self._current_index = index
        for i, tab in enumerate(self._tabs):
            if i == index:
                tab['widget'].show()
                # Resize child to fit content area (below tabs)
                # The widget itself is positioned at (0, 31) relative to QTabWidget
                w, h = self._rect.width, self._rect.height - 31
                tab['widget']._rect = pygame.Rect(0, 31, w, h)
                
                # trigger layout if needed - arrange relative to the widget's own origin (0,0)
                if tab['widget']._layout: 
                    tab['widget']._layout.arrange(pygame.Rect(0, 0, w, h))
            else:
                tab['widget'].hide()

    def _draw_recursive(self, offset=pygame.Vector2(0,0)):
        # Ensure correct child sizing before draw
        if 0 <= self._current_index < len(self._tabs):
            w = self._tabs[self._current_index]['widget']
            w._rect = pygame.Rect(0, 31, self._rect.width, self._rect.height - 31)
            
        super()._draw_recursive(offset)

class QTextEdit(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._html = ""; self._plain_text = ""; self._lines = []; self._focused = False; self._read_only = False
        self._scroll_y = 0
        self.textChanged = Signal()
    def setPlainText(self, t): self._plain_text = t; self._lines = t.split('\n'); self.textChanged.emit()
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
        if not QApplication._instance or not QApplication._instance._windows: return
        screen = QApplication._instance._windows[0]._screen
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
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self._plain_text += '\n'; self._lines = self._plain_text.split('\n'); self.textChanged.emit()
            elif event.unicode and event.unicode.isprintable():
                self._plain_text += event.unicode; self._lines = self._plain_text.split('\n'); self.textChanged.emit()
        return False

class QScrollArea(QWidget):
    class Shape: NoFrame = 0
    def __init__(self, parent=None):
        super().__init__(parent)
        self._scroll_widget = None
        self._scroll_y = 0
        
    def setWidget(self, w): 
        self._scroll_widget = w
        w._set_parent(self)
        
    def setWidgetResizable(self, b): 
        self._widget_resizable = b
        
    def setFrameShape(self, shape): pass
    
    def _draw_recursive(self, offset=pygame.Vector2(0,0)):
        if not self.isVisible(): return
        my_pos = offset + pygame.Vector2(self._rect.topleft)
        self._draw(my_pos)
        
        if self._scroll_widget:
            # Resize child to match width
            if self._scroll_widget._rect.width != self._rect.width:
                self._scroll_widget._rect.width = self._rect.width
                if hasattr(self._scroll_widget, '_calculate_natural_size'):
                    self._scroll_widget._calculate_natural_size()
            
            # Height is managed by child itself or natural size
                 
            screen = QApplication._instance._windows[0]._screen
            old_clip = screen.get_clip()
            screen.set_clip(pygame.Rect(my_pos.x, my_pos.y, self._rect.width, self._rect.height))
            
            self._scroll_widget._draw_recursive(my_pos + pygame.Vector2(0, -self._scroll_y))
            
            screen.set_clip(old_clip)
            
            # Scrollbar
            if self._scroll_widget._rect.height > self._rect.height:
                bar_h = max(20, self._rect.height * (self._rect.height / self._scroll_widget._rect.height))
                bar_y = my_pos.y + (self._scroll_y / self._scroll_widget._rect.height) * self._rect.height
                pygame.draw.rect(screen, (180, 180, 180), (my_pos.x + self._rect.width - 8, bar_y, 6, bar_h), border_radius=3)

    def wheelEvent(self, ev):
        if self._scroll_widget:
            delta = ev.angleDelta().y()
            max_scroll = max(0, self._scroll_widget._rect.height - self._rect.height)
            move = (delta / 120.0) * 40 
            self._scroll_y = max(0, min(max_scroll, self._scroll_y - move))
            ev.accept()

    def mousePressEvent(self, ev):
        if ev.button() == 4: # Scroll Up
            self._scroll_y = max(0, self._scroll_y - 20)
            ev.accept()
        elif ev.button() == 5: # Scroll Down
            if self._scroll_widget:
                max_scroll = max(0, self._scroll_widget._rect.height - self._rect.height)
                self._scroll_y = min(max_scroll, self._scroll_y + 20)
                ev.accept()
        else:
            # Propagate click to child?
            # Simple hit test
            if self._scroll_widget:
                # We need to offset event pos 
                # ev.pos() is local to ScrollArea.
                # Child expects local to Child.
                # Child is at (0, -scroll_y).
                # So child_local = ev.pos() - (0, -scroll_y) = ev.pos() + (0, scroll_y)
                
                local_pos = ev.pos() + pygame.Vector2(0, self._scroll_y)
                # Create mapped event
                # This is getting complex for MVP.
                pass

class QFileDialog:
    @staticmethod
    def getOpenFileName(parent=None, caption="Open File", dir="", filter=""):
        dlg = FileDialog(caption, mode="open", directory=dir, filter=filter)
        return dlg.exec_()

    @staticmethod
    def getSaveFileName(parent=None, caption="Save File", dir="", filter=""):
        dlg = FileDialog(caption, mode="save", directory=dir, filter=filter)
        return dlg.exec_()

    @staticmethod
    def getExistingDirectory(parent=None, caption="Select Directory", dir=""):
        dlg = FileDialog(caption, mode="dir", directory=dir)
        res = dlg.exec_()
        return res[0] if res else ""

class FileDialog(PyGameModalDialog):
    def __init__(self, title, mode="open", directory="", filter=""):
        super().__init__(title, 600, 400)
        self.mode = mode
        self.current_dir = directory if directory else os.getcwd()
        self.filter = filter
        self.items = []
        self.selected_index = -1
        self.scroll_y = 0
        self.refresh_items()
        self.filename_input = ""
        
    def refresh_items(self):
        self.items = []
        try:
            # Add ".." for parent
            self.items.append({"name": "..", "is_dir": True})
            
            for f in sorted(os.listdir(self.current_dir)):
                if f.startswith("."): continue
                path = os.path.join(self.current_dir, f)
                is_dir = os.path.isdir(path)
                
                # Filter files based on extension if needed
                if not is_dir and self.filter and self.mode in ("open", "save"):
                    # Basic filter parsing logic (e.g. "*.pdf")
                    valid_exts = []
                    if "(" in self.filter:
                        # Extract from "Description (*.ext *.ext2)"
                        parts = self.filter.split("(")[1].split(")")[0].split()
                        valid_exts = [p.replace("*", "").lower() for p in parts]
                    
                    if valid_exts:
                        _, ext = os.path.splitext(f)
                        if ext.lower() not in valid_exts:
                            continue
                
                self.items.append({"name": f, "is_dir": is_dir})
                
            # Sort: Directories first, then files
            self.items.sort(key=lambda x: (not x["is_dir"], x["name"].lower()))
            
        except Exception as e:
            print(f"Error accessing directory: {e}")
            self.current_dir = os.getcwd() # Fallback

    def draw(self, screen):
        super().draw(screen)
        
        font = pygame.font.SysFont("Arial", 14)
        
        # Path Bar
        pygame.draw.rect(screen, (255, 255, 255), (self.rect.x + 10, self.rect.y + 40, self.rect.width - 20, 25))
        pygame.draw.rect(screen, (150, 150, 150), (self.rect.x + 10, self.rect.y + 40, self.rect.width - 20, 25), 1)
        path_txt = font.render(self.current_dir[-60:], True, (0, 0, 0)) # Truncate for display
        screen.blit(path_txt, (self.rect.x + 15, self.rect.y + 45))
        
        # File List Area
        list_rect = pygame.Rect(self.rect.x + 10, self.rect.y + 75, self.rect.width - 20, self.rect.height - 120)
        pygame.draw.rect(screen, (255, 255, 255), list_rect)
        pygame.draw.rect(screen, (150, 150, 150), list_rect, 1)
        
        # Draw items
        old_clip = screen.get_clip()
        screen.set_clip(list_rect)
        
        start_y = list_rect.y + 5 - self.scroll_y
        item_height = 20
        
        for i, item in enumerate(self.items):
            y = start_y + i * item_height
            if y > list_rect.bottom: break
            if y + item_height < list_rect.top: continue
            
            # Selection highlight
            if i == self.selected_index:
                pygame.draw.rect(screen, (0, 120, 215), (list_rect.x + 2, y, list_rect.width - 4, item_height))
                text_color = (255, 255, 255)
            else:
                text_color = (0, 0, 0)
                
            icon = "[D]" if item["is_dir"] else "[F]"
            t = font.render(f"{icon} {item['name']}", True, text_color)
            screen.blit(t, (list_rect.x + 5, y + 2))
            
        screen.set_clip(old_clip)
        
        # Footer
        footer_y = self.rect.bottom - 40
        if self.mode == "save":
            # Filename input box
            pygame.draw.rect(screen, (255, 255, 255), (self.rect.x + 80, footer_y, 200, 25))
            pygame.draw.rect(screen, (150, 150, 150), (self.rect.x + 80, footer_y, 200, 25), 1)
            fname_txt = font.render(self.filename_input, True, (0, 0, 0))
            screen.blit(fname_txt, (self.rect.x + 85, footer_y + 5))
            
            lbl = font.render("Filename:", True, (0,0,0))
            screen.blit(lbl, (self.rect.x + 10, footer_y + 5))

        # Buttons
        btn_width = 80
        ok_rect = pygame.Rect(self.rect.right - 180, footer_y, btn_width, 25)
        cancel_rect = pygame.Rect(self.rect.right - 90, footer_y, btn_width, 25)
        
        mouse_pos = pygame.mouse.get_pos()
        
        # OK Button
        color = (0, 100, 200) if ok_rect.collidepoint(mouse_pos) else (0, 120, 215)
        pygame.draw.rect(screen, color, ok_rect, border_radius=3)
        ok_txt = font.render("Open" if self.mode == "open" else "Save", True, (255, 255, 255))
        screen.blit(ok_txt, (ok_rect.centerx - ok_txt.get_width()//2, ok_rect.centery - ok_txt.get_height()//2))
        
        # Cancel Button
        color = (200, 200, 200) if cancel_rect.collidepoint(mouse_pos) else (220, 220, 220)
        pygame.draw.rect(screen, color, cancel_rect, border_radius=3)
        cancel_txt = font.render("Cancel", True, (0, 0, 0))
        screen.blit(cancel_txt, (cancel_rect.centerx - cancel_txt.get_width()//2, cancel_rect.centery - cancel_txt.get_height()//2))

    def handle_key(self, event):
        super().handle_key(event)
        if self.mode == "save":
            if event.key == pygame.K_BACKSPACE:
                self.filename_input = self.filename_input[:-1]
            elif event.unicode and event.unicode.isprintable():
                self.filename_input += event.unicode
        
        if event.key == pygame.K_UP:
            self.selected_index = max(0, self.selected_index - 1)
            self.ensure_visible(self.selected_index)
        elif event.key == pygame.K_DOWN:
            self.selected_index = min(len(self.items) - 1, self.selected_index + 1)
            self.ensure_visible(self.selected_index)
        elif event.key == pygame.K_RETURN:
            self.go_or_select()

    def ensure_visible(self, index):
        # Adjust scroll_y so index is visible
        list_height = self.rect.height - 120
        item_height = 20
        
        top_y = index * item_height
        bottom_y = top_y + item_height
        
        if top_y < self.scroll_y:
            self.scroll_y = top_y
        elif bottom_y > self.scroll_y + list_height:
            self.scroll_y = bottom_y - list_height

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # Left click
                x, y = event.pos
                
                # Check file list click
                list_rect = pygame.Rect(self.rect.x + 10, self.rect.y + 75, self.rect.width - 20, self.rect.height - 120)
                if list_rect.collidepoint(x, y):
                    idx = int((y - list_rect.y + self.scroll_y) // 20)
                    if 0 <= idx < len(self.items):
                        self.selected_index = idx
                        self.filename_input = self.items[idx]["name"] if not self.items[idx]["is_dir"] else self.filename_input
                        
                        # Double click detection (simplified - relying on swift consecutive clicks or just button)
                        # For now, just require clicking Open button or Enter key to confirm file
                        pass
                
                # Check Buttons
                footer_y = self.rect.bottom - 40
                ok_rect = pygame.Rect(self.rect.right - 180, footer_y, 80, 25)
                cancel_rect = pygame.Rect(self.rect.right - 90, footer_y, 80, 25)
                
                if ok_rect.collidepoint(x, y):
                    self.go_or_select()
                elif cancel_rect.collidepoint(x, y):
                    self.running = False
                    self.result = ("", "")
                    
            elif event.button == 4: # Scroll Up
                self.scroll_y = max(0, self.scroll_y - 20)
            elif event.button == 5: # Scroll Down
                max_scroll = max(0, len(self.items) * 20 - (self.rect.height - 120))
                self.scroll_y = min(max_scroll, self.scroll_y + 20)

    def go_or_select(self):
        if 0 <= self.selected_index < len(self.items):
            item = self.items[self.selected_index]
            if item["is_dir"]:
                # Enter directory
                path = os.path.abspath(os.path.join(self.current_dir, item["name"]))
                if os.path.exists(path):
                    self.current_dir = path
                    self.refresh_items()
                    self.selected_index = -1
                    self.scroll_y = 0
            else:
                # Select file
                path = os.path.abspath(os.path.join(self.current_dir, item["name"]))
                self.result = (path, self.filter)
                self.running = False
        elif self.mode == "save" and self.filename_input:
             # Save logic
             path = os.path.abspath(os.path.join(self.current_dir, self.filename_input))
             self.result = (path, self.filter)
             self.running = False

class QMessageBox:
    class StandardButton: Ok = 1; Yes = 2; No = 3; Cancel = 4
    class Icon: Warning = 1; Information = 2; Critical = 3; Question = 4
    @staticmethod
    def warning(parent, title, text, buttons=StandardButton.Ok, defaultButton=StandardButton.Ok):
        return MessageBox(title, text, buttons).exec_()
    @staticmethod
    def information(parent, title, text, buttons=StandardButton.Ok, defaultButton=StandardButton.Ok):
        return MessageBox(title, text, buttons).exec_()
    @staticmethod
    def critical(parent, title, text, buttons=StandardButton.Ok, defaultButton=StandardButton.Ok):
        return MessageBox(title, text, buttons).exec_()
    @staticmethod
    def question(parent, title, text, buttons=StandardButton.Yes|StandardButton.No, defaultButton=StandardButton.No):
        return MessageBox(title, text, buttons).exec_()

class MessageBox(PyGameModalDialog):
    def __init__(self, title, text, buttons):
        super().__init__(title, 350, 200)
        self.text = text
        self.buttons = buttons
        self.btn_rects = []
        
    def draw(self, screen):
        super().draw(screen)
        
        font = pygame.font.SysFont("Arial", 14)
        
        # Text wrapping
        words = self.text.split(' ')
        lines = []
        curr_line = ""
        for w in words:
            test_line = curr_line + " " + w if curr_line else w
            if font.size(test_line)[0] < self.rect.width - 40:
                curr_line = test_line
            else:
                lines.append(curr_line)
                curr_line = w
        lines.append(curr_line)
        
        y = self.rect.y + 50
        for line in lines:
            txt = font.render(line, True, (0, 0, 0))
            screen.blit(txt, (self.rect.x + 20, y))
            y += 20
            
        # Buttons
        self.btn_rects = []
        btn_y = self.rect.bottom - 40
        btn_w = 80
        
        flags = QMessageBox.StandardButton
        btns_to_show = []
        if self.buttons & flags.Ok: btns_to_show.append((flags.Ok, "OK"))
        if self.buttons & flags.Yes: btns_to_show.append((flags.Yes, "Yes"))
        if self.buttons & flags.No: btns_to_show.append((flags.No, "No"))
        if self.buttons & flags.Cancel: btns_to_show.append((flags.Cancel, "Cancel"))
        
        total_w = len(btns_to_show) * (btn_w + 10)
        start_x = self.rect.centerx - total_w // 2
        
        mouse_pos = pygame.mouse.get_pos()
        
        for i, (val, label) in enumerate(btns_to_show):
            r = pygame.Rect(start_x + i*(btn_w+10), btn_y, btn_w, 25)
            self.btn_rects.append((val, r))
            
            color = (0, 100, 200) if r.collidepoint(mouse_pos) else (0, 120, 215)
            pygame.draw.rect(screen, color, r, border_radius=3)
            
            txt = font.render(label, True, (255, 255, 255))
            screen.blit(txt, (r.centerx - txt.get_width()//2, r.centery - txt.get_height()//2))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            x, y = event.pos
            for val, r in self.btn_rects:
                if r.collidepoint(x, y):
                    self.result = val
                    self.running = False

class QColorDialog(PyGameModalDialog):
    def __init__(self, initial=None, title="Select Color"):
        super().__init__(title, 300, 250)
        from .gui import QColor
        if initial is None: initial = QColor(255, 255, 255)
        self.r = initial.r; self.g = initial.g; self.b = initial.b
    @staticmethod
    def getColor(initial=None, parent=None, title="Select Color"):
        from .gui import QColor
        if initial is None: initial = QColor(255, 255, 255)
        dlg = QColorDialog(initial, title)
        res = dlg.exec_()
        return QColor(dlg.r, dlg.g, dlg.b) if res else initial
    def draw(self, screen):
        super().draw(screen)
        y = self.rect.y + 50
        for i, (label, val) in enumerate([("R", self.r), ("G", self.g), ("B", self.b)]):
            font = pygame.font.SysFont(None, 20)
            txt = font.render(f"{label}: {val}", True, (0,0,0))
            screen.blit(txt, (self.rect.x + 20, y))
            # Drawer sliders or just rely on mouse interaction
            pygame.draw.rect(screen, (200, 200, 200), (self.rect.x + 80, y, 150, 20))
            pygame.draw.rect(screen, (100, 150, 240), (self.rect.x + 80 + int((val/255)*140), y, 10, 20))
            y += 40
        # Preview
        pygame.draw.rect(screen, (self.r, self.g, self.b), (self.rect.x + 80, y, 150, 40))
        pygame.draw.rect(screen, (0,0,0), (self.rect.x + 80, y, 150, 40), 1)
        # OK Button
        btn_ok = pygame.Rect(self.rect.centerx - 40, self.rect.bottom - 40, 80, 25)
        pygame.draw.rect(screen, (0, 120, 215), btn_ok, border_radius=3)
        txt = font.render("OK", True, (255,255,255))
        screen.blit(txt, (btn_ok.centerx - txt.get_width()//2, btn_ok.centery - txt.get_height()//2))
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN or (event.type == pygame.MOUSEMOTION and event.buttons[0]):
            x, y = event.pos
            # Check sliders
            start_y = self.rect.y + 45
            for i in range(3):
                slider_rect = pygame.Rect(self.rect.x + 80, start_y + i*40, 150, 25)
                if slider_rect.collidepoint(x, y):
                    val = int(max(0, min(255, (x - slider_rect.x) / 150 * 255)))
                    if i == 0: self.r = val
                    elif i == 1: self.g = val
                    else: self.b = val
            # Check OK button
            btn_ok = pygame.Rect(self.rect.centerx - 40, self.rect.bottom - 40, 80, 25)
            if event.type == pygame.MOUSEBUTTONDOWN and btn_ok.collidepoint(x, y):
                self.result = True
                self.running = False

class QFontDialog(PyGameModalDialog):
    def __init__(self, initial=None, title="Select Font"):
        super().__init__(title, 400, 350)
        self.fonts = pygame.font.get_fonts()[:20] # Limit for demo
        self.selected_font = self.fonts[0]
        self.size = 12
    @staticmethod
    def getFont(initial=None, parent=None, title="Select Font"):
        dlg = QFontDialog(initial, title)
        res = dlg.exec_()
        from .gui import QFont
        return QFont(dlg.selected_font, dlg.size), res
    def draw(self, screen):
        super().draw(screen)
        font = pygame.font.SysFont(None, 18)
        for i, f in enumerate(self.fonts):
            y = self.rect.y + 50 + i*15
            color = (0, 120, 215) if f == self.selected_font else (0,0,0)
            txt = font.render(f, True, color)
            screen.blit(txt, (self.rect.x + 20, y))
        # Size SpinBox replacement
        y_size = self.rect.bottom - 80
        txt = font.render(f"Size: {self.size}", True, (0,0,0))
        screen.blit(txt, (self.rect.x + 20, y_size))
        # Simple buttons
        btn_ok = pygame.Rect(self.rect.centerx - 40, self.rect.bottom - 40, 80, 25)
        pygame.draw.rect(screen, (0, 120, 215), btn_ok, border_radius=3)
        txt = font.render("OK", True, (255,255,255))
        screen.blit(txt, (btn_ok.centerx - txt.get_width()//2, btn_ok.centery - txt.get_height()//2))
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            # Select font
            for i, f in enumerate(self.fonts):
                if pygame.Rect(self.rect.x + 20, self.rect.y + 50 + i*15, 200, 15).collidepoint(x, y):
                    self.selected_font = f
            # Check OK button
            btn_ok = pygame.Rect(self.rect.centerx - 40, self.rect.bottom - 40, 80, 25)
            if btn_ok.collidepoint(x, y):
                self.result = True
                self.running = False

class QGroupBox(QWidget):
    def __init__(self, title="", parent=None):
        super().__init__(parent); self._title = title
    def setTitle(self, t): self._title = t
    def _draw(self, pos):
        screen = QApplication.instance()._windows[0]._screen
        pygame.draw.rect(screen, (150, 150, 160), (pos.x, pos.y + 10, self._rect.width, self._rect.height - 10), 1)
        font = pygame.font.SysFont(None, 16, bold=True)
        txt = font.render(self._title, True, (50, 50, 60))
        pygame.draw.rect(screen, (230, 230, 235), (pos.x + 10, pos.y, txt.get_width() + 4, 20))
        screen.blit(txt, (pos.x + 12, pos.y + 2))

class QToolBar(QWidget):
    def __init__(self, title="", parent=None):
        super().__init__(parent); self._actions = []
        self._rect.height = 40
    def addAction(self, action):
        self._actions.append(action)
        btn = QPushButton(action.text, self)
        btn.clicked.connect(action.triggered.emit)
        # Layout? For now manual
        btn._rect = pygame.Rect(len(self._children)*85 - 80, 5, 80, 30)
    def _draw(self, pos):
        screen = QApplication.instance()._windows[0]._screen
        pygame.draw.rect(screen, (210, 210, 215), (pos.x, pos.y, self._rect.width, self._rect.height))
        pygame.draw.line(screen, (160, 160, 170), (pos.x, pos.y + self._rect.height - 1), (pos.x + self._rect.width, pos.y + self._rect.height - 1))

class QStackedWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        from .layouts import QStackedLayout
        self._layout = QStackedLayout(self)
    def addWidget(self, w): self._layout.addWidget(w)
    def setCurrentIndex(self, index): self._layout.setCurrentIndex(index)
    def currentIndex(self): return self._layout._current_index
