import pygame
from .core import QObject, Signal, QPointF, QRectF, Qt
from .widgets import QWidget
from .gui import QTransform, QColor, QFont, QPen, QBrush, QTextCursor
from .application import QApplication

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
        self._flags = 0
        self._rotation = 0.0
    def setPos(self, *args): self._pos = QPointF(*args) if len(args) == 2 else QPointF(args[0])
    def pos(self): return self._pos
    def setZValue(self, z): self._z = z
    def zValue(self): return self._z
    def setVisible(self, v): self._visible = v
    def isVisible(self): return self._visible
    def setSelected(self, s): self._selected = s; (self._scene.selectionChanged.emit() if self._scene else None)
    def setFlag(self, f, enabled=True):
        if enabled: self._flags |= f
        else: self._flags &= ~f
    def setFlags(self, f): self._flags = f
    def flags(self): return self._flags
    def boundingRect(self): return QRectF(0, 0, 0, 0)
    def scene(self): return self._scene
    def setOpacity(self, o): self._opacity = o
    def opacity(self): return self._opacity
    def transform(self): return self._transform
    def setTransform(self, t, combine=False): self._transform = t
    def scale(self): return 1.0
    def rotation(self): return self._rotation
    def setRotation(self, r): self._rotation = r
    def update(self): pass
    def mapToScene(self, *args): return QPointF(*args) + self._pos
    def mapFromScene(self, *args): return QPointF(*args) - self._pos
    def sceneBoundingRect(self):
        br = self.boundingRect(); return QRectF(self._pos.x() + br.x(), self._pos.y() + br.y(), br.width(), br.height())
    def setCursor(self, cursor): pass
    def setFocus(self): pass
    def paint(self, surface, offset): pass
    def mousePressEvent(self, event): pass
    def keyPressEvent(self, event): pass

class QGraphicsRectItem(QGraphicsItem):
    def __init__(self, *args):
        if len(args) > 0 and isinstance(args[0], QGraphicsItem): super().__init__(args[0]); args = args[1:]
        else: super().__init__()
        self._rect = QRectF(*args) if len(args) in (1, 4) else QRectF(0,0,0,0)
        self._pen = QPen(QColor(0,0,0))
        self._brush = QBrush()

    def setPen(self, pen): self._pen = pen
    def setBrush(self, brush): self._brush = brush
    def setRect(self, *args): self._rect = QRectF(*args)

    def rect(self): return self._rect
    def boundingRect(self): return self._rect
    def paint(self, surface, offset):
        r = self._rect.toRect(); r.x += offset.x() + self._pos.x(); r.y += offset.y() + self._pos.y()
        
        # Fill
        if self._brush._style > 0:
            color = self._brush._color.to_pygame()
            pygame.draw.rect(surface, color, r)
        
        # Border
        if self._pen._style > 0:
            color = self._pen._color.to_pygame()
            width = self._pen._width
            pygame.draw.rect(surface, color, r, width)

class QGraphicsPixmapItem(QGraphicsItem):
    class ShapeMode: BoundingRectShape = 1
    def __init__(self, pixmap=None, parent=None): super().__init__(parent); self._pixmap = pixmap
    def pixmap(self): return self._pixmap
    def setPixmap(self, p): self._pixmap = p
    def setShapeMode(self, mode): 
        self._shape_mode = mode
    def boundingRect(self): return self._pixmap.rect() if self._pixmap else QRectF(0,0,0,0)
    def paint(self, surface, offset):
        if self._pixmap and self._pixmap.surface: surface.blit(self._pixmap.surface, (self._pos.x() + offset.x(), self._pos.y() + offset.y()))

class QGraphicsTextItem(QGraphicsItem):
    def __init__(self, text="", parent=None): 
        super().__init__(parent); self._text, self._color, self._font = text, QColor(0,0,0), QFont()
        self._text_interaction_flags = 0
    def setTextInteractionFlags(self, flags): self._text_interaction_flags = flags
    def textInteractionFlags(self): return self._text_interaction_flags
    def textCursor(self): return QTextCursor()
    def setTextCursor(self, cursor): pass
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
    def setRenderHint(self, h, on=True): 
        if not hasattr(self, '_render_hints'):
            self._render_hints = set()
        if on:
            self._render_hints.add(h)
        else:
            self._render_hints.discard(h)
    def setDragMode(self, m): 
        self._drag_mode = m
    def setTransformationAnchor(self, a): 
        self._transformation_anchor = a
    def setResizeAnchor(self, a): 
        self._resize_anchor = a
    def mapToScene(self, p): return QPointF(p.x, p.y)
    def _draw(self, pos):
        if not QApplication._instance or not QApplication._instance._windows: return
        screen = QApplication._instance._windows[0]._screen
        if self._scene and screen:
            pygame.draw.rect(screen, (240, 240, 240), (pos.x, pos.y, self._rect.width, self._rect.height))
            [item.paint(screen, pos) for item in self._scene.items() if item.isVisible()]
    def mousePressEvent(self, ev):
        if self._scene: self._scene.mousePressEvent(ev)
    def mouseMoveEvent(self, ev):
        pass  # Override in subclasses if needed
    def mouseReleaseEvent(self, ev):
        pass  # Override in subclasses if needed
