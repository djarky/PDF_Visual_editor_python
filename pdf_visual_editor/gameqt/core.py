import pygame

class Qt:
    class Orientation: Horizontal = 1; Vertical = 2
    class WindowType: Widget = 0; Window = 1; Dialog = 2; Sheet = 3; Drawer = 4; Popup = 5; Tool = 6; ToolTip = 7; SplashScreen = 8
    class AlignmentFlag: 
        AlignLeft = 0x0001
        AlignRight = 0x0002
        AlignHCenter = 0x0004
        AlignTop = 0x0020
        AlignBottom = 0x0040
        AlignVCenter = 0x0080
        AlignCenter = AlignHCenter | AlignVCenter
    class MouseButton: LeftButton = 0x01; RightButton = 0x02; MidButton = 0x04; NoButton = 0x00
    DROPFILE = pygame.DROPFILE
    DROPBEGIN = pygame.DROPBEGIN
    DROPCOMPLETE = pygame.DROPCOMPLETE
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
        if parent and hasattr(parent, '_children'):
            if self not in parent._children:
                parent._children.append(self)
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
    def intersects(self, other):
        return not (self._x + self._w <= other.x() or
                    other.x() + other.width() <= self._x or
                    self._y + self._h <= other.y() or
                    other.y() + other.height() <= self._y)

class QUrl:
    def __init__(self, path=""): self._path = path
    def toLocalFile(self):
        # Handle file:/// URLs (file:// + /absolute/path)
        if self._path.startswith('file://'):
            return self._path[7:]  # Remove 'file://' keeping the leading /
        return self._path
    def toString(self): return self._path

class QMimeData:
    def __init__(self): self._data = {}; self._urls = []
    def setText(self, t): self._data['text/plain'] = t.encode('utf-8')
    def text(self): return self._data.get('text/plain', b'').decode('utf-8')
    def hasText(self): return 'text/plain' in self._data
    def setUrls(self, urls): self._urls = urls
    def urls(self): return self._urls
    def hasUrls(self): return len(self._urls) > 0
    def setData(self, mime, data): self._data[mime] = data
    def data(self, mime): return self._data.get(mime, b'')
    def hasImage(self): return 'image/png' in self._data or 'image/jpeg' in self._data

class QClipboard:
    def __init__(self):
        self._fallback_text = ""
        self._scrap_available = False
        try:
            pygame.scrap.init()
            self._scrap_available = True
        except:
            pass
    
    def setText(self, text):
        self._fallback_text = text
        if self._scrap_available:
            try:
                pygame.scrap.put(pygame.SCRAP_TEXT, text.encode('utf-8'))
            except:
                pass
    
    def text(self):
        if self._scrap_available:
            try:
                res = pygame.scrap.get(pygame.SCRAP_TEXT)
                if res:
                    return res.decode('utf-8')
            except:
                pass
        return self._fallback_text
    
    def setMimeData(self, mime):
        if mime.hasText(): self.setText(mime.text())
    
    def mimeData(self):
        m = QMimeData()
        t = self.text()
        if t: m.setText(t)
        return m

class QMouseEvent:
    def __init__(self, pos, button=Qt.MouseButton.NoButton, buttons=None, modifiers=Qt.KeyboardModifier.NoModifier):
        self._pos = QPointF(pos)
        self._button = button
        self._buttons = buttons if buttons is not None else button
        self._modifiers = modifiers
        self._accepted = True
    def pos(self): return self._pos
    def button(self): return self._button
    def position(self): return self._pos
    def buttons(self): return self._buttons
    def modifiers(self): return self._modifiers
    def accept(self): self._accepted = True
    def ignore(self): self._accepted = False
    def isAccepted(self): return self._accepted

class QPoint:
    def __init__(self, x=0, y=0):
        if isinstance(x, (QPoint, QPointF, tuple, list, pygame.Vector2)):
            if isinstance(x, (tuple, list, pygame.Vector2)): self._x, self._y = int(x[0]), int(x[1])
            else: self._x, self._y = int(x.x()), int(x.y())
        else: self._x, self._y = int(x), int(y)
    def x(self): return self._x
    def y(self): return self._y

class QWheelEvent:
    def __init__(self, pos, angleDelta, modifiers=Qt.KeyboardModifier.NoModifier):
        self._pos = QPointF(pos)
        self._angleDelta = QPoint(angleDelta.x(), angleDelta.y())
        self._modifiers = modifiers
        self._accepted = True
    def pos(self): return self._pos
    def angleDelta(self): return self._angleDelta
    def pixelDelta(self): return self._angleDelta 
    def modifiers(self): return self._modifiers
    def accept(self): self._accepted = True
    def ignore(self): self._accepted = False
    def isAccepted(self): return self._accepted

def pyqtSignal(*args): return Signal(*args)

class PyGameModalDialog:
    def __init__(self, title="Dialog", width=400, height=300):
        self.title = title
        self.rect = pygame.Rect(0, 0, width, height)
        self.result = None
        self.running = False
        
    def exec_(self):
        screen = pygame.display.get_surface()
        if not screen: return
        
        # Capture background
        bg = screen.copy()
        
        # Center dialog
        sw, sh = screen.get_size()
        self.rect.center = (sw // 2, sh // 2)
        
        clock = pygame.time.Clock()
        self.running = True
        
        while self.running:
            # Event Loop
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                    self.result = None
                elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
                    # Handle mouse interaction with dialog elements
                    self.handle_event(event) # Custom handler
                elif event.type == pygame.KEYDOWN:
                    self.handle_key(event)
            
            # Draw
            screen.blit(bg, (0, 0))
            
            # Dim background
            overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 100))
            screen.blit(overlay, (0, 0))
            
            # Draw Dialog
            self.draw(screen)
            
            pygame.display.flip()
            clock.tick(60)
            
        return self.result

    def draw(self, screen):
        # Base window
        pygame.draw.rect(screen, (240, 240, 245), self.rect, border_radius=8)
        pygame.draw.rect(screen, (100, 100, 110), self.rect, 1, border_radius=8)
        
        # Title bar
        title_rect = pygame.Rect(self.rect.x, self.rect.y, self.rect.width, 30)
        pygame.draw.rect(screen, (220, 220, 230), title_rect, border_top_left_radius=8, border_top_right_radius=8)
        pygame.draw.line(screen, (180, 180, 190), title_rect.bottomleft, title_rect.bottomright)
        
        font = pygame.font.SysFont("Arial", 16, bold=True)
        txt = font.render(self.title, True, (50, 50, 60))
        screen.blit(txt, (self.rect.x + 10, self.rect.y + 5))

    def handle_event(self, event): pass
    def handle_key(self, event): 
        if event.key == pygame.K_ESCAPE: self.running = False

class QShortcut(QObject):
    def __init__(self, sequence, parent=None):
        super().__init__(parent)
        self._sequence = sequence
        self.activated = Signal()
        from .application import QApplication
        if QApplication._instance:
            if not hasattr(QApplication._instance, '_shortcuts'):
                QApplication._instance._shortcuts = []
            QApplication._instance._shortcuts.append(self)
    def setKey(self, seq): self._sequence = seq
