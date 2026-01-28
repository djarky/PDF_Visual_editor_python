import pygame
from ..core import Qt
from ..application import QApplication
from .qwidget import QWidget

class QMainWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent); self._screen = None; self._central_widget = None; self._menu_bar = None; self._status_bar = None
        if QApplication._instance: QApplication._instance._windows.append(self)
    def show(self):
        super().show()
        if self._screen and hasattr(QApplication.instance(), '_app_name'):
             pygame.display.set_caption(QApplication.instance()._app_name)
    def setMenuBar(self, menu_bar):
        self._menu_bar = menu_bar
        menu_bar._set_parent(self); menu_bar.show()
    def setCentralWidget(self, widget):
        self._central_widget = widget
        widget._set_parent(self); widget.show()
    def statusBar(self):
        if not self._status_bar:
            from .qstatusbar import QStatusBar
            self._status_bar = QStatusBar(self)
            self._status_bar.show()
        return self._status_bar
    def _draw_recursive(self, offset=pygame.Vector2(0,0)):
        if not self.isVisible(): return
        menu_h = 35 if self._menu_bar and self._menu_bar.isVisible() else 0
        status_h = 25 if self._status_bar and self._status_bar.isVisible() else 0
        
        if self._menu_bar: self._menu_bar._rect = pygame.Rect(0, 0, self._rect.width, menu_h)
        if self._status_bar: self._status_bar._rect = pygame.Rect(0, self._rect.height - status_h, self._rect.width, status_h)
        if self._central_widget:
            cw, ch = self._rect.width, self._rect.height - menu_h - status_h
            if self._central_widget._rect.size != (cw, ch):
                self._central_widget.resize(cw, ch)
            self._central_widget._rect.x = 0
            self._central_widget._rect.y = menu_h
        
        my_pos = offset + pygame.Vector2(self._rect.topleft)
        self._draw(my_pos)
        
        # Draw central widget and other children first
        if self._central_widget: self._central_widget._draw_recursive(my_pos)
        for child in self._children:
            if child not in (self._central_widget, self._menu_bar): child._draw_recursive(my_pos)
        
        # Draw menu bar LAST so dropdowns appear on top
        if self._menu_bar: self._menu_bar._draw_recursive(my_pos)
    def _draw(self, pos):
        screen = self._screen or (self.window()._screen if self.window() else None)
        if screen: screen.fill((230, 230, 235))
