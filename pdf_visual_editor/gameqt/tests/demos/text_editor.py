
import sys
import os

# Ensure gameqt is in path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
if os.path.join(project_root, 'pdf_visual_editor') not in sys.path:
     sys.path.insert(0, os.path.join(project_root, 'pdf_visual_editor'))

from gameqt.application import QApplication
from gameqt.widgets import QMainWindow, QTextEdit
from gameqt.menus import QMenuBar, QAction

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

def main():
    app = QApplication(sys.argv)
    editor = TextEditor()
    editor.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
