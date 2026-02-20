import pygame
from .core import QMouseEvent, Qt, QPointF, QClipboard, QMimeData, QUrl

class QDragEnterEvent:
    def __init__(self, pos, mimeData): self._pos, self._mime = pos, mimeData; self._accepted = False
    def pos(self): return self._pos
    def mimeData(self): return self._mime
    def accept(self): self._accepted = True
    def ignore(self): self._accepted = False
    def isAccepted(self): return self._accepted

class QDropEvent:
    def __init__(self, pos, mimeData): self._pos, self._mime = pos, mimeData; self._accepted = False
    def pos(self): return self._pos
    def position(self): return self._pos # Compatibility
    def mimeData(self): return self._mime
    def accept(self): self._accepted = True
    def ignore(self): self._accepted = False
    def isAccepted(self): return self._accepted

class QApplication:
    _instance = None
    _clipboard = None
    _global_style = {}
    
    DEFAULT_SYSTEM_STYLE = """
    QWidget { 
        background-color: #f0f0f5; 
        color: #1e1e23; 
        font-family: 'Segoe UI', 'Roboto', 'Arial', sans-serif;
        font-size: 10pt;
    }
    QMainWindow { 
        background-color: #e6e6eb; 
    }
    QPushButton { 
        background-color: #e1e1e6; 
        border: 1px solid #a0a0aa; 
        border-radius: 2px; 
        color: #1e1e23;
    }
    QPushButton:hover { 
        background-color: #d2d2d7; 
        border-color: #787882;
    }
    QPushButton:pressed { 
        background-color: #c8c8cd; 
    }
    QLineEdit { 
        background-color: #ffffff; 
        border: 1px solid #b4b4be; 
        color: #1e1e23;
    }
    QLineEdit:focus { 
        border: 1px solid #0078d7; 
    }
    QLabel { 
        color: #1e1e23; 
        background-color: transparent;
    }
    QSplitter::handle { 
        background-color: #c8c8cd; 
    }
    QSplitter::handle:hover { 
        background-color: #a0a0aa; 
    }
    QMenuBar { 
        background-color: #f0f0f5; 
        border-bottom: 1px solid #d2d2d7;
    }
    QMenuBar::item:selected { 
        background-color: #d2d2d7; 
    }
    QMenu { 
        background-color: #ffffff; 
        border: 1px solid #b4b4be;
    }
    QMenu::item:selected { 
        background-color: #0078d7; 
        color: #ffffff;
    }
    """
    
    def __init__(self, args): 
        pygame.init()
        QApplication._instance = self
        QApplication._clipboard = QClipboard()
        self._windows = []
        self._shortcuts = []
        self._popups = [] 
        self._running = False
        self._stylesheet = ""
        
        # Initialize global style with default system style
        from .utils import QSSParser
        QApplication._global_style = QSSParser.parse(self.DEFAULT_SYSTEM_STYLE)
        
        try:
            if not pygame.scrap.get_init(): pygame.scrap.init()
        except Exception as e:
            from .error_handler import get_logger
            get_logger().info("application.QApplication", f"pygame.scrap not available: {e}")

    def setStyleSheet(self, ss):
        from .utils import QSSParser
        self._stylesheet = ss
        
        # If empty, revert to default system style
        actual_ss = ss if ss.strip() else self.DEFAULT_SYSTEM_STYLE
        QApplication._global_style = QSSParser.parse(actual_ss)
        
        # Invalidate ALL widget style caches globally
        for win in self._windows:
            self._invalidate_all_styles(win)
            win.update()
            
    def _invalidate_all_styles(self, widget):
        if hasattr(widget, '_style_cache'):
            widget._style_cache.clear()
        if hasattr(widget, '_children'):
            for child in widget._children:
                self._invalidate_all_styles(child)
        
    def styleSheet(self):
        return self._stylesheet

    @staticmethod
    def clipboard(): return QApplication._clipboard
    @staticmethod
    def instance(): return QApplication._instance

    def add_popup(self, popup):
        if popup not in self._popups:
            self._popups.append(popup)
            
    def remove_popup(self, popup):
        if popup in self._popups:
            self._popups.remove(popup)

    def setApplicationName(self, name):
        self._app_name = name
        if self._windows:
            pygame.display.set_caption(name)

    def startDrag(self, drag):
        # Local event loop for dragging
        clock = pygame.time.Clock()
        dragging = True
        result = 0
        from .core import Qt
        
        # Cursor?
        # pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND) 

        while dragging:
            events = pygame.event.get()
            mouse_pos = pygame.mouse.get_pos()
            
            for event in events:
                if event.type == pygame.QUIT:
                    dragging = False
                    self._running = False
                elif event.type == pygame.MOUSEBUTTONUP:
                     if event.button == 1: # Left button release
                        dragging = False
                        # Drop!
                        # Find widget under mouse
                        target = None
                        target_local_pos = None
                        
                        # Walk windows in reverse (topmost first)
                        for win in reversed(self._windows):
                             if win.isVisible() and win._rect.collidepoint(mouse_pos):
                                  # Found window, now find specific child?
                                  # For now just send to window or focused widget?
                                  # Let's try to recursively find the deepest child that accepts drops
                                  target, target_local_pos = self._find_drop_target(win, pygame.Vector2(mouse_pos), win._rect.topleft)
                                  if target: break
                        
                        if target:
                            mime = drag._mime_data
                            drop_event = QDropEvent(target_local_pos, mime)
                            target.dropEvent(drop_event)
                            if drop_event.isAccepted():
                                 result = 1 # Copy/Move action
                        else:
                            mime = drag._mime_data
                            if mime:
                                from .widgets import QMessageBox
                                if mime.hasText() or mime.hasImage():
                                    msg = "Elemento arrastrado fuera del lienzo.\n¿Deseas copiarlo al portapapeles del sistema?"
                                    ans = QMessageBox.question(
                                        None, 
                                        "Exportar Elemento", 
                                        msg,
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                                    )
                                    if ans == QMessageBox.StandardButton.Yes:
                                        if mime.hasImage():
                                            QApplication.clipboard().setImage(mime.imageData())
                                        elif mime.hasText():
                                            QApplication.clipboard().setText(mime.text())
                
                # Forward other events? (Paint)
            
            # Draw everything to keep UI alive
            for win in self._windows:
                 if win.isVisible(): win._draw_recursive(pygame.Vector2(0,0))
            
            # Popups in drag loop? Usually not needed but for consistency:
            for popup in self._popups:
                 if hasattr(popup, '_draw_popup_overlay'): popup._draw_popup_overlay()

            # Draw Drag Icon?
            # if drag.pixmap...
            
            pygame.display.flip()
            clock.tick(60)
            
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        return result

    def _find_drop_target(self, widget, global_pos, widget_offset):
        # widget_offset is the absolute position of this widget
        # Check children first
        my_local_pos = global_pos - pygame.Vector2(widget_offset)
        
        for child in reversed(widget._children):
            if child.isVisible():
                 # child rect is relative to widget. QGraphicsScene doesn't have _rect.
                 if not hasattr(child, '_rect'): continue
                 
                 child_abs_pos = pygame.Vector2(widget_offset) + pygame.Vector2(child._rect.topleft)
                 child_rect_abs = pygame.Rect(child_abs_pos.x, child_abs_pos.y, child._rect.width, child._rect.height)
                 if child_rect_abs.collidepoint(global_pos):
                      found, pos = self._find_drop_target(child, global_pos, child_abs_pos)
                      if found: return found, pos
        
        # If no child handles it, check self
        if widget.acceptDrops():
             return widget, QPointF(my_local_pos)
        
        return None, None

    def quit(self):
        self._running = False
    def exec(self):
        clock = pygame.time.Clock(); self._running = True
        while self._running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT: self._running = False
                elif event.type == pygame.KEYDOWN:
                    # Check shortcuts
                    for shortcut in self._shortcuts:
                        if hasattr(shortcut._sequence, 'matches') and shortcut._sequence.matches(event.key, event.mod):
                            shortcut.activated.emit()
                            # Should we break here? Usually yes if shortcut is triggered
                            break
                elif event.type == pygame.VIDEORESIZE:
                    for win in self._windows:
                        from .widgets import QMainWindow
                        if isinstance(win, QMainWindow): 
                            win.resize(event.w, event.h)
                            win._screen = pygame.display.get_surface()
                elif event.type == pygame.DROPFILE:
                    # Handle file drop
                    mime = QMimeData()
                    mime.setUrls([QUrl(event.file)])
                    drop_event = QDropEvent(pygame.mouse.get_pos(), mime)
                    for win in self._windows:
                        if win.isVisible() and win._handle_drop_event(drop_event, pygame.Vector2(0,0)):
                            break
                
                # 1. Handle popups first (highest priority)
                handled = False
                for popup in reversed(self._popups):
                    if hasattr(popup, '_handle_popup_event'):
                        if popup._handle_popup_event(event):
                            handled = True
                            break
                if handled: continue

                # 2. Handle normal windows
                for win in self._windows:
                    if win.isVisible(): win._handle_event(event, pygame.Vector2(0,0))
                
                # Check for hover/motion globally if needed, or let windows handle it


            if not self._windows: break
            has_visible = False
            for win in self._windows:
                if win.isVisible():
                    has_visible = True
                    win._draw_recursive(pygame.Vector2(0,0))
            
            # 3. Draw popups last (highest z-order)
            for popup in self._popups:
                if hasattr(popup, '_draw_popup_overlay'):
                    popup._draw_popup_overlay()

            if not has_visible: break
            pygame.display.flip(); clock.tick(60)
        pygame.quit(); return 0
