import sys
import os
from qt_compat import QApplication
from gui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("PDF Visual Editor")
    
    window = MainWindow()
    window.show()
    
    # Compatibility for PySide2 (uses exec_) vs PyQt6/PySide6 (uses exec)
    if hasattr(app, 'exec'):
        sys.exit(app.exec())
    else:
        sys.exit(app.exec_())

if __name__ == "__main__":
    main()
