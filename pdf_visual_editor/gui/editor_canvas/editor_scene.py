"""
EditorScene — QGraphicsScene subclass with undo support for item moves.
"""

from qt_compat import (QGraphicsScene, QGraphicsItem, QBrush, QColor, Signal)


class EditorScene(QGraphicsScene):
    itemSelected = Signal(object)

    def __init__(self, parent=None, undo_stack=None):
        super().__init__(parent)
        self.setBackgroundBrush(QBrush(QColor("#e0e0e0")))
        self.undo_stack = undo_stack
        self.item_move_start_pos = {}  # Track initial positions for undo

    def mousePressEvent(self, event):
        super().mousePressEvent(event)

        # Track initial positions of all selected items
        # We do this AFTER super() so that selection is updated
        self.item_move_start_pos.clear()
        for item in self.selectedItems():
            if item.flags() & QGraphicsItem.GraphicsItemFlag.ItemIsMovable:
                self.item_move_start_pos[item] = item.pos()

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)

        # Check for completed moves and create undo command
        # Fallback: Try to get undo_stack from view if missing
        stack = self.undo_stack
        if stack is None and self.views():
            view = self.views()[0]
            if hasattr(view, 'undo_stack'):
                stack = view.undo_stack

        if stack is not None and self.item_move_start_pos:
            moved_items = []
            for item, old_pos in self.item_move_start_pos.items():
                new_pos = item.pos()
                if old_pos != new_pos:
                    moved_items.append((item, old_pos, new_pos))

            if moved_items:
                if len(moved_items) > 1:
                    stack.beginMacro("Move Items")

                from gui.commands import MoveItemCommand
                for item, old_pos, new_pos in moved_items:
                    cmd = MoveItemCommand(item, old_pos, new_pos)
                    stack.push(cmd)

                if len(moved_items) > 1:
                    stack.endMacro()

        # Clear tracking
        self.item_move_start_pos.clear()
