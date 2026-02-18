"""
GameQt Error Handling and Logging System

Provides centralized error handling, custom exceptions, and logging
with optional error dialogs for debugging and user feedback.
"""

import sys
import os
import traceback
from enum import Enum
from datetime import datetime
import inspect


class ErrorCategory(Enum):
    """Categories for GameQt errors."""
    IMPLEMENTATION = "Implementation Error"  # Missing/incomplete feature
    EXTERNAL = "External Error"  # User or system issue
    INTERNAL = "Internal Error"  # Library bug
    WARNING = "Warning"  # Non-critical issue


class GameQtError(Exception):
    """Base exception for all GameQt errors."""
    category = ErrorCategory.INTERNAL
    
    def __init__(self, message, module=None):
        super().__init__(message)
        self.message = message
        self.module = module or self._get_caller_module()
    
    def _get_caller_module(self):
        """Auto-detect module name from caller."""
        frame = inspect.currentframe()
        try:
            # Go up the stack to find the actual caller
            for _ in range(5):
                if frame is None:
                    break
                frame = frame.f_back
                if frame and 'self' in frame.f_locals:
                    obj = frame.f_locals['self']
                    return obj.__class__.__module__ + '.' + obj.__class__.__name__
            return "gameqt.unknown"
        finally:
            del frame


class GameQtNotImplementedError(GameQtError):
    """Raised when a feature is not yet implemented."""
    category = ErrorCategory.IMPLEMENTATION


class GameQtExternalError(GameQtError):
    """Raised for errors from external sources (user input, file system, etc)."""
    category = ErrorCategory.EXTERNAL


class GameQtInternalError(GameQtError):
    """Raised for internal library bugs."""
    category = ErrorCategory.INTERNAL


class LogLevel(Enum):
    """Logging levels."""
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40


class GameQtLogger:
    """Centralized logging system for GameQt.
    
    Singleton logger that handles:
    - File logging to gameqt.log
    - Console output with optional colors
    - Error dialog display (optional)
    - Log level filtering
    """
    
    _instance = None
    
    def __init__(self):
        self.log_file = "gameqt.log"
        self.level = LogLevel.WARNING
        self.show_dialogs = True  # Can be disabled for production
        self._suppress_dialogs = False  # Temporary suppression
        
        # Convenience attributes for log levels
        self.DEBUG = LogLevel.DEBUG
        self.INFO = LogLevel.INFO
        self.WARNING = LogLevel.WARNING
        self.ERROR = LogLevel.ERROR
        
    @classmethod
    def get_instance(cls):
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def set_level(self, level):
        """Set minimum log level (LogLevel enum or int)."""
        if isinstance(level, int):
            for lvl in LogLevel:
                if lvl.value == level:
                    self.level = lvl
                    return
        self.level = level
    
    def set_show_dialogs(self, show):
        """Enable or disable error dialogs."""
        self.show_dialogs = show
    
    def set_log_file(self, path):
        """Set custom log file path."""
        self.log_file = path
    
    def _should_log(self, level):
        """Check if message should be logged at this level."""
        level_value = level.value if isinstance(level, LogLevel) else level
        return level_value >= self.level.value
    
    def _write_log(self, level, module, message):
        """Write to log file."""
        if not self._should_log(level):
            return
            
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        level_name = level.name if isinstance(level, LogLevel) else str(level)
        log_line = f"[{timestamp}] [{level_name}] {module}: {message}\n"
        
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_line)
        except:
            # If we can't write to log, print to stderr
            print(log_line, file=sys.stderr)
        
        # Also print to console for DEBUG and ERROR
        if level in (LogLevel.DEBUG, LogLevel.ERROR):
            print(log_line.strip(), file=sys.stderr if level == LogLevel.ERROR else sys.stdout)
    
    def debug(self, module, message):
        """Log debug message."""
        self._write_log(LogLevel.DEBUG, module, message)
    
    def info(self, module, message):
        """Log info message."""
        self._write_log(LogLevel.INFO, module, message)
    
    def warning(self, module, message):
        """Log warning message."""
        self._write_log(LogLevel.WARNING, module, message)
    
    def error(self, module, message, exception=None, show_dialog=None):
        """Log error message and optionally show dialog.
        
        Args:
            module: Module name where error occurred
            message: Error message
            exception: Optional exception object
            show_dialog: Override show_dialogs setting for this error
        """
        # Get traceback if exception provided
        tb_str = ""
        if exception:
            tb_str = "\\n" + "".join(traceback.format_exception(type(exception), exception, exception.__traceback__))
        
        self._write_log(LogLevel.ERROR, module, message + tb_str)
        
        # Show dialog if enabled
        should_show = show_dialog if show_dialog is not None else self.show_dialogs
        if should_show and not self._suppress_dialogs:
            # Determine category
            category = ErrorCategory.INTERNAL
            if isinstance(exception, GameQtError):
                category = exception.category
            
            show_error_dialog(module, message, category, exception)


def show_error_dialog(module, message, category=ErrorCategory.INTERNAL, exception=None):
    """Show error dialog using QMessageBox.
    
    Args:
        module: Module name where error occurred
        message: Error message
        category: ErrorCategory enum
        exception: Optional exception object for traceback
    """
    try:
        # Import here to avoid circular dependencies
        from .widgets import QMessageBox
        from .core import Qt
        
        # Create message box
        msg_box = QMessageBox()
        
        # Set title
        icon = "⚠️" if category == ErrorCategory.WARNING else "❌"
        if category == ErrorCategory.IMPLEMENTATION:
            icon = "🔧"
        msg_box.setWindowTitle(f"{icon} GameQt Error: {module}")
        
        # Build detailed message
        full_message = f"Type: {category.value}\\n\\n{message}"
        
        if category == ErrorCategory.IMPLEMENTATION:
            full_message += "\\n\\nThis feature has not been fully implemented yet."
        
        # Add traceback for debugging
        if exception:
            tb_lines = traceback.format_exception(type(exception), exception, exception.__traceback__)
            tb_str = "".join(tb_lines)
            full_message += f"\\n\\n--- Technical Details ---\\n{tb_str}"
        
        msg_box.setText(full_message)
        
        # Set icon based on category
        if category == ErrorCategory.WARNING:
            msg_box.setIcon(QMessageBox.Icon.Warning)
        else:
            msg_box.setIcon(QMessageBox.Icon.Critical)
        
        # Show dialog
        msg_box.exec()
        
    except Exception as e:
        # Fallback: print to console if dialog fails
        print(f"\\n{'='*60}", file=sys.stderr)
        print(f"GAMEQT ERROR: {module}", file=sys.stderr)
        print(f"Category: {category.value}", file=sys.stderr)
        print(f"Message: {message}", file=sys.stderr)
        if exception:
            print(f"\\nTraceback:", file=sys.stderr)
            traceback.print_exception(type(exception), exception, exception.__traceback__)
        print(f"{'='*60}\\n", file=sys.stderr)


# Create global logger instance
_logger = GameQtLogger.get_instance()

# Convenience functions
def get_logger():
    """Get the global GameQt logger instance."""
    return _logger
