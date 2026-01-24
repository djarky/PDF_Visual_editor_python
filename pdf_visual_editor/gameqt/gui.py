import pygame
from .core import QRectF, QSize, QPointF, Qt

class QColor:
    def __init__(self, *args):
        if len(args) == 1:
            if isinstance(args[0], str):
                h = args[0].lstrip('#')
                if len(h) == 6: self.r, self.g, self.b = tuple(int(h[i:i+2], 16) for i in (0, 2, 4)); self.a = 255
                elif len(h) == 8: self.r, self.g, self.b, self.a = tuple(int(h[i:i+2], 16) for i in (0, 2, 4, 6))
                else: self.r = self.g = self.b = self.a = 255
            elif isinstance(args[0], QColor): self.r, self.g, self.b, self.a = args[0].r, args[0].g, args[0].b, args[0].a
            else: self.r = self.g = self.b = self.a = 255
        elif len(args) >= 3: self.r, self.g, self.b = args[:3]; self.a = args[3] if len(args) > 3 else 255
        else: self.r = self.g = self.b = 0; self.a = 255
    def to_pygame(self): return (self.r, self.g, self.b, self.a)

class QFont:
    def __init__(self, family="Arial", size=12): self._family, self._size = family, size
    def setPointSize(self, size): self._size = size
    def pointSize(self): return self._size

class QPixmap:
    def __init__(self, arg=None):
        if isinstance(arg, str): 
            try: self.surface = pygame.image.load(arg).convert_alpha()
            except: self.surface = None
        elif isinstance(arg, pygame.Surface): self.surface = arg
        elif isinstance(arg, QSize): self.surface = pygame.Surface((arg.width(), arg.height()), pygame.SRCALPHA)
        else: self.surface = None
    def width(self): return self.surface.get_width() if self.surface else 0
    def height(self): return self.surface.get_height() if self.surface else 0
    def rect(self): return QRectF(0, 0, self.width(), self.height())
    def scaledToWidth(self, w, mode=None):
        if not self.surface or self.width() == 0: return self
        h = int(self.height() * (w / self.width())); return QPixmap(pygame.transform.smoothscale(self.surface, (w, h)))
    def toImage(self): return QImage()
    def save(self, buffer, fmt="PNG"):
        if not self.surface: return False
        try:
            if isinstance(buffer, str):
                pygame.image.save(self.surface, buffer)
            else:
                # Handle QBuffer or file-like object
                import io
                temp = io.BytesIO()
                pygame.image.save(self.surface, temp, fmt.lower())
                if hasattr(buffer, 'write'):
                    buffer.write(temp.getvalue())
                elif hasattr(buffer, 'setData'):
                    buffer.setData(temp.getvalue())
            return True
        except:
            return False

class QImage:
    def __init__(self, *args): pass
    def isNull(self): return True

class QPainter:
    class RenderHint: Antialiasing = 1; SmoothPixmapTransform = 2
    def __init__(self, device=None): 
        self._device = device
        self._pen = QPen()
        self._brush = QBrush()
        self._state_stack = []  # Stack for save/restore
    def save(self):
        # Save current state
        self._state_stack.append({
            'pen': self._pen,
            'brush': self._brush
        })
    def restore(self):
        # Restore previous state
        if self._state_stack:
            state = self._state_stack.pop()
            self._pen = state['pen']
            self._brush = state['brush']
    def setPen(self, pen): self._pen = pen
    def setBrush(self, brush): self._brush = brush
    def drawRect(self, rect):
        if not self._device: return
        r = rect.toRect() if hasattr(rect, 'toRect') else rect
        pygame.draw.rect(self._device, (0,0,0), r, 1) # Simple black outline
    def drawPixmap(self, *args):
        if not self._device: return
        # Handle different signatures: drawPixmap(rect, pixmap) or drawPixmap(x, y, pixmap)
        if len(args) == 2:
            rect, pixmap = args
            if pixmap.surface:
                self._device.blit(pixmap.surface, (rect.x() if hasattr(rect, 'x') else rect[0], 
                                                   rect.y() if hasattr(rect, 'y') else rect[1]))
        elif len(args) == 3:
            x, y, pixmap = args
            if pixmap.surface:
                self._device.blit(pixmap.surface, (x, y))
    def drawText(self, *args):
        if not self._device: return
        # Handle different signatures: drawText(rect, flags, text) or drawText(x, y, text)
        if len(args) == 3:
            if isinstance(args[0], (int, float)):
                # drawText(x, y, text)
                x, y, text = args
                font = pygame.font.SysFont('Arial', 12)
                color = self._pen._color.to_pygame() if hasattr(self._pen._color, 'to_pygame') else (0, 0, 0)
                surface = font.render(str(text), True, color)
                self._device.blit(surface, (x, y))
            else:
                # drawText(rect, flags, text)
                rect, flags, text = args
                font = pygame.font.SysFont('Arial', 12)
                color = self._pen._color.to_pygame() if hasattr(self._pen._color, 'to_pygame') else (0, 0, 0)
                surface = font.render(str(text), True, color)
                r = rect.toRect() if hasattr(rect, 'toRect') else rect
                self._device.blit(surface, (r.x if hasattr(r, 'x') else r[0], 
                                           r.y if hasattr(r, 'y') else r[1]))
        elif len(args) == 2:
            # drawText(point, text)
            point, text = args
            font = pygame.font.SysFont('Arial', 12)
            color = self._pen._color.to_pygame() if hasattr(self._pen._color, 'to_pygame') else (0, 0, 0)
            surface = font.render(str(text), True, color)
            self._device.blit(surface, (point.x(), point.y()))

class QPen:
    def __init__(self, color=None, width=1, style=None):
        self._color = QColor(color) if color is not None else QColor(0,0,0)
        self._width = width
        self._style = style if style is not None else 1  # Qt.PenStyle.SolidLine
class QBrush:
    def __init__(self, color=None, style=None):
        self._color = QColor(color) if color is not None else QColor(0,0,0,0)
        self._style = style if style is not None else 1  # Qt.BrushStyle.SolidPattern
class QTransform:
    @staticmethod
    def fromScale(sx, sy): return QTransform()
    def m11(self): return 1.0
    def m22(self): return 1.0

class QIcon:
    def __init__(self, *args): (setattr(self, 'pixmap', args[0]) if args else None)
class QKeySequence:
    class StandardKey: Cut = 1; Copy = 2; Paste = 3
    @staticmethod
    def matches(k1, k2): return False

class QTextCursor:
    class SelectionType: Document = 1
    def __init__(self): pass
    def select(self, selection_type): pass
    def clearSelection(self): pass
