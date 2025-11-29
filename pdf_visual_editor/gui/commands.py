"""
Undo/Redo commands for the PDF Visual Editor.
Each command encapsulates a single operation that can be undone and redone.
"""
from qt_compat import QUndoCommand, QPointF, QGraphicsItem


class MoveItemCommand(QUndoCommand):
    """Command for moving graphics items."""
    
    def __init__(self, item: QGraphicsItem, old_pos: QPointF, new_pos: QPointF):
        super().__init__("Move Item")
        self.item = item
        self.old_pos = old_pos
        self.new_pos = new_pos
    
    def undo(self):
        self.item.setPos(self.old_pos)
    
    def redo(self):
        self.item.setPos(self.new_pos)


class ResizeItemCommand(QUndoCommand):
    """Command for resizing graphics items."""
    
    def __init__(self, item: QGraphicsItem, old_rect, new_rect):
        super().__init__("Resize Item")
        self.item = item
        self.old_rect = old_rect
        self.new_rect = new_rect
    
    def undo(self):
        from qt_compat import QGraphicsRectItem
        if isinstance(self.item, QGraphicsRectItem):
            self.item.setRect(self.old_rect)
    
    def redo(self):
        from PyQt6.QtWidgets import QGraphicsRectItem
        if isinstance(self.item, QGraphicsRectItem):
            self.item.setRect(self.new_rect)


class AddItemCommand(QUndoCommand):
    """Command for adding new items to the scene."""
    
    def __init__(self, scene, item: QGraphicsItem, description: str = "Add Item"):
        super().__init__(description)
        self.scene = scene
        self.item = item
        self.was_added = False
    
    def undo(self):
        if self.item in self.scene.items():
            self.scene.removeItem(self.item)
            self.was_added = False
    
            self.was_added = False
    
    def redo(self):
        if self.item not in self.scene.items():
            self.scene.addItem(self.item)
            self.was_added = True


class DeleteItemCommand(QUndoCommand):
    """Command for deleting items from the scene."""
    
    def __init__(self, scene, items: list):
        super().__init__(f"Delete {len(items)} Item(s)")
        self.scene = scene
        self.items = items
        self.positions = [item.pos() for item in items]
    
    def undo(self):
        for item, pos in zip(self.items, self.positions):
            if item not in self.scene.items():
                self.scene.addItem(item)
                item.setPos(pos)
    
    def redo(self):
        for item in self.items:
            if item in self.scene.items():
                self.scene.removeItem(item)


class EditTextCommand(QUndoCommand):
    """Command for editing text content."""
    
    def __init__(self, text_item, old_text: str, new_text: str):
        super().__init__("Edit Text")
        self.text_item = text_item
        self.old_text = old_text
        self.new_text = new_text
    
    def undo(self):
        self.text_item.setPlainText(self.old_text)
    
    def redo(self):
        self.text_item.setPlainText(self.new_text)


class RotateItemCommand(QUndoCommand):
    """Command for rotating items."""
    
    def __init__(self, item: QGraphicsItem, old_rotation: float, new_rotation: float):
        super().__init__("Rotate Item")
        self.item = item
        self.old_rotation = old_rotation
        self.new_rotation = new_rotation
    
    def undo(self):
        self.item.setRotation(self.old_rotation)
    
    def redo(self):
        self.item.setRotation(self.new_rotation)


class ScaleItemCommand(QUndoCommand):
    """Command for scaling items."""
    
    def __init__(self, item: QGraphicsItem, old_transform, new_transform):
        super().__init__("Scale Item")
        self.item = item
        self.old_transform = old_transform
        self.new_transform = new_transform
    
    def undo(self):
        self.item.setTransform(self.old_transform)
    
    def redo(self):
        self.item.setTransform(self.new_transform)
