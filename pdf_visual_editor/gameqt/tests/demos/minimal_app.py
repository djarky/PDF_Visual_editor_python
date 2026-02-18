
import sys
import os

# Ensure gameqt is in path for these demos if run directly
current_dir = os.path.dirname(os.path.abspath(__file__))
# Go up two levels to reach pdf_visual_editor/tests/demos -> pdf_visual_editor
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
if project_root not in sys.path:
    sys.path.insert(0, os.path.join(project_root, 'pdf_visual_editor'))

# Fallback: try adding the parent of the current file's directory (assuming run from tests/demos)
# or the current directory itself if the package structure is different.
# But following the "from gameqt" pattern, we need the folder CONTAINING gameqt in path.
# gameqt is in pdf_visual_editor/gameqt. So we need pdf_visual_editor in path?
# If we add project_root/pdf_visual_editor, then "import gameqt" works.

if os.path.join(project_root, 'pdf_visual_editor') not in sys.path:
     sys.path.insert(0, os.path.join(project_root, 'pdf_visual_editor'))

from gameqt.application import QApplication
from gameqt.widgets import QMainWindow, QLabel

def main():
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("Minimal App")
    window.resize(300, 200)

    label = QLabel()
    label.setText("Hello, World!")
    window.setCentralWidget(label)

    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
