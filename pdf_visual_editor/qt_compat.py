"""
Qt Compatibility Layer
Provides compatibility between PyQt6 and PySide2.
Tries PyQt6 first, falls back to PySide2 if unavailable.
"""

QT_API = None

# Python < 3.8 compatibility for importlib.metadata
# This must be done BEFORE importing libraries that rely on it (like pdfminer)
import sys
if sys.version_info < (3, 8):
    try:
        import importlib_metadata
        import importlib
        # Inject into sys.modules so 'from importlib.metadata import ...' works
        sys.modules['importlib.metadata'] = importlib_metadata
        importlib.metadata = importlib_metadata
    except ImportError:
        pass

# Fix for 'DLL load failed' with cryptography on older Windows/Python versions
# pdfminer.six imports cryptography, but we can mock it if it's broken.
try:
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
except (ImportError, OSError):
    # OSError catches 'DLL load failed'
    print("[Qt Compat] Warning: Cryptography module is broken or missing. Mocking it to allow startup.")
    
    class MockCrypto:
        def __getattr__(self, name):
            return self
        def __call__(self, *args, **kwargs):
            return self

    import sys
    import types
    
    # Create dummy modules
    crypto = types.ModuleType('cryptography')
    hazmat = types.ModuleType('cryptography.hazmat')
    backends = types.ModuleType('cryptography.hazmat.backends')
    primitives = types.ModuleType('cryptography.hazmat.primitives')
    ciphers = types.ModuleType('cryptography.hazmat.primitives.ciphers')
    
    # Populate backends module
    backends.default_backend = MockCrypto()
    
    # Populate ciphers module
    ciphers.Cipher = MockCrypto()
    ciphers.algorithms = MockCrypto()
    ciphers.modes = MockCrypto()
    
    # Inject into sys.modules
    sys.modules['cryptography'] = crypto
    sys.modules['cryptography.hazmat'] = hazmat
    sys.modules['cryptography.hazmat.backends'] = backends
    sys.modules['cryptography.hazmat.primitives'] = primitives
    sys.modules['cryptography.hazmat.primitives.ciphers'] = ciphers

# Try PyQt6 first
try:
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QDialog, QVBoxLayout, QHBoxLayout,
        QSplitter, QFileDialog, QMessageBox, QLabel, QTreeWidget, QTreeWidgetItem,
        QHeaderView, QAbstractItemView, QPushButton, QMenu, QSlider,
        QStyledItemDelegate, QStyleOptionViewItem, QGraphicsView, QGraphicsScene,
        QGraphicsPixmapItem, QGraphicsRectItem, QGraphicsTextItem, QGraphicsItem,
        QMenuBar, QListWidget, QListWidgetItem, QTabWidget, QTextEdit, QUndoView
    )
    from PyQt6.QtCore import (
        Qt, QSettings, QPointF, QRectF, QSize, QBuffer, QIODevice,
        QMimeData, QModelIndex, pyqtSignal as Signal
    )
    from PyQt6.QtGui import (
        QPixmap, QImage, QTransform, QPainter, QPen, QColor, QBrush,
        QMouseEvent, QKeySequence, QDrag, QIcon, QFont, QUndoCommand,
        QUndoStack, QAction
    )
    from PyQt6.QtPrintSupport import QPrinter
    
    QT_API = "PyQt6"
    print(f"[Qt Compat] Using {QT_API}")

except ImportError:
    # Fall back to PySide2
    try:
        from PySide2.QtWidgets import (
            QApplication, QMainWindow, QWidget, QDialog, QVBoxLayout, QHBoxLayout,
            QSplitter, QFileDialog, QMessageBox, QLabel, QTreeWidget, QTreeWidgetItem,
            QHeaderView, QAbstractItemView, QPushButton, QMenu, QSlider,
            QStyledItemDelegate, QStyleOptionViewItem, QGraphicsView, QGraphicsScene,
            QGraphicsPixmapItem, QGraphicsRectItem, QGraphicsTextItem, QGraphicsItem,
            QMenuBar, QListWidget, QListWidgetItem, QTabWidget, QTextEdit, QUndoView
        )
        from PySide2.QtCore import (
            Qt, QSettings, QPointF, QRectF, QSize, QBuffer, QIODevice,
            QMimeData, QModelIndex, Signal
        )
        from PySide2.QtGui import (
            QPixmap, QImage, QTransform, QPainter, QPen, QColor, QBrush,
            QMouseEvent, QKeySequence, QDrag, QIcon, QFont
        )
        from PySide2.QtWidgets import QUndoCommand, QUndoStack
        from PySide2.QtWidgets import QAction
        from PySide2.QtPrintSupport import QPrinter
        
        QT_API = "PySide2"
        print(f"[Qt Compat] Using {QT_API}")
    
    except ImportError as e:
        raise ImportError(
            "Neither PyQt6 nor PySide2 could be imported. "
            "Please install one of them:\n"
            "  pip install PyQt6  (for Python 3.9+)\n"
            "  pip install PySide2 (for older systems)"
        ) from e

# Export all
__all__ = [
    'QT_API',
    # QtWidgets
    'QApplication', 'QMainWindow', 'QWidget', 'QDialog', 'QVBoxLayout', 'QHBoxLayout',
    'QSplitter', 'QFileDialog', 'QMessageBox', 'QLabel', 'QTreeWidget', 'QTreeWidgetItem',
    'QHeaderView', 'QAbstractItemView', 'QPushButton', 'QMenu', 'QSlider',
    'QStyledItemDelegate', 'QStyleOptionViewItem', 'QGraphicsView', 'QGraphicsScene',
    'QGraphicsPixmapItem', 'QGraphicsRectItem', 'QGraphicsTextItem', 'QGraphicsItem',
    'QMenuBar', 'QListWidget', 'QListWidgetItem', 'QTabWidget', 'QTextEdit', 'QUndoView',
    # QtCore
    'Qt', 'QSettings', 'QPointF', 'QRectF', 'QSize', 'QBuffer', 'QIODevice',
    'QMimeData', 'QModelIndex', 'Signal',
    # QtGui
    'QPixmap', 'QImage', 'QTransform', 'QPainter', 'QPen', 'QColor', 'QBrush',
    'QMouseEvent', 'QKeySequence', 'QDrag', 'QIcon', 'QFont', 'QUndoCommand',
    'QUndoStack', 'QAction',
    # QtPrintSupport
    'QPrinter',
]
