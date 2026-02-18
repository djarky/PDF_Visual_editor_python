
import sys
import os

# Ensure gameqt is in path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
if os.path.join(project_root, 'pdf_visual_editor') not in sys.path:
     sys.path.insert(0, os.path.join(project_root, 'pdf_visual_editor'))

from gameqt.application import QApplication
from gameqt.widgets import (QMainWindow, QWidget, QLabel, QLineEdit, 
                             QPushButton, QCheckBox)
from gameqt.layouts import QVBoxLayout, QFormLayout, QHBoxLayout

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

def main():
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
