import sys
import os
from unittest.mock import MagicMock

# Mock PyQt6 to force qt_compat to use PySide6
sys.modules["PyQt6"] = None
sys.modules["PyQt6.QtWidgets"] = None
sys.modules["PyQt6.QtCore"] = None
sys.modules["PyQt6.QtGui"] = None
sys.modules["PyQt6.QtPrintSupport"] = None

# Now import qt_compat
try:
    import qt_compat
    print(f"QT_API: {qt_compat.QT_API}")
    
    if qt_compat.QT_API != "PySide6":
        print("FAILURE: Expected PySide6, got", qt_compat.QT_API)
        sys.exit(1)
        
    # Verify imports work
    from qt_compat import QApplication, QLabel
    app = QApplication(sys.argv)
    label = QLabel("PySide6 Test")
    print("SUCCESS: PySide6 initialized and widget created")
    
except ImportError as e:
    print(f"FAILURE: ImportError: {e}")
    sys.exit(1)
except Exception as e:
    print(f"FAILURE: Unexpected error: {e}")
    sys.exit(1)
