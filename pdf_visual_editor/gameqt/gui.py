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
    def red(self): return self.r
    def green(self): return self.g
    def blue(self): return self.b
    def alpha(self): return self.a

class QFont:
    def __init__(self, family="Arial", size=12): self._family, self._size = family, size
    def setPointSize(self, size): self._size = size
    def pointSize(self): return self._size

class QPixmap:
    def __init__(self, arg=None, h=None):
        if h is not None:
             self.surface = pygame.Surface((arg, h), pygame.SRCALPHA)
        elif isinstance(arg, str): 
            try: self.surface = pygame.image.load(arg).convert_alpha()
            except: self.surface = None
        elif isinstance(arg, pygame.Surface): self.surface = arg
        elif isinstance(arg, QSize): self.surface = pygame.Surface((arg.width(), arg.height()), pygame.SRCALPHA)
        else: self.surface = None
    @staticmethod
    def fromImage(img): return QPixmap(img.surface) if hasattr(img, 'surface') else QPixmap()
    def width(self): return self.surface.get_width() if self.surface else 0
    def height(self): return self.surface.get_height() if self.surface else 0
    def rect(self): return QRectF(0, 0, self.width(), self.height())
    def scaledToWidth(self, w, mode=None):
        if not self.surface or self.width() == 0: return self
        h = int(self.height() * (w / self.width())); return QPixmap(pygame.transform.smoothscale(self.surface, (w, h)))
    def toImage(self): return QImage(self.surface)
    def copy(self, rect):
        if not self.surface: return QPixmap()
        r = rect._to_pygame() if hasattr(rect, '_to_pygame') else (rect.toRect()._to_pygame() if hasattr(rect, 'toRect') else rect)
        # Ensure rect is within surface bounds to avoid pygame error
        surf_rect = self.surface.get_rect()
        clip_rect = surf_rect.clip(r)
        if clip_rect.width <= 0 or clip_rect.height <= 0:
            return QPixmap(pygame.Surface((1, 1), pygame.SRCALPHA))
        return QPixmap(self.surface.subsurface(clip_rect).copy())
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
    class Format:
        Format_RGB888 = 13
        Format_RGBA8888 = 26
    Format_RGB888 = 13
    Format_RGBA8888 = 26
    def __init__(self, *args):
        self.surface = None
        if len(args) == 1 and isinstance(args[0], pygame.Surface):
            self.surface = args[0]
        elif len(args) >= 3:
            if isinstance(args[0], (bytes, bytearray)):
                data, w, h, bpl, fmt = args
                mode = "RGBA" if fmt in (QImage.Format_RGBA8888, QImage.Format.Format_RGBA8888) else "RGB"
                self.surface = pygame.image.fromstring(bytes(data), (w, h), mode)
            else:
                w, h, fmt = args[:3]
                self.surface = pygame.Surface((w, h), pygame.SRCALPHA)
    def isNull(self): return self.surface is None

class QPainter:
    class RenderHint: Antialiasing = 1; SmoothPixmapTransform = 2
    def __init__(self, device=None): 
        self._device = device
        self._pen = QPen()
        self._brush = QBrush()
        self._font = QFont()
        self._transform = QTransform()
        self._state_stack = []  # Stack for save/restore
    def save(self):
        # Save current state
        self._state_stack.append({
            'pen': self._pen,
            'brush': self._brush,
            'font': self._font,
            'transform': QTransform(*self._transform._m[:2], *self._transform._m[3:5], *self._transform._m[6:8])
        })
    def restore(self):
        # Restore previous state
        if self._state_stack:
            state = self._state_stack.pop()
            self._pen = state['pen']
            self._brush = state['brush']
            self._font = state['font']
            self._transform = state['transform']
    def setPen(self, pen):
        if isinstance(pen, QColor):
            self._pen = QPen(pen)
        else:
            self._pen = pen
    def setBrush(self, brush):
        if isinstance(brush, QColor):
            self._brush = QBrush(brush)
        else:
            self._brush = brush
    def setFont(self, font): self._font = font
    def setTransform(self, transform): self._transform = transform
    def transform(self): return self._transform
    def translate(self, dx, dy): self._transform.translate(dx, dy)
    def scale(self, sx, sy): self._transform.scale(sx, sy)
    def rotate(self, angle): self._transform.rotate(angle)
    def fillRect(self, rect, color):
        if not self._device: return
        # Handle color or brush
        fill_color = color.to_pygame() if hasattr(color, 'to_pygame') else color
        if isinstance(fill_color, QColor): fill_color = fill_color.to_pygame()
        
        # Access coordinates safely
        x = rect.x() if hasattr(rect, 'x') and callable(rect.x) else getattr(rect, 'x', 0)
        y = rect.y() if hasattr(rect, 'y') and callable(rect.y) else getattr(rect, 'y', 0)
        w = rect.width() if hasattr(rect, 'width') and callable(rect.width) else getattr(rect, 'width', 0)
        h = rect.height() if hasattr(rect, 'height') and callable(rect.height) else getattr(rect, 'height', 0)
        
        tx, ty = self._transform._m[6], self._transform._m[7]
        sx, sy = self._transform._m[0], self._transform._m[4]
        
        nx, ny = int(x * sx + tx), int(y * sy + ty)
        nw, nh = int(w * sx), int(h * sy)
        r = pygame.Rect(nx, ny, nw, nh)
        
        pygame.draw.rect(self._device, fill_color, r)

    def strokeRect(self, rect, color, width=1):
        # Helper for common Qt-like tasks if needed
        pass

    def drawRect(self, rect):
        if not self._device: return
        # Access coordinates safely
        x = rect.x() if hasattr(rect, 'x') and callable(rect.x) else getattr(rect, 'x', 0)
        y = rect.y() if hasattr(rect, 'y') and callable(rect.y) else getattr(rect, 'y', 0)
        w = rect.width() if hasattr(rect, 'width') and callable(rect.width) else getattr(rect, 'width', 0)
        h = rect.height() if hasattr(rect, 'height') and callable(rect.height) else getattr(rect, 'height', 0)
        
        tx, ty = self._transform._m[6], self._transform._m[7]
        sx, sy = self._transform._m[0], self._transform._m[4]
        
        nx, ny = int(x * sx + tx), int(y * sy + ty)
        nw, nh = int(w * sx), int(h * sy)
        r = pygame.Rect(nx, ny, nw, nh)
        
        # Fill
        if self._brush._style == 1: # SolidPattern
            pygame.draw.rect(self._device, self._brush._color.to_pygame(), r)
        elif self._brush._style == 2 and hasattr(self._brush, '_gradient'):
            # Simple Vertical Gradient
            grad = self._brush._gradient
            if len(grad._stops) >= 2:
                c1 = grad._stops[0][1].to_pygame(); c2 = grad._stops[-1][1].to_pygame()
                for i in range(r.height):
                    ratio = i / r.height
                    c = [int(c1[j]*(1-ratio) + c2[j]*ratio) for j in range(3)]
                    pygame.draw.line(self._device, c, (r.x, r.y + i), (r.x + r.width, r.y + i))
            else: pygame.draw.rect(self._device, (200, 200, 200), r)
        
        # Stroke
        if self._pen._style > 0:
            pygame.draw.rect(self._device, self._pen._color.to_pygame(), r, self._pen._width)
    def drawLine(self, *args):
        if not self._device: return
        p1, p2 = (args[0], args[1]) if len(args) == 2 else (QPointF(args[0], args[1]), QPointF(args[2], args[3]))
        p1_t, p2_t = self._transform.map(p1), self._transform.map(p2)
        pygame.draw.line(self._device, self._pen._color.to_pygame(), (p1_t.x(), p1_t.y()), (p2_t.x(), p2_t.y()), self._pen._width)
    def drawEllipse(self, rect):
        if not self._device: return
        x = rect.x() if hasattr(rect, 'x') and callable(rect.x) else getattr(rect, 'x', 0)
        y = rect.y() if hasattr(rect, 'y') and callable(rect.y) else getattr(rect, 'y', 0)
        w = rect.width() if hasattr(rect, 'width') and callable(rect.width) else getattr(rect, 'width', 0)
        h = rect.height() if hasattr(rect, 'height') and callable(rect.height) else getattr(rect, 'height', 0)
        
        tx, ty = self._transform._m[6], self._transform._m[7]
        sx, sy = self._transform._m[0], self._transform._m[4]
        nx, ny = int(x * sx + tx), int(y * sy + ty)
        nw, nh = int(w * sx), int(h * sy)
        r = pygame.Rect(nx, ny, nw, nh)
        if self._brush._style == 1: pygame.draw.ellipse(self._device, self._brush._color.to_pygame(), r)
        if self._pen._style > 0: pygame.draw.ellipse(self._device, self._pen._color.to_pygame(), r, self._pen._width)
    def drawPolygon(self, points):
        if not self._device: return
        pts = [(p.x(), p.y()) for p in [self._transform.map(p) for p in points]]
        if self._brush._style == 1: pygame.draw.polygon(self._device, self._brush._color.to_pygame(), pts)
        if self._pen._style > 0: pygame.draw.polygon(self._device, self._pen._color.to_pygame(), pts, self._pen._width)
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
                p = self._transform.map(QPointF(x, y))
                font = pygame.font.SysFont(self._font._family, self._font._size)
                color = self._pen._color.to_pygame()
                surface = font.render(str(text), True, color)
                self._device.blit(surface, (p.x(), p.y()))
            else:
                # drawText(rect, flags, text)
                rect, flags, text = args
                font = pygame.font.SysFont(self._font._family, self._font._size)
                color = self._pen._color.to_pygame()
                surface = font.render(str(text), True, color)
                r = rect.toRect() if hasattr(rect, 'toRect') else rect
                
                # Alignment logic
                tx = r.x() if hasattr(r, 'x') and callable(r.x) else getattr(r, 'x', 0)
                ty = r.y() if hasattr(r, 'y') and callable(r.y) else getattr(r, 'y', 0)
                rw = r.width() if hasattr(r, 'width') and callable(r.width) else getattr(r, 'width', 0)
                rh = r.height() if hasattr(r, 'height') and callable(r.height) else getattr(r, 'height', 0)
                tw, th = surface.get_size()
                
                if flags & Qt.AlignmentFlag.AlignRight: tx = tx + rw - tw
                elif flags & Qt.AlignmentFlag.AlignHCenter: tx = tx + (rw - tw) // 2
                
                if flags & Qt.AlignmentFlag.AlignBottom: ty = ty + rh - th
                elif flags & Qt.AlignmentFlag.AlignVCenter: ty = ty + (rh - th) // 2
                
                p = self._transform.map(QPointF(tx, ty))
                self._device.blit(surface, (p.x(), p.y()))
        elif len(args) == 2:
            # drawText(point, text)
            point, text = args
            p = self._transform.map(point)
            font = pygame.font.SysFont(self._font._family, self._font._size)
            color = self._pen._color.to_pygame()
            surface = font.render(str(text), True, color)
            self._device.blit(surface, (p.x(), p.y()))

class QPen:
    def __init__(self, color=None, width=1, style=None):
        self._color = QColor(color) if color is not None else QColor(0,0,0)
        self._width = width
        self._style = style if style is not None else 1  # Qt.PenStyle.SolidLine
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
class QTransform:
    def __init__(self, m11=1.0, m12=0.0, m21=0.0, m22=1.0, dx=0.0, dy=0.0):
        if isinstance(m11, (list, tuple)) and len(m11) == 9:
            self._m = list(m11)
        else:
            self._m = [m11, m12, 0.0, m21, m22, 0.0, dx, dy, 1.0]
    def translate(self, dx, dy):
        self._m[6] += dx * self._m[0] + dy * self._m[3]
        self._m[7] += dx * self._m[1] + dy * self._m[4]
        return self
    def scale(self, sx, sy):
        self._m[0] *= sx; self._m[1] *= sx
        self._m[3] *= sy; self._m[4] *= sy
        return self
    def rotate(self, angle): # angle in degrees
        import math
        rad = math.radians(angle)
        c, s = math.cos(rad), math.sin(rad)
        m11, m12, m21, m22 = self._m[0], self._m[1], self._m[3], self._m[4]
        self._m[0] = m11 * c + m21 * s
        self._m[1] = m12 * c + m22 * s
        self._m[3] = m11 * -s + m21 * c
        self._m[4] = m12 * -s + m22 * c
        return self
    def map(self, p):
        x, y = (p.x(), p.y()) if hasattr(p, 'x') else (p[0], p[1])
        nx = x * self._m[0] + y * self._m[3] + self._m[6]
        ny = x * self._m[1] + y * self._m[4] + self._m[7]
        return QPointF(nx, ny)
    @staticmethod
    def fromScale(sx, sy): return QTransform().scale(sx, sy)
    def m11(self): return self._m[0]
    def m22(self): return self._m[4]

class QIcon:
    def __init__(self, *args): (setattr(self, 'pixmap', args[0]) if args else None)
class QKeySequence:
    class StandardKey: Cut = 1; Copy = 2; Paste = 3
    def __init__(self, key_str):
        self._key_str = key_str
        self._keys = []
        self._modifiers = 0
        
        parts = key_str.split('+')
        for p in parts:
            p = p.strip().upper()
            if p == 'CTRL': self._modifiers |= pygame.KMOD_CTRL
            elif p == 'ALT': self._modifiers |= pygame.KMOD_ALT
            elif p == 'SHIFT': self._modifiers |= pygame.KMOD_SHIFT
            else:
                # Try to find the key in pygame constants
                try: 
                    k_attr = f"K_{p.lower()}" if len(p) == 1 else f"K_{p}"
                    self._keys.append(getattr(pygame, k_attr))
                except: pass
    
    def matches(self, key, mods):
        # Simplistic check
        if not self._keys: return False
        return key == self._keys[0] and (mods & self._modifiers) == self._modifiers

    @staticmethod
    def matches_static(k1, k2): 
        # k1 and k2 are likely QKeySequence or strings
        s1 = k1._key_str if hasattr(k1, '_key_str') else str(k1)
        s2 = k2._key_str if hasattr(k2, '_key_str') else str(k2)
        return s1.upper() == s2.upper()

class QTextCursor:
    class SelectionType: Document = 1; BlockUnderCursor = 2; LineUnderCursor = 3; WordUnderCursor = 4
    def __init__(self):
        self._pos = 0
        self._anchor = 0
    def position(self): return self._pos
    def setPosition(self, pos, mode=0): # mode 1 is KeepAnchor
        self._pos = pos
        if mode == 0: self._anchor = pos
    def anchor(self): return self._anchor
    def select(self, selection_type):
        if selection_type == QTextCursor.SelectionType.Document:
            self._anchor = 0
            # We don't know the end, so we can't fully implement without doc reference. 
            # But this is a data object, usually created by a document/edit.
            # We'll just assume a large number if no doc? Or just set to 0?
            pass 
        elif selection_type == QTextCursor.SelectionType.WordUnderCursor:
             # Placeholder logic for selecting word
             self._anchor = max(0, self._pos - 5)
             self._pos = self._pos + 5
             
    def selectionStart(self): return min(self._pos, self._anchor)
    def selectionEnd(self): return max(self._pos, self._anchor)
    def clearSelection(self): self._anchor = self._pos
    def hasSelection(self): return self._pos != self._anchor
    
    def selectedText(self): 
        # Needs reference to text. 
        # If this cursor is attached to a document, we could get it.
        if hasattr(self, '_document') and self._document:
             return self._document.toPlainText()[self.selectionStart():self.selectionEnd()]
        return ""
