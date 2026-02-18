import pygame
from ..core import Qt, QSize
from ..widgets import QWidget

class QSplitter(QWidget):
    def __init__(self, orientation=Qt.Orientation.Horizontal, parent=None):
        super().__init__(parent)
        self._items = []
        self._orientation = orientation
        self._sizes = [] 
        self._handle_width = 5
        self._handle_rects = []
        self._dragging_index = -1
        self._hover_index = -1
        self._pressed_pos = None
        
        # Setup cursors
        self._h_cursor = pygame.SYSTEM_CURSOR_SIZEWE
        self._v_cursor = pygame.SYSTEM_CURSOR_SIZENS
        
    def addWidget(self, w): 
        self._items.append(w)
        if len(self._sizes) < len(self._items):
            self._sizes.append(100) # Default size/weight
        w._set_parent(self)
        w.show()
        self._update_geometries()
        
    def setSizes(self, sizes): 
        self._sizes = list(sizes)
        # Pad with current sizes or defaults if provided list is too short
        while len(self._sizes) < len(self._items):
             self._sizes.append(100) # Default or generic
        self._update_geometries()
        
    def sizes(self):
        return [item._rect.width if self._orientation == Qt.Orientation.Horizontal else item._rect.height for item in self._items]

    def setHandleWidth(self, width):
        self._handle_width = width
        self._update_geometries()

    def _update_geometries(self):
        visible_items = [i for i in self._items if i.isVisible()]
        if not visible_items: return
        
        n = len(visible_items)
        if n == 0: return
        
        total_handle_w = (n - 1) * self._handle_width
        
        rect = self._rect
        if self._orientation == Qt.Orientation.Horizontal:
            available_space = max(0, rect.width - total_handle_w)
            total_size_req = sum(self._sizes[:n]) 
            if total_size_req == 0: total_size_req = 1
            
            curr = 0
            self._handle_rects = []
            
            for i, item in enumerate(visible_items):
                # Calculate simple proportion of current stored sizes
                # If we are dragging, self._sizes should be updated to reflect pixels
                
                # Logic: Distribute available space based on self._sizes ratios
                ratio = self._sizes[self._items.index(item)] / total_size_req if i < len(self._sizes) else 1/n
                
                w = int(available_space * ratio)
                # Correction for last item to fill space
                if i == n - 1:
                    w = available_space - curr
                
                item._rect = pygame.Rect(curr, 0, w, rect.height)
                curr += w
                
                if i < n - 1:
                    # Create handle
                    h_rect = pygame.Rect(curr, 0, self._handle_width, rect.height)
                    self._handle_rects.append(h_rect)
                    curr += self._handle_width
                    
        else: # Vertical
            available_space = max(0, rect.height - total_handle_w)
            total_size_req = sum(self._sizes[:n])
            if total_size_req == 0: total_size_req = 1
            
            curr = 0
            self._handle_rects = []
            
            for i, item in enumerate(visible_items):
                ratio = self._sizes[self._items.index(item)] / total_size_req if i < len(self._sizes) else 1/n
                
                h = int(available_space * ratio)
                if i == n - 1:
                    h = available_space - curr
                    
                item._rect = pygame.Rect(0, curr, rect.width, h)
                curr += h
                
                if i < n - 1:
                    h_rect = pygame.Rect(0, curr, rect.width, self._handle_width)
                    self._handle_rects.append(h_rect)
                    curr += self._handle_width

    def _draw_recursive(self, offset=pygame.Vector2(0,0)):
        if not self.isVisible(): return
        
        self._update_geometries()
        
        super()._draw_recursive(offset)
        
        my_pos = offset + pygame.Vector2(self._rect.topleft)
        screen = self._get_screen()
        if not screen: return
        
        from ..gui import QColor
        # Draw handles with QSS support
        for i, h_rect in enumerate(self._handle_rects):
            # Check for hover or dragging to set pseudo-state
            is_active = (self._dragging_index == i or self._hover_index == i)
            pseudo = "hover" if is_active else None
            
            bg_str = self._get_style_property('background-color', pseudo=pseudo, sub_element='handle')
            handle_color = (200, 200, 205)
            if bg_str:
                try: handle_color = QColor(bg_str).to_pygame()
                except: pass
            
            r = pygame.Rect(my_pos.x + h_rect.x, my_pos.y + h_rect.y, h_rect.width, h_rect.height)
            pygame.draw.rect(screen, handle_color, r)

    def mousePressEvent(self, ev):
        if ev.button() == Qt.MouseButton.LeftButton:
            pos = ev.pos()
            for i, rect in enumerate(self._handle_rects):
                if rect.collidepoint(pos.x(), pos.y()):
                    self._dragging_index = i
                    # Use local pos for delta calculation
                    self._pressed_pos = ev.pos() 
                    ev.accept()
                    return
        super().mousePressEvent(ev) # Bubble up if not handled

    def mouseMoveEvent(self, ev):
        pos = ev.pos()
        
        # Update Cursor
        hover = False
        for rect in self._handle_rects:
            if rect.collidepoint(pos.x(), pos.y()):
                hover = True
                break
        
        if hover or self._dragging_index != -1:
            cursor = self._h_cursor if self._orientation == Qt.Orientation.Horizontal else self._v_cursor
            try: pygame.mouse.set_cursor(cursor)
            except: pass
        else:
             try: pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
             except: pass

        # Handle Drag
        if self._dragging_index != -1:
            delta = 0
            if self._orientation == Qt.Orientation.Horizontal:
                delta = ev.pos().x() - self._handle_rects[self._dragging_index].centerx
            else:
                delta = ev.pos().y() - self._handle_rects[self._dragging_index].centery
                
            if delta != 0:
                # Update sizes
                # We need to adjust weights of item i and i+1
                # To do this correctly, we convert current calc sizes to weights (if they aren't already matched 1:1)
                # But self._sizes IS the source of truth.
                
                # Get visible items indices mapping
                visible_items = [item for item in self._items if item.isVisible()]
                if self._dragging_index < len(visible_items) - 1:
                    idx1 = self._items.index(visible_items[self._dragging_index])
                    idx2 = self._items.index(visible_items[self._dragging_index+1])
                    
                    # Ensure sizes list is large enough (robustness)
                    required_len = max(idx1, idx2) + 1
                    while len(self._sizes) < required_len:
                        self._sizes.append(100)
                    
                    # Prevent going too small
                    # This implies _sizes contains approximate pixel values if we just add delta
                    # If _sizes were small weights (e.g. 1, 2), adding 'delta' pixels (e.g. 5) breaks proportion logic
                    # So we should Normalize _sizes to pixels first?
                    
                    # normalize _sizes to match current actual pixels
                    # But we only want to do this ONCE at start of drag?
                    # Doing it continuously is fine if we stick to pixel values.
                    
                    # Let's ensure _sizes are treated as pixels sum
                    # On drag, we modify them. 
                    
                    s1 = self._sizes[idx1]
                    s2 = self._sizes[idx2]
                    
                    # Sensitivity factor? 1:1 pixel mapping
                    new_s1 = max(10, s1 + delta)
                    # We don't necessarily subtract from s2 strictly if we want to push? 
                    # But in a fixed total container, s2 must shrink.
                    # Actually, we should look at available space.
                    
                    # Simple approach: subtract from neighbor
                    shift = new_s1 - s1
                    new_s2 = max(10, s2 - shift)
                    
                    # Re-adjust shift if s2 hit limit
                    real_shift = s2 - new_s2
                    final_s1 = s1 + real_shift
                    
                    self._sizes[idx1] = final_s1
                    self._sizes[idx2] = new_s2
                    
                    self._update_geometries()
                    ev.accept()
                    return

    def mouseReleaseEvent(self, ev):
        if self._dragging_index != -1:
            self._dragging_index = -1
            ev.accept()
            return
        super().mouseReleaseEvent(ev)
