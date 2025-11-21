from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsRectItem, QGraphicsTextItem, QGraphicsItem, QMenu
from PyQt6.QtCore import Qt, pyqtSignal, QPointF, QRectF
from PyQt6.QtGui import QPainter, QPen, QColor, QBrush, QMouseEvent, QTransform, QKeySequence, QPixmap, QDrag

class EditorScene(QGraphicsScene):
    itemSelected = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setBackgroundBrush(QBrush(QColor("#e0e0e0")))

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        item = self.itemAt(event.scenePos(), QTransform())
        if item:
            self.itemSelected.emit(item)
        else:
            self.itemSelected.emit(None)

class EditableTextItem(QGraphicsTextItem):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsMovable | 
                      QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
                      QGraphicsItem.GraphicsItemFlag.ItemIsFocusable)
        # Default: No text interaction (just movable)
        self.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        self.is_editing = False

    def mouseDoubleClickEvent(self, event):
        if self.textInteractionFlags() == Qt.TextInteractionFlag.NoTextInteraction:
            self.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
            self.setFocus()
            self.is_editing = True
            # Add visual feedback - highlight border
            self.setDefaultTextColor(QColor(0, 0, 0))  # Reset text color
            # Select all text for easy editing
            cursor = self.textCursor()
            cursor.select(cursor.SelectionType.Document)
            self.setTextCursor(cursor)
            self.update()  # Trigger repaint
        super().mouseDoubleClickEvent(event)

    def focusOutEvent(self, event):
        if self.is_editing:
            self.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
            self.is_editing = False
            # Clear selection cursor
            cursor = self.textCursor()
            cursor.clearSelection()
            self.setTextCursor(cursor)
            self.update()  # Trigger repaint
        super().focusOutEvent(event)

    def keyPressEvent(self, event):
        # If we are in editing mode (interaction flags set), we MUST let the base class handle it.
        if self.textInteractionFlags() & Qt.TextInteractionFlag.TextEditorInteraction:
            super().keyPressEvent(event)
        else:
            # If not editing, ignore key events so they bubble up to the View (for shortcuts like Del, Ctrl+C)
            event.ignore()
    
    def paint(self, painter, option, widget):
        # Draw custom border when in editing mode
        if self.is_editing:
            painter.save()
            pen = QPen(QColor(0, 120, 215), 2, Qt.PenStyle.SolidLine)  # Blue border
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(self.boundingRect().adjusted(1, 1, -1, -1))
            painter.restore()
        # Call parent paint for text rendering
        super().paint(painter, option, widget)


class ResizerHandle(QGraphicsRectItem):
    def __init__(self, parent, cursor_shape, position_func):
        super().__init__(-4, -4, 8, 8, parent)
        self.setBrush(QBrush(Qt.GlobalColor.blue))
        self.setPen(QPen(Qt.GlobalColor.white))
        self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setCursor(cursor_shape)
        self.position_func = position_func
        self.parent_item = parent
        self.update_position()

    def update_position(self):
        if self.parent_item:
            pos = self.position_func(self.parent_item.boundingRect())
            self.setPos(pos)

    def mouseMoveEvent(self, event):
        # Delegate to parent's resize handler
        if self.parent_item and hasattr(self.parent_item, 'handle_resize'):
            self.parent_item.handle_resize(self, event.scenePos())

class ResizableMixin:
    """Mixin to add resize handles to a QGraphicsItem."""
    def __init__(self):
        self.handles = []
        self._create_handles()
        
    def _create_handles(self):
        # Check if we are a QGraphicsItem
        if not isinstance(self, QGraphicsItem):
            return
            
        # Bottom-Right Handle
        h_br = ResizerHandle(self, Qt.CursorShape.SizeFDiagCursor, lambda r: r.bottomRight())
        self.handles.append(h_br)
        
    def handle_resize(self, handle, new_pos):
        # We need to calculate the new scale based on the handle movement.
        # Using mapFromScene is tricky if we are already transformed.
        # Instead, let's calculate the distance from the item's origin (top-left) to the new handle position.
        
        # Current origin in scene coords
        origin_scene = self.mapToScene(0, 0)
        
        # Vector from origin to new handle pos
        diff = new_pos - origin_scene
        
        # We need to project this vector onto the item's local axes to get local width/height
        # But simpler: just use the distance? No, that ignores aspect ratio.
        
        # Let's try mapping the new_pos to the item's coordinate system *without* the scale?
        # No, the item's coordinate system includes the scale.
        
        # Better approach for MVP:
        # 1. Get current local rect
        rect = self.boundingRect()
        current_w = rect.width()
        current_h = rect.height()
        
        # 2. Map new_pos to local coordinates
        local_pos = self.mapFromScene(new_pos)
        new_w = local_pos.x()
        new_h = local_pos.y()
        
        # Avoid collapse
        if new_w < 10: new_w = 10
        if new_h < 10: new_h = 10
        
        if isinstance(self, QGraphicsRectItem):
            self.setRect(0, 0, new_w, new_h)
            
        elif isinstance(self, QGraphicsPixmapItem):
            # For pixmaps, we want to change the *scale* of the item, not the pixmap itself.
            # But mapFromScene takes current scale into account.
            # So if we drag the handle, local_pos should be roughly (width, height) of the unscaled item
            # IF we were just moving it.
            # But we want to CHANGE the scale.
            
            # Let's reset scale to 1 temporarily to calculate new scale? No, flickers.
            
            # Alternative: Calculate scale factor change.
            # If we are at scale S, and local_pos says we are at X, but we want to be at X_new...
            # Actually, for QGraphicsItem, it's often easier to keep the bounding rect fixed (for pixmaps)
            # and just change the scale.
            
            # Let's try this:
            # The handle is at the bottom-right of the *transformed* bounds.
            # We want the new bottom-right to be at `new_pos`.
            
            # Unmap the rotation component of the transform?
            # This is getting complex math-wise.
            
            # SIMPLIFIED APPROACH:
            # Just use the local_pos.x() / width ratio?
            # If we are scaled by 2x, local_pos.x() will be `width`.
            # If we drag it further out, local_pos.x() will be > width.
            # So we can just multiply the current scale by (local_pos.x / width).
            
            base_w = self.pixmap().width()
            base_h = self.pixmap().height()
            
            if base_w > 0 and base_h > 0:
                # Calculate requested new size in local coords
                # Note: mapFromScene handles the rotation, so local_pos is axis-aligned to the item.
                # But it also handles existing scale.
                # So if we are scaled 2x, and base is 100, and we click at 200 visual, local_pos is 100.
                # If we drag to 300 visual, local_pos becomes 150.
                # So we want new scale to be 2x * (150/100) = 3x.
                
                # Current scale factors
                sx = self.transform().m11()
                sy = self.transform().m22()
                # (Ignoring shear/rotation in m11/m22 for a moment, assuming simple scale+rotate)
                # Actually, m11 is not just scale if rotated.
                
                # Let's use the item's scale() method if we only used setScale()?
                # But we used setTransform previously.
                
                # Let's revert to using setScale() and setRotation() separately if possible?
                # It's much easier.
                pass

        elif isinstance(self, QGraphicsTextItem):
            # For text, we want to scale the font size.
            # local_pos.x() is the new width in local coords.
            # If we drag it out, local_pos.x() increases.
            # We can scale the font size proportional to width change.
            
            current_font = self.font()
            # Initial width (approx)
            # We need a reference width.
            pass

    # Redefining handle_resize with a simpler, robust approach:
    # We will use `setScale` for resizing.
    # We assume the item's base geometry (boundingRect) is constant (except for RectItem).
    
    def handle_resize(self, handle, new_pos):
        # Convert new_pos to parent coordinates (scene)
        # We want to find the new scale factor.
        
        # Center of the item in scene coordinates
        center = self.sceneBoundingRect().center() # This changes as we resize!
        # Anchor point: Top-Left of the item.
        # We want to keep Top-Left fixed? Or Center fixed?
        # Usually Top-Left fixed for bottom-right handle.
        
        # Top-Left in scene coords
        tl_scene = self.mapToScene(self.boundingRect().topLeft())
        
        # Vector from TL to new handle pos
        diff = new_pos - tl_scene
        
        # We need to decompose this into the item's local axes (u, v)
        # Unit vectors for item's local axes in scene coords:
        t = self.transform() # Current transform
        # But this includes scale. We want rotation only.
        
        # Let's just use the local_pos approach but be careful.
        local_pos = self.mapFromScene(new_pos)
        
        if isinstance(self, QGraphicsRectItem):
            # For RectItem, we actually change the rect, not the scale.
            self.setRect(0, 0, local_pos.x(), local_pos.y())
            
        elif isinstance(self, QGraphicsPixmapItem):
            # For Pixmap, we change the scale.
            # local_pos is the position in the *current* scaled coordinate system.
            # If we drag out, local_pos x > current width.
            # We want to update scale such that the new bound aligns with new_pos.
            
            # Current effective scale is embedded in the coordinate system.
            # If we just multiply the current transform by (local_x / width), it works!
            
            base_w = self.boundingRect().width()
            base_h = self.boundingRect().height()
            
            if base_w > 1 and base_h > 1:
                scale_x = local_pos.x() / base_w
                scale_y = local_pos.y() / base_h
                
                # Apply this incremental scale to the current transform
                # Note: local_pos is relative to the *current* transform.
                # So if we are at x=100 (visual 200), and drag to visual 220, local_pos is 110.
                # We want to scale by 110/100 = 1.1.
                
                if scale_x > 0.1 and scale_y > 0.1:
                    self.setTransform(QTransform.fromScale(scale_x, scale_y), combine=True)
        
        elif isinstance(self, QGraphicsTextItem):
            # Similar logic for text, scale the whole item
            base_w = self.boundingRect().width()
            base_h = self.boundingRect().height()
            
            if base_w > 1 and base_h > 1:
                scale_x = local_pos.x() / base_w
                scale_y = local_pos.y() / base_h
                
                # Uniform scale for text usually looks better?
                avg_scale = (scale_x + scale_y) / 2
                if avg_scale > 0.1:
                     self.setTransform(QTransform.fromScale(avg_scale, avg_scale), combine=True)

        # Update handles
        for h in self.handles:
            h.update_position()

# Update EditableTextItem to use Mixin
class EditableTextItem(QGraphicsTextItem, ResizableMixin):
    def __init__(self, text, parent=None):
        QGraphicsTextItem.__init__(self, text, parent)
        ResizableMixin.__init__(self)
        self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsMovable | 
                      QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
                      QGraphicsItem.GraphicsItemFlag.ItemIsFocusable)
        self.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        self.is_editing = False
    
    def mouseDoubleClickEvent(self, event):
        if self.textInteractionFlags() == Qt.TextInteractionFlag.NoTextInteraction:
            self.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
            self.setFocus()
            self.is_editing = True
            self.setDefaultTextColor(QColor(0, 0, 0))
            cursor = self.textCursor()
            cursor.select(cursor.SelectionType.Document)
            self.setTextCursor(cursor)
            self.update()
        super().mouseDoubleClickEvent(event)

    def focusOutEvent(self, event):
        if self.is_editing:
            self.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
            self.is_editing = False
            cursor = self.textCursor()
            cursor.clearSelection()
            self.setTextCursor(cursor)
            self.update()
        super().focusOutEvent(event)

    def keyPressEvent(self, event):
        if self.textInteractionFlags() & Qt.TextInteractionFlag.TextEditorInteraction:
            super().keyPressEvent(event)
        else:
            event.ignore()
    
    def paint(self, painter, option, widget):
        if self.is_editing:
            painter.save()
            pen = QPen(QColor(0, 120, 215), 2, Qt.PenStyle.SolidLine)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(self.boundingRect().adjusted(1, 1, -1, -1))
            painter.restore()
        super().paint(painter, option, widget)


# We also need a ResizablePixmapItem
class ResizablePixmapItem(QGraphicsPixmapItem, ResizableMixin):
    def __init__(self, pixmap, parent=None):
        QGraphicsPixmapItem.__init__(self, pixmap, parent)
        ResizableMixin.__init__(self)
        self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsMovable | 
                      QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setShapeMode(QGraphicsPixmapItem.ShapeMode.BoundingRectShape)

class EditorCanvas(QGraphicsView):
    """
    The central widget for editing PDF pages.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = EditorScene(self)
        self.setScene(self.scene)
        
        # Graphics View settings
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        
        self.current_page_item = None
        
        # Capture Mode State
        self.capture_mode = False
        self.capture_start_pos = None
        self.capture_rect_item = None

    def set_scene(self, scene):
        self.scene = scene
        self.setScene(self.scene)

    def start_capture_mode(self):
        self.capture_mode = True
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.viewport().setCursor(Qt.CursorShape.CrossCursor)

    def mousePressEvent(self, event):
        if self.capture_mode:
            if event.button() == Qt.MouseButton.LeftButton:
                self.capture_start_pos = self.mapToScene(event.pos())
                self.capture_rect_item = QGraphicsRectItem()
                self.capture_rect_item.setPen(QPen(Qt.GlobalColor.red, 2, Qt.PenStyle.DashLine))
                self.capture_rect_item.setBrush(QBrush(QColor(255, 0, 0, 50)))
                self.scene.addItem(self.capture_rect_item)
                self.capture_rect_item.setRect(QRectF(self.capture_start_pos, self.capture_start_pos))
                return # Consume event
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.capture_mode and self.capture_start_pos:
            current_pos = self.mapToScene(event.pos())
            rect = QRectF(self.capture_start_pos, current_pos).normalized()
            if self.capture_rect_item:
                self.capture_rect_item.setRect(rect)
            return

        # Handle Drag Export (Alt + Drag)
        if event.buttons() & Qt.MouseButton.LeftButton and event.modifiers() & Qt.KeyboardModifier.AltModifier:
            items = self.scene.selectedItems()
            if items:
                drag = QDrag(self)
                mime_data = self._create_mime_data(items)
                drag.setMimeData(mime_data)
                
                # Set drag pixmap (optional but nice)
                if len(items) == 1 and isinstance(items[0], QGraphicsPixmapItem):
                    pixmap = items[0].pixmap()
                    if pixmap.width() > 200:
                         pixmap = pixmap.scaledToWidth(200, Qt.TransformationMode.SmoothTransformation)
                    drag.setPixmap(pixmap)
                    drag.setHotSpot(pixmap.rect().center())
                
                drag.exec(Qt.DropAction.CopyAction)
                return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.capture_mode and self.capture_start_pos:
            if event.button() == Qt.MouseButton.LeftButton:
                # Finalize capture
                rect = self.capture_rect_item.rect()
                self.scene.removeItem(self.capture_rect_item)
                self.capture_rect_item = None
                self.capture_start_pos = None
                self.capture_mode = False
                self.viewport().setCursor(Qt.CursorShape.ArrowCursor)
                self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
                
                # Perform Capture
                if rect.width() > 5 and rect.height() > 5:
                    self.capture_area(rect)
                return
        super().mouseReleaseEvent(event)

    def capture_area(self, rect):
        # Capture from the current page background (original PDF)
        if not self.current_page_item:
            return
            
        # The rect is in scene coordinates.
        # The current_page_item is at (0,0) usually, but let's map just in case.
        # Actually, current_page_item is the background pixmap.
        
        # Map rect to item coordinates
        item_rect = self.current_page_item.mapFromScene(rect).boundingRect()
        
        # Get pixmap
        full_pixmap = self.current_page_item.pixmap()
        
        # Crop
        # We need to convert QRectF to QRect for copy()
        crop_rect = item_rect.toRect()
        
        # Intersect with bounds
        crop_rect = crop_rect.intersected(full_pixmap.rect())
        
        if not crop_rect.isEmpty():
            cropped_pixmap = full_pixmap.copy(crop_rect)
            
            # Create new item
            item = ResizablePixmapItem(cropped_pixmap)
            item.setPos(rect.topLeft())
            self.scene.addItem(item)
            
            # Select it
            self.scene.clearSelection()
            item.setSelected(True)

    def load_page_image(self, pixmap):
        self.scene.clear()
        self.current_page_item = QGraphicsPixmapItem(pixmap)
        self.current_page_item.setZValue(-100) # Background
        self.current_page_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
        self.current_page_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        self.scene.addItem(self.current_page_item)
        self.setSceneRect(QRectF(pixmap.rect()))

    def add_text_element(self, text, x, y, font_size=12):
        item = EditableTextItem(text)
        item.setPos(x, y)
        
        # Scale based on font size (approximate)
        font = item.font()
        font.setPointSize(int(font_size))
        item.setFont(font)
        
        self.scene.addItem(item)
        return item

    def add_rect_element(self, x, y, w, h):
        item = QGraphicsRectItem(x, y, w, h)
        item.setPen(QPen(Qt.GlobalColor.blue))
        item.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsMovable | QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.scene.addItem(item)
        return item

    def keyPressEvent(self, event):
        if event.matches(QKeySequence.StandardKey.Copy):
            self.copy_selection()
        elif event.matches(QKeySequence.StandardKey.Paste):
            self.paste_from_clipboard()
        elif event.key() == Qt.Key.Key_Delete:
            self.delete_selection()
        elif event.modifiers() & Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_R:
            self.rotate_selection(90)
        else:
            super().keyPressEvent(event)

    def copy_selection(self):
        items = self.scene.selectedItems()
        if not items:
            return
            
        from PyQt6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        mime_data = self._create_mime_data(items)
        clipboard.setMimeData(mime_data)

    def paste_from_clipboard(self):
        from PyQt6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        mime_data = clipboard.mimeData()
        
        if mime_data.hasImage():
            # Handle Image Paste
            image = clipboard.image()
            if not image.isNull():
                pixmap = QPixmap.fromImage(image)
                # Add to canvas
                # We need to import ResizablePixmapItem here to avoid circular import at top level if not careful,
                # but we can assume it's available or use the class defined in this file if we moved it?
                # Actually ResizablePixmapItem is defined in this file now (or should be).
                # Wait, ResizablePixmapItem is defined in this file.
                
                item = ResizablePixmapItem(pixmap)
                # Center on view
                center = self.mapToScene(self.viewport().rect().center())
                item.setPos(center)
                self.scene.addItem(item)
                
        elif mime_data.hasText():
            # Handle Text Paste
            text = mime_data.text()
            if text:
                center = self.mapToScene(self.viewport().rect().center())
                self.add_text_element(text, center.x(), center.y())
            
    def _create_mime_data(self, items):
        from PyQt6.QtCore import QMimeData
        mime = QMimeData()
        
        # If single image selected, copy as image
        if len(items) == 1 and isinstance(items[0], QGraphicsPixmapItem):
            mime.setImageData(items[0].pixmap().toImage())
            
        # Also set text representation if possible
        text_parts = []
        for item in items:
            if isinstance(item, QGraphicsTextItem):
                text_parts.append(item.toPlainText())
        
        if text_parts:
            mime.setText("\n".join(text_parts))
            
        return mime

    def delete_selection(self):
        for item in self.scene.selectedItems():
            self.scene.removeItem(item)

    def rotate_selection(self, angle):
        for item in self.scene.selectedItems():
            # Rotate around center
            rect = item.boundingRect()
            center = rect.center()
            transform = item.transform()
            transform.translate(center.x(), center.y())
            transform.rotate(angle)
            transform.translate(-center.x(), -center.y())
            item.setTransform(transform)

    def wheelEvent(self, event):
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            zoom_in = event.angleDelta().y() > 0
            scale_factor = 1.15 if zoom_in else 1 / 1.15
            self.scale(scale_factor, scale_factor)
        else:
            super().wheelEvent(event)

    def contextMenuEvent(self, event):
        """Show context menu on right-click."""
        menu = QMenu(self)
        
        copy_action = menu.addAction("Copy")
        paste_action = menu.addAction("Paste")
        menu.addSeparator()
        capture_action = menu.addAction("Capture Area")
        menu.addSeparator()
        delete_action = menu.addAction("Delete")
        
        # Enable/disable based on selection
        has_selection = bool(self.scene.selectedItems())
        copy_action.setEnabled(has_selection)
        delete_action.setEnabled(has_selection)
        
        action = menu.exec(event.globalPos())
        
        if action == copy_action:
            self.copy_selection()
        elif action == paste_action:
            self.paste_from_clipboard()
        elif action == capture_action:
            self.start_capture_mode()
        elif action == delete_action:
            self.delete_selection()
