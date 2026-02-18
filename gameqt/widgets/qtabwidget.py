import pygame
from .qwidget import QWidget

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
        from ..application import QApplication
        if not QApplication._instance or not QApplication._instance._windows: return
        screen = self._get_screen()
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
