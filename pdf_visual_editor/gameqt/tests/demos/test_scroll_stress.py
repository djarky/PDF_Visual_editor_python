import sys
import os
import pygame

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from pdf_visual_editor.gameqt.application import QApplication
from pdf_visual_editor.gameqt.widgets import QMainWindow, QWidget, QPushButton, QScrollArea, QLabel
from pdf_visual_editor.gameqt.layouts import QVBoxLayout

class ScrollStressTest(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Scroll Stress Test")
        self.resize(500, 400)
        
        # Use a main widget for the window layout
        main_container = QWidget(self)
        self.setCentralWidget(main_container)
        main_layout = QVBoxLayout(main_container)
        
        scroll = QScrollArea(main_container)
        scroll.resize(460, 340)
        main_layout.addWidget(scroll)
        
        content = QWidget()
        scroll.setWidget(content)
        
        layout = QVBoxLayout(content)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        
        # Test 1: Explicitly resized widget
        big_btn = QPushButton("Explicitly sized (200x150)")
        big_btn.resize(200, 150)
        layout.addWidget(big_btn)
        
        # Test 2: Nested Layout (Container widget)
        sub_widget = QWidget()
        sub_layout = QVBoxLayout(sub_widget)
        for i in range(5):
             btn = QPushButton(f"Sub-item {i+1}")
             btn.resize(200, 40)
             sub_layout.addWidget(btn)
        layout.addWidget(sub_widget)
        
        # Test 3: Many items
        for i in range(20):
            layout.addWidget(QPushButton(f"Bottom Item {i+1}"))
            
        end_label = QLabel("--- THIS IS THE VERY END ---")
        layout.addWidget(end_label)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = ScrollStressTest()
    win.show()
    sys.exit(app.exec())
