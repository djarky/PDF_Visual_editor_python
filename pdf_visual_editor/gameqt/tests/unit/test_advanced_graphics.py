import sys
import os
import pygame

# Add parent directory to path so we can import gameqt
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from gameqt.application import QApplication
from gameqt.widgets import QMainWindow, QWidget, QLabel
from gameqt.graphics import QGraphicsScene, QGraphicsView, QGraphicsRectItem, QGraphicsItem
from gameqt.gui import QPainter, QPen, QBrush, QColor, QLinearGradient, QTransform, QKeySequence
from gameqt.core import Qt, QRectF, QPointF, QShortcut

def test_advanced_graphics():
    app = QApplication(sys.argv)
    win = QMainWindow()
    win.setWindowTitle("GameQt Advanced Graphics Test")
    win.resize(800, 600)
    
    view = QGraphicsView()
    scene = QGraphicsScene()
    view.setScene(scene)
    
    # Enable RubberBand selection
    view.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
    
    # Add a rect with gradient
    # Since QGraphicsRectItem.paint uses current painter state implicitly via drawRect,
    # it should respect current view transform.
    rect_item = QGraphicsRectItem(0, 0, 150, 150)
    rect_item.setPos(50, 50)
    grad = QLinearGradient(0, 0, 0, 150)
    grad.setColorAt(0, QColor(255, 100, 100)) # Light Red
    grad.setColorAt(1, QColor(100, 100, 255)) # Light Blue
    rect_item.setBrush(QBrush(grad))
    rect_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
    scene.addItem(rect_item)
    
    # Add another rect
    rect2 = QGraphicsRectItem(0, 0, 100, 100)
    rect2.setPos(250, 100)
    rect2.setBrush(QBrush(QColor(100, 255, 100, 120)))
    rect2.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
    scene.addItem(rect2)
    
    # Controls
    zoom_in = QShortcut(QKeySequence("v"), win) # Use 'v' for zoom in
    zoom_in.activated.connect(lambda: (view.scale(1.1, 1.1), print("Zoom In")))
    
    zoom_out = QShortcut(QKeySequence("b"), win) # Use 'b' for zoom out
    zoom_out.activated.connect(lambda: (view.scale(0.9, 0.9), print("Zoom Out")))
    
    win.setCentralWidget(view)
    win.show()
    
    print("Test ready:")
    print("  Left Drag: Move items or Rubber-band select")
    print("  Right Drag: Pan view")
    print("  Press 'V': Zoom In")
    print("  Press 'B': Zoom Out")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    test_advanced_graphics()
