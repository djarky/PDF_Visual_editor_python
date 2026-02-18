"""
Unit tests for GameQt error handling system.
"""

import unittest
import sys
import os
import tempfile

# Mock pygame before importing gameqt
from unittest.mock import MagicMock
sys.modules['pygame'] = MagicMock()

# Ensure pdf_visual_editor is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from gameqt.error_handler import (
    GameQtError,
    GameQtNotImplementedError,
    GameQtExternalError,
    GameQtInternalError,
    ErrorCategory,
    GameQtLogger,
    LogLevel,
    get_logger
)


class TestCustomExceptions(unittest.TestCase):
    """Test custom exception classes."""
    
    def test_gameqt_error_base(self):
        """Test base GameQtError exception."""
        error = GameQtError("Test error", module="test.module")
        self.assertEqual(error.message, "Test error")
        self.assertEqual(error.module, "test.module")
        self.assertEqual(error.category, ErrorCategory.INTERNAL)
    
    def test_not_implemented_error(self):
        """Test GameQtNotImplementedError."""
        error = GameQtNotImplementedError("Feature not implemented")
        self.assertEqual(error.category, ErrorCategory.IMPLEMENTATION)
        self.assertIn("Feature not implemented", str(error))
    
    def test_external_error(self):
        """Test GameQtExternalError."""
        error = GameQtExternalError("File not found")
        self.assertEqual(error.category, ErrorCategory.EXTERNAL)
    
    def test_internal_error(self):
        """Test GameQtInternalError."""
        error = GameQtInternalError("Internal bug")
        self.assertEqual(error.category, ErrorCategory.INTERNAL)


class TestGameQtLogger(unittest.TestCase):
    """Test GameQtLogger functionality."""
    
    def setUp(self):
        """Set up test logger with temporary file."""
        self.logger = GameQtLogger.get_instance()
        # Use temp file for testing
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log')
        self.temp_file.close()
        self.logger.set_log_file(self.temp_file.name)
        self.logger.set_level(LogLevel.DEBUG)
        self.logger.set_show_dialogs(False)  # Disable dialogs for unit tests
    
    def tearDown(self):
        """Clean up temp file."""
        try:
            os.unlink(self.temp_file.name)
        except:
            pass
    
    def test_singleton(self):
        """Test logger is singleton."""
        logger1 = GameQtLogger.get_instance()
        logger2 = GameQtLogger.get_instance()
        self.assertIs(logger1, logger2)
    
    def test_set_level(self):
        """Test setting log level."""
        self.logger.set_level(LogLevel.ERROR)
        self.assertEqual(self.logger.level, LogLevel.ERROR)
        
        # Test setting by int value
        self.logger.set_level(20)  # INFO
        self.assertEqual(self.logger.level, LogLevel.INFO)
    
    def test_should_log(self):
        """Test log level filtering."""
        self.logger.set_level(LogLevel.WARNING)
        
        self.assertFalse(self.logger._should_log(LogLevel.DEBUG))
        self.assertFalse(self.logger._should_log(LogLevel.INFO))
        self.assertTrue(self.logger._should_log(LogLevel.WARNING))
        self.assertTrue(self.logger._should_log(LogLevel.ERROR))
    
    def test_log_writing(self):
        """Test that logs are written to file."""
        self.logger.debug("test.module", "Debug message")
        self.logger.info("test.module", "Info message")
        self.logger.warning("test.module", "Warning message")
        self.logger.error("test.module", "Error message")
        
        # Read log file
        with open(self.temp_file.name, 'r') as f:
            content = f.read()
        
        self.assertIn("DEBUG", content)
        self.assertIn("INFO", content)
        self.assertIn("WARNING", content)
        self.assertIn("ERROR", content)
        self.assertIn("test.module", content)
        self.assertIn("Debug message", content)
    
    def test_log_level_filtering_in_file(self):
        """Test that log level affects what's written."""
        # Clear log file
        with open(self.temp_file.name, 'w') as f:
            f.write("")
        
        # Set to WARNING level
        self.logger.set_level(LogLevel.WARNING)
        
        self.logger.debug("test.module", "Should not appear")
        self.logger.info("test.module", "Should not appear either")
        self.logger.warning("test.module", "Should appear")
        self.logger.error("test.module", "Should also appear")
        
        with open(self.temp_file.name, 'r') as f:
            content = f.read()
        
        self.assertNotIn("Should not appear", content)
        self.assertIn("Should appear", content)
        self.assertIn("Should also appear", content)
    
    def test_dialog_enable_disable(self):
        """Test enabling/disabling dialogs."""
        self.logger.set_show_dialogs(True)
        self.assertTrue(self.logger.show_dialogs)
        
        self.logger.set_show_dialogs(False)
        self.assertFalse(self.logger.show_dialogs)
    
    def test_get_logger_convenience(self):
        """Test get_logger() convenience function."""
        logger = get_logger()
        self.assertIsInstance(logger, GameQtLogger)
        self.assertIs(logger, self.logger)


class TestErrorCategories(unittest.TestCase):
    """Test ErrorCategory enum."""
    
    def test_category_values(self):
        """Test that all categories have correct string values."""
        self.assertEqual(ErrorCategory.IMPLEMENTATION.value, "Implementation Error")
        self.assertEqual(ErrorCategory.EXTERNAL.value, "External Error")
        self.assertEqual(ErrorCategory.INTERNAL.value, "Internal Error")
        self.assertEqual(ErrorCategory.WARNING.value, "Warning")


if __name__ == '__main__':
    unittest.main()
