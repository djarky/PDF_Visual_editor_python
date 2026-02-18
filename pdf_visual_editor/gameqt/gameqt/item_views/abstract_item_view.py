import pygame
from ..core import QObject, Signal, Qt, QSize, QRect
from ..widgets import QWidget
from ..gui import QColor, QPen

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
        self._scroll_y = 0
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
    MIN_SECTION_SIZE = 30  # Minimum column width in pixels

    def __init__(self, parent=None):
        self._resize_modes = {}
        self._default_resize_mode = 0
        self._section_sizes = {}   # {col_index: width_in_pixels}

    def setSectionResizeMode(self, *args):
        if not hasattr(self, '_resize_modes'): self._resize_modes = {}
        if len(args) == 2: self._resize_modes[args[0]] = args[1]
        elif len(args) == 1: self._default_resize_mode = args[0]

    def resizeSection(self, index, size):
        """Programmatically set a column width (also used by drag logic)."""
        self._section_sizes[index] = max(self.MIN_SECTION_SIZE, int(size))

    def sectionSize(self, index, total_w, count):
        # If user has manually resized this column, use that width.
        if index in self._section_sizes:
            return self._section_sizes[index]
        mode = self._resize_modes.get(index, getattr(self, '_default_resize_mode', 0))
        if mode == 2:  # ResizeToContents → compact fixed fallback
            return 60
        # Stretch or Interactive with no stored size → equal share
        return max(self.MIN_SECTION_SIZE, total_w // count)

    def columnOffsets(self, total_w, count):
        """Return list of (x_offset, width) for each column."""
        result = []
        x = 0
        for i in range(count):
            w = self.sectionSize(i, total_w, count)
            result.append((x, w))
            x += w
        return result

    def initDefaultSizes(self, total_w, count):
        """Seed _section_sizes with equal widths if not yet set."""
        if not self._section_sizes:
            base = max(self.MIN_SECTION_SIZE, total_w // count)
            for i in range(count):
                self._section_sizes[i] = base

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
                    from ..gui import QPixmap
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
            from ..gui import QPen
            pen = QPen(QColor(100, 100, 100))
            pen.setStyle(Qt.PenStyle.DotLine)
            painter.setPen(pen)
            painter.drawRect(option.rect)
            
    def sizeHint(self, option, index):
        # Basic size hint based on text
        text = str(index.data(Qt.ItemDataRole.DisplayRole) or "")
        return QSize(100, 30) # Default/Fallback
