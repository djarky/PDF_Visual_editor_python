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
        if not screen: return
        
        # 1. Base QSS Drawing (background/border)
        super()._draw(pos)
        
        # QMenuBar often has a specific border-bottom in themes
        from .gui import QColor
        bb = self._get_style_property('border-bottom')
        if bb:
            border_color = (180, 180, 180)
            parts = bb.split()
            for p in parts:
                if p.startswith('#') or p in QColor.NAMED_COLORS:
                    try: border_color = QColor(p).to_pygame()
                    except: pass
            pygame.draw.line(screen, border_color, (pos.x, pos.y + self._rect.height - 1), (pos.x + self._rect.width, pos.y + self._rect.height - 1))
        
        text_color_str = self._get_style_property('color')
        text_color = (30, 30, 35)
        if text_color_str:
            try: text_color = QColor(text_color_str).to_pygame()
            except: pass
            
        font = pygame.font.SysFont(None, 20)
        curr_x_local = 12
        self._menu_rects = []
        for m in self._menus:
            is_active = (self._active_menu == m)
            item_rect_local = None # defined below
            
            # Temporary render to get size
            txt_surface = font.render(m.text if m.text else "[?]", True, text_color)
            tw, th = txt_surface.get_size()
            item_rect_local = pygame.Rect(curr_x_local - 5, 0, tw + 20, self._rect.height)
            self._menu_rects.append((m, item_rect_local))
            
            is_hovered = item_rect_local.move(pos.x, pos.y).collidepoint(pygame.mouse.get_pos())
            
            if is_active or is_hovered:
                # Use sub_element='item' for QMenuBar::item
                pseudo = 'selected' if is_active or is_hovered else None
                sel_bg_str = self._get_style_property('background-color', pseudo=pseudo, sub_element='item')
                
                sel_bg = (200, 210, 230)
                if sel_bg_str:
                    try: sel_bg = QColor(sel_bg_str).to_pygame()
                    except: pass
                pygame.draw.rect(screen, sel_bg, (pos.x + item_rect_local.x, pos.y, item_rect_local.width, item_rect_local.height))
            
            screen.blit(txt_surface, (pos.x + curr_x_local, pos.y + (self._rect.height - th) // 2))
            curr_x_local += tw + 25
            
            # Active dropdown is now drawn by QApp overlay

    def _draw_popup_overlay(self):
        if not self._active_menu: return
        pos = self.mapToGlobal(pygame.Vector2(0,0))
        for m, rect in self._menu_rects:
            if m == self._active_menu:
                dropdown_pos = pygame.Vector2(pos.x() + rect.x, pos.y() + self._rect.height)
                m._draw_dropdown(dropdown_pos)
                break

    def _handle_event(self, event, offset):
        # Normal handle_event only for the bar itself
        if not self.isVisible(): return False
        my_pos = offset + pygame.Vector2(self._rect.topleft)
        
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
            mouse_rect = pygame.Rect(my_pos.x, my_pos.y, self._rect.width, self._rect.height)
            if mouse_rect.collidepoint(pygame.mouse.get_pos()):
                local_pos = pygame.Vector2(pygame.mouse.get_pos()) - my_pos
                q_event = QMouseEvent(local_pos, getattr(event, 'button', Qt.MouseButton.NoButton), pygame.key.get_mods())
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.mousePressEvent(q_event)
                return True
        return False

    def _handle_popup_event(self, event):
        if not self._active_menu: return False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check if clicking on an item in an active dropdown (or submenus)
            pos = self.mapToGlobal(pygame.Vector2(0,0))
            for m, rect in self._menu_rects:
                if m == self._active_menu:
                    # Dropdown is below the menu bar
                    dropdown_x = pos.x() + rect.x
                    dropdown_y = pos.y() + self._rect.height
                    
                    # Delegate click to menu structure (recursive check)
                    # We convert global mouse pos to local pos relative to the dropdown start
                    mouse_pos = pygame.mouse.get_pos()
                    local_pos = pygame.Vector2(mouse_pos[0] - dropdown_x, mouse_pos[1] - dropdown_y)
                    
                    result = m._handle_dropdown_click(local_pos)
                    if result:
                        self._set_active_menu(None)
                        return True
                    
                    # If returned False, it might be a click on a submenu item that kept menu open
                    # OR a click outside entirely
                    
                    # Check if click was within the root menu rect to consume it?
                    # Actually _handle_dropdown_click returns True only if an action was triggered (close menu)
                    
                    # We need to know if we should close the menu (clicked outside)
                    if not m._rect_contains(local_pos):
                         break # Go check menu bar items
                    else:
                         return True # Clicked inside but no action (e.g. separator or just empty space)
                    break
            
            # Clicked outside. Check if it's another menu title in the bar
            pos = self.mapToGlobal(pygame.Vector2(0,0))
            mouse_pos = pygame.mouse.get_pos()
            for m, rect in self._menu_rects:
                if rect.move(pos.x(), pos.y()).collidepoint(mouse_pos):
                    if self._active_menu == m:
                        self._set_active_menu(None)
                    else:
                        self._set_active_menu(m)
                    return True
            
            # Clicked completely elsewhere
            self._set_active_menu(None)
            return True
            
        elif event.type == pygame.MOUSEMOTION:
             # Pass motion to active menu for submenu handling
             if self._active_menu:
                 pos = self.mapToGlobal(pygame.Vector2(0,0))
                 for m, rect in self._menu_rects:
                     if m == self._active_menu:
                         dropdown_x = pos.x() + rect.x
                         dropdown_y = pos.y() + self._rect.height
                         
                         mouse_pos = pygame.mouse.get_pos()
                         local_pos = pygame.Vector2(mouse_pos[0] - dropdown_x, mouse_pos[1] - dropdown_y)
                         
                         if m._handle_dropdown_motion(local_pos):
                             return True
                         
                         # Check if over menu bar to switch menus on hover (classic behavior)
                         # This allows sliding across "File Edit View"
                         for other_m, other_rect in self._menu_rects:
                             if other_m != m and other_rect.move(pos.x(), pos.y()).collidepoint(mouse_pos):
                                 self._set_active_menu(other_m)
                                 return True
                                 
        return False

    def _set_active_menu(self, m):
        if self._active_menu != m:
            if self._active_menu:
                self._active_menu._close_all_submenus()
            self._active_menu = m
            from .application import QApplication
            if m:
                QApplication.instance().add_popup(self)
            else:
                QApplication.instance().remove_popup(self)

    def mousePressEvent(self, ev):
        # This is reached if event was NOT handled by popup layer first (i.e. no menu active)
        # Check if clicking on a menu title
        for m, rect in self._menu_rects:
            if rect.collidepoint(ev.pos().x(), ev.pos().y()):
                self._set_active_menu(m)
                return
        
        # Click outside menus
        self._set_active_menu(None)

class QMenu(QWidget):
    def __init__(self, title="", parent=None): 
        super().__init__(parent); self.text = title; self._actions = []
        self._active_submenu = None
        self._submenu_rect = None # Rect of the item that opened the submenu
    
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
        if not pos: return None
        self._popup_pos = pos
        self._triggered_action = None
        self._closing = False
        
        # Intercept action signals
        original_slots = {}
        for a in self._actions:
            if isinstance(a, QAction):
                def make_interceptor(act):
                    return lambda: self._on_action_triggered(act)
                original_slots[a] = a.triggered.connect(make_interceptor(a))

        QApplication.instance().add_popup(self)
        
        # Local event loop for modal menu
        clock = pygame.time.Clock()
        while not self._closing and QApplication.instance()._running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    QApplication.instance().quit()
                    self._closing = True
                elif self._handle_popup_event(event):
                    pass
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Clicked outside
                    self._closing = True
            
            # Redraw
            app = QApplication.instance()
            for win in app._windows:
                if win.isVisible(): win._draw_recursive(pygame.Vector2(0,0))
            for popup in app._popups:
                if hasattr(popup, '_draw_popup_overlay'): popup._draw_popup_overlay()
            
            pygame.display.flip()
            clock.tick(60)
            
        QApplication.instance().remove_popup(self)
        return self._triggered_action

    def _on_action_triggered(self, action):
        self._triggered_action = action
        self._closing = True

    def _draw_popup_overlay(self):
        if hasattr(self, '_popup_pos'):
            self._draw_dropdown(pygame.Vector2(self._popup_pos.x(), self._popup_pos.y()))

    def _handle_popup_event(self, event):
        if not hasattr(self, '_popup_pos'): return False
        pos = pygame.Vector2(self._popup_pos.x(), self._popup_pos.y())
        mouse_pos = pygame.mouse.get_pos()
        local_pos = pygame.Vector2(mouse_pos[0] - pos.x, mouse_pos[1] - pos.y)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self._handle_dropdown_click(local_pos):
                return True
            if not self._rect_contains(local_pos):
                self._closing = True
                return False # Let it pass to maybe open another menu
        elif event.type == pygame.MOUSEMOTION:
            return self._handle_dropdown_motion(local_pos)
        return False

    def _close_all_submenus(self):
        if self._active_submenu:
            self._active_submenu._close_all_submenus()
            self._active_submenu = None

    def _draw(self, pos):
        """Draw the menu at the given position (standalone, not dropdown)."""
        self._draw_dropdown(pos)
        
    def _draw_dropdown(self, pos):
        screen = pygame.display.get_surface()
        if not screen or not self._actions: return
        w, h = 200, len(self._actions) * 28
        
        from .gui import QColor
        bg_color_str = self._get_style_property('background-color')
        bg_color = (255, 255, 255)
        if bg_color_str:
            try: bg_color = QColor(bg_color_str).to_pygame()
            except: pass
            
        text_color_str = self._get_style_property('color')
        text_color = (45, 45, 50)
        if text_color_str:
            try: text_color = QColor(text_color_str).to_pygame()
            except: pass
            
        border_color = (160, 160, 170)
        border_str = self._get_style_property('border')
        if border_str:
            parts = border_str.split()
            for p in parts:
                if p.startswith('#') or p in QColor.NAMED_COLORS:
                    try: border_color = QColor(p).to_pygame()
                    except: pass

        # Draw main background
        pygame.draw.rect(screen, bg_color, (pos.x, pos.y, w, h))
        pygame.draw.rect(screen, border_color, (pos.x, pos.y, w, h), 1)
        
        font = pygame.font.SysFont(None, 18)
        mouse_pos = pygame.mouse.get_pos()
        
        for i, a in enumerate(self._actions):
            rect = pygame.Rect(pos.x, pos.y + i*28, w, 28)
            
            # Highlight if hovered or if it's the active submenu parent
            is_active_parent = (isinstance(a, QMenu) and self._active_submenu == a)
            is_hovered = rect.collidepoint(mouse_pos)
            
            if a == "SEP":
                 pygame.draw.line(screen, (220, 220, 225), (pos.x+10, pos.y+i*28+14), (pos.x+w-10, pos.y+i*28+14))
            else:
                is_menu = isinstance(a, QMenu)
                label = (a.text if not is_menu else a.text + "  >")
                
                if is_hovered or is_active_parent:
                    # Selection/Hover style via sub_element='item'
                    sel_bg_str = self._get_style_property('background-color', pseudo='selected', sub_element='item')
                    sel_color_str = self._get_style_property('color', pseudo='selected', sub_element='item')
                    
                    sel_bg = (0, 120, 215)
                    if sel_bg_str:
                        try: sel_bg = QColor(sel_bg_str).to_pygame()
                        except: pass
                    
                    sel_color = (255, 255, 255)
                    if sel_color_str:
                        try: sel_color = QColor(sel_color_str).to_pygame()
                        except: pass
                    else:
                        # Fallback: contrast check
                        if (sel_bg[0]*0.299 + sel_bg[1]*0.587 + sel_bg[2]*0.114) > 186:
                            sel_color = (0, 0, 0)
                        
                    pygame.draw.rect(screen, sel_bg, rect)
                    txt = font.render(str(label) if label is not None else "", True, sel_color)
                else:
                    txt = font.render(str(label) if label is not None else "", True, text_color)
                
                screen.blit(txt, (pos.x + 12, pos.y + i*28 + (28 - txt.get_height()) // 2))
                
                # Draw submenu if active
                if is_active_parent:
                    submenu_pos = pygame.Vector2(pos.x + w, pos.y + i*28)
                    a._draw_dropdown(submenu_pos)

    def _rect_contains(self, local_pos):
        # Helper to check if pos is within this menu OR its submenus
        w, h = 200, len(self._actions) * 28
        if 0 <= local_pos.x <= w and 0 <= local_pos.y <= h:
            return True
            
        if self._active_submenu:
            # Check submenu bounds
            # Submenu is at x+200, and some y offset
            # We need to find the y offset of the submenu parent
            submenu_y_offset = -1
            for i, a in enumerate(self._actions):
                if a == self._active_submenu:
                    submenu_y_offset = i * 28
                    break
            
            if submenu_y_offset != -1:
                # Transform local_pos to submenu local space
                # Submenu starts at (200, submenu_y_offset) relative to this menu
                sub_local = pygame.Vector2(local_pos.x - 200, local_pos.y - submenu_y_offset)
                return self._active_submenu._rect_contains(sub_local)
                
        return False

    def _handle_dropdown_click(self, local_pos):
        # local_pos is relative to the top-left of THIS menu
        w, h = 200, len(self._actions) * 28
        
        # 1. Check if click is in active submenu
        if self._active_submenu:
            submenu_y_offset = -1
            for i, a in enumerate(self._actions):
                if a == self._active_submenu:
                    submenu_y_offset = i * 28
                    break
            
            if submenu_y_offset != -1:
                # Submenu area check loosely (right side)
                if local_pos.x >= 200:
                    sub_local = pygame.Vector2(local_pos.x - 200, local_pos.y - submenu_y_offset)
                    if self._active_submenu._handle_dropdown_click(sub_local):
                        return True
        
        # 2. Check click on this menu items
        if 0 <= local_pos.x <= w and 0 <= local_pos.y <= h:
            idx = int(local_pos.y // 28)
            if 0 <= idx < len(self._actions):
                a = self._actions[idx]
                if a == "SEP": return False
                
                if isinstance(a, QAction):
                     if a.isEnabled() and a.isVisible():
                        # Close menu hierarchy
                        curr = self
                        while curr:
                            if hasattr(curr, '_active_menu'): curr._active_menu = None
                            if hasattr(curr, '_parent'): curr = curr._parent
                            else: break
                        
                        a.triggered.emit() 
                        return True
                elif isinstance(a, QMenu):
                    # Clicked on a submenu item -> Toggle it? 
                    # Usually clicks just open it if not open, or do nothing if already open
                    # We rely on hover, but click is good backup
                    self._active_submenu = a
                    return False # Keep menu open
        return False

    def _handle_dropdown_motion(self, local_pos):
        w, h = 200, len(self._actions) * 28
        
        # 1. Pass motion to active submenu if we are in its "territory" (to the right)
        if self._active_submenu:
            submenu_y_offset = -1
            for i, a in enumerate(self._actions):
                if a == self._active_submenu:
                    submenu_y_offset = i * 28
                    break
            
            # If mouse is clearly strictly inside the submenu zone
            # (Simple heuristic: to the right of this menu)
            if local_pos.x >= 200:
                 sub_local = pygame.Vector2(local_pos.x - 200, local_pos.y - submenu_y_offset)
                 if self._active_submenu._handle_dropdown_motion(sub_local):
                     return True
                 # If returns False, maybe we moved out of submenu?
                 # Don't close immediately to allow diagonal movement? 
                 # For now, strict: if not in submenu, maybe we are back in this menu?
        
        # 2. Check hover on this menu items
        if 0 <= local_pos.x <= w and 0 <= local_pos.y <= h:
            idx = int(local_pos.y // 28)
            if 0 <= idx < len(self._actions):
                item = self._actions[idx]
                if isinstance(item, QMenu):
                    # Hovering over a submenu item -> Open it
                    if self._active_submenu != item:
                        self._active_submenu = item
                elif isinstance(item, QAction) or item == "SEP":
                    # Hovering over a normal item -> Close active submenu
                    if self._active_submenu:
                        self._active_submenu = None
            return True
        
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
