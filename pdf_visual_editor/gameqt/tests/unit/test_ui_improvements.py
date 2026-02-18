import sys
import os
import pygame

# Add parent directory to path so we can import gameqt
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from gameqt.application import QApplication
from gameqt.widgets import QMainWindow, QWidget, QLabel, QPushButton, QTextEdit, QGroupBox, QToolBar
from gameqt.menus import QAction
from gameqt.core import Qt

def test_ui_improvements():
    app = QApplication(sys.argv)
    win = QMainWindow()
    win.setWindowTitle("GameQt UI Improvements Demo")
    win.resize(600, 500)
    
    # 1. ToolBar
    toolbar = QToolBar("Main Toolbar", win)
    action1 = QAction("Action 1", win)
    action1.triggered.connect(lambda: print("Action 1 Triggered!"))
    toolbar.addAction(action1)
    
    # 2. Main Layout
    central = QWidget()
    from gameqt.layouts import QVBoxLayout, QHBoxLayout
    layout = QVBoxLayout(central)
    
    # CSS Test
    css_widget = QWidget()
    css_widget.setStyleSheet("background-color: #ffcccc; border: 1px solid red;")
    css_widget.resize(100, 50)
    layout.addWidget(QLabel("Widget below has CSS background red-ish:"))
    layout.addWidget(css_widget)
    
    # 3. GroupBox
    group = QGroupBox("Input Section")
    glayout = QVBoxLayout(group)
    glayout.addWidget(QLabel("Enter multi-line text below:"))
    
    text_edit = QTextEdit()
    text_edit.setPlainText("Hello,\nThis is a multiline edit test.\nYou can type here.")
    text_edit.textChanged.connect(lambda: print(f"Text length: {len(text_edit.toPlainText())}"))
    glayout.addWidget(text_edit)
    
    layout.addWidget(group)
    
    win.setCentralWidget(central)
    win.show()
    
    print("Test ready:")
    print("  - Click on QTextEdit to focus and type.")
    print("  - Click on 'Action 1' in toolbar.")
    print("  - Verify red-ish background on the top widget.")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    test_ui_improvements()
