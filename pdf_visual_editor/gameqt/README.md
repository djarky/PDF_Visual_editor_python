# GameQt - Qt-Compatible GUI Framework for Pygame

**GameQt** is a comprehensive Qt-compatible GUI framework built on top of Pygame, providing a familiar Qt-like API for creating desktop applications with Pygame as the rendering backend. Perfect for projects that need Qt's API but want to use Pygame's capabilities.

## 🌟 Features

### Core Features
- **Qt-Compatible API**: Familiar Qt classes and methods (QWidget, QMainWindow, QApplication, etc.)
- **Event System**: Complete signal/slot mechanism and event bubbling
- **Rich Widgets**: Buttons, labels, text inputs, checkboxes, radio buttons, combo boxes, spin boxes, and more
- **Advanced Layouts**: VBox, HBox, Grid, Form, Stacked, and Splitter layouts
- **Graphics Framework**: QGraphicsView/Scene architecture for 2D graphics and custom rendering

### Advanced Features
- **Tree & List Views**: QTreeWidget and QListWidget with full hierarchy support
- **Clipboard Integration**: System clipboard support via pygame.scrap
- **Drag & Drop**: External file drag and drop from file managers
- **Menu System**: Menu bars, context menus, and actions
- **Dialogs**: File dialogs, color picker, font selector, message boxes
- **Rich Text**: HTML rendering with bold, italic, colors, lists, and tables
- **Scrolling**: High-precision scroll support for trackpads and mice

### Graphics & Rendering
- **QPainter**: Drawing primitives (lines, rectangles, ellipses, polygons)
- **Transformations**: Rotation, scaling, translation with QTransform
- **Graphics Items**: Pixmap, text, rect, ellipse items with selection and manipulation
- **Custom Rendering**: Override paint events for custom widgets

## 📦 Installation

GameQt is included as part of the PDF Visual Editor project. It requires:

```bash
pip install pygame-ce>=2.4.0
```

## 🚀 Quick Start

### Hello World

```python
from gameqt.application import QApplication
from gameqt.widgets import QMainWindow, QLabel
import sys

app = QApplication(sys.argv)

window = QMainWindow()
window.setWindowTitle("Hello GameQt")
window.resize(400, 300)

label = QLabel()
label.setText("Hello, World!")
window.setCentralWidget(label)

window.show()
sys.exit(app.exec())
```

### Simple Form with Layout

```python
from gameqt.application import QApplication
from gameqt.widgets import QMainWindow, QWidget, QLabel, QLineEdit, QPushButton
from gameqt.layouts import QVBoxLayout, QFormLayout
import sys

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Form Example")
        self.resize(400, 300)
        
        central = QWidget()
        layout = QVBoxLayout(central)
        
        # Form
        form = QFormLayout()
        self.name_input = QLineEdit()
        self.email_input = QLineEdit()
        
        form.addRow("Name:", self.name_input)
        form.addRow("Email:", self.email_input)
        layout.addLayout(form)
        
        # Button
        submit_btn = QPushButton("Submit")
        submit_btn.clicked.connect(self.on_submit)
        layout.addWidget(submit_btn)
        
        self.setCentralWidget(central)
        central.show()
    
    def on_submit(self):
        name = self.name_input.text()
        email = self.email_input.text()
        print(f"Submitted: {name}, {email}")

app = QApplication(sys.argv)
window = MyWindow()
window.show()
sys.exit(app.exec())
```

### Graphics View Example

```python
from gameqt.application import QApplication
from gameqt.graphics import QGraphicsView, QGraphicsScene, QGraphicsRectItem
from gameqt.gui import QPen, QBrush, QColor
from gameqt.core import Qt
import sys

app = QApplication(sys.argv)

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

view.show()
sys.exit(app.exec())
```

## 📚 Documentation

- **[API Reference](API_REFERENCE.md)** - Complete API documentation
- **[Tutorial](TUTORIAL.md)** - Step-by-step tutorials
- **[Examples](EXAMPLES.md)** - Code examples and recipes
- **[Architecture](ARCHITECTURE.md)** - Internal design and architecture

## 🏗️ Architecture

GameQt is organized into several modules:

- **`core.py`** - Core classes (Qt, QObject, Signal, Events, QMimeData, QClipboard)
- **`application.py`** - QApplication and main event loop
- **`widgets.py`** - All widget classes (QWidget, QMainWindow, controls)
- **`layouts.py`** - Layout managers (QVBoxLayout, QHBoxLayout, QGridLayout, etc.)
- **`graphics.py`** - Graphics framework (QGraphicsView, QGraphicsScene, items)
- **`gui.py`** - GUI utilities (QPainter, QPen, QBrush, QColor, QPixmap)
- **`item_views.py`** - Tree and list widgets (QTreeWidget, QListWidget)
- **`menus.py`** - Menu system (QMenuBar, QMenu, QAction)
- **`utils.py`** - Utility classes (QSettings, QUndoStack)

## 🎯 Use Cases

GameQt is ideal for:

- **Desktop Applications**: Build full-featured desktop apps with Qt API
- **Game Tools**: Level editors, asset managers, debug consoles
- **Prototyping**: Quickly prototype UIs with familiar Qt syntax
- **Education**: Learn Qt concepts with a simpler implementation
- **Cross-Platform**: Works anywhere Pygame runs (Windows, macOS, Linux)

## 🔧 Key Differences from Qt

While GameQt aims for Qt compatibility, there are some differences:

1. **Rendering**: Uses Pygame instead of native widgets
2. **Performance**: Suitable for tools and editors, not high-performance UIs
3. **Styling**: Limited CSS support, custom drawing via QPainter
4. **Threading**: Single-threaded event loop
5. **Clipboard**: Uses pygame.scrap (may have platform limitations)

## 🤝 Contributing

GameQt is part of the PDF Visual Editor project. Contributions are welcome!

## 📄 License

This project is part of the PDF Visual Editor and follows its license terms.

## 🙏 Acknowledgments

- Built on top of [Pygame Community Edition](https://github.com/pygame-community/pygame-ce)
- Inspired by [Qt for Python (PySide6)](https://doc.qt.io/qtforpython/)
- Developed as part of the PDF Visual Editor project

## 📞 Support

For issues, questions, or contributions, please refer to the main PDF Visual Editor project.

---

**GameQt** - Bringing Qt's elegance to Pygame's flexibility! 🎮✨
