from PyQt6.QtWidgets import QGraphicsItem

class SelectionManager:
    """
    Manages selection state of graphics items.
    """
    def __init__(self):
        self.selected_items = []

    def select(self, item: QGraphicsItem, clear_existing: bool = True):
        if clear_existing:
            self.clear_selection()
        
        if item not in self.selected_items:
            item.setSelected(True)
            self.selected_items.append(item)

    def deselect(self, item: QGraphicsItem):
        if item in self.selected_items:
            item.setSelected(False)
            self.selected_items.remove(item)

    def clear_selection(self):
        for item in self.selected_items:
            item.setSelected(False)
        self.selected_items.clear()

    def get_selection(self):
        return self.selected_items
