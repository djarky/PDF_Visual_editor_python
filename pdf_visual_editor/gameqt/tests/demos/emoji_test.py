import sys
import os
import pygame

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pdf_visual_editor.gameqt.application import QApplication
from pdf_visual_editor.gameqt.widgets.qwidget import QWidget
from pdf_visual_editor.gameqt.widgets.qlabel import QLabel
from pdf_visual_editor.gameqt.widgets.qpushbutton import QPushButton
from pdf_visual_editor.gameqt.layouts.box_layout import QVBoxLayout
from pdf_visual_editor.gameqt.core import Qt

def main():
    app = QApplication(sys.argv)
    
    window = QWidget()
    window.setWindowTitle("Emoji Support Test")
    window.resize(400, 300)
    
    layout = QVBoxLayout(window)
    
    label1 = QLabel("Standard Text")
    layout.addWidget(label1)
    
    label2 = QLabel("Text with Emoji: 🚀 🌟 🍎")
    layout.addWidget(label2)
    
    btn1 = QPushButton("Standard Button")
    layout.addWidget(btn1)
    
    btn2 = QPushButton("Button with Emoji 👍 ✅")
    layout.addWidget(btn2)
    
    window.show()
    
    # Run for a few frames then exit if in non-interactive mode
    # For now, just let it run
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
