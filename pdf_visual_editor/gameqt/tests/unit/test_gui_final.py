import sys
import os

# Ensure gameqt is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from gameqt.gui import QTextCursor, QKeySequence
from gameqt.item_views import QHeaderView

def test_qtextcursor():
    print("Testing QTextCursor...")
    cursor = QTextCursor()
    assert cursor.position() == 0
    assert cursor.anchor() == 0
    assert not cursor.hasSelection()
    
    cursor.setPosition(10)
    assert cursor.position() == 10
    assert cursor.anchor() == 10
    
    cursor.setPosition(20, 1) # KeepAnchor (mode=1)
    assert cursor.position() == 20
    assert cursor.anchor() == 10
    assert cursor.hasSelection()
    
    cursor.clearSelection()
    assert cursor.position() == 20
    assert cursor.anchor() == 20
    assert not cursor.hasSelection()
    print("✓ QTextCursor passed")

def test_qkeysequence_matching():
    print("Testing QKeySequence matches_static...")
    seq = QKeySequence("Ctrl+C")
    assert QKeySequence.matches_static(seq, "Ctrl+C")
    assert QKeySequence.matches_static("CTRL+C", seq)
    assert not QKeySequence.matches_static(seq, "Ctrl+V")
    print("✓ QKeySequence matching passed")

def test_qheaderview_sizing():
    print("Testing QHeaderView sectionSize...")
    header = QHeaderView()
    header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    
    # 800 width, 4 columns -> 200 each
    size = header.sectionSize(0, 800, 4)
    assert size == 200
    
    header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
    size = header.sectionSize(0, 400, 2)
    assert size == 200
    print("✓ QHeaderView sizing passed")

if __name__ == "__main__":
    try:
        test_qtextcursor()
        test_qkeysequence_matching()
        test_qheaderview_sizing()
        print("\nAll Final GUI tests passed!")
    except Exception as e:
        print(f"Test failed: {e}")
        sys.exit(1)
