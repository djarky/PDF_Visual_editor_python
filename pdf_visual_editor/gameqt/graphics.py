import pygame
from .core import QObject, Signal, QPointF, QRectF, Qt
from .widgets import QWidget
from .gui import QPainter, QTransform, QColor, QFont, QPen, QBrush, QTextCursor
from .application import QApplication

class QGraphicsScene(QObject):
    def __init__(self, parent=None):
        super().__init__(parent); self.selectionChanged = Signal(); self.items_list, self._bg_brush, self._scene_rect = [], None, QRectF(0,0,800,600); self._views = []
        self._focus_item = None
    def focusItem(self): return self._focus_item
    def setFocusItem(self, item): 
        if self._focus_item != item:
            self._focus_item = item
            if item: item.setFocus()
    def views(self): return self._views
    def addItem(self, item): self.items_list.append(item); item._scene = self
    def removeItem(self, item): (self.items_list.remove(item), setattr(item, '_scene', None)) if item in self.items_list else None
    def items(self): return sorted(self.items_list, key=lambda i: i.zValue())
    def selectedItems(self): return [i for i in self.items_list if i._selected]
    def clear(self): self.items_list = []; self.selectionChanged.emit()
    def clearSelection(self): [setattr(i, '_selected', False) for i in self.items_list]; self.selectionChanged.emit()
    def setBackgroundBrush(self, brush): self._bg_brush = brush
    def setSceneRect(self, rect): self._scene_rect = rect
    def mousePressEvent(self, event):
        pos = event.pos(); clicked_item = None
        for item in reversed(self.items()):
            if item.isVisible() and item.sceneBoundingRect().contains(pos): clicked_item = item; break
        
        if clicked_item:
            if not (event.modifiers() & Qt.KeyboardModifier.ControlModifier): self.clearSelection()
            # Defer to item for selection/focus logic
            clicked_item.mousePressEvent(event)
        else:
            self.clearSelection()

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
    def update(self): 
        if self._scene:
            for v in self._scene.views(): v.update()
    def mapToScene(self, *args):
        arg = args[0] if len(args) == 1 else QPointF(*args)
        if isinstance(arg, QRectF):
            return QRectF(arg.x() + self._pos.x(), arg.y() + self._pos.y(), arg.width(), arg.height())
        return QPointF(arg) + self._pos
    def mapFromScene(self, *args):
        arg = args[0] if len(args) == 1 else QPointF(*args)
        if isinstance(arg, QRectF):
            return QRectF(arg.x() - self._pos.x(), arg.y() - self._pos.y(), arg.width(), arg.height())
        return QPointF(arg) - self._pos
    def sceneBoundingRect(self):
        br = self.boundingRect(); return QRectF(self._pos.x() + br.x(), self._pos.y() + br.y(), br.width(), br.height())
    def setCursor(self, cursor): 
        self._cursor = cursor
        # If hovering, we should apply it, but for now we store it
    def setData(self, key, value):
        if not hasattr(self, '_data'): self._data = {}
        self._data[key] = value
    def data(self, key):
        return getattr(self, '_data', {}).get(key)
    def setFocus(self): 
        if self._scene: self._scene._focus_item = self
    def paint(self, painter, option, widget): 
        # Virtual method to be overridden
        pass
    def mousePressEvent(self, event): 
        if self._flags & QGraphicsItem.GraphicsItemFlag.ItemIsSelectable:
            self.setSelected(True)
            event.accept()
        if self._flags & QGraphicsItem.GraphicsItemFlag.ItemIsFocusable:
            self.setFocus()
            event.accept()

    def keyPressEvent(self, event): 
        # Default implementation: ignore, let bubble
        event.ignore()

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
    def paint(self, painter, option, widget):
        painter.save()
        painter.translate(self._pos.x(), self._pos.y())
        # Apply item transform if needed 
        
        painter.setPen(self._pen)
        painter.setBrush(self._brush)
        painter.drawRect(self._rect)
        painter.restore()

class QGraphicsEllipseItem(QGraphicsItem):
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
    def paint(self, painter, option, widget):
        painter.save()
        painter.translate(self._pos.x(), self._pos.y())
        painter.setPen(self._pen)
        painter.setBrush(self._brush)
        painter.drawEllipse(self._rect)
        painter.restore()

class QGraphicsPixmapItem(QGraphicsItem):
    class ShapeMode: BoundingRectShape = 1
    def __init__(self, pixmap=None, parent=None): super().__init__(parent); self._pixmap = pixmap
    def pixmap(self): return self._pixmap
    def setPixmap(self, p): self._pixmap = p
    def setShapeMode(self, mode): 
        self._shape_mode = mode
    def boundingRect(self): return self._pixmap.rect() if self._pixmap else QRectF(0,0,0,0)
    def paint(self, painter, option, widget):
        if self._pixmap:
            painter.save()
            painter.translate(self._pos.x(), self._pos.y())
            painter.drawPixmap(0, 0, self._pixmap)
            painter.restore()

class QGraphicsTextItem(QGraphicsItem):
    def __init__(self, text="", parent=None): 
        super().__init__(parent); self._text, self._color, self._font = text, QColor(0,0,0), QFont()
        self._text_interaction_flags = 0
    def setTextInteractionFlags(self, flags): self._text_interaction_flags = flags
    def textInteractionFlags(self): return self._text_interaction_flags
    def textCursor(self): 
        if not hasattr(self, '_cursor_obj'):
            from .gui import QTextCursor
            self._cursor_obj = QTextCursor()
        return self._cursor_obj
    def setTextCursor(self, cursor): self._cursor_obj = cursor
    def toPlainText(self): return self._text
    def setDefaultTextColor(self, c): self._color = c
    def defaultTextColor(self): return self._color
    def setFont(self, f): self._font = f
    def font(self): return self._font
    def boundingRect(self): return QRectF(0,0,100,20)
    def paint(self, painter, option, widget):
        painter.save()
        painter.translate(self._pos.x(), self._pos.y())
        painter.setFont(self._font)
        painter.setPen(QPen(self._color))
        painter.drawText(0, 0, self._text)
        painter.restore()
        

class QGraphicsView(QWidget):
    class DragMode: RubberBandDrag = 1; NoDrag = 0
    class ViewportAnchor: AnchorUnderMouse = 1
    def __init__(self, parent=None):
        super().__init__(parent); self._scene = None; self.sceneChanged = Signal(); self.joinRequested = Signal()
        self._view_transform = QTransform()
        self._drag_mode = QGraphicsView.DragMode.NoDrag
        self._rubber_band_rect = None
        self._is_panning = False
    def setScene(self, scene):
        if scene: self._scene = scene; scene._views.append(self)
    def viewport(self): return self
    def setRenderHint(self, h, on=True): 
        if not hasattr(self, '_render_hints'): self._render_hints = set()
        if on: self._render_hints.add(h)
        else: self._render_hints.discard(h)
    def setDragMode(self, m): self._drag_mode = m
    def setTransformationAnchor(self, a): self._transformation_anchor = a
    def setResizeAnchor(self, a): self._resize_anchor = a
    def scale(self, sx, sy): self._view_transform.scale(sx, sy)
    def translate(self, dx, dy): self._view_transform.translate(dx, dy)
    def mapToScene(self, p):
        # p is local to widget. 
        # Need to invert transform. 
        tx, ty = self._view_transform._m[6], self._view_transform._m[7]
        sx, sy = self._view_transform._m[0], self._view_transform._m[4]
        return QPointF((p.x() - tx) / sx, (p.y() - ty) / sy)
    def _draw(self, pos):
        screen = self._get_screen()
        if self._scene and screen:
            # Viewport Background
            pygame.draw.rect(screen, (240, 240, 240), (pos.x, pos.y, self._rect.width, self._rect.height))
            
            # Simple clipping to widget area
            old_clip = screen.get_clip()
            screen.set_clip(pygame.Rect(pos.x, pos.y, self._rect.width, self._rect.height))
            
            # Drawing offset includes widget pos AND view transform
            tx, ty = self._view_transform._m[6], self._view_transform._m[7]
            total_offset = QPointF(pos.x + tx, pos.y + ty)
            
            painter = QPainter(screen)
            # Apply view transform: Translate AND Scale (m11, m12, m21, m22, dx, dy)
            m = self._view_transform._m
            painter.setTransform(QTransform(m[0], m[1], m[3], m[4], pos.x + m[6], pos.y + m[7]))
            
            for item in self._scene.items():
                if item.isVisible():
                    item.paint(painter, None, self)
            
            # Draw rubber band
            if self._rubber_band_rect:
                r = self._rubber_band_rect.toRect()._to_pygame()
                r.x += pos.x; r.y += pos.y
                pygame.draw.rect(screen, (0, 120, 215), r, 1)
                overlay = pygame.Surface((r.width, r.height), pygame.SRCALPHA)
                overlay.fill((0, 120, 215, 50))
                screen.blit(overlay, (r.x, r.y))

            screen.set_clip(old_clip)

    def mousePressEvent(self, ev):
        if self._drag_mode == QGraphicsView.DragMode.RubberBandDrag and ev.button() == Qt.MouseButton.LeftButton:
            self._rubber_band_start = ev.pos()
            self._rubber_band_rect = QRectF(ev.pos().x(), ev.pos().y(), 0, 0)
        elif ev.button() == Qt.MouseButton.RightButton: # Right drag to pan
            self._is_panning = True
            self._last_pan_pos = ev.pos()
        
        if self._scene: self._scene.mousePressEvent(ev)

    def mouseMoveEvent(self, ev):
        # Cursor logic
        if self._scene:
            p = self.mapToScene(ev.pos())
            item = next((i for i in reversed(self._scene.items()) if i.isVisible() and i.sceneBoundingRect().contains(p)), None)
            if item and hasattr(item, '_cursor'):
                pygame.mouse.set_cursor(item._cursor)
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        handled = False
        if self._rubber_band_rect:
            x1, y1 = self._rubber_band_start.x(), self._rubber_band_start.y()
            x2, y2 = ev.pos().x(), ev.pos().y()
            self._rubber_band_rect = QRectF(min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))
            handled = True
        elif self._is_panning:
            delta = ev.pos() - self._last_pan_pos
            self.translate(delta.x(), delta.y())
            self._last_pan_pos = ev.pos()
            handled = True
            
        if not handled and self._scene and pygame.mouse.get_pressed()[0]:
             if not hasattr(self, '_last_mouse_pos'):
                 self._last_mouse_pos = ev.pos()
                 return
             
             delta = ev.pos() - self._last_mouse_pos
             # Scale delta? No, items are in scene coords.
             for item in self._scene.selectedItems():
                 if item.flags() & QGraphicsItem.GraphicsItemFlag.ItemIsMovable:
                     item.setPos(item.pos() + delta)
             
             self._last_mouse_pos = ev.pos()
             self.sceneChanged.emit()
             
    def mouseReleaseEvent(self, ev):
        if self._rubber_band_rect:
            # Select items in rect
            p1 = self.mapToScene(self._rubber_band_rect.topLeft())
            p2 = self.mapToScene(self._rubber_band_rect.bottomRight())
            scene_rect = QRectF(p1, p2)
            
            if not (ev.modifiers() & Qt.KeyboardModifier.ControlModifier):
                self._scene.clearSelection()
            
            for item in self._scene.items():
                if item.isVisible() and scene_rect.intersects(item.sceneBoundingRect()):
                    item.setSelected(True)
            
            self._rubber_band_rect = None
        
        self._is_panning = False
        if hasattr(self, '_last_mouse_pos'):
            del self._last_mouse_pos

    def wheelEvent(self, ev):
        # Default behavior: scroll vertically
        delta = ev.angleDelta().y()
        self.translate(0, delta)
        ev.accept()

