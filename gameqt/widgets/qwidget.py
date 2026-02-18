import pygame
import os
import sys
from ..core import QObject, Signal, QMouseEvent, QWheelEvent, QPoint, QSize, Qt, PyGameModalDialog
from ..application import QApplication

class QWidget(QObject):
    def __init__(self, parent=None):
        from ..gui import QFont
        super().__init__(parent); self._rect, self._visible, self._layout, self._stylesheet, self._screen = pygame.Rect(0, 0, 100, 100), False, None, "", None
        self._font = QFont()
        self._parent = None # Initialized by _set_parent
        self._children = []
        self._set_parent(parent)
        self.clicked = Signal(); self._accept_drops = False
        self._resized = False
        self._frame_shape = 0  # Qt.FrameShape.NoFrame
        self._window_flags = 0  # No flags by default
        self._cursor = None
    def update(self):
        for child in self._children: 
            if hasattr(child, 'update'): child.update()
    def setAcceptDrops(self, b): self._accept_drops = b
    def acceptDrops(self): return self._accept_drops
    def dragEnterEvent(self, event): 
        # Default implementation: accept nothing
        pass
    def dropEvent(self, event): 
        # Default implementation: do nothing
        pass
    def mousePressEvent(self, event):
        pass
    def mouseReleaseEvent(self, event):
        pass
    def mouseMoveEvent(self, event):
        pass
    def wheelEvent(self, event):
        pass
    def setWindowTitle(self, title):
        self._window_title = title
        from .qmainwindow import QMainWindow
        if isinstance(self, QMainWindow): pygame.display.set_caption(title)
    def resize(self, w, h): 
        self._rect.width, self._rect.height = w, h
        self._resized = True
        if hasattr(self, '_layout') and self._layout: self._layout.arrange(pygame.Rect(0, 0, w, h))
    def setGeometry(self, x, y, w, h):
        self._rect = pygame.Rect(x, y, w, h)
        self._resized = True
        if hasattr(self, '_layout') and self._layout: self._layout.arrange(pygame.Rect(0, 0, w, h))
    def move(self, x, y): self._rect.x, self._rect.y = x, y
    def setMinimumSize(self, w, h): self._min_size = (w, h)
    def minimumSize(self): return getattr(self, '_min_size', (0, 0))
    def setFrameShape(self, shape): 
        """Set the frame shape for this widget."""
        self._frame_shape = shape
    def frameShape(self): return getattr(self, '_frame_shape', 0)
    def setCursor(self, cursor): 
        """Set the cursor for this widget."""
        self._cursor = cursor
    def setFont(self, font):
        """Set the font for this widget."""
        self._font = font
        if hasattr(self, 'update'): self.update()
    def font(self):
        """Returns the font for this widget, respecting QSS properties."""
        if not hasattr(self, '_font'):
            from ..gui import QFont
            self._font = QFont()
        
        # Check for QSS overrides
        fs = self._get_style_property('font-size')
        if fs:
            try:
                # Handle '12px', '12pt', or just '12'
                size = int(re.search(r'\d+', fs).group())
                self._font.setPointSize(size)
            except: pass
            
        ff = self._get_style_property('font-family')
        if ff:
            # Strip quotes if present
            ff = ff.strip("'\"")
            self._font._family = ff
            
        fw = self._get_style_property('font-weight')
        if fw:
            bold = 'bold' in fw.lower() or any(x in fw for x in ['600','700','800','900'])
            if hasattr(self._font, 'setBold'): self._font.setBold(bold)
            elif hasattr(self._font, '_bold'): self._font._bold = bold # Fallback if setBold missing
            
        return self._font
    def setWindowFlags(self, flags):
        """Set window flags (Dialog, FramelessWindowHint, etc.)."""
        self._window_flags = flags
        # Apply frameless hint if set
        from ..core import Qt
        if flags & Qt.WindowType.WindowTitleHint == 0:
            # Frameless - would need window chrome removal in future
            pass
    def windowFlags(self): return getattr(self, '_window_flags', 0)
    def viewport(self): return self # Fallback
    def window(self):
        curr = self
        while curr._parent: curr = curr._parent
        return curr
    def _get_screen(self):
        if not QApplication._instance: return None
        win = self.window()
        screen = getattr(win, '_screen', None)
        if not screen and QApplication._instance._windows: screen = getattr(QApplication._instance._windows[0], '_screen', None)
        return screen
    def mapToGlobal(self, p):
        # Calculate absolute position by traversing parent hierarchy
        abs_x, abs_y = 0, 0
        curr = self
        while curr:
            abs_x += curr._rect.x
            abs_y += curr._rect.y
            curr = curr._parent
        
        # Use QPointF if available, otherwise fallback to QPoint
        try: from ..core import QPointF
        except ImportError: from ..core import QPoint as QPointF
        
        pt = QPointF(p)
        return QPointF(abs_x + pt.x(), abs_y + pt.y())
    def setCentralWidget(self, widget):
        widget._set_parent(self); widget.show()
        widget._rect = pygame.Rect(0, 0, self._rect.width, self._rect.height)
    def sizeHint(self):
        """Returns the recommended size for the widget."""
        if hasattr(self, '_layout') and self._layout:
            return self._layout.sizeHint()
        return QSize(100, 30)
    def setStyleSheet(self, ss):
        from ..utils import QSSParser
        self._stylesheet = ss
        self._parsed_styles = QSSParser.parse(ss)
        
        # Invalidate style cache recursively for this subtree
        self._reset_style_cache()

        # Notify of style change for dynamic updates (fonts, etc.)
        if hasattr(self, '_calculate_natural_size'):
            self._calculate_natural_size()
        self.update()

    def _reset_style_cache(self):
        if hasattr(self, '_style_cache'): self._style_cache.clear()
        for child in self._children:
            if hasattr(child, '_reset_style_cache'):
                child._reset_style_cache()

    def _get_style_property(self, prop, pseudo=None, sub_element=None):
        """Resolves a style property checking local, parent, and global stylesheets. Cached."""
        if not hasattr(self, '_style_cache'): self._style_cache = {}
        cache_key = (prop, pseudo, sub_element)
        if cache_key in self._style_cache:
            return self._style_cache[cache_key]

        inheritable = ['font-size', 'font-family', 'font-weight', 'color', 'text-align']
        
        mro_names = [cls.__name__ for cls in self.__class__.mro() if cls.__name__ != 'object']
        parent_chain = []
        curr = self._parent
        while curr:
            parent_chain.insert(0, [cls.__name__ for cls in curr.__class__.mro() if cls.__name__ != 'object'])
            curr = curr._parent

        def find_in_stylesheet(styles, cls_mro, p_chain):
            """Helper to find best matching style for this widget in a given parsed QSS dict."""
            best_val = None
            best_spec = -1
            for cls_name in cls_mro:
                for sel in styles:
                    parts = sel.split()
                    last_part = parts[-1]
                    
                    # Parsing sel last_part
                    s_pseudo = None
                    rem = last_part
                    if ':' in rem:
                        idx = rem.rfind(':')
                        if idx > 0 and rem[idx-1] != ':' and (idx == len(rem)-1 or rem[idx+1] != ':'):
                             s_pseudo = rem[idx+1:]
                             rem = rem[:idx]
                    s_sub = rem.split('::')[1] if '::' in rem else None
                    s_cls = rem.split('::')[0] if '::' in rem else rem
                    
                    if s_cls in (cls_name, "*") and s_sub == sub_element and s_pseudo == pseudo:
                        if len(parts) > 1:
                            # Descendant
                            match = True
                            curr_p_idx = len(p_chain) - 1
                            for anc_sel in reversed(parts[:-1]):
                                found = False
                                while curr_p_idx >= 0:
                                    if anc_sel in p_chain[curr_p_idx]:
                                        found = True; curr_p_idx -= 1; break
                                    curr_p_idx -= 1
                                if not found: match = False; break
                            if match and prop in styles[sel]:
                                if len(parts) > best_spec:
                                    best_val = styles[sel][prop]; best_spec = len(parts)
                        else:
                            if prop in styles[sel] and best_spec <= 1:
                                best_val = styles[sel][prop]; best_spec = 1
            return best_val

        # 1. Local overrides (Directly set on this instance via setStyleSheet)
        if hasattr(self, '_parsed_styles') and self._parsed_styles:
            # Check for flat properties first (selector "*")
            if "*" in self._parsed_styles and prop in self._parsed_styles["*"]:
                if not sub_element and (not pseudo or pseudo in getattr(self, '_active_pseudos', [])):
                    res = self._parsed_styles["*"][prop]
                    self._style_cache[cache_key] = res
                    return res
            # Check for selector matches in local stylesheet
            res = find_in_stylesheet(self._parsed_styles, mro_names, parent_chain)
            if res:
                self._style_cache[cache_key] = res
                return res

        # 2. Walk up parent hierarchy for local/regional stylesheets and inheritable properties
        curr = self._parent
        curr_p_chain = list(parent_chain)
        while curr:
            if hasattr(curr, '_parsed_styles') and curr._parsed_styles:
                # A. Check for selector matches in parent's stylesheet for THIS widget
                # When checking parent styles, parent_chain for THIS widget vs parent is same
                res = find_in_stylesheet(curr._parsed_styles, mro_names, curr_p_chain[:len(curr_p_chain)-1])
                if res:
                    self._style_cache[cache_key] = res
                    return res
                
                # B. Inheritable flat properties from parent
                if prop in inheritable and "*" in curr._parsed_styles and prop in curr._parsed_styles["*"]:
                    res = curr._parsed_styles["*"][prop]
                    self._style_cache[cache_key] = res
                    return res
            curr = curr._parent
            if curr_p_chain: curr_p_chain.pop()

        # 3. Global stylesheet resolution (Application-wide)
        app_style = QApplication._global_style
        if app_style:
            res = find_in_stylesheet(app_style, mro_names, parent_chain)
            if res:
                self._style_cache[cache_key] = res
                return res

        # 4. Fallback: Inherit from parent global style for inheritable properties
        if prop in inheritable and self._parent:
            res = self._parent._get_style_property(prop, pseudo, sub_element)
            self._style_cache[cache_key] = res
            return res

        self._style_cache[cache_key] = None
        return None
    def show(self):
        self._visible = True
        if not self._parent and not self._screen:
            self._screen = pygame.display.set_mode((self._rect.width, self._rect.height), pygame.RESIZABLE)
        for child in self._children:
            from ..menus import QMenu
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
        if parent and hasattr(parent, '_children'):
            if self not in parent._children:
                parent._children.append(self)
    def _handle_event(self, event, offset):
        if not self.isVisible(): return False
        my_pos = offset + pygame.Vector2(self._rect.topleft)
        
        # Apply cursor if mouse is over this widget
        if event.type == pygame.MOUSEMOTION and hasattr(self, '_cursor') and self._cursor:
            mouse_rect = pygame.Rect(my_pos.x, my_pos.y, self._rect.width, self._rect.height)
            if mouse_rect.collidepoint(pygame.mouse.get_pos()):
                try: 
                    pygame.mouse.set_cursor(self._cursor)
                except: 
                    pass
        
        # Special handling for QMainWindow with menu bar
        if hasattr(self, '_menu_bar') and self._menu_bar:
            if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
                menu_bar_rect = pygame.Rect(my_pos.x, my_pos.y, self._menu_bar._rect.width, self._menu_bar._rect.height)
                if menu_bar_rect.collidepoint(pygame.mouse.get_pos()) or (hasattr(self._menu_bar, '_active_menu') and self._menu_bar._active_menu):
                    return self._menu_bar._handle_event(event, my_pos)

        # 1. Deliver to children first (highest z-order)
        for child in reversed(self._children): 
            if child._handle_event(event, my_pos):
                return True
        
        # 2. Handle events for THIS widget
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
            mouse_rect = pygame.Rect(my_pos.x, my_pos.y, self._rect.width, self._rect.height)
            if mouse_rect.collidepoint(pygame.mouse.get_pos()):
                local_pos = pygame.Vector2(pygame.mouse.get_pos()) - my_pos
                btn = getattr(event, 'button', Qt.MouseButton.NoButton)
                if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
                    if btn == 1: btn = Qt.MouseButton.LeftButton
                    elif btn == 2: btn = Qt.MouseButton.MidButton
                    elif btn == 3: btn = Qt.MouseButton.RightButton
                    # Do not filter out 4/5, let them be for now if needed, but QMouseEvent doesn't have flags for them
                
                btns = 0
                if event.type == pygame.MOUSEMOTION:
                    if event.buttons[0]: btns |= Qt.MouseButton.LeftButton
                    if event.buttons[1]: btns |= Qt.MouseButton.MidButton
                    if event.buttons[2]: btns |= Qt.MouseButton.RightButton
                else: btns = btn
                
                q_event = QMouseEvent(local_pos, btn, btns, pygame.key.get_mods())
                q_event.ignore() # Not accepted by default for bubbling
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if hasattr(self, 'mousePressEvent'): 
                        self.mousePressEvent(q_event)
                        q_event.accept()
                elif event.type == pygame.MOUSEBUTTONUP:
                    if hasattr(self, 'mouseReleaseEvent'): self.mouseReleaseEvent(q_event)
                elif event.type == pygame.MOUSEMOTION:
                    if hasattr(self, 'mouseMoveEvent'): self.mouseMoveEvent(q_event)
                
                return q_event.isAccepted()
        
        if event.type == pygame.MOUSEWHEEL:
            mouse_rect = pygame.Rect(my_pos.x, my_pos.y, self._rect.width, self._rect.height)
            if mouse_rect.collidepoint(pygame.mouse.get_pos()):
                local_pos = pygame.Vector2(pygame.mouse.get_pos()) - my_pos
                px = getattr(event, 'precise_x', float(event.x))
                py = getattr(event, 'precise_y', float(event.y))
                w_event = QWheelEvent(local_pos, QPoint(int(px * 120), int(py * 120)), pygame.key.get_mods())
                w_event.ignore() # Default to ignored for bubbling
                if hasattr(self, 'wheelEvent'): self.wheelEvent(w_event)
                return w_event.isAccepted()
        
        # Legacy scroll
        if event.type == pygame.MOUSEBUTTONDOWN and event.button in (4, 5):
             mouse_rect = pygame.Rect(my_pos.x, my_pos.y, self._rect.width, self._rect.height)
             if mouse_rect.collidepoint(pygame.mouse.get_pos()):
                # We reuse mousePressEvent for legacy scroll handling in QScrollArea
                # But we should actually trigger wheelEvent or accepted mousePress
                return False # Let it bubble or be handled by specific logic
        
        return False
    
    def _handle_drop_event(self, event, offset):
        """Handle drag and drop events (DROPFILE, etc)"""
        if not self.isVisible(): return False
        my_pos = offset + pygame.Vector2(self._rect.topleft)
        
        # 1. Deliver to children first (highest z-order)
        for child in reversed(self._children): 
            if child._handle_drop_event(event, my_pos):
                return True
        
        # 2. Check if THIS widget accepts drops and mouse is over it
        if self._accept_drops:
            mouse_rect = pygame.Rect(my_pos.x, my_pos.y, self._rect.width, self._rect.height)
            if mouse_rect.collidepoint(pygame.mouse.get_pos()):
                from ..application import QDragEnterEvent, QDropEvent
                if isinstance(event, QDragEnterEvent):
                    event.ignore() # Default to ignored, subclass must accept
                    if hasattr(self, 'dragEnterEvent'): self.dragEnterEvent(event)
                elif isinstance(event, QDropEvent):
                    event.ignore() # Default to ignored
                    if hasattr(self, 'dropEvent'): self.dropEvent(event)
                return event.isAccepted()
        return False

    def _draw_recursive(self, offset=pygame.Vector2(0,0)):
        if not self.isVisible(): return
        if self._layout and hasattr(self._layout, 'arrange'): 
            # Layout arranges items relative to this widget's origin (0,0)
            self._layout.arrange(pygame.Rect(0, 0, self._rect.width, self._rect.height))
        my_pos = offset + pygame.Vector2(self._rect.topleft)
        self._draw(my_pos)
        for child in self._children: child._draw_recursive(my_pos)
    def _draw(self, pos):
        screen = self._get_screen()
        if not screen: return
        
        from ..gui import QColor
        
        # Determine pseudo-state
        abs_pos = self.mapToGlobal(QPoint(0,0))
        abs_rect = pygame.Rect(abs_pos.x(), abs_pos.y(), self._rect.width, self._rect.height)
        is_hovered = abs_rect.collidepoint(pygame.mouse.get_pos())
        
        pseudo = None
        if getattr(self, '_pressed', False): pseudo = "pressed"
        elif is_hovered: pseudo = "hover"
        elif getattr(self, '_focused', False): pseudo = "focus"
        
        # Resolve Styles from QSS (global or local)
        bg_color_str = self._get_style_property('background-color', pseudo)
        border_radius_str = self._get_style_property('border-radius', pseudo)
        border_str = self._get_style_property('border', pseudo)
        
        rect = pygame.Rect(pos.x, pos.y, self._rect.width, self._rect.height)
        
        # 1. Background
        radius = 0
        if border_radius_str:
            try: radius = int(border_radius_str.replace('px', '').strip())
            except: pass
            
        final_bg = None
        if bg_color_str:
            try: final_bg = QColor(bg_color_str).to_pygame()
            except: pass
        
        if final_bg:
            pygame.draw.rect(screen, final_bg, rect, border_radius=radius)
        elif self.__class__.__name__ == 'QMainWindow':
            # Default QMainWindow bg handled in subclass or here
            pygame.draw.rect(screen, (230, 230, 235), rect)
            
        # 2. Border
        if border_str:
            border_color = (120, 120, 130)
            border_width = 1
            if 'solid' in border_str:
                parts = border_str.split()
                for p in parts:
                    if p.endswith('px'): 
                        try: border_width = int(p.replace('px', ''))
                        except: pass
                    elif p.startswith('#') or p in QColor.NAMED_COLORS:
                        try: border_color = QColor(p).to_pygame()
                        except: pass
            pygame.draw.rect(screen, border_color, rect, border_width, border_radius=radius)
            
        # 2. Border
        if border_str:
            border_color = (120, 120, 130)
            border_width = 1
            if 'solid' in border_str:
                parts = border_str.split()
                for p in parts:
                    if p.endswith('px'): 
                        try: border_width = int(p.replace('px', ''))
                        except: pass
                    elif p.startswith('#') or p in QColor.NAMED_COLORS:
                        try: border_color = QColor(p).to_pygame()
                        except: pass
            pygame.draw.rect(screen, border_color, rect, border_width, border_radius=radius)
        # Removed hardcoded border fallback for legacy widgets to allow clean themes

        # 3. Frame Layout (Legacy frameShape support)
        from ..core import Qt
        frame_shape = getattr(self, '_frame_shape', 0)
        if frame_shape != Qt.FrameShape.NoFrame and frame_shape != 0 and not border_str:
            if frame_shape == Qt.FrameShape.Box:
                pygame.draw.rect(screen, (100, 100, 100), rect, 1)
            elif frame_shape == Qt.FrameShape.Panel:
                pygame.draw.line(screen, (220, 220, 220), (rect[0], rect[1]), (rect[0] + rect[2], rect[1]))
                pygame.draw.line(screen, (220, 220, 220), (rect[0], rect[1]), (rect[0], rect[1] + rect[3]))
                pygame.draw.line(screen, (80, 80, 80), (rect[0], rect[1] + rect[3]), (rect[0] + rect[2], rect[1] + rect[3]))
                pygame.draw.line(screen, (80, 80, 80), (rect[0] + rect[2], rect[1]), (rect[0] + rect[2], rect[1] + rect[3]))
            elif frame_shape == Qt.FrameShape.StyledPanel:
                pygame.draw.rect(screen, (200, 200, 200), rect, 2, border_radius=4)
    def statusBar(self):
        # In Qt, only QMainWindow has a statusBar. 
        # For compatibility in nested widgets, we can try to find the window.
        curr = self
        while curr:
            if hasattr(curr, 'statusBar') and curr != self:
                return curr.statusBar()
            curr = curr._parent
        return None
    def setAcceptDrops(self, b): 
        self._accept_drops = b
    def addAction(self, action): 
        if not hasattr(self, '_actions'):
            self._actions = []
        self._actions.append(action)
    def setContextMenuPolicy(self, policy): 
        self._context_menu_policy = policy
