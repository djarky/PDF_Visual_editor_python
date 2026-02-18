import sys
import os
import pygame

# Ensure gameqt is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from gameqt.application import QApplication
from gameqt.widgets import QMainWindow, QStatusBar, QLabel
from gameqt.item_views import QTreeWidget, QTreeWidgetItem

def test_statusbar_logic():
    print("Testing QStatusBar logic...")
    app = QApplication(sys.argv)
    win = QMainWindow()
    sb = win.statusBar()
    assert isinstance(sb, QStatusBar)
    
    sb.showMessage("Hello Status")
    assert sb._message_label.text() == "Hello Status"
    
    lbl = QLabel("Extra")
    sb.addWidget(lbl)
    assert lbl in sb._children
    print("✓ QStatusBar passed")

def test_treewidget_enhancements():
    print("Testing QTreeWidget expand/collapse...")
    tree = QTreeWidget()
    root = QTreeWidgetItem(tree, ["Root"])
    child = QTreeWidgetItem(root, ["Child"])
    
    tree.collapseAll()
    assert not root.isExpanded()
    assert not child.isExpanded()
    
    tree.expandAll()
    assert root.isExpanded()
    assert child.isExpanded()
    print("✓ QTreeWidget enhancements passed")

if __name__ == "__main__":
    pygame.init()
    try:
        test_statusbar_logic()
        test_treewidget_enhancements()
        print("\nAll Widget Enhancement tests passed!")
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
