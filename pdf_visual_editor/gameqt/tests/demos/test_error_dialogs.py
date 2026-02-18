"""
Visual test for GameQt error dialog and alert system.

Tests the error handling infrastructure with different error types.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from gameqt.application import QApplication
from gameqt.widgets import QMainWindow, QWidget, QPushButton
from gameqt.layouts import QVBoxLayout
from gameqt.error_handler import (
    GameQtNotImplementedError,
    GameQtExternalError,
    GameQtInternalError,
    ErrorCategory,
    show_error_dialog,
    get_logger
)


class ErrorTestWindow(QMainWindow):
    """Window for testing error dialogs."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GameQt Error Dialog Tests")
        self.resize(600, 400)
        
        # Central widget and layout
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout()
        central.setLayout(layout)
        
        # Test buttons for different error types
        btn1 = QPushButton("Show Implementation Error", self)
        btn1.setStyleSheet("padding: 10px; font-size: 14px; background-color: #FFA500;")
        btn1.clicked.connect(self.show_implementation_error)
        layout.addWidget(btn1)
        
        btn2 = QPushButton("Show External Error", self)
        btn2.setStyleSheet("padding: 10px; font-size: 14px; background-color: #F44336;")
        btn2.clicked.connect(self.show_external_error)
        layout.addWidget(btn2)
        
        btn3 = QPushButton("Show Internal Error", self)
        btn3.setStyleSheet("padding: 10px; font-size: 14px; background-color: #9C27B0;")
        btn3.clicked.connect(self.show_internal_error)
        layout.addWidget(btn3)
        
        btn4 = QPushButton("Show Warning", self)
        btn4.setStyleSheet("padding: 10px; font-size: 14px; background-color: #2196F3;")
        btn4.clicked.connect(self.show_warning)
        layout.addWidget(btn4)
        
        btn5 = QPushButton("Test Logger (Check Console)", self)
        btn5.setStyleSheet("padding: 10px; font-size: 14px; background-color: #4CAF50;")
        btn5.clicked.connect(self.test_logger)
        layout.addWidget(btn5)
        
        btn_quit = QPushButton("Quit", self)
        btn_quit.setStyleSheet("padding: 10px; font-size: 14px; background-color: #757575;")
        btn_quit.clicked.connect(QApplication.instance().quit)
        layout.addWidget(btn_quit)
        
    def show_implementation_error(self):
        """Show an implementation error dialog."""
        error = GameQtNotImplementedError(
            "The feature 'SuperWidget.advancedFeature()' has not been fully implemented yet.",
            module="test.ErrorTestWindow"
        )
        show_error_dialog(
            "test.ErrorTestWindow",
            "The feature 'SuperWidget.advancedFeature()' is not implemented.",
            ErrorCategory.IMPLEMENTATION,
            error
        )
    
    def show_external_error(self):
        """Show an external error dialog."""
        error = GameQtExternalError(
            "Failed to open file '/nonexistent/file.txt': No such file or directory",
            module="test.ErrorTestWindow"
        )
        show_error_dialog(
            "test.ErrorTestWindow",
            "Failed to open file '/nonexistent/file.txt'",
            ErrorCategory.EXTERNAL,
            error
        )
    
    def show_internal_error(self):
        """Show an internal error dialog."""
        error = GameQtInternalError(
            "Unexpected state in layout manager: widget has negative size",
            module="test.ErrorTestWindow"
        )
        show_error_dialog(
            "test.ErrorTestWindow",
            "Unexpected state in layout manager",
            ErrorCategory.INTERNAL,
            error
        )
    
    def show_warning(self):
        """Show a warning dialog."""
        show_error_dialog(
            "test.ErrorTestWindow",
            "This widget's minimum size is below recommended values (50x20)",
            ErrorCategory.WARNING,
            None
        )
    
    def test_logger(self):
        """Test logger output."""
        logger = get_logger()
        
        # Test all log levels
        logger.debug("test.ErrorTestWindow", "This is a DEBUG message")
        logger.info("test.ErrorTestWindow", "This is an INFO message")
        logger.warning("test.ErrorTestWindow", "This is a WARNING message")
        logger.error("test.ErrorTestWindow", "This is an ERROR message", show_dialog=False)
        
        print("\\n--- Logger test complete. Check console and gameqt.log file ---\\n")


if __name__ == "__main__":
    app = QApplication([])
    
    # Configure logger for testing
    logger = get_logger()
    logger.set_level(logger.DEBUG)  # Show all messages
    logger.set_show_dialogs(True)   # Enable dialogs
    
    print("=" * 60)
    print("GameQt Error Dialog Test")
    print("=" * 60)
    print("Click buttons to test different error types.")
    print(f"Log file: {logger.log_file}")
    print("=" * 60)
    
    window = ErrorTestWindow()
    window.show()
    
    sys.exit(app.exec())
