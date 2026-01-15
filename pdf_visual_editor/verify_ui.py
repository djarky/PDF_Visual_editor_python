import sys
import os
from qt_compat import QApplication, QScrollArea
from gui.main_window import MainWindow
from gui.about_dialog import AboutDialog

def verify_ui():
    app = QApplication(sys.argv)
    
    # 1. Verify System Theme
    window = MainWindow()
    
    # Check if action exists
    if not hasattr(window.menu_bar, 'action_theme_system'):
        print("FAILURE: System theme action not found in menu")
        return False
        
    # Trigger action
    window.menu_bar.action_theme_system.trigger()
    
    if window.current_theme != "system":
        print(f"FAILURE: Theme not set to 'system', got '{window.current_theme}'")
        return False
        
    if window.styleSheet() != "":
        print("FAILURE: Stylesheet not cleared for system theme")
        return False
        
    print("SUCCESS: System theme logic verified")
    
    # 2. Verify About Dialog Scrollbar
    dialog = AboutDialog(window)
    
    # Find the tab widget
    tabs = dialog.findChild(object, name="") # QTabWidget doesn't have a default name, but it's the first child added to layout
    # Actually, let's inspect the result of create_about_tab directly or check children
    
    # We can check if the first tab is a QScrollArea
    # The tabs are added in __init__: tabs.addTab(about_widget, "About")
    # So we need to access the widget of the first tab
    
    # Accessing QTabWidget from dialog layout
    layout = dialog.layout()
    # Item 0 is the tab widget
    tab_widget = layout.itemAt(0).widget()
    
    about_tab = tab_widget.widget(0)
    
    if isinstance(about_tab, QScrollArea):
        print("SUCCESS: About tab is wrapped in QScrollArea")
    else:
        print(f"FAILURE: About tab is {type(about_tab)}, expected QScrollArea")
        return False
        
    return True

if __name__ == "__main__":
    try:
        if verify_ui():
            print("All UI verifications passed!")
            sys.exit(0)
        else:
            sys.exit(1)
    except Exception as e:
        print(f"FAILURE: Exception during verification: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
