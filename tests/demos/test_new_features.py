
import sys
import os
import pygame

# Ensure gameqt is in path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from gameqt.application import QApplication
from gameqt.widgets import QMainWindow, QWidget, QLabel, QLineEdit, QComboBox, QScrollArea, QPushButton
from gameqt.layouts import QVBoxLayout, QHBoxLayout, QFormLayout
from gameqt.core import Qt

class NewFeaturesDemo(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GameQt New Features Test")
        self.resize(800, 600)
        
        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 1. Styling Test (Border Radius & Padding)
        styling_label = QLabel("1. Styling Test (Border Radius & Padding)")
        styling_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(styling_label)
        
        styled_box = QWidget()
        styled_box.resize(300, 80)
        styled_box.setStyleSheet("background-color: #E3F2FD; border: 2px solid blue; border-radius: 15px; padding: 10px;")
        
        box_layout = QHBoxLayout(styled_box)
        box_text = QLabel("Rounded Corners & Blue Border")
        box_text.setStyleSheet("color: darkblue; border: none;") # Ensure no border on text
        box_layout.addWidget(box_text)
        layout.addWidget(styled_box)
        
        # 2. QLineEdit Test (Selection & Cursor)
        lineedit_label = QLabel("2. QLineEdit Test (Selection & Cursor)")
        lineedit_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(lineedit_label)
        
        self.le = QLineEdit("Try selecting me or moving cursor!")
        self.le.setPlaceholderText("Typed text appears here...")
        layout.addWidget(self.le)
        
        # 3. QComboBox Test (Positioning & Hover)
        combo_label = QLabel("3. QComboBox Test (Positioning & Hover)")
        combo_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(combo_label)
        
        self.combo = QComboBox()
        self.combo.addItems(["Option 1", "Option 2", "Option 3", "Option 4", "Option 5"])
        layout.addWidget(self.combo)
        
        # 4. QScrollArea Test (Dynamic SizeHint)
        scroll_label = QLabel("4. QScrollArea Test (Dynamic SizeHint)")
        scroll_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(scroll_label)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.resize(400, 150)
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        for i in range(10):
            btn = QPushButton(f"Button {i+1}")
            btn.resize(350, 40)
            scroll_layout.addWidget(btn)
            
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        
        # Bottom controls
        bottom_layout = QHBoxLayout()
        test_btn = QPushButton("Check Console Mapping")
        test_btn.clicked.connect(self.test_mappings)
        bottom_layout.addWidget(test_btn)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        bottom_layout.addWidget(close_btn)
        
        layout.addLayout(bottom_layout)
        
        self.setCentralWidget(central)
        central.show()

    def test_mappings(self):
        # Verify mapToGlobal
        pos = self.le.mapToGlobal(pygame.Vector2(0, 0))
        print(f"QLineEdit Global Pos: {pos.x()}, {pos.y()}")
        # Verify scale
        from gameqt.graphics import QGraphicsItem
        from gameqt.gui import QTransform
        item = QGraphicsItem()
        item.setTransform(QTransform().scale(2.5, 2.5))
        print(f"GraphicsItem Scale: {item.scale()}")

def main():
    app = QApplication(sys.argv)
    demo = NewFeaturesDemo()
    demo.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
