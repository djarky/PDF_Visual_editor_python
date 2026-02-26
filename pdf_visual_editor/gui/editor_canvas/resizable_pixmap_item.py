"""
ResizablePixmapItem — pixmap element with resize handles.
"""

from qt_compat import (QGraphicsPixmapItem, QGraphicsItem)
from .resizable_mixin import ResizableMixin


class ResizablePixmapItem(QGraphicsPixmapItem, ResizableMixin):
    def __init__(self, pixmap, parent=None):
        QGraphicsPixmapItem.__init__(self, pixmap, parent)
        ResizableMixin.__init__(self)
        self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
                      QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setShapeMode(QGraphicsPixmapItem.ShapeMode.BoundingRectShape)
