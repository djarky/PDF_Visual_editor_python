from .qcolor import QColor

class QBrush:
    def __init__(self, color=None, style=None):
        if hasattr(color, 'setColorAt'): # It's a gradient
            self._color = QColor(0,0,0,0); self._style = 2; self._gradient = color
        else:
            self._color = QColor(color) if color is not None else QColor(0,0,0,0)
            self._style = style if style is not None else 1  # Qt.BrushStyle.SolidPattern

class QGradient:
    def __init__(self): self._stops = []
    def setColorAt(self, pos, color): self._stops.append((pos, QColor(color)))

class QLinearGradient(QGradient):
    def __init__(self, x1, y1, x2, y2):
        super().__init__()
        self._p1 = (x1, y1); self._p2 = (x2, y2)

class QRadialGradient(QGradient):
    def __init__(self, cx, cy, radius):
        super().__init__()
        self._center = (cx, cy); self._radius = radius
