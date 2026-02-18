import pygame

class Qt:
    class Orientation: Horizontal = 1; Vertical = 2
    class WindowType: 
        Widget = 0; Window = 1; Dialog = 2; Sheet = 3; Drawer = 4; Popup = 5; Tool = 6; ToolTip = 7; SplashScreen = 8
        WindowStaysOnTopHint = 0x00040000
        WindowTitleHint = 0x00001000
        WindowSystemMenuHint = 0x00002000
        WindowMinimizeButtonHint = 0x00004000
        WindowMaximizeButtonHint = 0x00008000
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
    class ItemDataRole: 
        DisplayRole = 0
        DecorationRole = 1
        EditRole = 2
        ToolTipRole = 3
        StatusTipRole = 4
        WhatsThisRole = 5
        SizeHintRole = 13
        FontRole = 6
        TextAlignmentRole = 7
        BackgroundRole = 8
        ForegroundRole = 9
        CheckStateRole = 10
        UserRole = 1000
    class ItemFlag:
        NoItemFlags = 0
        ItemIsSelectable = 1
        ItemIsSelected = 1 # Alias
        ItemIsEditable = 2
        ItemIsDragEnabled = 4
        ItemIsDropEnabled = 8
        ItemIsUserCheckable = 16
        ItemIsEnabled = 32
        ItemIsTristate = 64
        ItemNeverHasChildren = 128
        ItemIsFocused = 256
    class CheckState: Checked = 2; Unchecked = 0
    class PenStyle: SolidLine = 1; DashLine = 2; DotLine = 3
    class BrushStyle: SolidPattern = 1; NoBrush = 0
    class FrameShape: NoFrame = 0; Box = 1; Panel = 2; WinPanel = 3; HLine = 4; VLine = 5; StyledPanel = 6
    class TextInteractionFlag: NoTextInteraction = 0; TextEditorInteraction = 1
    class ContextMenuPolicy: CustomContextMenu = 1; PreventContextMenu = 0; DefaultContextMenu = 2
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
        transparent = "#00000000"
