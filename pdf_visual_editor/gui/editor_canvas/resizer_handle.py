"""
ResizerHandle — draggable handle for resizing QGraphicsItems.
"""

from qt_compat import (QGraphicsRectItem, QGraphicsItem, QBrush, QPen, Qt)


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

    def mousePressEvent(self, event):
        # Capture start state
        if self.parent_item:
            from qt_compat import QGraphicsRectItem
            if isinstance(self.parent_item, QGraphicsRectItem):
                self.start_rect = self.parent_item.rect()
            else:
                self.start_transform = self.parent_item.transform()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        # Delegate to parent's resize handler
        if self.parent_item and hasattr(self.parent_item, 'handle_resize'):
            self.parent_item.handle_resize(self, event.scenePos())

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)

        if not self.parent_item:
            return

        scene = self.parent_item.scene()
        if not scene or not hasattr(scene, 'undo_stack') or not scene.undo_stack:
            return

        from qt_compat import QGraphicsRectItem
        from gui.commands import ResizeItemCommand, ScaleItemCommand

        if isinstance(self.parent_item, QGraphicsRectItem):
            if hasattr(self, 'start_rect') and self.start_rect != self.parent_item.rect():
                cmd = ResizeItemCommand(self.parent_item, self.start_rect, self.parent_item.rect())
                scene.undo_stack.push(cmd)
        else:
            if hasattr(self, 'start_transform') and self.start_transform != self.parent_item.transform():
                cmd = ScaleItemCommand(self.parent_item, self.start_transform, self.parent_item.transform())
                scene.undo_stack.push(cmd)
