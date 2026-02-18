import pygame

class QPoint:
    def __init__(self, x=0, y=0):
        if isinstance(x, (QPoint, tuple, list, pygame.Vector2)): # QPointF handled by duck typing mostly
            if isinstance(x, (tuple, list, pygame.Vector2)): self._x, self._y = int(x[0]), int(x[1])
            elif hasattr(x, 'x'): self._x, self._y = int(x.x()), int(x.y())
            else: self._x, self._y = int(x), int(y) # Fallback
        else: self._x, self._y = int(x), int(y)
    def x(self): return self._x
    def y(self): return self._y

class QPointF:
    def __init__(self, x=0, y=0):
        if isinstance(x, (QPointF, tuple, list, pygame.Vector2, QPoint)):
            if isinstance(x, (tuple, list, pygame.Vector2)): self._x, self._y = float(x[0]), float(x[1])
            elif hasattr(x, 'x'): self._x, self._y = float(x.x()), float(x.y())
            else: self._x, self._y = float(x), float(y)
        else: self._x, self._y = float(x), float(y)
    def x(self): return self._x
    def y(self): return self._y
    def toPoint(self): return QPoint(self._x, self._y)
    def setX(self, x): self._x = float(x)
    def setY(self, y): self._y = float(y)
    def __getitem__(self, i): return [self._x, self._y][i]
    def __add__(self, other): 
        o = QPointF(other); return QPointF(self._x + o.x(), self._y + o.y())
    def __sub__(self, other):
        o = QPointF(other); return QPointF(self._x - o.x(), self._y - o.y())
    def __mul__(self, factor): return QPointF(self._x * factor, self._y * factor)

class QSize:
    def __init__(self, w=0, h=0): self._w, self._h = w, h
    def width(self): return self._w
    def height(self): return self._h

class QRect:
    def __init__(self, *args):
        if len(args) == 4: self._x, self._y, self._w, self._h = [int(a) for a in args]
        elif len(args) == 1:
            if isinstance(args[0], pygame.Rect): self._x, self._y, self._w, self._h = args[0].x, args[0].y, args[0].width, args[0].height
            elif hasattr(args[0], 'x'): self._x, self._y, self._w, self._h = int(args[0].x()), int(args[0].y()), int(args[0].width()), int(args[0].height())
        else: self._x = self._y = self._w = self._h = 0
    def x(self): return self._x
    def y(self): return self._y
    def width(self): return self._w
    def height(self): return self._h
    def isEmpty(self): return self._w <= 0 or self._h <= 0
    def _to_pygame(self): return pygame.Rect(self._x, self._y, self._w, self._h)
    def intersected(self, other):
        r1 = self._to_pygame()
        r2 = other._to_pygame() if hasattr(other, '_to_pygame') else pygame.Rect(int(other.x()), int(other.y()), int(other.width()), int(other.height()))
        return QRect(r1.clip(r2))
    def toRect(self): return self
    def contains(self, p): return self._x <= p.x() <= self._x + self._w and self._y <= p.y() <= self._y + self._h

class QRectF:
    def __init__(self, *args):
        if len(args) == 4: self._x, self._y, self._w, self._h = [float(a) for a in args]
        elif len(args) == 2:
            if isinstance(args[0], QPointF) and isinstance(args[1], QPointF): 
                self._x, self._y = min(args[0].x(), args[1].x()), min(args[0].y(), args[1].y())
                self._w, self._h = abs(args[0].x() - args[1].x()), abs(args[0].y() - args[1].y())
            elif isinstance(args[0], QPointF) and isinstance(args[1], (int, float, QSize)):
                self._x, self._y = args[0].x(), args[0].y()
                self._w = float(args[1].width()) if isinstance(args[1], QSize) else float(args[1])
                self._h = float(args[1].height()) if isinstance(args[1], QSize) else float(args[1])
            else: self._x, self._y = float(args[0]), float(args[1]); self._w, self._h = 0.0, 0.0
        elif len(args) == 1:
            if isinstance(args[0], pygame.Rect): self._x, self._y, self._w, self._h = float(args[0].x), float(args[0].y), float(args[0].width), float(args[0].height)
            elif isinstance(args[0], (QRectF, QRect)): self._x, self._y, self._w, self._h = float(args[0].x()), float(args[0].y()), float(args[0].width()), float(args[0].height())
        else: self._x = self._y = self._w = self._h = 0.0
    def x(self): return self._x
    def y(self): return self._y
    def width(self): return self._w
    def height(self): return self._h
    def topLeft(self): return QPointF(self._x, self._y)
    def bottomRight(self): return QPointF(self._x + self._w, self._y + self._h)
    def center(self): return QPointF(self._x + self._w/2, self._y + self._h/2)
    def normalized(self):
        x, y, w, h = self._x, self._y, self._w, self._h
        if w < 0: x += w; w = abs(w)
        if h < 0: y += h; h = abs(h)
        return QRectF(x, y, w, h)
    def toRect(self): return QRect(int(self._x), int(self._y), int(self._w), int(self._h))
    def intersected(self, other):
        r1 = self.toRect()._to_pygame()
        r2 = other.toRect()._to_pygame() if hasattr(other, 'toRect') else pygame.Rect(int(other.x()), int(other.y()), int(other.width()), int(other.height()))
        return QRectF(r1.clip(r2))
    def isEmpty(self): return self._w <= 0 or self._h <= 0
    def contains(self, p): return self._x <= p.x() <= self._x + self._w and self._y <= p.y() <= self._y + self._h
    def intersects(self, other):
        return not (self._x + self._w <= other.x() or
                    other.x() + other.width() <= self._x or
                    self._y + self._h <= other.y() or
                    other.y() + other.height() <= self._y)
    def boundingRect(self): return self
