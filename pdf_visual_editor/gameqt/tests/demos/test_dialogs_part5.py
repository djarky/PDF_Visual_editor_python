#!/usr/bin/env python3
"""
test_part5_dialogs.py
Visual test for Part 5: Dialogs and QStyledItemDelegate
"""
import sys
import os

# Ensure gameqt is in path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

from gameqt.application import QApplication
from gameqt.widgets import (QMainWindow, QWidget, QLabel, QPushButton, 
                             QMessageBox, QColorDialog, QFontDialog)
from gameqt.layouts import QVBoxLayout, QHBoxLayout
from gameqt.core import Qt
print("DEBUG: ItemFlag attributes:", dir(Qt.ItemFlag))
print("DEBUG: core file:", Qt.__module__)
import inspect
print("DEBUG: core file path:", inspect.getfile(Qt))

class Part5Test(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Part 5: Dialogs & Delegates")
        self.resize(800, 600)
        
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # 1. Dialogs Section
        lbl_dialogs = QLabel("Dialog Tests (Robustness):")
        lbl_dialogs.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(lbl_dialogs)
        
        btn_layout = QHBoxLayout()
        
        btn_msg = QPushButton("Show MessageBox")
        btn_msg.clicked.connect(self.show_message)
        btn_layout.addWidget(btn_msg)
        
        btn_color = QPushButton("Show ColorDialog")
        btn_color.clicked.connect(self.show_color)
        btn_layout.addWidget(btn_color)
        
        btn_font = QPushButton("Show FontDialog")
        btn_font.clicked.connect(self.show_font)
        btn_layout.addWidget(btn_font)
        
        layout.addLayout(btn_layout)
        
        layout.addSpacing(20)
        
        # 2. Delegate Section
        lbl_delegate = QLabel("QStyledItemDelegate Test (QTreeWidget):")
        lbl_delegate.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(lbl_delegate)
        
        # Define Custom Delegate
        from gameqt.item_views import QStyledItemDelegate, QTreeWidget, QTreeWidgetItem
        from gameqt.gui import QColor
        
        class CustomDelegate(QStyledItemDelegate):
             def paint(self, painter, option, index):
                 # Custom background for all items handled by this delegate
                 if option.state & Qt.ItemFlag.ItemIsSelectable:
                     painter.fillRect(option.rect, QColor(0, 100, 255)) # Bright Blue
                 else:
                     painter.fillRect(option.rect, QColor(240, 255, 240)) # Light Green for verification
                 
                 # Draw text manually or via super
                 # Let's draw text in red to prove control
                 painter.drawText(option.rect.x + 5, option.rect.y + 5, str(index.data()))

        tree = QTreeWidget()
        tree.setHeaderLabels(["Col 1 (Custom)", "Col 2 (Default)"])
        
        item1 = QTreeWidgetItem(["Custom 1", "Default 1"])
        item2 = QTreeWidgetItem(["Custom 2", "Default 2"])
        tree.addTopLevelItem(item1)
        tree.addTopLevelItem(item2)
        
        # Set delegate for column 0 only
        tree.setItemDelegateForColumn(0, CustomDelegate())
        
        layout.addWidget(tree)
        
        lbl_info = QLabel("Verify: Col 1 has Green BG/Red Text. Col 2 is standard.")
        layout.addWidget(lbl_info)
        
    def show_message(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("Test Message")
        msg.setText("This is a modal message box.\nIt should not freeze properly.")
        msg.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
        res = msg.exec_()
        print(f"Message result: {res}")
        
    def show_color(self):
        dlg = QColorDialog(self)
        if dlg.exec_():
            print(f"Color selected: {dlg.selectedColor()}")
            
    def show_font(self):
        dlg = QFontDialog(self)
        if dlg.exec_():
            print(f"Font selected: {dlg.selectedFont()}")

def main():
    app = QApplication(sys.argv)
    win = Part5Test()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
