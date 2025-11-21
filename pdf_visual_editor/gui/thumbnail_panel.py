from PyQt6.QtWidgets import QListWidget, QListWidgetItem, QWidget, QVBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QIcon

class ThumbnailPanel(QWidget):
    """
    Panel showing thumbnails of PDF pages.
    """
    pageSelected = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        
        self.list_widget = QListWidget()
        self.list_widget.setIconSize(QSize(100, 140))
        self.list_widget.setViewMode(QListWidget.ViewMode.IconMode)
        self.list_widget.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.list_widget.setDragEnabled(True)
        self.list_widget.setAcceptDrops(True)
        self.list_widget.setDropIndicatorShown(True)
        self.list_widget.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        
        self.list_widget.itemClicked.connect(self._on_item_clicked)
        # Connect model signal to detect reordering
        self.list_widget.model().rowsMoved.connect(self._on_rows_moved)
        
        layout.addWidget(self.list_widget)

    def add_page(self, pixmap, page_num):
        icon = QIcon(pixmap)
        item = QListWidgetItem(icon, f"Page {page_num + 1}")
        item.setData(Qt.ItemDataRole.UserRole, page_num)
        self.list_widget.addItem(item)

    def _on_item_clicked(self, item):
        # When clicked, we might want to reload the page, 
        # but be careful if the item data (page_num) is stale after reorder.
        # For now, we rely on the stored page_num which represents the ORIGINAL page index.
        page_num = item.data(Qt.ItemDataRole.UserRole)
        self.pageSelected.emit(page_num)

    def _on_rows_moved(self, parent, start, end, destination, row):
        # Reordering happened. 
        # We need to update the MainWindow's knowledge of page order if we want to save it correctly.
        # For now, we just let the visual list change. 
        # The exporter will need to query this list order.
        pass

    def get_page_order(self):
        """Returns a list of original page indices in their new order."""
        order = []
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            order.append(item.data(Qt.ItemDataRole.UserRole))
        return order

    def clear(self):
        self.list_widget.clear()
