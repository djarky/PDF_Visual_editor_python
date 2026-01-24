import pygame
import os
import sys
from .core import QObject, Signal, QMouseEvent, Qt
from .application import QApplication

class PyGameModalDialog:
    def __init__(self, title="Dialog", width=400, height=300):
        self.title = title
        self.rect = pygame.Rect(0, 0, width, height)
        self.result = None
        self.running = False
        
    def exec_(self):
        screen = pygame.display.get_surface()
        if not screen: return
        
        # Capture background
        bg = screen.copy()
        
        # Center dialog
        sw, sh = screen.get_size()
        self.rect.center = (sw // 2, sh // 2)
        
        clock = pygame.time.Clock()
        self.running = True
        
        while self.running:
            # Event Loop
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                    self.result = None
                elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
                    # Handle mouse interaction with dialog elements
                    self.handle_event(event) # Custom handler
                elif event.type == pygame.KEYDOWN:
                    self.handle_key(event)
            
            # Draw
            screen.blit(bg, (0, 0))
            
            # Dim background
            overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 100))
            screen.blit(overlay, (0, 0))
            
            # Draw Dialog
            self.draw(screen)
            
            pygame.display.flip()
            clock.tick(60)
            
        return self.result

    def draw(self, screen):
        # Base window
        pygame.draw.rect(screen, (240, 240, 245), self.rect, border_radius=8)
        pygame.draw.rect(screen, (100, 100, 110), self.rect, 1, border_radius=8)
        
        # Title bar
        title_rect = pygame.Rect(self.rect.x, self.rect.y, self.rect.width, 30)
        pygame.draw.rect(screen, (220, 220, 230), title_rect, border_top_left_radius=8, border_top_right_radius=8)
        pygame.draw.line(screen, (180, 180, 190), title_rect.bottomleft, title_rect.bottomright)
        
        font = pygame.font.SysFont("Arial", 16, bold=True)
        txt = font.render(self.title, True, (50, 50, 60))
        screen.blit(txt, (self.rect.x + 10, self.rect.y + 5))

    def handle_event(self, event): pass
    def handle_key(self, event): 
        if event.key == pygame.K_ESCAPE: self.running = False

class QWidget(QObject):
    def __init__(self, parent=None):
        super().__init__(parent); self._rect, self._visible, self._layout, self._stylesheet = pygame.Rect(0, 0, 100, 100), False, None, ""
        self._parent, self._children = parent, []
        if parent and hasattr(parent, '_children'): parent._children.append(self)
        self.clicked = Signal()
    def setWindowTitle(self, title):
        from .widgets import QMainWindow
        if isinstance(self, QMainWindow): pygame.display.set_caption(title)
    def resize(self, w, h): self._rect.width, self._rect.height = w, h
    def setMinimumSize(self, w, h): pass
    def setCursor(self, cursor): pass
    def setCentralWidget(self, widget):
        widget._set_parent(self); widget.show()
        widget._rect = pygame.Rect(0, 0, self._rect.width, self._rect.height)
    def setStyleSheet(self, ss): self._stylesheet = ss
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
        if parent and hasattr(parent, '_children'): parent._children.append(self)
    def _handle_event(self, event, offset):
        if not self.isVisible(): return
        my_pos = offset + pygame.Vector2(self._rect.topleft)
        
        # Special handling for QMainWindow with menu bar
        if hasattr(self, '_menu_bar') and self._menu_bar:
            # Check if event is a mouse event in menu bar area
            if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
                menu_bar_rect = pygame.Rect(my_pos.x, my_pos.y, 
                                            self._menu_bar._rect.width, 
                                            self._menu_bar._rect.height)
                mouse_pos = pygame.mouse.get_pos()
                
                # If clicking in menu bar area OR menu bar has active menu, let it handle the event
                if menu_bar_rect.collidepoint(mouse_pos) or (hasattr(self._menu_bar, '_active_menu') and self._menu_bar._active_menu):
                    self._menu_bar._handle_event(event, my_pos)
                    return  # Menu bar handled it, don't propagate
        
        # Normal event propagation to children
        for child in reversed(self._children): 
            child._handle_event(event, my_pos)
        
        # Handle events for this widget
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
            mouse_rect = pygame.Rect(my_pos.x, my_pos.y, self._rect.width, self._rect.height)
            if mouse_rect.collidepoint(pygame.mouse.get_pos()):
                local_pos = pygame.Vector2(pygame.mouse.get_pos()) - my_pos
                q_event = QMouseEvent(local_pos, 
                                     getattr(event, 'button', Qt.MouseButton.NoButton), 
                                     pygame.key.get_mods())
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if hasattr(self, 'mousePressEvent'): self.mousePressEvent(q_event)
                    self.clicked.emit()
                elif event.type == pygame.MOUSEBUTTONUP:
                    if hasattr(self, 'mouseReleaseEvent'): self.mouseReleaseEvent(q_event)
                elif event.type == pygame.MOUSEMOTION:
                    if hasattr(self, 'mouseMoveEvent'): self.mouseMoveEvent(q_event)
    def _draw_recursive(self, offset=pygame.Vector2(0,0)):
        if not self.isVisible(): return
        if self._layout and hasattr(self._layout, 'arrange'): self._layout.arrange(self._rect)
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
        self.setWindowFlags(Qt.WindowType.Dialog) # Mock
        
    def exec(self):
        # Modal loop implementation for QDialog
        screen = pygame.display.get_surface()
        if not screen: return 0
        
        # Center dialog on screen
        sw, sh = screen.get_size()
        w, h = self._rect.width, self._rect.height
        
        # If generic minimal size, expand a bit
        if w < 100: w = 600
        if h < 100: h = 500
        
        self._rect.x = (sw - w) // 2
        self._rect.y = (sh - h) // 2
        self._rect.width, self._rect.height = w, h
        
        # Adjust layout if present
        if self._layout: self._layout.arrange(self._rect)
        
        # Capture background
        bg = screen.copy()
        
        clock = pygame.time.Clock()
        self._running = True
        self._result = 0
        
        # Ensure all children visibility is correct
        self.show()
        
        while self._running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self._running = False
                else:
                    # Pass event to this widget (tree)
                    # We need to offset mouse events because _handle_event implies global or relative?
                    # GameQt widgets expect global events usually or relative to parent?
                    # _handle_event takes 'offset'. 
                    # For a top-level dialog, offset is 0?
                    # The widget's own rect is absolute in this modal context.
                    self._handle_event(event, pygame.Vector2(0,0))
            
            # Draw
            screen.blit(bg, (0, 0))
            
            # Dim background
            overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 100))
            screen.blit(overlay, (0, 0))
            
            # Draw Dialog and children
            self._draw_recursive(pygame.Vector2(0,0))
            
            pygame.display.flip()
            clock.tick(60)
            
        return self._result

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
    def setText(self, text): self._text = text
    def text(self): return self._text
    def setAlignment(self, align): self._alignment = align
    def setMargin(self, m): self._margin = m
    def setWordWrap(self, on): pass
    def setTextFormat(self, fmt): pass
    def setOpenExternalLinks(self, open): pass
    def _draw(self, pos):
        font = pygame.font.SysFont(None, 22)
        txt = font.render(self._text, True, (20, 20, 20))
        
        # Calculate position based on alignment
        x = pos.x + self._margin
        y = pos.y + self._margin
        
        if self._alignment == Qt.AlignmentFlag.AlignCenter:
             x = pos.x + (self._rect.width - txt.get_width()) // 2
             y = pos.y + (self._rect.height - txt.get_height()) // 2
        
        if QApplication._instance and QApplication._instance._windows and QApplication._instance._windows[0]._screen:
            QApplication._instance._windows[0]._screen.blit(txt, (x, y))

class QPushButton(QWidget):
    def __init__(self, text="", parent=None): super().__init__(parent); self._text = text
    def setText(self, text): self._text = text
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

class QSlider(QWidget):
    valueChanged = Signal(int)
    def __init__(self, orientation=Qt.Orientation.Horizontal, parent=None):
        super().__init__(parent); self._val, self._min, self._max = 50, 0, 100
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
        x, y = ev.pos()
        # Check tab clicks
        for i, tab in enumerate(self._tabs):
            rect = tab.get('rect')
            if rect:
                # Convert event pos (local to widget, but rects I calculated above are global... wait)
                # My _draw calculation uses 'pos' which is offset + self._rect.topleft (Global)
                # ev.pos() is also Local (relative to widget).
                # Wait, QMouseEvent in widgets.py is passed as `local_pos`.
                # So if I use local coordinates in _draw, I need to be consistent.
                # In _draw, 'pos' is GLOBAL screen coordinates.
                # In mousePressEvent, 'ev.pos()' is LOCAL.
                
                # Let's adjust hit test.
                # Tab is at (10 + accumulated_width, 0) in local coords.
                
                # Re-calculate local rect logic or use stored rect converted to local?
                # Stored rect 'rect' is GLOBAL because it came from 'pos' in _draw.
                
                # Hack: Since I don't easily have 'offset' here, let's recalculate local geometry strictly.
                pass
        
        # Simple recalculation
        font = pygame.font.SysFont("Arial", 16)
        curr_x = 10
        tab_h = 30
        
        if y < tab_h:
            for i, tab in enumerate(self._tabs):
                text = font.render(tab['label'], True, (0,0,0))
                w = text.get_width() + 20
                if curr_x <= x <= curr_x + w:
                    self.setCurrentIndex(i)
                    return
                curr_x += w + 2

    def setCurrentIndex(self, index):
        self._current_index = index
        for i, tab in enumerate(self._tabs):
            if i == index:
                tab['widget'].show()
                # Resize child to fit content area
                tab['widget']._rect = pygame.Rect(0, 35, self._rect.width, self._rect.height - 35)
                # trigger layout if needed
                if tab['widget']._layout: tab['widget']._layout.arrange(tab['widget']._rect)
            else:
                tab['widget'].hide()

    def _draw_recursive(self, offset=pygame.Vector2(0,0)):
        # Ensure correct child sizing before draw
        if 0 <= self._current_index < len(self._tabs):
            w = self._tabs[self._current_index]['widget']
            w._rect = pygame.Rect(0, 35, self._rect.width, self._rect.height - 35)
            
        super()._draw_recursive(offset)

class QTextEdit(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._html = ""
        self._lines = []
        
    def setHtml(self, h): 
        self._html = h
        # Better parsing: Use regex to strip tags
        import re
        # Remove <style>...</style>
        text = re.sub(r'<style.*?>.*?</style>', '', h, flags=re.DOTALL)
        # Replace common block tags with newlines
        text = re.sub(r'</?(p|div|h[1-6]|br|tr|li).*?>', '\n', text)
        # Remove all other tags
        text = re.sub(r'<[^>]+>', '', text)
        # Fix multiple newlines
        text = re.sub(r'\n+', '\n', text).strip()
        
        self._lines = text.split('\n')
        
    def setReadOnly(self, b): pass
    def _draw(self, pos):
        super()._draw(pos)
        font = pygame.font.SysFont("Arial", 14)
        
        y = pos.y + 5
        line_height = 18
        
        if not QApplication._instance or not QApplication._instance._windows: return
        screen = QApplication._instance._windows[0]._screen
        
        # Simple clipping
        old_clip = screen.get_clip()
        screen.set_clip(pygame.Rect(pos.x, pos.y, self._rect.width, self._rect.height))
        
        for line in self._lines:
            if y > pos.y + self._rect.height: break
            if line.strip():
                # Word wrap simplistic
                words = line.split(' ')
                draw_line = ""
                for word in words:
                    test_line = draw_line + " " + word if draw_line else word
                    if font.size(test_line)[0] < self._rect.width - 10:
                        draw_line = test_line
                    else:
                        txt = font.render(draw_line, True, (0, 0, 0))
                        screen.blit(txt, (pos.x + 5, y))
                        y += line_height
                        draw_line = word
                if draw_line:
                    txt = font.render(draw_line, True, (0, 0, 0))
                    screen.blit(txt, (pos.x + 5, y))
                    y += line_height
            else:
                y += line_height
        
        screen.set_clip(old_clip)

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
        
        # Force widget size
        if self._scroll_widget:
            # We want the widget to be its natural height probably?
            # Or at least width matches
            self._scroll_widget._rect.width = self._rect.width
            if self._scroll_widget._rect.height < self._rect.height:
                self._scroll_widget._rect.height = self._rect.height # fill
                
        # Draw background
        if not QApplication._instance or not QApplication._instance._windows: return
        screen = QApplication._instance._windows[0]._screen
        pygame.draw.rect(screen, (255, 255, 255), (my_pos.x, my_pos.y, self._rect.width, self._rect.height))
        
        # Draw child with offset (clipping)
        if self._scroll_widget:
            old_clip = screen.get_clip()
            screen.set_clip(pygame.Rect(my_pos.x, my_pos.y, self._rect.width, self._rect.height))
            
            # Adjusted offset for scroll
            child_offset = my_pos + pygame.Vector2(0, -self._scroll_y)
            # We need to manually call _draw on child because passing offset to _draw_recursive does purely relative
            # Actually _draw_recursive calls _draw(my_pos) then child._draw_recursive(my_pos).
            # So if we change 'my_pos' passed to child, it moves.
            
            # This is tricky with the recursive design. 
            # We want to call child._draw_recursive(child_offset - child._rect.topleft)
            # because child adds its own topleft. 
            # Wait, child._draw_recursive(parent_pos) -> calculates own pos = parent_pos + own.topleft.
            # So we pass (my_pos - self._rect.topleft) ? No.
            # We passed 'my_pos' to children.
            
            # We want child to render at my_pos + (0, -scroll).
            # Child adds its own topleft (usually 0,0 for scroll contents?). 
            
            scroll_vec = pygame.Vector2(0, -self._scroll_y)
            self._scroll_widget._draw_recursive(my_pos + scroll_vec)
            
            screen.set_clip(old_clip)
            
            # Scrollbar
            if self._scroll_widget._rect.height > self._rect.height:
                bar_h = self._rect.height * (self._rect.height / self._scroll_widget._rect.height)
                bar_y = my_pos.y + (self._scroll_y / self._scroll_widget._rect.height) * self._rect.height
                pygame.draw.rect(screen, (180, 180, 180), (my_pos.x + self._rect.width - 10, bar_y, 8, bar_h), border_radius=4)

    def mousePressEvent(self, ev):
        if ev.button() == 4: # Scroll Up
            self._scroll_y = max(0, self._scroll_y - 20)
        elif ev.button() == 5: # Scroll Down
            if self._scroll_widget:
                max_scroll = max(0, self._scroll_widget._rect.height - self._rect.height)
                self._scroll_y = min(max_scroll, self._scroll_y + 20)
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
