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

    @staticmethod
    def clipboard(): return QApplication._clipboard
    @staticmethod
    def instance(): return QApplication._instance

    def setApplicationName(self, name):
        self._app_name = name
        if self._windows:
            pygame.display.set_caption(name)

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
