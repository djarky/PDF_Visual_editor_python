# GameQt Examples

Practical code examples and recipes for common tasks.

## Table of Contents

1. [Basic Applications](#basic-applications)
2. [Forms and Input](#forms-and-input)
3. [Graphics and Drawing](#graphics-and-drawing)
4. [File Operations](#file-operations)
5. [Custom Widgets](#custom-widgets)
6. [Real-World Applications](#real-world-applications)

---

## Basic Applications

### Minimal Application

```python
import sys
from gameqt.application import QApplication
from gameqt.widgets import QMainWindow, QLabel

app = QApplication(sys.argv)
window = QMainWindow()
window.setWindowTitle("Minimal App")
window.resize(300, 200)

label = QLabel()
label.setText("Hello, World!")
window.setCentralWidget(label)

window.show()
sys.exit(app.exec())
```

### Calculator

```python
from gameqt.application import QApplication
from gameqt.widgets import QMainWindow, QWidget, QPushButton, QLineEdit
from gameqt.layouts import QVBoxLayout, QGridLayout
import sys

class Calculator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calculator")
        self.resize(300, 400)
        
        central = QWidget()
        layout = QVBoxLayout(central)
        
        # Display
        self.display = QLineEdit()
        self.display.setReadOnly(True)
        layout.addWidget(self.display)
        
        # Buttons
        grid = QGridLayout()
        buttons = [
            ['7', '8', '9', '/'],
            ['4', '5', '6', '*'],
            ['1', '2', '3', '-'],
            ['0', '.', '=', '+']
        ]
        
        for row, button_row in enumerate(buttons):
            for col, button_text in enumerate(button_row):
                btn = QPushButton(button_text)
                btn.clicked.connect(lambda t=button_text: self.on_button(t))
                grid.addWidget(btn, row, col)
        
        layout.addLayout(grid)
        self.setCentralWidget(central)
        central.show()
        
        self.current = ""
    
    def on_button(self, text):
        if text == '=':
            try:
                result = eval(self.current)
                self.display.setText(str(result))
                self.current = str(result)
            except:
                self.display.setText("Error")
                self.current = ""
        else:
            self.current += text
            self.display.setText(self.current)

app = QApplication(sys.argv)
calc = Calculator()
calc.show()
sys.exit(app.exec())
```

---

## Forms and Input

### Login Form

```python
from gameqt.application import QApplication
from gameqt.widgets import (QMainWindow, QWidget, QLabel, QLineEdit, 
                             QPushButton, QCheckBox)
from gameqt.layouts import QVBoxLayout, QFormLayout, QHBoxLayout
import sys

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")
        self.resize(400, 250)
        
        central = QWidget()
        main_layout = QVBoxLayout(central)
        
        # Title
        title = QLabel()
        title.setText("User Login")
        main_layout.addWidget(title)
        
        # Form
        form = QFormLayout()
        self.username = QLineEdit()
        self.password = QLineEdit()
        # Note: GameQt doesn't have password mode yet, but you can add it
        
        form.addRow("Username:", self.username)
        form.addRow("Password:", self.password)
        main_layout.addLayout(form)
        
        # Remember me
        self.remember = QCheckBox("Remember me")
        main_layout.addWidget(self.remember)
        
        # Buttons
        btn_layout = QHBoxLayout()
        login_btn = QPushButton("Login")
        login_btn.clicked.connect(self.on_login)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.close)
        
        btn_layout.addStretch()
        btn_layout.addWidget(login_btn)
        btn_layout.addWidget(cancel_btn)
        main_layout.addLayout(btn_layout)
        
        self.setCentralWidget(central)
        central.show()
    
    def on_login(self):
        username = self.username.text()
        password = self.password.text()
        remember = self.remember.isChecked()
        
        print(f"Login: {username}")
        print(f"Remember: {remember}")
        # Add actual authentication here

app = QApplication(sys.argv)
window = LoginWindow()
window.show()
sys.exit(app.exec())
```

### Settings Panel

```python
from gameqt.widgets import (QWidget, QLabel, QCheckBox, QComboBox, 
                             QSlider, QPushButton)
from gameqt.layouts import QVBoxLayout, QFormLayout, QHBoxLayout
from gameqt.core import Qt

class SettingsPanel(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        # Form
        form = QFormLayout()
        
        # Theme selection
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark", "System"])
        form.addRow("Theme:", self.theme_combo)
        
        # Volume slider
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        form.addRow("Volume:", self.volume_slider)
        
        # Checkboxes
        self.auto_save = QCheckBox("Auto-save")
        self.auto_save.setChecked(True)
        form.addRow("", self.auto_save)
        
        self.notifications = QCheckBox("Enable notifications")
        form.addRow("", self.notifications)
        
        layout.addLayout(form)
        
        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_settings)
        reset_btn = QPushButton("Reset")
        
        btn_layout.addStretch()
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(reset_btn)
        layout.addLayout(btn_layout)
    
    def save_settings(self):
        theme = self.theme_combo.currentText()
        volume = self.volume_slider.value()
        auto_save = self.auto_save.isChecked()
        notifications = self.notifications.isChecked()
        
        print(f"Settings saved:")
        print(f"  Theme: {theme}")
        print(f"  Volume: {volume}")
        print(f"  Auto-save: {auto_save}")
        print(f"  Notifications: {notifications}")
```

---

## Graphics and Drawing

### Drawing Board

```python
from gameqt.graphics import QGraphicsView, QGraphicsScene, QGraphicsEllipseItem
from gameqt.gui import QPen, QBrush, QColor
from gameqt.core import Qt

class DrawingBoard(QGraphicsView):
    def __init__(self):
        scene = QGraphicsScene()
        super().__init__(scene)
        self.resize(600, 400)
        self.setWindowTitle("Drawing Board")
        
        self.drawing = False
        self.last_pos = None
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = True
            self.last_pos = self.mapToScene(event.pos())
    
    def mouseMoveEvent(self, event):
        if self.drawing and self.last_pos:
            current_pos = self.mapToScene(event.pos())
            
            # Draw a small circle
            ellipse = QGraphicsEllipseItem(
                current_pos.x() - 2, current_pos.y() - 2, 4, 4
            )
            ellipse.setPen(QPen(QColor(0, 0, 0), 1))
            ellipse.setBrush(QBrush(QColor(0, 0, 0)))
            self.scene().addItem(ellipse)
            
            self.last_pos = current_pos
    
    def mouseReleaseEvent(self, event):
        self.drawing = False
        self.last_pos = None
```

### Shape Editor

```python
from gameqt.graphics import (QGraphicsView, QGraphicsScene, 
                              QGraphicsRectItem, QGraphicsEllipseItem)
from gameqt.gui import QPen, QBrush, QColor
from gameqt.widgets import QMainWindow, QWidget, QPushButton
from gameqt.layouts import QVBoxLayout, QHBoxLayout
import random

class ShapeEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Shape Editor")
        self.resize(800, 600)
        
        central = QWidget()
        layout = QVBoxLayout(central)
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        add_rect_btn = QPushButton("Add Rectangle")
        add_rect_btn.clicked.connect(self.add_rectangle)
        toolbar.addWidget(add_rect_btn)
        
        add_circle_btn = QPushButton("Add Circle")
        add_circle_btn.clicked.connect(self.add_circle)
        toolbar.addWidget(add_circle_btn)
        
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.clear_scene)
        toolbar.addWidget(clear_btn)
        
        toolbar.addStretch()
        layout.addLayout(toolbar)
        
        # Graphics view
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        layout.addWidget(self.view)
        
        self.setCentralWidget(central)
        central.show()
    
    def add_rectangle(self):
        x = random.randint(50, 400)
        y = random.randint(50, 300)
        w = random.randint(50, 150)
        h = random.randint(50, 150)
        
        rect = QGraphicsRectItem(x, y, w, h)
        rect.setPen(QPen(QColor(random.randint(0, 255), 
                                random.randint(0, 255), 
                                random.randint(0, 255)), 2))
        rect.setBrush(QBrush(QColor(random.randint(0, 255), 
                                    random.randint(0, 255), 
                                    random.randint(0, 255), 100)))
        rect.setFlags(QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable | 
                     QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable)
        self.scene.addItem(rect)
    
    def add_circle(self):
        x = random.randint(50, 400)
        y = random.randint(50, 300)
        size = random.randint(50, 150)
        
        ellipse = QGraphicsEllipseItem(x, y, size, size)
        ellipse.setPen(QPen(QColor(random.randint(0, 255), 
                                   random.randint(0, 255), 
                                   random.randint(0, 255)), 2))
        ellipse.setBrush(QBrush(QColor(random.randint(0, 255), 
                                       random.randint(0, 255), 
                                       random.randint(0, 255), 100)))
        ellipse.setFlags(QGraphicsEllipseItem.GraphicsItemFlag.ItemIsMovable | 
                        QGraphicsEllipseItem.GraphicsItemFlag.ItemIsSelectable)
        self.scene.addItem(ellipse)
    
    def clear_scene(self):
        self.scene.clear()
```

---

## File Operations

### Text Editor

```python
from gameqt.application import QApplication
from gameqt.widgets import QMainWindow, QTextEdit
from gameqt.menus import QMenuBar, QAction
import sys

class TextEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Text Editor")
        self.resize(600, 400)
        self.current_file = None
        
        # Text edit
        self.text_edit = QTextEdit()
        self.setCentralWidget(self.text_edit)
        
        # Menu
        menubar = QMenuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        new_action = QAction("New", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)
        
        open_action = QAction("Open", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        save_action = QAction("Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        self.setMenuBar(menubar)
    
    def new_file(self):
        self.text_edit.setPlainText("")
        self.current_file = None
        self.setWindowTitle("Text Editor - Untitled")
    
    def open_file(self):
        # In a real app, use QFileDialog
        filename = "example.txt"
        try:
            with open(filename, 'r') as f:
                content = f.read()
                self.text_edit.setPlainText(content)
                self.current_file = filename
                self.setWindowTitle(f"Text Editor - {filename}")
        except:
            print("Could not open file")
    
    def save_file(self):
        if not self.current_file:
            self.current_file = "untitled.txt"
        
        try:
            with open(self.current_file, 'w') as f:
                f.write(self.text_edit.toPlainText())
            print(f"Saved to {self.current_file}")
        except:
            print("Could not save file")

app = QApplication(sys.argv)
editor = TextEditor()
editor.show()
sys.exit(app.exec())
```

---

## Custom Widgets

### Color Picker Widget

```python
from gameqt.widgets import QWidget
from gameqt.gui import QColor
from gameqt.application import QApplication
from gameqt.core import Signal
import pygame

class ColorPicker(QWidget):
    colorChanged = Signal(QColor)
    
    def __init__(self):
        super().__init__()
        self.selected_color = QColor(255, 0, 0)
        self.colors = [
            QColor(255, 0, 0), QColor(0, 255, 0), QColor(0, 0, 255),
            QColor(255, 255, 0), QColor(255, 0, 255), QColor(0, 255, 255),
            QColor(255, 128, 0), QColor(128, 0, 255), QColor(0, 128, 255)
        ]
    
    def _draw(self, pos):
        super()._draw(pos)
        
        if not QApplication._instance: return
        screen = QApplication._instance._windows[0]._screen
        
        # Draw color swatches
        swatch_size = 40
        spacing = 10
        x = pos.x + 10
        y = pos.y + 10
        
        for i, color in enumerate(self.colors):
            if i % 3 == 0 and i > 0:
                x = pos.x + 10
                y += swatch_size + spacing
            
            # Draw swatch
            pygame.draw.rect(screen, color.to_pygame()[:3], 
                           (x, y, swatch_size, swatch_size))
            
            # Draw border
            border_color = (255, 255, 255) if color == self.selected_color else (100, 100, 100)
            pygame.draw.rect(screen, border_color, 
                           (x, y, swatch_size, swatch_size), 2)
            
            x += swatch_size + spacing
    
    def mousePressEvent(self, event):
        # Determine which color was clicked
        swatch_size = 40
        spacing = 10
        
        for i, color in enumerate(self.colors):
            col = i % 3
            row = i // 3
            x = 10 + col * (swatch_size + spacing)
            y = 10 + row * (swatch_size + spacing)
            
            if (x <= event.pos().x() <= x + swatch_size and
                y <= event.pos().y() <= y + swatch_size):
                self.selected_color = color
                self.colorChanged.emit(color)
                break
```

---

## Real-World Applications

### Todo List App

```python
from gameqt.application import QApplication
from gameqt.widgets import (QMainWindow, QWidget, QLabel, QLineEdit, 
                             QPushButton, QCheckBox)
from gameqt.layouts import QVBoxLayout, QHBoxLayout
import sys

class TodoApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Todo List")
        self.resize(400, 500)
        
        central = QWidget()
        layout = QVBoxLayout(central)
        
        # Title
        title = QLabel()
        title.setText("My Todo List")
        layout.addWidget(title)
        
        # Input area
        input_layout = QHBoxLayout()
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Enter a new task...")
        self.task_input.returnPressed.connect(self.add_task)
        input_layout.addWidget(self.task_input)
        
        add_btn = QPushButton("Add")
        add_btn.clicked.connect(self.add_task)
        input_layout.addWidget(add_btn)
        layout.addLayout(input_layout)
        
        # Task list container
        self.task_container = QWidget()
        self.task_layout = QVBoxLayout(self.task_container)
        layout.addWidget(self.task_container)
        
        layout.addStretch()
        
        self.setCentralWidget(central)
        central.show()
        
        self.tasks = []
    
    def add_task(self):
        task_text = self.task_input.text().strip()
        if not task_text:
            return
        
        # Create task widget
        task_widget = QWidget()
        task_layout = QHBoxLayout(task_widget)
        
        checkbox = QCheckBox(task_text)
        checkbox.stateChanged.connect(lambda state, t=task_text: self.on_task_toggled(t, state))
        task_layout.addWidget(checkbox)
        
        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(lambda t=task_widget: self.delete_task(t))
        task_layout.addWidget(delete_btn)
        
        self.task_layout.addWidget(task_widget)
        self.tasks.append(task_widget)
        
        self.task_input.setText("")
    
    def on_task_toggled(self, task, state):
        if state == 2:  # Checked
            print(f"Completed: {task}")
        else:
            print(f"Uncompleted: {task}")
    
    def delete_task(self, task_widget):
        self.task_layout.removeWidget(task_widget)
        self.tasks.remove(task_widget)
        task_widget.hide()

app = QApplication(sys.argv)
todo = TodoApp()
todo.show()
sys.exit(app.exec())
```

---

For more information, see:
- [API Reference](API_REFERENCE.md)
- [Tutorial](TUTORIAL.md)
- [Architecture](ARCHITECTURE.md)
