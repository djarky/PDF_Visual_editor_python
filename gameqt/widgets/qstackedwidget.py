from .qwidget import QWidget

class QStackedWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        from ..layouts import QStackedLayout
        self._layout = QStackedLayout(self)
    def addWidget(self, w): self._layout.addWidget(w)
    def setCurrentIndex(self, index): self._layout.setCurrentIndex(index)
    def currentIndex(self): return self._layout._current_index
