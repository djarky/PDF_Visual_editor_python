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
        QMenuBar, QListWidget, QListWidgetItem, QTabWidget, QTextEdit, QUndoView,
        QScrollArea
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
    # Fall back to PySide6
    try:
        from PySide6.QtWidgets import (
            QApplication, QMainWindow, QWidget, QDialog, QVBoxLayout, QHBoxLayout,
            QSplitter, QFileDialog, QMessageBox, QLabel, QTreeWidget, QTreeWidgetItem,
            QHeaderView, QAbstractItemView, QPushButton, QMenu, QSlider,
            QStyledItemDelegate, QStyleOptionViewItem, QGraphicsView, QGraphicsScene,
            QGraphicsPixmapItem, QGraphicsRectItem, QGraphicsTextItem, QGraphicsItem,
            QMenuBar, QListWidget, QListWidgetItem, QTabWidget, QTextEdit, QUndoView,
            QScrollArea
        )
        from PySide6.QtCore import (
            Qt, QSettings, QPointF, QRectF, QSize, QBuffer, QIODevice,
            QMimeData, QModelIndex, Signal
        )
        from PySide6.QtGui import (
            QPixmap, QImage, QTransform, QPainter, QPen, QColor, QBrush,
            QMouseEvent, QKeySequence, QDrag, QIcon, QFont, QUndoCommand,
            QUndoStack, QAction
        )
        from PySide6.QtPrintSupport import QPrinter

        QT_API = "PySide6"
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
                QMenuBar, QListWidget, QListWidgetItem, QTabWidget, QTextEdit, QUndoView,
                QScrollArea
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
        
        except ImportError:
            # Fall back to PyQt5
            try:
                from PyQt5.QtWidgets import (
                    QApplication, QMainWindow, QWidget, QDialog, QVBoxLayout, QHBoxLayout,
                    QSplitter, QFileDialog, QMessageBox, QLabel, QTreeWidget, QTreeWidgetItem,
                    QHeaderView, QAbstractItemView, QPushButton, QMenu, QSlider,
                    QStyledItemDelegate, QStyleOptionViewItem, QGraphicsView, QGraphicsScene,
                    QGraphicsPixmapItem, QGraphicsRectItem, QGraphicsTextItem, QGraphicsItem,
                    QMenuBar, QListWidget, QListWidgetItem, QTabWidget, QTextEdit, QUndoView,
                    QScrollArea
                )
                from PyQt5.QtCore import (
                    Qt, QSettings, QPointF, QRectF, QSize, QBuffer, QIODevice,
                    QMimeData, QModelIndex, pyqtSignal as Signal
                )
                from PyQt5.QtGui import (
                    QPixmap, QImage, QTransform, QPainter, QPen, QColor, QBrush,
                    QMouseEvent, QKeySequence, QDrag, QIcon, QFont, QUndoCommand,
                    QUndoStack, QAction
                )
                from PyQt5.QtPrintSupport import QPrinter

                QT_API = "PyQt5"
                print(f"[Qt Compat] Using {QT_API}")

            except ImportError as e:
                # Final fall back to our custom GameQt (Pygame-based)
                try:
                    from .gameqt import (
                        QApplication, QMainWindow, QWidget, QDialog, QVBoxLayout, QHBoxLayout,
                        QSplitter, QFileDialog, QMessageBox, QLabel, QTreeWidget, QTreeWidgetItem,
                        QHeaderView, QAbstractItemView, QPushButton, QMenu, QSlider,
                        QStyledItemDelegate, QStyleOptionViewItem, QGraphicsView, QGraphicsScene,
                        QGraphicsPixmapItem, QGraphicsRectItem, QGraphicsTextItem, QGraphicsItem,
                        QMenuBar, QListWidget, QListWidgetItem, QTabWidget, QTextEdit, QUndoView,
                        QScrollArea, Qt, QSettings, QPointF, QRectF, QSize, QBuffer, QIODevice,
                        QMimeData, QModelIndex, Signal, QPixmap, QImage, QTransform, QPainter,
                        QPen, QColor, QBrush, QMouseEvent, QKeySequence, QDrag, QIcon, QFont,
                        QUndoCommand, QUndoStack, QAction, QPrinter
                    )
                    QT_API = "GameQt"
                    print(f"[Qt Compat] Using {QT_API} (Pygame Fallback)")
                except ImportError:
                    raise ImportError(
                        "Neither PyQt6, PySide6, PyQt5, PySide2, nor GameQt could be imported. "
                        "Please install one of them:\n"
                        "  pip install PyQt6\n"
                        "  pip install PySide6\n"
                        "  pip install PyQt5\n"
                        "  pip install PySide2\n"
                        "  pip install pygame (for GameQt fallback)"
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
    'QScrollArea',
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
