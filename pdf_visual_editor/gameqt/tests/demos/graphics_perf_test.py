
import sys
import os
import time
import random

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from gameqt import QApplication, QRectF
from gameqt.graphics import QGraphicsScene, QGraphicsView, QGraphicsRectItem, QGraphicsItem
from gameqt.gui import QColor, QBrush, QPen

def main():
    app = QApplication(sys.argv)
    
    # Create Scene
    scene = QGraphicsScene()
    scene.setSceneRect(QRectF(0, 0, 2000, 2000))
    
    # Add MANY items to stress test
    print("Creating 1000 items...")
    for i in range(1000):
        x = random.randint(0, 1900)
        y = random.randint(0, 1900)
        r = QGraphicsRectItem(x, y, 50, 50)
        r.setBrush(QBrush(QColor(random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))))
        r.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        r.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        scene.addItem(r)

    # Create View
    view = QGraphicsView(scene)
    view.setWindowTitle("Graphics Performance Test (1000 items)")
    view.resize(800, 600)
    view.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
    
    view.show()
    
    print("Running... Try to select items or pan/zoom.")
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
