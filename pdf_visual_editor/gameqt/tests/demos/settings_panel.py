
import sys
import os

# Ensure gameqt is in path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
if os.path.join(project_root, 'pdf_visual_editor') not in sys.path:
     sys.path.insert(0, os.path.join(project_root, 'pdf_visual_editor'))

from gameqt.widgets import (QWidget, QLabel, QCheckBox, QComboBox, 
                             QSlider, QPushButton, QMainWindow)
from gameqt.layouts import QVBoxLayout, QFormLayout, QHBoxLayout
from gameqt.core import Qt
from gameqt.application import QApplication

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

def main():
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("Settings Panel")
    window.setCentralWidget(SettingsPanel())
    window.resize(400, 300)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
