
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
from gameqt.layouts import QVBoxLayout, QHBoxLayout

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

def main():
    app = QApplication(sys.argv)
    todo = TodoApp()
    todo.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
