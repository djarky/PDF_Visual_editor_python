import pygame
from .qwidget import QWidget
from ..core import QWheelEvent, QPoint

class QScrollArea(QWidget):
    class Shape: NoFrame = 0
    def __init__(self, parent=None):
        super().__init__(parent)
        self._scroll_widget = None
        self._scroll_y = 0
        self._dragging_scrollbar = False
        self._drag_start_y = 0
        self._drag_start_scroll_y = 0
        
    def setWidget(self, w): 
        self._scroll_widget = w
        w._set_parent(self)
        
    def setWidgetResizable(self, b): 
        self._widget_resizable = b
        
    def setFrameShape(self, shape): self._frame_shape = shape
    
    def _get_content_height(self):
        """Calculate the natural height of the scroll content based on layout items."""
        if not self._scroll_widget:
            return 0
        
        layout = getattr(self._scroll_widget, '_layout', None)
        if layout and hasattr(layout, 'items'):
            visible = [i for i in layout.items if getattr(i, 'isVisible', lambda: True)()]
            spacing = getattr(layout, '_spacing', 5)
            margins = getattr(layout, '_margins', (0, 0, 0, 0))
            
            total_h = margins[1] + margins[3]
            for item in visible:
                rect = getattr(item, '_rect', None)
                if rect and hasattr(rect, 'height') and rect.height > 0 and rect.height != 100:
                    total_h += rect.height
                else:
                    total_h += 45  # Default card height
                total_h += spacing
            
            return max(total_h, self._scroll_widget._rect.height)
        
        return self._scroll_widget._rect.height
    
    def _draw_recursive(self, offset=pygame.Vector2(0,0)):
        if not self.isVisible(): return
        my_pos = offset + pygame.Vector2(self._rect.topleft)
        self._draw(my_pos)
        
        if self._scroll_widget:
            # Resize child width to match
            self._scroll_widget._rect.width = self._rect.width - 12  # Leave space for scrollbar
            
            # Calculate and set content height
            content_h = self._get_content_height()
            self._scroll_widget._rect.height = max(content_h, self._rect.height)
            
            from ..application import QApplication
            screen = self._get_screen()
            if not screen: return
            
            old_clip = screen.get_clip()
            screen.set_clip(pygame.Rect(my_pos.x, my_pos.y, self._rect.width, self._rect.height))
            
            self._scroll_widget._draw_recursive(my_pos + pygame.Vector2(0, -self._scroll_y))
            
            screen.set_clip(old_clip)
            
            # Draw scrollbar if needed
            if content_h > self._rect.height:
                bar_ratio = self._rect.height / content_h
                bar_h = max(30, self._rect.height * bar_ratio)
                max_scroll = content_h - self._rect.height
                bar_y = my_pos.y + (self._scroll_y / max_scroll) * (self._rect.height - bar_h) if max_scroll > 0 else my_pos.y
                
                # Bar background
                pygame.draw.rect(screen, (220, 220, 220), (my_pos.x + self._rect.width - 10, my_pos.y, 8, self._rect.height), border_radius=4)
                # Bar thumb
                pygame.draw.rect(screen, (150, 150, 160), (my_pos.x + self._rect.width - 10, bar_y, 8, bar_h), border_radius=4)

    def _handle_event(self, event, offset):
        """Override to handle scrollbar dragging and wheel events."""
        if not self.isVisible(): return False
        my_pos = offset + pygame.Vector2(self._rect.topleft)
        
        # 1. Handle scrollbar dragging
        content_h = self._get_content_height()
        max_scroll = max(0, content_h - self._rect.height)
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            scrollbar_rect = pygame.Rect(my_pos.x + self._rect.width - 12, my_pos.y, 12, self._rect.height)
            
            if scrollbar_rect.collidepoint(mouse_pos):
                if max_scroll > 0:
                    bar_ratio = self._rect.height / content_h
                    bar_h = max(30, self._rect.height * bar_ratio)
                    
                    bar_y = my_pos.y + (self._scroll_y / max_scroll) * (self._rect.height - bar_h)
                    thumb_rect = pygame.Rect(my_pos.x + self._rect.width - 10, bar_y, 8, bar_h)
                    
                    if thumb_rect.collidepoint(mouse_pos):
                        # Start dragging
                        self._dragging_scrollbar = True
                        self._drag_start_y = mouse_pos[1]
                        self._drag_start_scroll_y = self._scroll_y
                    else:
                        # Jump to position
                        rel_y = mouse_pos[1] - my_pos.y - (bar_h / 2)
                        self._scroll_y = max(0, min(max_scroll, (rel_y / (self._rect.height - bar_h)) * max_scroll))
                        # Also start dragging from here
                        self._dragging_scrollbar = True
                        self._drag_start_y = mouse_pos[1]
                        self._drag_start_scroll_y = self._scroll_y
                return True

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self._dragging_scrollbar:
                self._dragging_scrollbar = False
                return True

        elif event.type == pygame.MOUSEMOTION:
            if self._dragging_scrollbar:
                mouse_pos = pygame.mouse.get_pos()
                dy = mouse_pos[1] - self._drag_start_y
                
                bar_ratio = self._rect.height / content_h
                bar_h = max(30, self._rect.height * bar_ratio)
                
                bar_move_range = self._rect.height - bar_h
                if bar_move_range > 0:
                    scroll_delta = (dy / bar_move_range) * max_scroll
                    self._scroll_y = max(0, min(max_scroll, self._drag_start_scroll_y + scroll_delta))
                return True

        # Check if mouse is over this widget for wheel events
        mouse_rect = pygame.Rect(my_pos.x, my_pos.y, self._rect.width, self._rect.height)
        if not mouse_rect.collidepoint(pygame.mouse.get_pos()):
            return False
        
        # Intercept wheel events for scrolling
        if event.type == pygame.MOUSEWHEEL:
            delta = event.y * 30  # Scroll speed
            self._scroll_y = max(0, min(max_scroll, self._scroll_y - delta))
            return True  # Consume the event
        
        # Legacy scroll buttons
        if event.type == pygame.MOUSEBUTTONDOWN and event.button in (4, 5):
            if event.button == 4:  # Scroll up
                self._scroll_y = max(0, self._scroll_y - 30)
            else:  # Scroll down
                self._scroll_y = min(max_scroll, self._scroll_y + 30)
            return True
        
        # For other events, delegate to children with scroll offset
        if self._scroll_widget:
            adjusted_offset = my_pos + pygame.Vector2(0, -self._scroll_y)
            if self._scroll_widget._handle_event(event, adjusted_offset):
                return True
        
        return False

    def wheelEvent(self, ev):
        if self._scroll_widget:
            content_h = self._get_content_height()
            max_scroll = max(0, content_h - self._rect.height)
            delta = ev.angleDelta().y()
            move = (delta / 120.0) * 40 
            self._scroll_y = max(0, min(max_scroll, self._scroll_y - move))
            ev.accept()
