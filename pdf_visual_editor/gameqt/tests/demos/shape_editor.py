
import sys
import os
import random

# Ensure gameqt is in path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
if os.path.join(project_root, 'pdf_visual_editor') not in sys.path:
     sys.path.insert(0, os.path.join(project_root, 'pdf_visual_editor'))

from gameqt.graphics import (QGraphicsView, QGraphicsScene, 
                              QGraphicsRectItem, QGraphicsEllipseItem)
from gameqt.gui import QPen, QBrush, QColor
from gameqt.widgets import QMainWindow, QWidget, QPushButton
from gameqt.layouts import QVBoxLayout, QHBoxLayout
from gameqt.application import QApplication

class ShapeEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Shape Editor")
        self.resize(800, 600)
        
        central = QWidget()
        layout = QVBoxLayout(central)
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        add_rect_btn = QPushButton("Add Rectangle")
        add_rect_btn.clicked.connect(self.add_rectangle)
        toolbar.addWidget(add_rect_btn)
        
        add_circle_btn = QPushButton("Add Circle")
        add_circle_btn.clicked.connect(self.add_circle)
        toolbar.addWidget(add_circle_btn)
        
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.clear_scene)
        toolbar.addWidget(clear_btn)
        
        toolbar.addStretch()
        layout.addLayout(toolbar)
        
        # Graphics view
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        layout.addWidget(self.view)
        
        self.setCentralWidget(central)
        central.show()
    
    def add_rectangle(self):
        x = random.randint(50, 400)
        y = random.randint(50, 300)
        w = random.randint(50, 150)
        h = random.randint(50, 150)
        
        rect = QGraphicsRectItem(x, y, w, h)
        rect.setPen(QPen(QColor(random.randint(0, 255), 
                                random.randint(0, 255), 
                                random.randint(0, 255)), 2))
        rect.setBrush(QBrush(QColor(random.randint(0, 255), 
                                    random.randint(0, 255), 
                                    random.randint(0, 255), 100)))
        rect.setFlags(QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable | 
                     QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable)
        self.scene.addItem(rect)
    
    def add_circle(self):
        x = random.randint(50, 400)
        y = random.randint(50, 300)
        size = random.randint(50, 150)
        
        ellipse = QGraphicsEllipseItem(x, y, size, size)
        ellipse.setPen(QPen(QColor(random.randint(0, 255), 
                                   random.randint(0, 255), 
                                   random.randint(0, 255)), 2))
        ellipse.setBrush(QBrush(QColor(random.randint(0, 255), 
                                       random.randint(0, 255), 
                                       random.randint(0, 255), 100)))
        ellipse.setFlags(QGraphicsEllipseItem.GraphicsItemFlag.ItemIsMovable | 
                        QGraphicsEllipseItem.GraphicsItemFlag.ItemIsSelectable)
        self.scene.addItem(ellipse)
    
    def clear_scene(self):
        self.scene.clear()

def main():
    app = QApplication(sys.argv)
    editor = ShapeEditor()
    editor.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
