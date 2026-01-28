import pygame
from ..core import Qt
from ..application import QApplication
from .qwidget import QWidget

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
        
    def setWindowFlags(self, flags): self._window_flags = flags
    def setMinimumSize(self, w, h): 
        self._rect.width = max(self._rect.width, w)
        self._rect.height = max(self._rect.height, h)
