"""
About dialog for PDF Visual Editor.
Displays help, keyboard shortcuts, and developer information.
"""
from qt_compat import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QLabel, 
                       QTextEdit, QPushButton, Qt, QPixmap, QFont)
from __version__ import __version__
import os
import sys


class AboutDialog(QDialog):
    """About dialog with help and developer information."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About PDF Visual Editor")
        self.setMinimumSize(600, 500)
        
        layout = QVBoxLayout(self)
        
        # Create tab widget
        tabs = QTabWidget()
        
        # Tab 1: About
        about_widget = self.create_about_tab()
        tabs.addTab(about_widget, "About")
        
        # Tab 2: Help & Commands
        help_widget = self.create_help_tab()
        tabs.addTab(help_widget, "Help & Commands")
        
        # Tab 3: Keyboard Shortcuts
        shortcuts_widget = self.create_shortcuts_tab()
        tabs.addTab(shortcuts_widget, "Keyboard Shortcuts")
        
        layout.addWidget(tabs)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignRight)
    
    def load_html_resource(self, filename):
        """Load HTML content from resources directory."""
        try:
            # Get the base path for resources
            if getattr(sys, 'frozen', False):
                # Running in a PyInstaller bundle
                base_path = sys._MEIPASS
            else:
                # Running in development mode
                base_path = os.path.dirname(__file__)
                base_path = os.path.join(base_path, os.path.pardir)
            
            resource_path = os.path.join(base_path, "resources", filename)
            with open(resource_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error loading resource {filename}: {e}")
            return f"Error loading {filename}"

    def create_about_tab(self):
        """Create the About tab with logo and developer info."""
        widget = QLabel()
        widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        widget.setWordWrap(True)
        
        # Determine which logo to use based on parent's theme
        logo_filename = "logo_light.png"  # Default to light
        if self.parent() and hasattr(self.parent(), 'current_theme'):
            if self.parent().current_theme == "dark":
                logo_filename = "logo_dark.png"
        
        # Try to load theme-appropriate logo
        logo_html = ""
        # Get the base path for resources
        if getattr(sys, 'frozen', False):
            # Running in a PyInstaller bundle
            base_path = sys._MEIPASS
        else:
            # Running in development mode
            base_path = os.path.join(os.path.dirname(__file__), os.path.pardir)
        
        logo_path = os.path.join(base_path, "resources", logo_filename)
        if os.path.exists(logo_path):
            # Use absolute path for QLabel to load image properly
            logo_path = os.path.abspath(logo_path).replace("\\", "/")
            logo_html = f'<img src="file:///{logo_path}" width="200"><br><br>'
        
        # Load HTML template
        html_content = self.load_html_resource("about.html")
        
        # Format with dynamic data
        about_text = html_content.format(
            logo_html=logo_html,
            version=__version__
        )
        
        widget.setText(about_text)
        widget.setTextFormat(Qt.TextFormat.RichText)
        widget.setOpenExternalLinks(True)
        
        return widget
    
    def create_help_tab(self):
        """Create the Help & Commands tab."""
        widget = QTextEdit()
        widget.setReadOnly(True)
        
        help_text = self.load_html_resource("help.html")
        widget.setHtml(help_text)
        
        return widget
    
    def create_shortcuts_tab(self):
        """Create the Keyboard Shortcuts tab."""
        widget = QTextEdit()
        widget.setReadOnly(True)
        
        shortcuts_text = self.load_html_resource("shortcuts.html")
        widget.setHtml(shortcuts_text)
        
        return widget
