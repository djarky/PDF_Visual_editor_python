import sys
import os
import pygame

# Ensure gameqt is in path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
if os.path.join(project_root, 'pdf_visual_editor') not in sys.path:
     sys.path.insert(0, os.path.join(project_root, 'pdf_visual_editor'))

from gameqt.application import QApplication
from gameqt.widgets import QMainWindow, QWidget, QLabel, QPushButton, QTextEdit
from gameqt.item_views import QTreeWidget, QTreeWidgetItem
from gameqt.core import Qt, QMimeData, QUrl
from gameqt.gui import QColor
from gameqt.utils import QDrag

class DraggableLabel(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("background-color: #AADDFF; border: 1px solid blue;")
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            drag = QDrag(self)
            mime = QMimeData()
            mime.setText(self.text())
            drag.setMimeData(mime)
            drag.exec()

class DropZone(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setAcceptDrops(True)
        self.setStyleSheet("background-color: #DDFFDD; border: 2px dashed green;")
        
    def dropEvent(self, event):
        if event.mimeData().hasText():
            self.setText(f"Dropped: {event.mimeData().text()}")
            event.accept()

def main():
    app = QApplication(sys.argv)
    win = QMainWindow()
    win.setWindowTitle("GameQt Part 2 Visual Test")
    win.resize(1000, 800)
    
    # Setup Status Bar
    status = win.statusBar()
    status.showMessage("Ready")
    
    perm_btn = QPushButton("PermWidget", win)
    perm_btn.resize(100, 20)
    status.addPermanentWidget(perm_btn)

    central = QWidget()
    win.setCentralWidget(central)

    # 1. Text Selection Test
    lbl1 = QLabel("1. Text Selection (Not fully visual without mouse selection logic implemented yet)", central)
    lbl1.setGeometry(20, 20, 600, 20)
    
    edit = QTextEdit(central)
    edit.setGeometry(20, 50, 300, 100)
    edit.setText("Select me! stored in cursor logic.")
    
    def test_selection():
        cursor = edit.textCursor()
        cursor.setPosition(0)
        cursor.setPosition(10, 1) # Keep anchor
        # Note: selectedText requires document link, checking if supported
        try:
            txt = cursor.selectedText()
            status.showMessage(f"Selection Test: '{txt}'")
        except:
            status.showMessage("Selection Test Failed (No Doc Link?)")
            
    btn_sel = QPushButton("Test Selection Code", central)
    btn_sel.setGeometry(330, 50, 150, 30)
    btn_sel.clicked.connect(test_selection)

    # 2. Tree Scrolling
    lbl2 = QLabel("2. Tree Scrolling", central)
    lbl2.setGeometry(20, 180, 200, 20)
    
    tree = QTreeWidget(central)
    tree.setGeometry(20, 210, 300, 200)
    tree.setHeaderLabels(["Item", "Data"])
    
    items = []
    for i in range(100):
        item = QTreeWidgetItem(tree, [f"Item {i}", f"Val {i}"])
        items.append(item)
        
    def scroll_to_50():
        tree.scrollToItem(items[50])
        items[50].setSelected(True)
        status.showMessage("Scrolled to Item 50")
        
    btn_scroll = QPushButton("Scroll to Item 50", central)
    btn_scroll.setGeometry(330, 210, 150, 30)
    btn_scroll.clicked.connect(scroll_to_50)

    # 3. Drag & Drop
    lbl3 = QLabel("3. Drag & Drop", central)
    lbl3.setGeometry(20, 430, 200, 20)
    
    drag_lbl = DraggableLabel("Drag Me!", central)
    drag_lbl.setGeometry(20, 460, 100, 50)
    
    drop_zone = DropZone("Drop Here", central)
    drop_zone.setGeometry(150, 460, 150, 100)

    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
