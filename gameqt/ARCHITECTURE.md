# GameQt Architecture

Internal design and implementation details of the GameQt framework.

## Table of Contents

1. [Overview](#overview)
2. [Module Structure](#module-structure)
3. [Event System](#event-system)
4. [Rendering Pipeline](#rendering-pipeline)
5. [Layout System](#layout-system)
6. [Graphics Framework](#graphics-framework)
7. [Design Decisions](#design-decisions)
8. [Performance Considerations](#performance-considerations)

---

## Overview

GameQt is a Qt-compatible GUI framework built on Pygame. It provides a familiar Qt API while using Pygame for rendering and event handling.

### Core Philosophy

1. **Qt Compatibility**: Maintain API compatibility with Qt where possible
2. **Simplicity**: Keep implementation simple and understandable
3. **Extensibility**: Allow easy customization and extension
4. **Performance**: Optimize for tool and editor use cases

### Architecture Layers

```
┌─────────────────────────────────────┐
│     Application Layer (User Code)   │
├─────────────────────────────────────┤
│   Widgets & Controls (QWidget, etc) │
├─────────────────────────────────────┤
│   Layouts (QVBoxLayout, QGridLayout)│
├─────────────────────────────────────┤
│   Graphics (QGraphicsView/Scene)    │
├─────────────────────────────────────┤
│   Core (Qt, QObject, Signal, Events)│
├─────────────────────────────────────┤
│   Pygame (Rendering & Input)        │
└─────────────────────────────────────┘
```

---

## Module Structure

### core.py

**Purpose**: Foundation classes and constants

**Key Classes**:
- `Qt` - Namespace for constants and enums
- `QObject` - Base object with parent-child relationships
- `Signal` - Signal/slot mechanism
- `QPoint`, `QSize`, `QRectF` - Geometry primitives
- `QMimeData`, `QClipboard` - Data transfer
- Event classes (`QMouseEvent`, `QWheelEvent`, etc.)

**Design**:
- Minimal dependencies
- Pure Python implementations
- Pygame integration for clipboard via `pygame.scrap`

### application.py

**Purpose**: Application lifecycle and event loop

**Key Classes**:
- `QApplication` - Main application singleton
- `QDragEnterEvent`, `QDropEvent` - Drag & drop events

**Event Loop**:
```python
while running:
    events = pygame.event.get()
    for event in events:
        # Handle special events (QUIT, RESIZE, DROPFILE)
        # Dispatch to windows via _handle_event()
    
    # Draw all visible windows
    for window in windows:
        window._draw_recursive()
    
    pygame.display.flip()
```

### widgets.py

**Purpose**: All widget implementations

**Key Classes**:
- `QWidget` - Base widget class
- `QMainWindow` - Main window with menu support
- Controls: `QPushButton`, `QLabel`, `QLineEdit`, `QTextEdit`, etc.
- Containers: `QScrollArea`, `QStackedWidget`, `QTabWidget`, `QSplitter`

**Widget Hierarchy**:
```
QObject
  └─ QWidget
       ├─ QMainWindow
       ├─ QLabel
       ├─ QPushButton
       ├─ QLineEdit
       ├─ QTextEdit
       ├─ QCheckBox
       ├─ QRadioButton
       ├─ QComboBox
       ├─ QSpinBox
       ├─ QSlider
       ├─ QScrollArea
       ├─ QStackedWidget
       ├─ QTabWidget
       └─ QSplitter
```

### layouts.py

**Purpose**: Layout managers for organizing widgets

**Key Classes**:
- `QVBoxLayout` - Vertical box layout
- `QHBoxLayout` - Horizontal box layout
- `QGridLayout` - Grid layout
- `QFormLayout` - Form layout (label-field pairs)
- `QStackedLayout` - Stacked layout
- `QSpacerItem` - Spacer for layouts

**Layout Algorithm**:
1. Calculate minimum sizes for all widgets
2. Distribute available space based on stretch factors
3. Apply alignment flags
4. Set widget rectangles

### graphics.py

**Purpose**: Graphics view framework

**Key Classes**:
- `QGraphicsView` - Viewport for scenes
- `QGraphicsScene` - Container for graphics items
- `QGraphicsItem` - Base class for all items
- Item types: `QGraphicsRectItem`, `QGraphicsEllipseItem`, `QGraphicsTextItem`, `QGraphicsPixmapItem`

**Coordinate Systems**:
- **Widget coordinates**: Relative to widget's top-left
- **Scene coordinates**: Absolute positions in the scene
- **View coordinates**: Viewport position (with zoom/pan)

### gui.py

**Purpose**: Drawing and rendering utilities

**Key Classes**:
- `QPainter` - Drawing interface
- `QPen` - Outline styling
- `QBrush` - Fill styling
- `QColor` - Color representation
- `QPixmap` - Image container
- `QFont` - Font specification
- `QTransform` - 2D transformations

### item_views.py

**Purpose**: Tree and list widgets

**Key Classes**:
- `QTreeWidget`, `QTreeWidgetItem` - Hierarchical tree
- `QListWidget`, `QListWidgetItem` - Simple list
- `QAbstractItemView` - Base class for item views

**Tree Structure**:
```
QTreeWidget
  └─ QTreeWidgetItem (root)
       ├─ QTreeWidgetItem (child 1)
       │    └─ QTreeWidgetItem (grandchild)
       └─ QTreeWidgetItem (child 2)
```

### menus.py

**Purpose**: Menu system

**Key Classes**:
- `QMenuBar` - Menu bar for windows
- `QMenu` - Dropdown menu
- `QAction` - Menu/toolbar action

### utils.py

**Purpose**: Utility classes

**Key Classes**:
- `QSettings` - Persistent settings
- `QUndoStack`, `QUndoCommand` - Undo/redo system
- `QUndoView` - Undo history viewer

---

## Event System

### Event Flow

```
Pygame Event
    ↓
QApplication.exec() loop
    ↓
Window._handle_event()
    ↓
Widget._handle_event() (recursive to children)
    ↓
Widget event handlers (mousePressEvent, etc.)
```

### Event Bubbling

Events propagate from child to parent if not accepted:

```python
def _handle_event(self, event, offset):
    # 1. Try children first (reverse order for z-order)
    for child in reversed(self._children):
        if child._handle_event(event, offset):
            return True  # Child handled it
    
    # 2. Handle in this widget
    if self.handles_this_event(event):
        self.handle_event(event)
        if event.isAccepted():
            return True
    
    # 3. Bubble to parent
    return False
```

### Signal/Slot Mechanism

```python
class Signal:
    def __init__(self):
        self._callbacks = []
    
    def connect(self, callback):
        self._callbacks.append(callback)
    
    def emit(self, *args):
        for callback in self._callbacks:
            callback(*args)
```

---

## Rendering Pipeline

### Drawing Cycle

```
QApplication.exec()
    ↓
For each window:
    window._draw_recursive(offset=(0,0))
        ↓
    widget._draw(pos)  # Draw this widget
        ↓
    For each child:
        child._draw_recursive(offset=parent_pos)
```

### Widget Drawing

```python
def _draw(self, pos):
    # 1. Get screen surface
    screen = QApplication._instance._windows[0]._screen
    
    # 2. Draw background
    pygame.draw.rect(screen, bg_color, 
                    (pos.x, pos.y, width, height))
    
    # 3. Draw content (text, images, etc.)
    # ...
    
    # 4. Draw border
    pygame.draw.rect(screen, border_color, 
                    (pos.x, pos.y, width, height), 1)
```

### Clipping

Widgets use clipping to prevent drawing outside their bounds:

```python
old_clip = screen.get_clip()
screen.set_clip(pygame.Rect(x, y, w, h))
# ... draw content ...
screen.set_clip(old_clip)
```

---

## Layout System

### Layout Process

1. **Size Calculation**:
   - Each widget reports its minimum/preferred size
   - Layout calculates total space needed

2. **Space Distribution**:
   - Available space = parent size - margins - spacing
   - Distribute based on stretch factors
   - Apply size constraints

3. **Widget Positioning**:
   - Set each widget's `_rect` attribute
   - Widgets draw themselves at their rect position

### Example: QVBoxLayout

```python
def arrange(self, rect):
    # 1. Calculate total height needed
    total_height = sum(widget._rect.height for widget in widgets)
    total_height += spacing * (len(widgets) - 1)
    
    # 2. Distribute extra space
    extra_space = rect.height - total_height
    space_per_stretch = extra_space / total_stretch
    
    # 3. Position widgets
    y = rect.y
    for widget in widgets:
        height = widget._rect.height + (stretch * space_per_stretch)
        widget._rect = pygame.Rect(rect.x, y, rect.width, height)
        y += height + spacing
```

---

## Graphics Framework

### Scene/View Architecture

```
QGraphicsView (viewport)
    ↓ displays
QGraphicsScene (container)
    ↓ contains
QGraphicsItems (shapes, text, images)
```

### Item Rendering

```python
def _draw_scene(self):
    # 1. Sort items by z-value
    items = sorted(self.scene.items(), key=lambda i: i.zValue())
    
    # 2. Apply view transform (zoom, pan)
    transform = self.view_transform
    
    # 3. Draw each item
    for item in items:
        if not item.isVisible():
            continue
        
        # Transform item position
        pos = transform.map(item.pos())
        
        # Draw item
        item.paint(painter, option, widget)
```

### Selection and Interaction

- Items can be movable, selectable, focusable
- Scene tracks selected items
- Mouse events delivered to items under cursor
- Drag operations update item positions

---

## Design Decisions

### Why Pygame?

**Pros**:
- Cross-platform
- Simple API
- Good performance for 2D
- Large community

**Cons**:
- Not native widgets
- Limited text rendering
- No hardware acceleration (in standard Pygame)

### Qt Compatibility vs. Simplicity

**Tradeoffs**:
- Simplified implementations where full Qt compatibility is complex
- Focus on common use cases
- Omit rarely-used features
- Document differences from Qt

### Single-Threaded Design

**Rationale**:
- Simpler implementation
- Easier debugging
- Sufficient for tool/editor use cases
- Pygame is not thread-safe

### HTML Rendering

**Approach**:
- Use Python's `html.parser` for parsing
- Render as styled text spans
- Support common tags (b, i, color, lists, tables)
- No full CSS support

---

## Performance Considerations

### Optimization Strategies

1. **Lazy Evaluation**:
   - Only calculate layouts when needed
   - Cache computed sizes

2. **Dirty Rectangles**:
   - Could be implemented for partial redraws
   - Currently redraws entire window each frame

3. **Event Filtering**:
   - Early rejection of events outside widget bounds
   - Event bubbling stops when handled

4. **Widget Caching**:
   - Scene caching in PDF editor (max 5 pages)
   - Serialize/deserialize widget state

### Performance Limits

**Good For**:
- Tools and editors
- Form-based applications
- Graphics editors
- Prototyping

**Not Ideal For**:
- High-frequency updates (>60 FPS)
- Thousands of widgets
- Complex animations
- Video playback

### Memory Usage

- Each widget: ~1-2 KB
- Graphics items: ~500 bytes
- Pixmaps: width × height × 4 bytes
- Scenes: sum of all items

---

## Extension Points

### Creating Custom Widgets

```python
class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        # Initialize
    
    def _draw(self, pos):
        super()._draw(pos)  # Draw base widget
        # Custom drawing
    
    def mousePressEvent(self, event):
        # Handle mouse press
        event.accept()
```

### Custom Graphics Items

```python
class MyItem(QGraphicsItem):
    def boundingRect(self):
        return QRectF(0, 0, 100, 100)
    
    def paint(self, painter, option, widget):
        # Custom painting
        painter.drawRect(self.boundingRect())
```

### Custom Layouts

```python
class MyLayout:
    def __init__(self, parent=None):
        self._parent = parent
        self._items = []
    
    def addWidget(self, widget):
        self._items.append(widget)
    
    def arrange(self, rect):
        # Custom arrangement logic
        pass
```

---

## Future Improvements

### Potential Enhancements

1. **Performance**:
   - Dirty rectangle optimization
   - Caching rendered widgets
   - Hardware acceleration via Pygame-ce

2. **Features**:
   - More complete HTML/CSS support
   - Better text editing (cursor position, selection)
   - Drag & drop between widgets
   - Animation framework

3. **Qt Compatibility**:
   - More Qt classes
   - Better signal/slot compatibility
   - Model/View framework

4. **Developer Experience**:
   - Better error messages
   - Debugging tools
   - Performance profiling

---

## Conclusion

GameQt provides a Qt-compatible API on top of Pygame, making it easy to create desktop applications with familiar Qt patterns while leveraging Pygame's cross-platform capabilities.

The architecture prioritizes:
- **Simplicity** over completeness
- **Usability** over performance
- **Familiarity** over innovation

This makes GameQt ideal for tools, editors, and prototypes where Qt's API is desired but native widgets aren't required.

---

For more information:
- [README](README.md) - Overview and quick start
- [API Reference](API_REFERENCE.md) - Complete API documentation
- [Tutorial](TUTORIAL.md) - Step-by-step guides
- [Examples](EXAMPLES.md) - Code examples
