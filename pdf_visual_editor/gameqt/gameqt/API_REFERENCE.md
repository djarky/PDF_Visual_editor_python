# GameQt API Reference

Complete API documentation for all GameQt modules, classes, and methods.

## Table of Contents

1. [Core Module](#core-module)
2. [Application Module](#application-module)
3. [Widgets Module](#widgets-module)
4. [Layouts Module](#layouts-module)
5. [Graphics Module](#graphics-module)
6. [GUI Module](#gui-module)
7. [Item Views Module](#item-views-module)
8. [Menus Module](#menus-module)
9. [Utils Module](#utils-module)

---

## Core Module

### Qt

Central namespace for Qt constants and enumerations.

#### Enumerations

**Qt.Orientation**
- `Horizontal = 1` - Horizontal orientation
- `Vertical = 2` - Vertical orientation

**Qt.AlignmentFlag**
- `AlignLeft = 0x0001` - Align left
- `AlignRight = 0x0002` - Align right
- `AlignHCenter = 0x0004` - Center horizontally
- `AlignTop = 0x0020` - Align top
- `AlignBottom = 0x0040` - Align bottom
- `AlignVCenter = 0x0080` - Center vertically
- `AlignCenter` - Center both horizontally and vertically

**Qt.MouseButton**
- `LeftButton = 0x01`
- `RightButton = 0x02`
- `MidButton = 0x04`
- `NoButton = 0x00`

**Qt.KeyboardModifier**
- `ControlModifier` - Ctrl key
- `AltModifier` - Alt key
- `ShiftModifier` - Shift key
- `NoModifier = 0`

**Qt.CheckState**
- `Checked = 2`
- `Unchecked = 0`

**Qt.GlobalColor**
- `white`, `black`, `red`, `darkRed`, `green`, `darkGreen`
- `blue`, `darkBlue`, `cyan`, `darkCyan`, `magenta`, `darkMagenta`
- `yellow`, `darkYellow`, `gray`, `darkGray`, `lightGray`

### QObject

Base class for all Qt objects. Provides parent-child relationship and signal support.

```python
class QObject:
    def __init__(self, parent=None)
    def setParent(self, parent)
    def parent() -> QObject
```

### Signal

Signal/slot mechanism for event handling.

```python
signal = Signal()
signal.connect(callback_function)
signal.emit(*args)
signal.disconnect(callback_function)
```

**Example:**
```python
class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.clicked = Signal()
        self.clicked.connect(self.on_click)
    
    def on_click(self):
        print("Clicked!")
```

### QPoint / QPointF

Represents a point in 2D space.

```python
class QPointF:
    def __init__(self, x=0, y=0)
    def x() -> float
    def y() -> float
    def setX(x: float)
    def setY(y: float)
```

### QSize

Represents a size (width and height).

```python
class QSize:
    def __init__(self, w=0, h=0)
    def width() -> int
    def height() -> int
```

### QRectF

Represents a rectangle.

```python
class QRectF:
    def __init__(self, x, y, w, h)
    def x() -> float
    def y() -> float
    def width() -> float
    def height() -> float
    def topLeft() -> QPointF
    def bottomRight() -> QPointF
    def center() -> QPointF
    def normalized() -> QRectF
```

### QUrl

Represents a URL or file path.

```python
class QUrl:
    def __init__(self, path="")
    def toLocalFile() -> str  # Converts file:// URLs to local paths
    def toString() -> str
```

### QMimeData

Container for data in multiple formats (clipboard, drag & drop).

```python
class QMimeData:
    def setText(text: str)
    def text() -> str
    def hasText() -> bool
    
    def setUrls(urls: list[QUrl])
    def urls() -> list[QUrl]
    def hasUrls() -> bool
    
    def setData(mime_type: str, data: bytes)
    def data(mime_type: str) -> bytes
    def hasImage() -> bool
```

### QClipboard

System clipboard access.

```python
class QClipboard:
    def setText(text: str)
    def text() -> str
    def setMimeData(mime: QMimeData)
    def mimeData() -> QMimeData
```

**Example:**
```python
clipboard = QApplication.clipboard()
clipboard.setText("Hello, Clipboard!")
text = clipboard.text()
```

### Event Classes

**QMouseEvent**
```python
class QMouseEvent:
    def pos() -> QPointF
    def button() -> Qt.MouseButton
    def buttons() -> int
    def modifiers() -> Qt.KeyboardModifier
    def accept()
    def ignore()
    def isAccepted() -> bool
```

**QWheelEvent**
```python
class QWheelEvent:
    def pos() -> QPointF
    def angleDelta() -> QPoint
    def pixelDelta() -> QPoint
    def modifiers() -> Qt.KeyboardModifier
    def accept()
    def ignore()
    def isAccepted() -> bool
```

---

## Application Module

### QApplication

Main application class. Manages the event loop and global application state.

```python
class QApplication:
    def __init__(self, args: list)
    
    @staticmethod
    def instance() -> QApplication
    
    @staticmethod
    def clipboard() -> QClipboard
    
    def setApplicationName(name: str)
    def exec() -> int  # Start event loop
    def quit()
```

**Example:**
```python
import sys
from gameqt.application import QApplication

app = QApplication(sys.argv)
# ... create windows ...
sys.exit(app.exec())
```

### QDragEnterEvent / QDropEvent

Drag and drop events.

```python
class QDragEnterEvent:
    def pos() -> tuple
    def mimeData() -> QMimeData
    def accept()
    def ignore()
    def isAccepted() -> bool

class QDropEvent:
    def pos() -> tuple
    def position() -> tuple  # Alias for pos()
    def mimeData() -> QMimeData
    def accept()
    def ignore()
    def isAccepted() -> bool
```

---

## Widgets Module

### QWidget

Base class for all widgets.

```python
class QWidget(QObject):
    def __init__(self, parent=None)
    
    # Geometry
    def resize(w: int, h: int)
    def setMinimumSize(w: int, h: int)
    def move(x: int, y: int)
    
    # Visibility
    def show()
    def hide()
    def setVisible(visible: bool)
    def isVisible() -> bool
    def close()
    
    # Layout
    def setLayout(layout: QLayout)
    
    # Styling
    def setStyleSheet(css: str)
    
    # Drag & Drop
    def setAcceptDrops(accept: bool)
    def acceptDrops() -> bool
    def dragEnterEvent(event: QDragEnterEvent)
    def dropEvent(event: QDropEvent)
    
    # Events (override in subclasses)
    def mousePressEvent(event: QMouseEvent)
    def mouseReleaseEvent(event: QMouseEvent)
    def mouseMoveEvent(event: QMouseEvent)
    def wheelEvent(event: QWheelEvent)
    
    # Signals
    clicked = Signal()
```

### QMainWindow

Main application window with menu bar support.

```python
class QMainWindow(QWidget):
    def __init__(self)
    def setWindowTitle(title: str)
    def setCentralWidget(widget: QWidget)
    def setMenuBar(menu_bar: QMenuBar)
```

### QLabel

Text or image display widget.

```python
class QLabel(QWidget):
    def setText(text: str)
    def text() -> str
    def setPixmap(pixmap: QPixmap)
```

### QPushButton

Clickable button.

```python
class QPushButton(QWidget):
    def __init__(self, text="", parent=None)
    def setText(text: str)
    def text() -> str
    
    # Signals
    clicked = Signal()
```

### QLineEdit

Single-line text input.

```python
class QLineEdit(QWidget):
    def setText(text: str)
    def text() -> str
    def setPlaceholderText(text: str)
    def setReadOnly(readonly: bool)
    
    # Signals
    textChanged = Signal(str)
    returnPressed = Signal()
```

### QTextEdit

Multi-line text editor with HTML support.

```python
class QTextEdit(QWidget):
    def setPlainText(text: str)
    def toPlainText() -> str
    def setHtml(html: str)
    def setReadOnly(readonly: bool)
    
    # Signals
    textChanged = Signal()
```

**Supported HTML Tags:**
- `<b>`, `<strong>` - Bold text
- `<i>`, `<em>` - Italic text
- `<font color="#RRGGBB">` - Colored text
- `<h1>`, `<h2>`, `<h3>` - Headers (bold, larger font)
- `<p>`, `<div>` - Paragraphs
- `<br>` - Line break
- `<ul>`, `<li>` - Lists with bullets
- `<table>`, `<tr>`, `<td>` - Basic tables

### QCheckBox

Checkbox with label.

```python
class QCheckBox(QWidget):
    def __init__(self, text="", parent=None)
    def setText(text: str)
    def setChecked(checked: bool)
    def isChecked() -> bool
    
    # Signals
    stateChanged = Signal(int)
```

### QRadioButton

Radio button (mutually exclusive in groups).

```python
class QRadioButton(QWidget):
    def __init__(self, text="", parent=None)
    def setText(text: str)
    def setChecked(checked: bool)
    def isChecked() -> bool
    
    # Signals
    toggled = Signal(bool)
```

### QComboBox

Dropdown selection box.

```python
class QComboBox(QWidget):
    def addItem(text: str)
    def addItems(items: list[str])
    def currentText() -> str
    def currentIndex() -> int
    def setCurrentIndex(index: int)
    
    # Signals
    currentIndexChanged = Signal(int)
```

### QSpinBox

Numeric input with up/down buttons.

```python
class QSpinBox(QWidget):
    def setValue(value: int)
    def value() -> int
    def setMinimum(min: int)
    def setMaximum(max: int)
    def setRange(min: int, max: int)
    
    # Signals
    valueChanged = Signal(int)
```

### QSlider

Slider for selecting values in a range.

```python
class QSlider(QWidget):
    def __init__(self, orientation=Qt.Orientation.Horizontal, parent=None)
    def setValue(value: int)
    def value() -> int
    def setMinimum(min: int)
    def setMaximum(max: int)
    def setRange(min: int, max: int)
    
    # Signals
    valueChanged = Signal(int)
```

### QScrollArea

Scrollable container for widgets.

```python
class QScrollArea(QWidget):
    def setWidget(widget: QWidget)
    def setWidgetResizable(resizable: bool)
```

### QStackedWidget

Container showing one widget at a time.

```python
class QStackedWidget(QWidget):
    def addWidget(widget: QWidget)
    def setCurrentIndex(index: int)
    def currentIndex() -> int
```

### QTabWidget

Tabbed container.

```python
class QTabWidget(QWidget):
    def addTab(widget: QWidget, label: str)
    def setCurrentIndex(index: int)
    def currentIndex() -> int
```

### QSplitter

Resizable split container.

```python
class QSplitter(QWidget):
    def __init__(self, orientation=Qt.Orientation.Horizontal, parent=None)
    def addWidget(widget: QWidget)
    def setSizes(sizes: list[int])
```

---

## Layouts Module

### QVBoxLayout

Vertical box layout.

```python
class QVBoxLayout:
    def __init__(self, parent=None)
    def addWidget(widget: QWidget, stretch=0, alignment=0)
    def addLayout(layout: QLayout)
    def addStretch(stretch=0)
    def setSpacing(spacing: int)
```

### QHBoxLayout

Horizontal box layout.

```python
class QHBoxLayout:
    def __init__(self, parent=None)
    def addWidget(widget: QWidget, stretch=0, alignment=0)
    def addLayout(layout: QLayout)
    def addStretch(stretch=0)
    def setSpacing(spacing: int)
```

### QGridLayout

Grid layout.

```python
class QGridLayout:
    def __init__(self, parent=None)
    def addWidget(widget: QWidget, row: int, col: int, 
                  rowSpan=1, colSpan=1, alignment=0)
    def setSpacing(spacing: int)
    def setRowStretch(row: int, stretch: int)
    def setColumnStretch(col: int, stretch: int)
```

### QFormLayout

Form layout (label-field pairs).

```python
class QFormLayout:
    def __init__(self, parent=None)
    def addRow(label: str, field: QWidget)
    def addRow(widget: QWidget)
```

### QStackedLayout

Stacked layout (one visible at a time).

```python
class QStackedLayout:
    def __init__(self, parent=None)
    def addWidget(widget: QWidget)
    def setCurrentIndex(index: int)
    def currentIndex() -> int
```

### QSpacerItem

Spacer for layouts.

```python
class QSpacerItem:
    def __init__(self, w: int, h: int, hPolicy=None, vPolicy=None)
```

---

## Graphics Module

### QGraphicsView

View for displaying graphics scenes.

```python
class QGraphicsView(QWidget):
    def __init__(self, scene=None, parent=None)
    def setScene(scene: QGraphicsScene)
    def scene() -> QGraphicsScene
    def scale(sx: float, sy: float)
    def translate(dx: float, dy: float)
    def setSceneRect(rect: QRectF)
```

### QGraphicsScene

Container for graphics items.

```python
class QGraphicsScene(QObject):
    def __init__(self, parent=None)
    def addItem(item: QGraphicsItem)
    def removeItem(item: QGraphicsItem)
    def items() -> list[QGraphicsItem]
    def selectedItems() -> list[QGraphicsItem]
    def clearSelection()
    def setSceneRect(rect: QRectF)
    
    # Signals
    selectionChanged = Signal()
```

### QGraphicsItem

Base class for all graphics items.

```python
class QGraphicsItem:
    def setPos(x: float, y: float)
    def pos() -> QPointF
    def setZValue(z: float)
    def zValue() -> float
    def setVisible(visible: bool)
    def isVisible() -> bool
    def setSelected(selected: bool)
    def setFlag(flag: GraphicsItemFlag, enabled=True)
    def setFlags(flags: int)
    def flags() -> int
    def setOpacity(opacity: float)
    def opacity() -> float
    def setRotation(angle: float)
    def rotation() -> float
    def setTransform(transform: QTransform)
    def transform() -> QTransform
    def boundingRect() -> QRectF
    def setData(key: int, value: any)
    def data(key: int) -> any
    
    # Flags
    class GraphicsItemFlag:
        ItemIsMovable = 1
        ItemIsSelectable = 2
        ItemIsFocusable = 4
```

### QGraphicsRectItem

Rectangle graphics item.

```python
class QGraphicsRectItem(QGraphicsItem):
    def __init__(self, x: float, y: float, w: float, h: float, parent=None)
    def rect() -> QRectF
    def setPen(pen: QPen)
    def setBrush(brush: QBrush)
```

### QGraphicsEllipseItem

Ellipse graphics item.

```python
class QGraphicsEllipseItem(QGraphicsItem):
    def __init__(self, x: float, y: float, w: float, h: float, parent=None)
    def rect() -> QRectF
    def setPen(pen: QPen)
    def setBrush(brush: QBrush)
```

### QGraphicsTextItem

Text graphics item.

```python
class QGraphicsTextItem(QGraphicsItem):
    def __init__(self, text="", parent=None)
    def setPlainText(text: str)
    def toPlainText() -> str
    def setFont(font: QFont)
    def font() -> QFont
    def setDefaultTextColor(color: QColor)
```

### QGraphicsPixmapItem

Pixmap (image) graphics item.

```python
class QGraphicsPixmapItem(QGraphicsItem):
    def __init__(self, pixmap=None, parent=None)
    def setPixmap(pixmap: QPixmap)
    def pixmap() -> QPixmap
```

---

## GUI Module

### QPainter

Drawing interface.

```python
class QPainter:
    def __init__(self, surface: pygame.Surface)
    
    def setPen(pen: QPen)
    def setBrush(brush: QBrush)
    
    def drawLine(x1: int, y1: int, x2: int, y2: int)
    def drawRect(rect: pygame.Rect)
    def drawEllipse(rect: pygame.Rect)
    def drawPolygon(points: list[QPointF])
    def drawText(x: int, y: int, text: str)
```

### QPen

Pen for drawing outlines.

```python
class QPen:
    def __init__(self, color: QColor, width=1, style=Qt.PenStyle.SolidLine)
    def color() -> QColor
    def width() -> int
    def setColor(color: QColor)
    def setWidth(width: int)
```

### QBrush

Brush for filling shapes.

```python
class QBrush:
    def __init__(self, color: QColor, style=Qt.BrushStyle.SolidPattern)
    def color() -> QColor
    def setColor(color: QColor)
```

### QColor

Color representation.

```python
class QColor:
    def __init__(self, r: int, g: int, b: int, a=255)
    def __init__(self, hex_string: str)  # e.g., "#FF0000"
    
    def red() -> int
    def green() -> int
    def blue() -> int
    def alpha() -> int
    
    def to_pygame() -> tuple  # Returns (r, g, b, a)
```

### QPixmap

Image container.

```python
class QPixmap:
    def __init__(self, path="")
    def load(path: str) -> bool
    def loadFromData(data: bytes) -> bool
    def save(path: str, format="PNG") -> bool
    def scaled(w: int, h: int, mode=Qt.TransformationMode.SmoothTransformation) -> QPixmap
    def scaledToWidth(w: int, mode=Qt.TransformationMode.SmoothTransformation) -> QPixmap
    def width() -> int
    def height() -> int
    def isNull() -> bool
    
    @staticmethod
    def fromImage(image: QImage) -> QPixmap
```

### QFont

Font specification.

```python
class QFont:
    def __init__(self, family="Arial", pointSize=12)
    def setFamily(family: str)
    def setPointSize(size: int)
    def setBold(bold: bool)
    def setItalic(italic: bool)
    def family() -> str
    def pointSize() -> int
    def bold() -> bool
    def italic() -> bool
```

### QTransform

2D transformation matrix.

```python
class QTransform:
    def __init__(self, m11=1, m12=0, m21=0, m22=1, dx=0, dy=0)
    def scale(sx: float, sy: float)
    def rotate(angle: float)
    def translate(dx: float, dy: float)
    def m11() -> float  # Scale X
    def m22() -> float  # Scale Y
```

---

## Item Views Module

### QTreeWidget

Hierarchical tree widget.

```python
class QTreeWidget(QWidget):
    def __init__(self, parent=None)
    def setHeaderLabels(labels: list[str])
    def topLevelItemCount() -> int
    def topLevelItem(index: int) -> QTreeWidgetItem
    def addTopLevelItem(item: QTreeWidgetItem)
    def clear()
    def selectedItems() -> list[QTreeWidgetItem]
    
    # Signals
    itemChanged = Signal(QTreeWidgetItem, int)
    itemSelectionChanged = Signal()
```

### QTreeWidgetItem

Item in a tree widget.

```python
class QTreeWidgetItem:
    def __init__(self, parent=None)
    def setText(column: int, text: str)
    def text(column: int) -> str
    def setCheckState(column: int, state: Qt.CheckState)
    def checkState(column: int) -> Qt.CheckState
    def setData(column: int, role: int, value: any)
    def data(column: int, role: int) -> any
    def setExpanded(expanded: bool)
    def addChild(item: QTreeWidgetItem)
    def insertChild(index: int, item: QTreeWidgetItem)
    def removeChild(item: QTreeWidgetItem)
    def takeChild(index: int) -> QTreeWidgetItem
    def child(index: int) -> QTreeWidgetItem
    def childCount() -> int
    def parent() -> QTreeWidgetItem
```

### QListWidget

List widget.

```python
class QListWidget(QWidget):
    def __init__(self, parent=None)
    def addItem(text: str)
    def addItems(items: list[str])
    def clear()
    def count() -> int
    def currentRow() -> int
    def setCurrentRow(row: int)
    
    # Signals
    currentRowChanged = Signal(int)
```

---

## Menus Module

### QMenuBar

Menu bar for main windows.

```python
class QMenuBar(QWidget):
    def addMenu(title: str) -> QMenu
    def addMenu(menu: QMenu) -> QMenu
```

### QMenu

Dropdown menu.

```python
class QMenu(QWidget):
    def __init__(self, title="", parent=None)
    def addAction(text: str) -> QAction
    def addAction(action: QAction) -> QAction
    def addSeparator()
    def addMenu(menu: QMenu) -> QMenu
    def exec(pos: QPoint) -> QAction
```

### QAction

Menu or toolbar action.

```python
class QAction(QObject):
    def __init__(self, text="", parent=None)
    def setText(text: str)
    def text() -> str
    def setShortcut(shortcut: str)
    def setCheckable(checkable: bool)
    def setChecked(checked: bool)
    def isChecked() -> bool
    def setEnabled(enabled: bool)
    
    # Signals
    triggered = Signal()
    toggled = Signal(bool)
```

---

## Utils Module

### QSettings

Persistent application settings.

```python
class QSettings:
    def __init__(self, org: str, app: str)
    def setValue(key: str, value: any)
    def value(key: str, default=None) -> any
```

### QUndoStack

Undo/redo stack.

```python
class QUndoStack(QObject):
    def __init__(self, parent=None)
    def push(command: QUndoCommand)
    def undo()
    def redo()
    def canUndo() -> bool
    def canRedo() -> bool
    def clear()
    def beginMacro(text: str)
    def endMacro()
```

### QUndoCommand

Base class for undo commands.

```python
class QUndoCommand:
    def __init__(self, text="")
    def undo()  # Override
    def redo()  # Override
```

---

## Complete Example

Here's a comprehensive example using many GameQt features:

```python
from gameqt.application import QApplication
from gameqt.widgets import (QMainWindow, QWidget, QLabel, QPushButton, 
                             QLineEdit, QTextEdit, QCheckBox)
from gameqt.layouts import QVBoxLayout, QHBoxLayout, QFormLayout
from gameqt.menus import QMenuBar, QMenu, QAction
from gameqt.core import Qt
import sys

class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GameQt Demo")
        self.resize(600, 400)
        
        # Menu
        menubar = QMenuBar()
        file_menu = menubar.addMenu("File")
        
        open_action = QAction("Open", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.on_open)
        file_menu.addAction(open_action)
        
        self.setMenuBar(menubar)
        
        # Central widget
        central = QWidget()
        main_layout = QVBoxLayout(central)
        
        # Form
        form = QFormLayout()
        self.name_edit = QLineEdit()
        self.email_edit = QLineEdit()
        form.addRow("Name:", self.name_edit)
        form.addRow("Email:", self.email_edit)
        main_layout.addLayout(form)
        
        # Checkbox
        self.subscribe_check = QCheckBox("Subscribe to newsletter")
        main_layout.addWidget(self.subscribe_check)
        
        # Text area
        self.notes = QTextEdit()
        self.notes.setPlainText("Enter notes here...")
        main_layout.addWidget(self.notes)
        
        # Buttons
        btn_layout = QHBoxLayout()
        submit_btn = QPushButton("Submit")
        submit_btn.clicked.connect(self.on_submit)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.close)
        btn_layout.addWidget(submit_btn)
        btn_layout.addWidget(cancel_btn)
        main_layout.addLayout(btn_layout)
        
        self.setCentralWidget(central)
        central.show()
    
    def on_open(self):
        print("Open clicked")
    
    def on_submit(self):
        name = self.name_edit.text()
        email = self.email_edit.text()
        subscribe = self.subscribe_check.isChecked()
        notes = self.notes.toPlainText()
        
        print(f"Name: {name}")
        print(f"Email: {email}")
        print(f"Subscribe: {subscribe}")
        print(f"Notes: {notes}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec())
```

---

For more examples, see [EXAMPLES.md](EXAMPLES.md).
For tutorials, see [TUTORIAL.md](TUTORIAL.md).
