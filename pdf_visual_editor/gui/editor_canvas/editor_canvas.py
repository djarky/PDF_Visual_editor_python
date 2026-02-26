"""
EditorCanvas — the central QGraphicsView widget for editing PDF pages.
"""

from qt_compat import (QGraphicsView, QGraphicsPixmapItem, QGraphicsRectItem,
                       QGraphicsTextItem, QGraphicsItem, QMenu, Qt, Signal,
                       QPointF, QRectF, QPainter, QPen, QColor, QBrush,
                       QTransform, QKeySequence, QPixmap, QDrag, QApplication,
                       QMimeData)
from .editor_scene import EditorScene
from .editable_text_item import EditableTextItem
from .resizable_pixmap_item import ResizablePixmapItem


class EditorCanvas(QGraphicsView):
    """
    The central widget for editing PDF pages.
    """
    sceneChanged = Signal()   # Signal to notify when scene content changes
    joinRequested = Signal()  # Signal to request joining items (Ctrl+J)

    def __init__(self, parent=None, undo_stack=None):
        super().__init__(parent)
        self.scene = EditorScene(self, undo_stack=undo_stack)
        self.setScene(self.scene)
        self.undo_stack = undo_stack  # Store undo stack reference

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
        # Set the undo_stack for this scene if it doesn't have one already
        if self.undo_stack and not scene.undo_stack:
            scene.undo_stack = self.undo_stack
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
                return  # Consume event
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

        # Map rect to item coordinates
        item_rect = self.current_page_item.mapFromScene(rect).boundingRect()

        # Get pixmap
        full_pixmap = self.current_page_item.pixmap()

        # Crop
        crop_rect = item_rect.toRect()

        # Intersect with bounds
        crop_rect = crop_rect.intersected(full_pixmap.rect())

        if not crop_rect.isEmpty():
            cropped_pixmap = full_pixmap.copy(crop_rect)

            # Create new item
            item = ResizablePixmapItem(cropped_pixmap)
            item.setPos(rect.topLeft())

            # Use undo command if available
            if self.undo_stack:
                from gui.commands import AddItemCommand
                cmd = AddItemCommand(self.scene, item, "Capture Area")
                self.undo_stack.push(cmd)
            else:
                self.scene.addItem(item)

            # Select it
            self.scene.clearSelection()
            item.setSelected(True)

            # Notify inspector
            self.sceneChanged.emit()

    def load_page_image(self, pixmap):
        self.scene.clear()
        self.current_page_item = QGraphicsPixmapItem(pixmap)
        self.current_page_item.setZValue(-100)  # Background
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

        if self.undo_stack:
            from gui.commands import AddItemCommand
            cmd = AddItemCommand(self.scene, item, "Add Text")
            self.undo_stack.push(cmd)
        else:
            self.scene.addItem(item)
        return item

    def add_rect_element(self, x, y, w, h):
        item = QGraphicsRectItem(x, y, w, h)
        item.setPen(QPen(Qt.GlobalColor.blue))
        item.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsMovable | QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        if self.undo_stack:
            from gui.commands import AddItemCommand
            cmd = AddItemCommand(self.scene, item, "Add Rectangle")
            self.undo_stack.push(cmd)
        else:
            self.scene.addItem(item)
        return item

    def keyPressEvent(self, event):
        if event.matches(QKeySequence.StandardKey.Cut):
            self.cut_selection()
        elif event.matches(QKeySequence.StandardKey.Copy):
            self.copy_selection()
        elif event.matches(QKeySequence.StandardKey.Paste):
            self.paste_from_clipboard()
        elif event.key() == Qt.Key.Key_Delete:
            self.delete_selection()
        elif event.modifiers() & Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_R:
            self.rotate_selection(90)
        elif event.modifiers() & Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_J:
            self.joinRequested.emit()
        else:
            super().keyPressEvent(event)

    def cut_selection(self):
        """Cut selection to clipboard (Copy + Delete)."""
        self.copy_selection()
        self.delete_selection()

    def copy_selection(self):
        items = self.scene.selectedItems()
        if not items:
            return

        clipboard = QApplication.clipboard()
        mime_data = self._create_mime_data(items)
        clipboard.setMimeData(mime_data)

    def paste_from_clipboard(self):
        clipboard = QApplication.clipboard()
        mime_data = clipboard.mimeData()

        if mime_data.hasImage():
            # Handle Image Paste
            image = clipboard.image()
            if not image.isNull():
                pixmap = QPixmap.fromImage(image)

                item = ResizablePixmapItem(pixmap)
                # Center on view
                center = self.mapToScene(self.viewport().rect().center())
                item.setPos(center)

                # Use undo command if available
                if self.undo_stack:
                    from gui.commands import AddItemCommand
                    cmd = AddItemCommand(self.scene, item, "Paste Image")
                    self.undo_stack.push(cmd)
                else:
                    self.scene.addItem(item)

                # Select the new item
                self.scene.clearSelection()
                item.setSelected(True)

                # Notify inspector
                self.sceneChanged.emit()

        elif mime_data.hasText():
            # Handle Text Paste
            text = mime_data.text()
            if text:
                center = self.mapToScene(self.viewport().rect().center())
                item = self.add_text_element(text, center.x(), center.y())

                # Use undo command if available
                if self.undo_stack and item:
                    from gui.commands import AddItemCommand
                    cmd = AddItemCommand(self.scene, item, "Paste Text")
                    self.undo_stack.push(cmd)

                # Select the new item
                if item:
                    self.scene.clearSelection()
                    item.setSelected(True)

                # Notify inspector
                self.sceneChanged.emit()

    def _create_mime_data(self, items):
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
        items = self.scene.selectedItems()
        if not items:
            return

        # Use undo command if available
        if self.undo_stack:
            from gui.commands import DeleteItemCommand
            cmd = DeleteItemCommand(self.scene, items)
            self.undo_stack.push(cmd)
        else:
            for item in items:
                self.scene.removeItem(item)

        # Notify inspector
        self.sceneChanged.emit()

    def rotate_selection(self, angle):
        if not self.scene.selectedItems():
            return

        if self.undo_stack:
            self.undo_stack.beginMacro(f"Rotate {angle}°")

        from gui.commands import RotateItemCommand

        for item in self.scene.selectedItems():
            old_rotation = item.rotation()
            new_rotation = old_rotation + angle

            if self.undo_stack:
                cmd = RotateItemCommand(item, old_rotation, new_rotation)
                self.undo_stack.push(cmd)
            else:
                item.setRotation(new_rotation)

        if self.undo_stack:
            self.undo_stack.endMacro()

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

        cut_action = menu.addAction("Cut")
        copy_action = menu.addAction("Copy")
        paste_action = menu.addAction("Paste")
        menu.addSeparator()
        capture_action = menu.addAction("Capture Area")
        menu.addSeparator()
        delete_action = menu.addAction("Delete")

        # Enable/disable based on selection
        has_selection = bool(self.scene.selectedItems())
        cut_action.setEnabled(has_selection)
        copy_action.setEnabled(has_selection)
        delete_action.setEnabled(has_selection)

        action = menu.exec(event.globalPos())

        if action == cut_action:
            self.cut_selection()
        elif action == copy_action:
            self.copy_selection()
        elif action == paste_action:
            self.paste_from_clipboard()
        elif action == capture_action:
            self.start_capture_mode()
        elif action == delete_action:
            self.delete_selection()
