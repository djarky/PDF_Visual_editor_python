import pygame
from .core import Signal, Qt
from .widgets import QWidget
from .application import QApplication

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
    def setSectionResizeMode(self, *args):
        if not hasattr(self, '_resize_modes'):
            self._resize_modes = {}
        if len(args) == 2:
            c, m = args
            self._resize_modes[c] = m
        elif len(args) == 1:
            self._default_resize_mode = args[0]

class QStyledItemDelegate: pass
class QStyleOptionViewItem: pass

class QTreeWidget(QAbstractItemView):
    def __init__(self, parent=None):
        super().__init__(parent); self._items, self._header = [], QHeaderView(); self._root = QTreeWidgetItem(self); self.tree = self
        self.itemChanged, self.itemSelectionChanged, self.customContextMenuRequested = Signal(object, int), Signal(), Signal(object)
    def clear(self): self._items = []
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
        return self._items.index(item) if item in self._items else -1
    def takeTopLevelItem(self, index):
        return self._items.pop(index) if 0 <= index < len(self._items) else None
    def topLevelItem(self, i): return self._items[i] if i < len(self._items) else None
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
    def expandAll(self): pass
    def collapseAll(self): pass
    def _draw(self, pos):
        super()._draw(pos)
        if not QApplication._instance or not QApplication._instance._windows: return
        screen = QApplication._instance._windows[0]._screen
        if not screen: return
        
        font = pygame.font.SysFont("Arial", 12)
        header_h = 25
        item_h = 22
        
        # Header background
        pygame.draw.rect(screen, (240, 240, 243), (pos.x, pos.y, self._rect.width, header_h))
        pygame.draw.line(screen, (200, 200, 205), (pos.x, pos.y + header_h), (pos.x + self._rect.width, pos.y + header_h))
        
        # Header text
        labels = getattr(self, '_header_labels', ["Element", "Type", "Vis", "Opacity"])
        col_w = self._rect.width // len(labels)
        for i, lbl in enumerate(labels):
            txt = font.render(lbl, True, (60, 60, 70))
            screen.blit(txt, (pos.x + i * col_w + 5, pos.y + (header_h - txt.get_height()) // 2))
            if i > 0:
                pygame.draw.line(screen, (200, 200, 205), (pos.x + i * col_w, pos.y + 2), (pos.x + i * col_w, pos.y + header_h - 2))

        # Items
        curr_y = pos.y + header_h
        
        # Recursive draw for tree
        def draw_item(item, level, y_offset):
            nonlocal curr_y
            if curr_y > pos.y + self._rect.height: return
            
            # Selection
            if getattr(item, '_selected', False):
                pygame.draw.rect(screen, (0, 120, 215), (pos.x + 1, curr_y, self._rect.width - 2, item_h))
                text_color = (255, 255, 255)
            else:
                text_color = (30, 30, 30)
                if (curr_y - pos.y - header_h) // item_h % 2 == 1:
                    pygame.draw.rect(screen, (245, 245, 250), (pos.x + 1, curr_y, self._rect.width - 2, item_h))
            
            # Draw Columns
            indent = level * 15
            # Column 0: Text with "tree" indicator
            txt = font.render(item.text(0), True, text_color)
            screen.blit(txt, (pos.x + 5 + indent, curr_y + (item_h - txt.get_height()) // 2))
            
            # Other columns
            for c in range(1, len(labels)):
                val = item.text(c)
                if not val: continue
                txt = font.render(str(val), True, text_color)
                screen.blit(txt, (pos.x + c * col_w + 5, curr_y + (item_h - txt.get_height()) // 2))
                
            curr_y += item_h
            
            if getattr(item, '_expanded', True):
                for i in range(item.childCount()):
                    draw_item(item.child(i), level + 1, y_offset)

        # We need to iterate top level items
        # Root item children are top level
        for i in range(self._root.childCount()):
            draw_item(self._root.child(i), 0, 0)

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
    def __init__(self, parent=None):
        self._parent, self._children, self._data, self._text = parent, [], {}, {}
        self._selected = False; self._expanded = True; self._flags = 0
        if parent and hasattr(parent, 'addChild'): parent.addChild(self)
    def flags(self): return self._flags
    def setFlags(self, f): self._flags = f
    def isSelected(self): return self._selected
    def setSelected(self, b): self._selected = b
    def checkState(self, column): return self._data.get(('check', column), Qt.CheckState.Unchecked)
    def setCheckState(self, column, state): self._data[('check', column)] = state
    def setExpanded(self, b): self._expanded = b
    def data(self, c, r): return self._data.get((c, r))
    def setData(self, c, r, v): self._data[(c, r)] = v
    def text(self, c): return self._text.get(c, "")
    def setText(self, c, t): self._text[c] = t
    def addChild(self, i): self._children.append(i); i._parent = self
    def insertChild(self, index, i): self._children.insert(index, i); i._parent = self
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

class QListWidget(QAbstractItemView):
    class ViewMode: IconMode = 1; ListMode = 0
    def __init__(self, parent=None):
        super().__init__(parent); self.itemClicked, self._items = Signal(), []
        self._model = type('MockModel', (), {'rowsMoved': Signal()})()
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
    def addItem(self, i): self._items.append(i); i._list = self
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
            txt_surf = font.render(getattr(item, 'text', ''), True, (0, 0, 0))
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
        self.text = ""
        self.icon = None
        self._selected = False
        from .gui import QIcon
        if len(args) > 1: 
            self.icon = args[0] # Might be QIcon or QPixmap
            self.text = args[1]
        elif len(args) > 0: 
            if isinstance(args[0], QIcon): self.icon = args[0]
            else: self.text = args[0]
    def setData(self, r, v): self._data[r] = v
    def data(self, r): return self._data.get(r)
    def text(self): return self.text
