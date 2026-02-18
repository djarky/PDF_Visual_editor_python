import sys
import os

# Ensure gameqt is in path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
if os.path.join(project_root, 'pdf_visual_editor') not in sys.path:
     sys.path.insert(0, os.path.join(project_root, 'pdf_visual_editor'))

from gameqt.application import QApplication
from gameqt.widgets import QMainWindow, QWidget
from gameqt.graphics import QGraphicsView, QGraphicsScene, QGraphicsRectItem
from gameqt.gui import QPainter, QColor, QPen, QBrush, QPixmap
from gameqt.core import QRectF

class TestPainterStroke(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QPainter.strokeRect() Test")
        self.resize(800, 600)
        
        # Create a custom widget for direct painting
        canvas = CanvasWidget(self)
        self.setCentralWidget(canvas)
        canvas.show()
        
        status = self.statusBar()
        status.showMessage("Testing QPainter.strokeRect() - different colors and widths")

class CanvasWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
    def _draw(self, pos):
        super()._draw(pos)
        screen = self._get_screen()
        if not screen:
            return
        
        painter = QPainter(screen)
        
        # Title
        painter.setPen(QColor(0, 0, 0))
        painter.drawText(pos.x + 20, pos.y + 20, "QPainter.strokeRect() Demo")
        
        # Test 1: Different stroke widths
        y_offset = 60
        for i, width in enumerate([1, 2, 4, 8]):
            x = pos.x + 50 + (i * 150)
            rect = QRectF(x, pos.y + y_offset, 100, 80)
            color = QColor(100, 150, 200)
            painter.strokeRect(rect, color, width)
            painter.drawText(x, pos.y + y_offset + 100, f"Width: {width}px")
        
        # Test 2: Different colors
        y_offset = 200
        colors = [
            (QColor(255, 0, 0), "Red"),
            (QColor(0, 255, 0), "Green"),
            (QColor(0, 0, 255), "Blue"),
            (QColor(255, 165, 0), "Orange")
        ]
        
        for i, (color, name) in enumerate(colors):
            x = pos.x + 50 + (i * 150)
            rect = QRectF(x, pos.y + y_offset, 100, 80)
            painter.strokeRect(rect, color, 3)
            painter.drawText(x, pos.y + y_offset + 100, name)
        
        # Test 3: Comparison - fillRect vs strokeRect vs drawRect
        y_offset = 380
        
        # fillRect (solid fill)
        rect1 = QRectF(pos.x + 50, pos.y + y_offset, 120, 80)
        painter.fillRect(rect1, QColor(255, 200, 200))
        painter.drawText(pos.x + 50, pos.y + y_offset + 100, "fillRect")
        
        # strokeRect (outline only)
        rect2 = QRectF(pos.x + 220, pos.y + y_offset, 120, 80)
        painter.strokeRect(rect2, QColor(200, 100, 100), 4)
        painter.drawText(pos.x + 220, pos.y + y_offset + 100, "strokeRect")
        
        # drawRect (with pen and brush)
        rect3 = QRectF(pos.x + 390, pos.y + y_offset, 120, 80)
        painter.setPen(QPen(QColor(100, 100, 200), 3))
        painter.setBrush(QBrush(QColor(200, 200, 255)))
        painter.drawRect(rect3)
        painter.drawText(pos.x + 390, pos.y + y_offset + 100, "drawRect")

def main():
    app = QApplication(sys.argv)
    win = TestPainterStroke()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
