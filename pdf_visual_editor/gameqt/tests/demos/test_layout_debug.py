import sys
import os
import pygame

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from pdf_visual_editor.gameqt.application import QApplication
from pdf_visual_editor.gameqt.widgets import QDialog, QTabWidget, QPushButton, QLabel, QScrollArea
from pdf_visual_editor.gameqt.layouts import QVBoxLayout
from pdf_visual_editor.gameqt.core import Qt

def test_layout_logic():
    app = QApplication(sys.argv)
    
    dlg = QDialog()
    dlg.setMinimumSize(600, 500)
    
    layout = QVBoxLayout(dlg)
    
    tabs = QTabWidget()
    label = QLabel("Internal Label Content")
    label.setWordWrap(True)
    
    scroll = QScrollArea()
    scroll.setWidget(label)
    
    tabs.addTab(scroll, "Tab 1")
    
    layout.addWidget(tabs)
    
    btn = QPushButton("Close")
    layout.addWidget(btn)
    
    # Must show dialog so children become visible for layout
    dlg.show()
    
    # Trigger layout
    print(f"Dialog initial rect: {dlg._rect}")
    
    # Simulating QDialog.exec arrange logic
    w, h = 600, 500
    content_rect = pygame.Rect(0, 30, w, h - 30)
    layout.arrange(content_rect)
    
    # Now trigger recursive drawing logic (which also does deeper sizing in QTabWidget/QScrollArea)
    dlg._draw_recursive(pygame.Vector2(0, 0))
    
    print(f"Tabs rect after layout: {tabs._rect}")
    print(f"ScrollArea rect after layout: {scroll._rect}")
    print(f"Label rect after layout: {label._rect}")
    print(f"Button rect after layout: {btn._rect}")
    
    if tabs._rect.height <= 50:
        print("CRITICAL: QTabWidget is too small!")
    elif scroll._rect.height < 395:
        print(f"CRITICAL: ScrollArea failed to fill tabs! Height={scroll._rect.height}")
    elif label._rect.width < 500:
        print(f"CRITICAL: Label failed to fill ScrollArea! Width={label._rect.width}")
    else:
        print("SUCCESS: Recursive layout sizing verified.")

    # Cleanup
    app.quit()

if __name__ == "__main__":
    test_layout_logic()
