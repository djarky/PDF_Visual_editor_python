from ..core import QPointF

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
