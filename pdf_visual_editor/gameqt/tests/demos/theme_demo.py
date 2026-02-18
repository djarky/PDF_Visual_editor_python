
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from gameqt import QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout, QLabel

def load_qss(path):
    if not os.path.exists(path):
        print(f"Warning: {path} not found")
        return ""
    with open(path, 'r') as f:
        return f.read()

def main():
    app = QApplication(sys.argv)
    
    # Paths to themes
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    dark_path = os.path.join(root_dir, 'themes', 'dark_theme.qss')
    light_path = os.path.join(root_dir, 'themes', 'light_theme.qss')
    
    # 1. Create Window
    window = QMainWindow()
    window.setWindowTitle("QSS Theme Demo")
    window.resize(400, 300)
    
    central = QWidget(window)
    layout = QVBoxLayout(central)
    window.setCentralWidget(central)
    
    label = QLabel("Dynamic Theme Switching Demo", central)
    layout.addWidget(label)
    
    btn_dark = QPushButton("Apply Dark Theme", central)
    btn_dark.clicked.connect(lambda: app.setStyleSheet(load_qss(dark_path)))
    layout.addWidget(btn_dark)
    
    btn_light = QPushButton("Apply Light Theme", central)
    btn_light.clicked.connect(lambda: app.setStyleSheet(load_qss(light_path)))
    layout.addWidget(btn_light)
    
    btn_custom = QPushButton("Custom Local Style (Yellow Bg)", central)
    btn_custom.setStyleSheet("background-color: #ffff00; color: #000000; border-radius: 10px;")
    layout.addWidget(btn_custom)
    
    # Start with light theme
    app.setStyleSheet(load_qss(light_path))
    
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
