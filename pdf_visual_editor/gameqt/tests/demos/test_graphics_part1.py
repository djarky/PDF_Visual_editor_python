import sys
import os
import pygame

# Ensure gameqt is in path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
if os.path.join(project_root, 'pdf_visual_editor') not in sys.path:
     sys.path.insert(0, os.path.join(project_root, 'pdf_visual_editor'))

from gameqt.application import QApplication
from gameqt.widgets import QMainWindow, QWidget, QLabel
from gameqt.graphics import QGraphicsScene, QGraphicsView, QGraphicsRectItem, QGraphicsEllipseItem, QGraphicsTextItem, QGraphicsItem
from gameqt.core import Qt, QRectF, QPointF
from gameqt.gui import QColor, QPen, QBrush

class InteractionItem(QGraphicsRectItem):
    def __init__(self, rect, parent=None):
        super().__init__(rect, parent)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsFocusable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setBrush(QBrush(QColor(200, 255, 200)))
    
    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        print(f"InteractionItem clicked at {event.pos().x()}, {event.pos().y()}")
        self.setBrush(QBrush(QColor(150, 255, 150)))
        self.update()

    def keyPressEvent(self, event):
        print(f"Key pressed in InteractionItem: {event.key}")
        if event.key == pygame.K_r:
            self.setBrush(QBrush(QColor(255, 200, 200)))
        elif event.key == pygame.K_g:
            self.setBrush(QBrush(QColor(200, 255, 200)))
        elif event.key == pygame.K_b:
            self.setBrush(QBrush(QColor(200, 200, 255)))
        self.update()

def main():
    app = QApplication(sys.argv)
    win = QMainWindow()
    win.setWindowTitle("GameQt Part 1 Visual Test")
    win.resize(1000, 800)

    scene = QGraphicsScene()
    view = QGraphicsView(win)
    view.setScene(scene)
    win.setCentralWidget(view)

    # 1. Test Text Alignment
    # Grid of rectangles with aligned text
    alignments = [
        (Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop, "Top-Left"),
        (Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop, "Top-Center"),
        (Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop, "Top-Right"),
        (Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, "Mid-Left"),
        (Qt.AlignmentFlag.AlignCenter, "Center"),
        (Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, "Mid-Right"),
        (Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom, "Bot-Left"),
        (Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom, "Bot-Center"),
        (Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom, "Bot-Right"),
    ]

    for i, (flag, label) in enumerate(alignments):
        row, col = i // 3, i % 3
        x, y = 50 + col * 160, 50 + row * 110
        rect_item = QGraphicsRectItem(QRectF(0, 0, 150, 100))
        rect_item.setPos(x, y)
        rect_item.setBrush(QBrush(QColor(240, 240, 240)))
        scene.addItem(rect_item)
        
        # We need a custom paint or just use QGraphicsTextItem? 
        # Actually QPainter.drawText is what we improved. 
        # Let's create a custom item to test QPainter.drawText directly or 
        # improve QGraphicsTextItem to use the new logic.
        
        # For now, let's subclass QGraphicsRectItem to test drawing text inside it
        class AlignedTextRect(QGraphicsRectItem):
            def __init__(self, rect, text, flags):
                super().__init__(rect)
                self.text = text
                self.flags = flags
            def paint(self, painter, option, widget):
                super().paint(painter, option, widget)
                painter.drawText(self.rect(), self.flags, self.text)
        
        scene.removeItem(rect_item)
        aligned_item = AlignedTextRect(QRectF(0, 0, 150, 100), label, flag)
        aligned_item.setPos(x, y)
        aligned_item.setBrush(QBrush(QColor(240, 240, 240)))
        scene.addItem(aligned_item)

    # 2. Test Cursors
    cursors = [
        (pygame.SYSTEM_CURSOR_HAND, "Hand Cursor", 50, 400),
        (pygame.SYSTEM_CURSOR_CROSSHAIR, "Crosshair", 250, 400),
        (pygame.SYSTEM_CURSOR_IBEAM, "I-Beam", 450, 400),
        (pygame.SYSTEM_CURSOR_WAIT, "Wait", 650, 400),
    ]

    for cur, label, x, y in cursors:
        ellipse = QGraphicsEllipseItem(QRectF(0, 0, 150, 100))
        ellipse.setPos(x, y)
        ellipse.setBrush(QBrush(QColor(200, 200, 250)))
        ellipse.setCursor(cur)
        scene.addItem(ellipse)
        
        # Label for cursor
        txt = QGraphicsTextItem(label)
        txt.setPos(x + 30, y + 40)
        scene.addItem(txt)

    # 3. Test Interaction (Focus/Key Events)
    inter = InteractionItem(QRectF(0, 0, 300, 150))
    inter.setPos(50, 550)
    scene.addItem(inter)
    
    txt_inter = QGraphicsTextItem("Click to focus, then press R, G, or B")
    txt_inter.setPos(60, 600)
    scene.addItem(txt_inter)

    # Instructions
    instr = QGraphicsTextItem("PART 1 TEST: Text Alignment, Cursors, and Interaction")
    instr.setPos(550, 50)
    scene.addItem(instr)

    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
