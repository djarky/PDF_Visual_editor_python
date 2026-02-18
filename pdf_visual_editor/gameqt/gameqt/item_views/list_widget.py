import pygame
from ..core import Signal, Qt
from ..application import QApplication
from .abstract_item_view import QAbstractItemView, QAbstractItemModel

class QListModel(QAbstractItemModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.rowsMoved = Signal()

class QListWidgetItem:
    def __init__(self, *args):
        self._data = {}
        self._text = ""
        self.icon = None
        self._selected = False
        from ..gui import QIcon
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
            idx = int(row * cols + col)
            if 0 <= idx < len(self._items):
                # Clear previous selection
                for item in self._items: item._selected = False
                self._items[idx]._selected = True
                self.itemClicked.emit(self._items[idx])
