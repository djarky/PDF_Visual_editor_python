
import sys
import os

# Ensure gameqt is in path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
if os.path.join(project_root, 'pdf_visual_editor') not in sys.path:
     sys.path.insert(0, os.path.join(project_root, 'pdf_visual_editor'))

from gameqt.widgets import QWidget, QMainWindow
from gameqt.gui import QColor
from gameqt.application import QApplication
from gameqt.core import Signal
import pygame

class ColorPicker(QWidget):
    colorChanged = Signal(QColor)
    
    def __init__(self):
        super().__init__()
        self.selected_color = QColor(255, 0, 0)
        self.colors = [
            QColor(255, 0, 0), QColor(0, 255, 0), QColor(0, 0, 255),
            QColor(255, 255, 0), QColor(255, 0, 255), QColor(0, 255, 255),
            QColor(255, 128, 0), QColor(128, 0, 255), QColor(0, 128, 255)
        ]
    
    def _draw(self, pos):
        super()._draw(pos)
        
        if not QApplication._instance: return
        # Accessing private members as per example
        if hasattr(QApplication._instance, '_windows') and QApplication._instance._windows:
             screen = QApplication._instance._windows[0]._screen
        else:
             return
        
        # Draw color swatches
        swatch_size = 40
        spacing = 10
        x = pos.x + 10
        y = pos.y + 10
        
        for i, color in enumerate(self.colors):
            if i % 3 == 0 and i > 0:
                x = pos.x + 10
                y += swatch_size + spacing
            
            # Draw swatch
            pygame.draw.rect(screen, color.to_pygame()[:3], 
                           (x, y, swatch_size, swatch_size))
            
            # Draw border
            border_color = (255, 255, 255) if color == self.selected_color else (100, 100, 100)
            pygame.draw.rect(screen, border_color, 
                           (x, y, swatch_size, swatch_size), 2)
            
            x += swatch_size + spacing
    
    def mousePressEvent(self, event):
        # Determine which color was clicked
        swatch_size = 40
        spacing = 10
        
        for i, color in enumerate(self.colors):
            col = i % 3
            row = i // 3
            x = 10 + col * (swatch_size + spacing)
            y = 10 + row * (swatch_size + spacing)
            
            if (x <= event.pos().x() <= x + swatch_size and
                y <= event.pos().y() <= y + swatch_size):
                self.selected_color = color
                self.colorChanged.emit(color)
                break

def main():
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("Color Picker")
    window.resize(200, 200)
    
    picker = ColorPicker()
    picker.colorChanged.connect(lambda c: print(f"Selected: {c.red()}, {c.green()}, {c.blue()}"))
    window.setCentralWidget(picker)
    
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
