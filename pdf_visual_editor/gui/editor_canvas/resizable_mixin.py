"""
ResizableMixin — adds resize handles to any QGraphicsItem.
"""

from qt_compat import (QGraphicsItem, QGraphicsRectItem, QGraphicsPixmapItem,
                       QGraphicsTextItem, Qt, QTransform)
from .resizer_handle import ResizerHandle


class ResizableMixin:
    """Mixin to add resize handles to a QGraphicsItem."""

    def __init__(self):
        self.handles = []
        self._create_handles()

    def _create_handles(self):
        # Check if we are a QGraphicsItem
        if not isinstance(self, QGraphicsItem):
            return

        # Bottom-Right Handle
        h_br = ResizerHandle(self, Qt.CursorShape.SizeFDiagCursor, lambda r: r.bottomRight())
        self.handles.append(h_br)

    def handle_resize(self, handle, new_pos):
        # Convert new_pos to parent coordinates (scene)
        # We want to find the new scale factor.

        # Top-Left in scene coords
        tl_scene = self.mapToScene(self.boundingRect().topLeft())

        # Vector from TL to new handle pos
        diff = new_pos - tl_scene

        # Map new_pos to local coordinates
        local_pos = self.mapFromScene(new_pos)

        if isinstance(self, QGraphicsRectItem):
            # For RectItem, we actually change the rect, not the scale.
            self.setRect(0, 0, local_pos.x(), local_pos.y())

        elif isinstance(self, QGraphicsPixmapItem):
            # For Pixmap, we change the scale.
            base_w = self.boundingRect().width()
            base_h = self.boundingRect().height()

            if base_w > 1 and base_h > 1:
                scale_x = local_pos.x() / base_w
                scale_y = local_pos.y() / base_h

                if scale_x > 0.1 and scale_y > 0.1:
                    self.setTransform(QTransform.fromScale(scale_x, scale_y), combine=True)

        elif isinstance(self, QGraphicsTextItem):
            # Similar logic for text, scale the whole item
            base_w = self.boundingRect().width()
            base_h = self.boundingRect().height()

            if base_w > 1 and base_h > 1:
                scale_x = local_pos.x() / base_w
                scale_y = local_pos.y() / base_h

                # Uniform scale for text usually looks better
                avg_scale = (scale_x + scale_y) / 2
                if avg_scale > 0.1:
                    self.setTransform(QTransform.fromScale(avg_scale, avg_scale), combine=True)

        # Update handles
        for h in self.handles:
            h.update_position()
