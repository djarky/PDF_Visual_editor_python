import pygame
from ..core import Signal
from .qwidget import QWidget

class QComboBox(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._items = []
        self._current_index = -1
        self.currentIndexChanged = Signal(int)
        self._popup_visible = False
        self._rect.height = 30
    def addItem(self, text, data=None):
        self._items.append({'text': text, 'data': data})
        if self._current_index == -1: self._current_index = 0
    def addItems(self, texts):
        for t in texts: self.addItem(t)
    def currentIndex(self): return self._current_index
    def currentText(self): return self._items[self._current_index]['text'] if 0 <= self._current_index < len(self._items) else ""
    def setCurrentIndex(self, index):
        if 0 <= index < len(self._items):
            self._current_index = index
            self.currentIndexChanged.emit(index)
    def _draw(self, pos):
        from ..application import QApplication
        screen = self._get_screen()
        if not screen: return
        pygame.draw.rect(screen, (255, 255, 255), (pos.x, pos.y, self._rect.width, self._rect.height))
        pygame.draw.rect(screen, (180, 180, 180), (pos.x, pos.y, self._rect.width, self._rect.height), 1)
        # Arrow
        arrow_x = pos.x + self._rect.width - 20
        arrow_y = pos.y + self._rect.height // 2
        pygame.draw.polygon(screen, (80, 80, 80), [(arrow_x, arrow_y - 2), (arrow_x + 10, arrow_y - 2), (arrow_x + 5, arrow_y + 4)])
        
        txt_str = self.currentText()
        font = pygame.font.SysFont(None, 18)
        txt = font.render(txt_str, True, (20, 20, 20))
        screen.blit(txt, (pos.x + 5, pos.y + (self._rect.height - txt.get_height())//2))
        
        if self._popup_visible:
            self._draw_popup(pos)

    def _draw_popup(self, pos):
        from ..application import QApplication
        screen = self._get_screen()
        item_h = 25
        popup_h = len(self._items) * item_h
        popup_rect = pygame.Rect(pos.x, pos.y + self._rect.height, self._rect.width, popup_h)
        pygame.draw.rect(screen, (245, 245, 250), popup_rect)
        pygame.draw.rect(screen, (150, 150, 150), popup_rect, 1)
        font = pygame.font.SysFont(None, 18)
        for i, item in enumerate(self._items):
            iy = popup_rect.y + i * item_h
            if pygame.Rect(popup_rect.x, iy, popup_rect.width, item_h).collidepoint(pygame.mouse.get_pos()):
                pygame.draw.rect(screen, (200, 220, 255), (popup_rect.x+1, iy+1, popup_rect.width-2, item_h-2))
            txt = font.render(item['text'], True, (20, 20, 20))
            screen.blit(txt, (popup_rect.x + 5, iy + (item_h - txt.get_height())//2))

    def mousePressEvent(self, ev):
        if self._popup_visible:
            # Check which item was clicked
            local_y = ev.pos().y() - self._rect.height
            if 0 <= local_y < len(self._items) * 25:
                index = int(local_y // 25)
                self.setCurrentIndex(index)
            self._popup_visible = False
        else:
            self._popup_visible = True

    def _handle_event(self, event, offset):
        if self._popup_visible and event.type == pygame.MOUSEBUTTONDOWN:
            my_pos = offset + pygame.Vector2(self._rect.topleft)
            popup_rect = pygame.Rect(my_pos.x, my_pos.y + self._rect.height, self._rect.width, len(self._items) * 25)
            if not popup_rect.collidepoint(pygame.mouse.get_pos()):
                # Allow toggle off if clicking the combo itself again
                combo_rect = pygame.Rect(my_pos.x, my_pos.y, self._rect.width, self._rect.height)
                if not combo_rect.collidepoint(pygame.mouse.get_pos()):
                    self._popup_visible = False
        super()._handle_event(event, offset)
