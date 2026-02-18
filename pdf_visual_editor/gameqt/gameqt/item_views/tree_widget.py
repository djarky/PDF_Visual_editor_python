import pygame
from ..core import Qt, Signal
from ..application import QApplication
from .abstract_item_view import QAbstractItemView, QHeaderView, QStyleOptionViewItem

class QTreeWidget(QAbstractItemView):
    def __init__(self, parent=None):
        super().__init__(parent); self._items, self._header = [], QHeaderView(); self._root = QTreeWidgetItem(None); self.tree = self
        self._root._item_view = self
        self.itemChanged, self.itemSelectionChanged, self.customContextMenuRequested = Signal(object, int), Signal(), Signal(object)
    def addChild(self, item): self._root.addChild(item)
    def addTopLevelItem(self, item): self._root.addChild(item)
    def topLevelItemCount(self): return self._root.childCount()
    def clear(self): self._root = QTreeWidgetItem(None); self._root._item_view = self
    def clearSelection(self):
        def unselect(item):
            item._selected = False
            for i in range(item.childCount()): unselect(item.child(i))
        unselect(self._root)
        self.selectionChanged.emit()
        self.itemSelectionChanged.emit()
    def invisibleRootItem(self): return self._root
    def header(self): return self._header
    def setHeaderLabels(self, l): 
        self._header_labels = l
    def setItemDelegateForColumn(self, c, d): 
        if not hasattr(self, '_delegates'):
            self._delegates = {}
        self._delegates[c] = d
    def setContextMenuPolicy(self, p): 
        self._context_menu_policy = p
    def setDragEnabled(self, b): 
        self._drag_enabled = b
    def setAcceptDrops(self, b): 
        self._accept_drops = b
    def indexOfTopLevelItem(self, item):
        return self._root.indexOfChild(item)
    def takeTopLevelItem(self, index):
        return self._root.takeChild(index)
    def topLevelItem(self, i): return self._root.child(i) if i < self._root.childCount() else None
    def selectedItems(self):
        # Recursive search for selected items
        items = []
        def traverse(item):
            if hasattr(item, 'isSelected') and item.isSelected(): items.append(item)
            for i in range(item.childCount()): traverse(item.child(i))
        # Also check top level items
        for item in self._items: traverse(item)
        return items
    def currentItem(self):
        sel = self.selectedItems()
        return sel[0] if sel else None
    def expandAll(self):
        def expand(item):
            item.setExpanded(True)
            for i in range(item.childCount()): expand(item.child(i))
        for i in range(self._root.childCount()): expand(self._root.child(i))
    def collapseAll(self):
        def collapse(item):
            item.setExpanded(False)
            for i in range(item.childCount()): collapse(item.child(i))
        for i in range(self._root.childCount()): collapse(self._root.child(i))

    def scrollToItem(self, item, hint=None):
        # Calculate Y position of the item
        y = 0
        found = False
        
        def traverse(curr, target):
            nonlocal y, found
            if found: return
            if curr == target: 
                found = True
                return
            
            y += 22 # item_h
            if curr.isExpanded():
                for i in range(curr.childCount()):
                    traverse(curr.child(i), target)
                    if found: return

        # Start traversal from root children
        for i in range(self.topLevelItemCount()):
            traverse(self.topLevelItem(i), item)
            if found: break
            
        if found:
            # Adjust _scroll_y
            header_h = 25
            visible_h = self._rect.height - header_h
            
            # Simple logic: ensure item top is visible
            current_scroll = getattr(self, '_scroll_y', 0)
            item_top = y
            item_bottom = y + 22
            
            if item_top < current_scroll:
                self._scroll_y = item_top
            elif item_bottom > current_scroll + visible_h:
                self._scroll_y = item_bottom - visible_h
            
            # Ensure non-negative? 
            # if self._scroll_y < 0: self._scroll_y = 0


    def _draw(self, pos):
        super()._draw(pos)
        if not QApplication._instance or not QApplication._instance._windows: return
        screen = self._get_screen()
        if not screen: return
        
        from ..gui import QPainter, QColor
        painter = QPainter(screen)
        
        font = pygame.font.SysFont("Arial", 12)
        header_h = 25
        item_h = 22
        
        labels = getattr(self, '_header_labels', ["Element", "Type", "Vis", "Opacity"])
        
        # Seed default sizes on first draw
        self._header.initDefaultSizes(self._rect.width, len(labels))
        col_offsets = self._header.columnOffsets(self._rect.width, len(labels))
        
        # 1. Header background styling
        header_bg = (240, 240, 243)
        header_text_color = (60, 60, 70)
        header_border_color = (200, 200, 205)
        
        app_style = QApplication._global_style
        if app_style and "QHeaderView::section" in app_style:
            h_style = app_style["QHeaderView::section"]
            if 'background-color' in h_style:
                try: header_bg = QColor(h_style['background-color']).to_pygame()
                except: pass
            if 'color' in h_style:
                try: header_text_color = QColor(h_style['color']).to_pygame()
                except: pass
            if 'border-right' in h_style:
                parts = h_style['border-right'].split()
                for p in parts:
                    if p.startswith('#') or p in QColor.NAMED_COLORS:
                        try: header_border_color = QColor(p).to_pygame()
                        except: pass
        
        pygame.draw.rect(screen, header_bg, (pos.x, pos.y, self._rect.width, header_h))
        pygame.draw.line(screen, header_border_color,
                         (pos.x, pos.y + header_h), (pos.x + self._rect.width, pos.y + header_h))
        
        # Header text + separator handles
        mouse_x, mouse_y = pygame.mouse.get_pos()
        sep_hit_zone = 4  # pixels either side of separator
        for i, lbl in enumerate(labels):
            col_x, col_w = col_offsets[i]
            txt = font.render(lbl, True, header_text_color)
            screen.blit(txt, (pos.x + col_x + 5, pos.y + (header_h - txt.get_height()) // 2))
            
            # Draw separator line between columns (not before first)
            if i > 0:
                sep_x = pos.x + col_x
                # Highlight if mouse is near this separator or we're dragging it
                is_near = abs(mouse_x - sep_x) <= sep_hit_zone and pos.y <= mouse_y <= pos.y + header_h
                is_dragging = getattr(self, '_resize_col', None) == i
                sep_color = (80, 120, 200) if (is_near or is_dragging) else header_border_color
                sep_width = 2 if (is_near or is_dragging) else 1
                pygame.draw.line(screen, sep_color,
                                 (sep_x, pos.y + 2), (sep_x, pos.y + header_h - 2), sep_width)

        # Items
        curr_y = pos.y + header_h - getattr(self, '_scroll_y', 0)
        
        # Clip body
        old_clip = screen.get_clip()
        body_rect = pygame.Rect(pos.x, pos.y + header_h, self._rect.width, self._rect.height - header_h)
        screen.set_clip(body_rect)

        # Helper for index
        class MockIndex:
            def __init__(self, item, col): self._item, self._col = item, col
            def data(self, role=Qt.ItemDataRole.DisplayRole): 
                if role == Qt.ItemDataRole.DisplayRole:
                    return self._item.text(self._col)
                return self._item.data(self._col, role)
            def row(self): return 0 # stub
            def column(self): return self._col

        # Recursive draw for tree
        def draw_item(item, level, y_offset):
            nonlocal curr_y
            
            item_h = 22
            # Visibility culling
            if curr_y + item_h < pos.y + header_h:
                if item.isExpanded():
                    for i in range(item.childCount()):
                        draw_item(item.child(i), level + 1, y_offset)
                curr_y += item_h
                return

            if curr_y > pos.y + self._rect.height: return
            
            is_selected = getattr(item, '_selected', False)
            indent = level * 16
            
            for c, _ in enumerate(labels):
                col_x_off, col_w = col_offsets[c]
                col_x = pos.x + col_x_off
                
                cell_rect = pygame.Rect(col_x, curr_y, col_w, item_h)
                
                delegate = self._delegates.get(c) if hasattr(self, '_delegates') else None
                
                if delegate:
                    option = QStyleOptionViewItem()
                    option.rect = cell_rect
                    option.state = Qt.ItemFlag.ItemIsSelected if is_selected else 0
                    if is_selected: option.state |= Qt.ItemFlag.ItemIsSelected
                    index = MockIndex(item, c)
                    delegate.paint(painter, option, index)
                else:
                    # Default drawing
                    if is_selected:
                        sel_bg = (0, 120, 215)
                        sel_bg_str = self._get_style_property('background-color', pseudo='selected', sub_element='item')
                        if sel_bg_str:
                            try: sel_bg = QColor(sel_bg_str).to_pygame()
                            except: pass
                        pygame.draw.rect(screen, sel_bg, cell_rect)
                        text_color = (255, 255, 255)
                    else:
                        text_color = (30, 30, 30)
                        if (curr_y - pos.y - header_h) // item_h % 2 == 1:
                            pygame.draw.rect(screen, (244, 244, 247), cell_rect)
                    
                    x_off = 5
                    if c == 0:
                        if item.childCount() > 0:
                            arrow_rect = pygame.Rect(col_x + indent + 2, curr_y + 4, 12, 12)
                            arrow_color = (100, 100, 110)
                            if item.isExpanded():
                                pygame.draw.polygon(screen, arrow_color, [
                                    (arrow_rect.centerx - 4, arrow_rect.centery - 2),
                                    (arrow_rect.centerx + 4, arrow_rect.centery - 2),
                                    (arrow_rect.centerx, arrow_rect.centery + 3)
                                ])
                            else:
                                pygame.draw.polygon(screen, arrow_color, [
                                    (arrow_rect.centerx - 2, arrow_rect.centery - 4),
                                    (arrow_rect.centerx - 2, arrow_rect.centery + 4),
                                    (arrow_rect.centerx + 3, arrow_rect.centery)
                                ])
                        x_off = 20 + indent

                    check_state = item.checkState(c)
                    if check_state is not None:
                        box_size = 14
                        box_x = col_x + x_off
                        box_y = curr_y + (item_h - box_size) // 2
                        pygame.draw.rect(screen, (255, 255, 255), (box_x, box_y, box_size, box_size))
                        pygame.draw.rect(screen, (120, 120, 130), (box_x, box_y, box_size, box_size), 1)
                        if check_state == Qt.CheckState.Checked:
                            pygame.draw.line(screen, (0, 150, 0), (box_x+3, box_y+box_size//2), (box_x+box_size//2, box_y+box_size-3), 2)
                            pygame.draw.line(screen, (0, 150, 0), (box_x+box_size//2, box_y+box_size-3), (box_x+box_size-3, box_y+3), 2)
                        x_off += box_size + 5

                    txt_val = item.text(c)
                    if txt_val:
                        txt_surf = font.render(str(txt_val), True, text_color)
                        screen.blit(txt_surf, (col_x + x_off, curr_y + (item_h - txt_surf.get_height()) // 2))

            curr_y += item_h
            if item.isExpanded():
                for i in range(item.childCount()):
                    draw_item(item.child(i), level + 1, y_offset)

        # Iterate roots
        for i in range(self._root.childCount()):
            draw_item(self._root.child(i), 0, 0)
            
        screen.set_clip(old_clip)

    def itemAt(self, *args):
        # handle point or x,y
        if len(args) == 1: p = args[0]; x, y = p.x(), p.y()
        else: x, y = args
        
        header_h = 25
        item_h = 22
        if y < header_h: return None
        
        idx = (y - header_h) // item_h
        flat_items = []
        def flatten(item):
            flat_items.append(item)
            if getattr(item, '_expanded', True):
                for i in range(item.childCount()): flatten(item.child(i))
        for i in range(self._root.childCount()): flatten(self._root.child(i))
        
        return flat_items[int(idx)] if 0 <= idx < len(flat_items) else None

    def _get_sep_col_at(self, mx, my):
        """Return the column index whose LEFT separator is near mx,my (in header zone), or None."""
        header_h = 25
        if my > header_h: return None
        labels = getattr(self, '_header_labels', [])
        col_offsets = self._header.columnOffsets(self._rect.width, len(labels))
        sep_hit_zone = 5
        for i in range(1, len(labels)):
            sep_x = col_offsets[i][0]
            if abs(mx - sep_x) <= sep_hit_zone:
                return i
        return None

    def mousePressEvent(self, ev):
        mx, my = ev.pos().x(), ev.pos().y()
        
        # 1. Handle Context Menu
        if ev.button() == Qt.MouseButton.RightButton:
            self.customContextMenuRequested.emit(ev.pos())
            return

        # 2. Check for header separator drag start
        sep_col = self._get_sep_col_at(mx, my)
        if sep_col is not None:
            self._resize_col = sep_col
            self._resize_start_x = mx
            labels = getattr(self, '_header_labels', [])
            self._header.initDefaultSizes(self._rect.width, len(labels))
            col_offsets = self._header.columnOffsets(self._rect.width, len(labels))
            # Store the width of the column to the LEFT of the separator
            self._resize_col_start_w = col_offsets[sep_col - 1][1]
            return

        item = self.itemAt(mx, my)
        if not item: return

        # 3. Determine Column using actual offsets
        labels = getattr(self, '_header_labels', [])
        col_offsets = self._header.columnOffsets(self._rect.width, len(labels))
        col = -1
        for i, (cx, cw) in enumerate(col_offsets):
            if cx <= mx < cx + cw:
                col = i
                break
        if col == -1: return

        # 4. Handle Special Interactive Zones
        if col == 0:
            def get_level(curr):
                lvl = 0; p = curr.parent()
                while p: lvl += 1; p = p.parent()
                return lvl
            level = get_level(item)
            indent = level * 16
            if item.childCount() > 0 and mx < col_offsets[0][0] + indent + 20:
                item.setExpanded(not item.isExpanded())
                self.update()
                return

        # 5. Checkbox click
        check_state = item.checkState(col)
        if check_state is not None:
            new_state = Qt.CheckState.Unchecked if check_state == Qt.CheckState.Checked else Qt.CheckState.Checked
            item.setCheckState(col, new_state)
            self.itemChanged.emit(item, col)
            self.update()
            return

        # 6. Standard Selection
        if not (pygame.key.get_mods() & pygame.KMOD_CTRL):
            self.clearSelection()
        item.setSelected(not item.isSelected())
        self.itemSelectionChanged.emit()
        self.update()

    def mouseMoveEvent(self, ev):
        mx, my = ev.pos().x(), ev.pos().y()
        
        if getattr(self, '_resize_col', None) is not None:
            # Dragging a separator → resize the column to the left
            delta = mx - self._resize_start_x
            new_w = max(QHeaderView.MIN_SECTION_SIZE, self._resize_col_start_w + delta)
            self._header.resizeSection(self._resize_col - 1, new_w)
            self.update()
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_SIZEWE)
        else:
            # Hover: change cursor when near a separator in the header
            sep_col = self._get_sep_col_at(mx, my)
            if sep_col is not None:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_SIZEWE)
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    def mouseReleaseEvent(self, ev):
        if getattr(self, '_resize_col', None) is not None:
            self._resize_col = None
            self._resize_start_x = None
            self._resize_col_start_w = None
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            self.update()

class QTreeWidgetItem:
    def __init__(self, parent=None, strings=None):
        self._parent, self._children, self._data, self._text = parent, [], {}, {}
        self._selected = False; self._expanded = True; self._flags = 0
        self._check_states = {} # Specific storage for checkstates to allow None
        if isinstance(strings, list):
            for i, s in enumerate(strings): self.setText(i, s)
        elif isinstance(strings, str):
            self.setText(0, strings)
        if parent and hasattr(parent, 'addChild'): parent.addChild(self)
    def flags(self): return self._flags
    def setFlags(self, f): self._flags = f
    def isSelected(self): return self._selected
    def setSelected(self, b): self._selected = b
    def checkState(self, column): return self._check_states.get(column)
    def setCheckState(self, column, state): self._check_states[column] = state
    def setExpanded(self, b): self._expanded = b
    def isExpanded(self): return self._expanded
    def data(self, c, r): return self._data.get((c, r))
    def setData(self, c, r, v): self._data[(c, r)] = v
    def text(self, c): return self._text.get(c, "")
    def setText(self, c, t): self._text[c] = t
    def addChild(self, i): self._children.append(i); i._parent = self
    def insertChild(self, index, i): self._children.insert(index, i); i._parent = self
    def setIcon(self, column, icon): self._data[(column, Qt.ItemDataRole.DecorationRole)] = icon
    def removeChild(self, i): 
        if i in self._children: self._children.remove(i); i._parent = None
    def takeChild(self, index):
        if 0 <= index < len(self._children):
            c = self._children.pop(index)
            c._parent = None
            return c
        return None
    def indexOfChild(self, i):
        return self._children.index(i) if i in self._children else -1
    def childCount(self): return len(self._children)
    def child(self, i): return self._children[i]
    def parent(self): return self._parent if isinstance(self._parent, QTreeWidgetItem) else None
