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
        self._opacity = 1.0

    def setOpacity(self, opacity): self._opacity = opacity
    def opacity(self): return self._opacity

    def _apply_opacity(self, color):
        """Helper to apply painter opacity to a color."""
        c = color.to_pygame() if hasattr(color, 'to_pygame') else color
        if hasattr(c, 'to_pygame'): c = c.to_pygame() # Handle QColor passed directly
        if len(c) < 4: c = (*c, 255)
        return (c[0], c[1], c[2], int(c[3] * self._opacity))
    def save(self):
        # Save current state
        self._state_stack.append({
            'pen': self._pen,
            'brush': self._brush,
            'font': self._font,
            'font': self._font,
            'transform': QTransform(*self._transform._m[:2], *self._transform._m[3:5], *self._transform._m[6:8]),
            'opacity': self._opacity
        })

    def _draw_via_temp_surface(self, rect, draw_callback):
        """Draws to a temporary surface to support alpha blending."""
        if rect.width <= 0 or rect.height <= 0: return
        
        # Create temp surface
        surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        
        # Callback draws to surface at (0,0) offset
        draw_callback(surf, -rect.x, -rect.y)
        
        # Blit to device
        self._device.blit(surf, (rect.x, rect.y))
    def restore(self):
        # Restore previous state
        if self._state_stack:
            state = self._state_stack.pop()
            self._pen = state['pen']
            self._brush = state['brush']
            self._font = state['font']
            self._transform = state['transform']
            self._opacity = state.get('opacity', 1.0)
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
        fill_color = self._apply_opacity(color)
        
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
        
        if fill_color[3] < 255:
            # Transparent draw
            def draw_cmd(surf, ox, oy):
                offset_r = pygame.Rect(r.x + ox, r.y + oy, r.width, r.height)
                pygame.draw.rect(surf, fill_color, offset_r)
            self._draw_via_temp_surface(r, draw_cmd)
        else:
            pygame.draw.rect(self._device, fill_color, r)

    def strokeRect(self, rect, color, width=1):
        """Draw a rectangle outline without fill."""
        if not self._device: return
        
        # Convert color to pygame format
        fill_color = self._apply_opacity(color)
        
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
        if fill_color[3] < 255:
            def draw_cmd(surf, ox, oy):
                offset_r = pygame.Rect(r.x + ox, r.y + oy, r.width, r.height)
                pygame.draw.rect(surf, fill_color, offset_r, width)
            self._draw_via_temp_surface(r, draw_cmd)
        else:
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
            col = self._apply_opacity(self._brush._color)
            if col[3] < 255:
                def draw_f(surf, ox, oy):
                    pygame.draw.rect(surf, col, (r.x + ox, r.y + oy, r.width, r.height))
                self._draw_via_temp_surface(r, draw_f)
            else:
                pygame.draw.rect(self._device, col, r)
        elif self._brush._style == 2 and hasattr(self._brush, '_gradient'):
            # Simple Vertical Gradient (Opacity handling difficult here, skipping for simplicity or applying to lines)
            grad = self._brush._gradient
            if len(grad._stops) >= 2:
                # ... existing gradient logic needs opacity application per line ...
                # Simplified: just draw opaque or apply simple global alpha?
                # Let's apply alpha to stops
                c1_full = grad._stops[0][1].to_pygame()
                c2_full = grad._stops[-1][1].to_pygame()
                # Apply opacity
                c1 = (*c1_full[:3], int((c1_full[3] if len(c1_full)>3 else 255) * self._opacity))
                c2 = (*c2_full[:3], int((c2_full[3] if len(c2_full)>3 else 255) * self._opacity))
                
                # If transparent, we need temp surface for whole rect
                use_temp = c1[3] < 255 or c2[3] < 255
                
                def draw_g(target, ox, oy):
                    rx, ry = r.x + ox, r.y + oy
                    for i in range(r.height):
                        ratio = i / r.height
                        c = [int(c1[j]*(1-ratio) + c2[j]*ratio) for j in range(3)]
                        alpha = int(c1[3]*(1-ratio) + c2[3]*ratio)
                        if len(c) == 3: c.append(alpha)
                        else: c[3] = alpha
                        pygame.draw.line(target, c, (rx, ry + i), (rx + r.width, ry + i))
                
                if use_temp: self._draw_via_temp_surface(r, draw_g)
                else: draw_g(self._device, 0, 0)
            else: 
                col = (200, 200, 200, int(255 * self._opacity))
                if col[3] < 255:
                     self._draw_via_temp_surface(r, lambda s,x,y: pygame.draw.rect(s, col, (r.x+x, r.y+y, r.width, r.height)))
                else:
                     pygame.draw.rect(self._device, col, r)
        
        # Stroke
        if self._pen._style > 0:
            col = self._apply_opacity(self._pen._color)
            if col[3] < 255:
                def draw_s(surf, ox, oy):
                    pygame.draw.rect(surf, col, (r.x + ox, r.y + oy, r.width, r.height), self._pen._width)
                self._draw_via_temp_surface(r, draw_s)
            else:
                pygame.draw.rect(self._device, col, r, self._pen._width)
    def drawLine(self, *args):
        if not self._device: return
        p1, p2 = (args[0], args[1]) if len(args) == 2 else (QPointF(args[0], args[1]), QPointF(args[2], args[3]))
        col = self._apply_opacity(self._pen._color)
        if col[3] < 255:
            # Lines need a bounding rect for temp surface
            x1, y1 = p1_t.x(), p1_t.y()
            x2, y2 = p2_t.x(), p2_t.y()
            bx, by = min(x1, x2), min(y1, y2)
            bw, bh = abs(x1 - x2) + self._pen._width*2, abs(y1 - y2) + self._pen._width*2
            r = pygame.Rect(bx, by, bw, bh)
            def draw_l(surf, ox, oy):
                pygame.draw.line(surf, col, (x1+ox, y1+oy), (x2+ox, y2+oy), self._pen._width)
            self._draw_via_temp_surface(r, draw_l)
        else:
            pygame.draw.line(self._device, col, (p1_t.x(), p1_t.y()), (p2_t.x(), p2_t.y()), self._pen._width)
            
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
        
        if self._brush._style == 1: 
            col = self._apply_opacity(self._brush._color)
            if col[3] < 255:
                # Ellipse bounds are r
                self._draw_via_temp_surface(r, lambda s,x,y: pygame.draw.ellipse(s, col, (r.x+x, r.y+y, r.width, r.height)))
            else:
                pygame.draw.ellipse(self._device, col, r)
                
        if self._pen._style > 0: 
            col = self._apply_opacity(self._pen._color)
            if col[3] < 255:
                self._draw_via_temp_surface(r, lambda s,x,y: pygame.draw.ellipse(s, col, (r.x+x, r.y+y, r.width, r.height), self._pen._width))
            else:
                pygame.draw.ellipse(self._device, col, r, self._pen._width)
            
    def drawPolygon(self, points):
        if not self._device: return
        pts = [(p.x(), p.y()) for p in [self._transform.map(p) for p in points]]
        
        # Calculate bounding rect for temp surface
        if not pts: return
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        r = pygame.Rect(min_x, min_y, max_x - min_x + 1, max_y - min_y + 1)
        
        if self._brush._style == 1: 
            col = self._apply_opacity(self._brush._color)
            if col[3] < 255:
                def draw_bp(surf, ox, oy):
                    off_pts = [(p[0]+ox, p[1]+oy) for p in pts]
                    pygame.draw.polygon(surf, col, off_pts)
                self._draw_via_temp_surface(r, draw_bp)
            else:
                pygame.draw.polygon(self._device, col, pts)
                
        if self._pen._style > 0: 
            col = self._apply_opacity(self._pen._color)
            if col[3] < 255:
                def draw_pp(surf, ox, oy):
                    off_pts = [(p[0]+ox, p[1]+oy) for p in pts]
                    pygame.draw.polygon(surf, col, off_pts, self._pen._width)
                self._draw_via_temp_surface(r, draw_pp)
            else:
                pygame.draw.polygon(self._device, col, pts, self._pen._width)
    def drawPixmap(self, *args):
        if not self._device: return
        # Handle different signatures: drawPixmap(rect, pixmap) or drawPixmap(x, y, pixmap)
        # Get transform parameters
        tx, ty = self._transform._m[6], self._transform._m[7]
        sx, sy = self._transform._m[0], self._transform._m[4]

        if len(args) == 2:
            rect, pixmap = args
            if pixmap.surface:
                # Calculate target rect in device/screen coordinates
                x = rect.x() if hasattr(rect, 'x') and callable(rect.x) else getattr(rect, 'x', 0)
                y = rect.y() if hasattr(rect, 'y') and callable(rect.y) else getattr(rect, 'y', 0)
                w = rect.width() if hasattr(rect, 'width') and callable(rect.width) else getattr(rect, 'width', 0)
                h = rect.height() if hasattr(rect, 'height') and callable(rect.height) else getattr(rect, 'height', 0)
                
                nx, ny = int(x * sx + tx), int(y * sy + ty)
                nw, nh = max(1, int(w * sx)), max(1, int(h * sy))
                
                # Get scaled surface (cached in QPixmap)
                scaled_surf = pixmap._get_scaled_surface(nw, nh) if hasattr(pixmap, '_get_scaled_surface') else None
                if not scaled_surf and pixmap.surface:
                     try: scaled_surf = pygame.transform.scale(pixmap.surface, (nw, nh))
                     except: pass
                
                if scaled_surf:
                    if self._opacity < 1.0:
                        scaled_surf.set_alpha(int(self._opacity * 255))
                    self._device.blit(scaled_surf, (nx, ny))

        elif len(args) == 3:
            x, y, pixmap = args
            if pixmap.surface:
                # Calculate target position and size
                nx, ny = int(x * sx + tx), int(y * sy + ty)
                nw = max(1, int(pixmap.width() * sx))
                nh = max(1, int(pixmap.height() * sy))
                
                # Get scaled surface
                scaled_surf = pixmap._get_scaled_surface(nw, nh) if hasattr(pixmap, '_get_scaled_surface') else None
                if not scaled_surf:
                     try: scaled_surf = pygame.transform.scale(pixmap.surface, (nw, nh))
                     except: pass

                if scaled_surf:
                    if self._opacity < 1.0:
                        scaled_surf.set_alpha(int(self._opacity * 255))
                    self._device.blit(scaled_surf, (nx, ny))
    def drawText(self, *args):
        if not self._device: return
        # Handle different signatures: drawText(rect, flags, text) or drawText(x, y, text)
        from ..utils.text_renderer import render_text
        # Get transform parameters
        tx, ty = self._transform._m[6], self._transform._m[7]
        sx, sy = self._transform._m[0], self._transform._m[4]
        
        # Calculate effective font size
        # We use sy (vertical scale) as the primary scale for font size
        effective_size = max(4, int(self._font._size * sy))
        effective_font_family = self._font._family
        
        if len(args) == 3:
            if isinstance(args[0], (int, float)):
                # drawText(x, y, text)
                x, y, text = args
                nx, ny = x * sx + tx, y * sy + ty
                color = self._apply_opacity(self._pen._color)
                surface = render_text(str(text), effective_font_family, effective_size, color)
                if self._opacity < 1.0: surface.set_alpha(int(self._opacity * 255))
                self._device.blit(surface, (nx, ny))
            else:
                # drawText(rect, flags, text)
                rect, flags, text = args
                color = self._apply_opacity(self._pen._color)
                surface = render_text(str(text), effective_font_family, effective_size, color)
                if self._opacity < 1.0: surface.set_alpha(int(self._opacity * 255))
                r = rect.toRect() if hasattr(rect, 'toRect') else rect
                
                # ...
                
                rx = r.x() if hasattr(r, 'x') and callable(r.x) else getattr(r, 'x', 0)
                ry = r.y() if hasattr(r, 'y') and callable(r.y) else getattr(r, 'y', 0)
                rw = r.width() if hasattr(r, 'width') and callable(r.width) else getattr(r, 'width', 0)
                rh = r.height() if hasattr(r, 'height') and callable(r.height) else getattr(r, 'height', 0)
                
                # Transform rect
                nrx, nry = rx * sx + tx, ry * sy + ty
                nrw, nrh = rw * sx, rh * sy
                
                tw, th = surface.get_size()
                
                # Calculate aligned position in device coords
                draw_x, draw_y = nrx, nry
                
                if flags & Qt.AlignmentFlag.AlignRight: draw_x = nrx + nrw - tw
                elif flags & Qt.AlignmentFlag.AlignHCenter: draw_x = nrx + (nrw - tw) // 2
                
                if flags & Qt.AlignmentFlag.AlignBottom: draw_y = nry + nrh - th
                elif flags & Qt.AlignmentFlag.AlignVCenter: draw_y = nry + (nrh - th) // 2
                
                self._device.blit(surface, (draw_x, draw_y))

        elif len(args) == 2:
            # drawText(point, text)
            point, text = args
            nx, ny = point.x() * sx + tx, point.y() * sy + ty
            color = self._apply_opacity(self._pen._color)
            surface = render_text(str(text), effective_font_family, effective_size, color)
            if self._opacity < 1.0: surface.set_alpha(int(self._opacity * 255))
            self._device.blit(surface, (nx, ny))
