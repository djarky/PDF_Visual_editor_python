import pygame
from .core import QObject, Signal, Qt, QSize, QRect
from .widgets import QWidget
from .application import QApplication
from .gui import QColor, QPen

class QAbstractItemModel(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
    def index(self, row, column, parent=None): return None
    def parent(self, index): return None
    def rowCount(self, parent=None): return 0
    def columnCount(self, parent=None): return 0
    def data(self, index, role=Qt.ItemDataRole.DisplayRole): return None

class QAbstractItemView(QWidget):
    class SelectionMode: SingleSelection = 1; MultiSelection = 2; ExtendedSelection = 3; ContourSelection = 4
    class DragDropMode: NoDragDrop = 0; InternalMove = 4
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selectionChanged = Signal()
    def setDragDropMode(self, m): 
        self._drag_drop_mode = m
    def setSelectionMode(self, m): 
        self._selection_mode = m
    def wheelEvent(self, ev):
        delta = ev.angleDelta().y()
        self._scroll_y = getattr(self, '_scroll_y', 0) - (delta / 120.0) * 40
        self._scroll_y = max(0, self._scroll_y)
        ev.accept()

class QHeaderView:
    class ResizeMode: Stretch = 1; ResizeToContents = 2; Fixed = 3; Interactive = 0
    def __init__(self, parent=None):
        self._resize_modes = {}
        self._default_resize_mode = 0
    def setSectionResizeMode(self, *args):
        if not hasattr(self, '_resize_modes'): self._resize_modes = {}
        if len(args) == 2: self._resize_modes[args[0]] = args[1]
        elif len(args) == 1: self._default_resize_mode = args[0]
    def sectionSize(self, index, total_w, count):
        mode = self._resize_modes.get(index, getattr(self, '_default_resize_mode', 0))
        if mode == 1: # Stretch
            return total_w // count
        return total_w // count # Default fallback

class QStyleOptionViewItem:
    def __init__(self):
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.state = 0
        self.text = ""

class QStyledItemDelegate(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        
    def paint(self, painter, option, index):
        if not index: return
        
        # State
        is_selected = option.state & Qt.ItemFlag.ItemIsSelected if hasattr(option, 'state') else False
        is_focused = option.state & Qt.ItemFlag.ItemIsFocused if hasattr(option, 'state') else False
        
        # Draw selection background
        if is_selected:
            painter.fillRect(option.rect, QColor(0, 120, 215)) # Standard blue selection
        
        # Get Icon
        icon_val = index.data(Qt.ItemDataRole.DecorationRole)
        icon_w = 0
        if icon_val:
            # icon_val could be QPixmap or QIcon
            pix = icon_val.pixmap if hasattr(icon_val, 'pixmap') else icon_val
            if hasattr(pix, 'surface') and pix.surface:
                icon_h = option.rect.height - 4
                # Scale if needed? Defaulting to small icons
                scaled_pix = pix
                if pix.height() > icon_h:
                    from .gui import QPixmap
                    scaled_pix = pix.scaledToWidth(int(pix.width() * (icon_h / pix.height())))
                
                painter.drawPixmap(option.rect.x + 2, option.rect.y + (option.rect.height - scaled_pix.height()) // 2, scaled_pix)
                icon_w = scaled_pix.width() + 5

        # Get Text
        text = str(index.data(Qt.ItemDataRole.DisplayRole) or "")
        
        # Text Color
        text_color = QColor(255, 255, 255) if is_selected else QColor(0, 0, 0)
        painter.setPen(text_color)
        
        # Alignment
        align = option.displayAlignment if hasattr(option, 'displayAlignment') else Qt.AlignmentFlag.AlignLeft
        
        # Draw Text with alignment
        rect = pygame.Rect(option.rect.x + icon_w, option.rect.y, option.rect.width - icon_w, option.rect.height)
        painter.drawText(rect, align, text)
        
        # Focus Rect
        if is_focused:
            from .gui import QPen
            pen = QPen(QColor(100, 100, 100))
            pen.setStyle(Qt.PenStyle.DotLine)
            painter.setPen(pen)
            painter.drawRect(option.rect)
            
    def sizeHint(self, option, index):
        # Basic size hint based on text
        text = str(index.data(Qt.ItemDataRole.DisplayRole) or "")
        return QSize(100, 30) # Default/Fallback

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
        
        from .gui import QPainter, QColor
        painter = QPainter(screen)
        
        font = pygame.font.SysFont("Arial", 12)
        header_h = 25
        item_h = 22
        
        # Header background
        pygame.draw.rect(screen, (240, 240, 243), (pos.x, pos.y, self._rect.width, header_h))
        pygame.draw.line(screen, (200, 200, 205), (pos.x, pos.y + header_h), (pos.x + self._rect.width, pos.y + header_h))
        
        # Header text
        labels = getattr(self, '_header_labels', ["Element", "Type", "Vis", "Opacity"])
        for i, lbl in enumerate(labels):
            col_w = self._header.sectionSize(i, self._rect.width, len(labels))
            txt = font.render(lbl, True, (60, 60, 70))
            screen.blit(txt, (pos.x + i * col_w + 5, pos.y + (header_h - txt.get_height()) // 2))
            if i > 0:
                pygame.draw.line(screen, (200, 200, 205), (pos.x + i * col_w, pos.y + 2), (pos.x + i * col_w, pos.y + header_h - 2))

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
            
            # Visibility culling
            if curr_y + item_h < pos.y + header_h:
                if getattr(item, '_expanded', True):
                    curr_y += item_h 
                    for i in range(item.childCount()):
                        draw_item(item.child(i), level + 1, y_offset)
                    curr_y -= item_h
                curr_y += item_h
                return

            if curr_y > pos.y + self._rect.height: return
            
            is_selected = getattr(item, '_selected', False)
            
            # Draw Columns
            indent = level * 15
            
            for c, _ in enumerate(labels):
                col_w = self._header.sectionSize(c, self._rect.width, len(labels))
                col_x = pos.x + c * col_w
                
                # Rect for this cell
                cell_rect = pygame.Rect(col_x, curr_y, col_w, item_h)
                
                # Delegate?
                delegate = self._delegates.get(c) if hasattr(self, '_delegates') else None
                
                if delegate:
                    option = QStyleOptionViewItem()
                    option.rect = cell_rect
                    option.state = Qt.ItemFlag.ItemIsSelected if is_selected else 0
                    if is_selected: option.state |= Qt.ItemFlag.ItemIsSelected
                    
                    index = MockIndex(item, c)
                    delegate.paint(painter, option, index)
                else:
                    # Default drawing - Inline implementation
                    if is_selected:
                        pygame.draw.rect(screen, (0, 120, 215), cell_rect)
                        text_color = (255, 255, 255)
                    else:
                        text_color = (30, 30, 30)
                        if (curr_y - pos.y - header_h) // item_h % 2 == 1:
                            pass # Alternating logic handled per row, simplifying here
                            # Or we can draw row background if c == 0
                    
                    # Manual alternation
                    if not is_selected and (curr_y - pos.y - header_h) // item_h % 2 == 1:
                         pygame.draw.rect(screen, (245, 245, 250), cell_rect)

                    txt_val = item.text(c)
                    if txt_val:
                        txt_surf = font.render(str(txt_val), True, text_color)
                        # Indent only for col 0
                        x_off = 5 + indent if c == 0 else 5
                        screen.blit(txt_surf, (col_x + x_off, curr_y + (item_h - txt_surf.get_height()) // 2))

            curr_y += item_h
            
            if getattr(item, '_expanded', True):
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

    def mousePressEvent(self, ev):
        mx, my = ev.pos().x(), ev.pos().y()
        item = self.itemAt(mx, my)
        if item:
            self.clearSelection()
            item._selected = True
            
            # Check for visibility toggle (Column 2)
            col_w = self._rect.width // 4 # Assume 4 columns
            col = int(mx // col_w)
            
            self.itemSelectionChanged.emit()
            if col == 2: # Vis column
                 self.itemChanged.emit(item, 2)

class QTreeWidgetItem:
    def __init__(self, parent=None, strings=None):
        self._parent, self._children, self._data, self._text = parent, [], {}, {}
        self._selected = False; self._expanded = True; self._flags = 0
        if isinstance(strings, list):
            for i, s in enumerate(strings): self.setText(i, s)
        elif isinstance(strings, str):
            self.setText(0, strings)
        if parent and hasattr(parent, 'addChild'): parent.addChild(self)
    def flags(self): return self._flags
    def setFlags(self, f): self._flags = f
    def isSelected(self): return self._selected
    def setSelected(self, b): self._selected = b
    def checkState(self, column): return self._data.get(('check', column), Qt.CheckState.Unchecked)
    def setCheckState(self, column, state): self._data[('check', column)] = state
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

class QListModel(QAbstractItemModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.rowsMoved = Signal()

class QListWidget(QAbstractItemView):
    class ViewMode: IconMode = 1; ListMode = 0
    def __init__(self, parent=None):
        super().__init__(parent); self.itemClicked, self._items = Signal(), []
        self._model = QListModel(self)
    def setIconSize(self, s): 
        self._icon_size = s
    def setViewMode(self, m): 
        self._view_mode = m
    def setSelectionMode(self, m): 
        self._selection_mode = m
    def setDragEnabled(self, b): 
        self._drag_enabled = b
    def setDropIndicatorShown(self, b): 
        self._drop_indicator_shown = b
    def setDragDropMode(self, m): 
        self._drag_drop_mode = m
    def model(self): return self._model
    def addItem(self, i): 
        if isinstance(i, str):
            i = QListWidgetItem(i)
        self._items.append(i); i._list = self
    def count(self): return len(self._items)
    def clear(self): self._items = []
    def item(self, i): return self._items[i] if i < len(self._items) else None

    def _draw(self, pos):
        super()._draw(pos)
        if not QApplication._instance or not QApplication._instance._windows: return
        screen = QApplication._instance._windows[0]._screen
        if not screen: return
        
        font = pygame.font.SysFont("Arial", 12)
        item_w, item_h = 110, 160
        margin = 10
        
        # Calculate grid
        cols = max(1, self._rect.width // (item_w + margin))
        
        # Clip
        old_clip = screen.get_clip()
        screen.set_clip(pygame.Rect(pos.x, pos.y, self._rect.width, self._rect.height))
        
        for i, item in enumerate(self._items):
            row, col = i // cols, i % cols
            x = pos.x + margin + col * (item_w + margin)
            y = pos.y + margin + row * (item_h + margin) - getattr(self, '_scroll_y', 0)
            
            if y + item_h < pos.y: continue
            if y > pos.y + self._rect.height: break
            
            # Selection highlight
            if getattr(item, '_selected', False):
                pygame.draw.rect(screen, (0, 120, 215), (x-2, y-2, item_w+4, item_h+4), border_radius=4)
            
            # Background
            pygame.draw.rect(screen, (255, 255, 255), (x, y, item_w, item_h), border_radius=2)
            pygame.draw.rect(screen, (200, 200, 200), (x, y, item_w, item_h), 1, border_radius=2)
            
            # Icon (Pixmap)
            if hasattr(item, 'icon') and item.icon and hasattr(item.icon, 'pixmap'):
                pix = item.icon.pixmap
                if pix and pix.surface:
                    # Scale pixmap to fit item_w - 10
                    scaled_w = item_w - 10
                    scaled_h = int(pix.height() * (scaled_w / pix.width()))
                    if scaled_h > item_h - 25:
                        scaled_h = item_h - 25
                        scaled_w = int(pix.width() * (scaled_h / pix.height()))
                    
                    try:
                        surf = pygame.transform.smoothscale(pix.surface, (scaled_w, scaled_h))
                        screen.blit(surf, (x + (item_w - scaled_w)//2, y + 5))
                    except: pass
            
            # Text
            text = item.text() if hasattr(item, 'text') and callable(item.text) else getattr(item, 'text', '')
            txt_surf = font.render(str(text), True, (0, 0, 0))
            screen.blit(txt_surf, (x + (item_w - txt_surf.get_width())//2, y + item_h - 18))
            
        screen.set_clip(old_clip)

    def mousePressEvent(self, ev):
        if not self._items: return
        mx, my = ev.pos().x(), ev.pos().y()
        
        item_w, item_h = 110, 160
        margin = 10
        cols = max(1, self._rect.width // (item_w + margin))
        
        # Calculate which item was clicked
        col = (mx - margin) // (item_w + margin)
        row = (my - margin + getattr(self, '_scroll_y', 0)) // (item_h + margin)
        
        if 0 <= col < cols:
            idx = row * cols + col
            if 0 <= idx < len(self._items):
                # Clear previous selection
                for item in self._items: item._selected = False
                self._items[idx]._selected = True
                self.itemClicked.emit(self._items[idx])

class QListWidgetItem:
    def __init__(self, *args):
        self._data = {}
        self._text = ""
        self.icon = None
        self._selected = False
        from .gui import QIcon
        if len(args) > 1: 
            self.icon = args[0] # Might be QIcon or QPixmap
            self._text = args[1]
        elif len(args) > 0: 
            if isinstance(args[0], QIcon): self.icon = args[0]
            else: self._text = args[0]
    def setData(self, r, v): self._data[r] = v
    def data(self, r): return self._data.get(r)
    def text(self): return self._text
    def isSelected(self): return self._selected
    def setSelected(self, b): self._selected = b
