import sys
import os
import pygame

# Add parent directory to path so we can import gameqt
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from gameqt.application import QApplication
from gameqt.widgets import QMainWindow, QWidget, QLabel, QPushButton, QLineEdit, QCheckBox, QComboBox
from gameqt.layouts import QVBoxLayout, QHBoxLayout, QFormLayout
from gameqt.core import Qt

def test_form():
    app = QApplication(sys.argv)
    win = QMainWindow()
    win.setWindowTitle("GameQt Layout & Alignment Demo")
    win.resize(600, 400)
    
    central = QWidget()
    main_layout = QVBoxLayout(central)
    
    # 1. Alignment Demo
    align_group = QWidget()
    align_group.setStyleSheet("background: #E0E0E0")
    align_layout = QVBoxLayout(align_group)
    
    btn_left = QPushButton("Left Aligned")
    align_layout.addWidget(btn_left, Qt.AlignmentFlag.AlignLeft)
    
    btn_center = QPushButton("Center Aligned")
    align_layout.addWidget(btn_center, Qt.AlignmentFlag.AlignHCenter)
    
    btn_right = QPushButton("Right Aligned")
    align_layout.addWidget(btn_right, Qt.AlignmentFlag.AlignRight)
    
    main_layout.addWidget(QLabel("Alignment Demo:"))
    main_layout.addWidget(align_group)
    
    # 2. Form Layout Demo
    form_widget = QWidget()
    form = QFormLayout(form_widget)
    
    form.addRow("Name:", QLineEdit("John Doe"))
    form.addRow("Email:", QLineEdit("john@example.com"))
    
    combo = QComboBox()
    combo.addItems(["Admin", "User", "Guest"])
    form.addRow("Mode:", combo)
    
    form.addRow("Active:", QCheckBox(""))
    
    main_layout.addWidget(QLabel("Form Layout Demo:"))
    main_layout.addWidget(form_widget)
    
    # 3. Footer
    btn_quit = QPushButton("Quit")
    btn_quit.clicked.connect(app.quit)
    main_layout.addWidget(btn_quit, Qt.AlignmentFlag.AlignRight)
    
    win.setCentralWidget(central)
    win.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    test_form()
