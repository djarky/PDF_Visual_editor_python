import pygame

class Qt:
    class Orientation: Horizontal = 1; Vertical = 2
    class WindowType: Widget = 0; Window = 1; Dialog = 2; Sheet = 3; Drawer = 4; Popup = 5; Tool = 6; ToolTip = 7; SplashScreen = 8
    class AlignmentFlag: AlignCenter = 0x0084; AlignRight = 0x0002; AlignLeft = 0x0001
    class MouseButton: LeftButton = 1; RightButton = 2; NoButton = 0
    class Key:
        Key_Delete = pygame.K_DELETE; Key_R = pygame.K_r; Key_J = pygame.K_j
        Key_Return = pygame.K_RETURN; Key_Enter = pygame.K_KP_ENTER; Key_Escape = pygame.K_ESCAPE
        Key_A = pygame.K_a; Key_C = pygame.K_c; Key_V = pygame.K_v; Key_X = pygame.K_x; Key_Z = pygame.K_z; Key_Y = pygame.K_y
    class KeyboardModifier: ControlModifier = pygame.KMOD_CTRL; AltModifier = pygame.KMOD_ALT; ShiftModifier = pygame.KMOD_SHIFT; NoModifier = 0
    class TransformationMode: SmoothTransformation = 1
    class CursorShape: ArrowCursor = pygame.SYSTEM_CURSOR_ARROW; CrossCursor = pygame.SYSTEM_CURSOR_CROSSHAIR; SizeFDiagCursor = pygame.SYSTEM_CURSOR_SIZENWSE
    class ItemDataRole: UserRole = 1000
    class CheckState: Checked = 2; Unchecked = 0
    class PenStyle: SolidLine = 1; DashLine = 2
    class BrushStyle: SolidPattern = 1; NoBrush = 0
    class TextInteractionFlag: NoTextInteraction = 0; TextEditorInteraction = 1
    class ContextMenuPolicy: CustomContextMenu = 1
    class ItemFlag: ItemIsEditable = 1
    class ContextMenuPolicy: CustomContextMenu = 1
    class ItemFlag: ItemIsEditable = 1
    class ItemFlag: ItemIsEditable = 1
    class TextFormat: PlainText = 0; RichText = 1
    class GlobalColor:
        white = "#FFFFFF"
        black = "#000000"
        red = "#FF0000"
        darkRed = "#800000"
        green = "#00FF00"
        darkGreen = "#008000"
        blue = "#0000FF"
        darkBlue = "#000080"
        cyan = "#00FFFF"
        darkCyan = "#008080"
        magenta = "#FF00FF"
        darkMagenta = "#800080"
        yellow = "#FFFF00"
        darkYellow = "#808000"
        gray = "#A0A0A4"
        darkGray = "#808080"
        lightGray = "#C0C0C0"
        transparent = "#00000000" # 8-digit hex for alpha? QColor in gui.py handles 8 digits.

class Signal:
    def __init__(self, *args): 
        self._slots = []
        self._blocked = False
    def connect(self, slot): (self._slots.append(slot) if slot not in self._slots else None)
    def disconnect(self, slot): (self._slots.remove(slot) if slot in self._slots else None)
    def emit(self, *args): 
        if not self._blocked:
            [slot(*args) for slot in self._slots]

class QObject:
    def __init__(self, parent=None):
        self._parent, self._children = parent, []
        self._signals_blocked = False
        (parent._children.append(self) if parent and hasattr(parent, '_children') else None)
    def parent(self): return self._parent
    def children(self): return self._children
    def blockSignals(self, b):
        old = self._signals_blocked
        self._signals_blocked = b
        # Apply to all Signals belonging to this object
        for attr in self.__dict__.values():
            if isinstance(attr, Signal):
                attr._blocked = b
        return old
    def signalsBlocked(self): return self._signals_blocked
    def isVisible(self): return getattr(self, '_visible', False)
    def show(self): self.setVisible(True)
    def hide(self): self.setVisible(False)
    def setVisible(self, v): self._visible = v
    def _handle_event(self, event, offset):
        for child in self._children:
            child._handle_event(event, offset)
    def _draw_recursive(self, pos=pygame.Vector2(0,0)):
        if self.isVisible():
            for child in self._children:
                child._draw_recursive(pos)

class QPointF:
    def __init__(self, x=0, y=0):
        if isinstance(x, (QPointF, tuple, list, pygame.Vector2)):
            if isinstance(x, (tuple, list, pygame.Vector2)): self._x, self._y = float(x[0]), float(x[1])
            else: self._x, self._y = float(x.x()), float(x.y())
        else: self._x, self._y = float(x), float(y)
    def x(self): return self._x
    def y(self): return self._y
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

class QRectF:
    def __init__(self, *args):
        if len(args) == 4: self._x, self._y, self._w, self._h = args
        elif len(args) == 2:
            if isinstance(args[0], QPointF) and isinstance(args[1], QPointF): self._x, self._y = args[0].x(), args[0].y(); self._w, self._h = args[1].x() - self._x, args[1].y() - self._y
            elif isinstance(args[0], QPointF) and isinstance(args[1], (int, float, QSize)):
                self._x, self._y = args[0].x(), args[0].y()
                self._w = args[1].width() if isinstance(args[1], QSize) else args[1]
                self._h = args[1].height() if isinstance(args[1], QSize) else args[1]
        elif len(args) == 1:
            if isinstance(args[0], pygame.Rect): self._x, self._y, self._w, self._h = args[0]
            elif isinstance(args[0], QRectF): self._x, self._y, self._w, self._h = args[0]._x, args[0]._y, args[0]._w, args[0]._h
        else: self._x = self._y = self._w = self._h = 0
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
    def toRect(self): return pygame.Rect(int(self._x), int(self._y), int(self._w), int(self._h))
    def intersected(self, other): return QRectF(self.toRect().clip(other.toRect()))
    def isEmpty(self): return self._w <= 0 or self._h <= 0
    def contains(self, p): return self._x <= p.x() <= self._x + self._w and self._y <= p.y() <= self._y + self._h

class QMouseEvent:
    def __init__(self, pos, button=Qt.MouseButton.NoButton, modifiers=Qt.KeyboardModifier.NoModifier):
        self._pos, self._button, self._modifiers = QPointF(pos), button, modifiers
    def pos(self): return self._pos
    def button(self): return self._button
    def buttons(self): return self._button  # For compatibility, return the same as button()
    def modifiers(self): return self._modifiers
    def ignore(self): pass

def pyqtSignal(*args): return Signal(*args)
