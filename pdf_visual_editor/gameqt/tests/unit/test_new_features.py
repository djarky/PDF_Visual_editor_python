import sys
import os
import pygame

# Add parent directory to path so we can import gameqt
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from gameqt.application import QApplication
from gameqt.widgets import QMainWindow, QWidget, QLabel, QPushButton, QLineEdit, QCheckBox, QRadioButton, QComboBox, QSpinBox, QStackedWidget
from gameqt.layouts import QVBoxLayout, QHBoxLayout, QGridLayout
from gameqt.core import Qt
from gameqt.gui import QPainter, QPen, QBrush, QColor, QPointF

class GraphicsWidget(QWidget):
    def _draw(self, pos):
        super()._draw(pos)
        screen = QApplication.instance()._windows[0]._screen
        painter = QPainter(screen)
        
        # Draw Line
        painter.setPen(QPen(QColor(255, 0, 0), 2))
        painter.drawLine(pos.x + 10, pos.y + 10, pos.x + 100, pos.y + 50)
        
        # Draw Filled Rect
        painter.setBrush(QBrush(QColor(0, 255, 0, 100)))
        painter.drawRect(pygame.Rect(pos.x + 10, pos.y + 60, 80, 40))
        
        # Draw Ellipse
        painter.setBrush(QBrush(QColor(0, 0, 255, 100)))
        painter.drawEllipse(pygame.Rect(pos.x + 110, pos.y + 10, 80, 50))
        
        # Draw Polygon
        painter.setBrush(QBrush(QColor(255, 255, 0, 100)))
        points = [QPointF(pos.x + 120, pos.y + 70), QPointF(pos.x + 180, pos.y + 70), QPointF(pos.x + 150, pos.y + 110)]
        painter.drawPolygon(points)

def test_app():
    app = QApplication(sys.argv)
    win = QMainWindow()
    win.setWindowTitle("GameQt New Features Demo")
    win.resize(800, 600)
    
    central = QWidget()
    layout = QHBoxLayout(central)
    
    # Left side: Widgets in a Grid
    form_container = QWidget()
    grid = QGridLayout(form_container)
    grid.setSpacing(10)
    
    grid.addWidget(QLabel("LineEdit:"), 0, 0)
    grid.addWidget(QLineEdit("Hello World"), 0, 1)
    
    grid.addWidget(QLabel("CheckBox:"), 1, 0)
    grid.addWidget(QCheckBox("Enable Option"), 1, 1)
    
    grid.addWidget(QLabel("RadioButtons:"), 2, 0)
    radio_container = QWidget()
    rlayout = QVBoxLayout(radio_container)
    r1 = QRadioButton("Option A", radio_container)
    r2 = QRadioButton("Option B", radio_container)
    rlayout.addWidget(r1)
    rlayout.addWidget(r2)
    grid.addWidget(radio_container, 2, 1)
    
    grid.addWidget(QLabel("ComboBox:"), 3, 0)
    combo = QComboBox()
    combo.addItems(["Item 1", "Item 2", "Item 3"])
    grid.addWidget(combo, 3, 1)
    
    grid.addWidget(QLabel("SpinBox:"), 4, 0)
    spin = QSpinBox()
    grid.addWidget(spin, 4, 1)
    
    layout.addWidget(form_container)
    
    # Right side: Stacked Widget and Graphics
    right_container = QWidget()
    rlayout2 = QVBoxLayout(right_container)
    
    stack = QStackedWidget()
    stack.addWidget(QLabel("I am Page 1"))
    stack.addWidget(QLabel("I am Page 2"))
    
    btn_switch = QPushButton("Switch Page")
    btn_switch.clicked.connect(lambda: stack.setCurrentIndex((stack.currentIndex() + 1) % 2))
    
    rlayout2.addWidget(stack)
    rlayout2.addWidget(btn_switch)
    
    # Custom graphics
    gfx = GraphicsWidget()
    gfx.resize(200, 150)
    rlayout2.addWidget(gfx)
    
    layout.addWidget(right_container)
    
    win.setCentralWidget(central)
    win.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    test_app()
