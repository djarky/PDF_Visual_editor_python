import sys
import os

# Ensure gameqt is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from gameqt import QApplication, QMainWindow, QAction, QMenu

def main():
    app = QApplication(sys.argv)
    
    window = QMainWindow()
    window.resize(600, 400)
    window.setWindowTitle("Menu Submenu Test")
    
    # Menu Bar
    menu_bar = window.menuBar()
    
    # File Menu
    file_menu = menu_bar.addMenu("File")
    
    # Standard Action
    new_action = QAction("New", window)
    new_action.triggered.connect(lambda: print("New Action Triggered"))
    file_menu.addAction(new_action)
    
    file_menu.addSeparator()
    
    # Submenu
    recent_menu = QMenu("Recent Files", window)
    file_menu.addAction(recent_menu)
    
    # Actions in Submenu
    file1 = QAction("document1.pdf", window)
    file1.triggered.connect(lambda: print("Opened document1.pdf"))
    recent_menu.addAction(file1)
    
    file2 = QAction("document2.pdf", window)
    file2.triggered.connect(lambda: print("Opened document2.pdf"))
    recent_menu.addAction(file2)
    
    file_menu.addSeparator()
    
    exit_action = QAction("Exit", window)
    exit_action.triggered.connect(window.close)
    file_menu.addAction(exit_action)
    
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
