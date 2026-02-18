#!/usr/bin/env python3
"""
Simple test to verify menu functionality
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from qt_compat import QApplication, QMainWindow, QLabel
from gameqt.menus import QMenuBar, QMenu, QAction

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Menu Test")
        self.resize(800, 600)
        
        # Create menu bar
        menubar = QMenuBar(self)
        self.setMenuBar(menubar)
        
        # File menu
        file_menu = menubar.addMenu("File")
        action1 = file_menu.addAction("Open")
        action1.triggered.connect(lambda: print("OPEN TRIGGERED!"))
        action2 = file_menu.addAction("Save")
        action2.triggered.connect(lambda: print("SAVE TRIGGERED!"))
        action3 = file_menu.addAction("Exit")
        action3.triggered.connect(lambda: print("EXIT TRIGGERED!"))
        
        # Edit menu
        edit_menu = menubar.addMenu("Edit")
        edit_menu.addAction("Copy")
        edit_menu.addAction("Paste")
        
        # Central widget
        label = QLabel("Click on File or Edit menu", self)
        self.setCentralWidget(label)
        
        self.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    sys.exit(app.exec())
