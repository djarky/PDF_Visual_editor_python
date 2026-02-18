
import sys
import os
import pygame

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from gameqt import QApplication, QRectF
from gameqt.graphics import QGraphicsScene, QGraphicsView, QGraphicsRectItem, QGraphicsItem
from gameqt.gui import QColor, QBrush, QPen

def main():
    app = QApplication(sys.argv)
    
    # Create Scene
    scene = QGraphicsScene()
    scene.setSceneRect(QRectF(0, 0, 800, 600))
    
    # Add some items
    r1 = QGraphicsRectItem(50, 50, 100, 100)
    r1.setBrush(QBrush(QColor(255, 100, 100)))
    r1.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
    r1.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
    scene.addItem(r1)
    
    r2 = QGraphicsRectItem(200, 50, 100, 100)
    r2.setBrush(QBrush(QColor(100, 255, 100)))
    r2.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
    r2.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
    scene.addItem(r2)
    
    r3 = QGraphicsRectItem(50, 200, 100, 100)
    r3.setBrush(QBrush(QColor(100, 100, 255)))
    r3.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
    r3.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
    scene.addItem(r3)

    # Create View
    view = QGraphicsView(scene)
    view.setWindowTitle("Selection Test")
    view.resize(800, 600)
    view.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
    
    # Hook into selection change
    def on_selection_changed():
        print(f"Selection changed! Selected items: {len(scene.selectedItems())}")
        for item in scene.selectedItems():
            # flash outline or something?
            pass
            
    scene.selectionChanged.connect(on_selection_changed)
    
    view.show()
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
