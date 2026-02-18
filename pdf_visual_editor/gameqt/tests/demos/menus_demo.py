
import sys
import os

# Ensure gameqt is in path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
if os.path.join(project_root, 'pdf_visual_editor') not in sys.path:
     sys.path.insert(0, os.path.join(project_root, 'pdf_visual_editor'))

from gameqt.application import QApplication
from gameqt.widgets import QMainWindow, QWidget, QLabel
from gameqt.layouts import QVBoxLayout
from gameqt.menus import QMenuBar, QAction

class MenusDemo(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GameQt Menus Demo")
        self.resize(500, 300)
        
        central = QWidget()
        layout = QVBoxLayout(central)
        self.status = QLabel("Try the menu bar at the top!")
        layout.addWidget(self.status)
        
        # Menu
        menubar = QMenuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        new_act = QAction("New", self)
        new_act.triggered.connect(lambda: self.status.setText("Action: New clicked"))
        file_menu.addAction(new_act)
        
        save_act = QAction("Save", self)
        save_act.triggered.connect(lambda: self.status.setText("Action: Save clicked"))
        file_menu.addAction(save_act)
        
        file_menu.addSeparator()
        
        exit_act = QAction("Exit", self)
        exit_act.triggered.connect(self.close)
        file_menu.addAction(exit_act)
        
        # Edit menu
        edit_menu = menubar.addMenu("Edit")
        cut_act = QAction("Cut", self)
        cut_act.triggered.connect(lambda: self.status.setText("Action: Cut clicked"))
        edit_menu.addAction(cut_act)
        
        self.setMenuBar(menubar)
        self.setCentralWidget(central)
        central.show()

def main():
    app = QApplication(sys.argv)
    demo = MenusDemo()
    demo.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
