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
    def __init__(self, args): 
        pygame.init()
        QApplication._instance = self
        QApplication._clipboard = QClipboard()
        self._windows = []
        self._shortcuts = []
        self._running = False
        try:
            if not pygame.scrap.get_init(): pygame.scrap.init()
        except: pass

    @staticmethod
    def clipboard(): return QApplication._clipboard
    @staticmethod
    def instance(): return QApplication._instance

    def setApplicationName(self, name):
        self._app_name = name
        if self._windows:
            pygame.display.set_caption(name)

    def startDrag(self, drag):
        # Local event loop for dragging
        clock = pygame.time.Clock()
        dragging = True
        result = 0
        from .core import Qt, QDropEvent
        
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
                
                # Forward other events? (Paint)
            
            # Draw everything to keep UI alive
            for win in self._windows:
                 if win.isVisible(): win._draw_recursive(pygame.Vector2(0,0))
            
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
                 # child rect is relative to widget
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
                
                for win in self._windows:
                    if win.isVisible(): win._handle_event(event, pygame.Vector2(0,0))
                
                # Check for hover/motion globally if needed, or let windows handle it


            if not self._windows: break
            has_visible = False
            for win in self._windows:
                if win.isVisible():
                    has_visible = True
                    win._draw_recursive(pygame.Vector2(0,0))
            if not has_visible and clock.get_time() > 5000: break
            pygame.display.flip(); clock.tick(60)
        pygame.quit(); return 0
