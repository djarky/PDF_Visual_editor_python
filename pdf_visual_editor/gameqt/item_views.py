import pygame
from .core import Signal, Qt
from .widgets import QWidget
from .application import QApplication

class QAbstractItemView(QWidget):
    class SelectionMode: SingleSelection = 1; MultiSelection = 2; ExtendedSelection = 3; ContourSelection = 4
    class DragDropMode: NoDragDrop = 0; InternalMove = 4
    def setDragDropMode(self, m): 
        self._drag_drop_mode = m
    def setSelectionMode(self, m): 
        self._selection_mode = m

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
    itemChanged, itemSelectionChanged, customContextMenuRequested = Signal(object, int), Signal(), Signal(object)
    def __init__(self, parent=None):
        super().__init__(parent); self._items, self._header = [], QHeaderView(); self._root = QTreeWidgetItem(self); self.tree = self
    def clear(self): self._items = []
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
        if screen:
            pygame.draw.rect(screen, (240, 240, 240), (pos.x, pos.y, self._rect.width, 25))
            txt = pygame.font.SysFont(None, 14).render("Element | Type | Vis | Opacity", True, (50, 50, 50))
            screen.blit(txt, (pos.x + 5, pos.y + 5))

class QTreeWidgetItem:
    def __init__(self, parent=None):
        self._parent, self._children, self._data, self._text = parent, [], {}, {}
        self._selected = False
        if parent and hasattr(parent, 'addChild'): parent.addChild(self)
    def isSelected(self): return self._selected
    def setSelected(self, b): self._selected = b
    def setExpanded(self, b): pass
    def data(self, c, r): return self._data.get((c, r))
    def setData(self, c, r, v): self._data[(c, r)] = v
    def text(self, c): return self._text.get(c, "")
    def setText(self, c, t): self._text[c] = t
    def addChild(self, i): self._children.append(i); i._parent = self
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

class QListWidgetItem:
    def __init__(self, *args):
        self._data = {}
        if len(args) > 1: self.text = args[1]
        elif len(args) > 0: self.text = args[0]
    def setData(self, r, v): self._data[r] = v
    def data(self, r): return self._data.get(r)
