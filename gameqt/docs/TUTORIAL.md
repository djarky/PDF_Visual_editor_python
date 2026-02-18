# GameQt Tutorial

Step-by-step tutorials to learn GameQt from basics to advanced features.

## Table of Contents

1. [Getting Started](#1-getting-started)
2. [Working with Widgets](#2-working-with-widgets)
3. [Layouts and Organization](#3-layouts-and-organization)
4. [Signals and Slots](#4-signals-and-slots)
5. [Graphics and Drawing](#5-graphics-and-drawing)
6. [Menus and Actions](#6-menus-and-actions)
7. [Clipboard and Drag & Drop](#7-clipboard-and-drag--drop)
8. [Advanced Topics](#8-advanced-topics)

---

## 1. Getting Started

### Your First GameQt Application

Let's create a simple "Hello World" application:

```python
import sys
from gameqt.application import QApplication
from gameqt.widgets import QMainWindow, QLabel

# Create the application
app = QApplication(sys.argv)

# Create the main window
window = QMainWindow()
window.setWindowTitle("My First GameQt App")
window.resize(400, 300)

# Create a label
label = QLabel()
label.setText("Hello, GameQt!")

# Set the label as the central widget
window.setCentralWidget(label)

# Show the window
window.show()

# Start the event loop
sys.exit(app.exec())
```

**Key Concepts:**
- `QApplication` manages the application lifecycle
- `QMainWindow` is the main window container
- `setCentralWidget()` sets the main content
- `show()` makes the window visible
- `exec()` starts the event loop

---

## 2. Working with Widgets

### Creating a Button

```python
from gameqt.widgets import QPushButton

button = QPushButton("Click Me!")
button.clicked.connect(lambda: print("Button clicked!"))
```

### Creating a Text Input

```python
from gameqt.widgets import QLineEdit

text_input = QLineEdit()
text_input.setPlaceholderText("Enter your name...")
text_input.textChanged.connect(lambda text: print(f"Text: {text}"))
```

### Creating a Checkbox

```python
from gameqt.widgets import QCheckBox

checkbox = QCheckBox("Enable notifications")
checkbox.stateChanged.connect(lambda state: print(f"Checked: {state == 2}"))
```

### Complete Widget Example

```python
import sys
from gameqt.application import QApplication
from gameqt.widgets import QMainWindow, QWidget, QLabel, QPushButton, QLineEdit
from gameqt.layouts import QVBoxLayout

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Widget Demo")
        self.resize(400, 300)
        
        # Create central widget
        central = QWidget()
        layout = QVBoxLayout(central)
        
        # Add widgets
        label = QLabel()
        label.setText("Enter your name:")
        layout.addWidget(label)
        
        self.name_input = QLineEdit()
        layout.addWidget(self.name_input)
        
        button = QPushButton("Greet")
        button.clicked.connect(self.on_greet)
        layout.addWidget(button)
        
        self.result_label = QLabel()
        layout.addWidget(self.result_label)
        
        self.setCentralWidget(central)
        central.show()
    
    def on_greet(self):
        name = self.name_input.text()
        self.result_label.setText(f"Hello, {name}!")

app = QApplication(sys.argv)
window = MyWindow()
window.show()
sys.exit(app.exec())
```

---

## 3. Layouts and Organization

### Vertical Layout (QVBoxLayout)

Arranges widgets vertically:

```python
from gameqt.layouts import QVBoxLayout

layout = QVBoxLayout(parent_widget)
layout.addWidget(widget1)
layout.addWidget(widget2)
layout.addWidget(widget3)
```

### Horizontal Layout (QHBoxLayout)

Arranges widgets horizontally:

```python
from gameqt.layouts import QHBoxLayout

layout = QHBoxLayout(parent_widget)
layout.addWidget(button1)
layout.addWidget(button2)
layout.addStretch()  # Pushes buttons to the left
```

### Grid Layout (QGridLayout)

Arranges widgets in a grid:

```python
from gameqt.layouts import QGridLayout

layout = QGridLayout(parent_widget)
layout.addWidget(label1, 0, 0)  # Row 0, Column 0
layout.addWidget(input1, 0, 1)  # Row 0, Column 1
layout.addWidget(label2, 1, 0)  # Row 1, Column 0
layout.addWidget(input2, 1, 1)  # Row 1, Column 1
```

### Form Layout (QFormLayout)

Perfect for forms with label-field pairs:

```python
from gameqt.layouts import QFormLayout

layout = QFormLayout(parent_widget)
layout.addRow("Name:", name_input)
layout.addRow("Email:", email_input)
layout.addRow("Phone:", phone_input)
```

### Nested Layouts

Combine layouts for complex UIs:

```python
from gameqt.layouts import QVBoxLayout, QHBoxLayout

main_layout = QVBoxLayout(central_widget)

# Top section
top_layout = QHBoxLayout()
top_layout.addWidget(logo_label)
top_layout.addWidget(title_label)
main_layout.addLayout(top_layout)

# Middle section
main_layout.addWidget(content_widget)

# Bottom section
bottom_layout = QHBoxLayout()
bottom_layout.addStretch()
bottom_layout.addWidget(ok_button)
bottom_layout.addWidget(cancel_button)
main_layout.addLayout(bottom_layout)
```

---

## 4. Signals and Slots

### Connecting Signals

Signals notify when something happens. Connect them to functions (slots):

```python
button.clicked.connect(my_function)
```

### Creating Custom Signals

```python
from gameqt.core import Signal

class MyWidget(QWidget):
    # Define custom signal
    dataChanged = Signal(str)
    
    def update_data(self, new_data):
        # Emit the signal
        self.dataChanged.emit(new_data)

# Connect to the signal
widget = MyWidget()
widget.dataChanged.connect(lambda data: print(f"Data: {data}"))
```

### Lambda Functions

Use lambda for simple callbacks:

```python
button.clicked.connect(lambda: print("Clicked!"))
button.clicked.connect(lambda: self.process_data(value))
```

### Multiple Connections

One signal can connect to multiple slots:

```python
button.clicked.connect(self.save_data)
button.clicked.connect(self.update_ui)
button.clicked.connect(self.log_action)
```

---

## 5. Graphics and Drawing

### Creating a Graphics View

```python
from gameqt.graphics import QGraphicsView, QGraphicsScene
from gameqt.graphics import QGraphicsRectItem, QGraphicsEllipseItem
from gameqt.gui import QPen, QBrush, QColor

# Create scene and view
scene = QGraphicsScene()
view = QGraphicsView(scene)
view.resize(600, 400)

# Add a rectangle
rect = QGraphicsRectItem(50, 50, 200, 100)
rect.setPen(QPen(QColor(255, 0, 0), 3))
rect.setBrush(QBrush(QColor(0, 255, 0, 100)))
rect.setFlags(QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable | 
              QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable)
scene.addItem(rect)

# Add an ellipse
ellipse = QGraphicsEllipseItem(300, 50, 150, 150)
ellipse.setPen(QPen(QColor(0, 0, 255), 2))
ellipse.setBrush(QBrush(QColor(255, 255, 0, 150)))
ellipse.setFlags(QGraphicsEllipseItem.GraphicsItemFlag.ItemIsMovable)
scene.addItem(ellipse)

view.show()
```

### Custom Drawing with QPainter

```python
from gameqt.widgets import QWidget
from gameqt.gui import QPainter, QPen, QColor
from gameqt.application import QApplication

class DrawingWidget(QWidget):
    def _draw(self, pos):
        super()._draw(pos)
        
        if not QApplication._instance: return
        screen = QApplication._instance._windows[0]._screen
        
        painter = QPainter(screen)
        painter.setPen(QPen(QColor(255, 0, 0), 2))
        
        # Draw a line
        painter.drawLine(pos.x + 10, pos.y + 10, 
                        pos.x + 200, pos.y + 100)
        
        # Draw a rectangle
        import pygame
        painter.drawRect(pygame.Rect(pos.x + 50, pos.y + 120, 
                                     100, 80))
```

---

## 6. Menus and Actions

### Creating a Menu Bar

```python
from gameqt.menus import QMenuBar, QAction

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Create menu bar
        menubar = QMenuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        open_action = QAction("Open", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.on_open)
        file_menu.addAction(open_action)
        
        save_action = QAction("Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.on_save)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("Edit")
        copy_action = QAction("Copy", self)
        copy_action.setShortcut("Ctrl+C")
        edit_menu.addAction(copy_action)
        
        self.setMenuBar(menubar)
    
    def on_open(self):
        print("Open file")
    
    def on_save(self):
        print("Save file")
```

### Context Menus

```python
from gameqt.menus import QMenu

class MyWidget(QWidget):
    def contextMenuEvent(self, event):
        menu = QMenu(self)
        
        copy_action = menu.addAction("Copy")
        paste_action = menu.addAction("Paste")
        menu.addSeparator()
        delete_action = menu.addAction("Delete")
        
        action = menu.exec(event.globalPos())
        
        if action == copy_action:
            self.copy()
        elif action == paste_action:
            self.paste()
        elif action == delete_action:
            self.delete()
```

---

## 7. Clipboard and Drag & Drop

### Using the Clipboard

```python
from gameqt.application import QApplication

# Copy to clipboard
clipboard = QApplication.clipboard()
clipboard.setText("Hello, Clipboard!")

# Paste from clipboard
text = clipboard.text()
print(f"Clipboard contains: {text}")
```

### Drag and Drop

```python
class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()
    
    def dropEvent(self, event):
        mime = event.mimeData()
        if mime.hasUrls():
            for url in mime.urls():
                file_path = url.toLocalFile()
                print(f"Dropped file: {file_path}")
            event.accept()
```

---

## 8. Advanced Topics

### Tree Widgets

```python
from gameqt.item_views import QTreeWidget, QTreeWidgetItem
from gameqt.core import Qt

tree = QTreeWidget()
tree.setHeaderLabels(["Name", "Type", "Size"])

# Add root item
root = QTreeWidgetItem(tree)
root.setText(0, "Documents")
root.setText(1, "Folder")
root.setExpanded(True)

# Add child items
child1 = QTreeWidgetItem(root)
child1.setText(0, "report.pdf")
child1.setText(1, "PDF")
child1.setText(2, "1.2 MB")

child2 = QTreeWidgetItem(root)
child2.setText(0, "notes.txt")
child2.setText(1, "Text")
child2.setText(2, "5 KB")
```

### Rich Text in QTextEdit

```python
from gameqt.widgets import QTextEdit

text_edit = QTextEdit()
html = """
<h2>Welcome to GameQt</h2>
<p>This is a <b>bold</b> and <i>italic</i> text.</p>
<p><font color="#FF0000">Red text</font> and <font color="#0000FF">blue text</font>.</p>
<ul>
    <li>Item 1</li>
    <li>Item 2</li>
    <li>Item 3</li>
</ul>
"""
text_edit.setHtml(html)
```

### Undo/Redo System

```python
from gameqt.utils import QUndoStack, QUndoCommand

class AddTextCommand(QUndoCommand):
    def __init__(self, text_edit, text):
        super().__init__("Add Text")
        self.text_edit = text_edit
        self.text = text
        self.old_text = text_edit.toPlainText()
    
    def undo(self):
        self.text_edit.setPlainText(self.old_text)
    
    def redo(self):
        self.text_edit.setPlainText(self.old_text + self.text)

# Usage
undo_stack = QUndoStack()
cmd = AddTextCommand(text_edit, "New text")
undo_stack.push(cmd)

# Later
undo_stack.undo()  # Undo the change
undo_stack.redo()  # Redo the change
```

---

## Next Steps

- Explore the [API Reference](API_REFERENCE.md) for complete documentation
- Check out [Examples](EXAMPLES.md) for more code samples
- Read [Architecture](ARCHITECTURE.md) to understand how GameQt works internally

Happy coding with GameQt! 🎮✨
