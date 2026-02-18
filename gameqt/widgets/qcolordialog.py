import pygame
from ..core import PyGameModalDialog

class QColorDialog(PyGameModalDialog):
    def __init__(self, *args, **kwargs):
        # Signature: QColorDialog(parent=None) or QColorDialog(initial, parent=None)
        title = kwargs.get('title', "Select Color")
        initial = None
        
        if len(args) > 0:
            if hasattr(args[0], '_rect') or hasattr(args[0], 'rect'):
                # First arg is likely a parent widget
                parent = args[0]
                if len(args) > 1: initial = args[1]
            else:
                initial = args[0]
        
        super().__init__(title, 300, 250)
        from ..gui import QColor
        if initial is None: initial = QColor(255, 255, 255)
        if not hasattr(initial, 'r'): initial = QColor(255, 255, 255)
        self.r = initial.r; self.g = initial.g; self.b = initial.b
    @staticmethod
    def getColor(initial=None, parent=None, title="Select Color"):
        from ..gui import QColor
        if initial is None: initial = QColor(255, 255, 255)
        dlg = QColorDialog(initial, title)
        res = dlg.exec_()
        return dlg.selectedColor() if res else initial

    def selectedColor(self):
        from ..gui import QColor
        return QColor(self.r, self.g, self.b)
    def draw(self, screen):
        super().draw(screen)
        y = self.rect.y + 50
        font = pygame.font.SysFont(None, 20)
        for i, (label, val) in enumerate([("R", self.r), ("G", self.g), ("B", self.b)]):
            txt = font.render(f"{label}: {val}", True, (0,0,0))
            screen.blit(txt, (self.rect.x + 20, y))
            # Slider
            pygame.draw.rect(screen, (200, 200, 200), (self.rect.x + 80, y, 150, 20))
            pygame.draw.rect(screen, (100, 150, 240), (self.rect.x + 80 + int((val/255)*140), y, 10, 20))
            y += 40
        # Preview
        pygame.draw.rect(screen, (self.r, self.g, self.b), (self.rect.x + 80, y, 150, 40))
        pygame.draw.rect(screen, (0,0,0), (self.rect.x + 80, y, 150, 40), 1)
        # OK Button
        btn_ok = pygame.Rect(self.rect.centerx - 40, self.rect.bottom - 40, 80, 25)
        pygame.draw.rect(screen, (0, 120, 215), btn_ok, border_radius=3)
        txt = font.render("OK", True, (255,255,255))
        screen.blit(txt, (btn_ok.centerx - txt.get_width()//2, btn_ok.centery - txt.get_height()//2))
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN or (event.type == pygame.MOUSEMOTION and event.buttons[0]):
            x, y = event.pos
            # Check sliders
            start_y = self.rect.y + 45
            for i in range(3):
                slider_rect = pygame.Rect(self.rect.x + 80, start_y + i*40, 150, 25)
                if slider_rect.collidepoint(x, y):
                    val = int(max(0, min(255, (x - slider_rect.x) / 150 * 255)))
                    if i == 0: self.r = val
                    elif i == 1: self.g = val
                    else: self.b = val
            # Check OK button
            btn_ok = pygame.Rect(self.rect.centerx - 40, self.rect.bottom - 40, 80, 25)
            if event.type == pygame.MOUSEBUTTONDOWN and btn_ok.collidepoint(x, y):
                self.result = True
                self.running = False
