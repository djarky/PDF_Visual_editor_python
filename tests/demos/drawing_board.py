
import sys
import os

# Ensure gameqt is in path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
if os.path.join(project_root, 'pdf_visual_editor') not in sys.path:
     sys.path.insert(0, os.path.join(project_root, 'pdf_visual_editor'))

from gameqt.graphics import QGraphicsView, QGraphicsScene, QGraphicsEllipseItem
from gameqt.gui import QPen, QBrush, QColor
from gameqt.core import Qt
from gameqt.application import QApplication

class DrawingBoard(QGraphicsView):
    def __init__(self):
        scene = QGraphicsScene()
        super().__init__(scene)
        self.resize(600, 400)
        self.setWindowTitle("Drawing Board")
        
        self.drawing = False
        self.last_pos = None
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = True
            self.last_pos = self.mapToScene(event.pos())
    
    def mouseMoveEvent(self, event):
        if self.drawing and self.last_pos:
            current_pos = self.mapToScene(event.pos())
            
            # Draw a small circle
            ellipse = QGraphicsEllipseItem(
                current_pos.x() - 2, current_pos.y() - 2, 4, 4
            )
            ellipse.setPen(QPen(QColor(0, 0, 0), 1))
            ellipse.setBrush(QBrush(QColor(0, 0, 0)))
            self.scene().addItem(ellipse)
            
            self.last_pos = current_pos
    
    def mouseReleaseEvent(self, event):
        self.drawing = False
        self.last_pos = None

def main():
    app = QApplication(sys.argv)
    board = DrawingBoard()
    board.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
