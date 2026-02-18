import sys
import os
import pygame

# Set GameQt as the Qt API
os.environ["QT_API"] = "GameQt"

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from pdf_visual_editor.gameqt.application import QApplication
from pdf_visual_editor.gui.about_dialog import AboutDialog

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # AboutDialog requires a parent sometimes for theme, 
    # but let's try standalone first common usage
    dlg = AboutDialog()
    
    # Debugging: Check sizes after show/layout
    dlg.show()
    from pdf_visual_editor.gameqt.widgets import QLabel, QTextEdit
    
    # In AboutDialog:
    # Tab 1: QScrollArea -> QLabel
    # Tab 2: QTextEdit
    # Tab 3: QTextEdit
    
    # tabs = dlg.findChild(pygame.Rect, "") # It's a QVBoxLayout with QTabWidget
    # We can just iterate through dlg._children or similar
    
    for child in dlg._children:
        if child.__class__.__name__ == 'QTabWidget':
            print(f"-- Verification Start (Initial Index: {child._current_index}) --")
            for i in range(len(child._tabs)):
                child.setCurrentIndex(i)
                tab = child._tabs[i]
                w = tab['widget']
                print(f"Index {i} ({tab['label']}) widget: {w.__class__.__name__}")
                
                # For QTextEdit, we need to trigger layout
                if w.__class__.__name__ == 'QTextEdit':
                    w._layout_text()
                    print(f"  TextEdit content height: {w._last_content_h if hasattr(w, '_last_content_h') else 'N/A'}")
                elif w.__class__.__name__ == 'QScrollArea' and w._scroll_widget:
                    print(f"  Scroll content height: {w._get_content_height()}")
            print("-- Verification End --")

    # If it's still running, it means no crash.
    # We can close it automatically after a few seconds or let it be.
    # For now, let's keep exec() but maybe add a timer to close it if we wanted it fully automated.
    dlg.exec()
    
    sys.exit(0)
