from .qcolor import QColor

class QPen:
    def __init__(self, color=None, width=1, style=None):
        self._color = QColor(color) if color is not None else QColor(0,0,0)
        self._width = width
        self._style = style if style is not None else 1  # Qt.PenStyle.SolidLine
