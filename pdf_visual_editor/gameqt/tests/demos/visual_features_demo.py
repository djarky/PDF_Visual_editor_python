import sys
import os

# Ensure gameqt is in path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if os.path.join(project_root, 'pdf_visual_editor') not in sys.path:
     sys.path.insert(0, os.path.join(project_root, 'pdf_visual_editor'))

from gameqt.application import QApplication
from gameqt.widgets import (QMainWindow, QWidget, QLabel, QLineEdit, 
                             QPushButton)
from gameqt.layouts import QVBoxLayout, QHBoxLayout
from gameqt.item_views import QTreeWidget, QTreeWidgetItem, QHeaderView

class VisualFeaturesDemo(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GameQt Visual Features Demo")
        self.resize(600, 500)
        
        central = QWidget()
        layout = QVBoxLayout(central)
        
        # 1. QLineEdit with Placeholder
        layout.addWidget(QLabel("1. QLineEdit with Placeholder:"))
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("This is a placeholder...")
        layout.addWidget(self.input_field)
        
        # 2. QTreeWidget with Expand/Collapse
        layout.addWidget(QLabel("\n2. QTreeWidget with Expand/Collapse (Stretched Columns):"))
        self.tree = QTreeWidget()
        self.tree.header().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        root = QTreeWidgetItem(self.tree, ["Project Root"])
        src = QTreeWidgetItem(root, ["src"])
        QTreeWidgetItem(src, ["main.py"])
        QTreeWidgetItem(src, ["utils.py"])
        
        tests = QTreeWidgetItem(root, ["tests"])
        QTreeWidgetItem(tests, ["test_logic.py"])
        
        layout.addWidget(self.tree)
        
        tree_btns = QHBoxLayout()
        expand_btn = QPushButton("Expand All")
        expand_btn.clicked.connect(self.tree.expandAll)
        tree_btns.addWidget(expand_btn)
        
        collapse_btn = QPushButton("Collapse All")
        collapse_btn.clicked.connect(self.tree.collapseAll)
        tree_btns.addWidget(collapse_btn)
        layout.addLayout(tree_btns)
        
        # 3. StatusBar Demo
        layout.addWidget(QLabel("\n3. QStatusBar Demo:"))
        status_btn = QPushButton("Update Status Message")
        status_btn.clicked.connect(lambda: self.statusBar().showMessage(f"Input: {self.input_field.text()}"))
        layout.addWidget(status_btn)
        
        self.setCentralWidget(central)
        central.show()
        
        # Initialize Status Bar
        self.statusBar().showMessage("Ready")

def main():
    app = QApplication(sys.argv)
    demo = VisualFeaturesDemo()
    demo.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
