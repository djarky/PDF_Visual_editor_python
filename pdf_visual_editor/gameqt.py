import pygame
import sys
import os

class Qt:
    class Orientation: Horizontal = 1; Vertical = 2
    class AlignmentFlag: AlignCenter = 0x0084
    class MouseButton: LeftButton = 1; RightButton = 2; NoButton = 0
    class Key:
        Key_Delete = pygame.K_DELETE; Key_R = pygame.K_r; Key_J = pygame.K_j
        Key_Return = pygame.K_RETURN; Key_Enter = pygame.K_KP_ENTER; Key_Escape = pygame.K_ESCAPE
        Key_A = pygame.K_a; Key_C = pygame.K_c; Key_V = pygame.K_v; Key_X = pygame.K_x; Key_Z = pygame.K_z; Key_Y = pygame.K_y
    class KeyboardModifier: ControlModifier = pygame.KMOD_CTRL; AltModifier = pygame.KMOD_ALT; ShiftModifier = pygame.KMOD_SHIFT; NoModifier = 0
    class TransformationMode: SmoothTransformation = 1
    class CursorShape: ArrowCursor = pygame.SYSTEM_CURSOR_ARROW; CrossCursor = pygame.SYSTEM_CURSOR_CROSSHAIR; SizeFDiagCursor = pygame.SYSTEM_CURSOR_SIZENWSE
    class ItemDataRole: UserRole = 1000
    class CheckState: Checked = 2; Unchecked = 0
    class PenStyle: SolidLine = 1; DashLine = 2
    class BrushStyle: SolidPattern = 1; NoBrush = 0
    class TextInteractionFlag: NoTextInteraction = 0; TextEditorInteraction = 1
    class ContextMenuPolicy: CustomContextMenu = 1
    class ItemFlag: ItemIsEditable = 1

class Signal:
    def __init__(self, *args): self._slots = []
    def connect(self, slot): (self._slots.append(slot) if slot not in self._slots else None)
    def disconnect(self, slot): (self._slots.remove(slot) if slot in self._slots else None)
    def emit(self, *args): [slot(*args) for slot in self._slots]

class QObject:
    def __init__(self, parent=None):
        self._parent, self._children = parent, []
        (parent._children.append(self) if parent and hasattr(parent, '_children') else None)
    def parent(self): return self._parent
    def children(self): return self._children
    def blockSignals(self, b): pass
    def signalsBlocked(self): return False
    def isVisible(self): return False
    def _handle_event(self, event): pass
    def _draw_recursive(self): pass

class QPointF:
    def __init__(self, x=0, y=0):
        if isinstance(x, (QPointF, tuple, list, pygame.Vector2)): self._x, self._y = float(x[0] if isinstance(x, (tuple, list, pygame.Vector2)) else x.x()), float(x[1] if isinstance(x, (tuple, list, pygame.Vector2)) else x.y())
        elif hasattr(x, 'x') and hasattr(x, 'y'): self._x, self._y = x.x(), x.y()
        else: self._x, self._y = float(x), float(y)
    def x(self): return self._x
    def y(self): return self._y
    def setX(self, x): self._x = float(x)
    def setY(self, y): self._y = float(y)
    def __getitem__(self, i): return [self._x, self._y][i]
    def __add__(self, other): return QPointF(self._x + other.x(), self._y + other.y())
    def __sub__(self, other): return QPointF(self._x - other.x(), self._y - other.y())
    def __mul__(self, factor): return QPointF(self._x * factor, self._y * factor)

class QSize:
    def __init__(self, w=0, h=0): self._w, self._h = w, h
    def width(self): return self._w
    def height(self): return self._h

class QRectF:
    def __init__(self, *args):
        if len(args) == 4: self._x, self._y, self._w, self._h = args
        elif len(args) == 2:
            if isinstance(args[0], QPointF) and isinstance(args[1], QPointF): self._x, self._y = args[0].x(), args[0].y(); self._w, self._h = args[1].x() - self._x, args[1].y() - self._y
            elif isinstance(args[0], QPointF) and isinstance(args[1], (int, float, QSize)):
                self._x, self._y = args[0].x(), args[0].y()
                self._w = args[1].width() if isinstance(args[1], QSize) else args[1]
                self._h = args[1].height() if isinstance(args[1], QSize) else args[1]
        elif len(args) == 1:
            if isinstance(args[0], pygame.Rect): self._x, self._y, self._w, self._h = args[0]
            elif isinstance(args[0], QRectF): self._x, self._y, self._w, self._h = args[0]._x, args[0]._y, args[0]._w, args[0]._h
        else: self._x = self._y = self._w = self._h = 0
    def x(self): return self._x
    def y(self): return self._y
    def width(self): return self._w
    def height(self): return self._h
    def topLeft(self): return QPointF(self._x, self._y)
    def bottomRight(self): return QPointF(self._x + self._w, self._y + self._h)
    def center(self): return QPointF(self._x + self._w/2, self._y + self._h/2)
    def normalized(self):
        x, y, w, h = self._x, self._y, self._w, self._h
        if w < 0: x += w; w = abs(w)
        if h < 0: y += h; h = abs(h)
        return QRectF(x, y, w, h)
    def toRect(self): return pygame.Rect(int(self._x), int(self._y), int(self._w), int(self._h))
    def intersected(self, other): return QRectF(self.toRect().clip(other.toRect()))
    def isEmpty(self): return self._w <= 0 or self._h <= 0
    def contains(self, p): return self._x <= p.x() <= self._x + self._w and self._y <= p.y() <= self._y + self._h

class QColor:
    def __init__(self, *args):
        if len(args) == 1:
            if isinstance(args[0], str):
                h = args[0].lstrip('#')
                if len(h) == 6: self.r, self.g, self.b = tuple(int(h[i:i+2], 16) for i in (0, 2, 4)); self.a = 255
                elif len(h) == 8: self.r, self.g, self.b, self.a = tuple(int(h[i:i+2], 16) for i in (0, 2, 4, 6))
                else: self.r = self.g = self.b = self.a = 255
            elif isinstance(args[0], QColor): self.r, self.g, self.b, self.a = args[0].r, args[0].g, args[0].b, args[0].a
            else: self.r = self.g = self.b = self.a = 255
        elif len(args) >= 3: self.r, self.g, self.b = args[:3]; self.a = args[3] if len(args) > 3 else 255
        else: self.r = self.g = self.b = 0; self.a = 255
    def to_pygame(self): return (self.r, self.g, self.b, self.a)

class QFont:
    def __init__(self, family="Arial", size=12): self._family, self._size = family, size
    def setPointSize(self, size): self._size = size
    def pointSize(self): return self._size

class QPixmap:
    def __init__(self, arg=None):
        if isinstance(arg, str): self.surface = pygame.image.load(arg).convert_alpha()
        elif isinstance(arg, pygame.Surface): self.surface = arg
        elif isinstance(arg, QSize): self.surface = pygame.Surface((arg.width(), arg.height()), pygame.SRCALPHA)
        else: self.surface = None
    def width(self): return self.surface.get_width() if self.surface else 0
    def height(self): return self.surface.get_height() if self.surface else 0
    def rect(self): return QRectF(0, 0, self.width(), self.height())
    def scaledToWidth(self, w, mode=None):
        if not self.surface or self.width() == 0: return self
        h = int(self.height() * (w / self.width())); return QPixmap(pygame.transform.smoothscale(self.surface, (w, h)))
    def toImage(self): return QImage()
    def save(self, buffer, fmt): pass

class QImage:
    def __init__(self, *args): pass
    def isNull(self): return True

class QMouseEvent:
    def __init__(self, pos, button=Qt.MouseButton.NoButton, modifiers=Qt.KeyboardModifier.NoModifier):
        self._pos, self._button, self._modifiers = QPointF(pos), button, modifiers
    def pos(self): return self._pos
    def button(self): return self._button
    def modifiers(self): return self._modifiers
    def ignore(self): pass

class QApplication:
    _instance = None
    def __init__(self, args): pygame.init(); QApplication._instance = self; self._windows = []
    def setApplicationName(self, name): pass
    @staticmethod
    def instance(): return QApplication._instance
    @staticmethod
    def clipboard():
        class MockClipboard:
            def mimeData(self):
                class MockMime:
                    def hasImage(self): return False
                    def hasText(self): return False
                    def text(self): return ""
                return MockMime()
            def setMimeData(self, data): pass
            def image(self): return QImage()
        return MockClipboard()
    def exec(self):
        clock = pygame.time.Clock(); running = True
        while running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT: running = False
                for win in self._windows: (win._handle_event(event) if win.isVisible() else None)
            for win in self._windows: (win._draw_recursive() if win.isVisible() else None)
            pygame.display.flip(); clock.tick(60)
        pygame.quit(); return 0

class QWidget(QObject):
    def __init__(self, parent=None):
        super().__init__(parent); self._rect, self._visible, self._layout, self._stylesheet = pygame.Rect(0, 0, 100, 100), True, None, ""
        self._parent, self._children = parent, []
        (parent._children.append(self) if parent and hasattr(parent, '_children') else None)
        self.clicked = Signal()
    def setWindowTitle(self, title): pygame.display.set_caption(title)
    def resize(self, w, h): self._rect.width, self._rect.height = w, h
    def setCentralWidget(self, widget): widget._parent = self
    def setStyleSheet(self, ss): self._stylesheet = ss
    def show(self): self._visible = True
    def hide(self): self._visible = False
    def setVisible(self, v): self._visible = v
    def isVisible(self): return self._visible
    def close(self): self.hide()
    def setLayout(self, layout): self._layout = layout
    def _handle_event(self, event): [child._handle_event(event) for child in self._children if child.isVisible()]
    def _draw_recursive(self):
        if not self.isVisible(): return
        self._draw(); [child._draw_recursive() for child in self._children]
    def _draw(self): pass
    def statusBar(self):
        class MockStatusBar:
            def addWidget(self, w): pass
        return MockStatusBar()
    def setAcceptDrops(self, b): pass
    def addAction(self, action): pass
    def setContextMenuPolicy(self, policy): pass

class QMainWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent); self._screen = None
        (QApplication._instance._windows.append(self) if QApplication._instance else None)
    def setMenuBar(self, menu_bar): pass
    def show(self):
        super().show()
        if not self._screen: self._screen = pygame.display.set_mode((self._rect.width, self._rect.height), pygame.RESIZABLE)
    def _draw(self): (self._screen.fill((240, 240, 240)) if self._screen else None)

class QDialog(QWidget):
    def __init__(self, parent=None): super().__init__(parent)
    def exec(self): self.show(); return 1

class QVBoxLayout:
    def __init__(self, parent=None):
        self.items = []
        if parent and hasattr(parent, 'setLayout'): parent.setLayout(self)
    def addWidget(self, w, alignment=0): self.items.append(w)
    def addLayout(self, l): self.items.append(l)
    def addStretch(self, s=0): pass
    def setContentsMargins(self, *args): pass
    def setSpacing(self, s): pass
class QHBoxLayout:
    def __init__(self, parent=None):
        self.items = []
        if parent and hasattr(parent, 'setLayout'): parent.setLayout(self)
    def addWidget(self, w, alignment=0): self.items.append(w)
    def addLayout(self, l): self.items.append(l)
    def addStretch(self, s=0): pass
    def setContentsMargins(self, *args): pass
    def setSpacing(self, s): pass
class QSplitter(QWidget):
    def __init__(self, orientation=Qt.Orientation.Horizontal, parent=None): super().__init__(parent)
    def addWidget(self, w): pass
    def setSizes(self, sizes): pass
class QFileDialog:
    @staticmethod
    def getOpenFileName(*args): return ("", "")
    @staticmethod
    def getSaveFileName(*args): return ("", "")
class QMessageBox:
    StandardButton = type('StandardButton', (), {'Yes':1, 'No':0})
    @staticmethod
    def information(*args): pass
    @staticmethod
    def warning(*args): pass
    @staticmethod
    def critical(*args): pass
    @staticmethod
    def question(*args): return 0
class QLabel(QWidget):
    def __init__(self, text="", parent=None): super().__init__(parent); self.text = text
    def setText(self, text): self.text = text
class QPushButton(QWidget):
    def __init__(self, text="", parent=None): super().__init__(parent); self.text = text

class QGraphicsScene(QObject):
    selectionChanged = Signal()
    def __init__(self, parent=None):
        super().__init__(parent); self.items_list, self._bg_brush, self._scene_rect = [], None, QRectF(0,0,800,600)
        self._views = []
    def views(self): return self._views
    def addItem(self, item): self.items_list.append(item); item._scene = self
    def removeItem(self, item): (self.items_list.remove(item), setattr(item, '_scene', None)) if item in self.items_list else None
    def items(self): return sorted(self.items_list, key=lambda i: i.zValue())
    def selectedItems(self): return [i for i in self.items_list if i._selected]
    def clearSelection(self): [setattr(i, '_selected', False) for i in self.items_list]; self.selectionChanged.emit()
    def setBackgroundBrush(self, brush): self._bg_brush = brush
    def setSceneRect(self, rect): self._scene_rect = rect
    def mousePressEvent(self, event):
        pos = event.pos(); clicked_item = None
        for item in reversed(self.items()):
            if item.isVisible() and item.sceneBoundingRect().contains(pos): clicked_item = item; break
        if clicked_item:
            if not (event.modifiers() & Qt.KeyboardModifier.ControlModifier): self.clearSelection()
            clicked_item.setSelected(True)
        else: self.clearSelection()

class QGraphicsItem:
    class GraphicsItemFlag: ItemIsMovable = 1; ItemIsSelectable = 2; ItemIsFocusable = 4
    def __init__(self, parent=None):
        self._pos, self._z, self._visible, self._selected, self._scene = QPointF(0, 0), 0, True, False, None
        self._parent, self._opacity, self._transform = parent, 1.0, QTransform()
    def setPos(self, *args): self._pos = QPointF(*args) if len(args) == 2 else QPointF(args[0])
    def pos(self): return self._pos
    def setZValue(self, z): self._z = z
    def zValue(self): return self._z
    def setVisible(self, v): self._visible = v
    def isVisible(self): return self._visible
    def setSelected(self, s): self._selected = s; (self._scene.selectionChanged.emit() if self._scene else None)
    def setFlag(self, f, enabled=True): pass
    def setFlags(self, f): pass
    def flags(self): return 0
    def boundingRect(self): return QRectF(0, 0, 0, 0)
    def scene(self): return self._scene
    def setOpacity(self, o): self._opacity = o
    def opacity(self): return self._opacity
    def transform(self): return self._transform
    def setTransform(self, t, combine=False): self._transform = t
    def scale(self): return 1.0
    def rotation(self): return 0.0
    def setRotation(self, r): pass
    def update(self): pass
    def mapToScene(self, *args): return QPointF(*args) + self._pos
    def mapFromScene(self, *args): return QPointF(*args) - self._pos
    def sceneBoundingRect(self):
        br = self.boundingRect(); return QRectF(self._pos.x() + br.x(), self._pos.y() + br.y(), br.width(), br.height())
    def paint(self, surface, offset): pass
    def mousePressEvent(self, event): pass
    def keyPressEvent(self, event): pass

class QGraphicsRectItem(QGraphicsItem):
    def __init__(self, *args):
        if len(args) > 0 and isinstance(args[0], QGraphicsItem): super().__init__(args[0]); args = args[1:]
        else: super().__init__()
        self._rect = QRectF(*args) if len(args) in (1, 4) else QRectF(0,0,0,0)
    def setRect(self, *args): self._rect = QRectF(*args)
    def rect(self): return self._rect
    def boundingRect(self): return self._rect
    def paint(self, surface, offset):
        r = self._rect.toRect(); r.x += offset.x() + self._pos.x(); r.y += offset.y() + self._pos.y()
        pygame.draw.rect(surface, (0, 0, 255), r, 1)

class QGraphicsPixmapItem(QGraphicsItem):
    class ShapeMode: BoundingRectShape = 1
    def __init__(self, pixmap=None, parent=None):
        super().__init__(parent); self._pixmap = pixmap
    def pixmap(self): return self._pixmap
    def setPixmap(self, p): self._pixmap = p
    def setShapeMode(self, mode): pass
    def boundingRect(self): return self._pixmap.rect() if self._pixmap else QRectF(0,0,0,0)
    def paint(self, surface, offset):
        if self._pixmap and self._pixmap.surface: surface.blit(self._pixmap.surface, (self._pos.x() + offset.x(), self._pos.y() + offset.y()))

class QGraphicsTextItem(QGraphicsItem):
    def __init__(self, text="", parent=None): super().__init__(parent); self._text, self._color, self._font = text, QColor(0,0,0), QFont()
    def toPlainText(self): return self._text
    def setDefaultTextColor(self, c): self._color = c
    def defaultTextColor(self): return self._color
    def setFont(self, f): self._font = f
    def font(self): return self._font
    def setTextInteractionFlags(self, flags): pass
    def textInteractionFlags(self): return 0
    def setFocus(self): pass
    def textCursor(self):
        class MockCursor:
            class SelectionType: Document = 1
            def select(self, t): pass
        return MockCursor()
    def setTextCursor(self, c): pass
    def boundingRect(self): return QRectF(0,0,100,20)
    def paint(self, surface, offset):
        font = pygame.font.SysFont(self._font._family, self._font._size)
        txt = font.render(self._text, True, self._color.to_pygame()); surface.blit(txt, (self._pos.x() + offset.x(), self._pos.y() + offset.y()))

class QGraphicsView(QWidget):
    class DragMode: RubberBandDrag = 1; NoDrag = 0
    class ViewportAnchor: AnchorUnderMouse = 1
    def __init__(self, parent=None):
        super().__init__(parent); self._scene = None; self.sceneChanged = Signal(); self.joinRequested = Signal()
    def setScene(self, scene):
        self._scene = scene
        if scene: scene._views.append(self)
    def viewport(self): return self
    def setCursor(self, cursor): pass
    def scale(self, sx, sy): pass
    def setRenderHint(self, hint, on=True): pass
    def setDragMode(self, mode): pass
    def setTransformationAnchor(self, anchor): pass
    def setResizeAnchor(self, anchor): pass
    def mapToScene(self, p): return QPointF(p.x, p.y)
    def _draw(self):
        screen = QApplication._instance._windows[0]._screen
        if self._scene and screen: [item.paint(screen, self._rect.topleft) for item in self._scene.items() if item.isVisible()]
    def _handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self._scene:
            q_event = QMouseEvent(event.pos, event.button, pygame.key.get_mods()); self._scene.mousePressEvent(q_event)

class QPainter:
    class RenderHint: Antialiasing = 1; SmoothPixmapTransform = 2
    def __init__(self, device=None): pass
    def save(self):
        pass
    def restore(self):
        pass
    def setPen(self, pen):
        pass
    def setBrush(self, brush):
        pass
    def drawRect(self, rect):
        pass

class QPen:
    def __init__(self, *args): pass
class QBrush:
    def __init__(self, *args): pass
class QTransform:
    @staticmethod
    def fromScale(sx, sy): return QTransform()
    def m11(self):
        return 1.0
    def m22(self):
        return 1.0
class QUndoStack(QObject):
    def __init__(self, parent=None): super().__init__(parent)
    def push(self, cmd): cmd.redo()
    def undo(self): pass
    def redo(self): pass
    def beginMacro(self, title): pass
    def endMacro(self): pass
    def redo(self):
        pass
    def beginMacro(self, text):
        pass
    def endMacro(self):
        pass
class QUndoCommand:
    def __init__(self, text=""): pass
    def redo(self):
        pass
    def undo(self):
        pass
class QSettings(QObject):
    def __init__(self, *args): super().__init__()
    def value(self, key, default=None, type=None): return default
    def setValue(self, key, val): pass
class QMenuBar(QWidget):
    def addMenu(self, title):
        m = QMenu(title, self)
        return m
class QMenu(QWidget):
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.title = title
        self.menu_edit = self
    def addAction(self, text):
        return QAction(text)
    def addMenu(self, arg):
        if isinstance(arg, str):
            return QMenu(arg, self)
        return arg
    def clear(self):
        pass
    def addSeparator(self):
        pass
    def exec(self, pos=None):
        return None
class QAction(QObject):
    triggered, toggled = Signal(), Signal(bool)
    def __init__(self, text="", parent=None): super().__init__(parent); self.text = text
    def setShortcut(self, s):
        pass
    def setEnabled(self, e):
        pass
    def setVisible(self, v):
        pass
    def setCheckable(self, b):
        pass
    def setChecked(self, b):
        pass
class QSlider(QWidget):
    valueChanged = Signal(int)
    def __init__(self, orientation=Qt.Orientation.Horizontal, parent=None): super().__init__(parent)
    def setMinimum(self, v): pass
    def setMaximum(self, v): pass
    def setSingleStep(self, v): pass
    def setPageStep(self, v): pass
    def setValue(self, v): pass
    def value(self): return 0
    def setGeometry(self, rect): pass
class QAbstractItemView(QWidget):
    class SelectionMode: SingleSelection = 1; MultiSelection = 2; ExtendedSelection = 3
    class DragDropMode: NoDragDrop = 0; DragOnly = 1; DropOnly = 2; DragDrop = 3; InternalMove = 4
class QHeaderView:
    class ResizeMode: Stretch = 1; ResizeToContents = 2
    def setSectionResizeMode(self, col, mode): pass
class QTreeWidget(QAbstractItemView):
    itemChanged = Signal(object, int)
    itemSelectionChanged = Signal()
    customContextMenuRequested = Signal(object)
    def __init__(self, parent=None):
        super().__init__(parent); self.tree = self
        self._items = []
        self._root = QTreeWidgetItem(self)
        self._header = QHeaderView()
    def clear(self): self._items = []
    def invisibleRootItem(self): return self._root
    def setHeaderLabels(self, labels): pass
    def header(self): return self._header
    def setItemDelegateForColumn(self, col, delegate): pass
    def setContextMenuPolicy(self, p): pass
    def setDragEnabled(self, b): pass
    def setAcceptDrops(self, b): pass
    def setDragDropMode(self, mode): pass
    def setSelectionMode(self, mode): pass
    def topLevelItem(self, i): return self._items[i] if i < len(self._items) else None
    def indexOfTopLevelItem(self, item): return self._items.index(item) if item in self._items else -1
    def takeTopLevelItem(self, i): return self._items.pop(i) if i < len(self._items) else None
    def itemAt(self, pos): return None
class QTreeWidgetItem:
    def __init__(self, parent=None):
        self._parent = parent
        self._children = []
        self._data = {}
        self._text = {}
        if parent and hasattr(parent, 'addChild'): parent.addChild(self)
    def data(self, col, role): return self._data.get((col, role))
    def setData(self, col, role, val): self._data[(col, role)] = val
    def checkState(self, col): return Qt.CheckState.Unchecked
    def setCheckState(self, col, s): pass
    def childCount(self): return len(self._children)
    def child(self, i): return self._children[i]
    def text(self, col): return self._text.get(col, "")
    def setText(self, col, text): self._text[col] = text
    def setFlags(self, f): pass
    def flags(self): return 0
    def setExpanded(self, b): pass
    def isExpanded(self): return False
    def addChild(self, item): self._children.append(item); item._parent = self
    def parent(self): return self._parent if isinstance(self._parent, QTreeWidgetItem) else None
    def removeChild(self, item): (self._children.remove(item) if item in self._children else None)
    def indexOfChild(self, item): return self._children.index(item) if item in self._children else -1
    def insertChild(self, i, item): self._children.insert(i, item); item._parent = self
    def takeChild(self, i): return self._children.pop(i)
class QStyledItemDelegate: pass
class QStyleOptionViewItem: pass
class QStyleOptionViewItem: pass
class QListWidget(QAbstractItemView):
    class ViewMode: IconMode = 1; ListMode = 0
    def __init__(self, parent=None):
        super().__init__(parent)
        self.itemClicked = Signal()
        self._items = []
        class MockModel:
            def __init__(self): self.rowsMoved = Signal()
        self._model = MockModel()
    def setIconSize(self, size): pass
    def setViewMode(self, mode): pass
    def setSelectionMode(self, mode): pass
    def setDragEnabled(self, b): pass
    def setDropIndicatorShown(self, b): pass
    def setDragDropMode(self, mode): pass
    def model(self): return self._model
    def addItem(self, item): self._items.append(item); item._list = self
    def item(self, i): return self._items[i]
    def count(self): return len(self._items)
    def clear(self): self._items = []
class QListWidgetItem:
    def __init__(self, *args):
        self._data = {}
        if len(args) > 1 and isinstance(args[0], QIcon): self.text = args[1]; self.icon = args[0]
        elif len(args) > 0: self.text = args[0]
    def setData(self, role, val): self._data[role] = val
    def data(self, role): return self._data.get(role)
class QTabWidget(QWidget):
    def addTab(self, w, label): pass
class QTextEdit(QWidget):
    def setHtml(self, html): pass
    def setReadOnly(self, b): pass
class QUndoView(QWidget): pass
class QScrollArea(QWidget):
    class Shape: NoFrame = 0
    def setWidget(self, w): pass
    def setWidgetResizable(self, b): pass
    def setFrameShape(self, s): pass
class QBuffer:
    def __init__(self):
        pass
    def open(self, mode):
        pass
    def data(self):
        class MockData:
            def data(self): return b""
        return MockData()
class QIODevice:
    class OpenModeFlag: ReadWrite = 1
class QMimeData:
    def hasImage(self):
        return False
    def hasText(self):
        return False
class QModelIndex: pass
class QPrinter: pass
class QIcon:
    def __init__(self, *args):
        if len(args) > 0: self.pixmap = args[0]
class QKeySequence:
    class StandardKey: Cut = 1; Copy = 2; Paste = 3
    @staticmethod
    def matches(k1, k2): return False
    def __init__(self, *args): pass
class QDrag:
    def __init__(self, *args):
        pass
    def exec(self, *args):
        pass
def pyqtSignal(*args): return Signal(*args)

__all__ = [
    'Qt', 'Signal', 'QObject', 'QApplication', 'QWidget', 'QMainWindow', 'QDialog',
    'QVBoxLayout', 'QHBoxLayout', 'QSplitter', 'QFileDialog', 'QMessageBox',
    'QLabel', 'QPushButton', 'QGraphicsScene', 'QGraphicsItem', 'QGraphicsRectItem',
    'QGraphicsPixmapItem', 'QGraphicsTextItem', 'QGraphicsView', 'QPainter',
    'QPen', 'QBrush', 'QColor', 'QTransform', 'QUndoStack', 'QUndoCommand',
    'QSettings', 'QMenuBar', 'QMenu', 'QAction', 'QSlider', 'QTreeWidget',
    'QTreeWidgetItem', 'QHeaderView', 'QAbstractItemView', 'QStyledItemDelegate',
    'QStyleOptionViewItem', 'QListWidget', 'QListWidgetItem', 'QTabWidget',
    'QTextEdit', 'QUndoView', 'QScrollArea', 'QBuffer', 'QIODevice', 'QMimeData',
    'QModelIndex', 'QPrinter', 'QKeySequence', 'QPointF', 'QRectF', 'QSize',
    'QPixmap', 'QImage', 'QFont', 'QMouseEvent', 'QIcon', 'QDrag'
]
