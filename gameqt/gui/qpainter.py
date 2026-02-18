import pygame
from ..core import Qt, QPointF
from .qcolor import QColor
from .qfont import QFont
from .qtransform import QTransform
from .qpen import QPen
from .qbrush import QBrush

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
        """Draw a rectangle outline without fill."""
        if not self._device: return
        
        # Convert color to pygame format
        fill_color = color.to_pygame() if hasattr(color, 'to_pygame') else color
        if isinstance(fill_color, tuple) and len(fill_color) == 4:
            # Has alpha, use as-is
            pass
        elif isinstance(fill_color, tuple) and len(fill_color) == 3:
            # RGB, add full alpha
            fill_color = fill_color + (255,)
        
        # Access coordinates safely
        x = rect.x() if hasattr(rect, 'x') and callable(rect.x) else getattr(rect, 'x', 0)
        y = rect.y() if hasattr(rect, 'y') and callable(rect.y) else getattr(rect, 'y', 0)
        w = rect.width() if hasattr(rect, 'width') and callable(rect.width) else getattr(rect, 'width', 0)
        h = rect.height() if hasattr(rect, 'height') and callable(rect.height) else getattr(rect, 'height', 0)
        
        # Apply transform
        tx, ty = self._transform._m[6], self._transform._m[7]
        sx, sy = self._transform._m[0], self._transform._m[4]
        
        nx, ny = int(x * sx + tx), int(y * sy + ty)
        nw, nh = int(w * sx), int(h * sy)
        r = pygame.Rect(nx, ny, nw, nh)
        
        # Draw outline only
        pygame.draw.rect(self._device, fill_color, r, width)


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
        from ..utils.text_renderer import render_text
        if len(args) == 3:
            if isinstance(args[0], (int, float)):
                # drawText(x, y, text)
                x, y, text = args
                p = self._transform.map(QPointF(x, y))
                color = self._pen._color.to_pygame()
                surface = render_text(str(text), self._font._family, self._font._size, color)
                self._device.blit(surface, (p.x(), p.y()))
            else:
                # drawText(rect, flags, text)
                rect, flags, text = args
                color = self._pen._color.to_pygame()
                surface = render_text(str(text), self._font._family, self._font._size, color)
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
            color = self._pen._color.to_pygame()
            surface = render_text(str(text), self._font._family, self._font._size, color)
            self._device.blit(surface, (p.x(), p.y()))
