
import sys
import os

# Ensure gameqt is in path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
if os.path.join(project_root, 'pdf_visual_editor') not in sys.path:
     sys.path.insert(0, os.path.join(project_root, 'pdf_visual_editor'))

from gameqt.application import QApplication
from gameqt.widgets import QMainWindow, QWidget, QPushButton, QLineEdit
from gameqt.layouts import QVBoxLayout, QGridLayout

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

def main():
    app = QApplication(sys.argv)
    calc = Calculator()
    calc.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
