import sys
import os
import pygame

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pdf_visual_editor.gameqt.application import QApplication
from pdf_visual_editor.gameqt.widgets.qwidget import QWidget
from pdf_visual_editor.gameqt.widgets.qlabel import QLabel
from pdf_visual_editor.gameqt.layouts.box_layout import QVBoxLayout
from pdf_visual_editor.gameqt.gui import QFont, QFontDatabase

def main():
    app = QApplication(sys.argv)
    
    # We'll use one of the discovered system fonts as a "custom" font for testing
    # assuming we can treat any TTF as a custom one.
    custom_font_path = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
    if not os.path.exists(custom_font_path):
        # Fallback if the path is different
        custom_font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        
    family = QFontDatabase.addApplicationFont(custom_font_path)
    print(f"Registered custom font: {family}")
    
    window = QWidget()
    window.setWindowTitle("Extended Font Support Test")
    window.resize(500, 300)
    
    layout = QVBoxLayout(window)
    
    label1 = QLabel(f"Standard SysFont")
    label1.setFont(QFont("Arial", 16))
    layout.addWidget(label1)
    
    label2 = QLabel(f"Custom Font: {family}")
    label2.setFont(QFont(family, 20))
    layout.addWidget(label2)
    
    label3 = QLabel(f"Custom Font + Emojis 🚀: {family}")
    label3.setFont(QFont(family, 18))
    layout.addWidget(label3)
    
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
