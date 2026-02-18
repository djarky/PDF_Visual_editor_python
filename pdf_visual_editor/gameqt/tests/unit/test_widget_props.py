import sys
import os

# Ensure gameqt is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from gameqt.core import Qt
from gameqt.widgets import QDialog, QScrollArea, QLabel

def test_widget_properties():
    print("Testing miscellaneous widget properties...")
    
    # QDialog
    dialog = QDialog()
    dialog.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
    assert dialog._window_flags == Qt.WindowType.WindowStaysOnTopHint
    
    # QScrollArea
    area = QScrollArea()
    area.setFrameShape(QScrollArea.Shape.NoFrame)
    assert area._frame_shape == QScrollArea.Shape.NoFrame
    
    # QLabel
    label = QLabel("Test")
    label.setOpenExternalLinks(True)
    assert label._open_external_links is True
    
    print("✓ Widget properties passed")

if __name__ == "__main__":
    try:
        test_widget_properties()
        print("\nAll Widget Property tests passed!")
    except Exception as e:
        print(f"Test failed: {e}")
        sys.exit(1)
