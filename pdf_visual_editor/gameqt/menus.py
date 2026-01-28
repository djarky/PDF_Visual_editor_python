import pygame
from .core import QObject, Signal, Qt, QMouseEvent
from .widgets import QWidget
from .application import QApplication

class QMenuBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent); self._menus = []; self._active_menu = None; self._menu_rects = []
    def addMenu(self, title):
        m = QMenu(title, self); self._menus.append(m); return m
    def _draw(self, pos):
        screen = pygame.display.get_surface()
        if screen:
            pygame.draw.rect(screen, (240, 240, 240), (pos.x, pos.y, self._rect.width, self._rect.height))
            pygame.draw.line(screen, (180, 180, 180), (pos.x, pos.y + self._rect.height - 1), (pos.x + self._rect.width, pos.y + self._rect.height - 1))
            
            font = pygame.font.SysFont(None, 20)
            curr_x_local = 12
            self._menu_rects = []
            for m in self._menus:
                txt = font.render(m.text if m.text else "[?]", True, (30, 30, 35))
                tw, th = txt.get_size()
                item_rect_local = pygame.Rect(curr_x_local - 5, 0, tw + 20, self._rect.height)
                self._menu_rects.append((m, item_rect_local))
                
                if self._active_menu == m:
                     pygame.draw.rect(screen, (200, 210, 230), (pos.x + item_rect_local.x, pos.y, item_rect_local.width, item_rect_local.height))
                elif item_rect_local.move(pos.x, pos.y).collidepoint(pygame.mouse.get_pos()):
                     pygame.draw.rect(screen, (225, 230, 240), (pos.x + item_rect_local.x, pos.y, item_rect_local.width, item_rect_local.height))
                
                screen.blit(txt, (pos.x + curr_x_local, pos.y + (self._rect.height - th) // 2))
                curr_x_local += tw + 25
            
            # Draw active dropdown AFTER all menu titles
            if self._active_menu:
                for m, rect in self._menu_rects:
                    if m == self._active_menu:
                        dropdown_pos = pygame.Vector2(pos.x + rect.x, pos.y + self._rect.height)
                        m._draw_dropdown(dropdown_pos)
                        break
    def _handle_event(self, event, offset):
        # Custom handle_event for QMenuBar to allow clicking outside bounds (on dropdowns)
        if not self.isVisible(): return
        
        # Calculate my absolute position
        my_pos = offset + pygame.Vector2(self._rect.topleft)
        
        # Prepare QMouseEvent
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
            # For QMenuBar allow events anywhere if we have an active menu
            # Otherwise only inside rect
            mouse_rect = pygame.Rect(my_pos.x, my_pos.y, self._rect.width, self._rect.height)
            is_inside = mouse_rect.collidepoint(pygame.mouse.get_pos())
            
            if is_inside or self._active_menu:
                local_pos = pygame.Vector2(pygame.mouse.get_pos()) - my_pos
                q_event = QMouseEvent(local_pos, 
                                     getattr(event, 'button', Qt.MouseButton.NoButton), 
                                     pygame.key.get_mods())
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.mousePressEvent(q_event)
                # We don't handle release/move for now in MenuBar extensively
    def mousePressEvent(self, ev):
        # Check if clicking on an item in an active dropdown
        if self._active_menu:
            for m, rect in self._menu_rects:
                if m == self._active_menu:
                    # Dropdown is below the menu bar
                    dropdown_x = rect.x
                    dropdown_y = self._rect.height
                    dropdown_width = 200
                    dropdown_height = len(m._actions) * 28
                    
                    # Check if click is in dropdown area
                    click_x = ev.pos().x()
                    click_y = ev.pos().y()
                    
                    if (dropdown_x <= click_x <= dropdown_x + dropdown_width and
                        dropdown_y <= click_y <= dropdown_y + dropdown_height):
                        # Click inside dropdown
                        local_x = click_x - dropdown_x
                        local_y = click_y - dropdown_y
                        
                        result = m._handle_dropdown_click(pygame.Vector2(local_x, local_y))
                        if result:
                            self._active_menu = None
                        return
                    break
        
        # Check if clicking on a menu title
        for m, rect in self._menu_rects:
            if rect.collidepoint(ev.pos().x(), ev.pos().y()):
                # Toggle menu
                if self._active_menu == m:
                    self._active_menu = None
                else:
                    self._active_menu = m
                return
        
        # Click outside menus
        self._active_menu = None

class QMenu(QWidget):
    def __init__(self, title="", parent=None): super().__init__(parent); self.text = title; self._actions = []
    def addAction(self, arg):
        if isinstance(arg, QAction):
            self._actions.append(arg)
            return arg
        else:
            # Assume it's text
            a = QAction(str(arg), self)
            self._actions.append(a)
            return a
    def addMenu(self, arg):
        m = QMenu(arg, self) if isinstance(arg, str) else arg
        self._actions.append(m); return m
    def clear(self): self._actions = []
    def addSeparator(self): self._actions.append("SEP")
    def exec(self, pos=None):
        # Show menu at position and wait for selection
        # In a real implementation, this would show a Pygame popup menu
        print(f"[QMenu] Showing popup menu at {pos}")
        return None
    def _draw(self, pos):
        # Draw the menu at the given position
        # This would render menu items using Pygame
        pass
    def _draw_dropdown(self, pos):
        screen = pygame.display.get_surface()
        if not screen or not self._actions: return
        w, h = 200, len(self._actions) * 28
        pygame.draw.rect(screen, (255, 255, 255), (pos.x, pos.y, w, h))
        pygame.draw.rect(screen, (160, 160, 170), (pos.x, pos.y, w, h), 1)
        font = pygame.font.SysFont(None, 18)
        mouse_pos = pygame.mouse.get_pos()
        for i, a in enumerate(self._actions):
            rect = pygame.Rect(pos.x, pos.y + i*28, w, 28)
            if a == "SEP":
                 pygame.draw.line(screen, (220, 220, 225), (pos.x+10, pos.y+i*28+14), (pos.x+w-10, pos.y+i*28+14))
            else:
                is_menu = isinstance(a, QMenu)
                label = (a.text if not is_menu else a.text + "  >")
                if rect.collidepoint(mouse_pos):
                    pygame.draw.rect(screen, (0, 120, 215), rect)
                    txt = font.render(str(label) if label is not None else "", True, (255, 255, 255))
                else:
                    txt = font.render(str(label) if label is not None else "", True, (45, 45, 50))
                screen.blit(txt, (pos.x + 12, pos.y + i*28 + (28 - txt.get_height()) // 2))
    def _handle_dropdown_click(self, local_pos):
        # Check if click is within dropdown bounds
        menu_width = 200
        menu_height = len(self._actions) * 28
        
        if 0 <= local_pos.x <= menu_width and 0 <= local_pos.y <= menu_height:
            idx = int(local_pos.y // 28)
            if 0 <= idx < len(self._actions):
                a = self._actions[idx]
                if a == "SEP": 
                    return False
                if isinstance(a, QAction): 
                    # Only trigger if action is enabled and visible
                    if a.isEnabled() and a.isVisible():
                        # Close menu before emitting, in case it starts a modal dialog
                        curr = self
                        while curr:
                            if hasattr(curr, '_active_menu'): curr._active_menu = None # For QMenuBar
                            if hasattr(curr, '_parent'): curr = curr._parent
                            else: break
                        
                        a.triggered.emit() # This should call the connected slot
                        return True
                elif isinstance(a, QMenu):
                    # Submenu clicked - for now just return False to keep menu open
                    return False
        return False

class QAction(QObject):
    def __init__(self, text="", parent=None): 
        super().__init__(parent); self.triggered, self.toggled = Signal(), Signal(bool)
        self.text = text
        self._shortcut = None
        self._enabled = True
        self._visible = True
        self._checkable = False
        self._checked = False
    def setShortcut(self, s): 
        self._shortcut = s
    def setEnabled(self, e): 
        self._enabled = e
    def setVisible(self, v): 
        self._visible = v
    def setCheckable(self, b): 
        self._checkable = b
    def setChecked(self, b): 
        if self._checkable:
            self._checked = b
            self.toggled.emit(b)
    def isEnabled(self): 
        return self._enabled
    def isVisible(self): 
        return self._visible
    def isCheckable(self): 
        return self._checkable
    def isChecked(self): 
        return self._checked
