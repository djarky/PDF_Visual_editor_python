import sys
import os
import pygame

# Add parent directory to path so we can import gameqt
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from gameqt.application import QApplication
from gameqt.widgets import QMainWindow, QWidget, QLabel, QPushButton, QColorDialog, QFontDialog
from gameqt.core import QShortcut
from gameqt.gui import QKeySequence

def test_phase4():
    app = QApplication(sys.argv)
    win = QMainWindow()
    win.setWindowTitle("GameQt Phase 4 Demo")
    win.resize(400, 300)
    
    central = QWidget()
    from gameqt.layouts import QVBoxLayout
    layout = QVBoxLayout(central)
    
    label = QLabel("Press Ctrl+S or use buttons below")
    layout.addWidget(label)
    
    # Shortcut test
    shortcut = QShortcut(QKeySequence("Ctrl+S"), win)
    shortcut.activated.connect(lambda: label.setText("Shortcut Ctrl+S Activated!"))
    
    # Color Dialog test
    btn_color = QPushButton("Pick Color")
    def pick_color():
        color = QColorDialog.getColor()
        label.setText(f"Picked Color: ({color.r}, {color.g}, {color.b})")
    btn_color.clicked.connect(pick_color)
    layout.addWidget(btn_color)
    
    # Font Dialog test
    btn_font = QPushButton("Pick Font")
    def pick_font():
        font, ok = QFontDialog.getFont()
        if ok:
            label.setText(f"Picked Font: {font._family} at {font._size}pt")
    btn_font.clicked.connect(pick_font)
    layout.addWidget(btn_font)
    
    win.setCentralWidget(central)
    win.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    test_phase4()
