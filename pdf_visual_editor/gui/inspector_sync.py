"""
InspectorSyncMixin — sincronización bidireccional inspector ↔ canvas.

Extraído de MainWindow para mantener una sola responsabilidad por archivo.
Se usa como mixin: class MainWindow(QMainWindow, ..., InspectorSyncMixin)
"""

from qt_compat import (Qt, QTreeWidgetItem, QGraphicsTextItem,
                       QGraphicsPixmapItem, QGraphicsRectItem,
                       QGraphicsItem, QPointF)


class InspectorSyncMixin:
    """Mixin que añade a MainWindow la sincronización entre inspector y canvas."""

    # ------------------------------------------------------------------
    # Background opacity
    # ------------------------------------------------------------------

    def update_background_opacity(self, opacity):
        """Update the opacity of the current page background."""
        if hasattr(self.canvas, 'current_page_item') and self.canvas.current_page_item:
            self.canvas.current_page_item.setOpacity(opacity)

    # ------------------------------------------------------------------
    # Duplicate items
    # ------------------------------------------------------------------

    def duplicate_items(self, items):
        """Duplicate the specified graphics items."""
        if not self.canvas or not self.canvas.scene:
            return

        from .editor_canvas import EditableTextItem, ResizablePixmapItem

        # Block signals to prevent full inspector rebuild (preserves custom folders)
        self.canvas.blockSignals(True)

        new_items = []
        offset = 20

        try:
            for item in items:
                new_item = None

                if isinstance(item, QGraphicsTextItem):
                    new_item = EditableTextItem(item.toPlainText())
                    new_item.setFont(item.font())
                    new_item.setDefaultTextColor(item.defaultTextColor())
                elif isinstance(item, QGraphicsPixmapItem):
                    new_item = ResizablePixmapItem(item.pixmap())
                elif isinstance(item, QGraphicsRectItem):
                    new_item = QGraphicsRectItem(item.rect())
                    new_item.setPen(item.pen())
                    new_item.setBrush(item.brush())
                    new_item.setFlags(
                        QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
                        QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
                    )

                if new_item:
                    new_item.setPos(item.pos() + QPointF(offset, offset))
                    new_item.setTransform(item.transform())
                    new_item.setRotation(item.rotation())
                    new_item.setScale(item.scale())
                    new_item.setOpacity(item.opacity())
                    new_item.setZValue(item.zValue() + 0.1)
                    new_item.setVisible(item.isVisible())

                    self.canvas.scene.addItem(new_item)
                    new_items.append(new_item)

                    # Manually add to inspector
                    self.inspector_panel.add_graphics_item(new_item)

            if new_items:
                self.canvas.scene.clearSelection()
                for item in new_items:
                    item.setSelected(True)

        finally:
            self.canvas.blockSignals(False)
            # Do NOT call populate_inspector_from_scene_auto here to preserve structure

    # ------------------------------------------------------------------
    # Selection sync: canvas → inspector
    # ------------------------------------------------------------------

    def sync_selection_to_inspector(self):
        """Syncs canvas selection to inspector tree."""
        if self.inspector_panel.tree.signalsBlocked():
            return

        selected_items = self.canvas.scene.selectedItems()

        self.inspector_panel.tree.blockSignals(True)
        self.inspector_panel.tree.clearSelection()

        if not selected_items:
            self.inspector_panel.tree.blockSignals(False)
            return

        def select_recursive(parent_item):
            for i in range(parent_item.childCount()):
                child = parent_item.child(i)
                graphics_item = child.data(0, Qt.ItemDataRole.UserRole + 1)
                if graphics_item in selected_items:
                    child.setSelected(True)
                    self.inspector_panel.tree.scrollToItem(child)
                select_recursive(child)

        root = self.inspector_panel.tree.invisibleRootItem()
        select_recursive(root)

        self.inspector_panel.tree.blockSignals(False)

    # ------------------------------------------------------------------
    # Selection sync: inspector → canvas
    # ------------------------------------------------------------------

    def sync_selection_to_canvas(self):
        """Syncs inspector tree selection to canvas."""
        if self.canvas.scene.signalsBlocked():
            return

        selected_tree_items = self.inspector_panel.tree.selectedItems()

        self.canvas.scene.blockSignals(True)
        self.canvas.scene.clearSelection()

        for tree_item in selected_tree_items:
            graphics_item = tree_item.data(0, Qt.ItemDataRole.UserRole + 1)
            if graphics_item:
                graphics_item.setSelected(True)

        self.canvas.scene.blockSignals(False)

    # ------------------------------------------------------------------
    # Populate inspector from scene
    # ------------------------------------------------------------------

    def populate_inspector_from_scene_auto(self, scene):
        """Populate inspector with auto-organization (for PDF imports)."""
        self.inspector_panel.populate_from_scene_auto_organize(scene)

    def populate_inspector_from_scene(self, scene):
        """Populate inspector by traversing scene items directly."""
        from .editor_canvas import ResizerHandle

        self.inspector_panel.clear()

        root = QTreeWidgetItem(self.inspector_panel.tree)
        root.setText(0, "Page Content")
        root.setExpanded(True)

        for item in scene.items():
            if item.zValue() == -100:
                continue  # Skip background
            if isinstance(item, ResizerHandle):
                continue

            tree_item = QTreeWidgetItem(root)

            if isinstance(item, QGraphicsTextItem):
                text = item.toPlainText()
                tree_item.setText(0, text[:20])
                tree_item.setText(1, "text")
            elif isinstance(item, QGraphicsPixmapItem):
                tree_item.setText(0, "Image")
                tree_item.setText(1, "image")
            else:
                tree_item.setText(0, "Element")
                tree_item.setText(1, "rect")

            tree_item.setCheckState(2, Qt.CheckState.Checked if item.isVisible() else Qt.CheckState.Unchecked)
            tree_item.setText(3, str(item.opacity()))
            tree_item.setFlags(tree_item.flags() | Qt.ItemFlag.ItemIsEditable)

            # Link back to graphics item
            tree_item.setData(0, Qt.ItemDataRole.UserRole + 1, item)

    def _link_item_to_inspector(self, index, graphics_item):
        # Deprecated by populate_inspector_from_scene
        pass

    # ------------------------------------------------------------------
    # Inspector item changed (visibility / opacity)
    # ------------------------------------------------------------------

    def on_inspector_item_changed(self, item, column):
        # Handle visibility change (Column 2)
        if column == 2:
            visible = item.checkState(2) == Qt.CheckState.Checked
            graphics_item = item.data(0, Qt.ItemDataRole.UserRole + 1)
            if graphics_item:
                graphics_item.setVisible(visible)
        # Handle Opacity change (Column 3)
        elif column == 3:
            try:
                opacity = float(item.text(3))
                graphics_item = item.data(0, Qt.ItemDataRole.UserRole + 1)
                if graphics_item:
                    graphics_item.setOpacity(opacity)
            except ValueError:
                pass  # Invalid float
