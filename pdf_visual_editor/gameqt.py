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
    def show(self): pass
    def hide(self): pass
    def setVisible(self, v): pass
    def _handle_event(self, event, offset): pass
    def _draw_recursive(self, pos=pygame.Vector2(0,0)): pass

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
                for win in self._windows:
                    if win.isVisible(): win._handle_event(event, pygame.Vector2(0,0))

            if not self._windows: break
            has_visible = False
            for win in self._windows:
                if win.isVisible():
                    has_visible = True
                    win._draw_recursive(pygame.Vector2(0,0))
            if not has_visible and clock.get_time() > 5000: break
            pygame.display.flip(); clock.tick(60)
        pygame.quit(); return 0

class QWidget(QObject):
    def __init__(self, parent=None):
        super().__init__(parent); self._rect, self._visible, self._layout, self._stylesheet = pygame.Rect(0, 0, 100, 100), False, None, ""
        self._parent, self._children = parent, []
        if parent and hasattr(parent, '_children'): parent._children.append(self)
        self.clicked = Signal()
    def setWindowTitle(self, title):
        if isinstance(self, QMainWindow): pygame.display.set_caption(title)
    def resize(self, w, h): self._rect.width, self._rect.height = w, h
    def setCentralWidget(self, widget):
        widget._set_parent(self); widget.show()
        widget._rect = pygame.Rect(0, 0, self._rect.width, self._rect.height)
    def setStyleSheet(self, ss): self._stylesheet = ss
    def show(self):
        self._visible = True
        for child in self._children:
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
        if parent and hasattr(parent, '_children'): parent._children.append(self)
    def _handle_event(self, event, offset):
        if not self.isVisible(): return
        my_pos = offset + pygame.Vector2(self._rect.topleft)
        for child in reversed(self._children): child._handle_event(event, my_pos)
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_rect = pygame.Rect(my_pos.x, my_pos.y, self._rect.width, self._rect.height)
            if mouse_rect.collidepoint(event.pos):
                local_pos = pygame.Vector2(event.pos) - my_pos
                q_event = QMouseEvent(local_pos, event.button, pygame.key.get_mods())
                if hasattr(self, 'mousePressEvent'): self.mousePressEvent(q_event)
                self.clicked.emit()
    def _draw_recursive(self, offset=pygame.Vector2(0,0)):
        if not self.isVisible(): return
        # Handle layout before calculating my_pos for children
        if self._layout and hasattr(self._layout, 'arrange'): self._layout.arrange(self._rect)
        my_pos = offset + pygame.Vector2(self._rect.topleft)
        self._draw(my_pos)
        for child in self._children: child._draw_recursive(my_pos)
    def _draw(self, pos):
        screen = QApplication._instance._windows[0]._screen
        if screen and self.__class__.__name__ != 'QMainWindow':
            color = (220, 220, 225)
            class_name = self.__class__.__name__
            if "Thumbnail" in class_name: color = (190, 190, 200)
            elif "Inspector" in class_name: color = (200, 200, 210)
            elif "Canvas" in class_name: color = (255, 255, 255)
            elif "Splitter" in class_name: color = (230, 230, 230)
            pygame.draw.rect(screen, color, (pos.x, pos.y, self._rect.width, self._rect.height))
            pygame.draw.rect(screen, (120, 120, 130), (pos.x, pos.y, self._rect.width, self._rect.height), 1)
            if self._rect.width > 50 and self._rect.height > 20:
                font = pygame.font.SysFont(None, 18)
                txt = font.render(class_name, True, (80, 80, 90))
                screen.blit(txt, (pos.x + 4, pos.y + 4))
    def statusBar(self):
        class MockStatusBar:
            def addWidget(self, w): w._set_parent(QApplication._instance._windows[0]); w.show()
        return MockStatusBar()
    def setAcceptDrops(self, b): pass
    def addAction(self, action): pass
    def setContextMenuPolicy(self, policy): pass

class QMainWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent); self._screen = None; self._central_widget = None
        if QApplication._instance: QApplication._instance._windows.append(self)
    def setMenuBar(self, menu_bar): menu_bar._set_parent(self); menu_bar.show()
    def setCentralWidget(self, widget):
        self._central_widget = widget
        widget._set_parent(self); widget.show()
        widget._rect = pygame.Rect(0, 0, self._rect.width, self._rect.height)
    def show(self):
        super().show()
        if not self._screen: self._screen = pygame.display.set_mode((self._rect.width, self._rect.height), pygame.RESIZABLE)
    def _draw(self, pos): (self._screen.fill((230, 230, 235)) if self._screen else None)

class QDialog(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        if not parent and QApplication._instance: QApplication._instance._windows.append(self)
    def exec(self): self.show(); return 1

class QVBoxLayout:
    def __init__(self, parent=None):
        self.items, self._parent = [], parent
        if parent and hasattr(parent, 'setLayout'): parent.setLayout(self)
    def addWidget(self, w, alignment=0):
        self.items.append(w); (w._set_parent(self._parent) if self._parent else None)
    def addLayout(self, l): self.items.append(l); l._parent = self._parent
    def addStretch(self, s=0): pass
    def setContentsMargins(self, *args): pass
    def setSpacing(self, s): pass
    def arrange(self, rect):
        visible_items = [i for i in self.items if getattr(i, 'isVisible', lambda: True)()]
        if not visible_items: return
        h = rect.height / len(visible_items)
        for i, item in enumerate(visible_items):
            r = pygame.Rect(0, i*h, rect.width, h)
            if hasattr(item, '_rect'): item._rect = r
            if hasattr(item, '_layout') and item._layout: item._layout.arrange(r)
            elif hasattr(item, 'arrange'): item.arrange(r)

class QHBoxLayout:
    def __init__(self, parent=None):
        self.items, self._parent = [], parent
        if parent and hasattr(parent, 'setLayout'): parent.setLayout(self)
    def addWidget(self, w, alignment=0):
        self.items.append(w); (w._set_parent(self._parent) if self._parent else None)
    def addLayout(self, l): self.items.append(l); l._parent = self._parent
    def addStretch(self, s=0): pass
    def setContentsMargins(self, *args): pass
    def setSpacing(self, s): pass
    def arrange(self, rect):
        visible_items = [i for i in self.items if getattr(i, 'isVisible', lambda: True)()]
        if not visible_items: return
        w = rect.width / len(visible_items)
        for i, item in enumerate(visible_items):
            r = pygame.Rect(i*w, 0, w, rect.height)
            if hasattr(item, '_rect'): item._rect = r
            if hasattr(item, '_layout') and item._layout: item._layout.arrange(r)
            elif hasattr(item, 'arrange'): item.arrange(r)

class QSplitter(QWidget):
    def __init__(self, orientation=Qt.Orientation.Horizontal, parent=None):
        super().__init__(parent); self._items, self._orientation, self._sizes = [], orientation, None
    def addWidget(self, w): self._items.append(w); w._set_parent(self); w.show()
    def setSizes(self, sizes): self._sizes = sizes
    def _draw_recursive(self, offset=pygame.Vector2(0,0)):
        if not self.isVisible(): return
        visible_items = [i for i in self._items if i.isVisible()]
        if visible_items:
            n = len(visible_items)
            proportions = [self._sizes[self._items.index(i)] for i in visible_items] if self._sizes and len(self._sizes) == len(self._items) else [1]*n
            total = sum(proportions); curr = 0
            for i, item in enumerate(visible_items):
                p = proportions[i] / total
                if self._orientation == Qt.Orientation.Horizontal:
                    w = int(self._rect.width * p)
                    item._rect = pygame.Rect(curr, 0, w, self._rect.height); curr += w
                else:
                    h = int(self._rect.height * p)
                    item._rect = pygame.Rect(0, curr, self._rect.width, h); curr += h
        super()._draw_recursive(offset)

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
    def __init__(self, text="", parent=None): super().__init__(parent); self._text = text
    def setText(self, text): self._text = text
    def text(self): return self._text
    def _draw(self, pos):
        font = pygame.font.SysFont(None, 22)
        txt = font.render(self._text, True, (20, 20, 20))
        screen = QApplication._instance._windows[0]._screen
        if screen: screen.blit(txt, (pos.x + 2, pos.y + 2))

class QPushButton(QWidget):
    def __init__(self, text="", parent=None): super().__init__(parent); self._text = text
    def setText(self, text): self._text = text
    def _draw(self, pos):
        screen = QApplication._instance._windows[0]._screen
        if screen:
            color = (100, 150, 240)
            if pygame.Rect(pos.x, pos.y, self._rect.width, self._rect.height).collidepoint(pygame.mouse.get_pos()): color = (120, 170, 255)
            pygame.draw.rect(screen, color, (pos.x, pos.y, self._rect.width, self._rect.height), border_radius=4)
            pygame.draw.rect(screen, (50, 80, 180), (pos.x, pos.y, self._rect.width, self._rect.height), 1, border_radius=4)
            font = pygame.font.SysFont(None, 18)
            txt = font.render(self._text, True, (255, 255, 255))
            screen.blit(txt, (pos.x + (self._rect.width - txt.get_width())//2, pos.y + (self._rect.height - txt.get_height())//2))

class QGraphicsScene(QObject):
    selectionChanged = Signal()
    def __init__(self, parent=None):
        super().__init__(parent); self.items_list, self._bg_brush, self._scene_rect = [], None, QRectF(0,0,800,600); self._views = []
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
    def __init__(self, pixmap=None, parent=None): super().__init__(parent); self._pixmap = pixmap
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
        if scene: self._scene = scene; scene._views.append(self)
    def viewport(self): return self
    def setRenderHint(self, h, on=True): pass
    def setDragMode(self, m): pass
    def setTransformationAnchor(self, a): pass
    def setResizeAnchor(self, a): pass
    def mapToScene(self, p): return QPointF(p.x, p.y)
    def _draw(self, pos):
        screen = QApplication._instance._windows[0]._screen
        if self._scene and screen:
            pygame.draw.rect(screen, (240, 240, 240), (pos.x, pos.y, self._rect.width, self._rect.height))
            [item.paint(screen, pos) for item in self._scene.items() if item.isVisible()]
    def mousePressEvent(self, ev):
        if self._scene: self._scene.mousePressEvent(ev)

class QPainter:
    class RenderHint: Antialiasing = 1; SmoothPixmapTransform = 2
    def __init__(self, device=None): pass
    def save(self): pass
    def restore(self): pass
    def setPen(self, pen): pass
    def setBrush(self, brush): pass
    def drawRect(self, rect): pass

class QPen:
    def __init__(self, *args): pass
class QBrush:
    def __init__(self, *args): pass
class QTransform:
    @staticmethod
    def fromScale(sx, sy): return QTransform()
    def m11(self): return 1.0
    def m22(self): return 1.0

class QUndoStack(QObject):
    def __init__(self, parent=None): super().__init__(parent)
    def push(self, cmd): cmd.redo()
    def undo(self): pass
    def redo(self): pass
    def beginMacro(self, text): pass
    def endMacro(self): pass

class QUndoCommand:
    def __init__(self, text=""): pass
    def redo(self): pass
    def undo(self): pass

class QSettings(QObject):
    def __init__(self, *args): super().__init__()
    def value(self, key, default=None, type=None): return default
    def setValue(self, key, val): pass

class QMenuBar(QWidget):
    def __init__(self, parent=None): super().__init__(parent); self._menus = []
    def addMenu(self, title): m = QMenu(title, self); self._menus.append(m); return m
    def _draw(self, pos):
        screen = QApplication._instance._windows[0]._screen
        if screen:
            pygame.draw.rect(screen, (240, 240, 240), (pos.x, pos.y, self._rect.width, 30))
            curr_x = pos.x + 10; font = pygame.font.SysFont(None, 16)
            for m in self._menus:
                txt = font.render(m._title, True, (20, 20, 20)); screen.blit(txt, (curr_x, pos.y + 8)); curr_x += txt.get_width() + 20

class QMenu(QWidget):
    def __init__(self, title="", parent=None): super().__init__(parent); self._title, self._actions = title, []
    def addAction(self, text): a = QAction(text, self); self._actions.append(a); return a
    def addMenu(self, arg): return QMenu(arg, self) if isinstance(arg, str) else arg
    def clear(self): self._actions = []
    def addSeparator(self): pass
    def exec(self, pos=None): pass

class QAction(QObject):
    triggered, toggled = Signal(), Signal(bool)
    def __init__(self, text="", parent=None): super().__init__(parent); self.text = text
    def setShortcut(self, s): pass
    def setEnabled(self, e): pass
    def setVisible(self, v): pass
    def setCheckable(self, b): pass
    def setChecked(self, b): pass

class QSlider(QWidget):
    valueChanged = Signal(int)
    def __init__(self, orientation=Qt.Orientation.Horizontal, parent=None):
        super().__init__(parent); self._val, self._min, self._max = 50, 0, 100
    def setRange(self, mi, ma): self._min, self._max = mi, ma
    def setMinimum(self, v): self._min = v
    def setMaximum(self, v): self._max = v
    def setValue(self, v): self._val = v; self.valueChanged.emit(v)
    def value(self): return self._val
    def _draw(self, pos):
        screen = QApplication._instance._windows[0]._screen
        if screen:
            cy = pos.y + self._rect.height // 2
            pygame.draw.line(screen, (150, 150, 150), (pos.x+10, cy), (pos.x+self._rect.width-10, cy), 2)
            r = (self._val - self._min) / (self._max - self._min) if self._max > self._min else 0.5
            pygame.draw.rect(screen, (100, 150, 240), (pos.x + 10 + int((self._rect.width-20)*r)-5, cy-10, 10, 20))
    def mousePressEvent(self, ev):
        if self._rect.width > 20: 
            r = max(0, min(1, (ev.pos().x() - 10) / (self._rect.width - 20)))
            self.setValue(int(self._min + r * (self._max - self._min)))

class QAbstractItemView(QWidget):
    class SelectionMode: SingleSelection = 1; MultiSelection = 2; ExtendedSelection = 3; ContourSelection = 4
    class DragDropMode: NoDragDrop = 0; InternalMove = 4
    def setDragDropMode(self, m): pass
    def setSelectionMode(self, m): pass

class QHeaderView:
    class ResizeMode: Stretch = 1; ResizeToContents = 2; Fixed = 3; Interactive = 0
    def setSectionResizeMode(self, c, m): pass

class QStyledItemDelegate: pass
class QStyleOptionViewItem: pass
class QTreeWidget(QAbstractItemView):
    itemChanged, itemSelectionChanged, customContextMenuRequested = Signal(object, int), Signal(), Signal(object)
    def __init__(self, parent=None):
        super().__init__(parent); self._items, self._header = [], QHeaderView(); self._root = QTreeWidgetItem(self); self.tree = self
    def clear(self): self._items = []
    def invisibleRootItem(self): return self._root
    def header(self): return self._header
    def setHeaderLabels(self, l): pass
    def setItemDelegateForColumn(self, c, d): pass
    def setContextMenuPolicy(self, p): pass
    def setDragEnabled(self, b): pass
    def setAcceptDrops(self, b): pass
    def topLevelItem(self, i): return self._items[i] if i < len(self._items) else None
    def _draw(self, pos):
        super()._draw(pos)
        screen = QApplication._instance._windows[0]._screen
        if screen:
            pygame.draw.rect(screen, (240, 240, 240), (pos.x, pos.y, self._rect.width, 25))
            txt = pygame.font.SysFont(None, 14).render("Element | Type | Vis | Opacity", True, (50, 50, 50))
            screen.blit(txt, (pos.x + 5, pos.y + 5))

class QTreeWidgetItem:
    def __init__(self, parent=None):
        self._parent, self._children, self._data, self._text = parent, [], {}, {}
        if parent and hasattr(parent, 'addChild'): parent.addChild(self)
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
    def setIconSize(self, s): pass
    def setViewMode(self, m): pass
    def setSelectionMode(self, m): pass
    def setDragEnabled(self, b): pass
    def setDropIndicatorShown(self, b): pass
    def setDragDropMode(self, m): pass
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

class QTabWidget(QWidget):
    def addTab(self, w, l): pass
class QTextEdit(QWidget):
    def setHtml(self, h): pass
class QUndoView(QWidget):
    def __init__(self, stack=None, parent=None): super().__init__(parent); self._stack = stack
class QScrollArea(QWidget):
    class Shape: NoFrame = 0
    def setWidget(self, w): pass
    def setWidgetResizable(self, b): pass

class QBuffer:
    def open(self, m): pass
    def data(self): return type('MockData', (), {'data': lambda: b""})()
class QIODevice:
    class OpenModeFlag: ReadWrite = 1
class QMimeData:
    def hasImage(self): return False
class QModelIndex: pass
class QPrinter: pass
class QIcon:
    def __init__(self, *args): (setattr(self, 'pixmap', args[0]) if args else None)
class QKeySequence:
    class StandardKey: Cut = 1; Copy = 2; Paste = 3
    @staticmethod
    def matches(k1, k2): return False
class QDrag:
    def __init__(self, *args): pass
    def exec(self, *args): pass

def pyqtSignal(*args): return Signal(*args)

__all__ = [
    'Qt', 'Signal', 'QObject', 'QApplication', 'QWidget', 'QMainWindow', 'QDialog',
    'QVBoxLayout', 'QHBoxLayout', 'QSplitter', 'QFileDialog', 'QMessageBox',
    'QLabel', 'QPushButton', 'QGraphicsScene', 'QGraphicsItem', 'QGraphicsRectItem',
    'QGraphicsPixmapItem', 'QGraphicsTextItem', 'QGraphicsView', 'QPainter',
    'QPen', 'QBrush', 'QColor', 'QTransform', 'QUndoStack', 'QUndoCommand',
    'QSettings', 'QMenuBar', 'QMenu', 'QAction', 'QSlider', 'QTreeWidget',
    'QTreeWidgetItem', 'QHeaderView', 'QAbstractItemView', 'QStyledItemDelegate',
    'QStyleOptionViewItem', 'QListWidget', 
    'QListWidgetItem', 'QTabWidget', 'QTextEdit', 'QUndoView', 'QScrollArea', 
    'QBuffer', 'QIODevice', 'QMimeData', 'QModelIndex', 'QPrinter', 
    'QKeySequence', 'QPointF', 'QRectF', 'QSize', 'QPixmap', 'QImage', 
    'QFont', 'QMouseEvent', 'QIcon', 'QDrag'
]
