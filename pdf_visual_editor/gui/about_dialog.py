"""
About dialog for PDF Visual Editor.
Displays help, keyboard shortcuts, and developer information.
"""
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QLabel, QTextEdit, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QFont
import os


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
        logo_path = os.path.join(os.path.dirname(__file__), os.path.pardir, "resources", logo_filename)
        if os.path.exists(logo_path):
            # Use absolute path for QLabel to load image properly
            logo_path = os.path.abspath(logo_path).replace("\\", "/")
            logo_html = f'<img src="file:///{logo_path}" width="200"><br><br>'
        
        about_text = f"""
        {logo_html}
        <h1>PDF Visual Editor</h1>
        <p style="font-size: 14pt;"><b>Version 1.0</b></p>
        <br>
        <p>A powerful visual editor for PDF documents</p>
        <p>with advanced editing capabilities</p>
        <br><br>
        <p><b>Developer:</b> ARKY750</p>
        <p><b>GitHub:</b> <a href="https://djarky.github.io">djarky.github.io</a></p>
        <br>
        <p style="font-size: 10pt; color: gray;">
        Built with PyQt6, pikepdf, and PyMuPDF<br>
        © 2024 ARKY750. All rights reserved.
        </p>
        """
        
        widget.setText(about_text)
        widget.setTextFormat(Qt.TextFormat.RichText)
        widget.setOpenExternalLinks(True)
        
        return widget
    
    def create_help_tab(self):
        """Create the Help & Commands tab."""
        widget = QTextEdit()
        widget.setReadOnly(True)
        
        help_text = """
<h2>PDF Visual Editor - Help & Commands</h2>

<h3>File Operations</h3>
<ul>
<li><b>Open PDF</b> - File → Open PDF (or drag & drop a PDF file)</li>
<li><b>Save</b> - File → Save (Ctrl+S) - Save changes to current PDF</li>
<li><b>Save As</b> - File → Save As (Ctrl+Shift+S) - Save to a new file</li>
<li><b>Export PDF</b> - File → Export PDF - Export with modifications</li>
</ul>

<h3>Editing Operations</h3>
<ul>
<li><b>Insert Text</b> - Insert → Insert Text - Add new text element</li>
<li><b>Insert Image</b> - Insert → Insert Image - Add image from file</li>
<li><b>Edit Text</b> - Double-click on any text element to edit in place</li>
<li><b>Move Elements</b> - Click and drag to move selected items</li>
<li><b>Resize Elements</b> - Drag the blue resize handles on corners</li>
<li><b>Delete Elements</b> - Select and press Delete key</li>
<li><b>Rotate Elements</b> - Select and press Ctrl+R to rotate 90°</li>
</ul>

<h3>Selection & Clipboard</h3>
<ul>
<li><b>Copy</b> - Edit → Copy (Ctrl+C) - Copy selected elements</li>
<li><b>Paste</b> - Edit → Paste (Ctrl+V) - Paste from clipboard</li>
<li><b>Capture Area</b> - Edit → Capture Area (Ctrl+Shift+C) - Draw rectangle to capture region</li>
</ul>

<h3>Undo & Redo</h3>
<ul>
<li><b>Undo</b> - Edit → Undo (Ctrl+Z) - Undo last action</li>
<li><b>Redo</b> - Edit → Redo (Ctrl+Y) - Redo previously undone action</li>
</ul>

<h3>View Controls</h3>
<ul>
<li><b>Zoom In</b> - Hold Ctrl and scroll mouse wheel up</li>
<li><b>Zoom Out</b> - Hold Ctrl and scroll mouse wheel down</li>
<li><b>Theme</b> - View → Theme → Light/Dark - Switch between themes</li>
</ul>

<h3>Inspector Panel</h3>
<ul>
<li><b>Visibility</b> - Check/uncheck to show/hide elements</li>
<li><b>Opacity</b> - Click opacity value to reveal slider (0-100%)</li>
<li><b>Organize</b> - Create folders to group elements (Right-click → Create Folder)</li>
<li><b>Drag & Drop</b> - Reorder elements by dragging in the tree</li>
<li><b>Show/Hide All</b> - Buttons to toggle visibility of all elements</li>
</ul>

<h3>Thumbnail Panel</h3>
<ul>
<li><b>Navigate Pages</b> - Click on any thumbnail to jump to that page</li>
<li><b>Page Order</b> - Drag thumbnails to reorder pages in exported PDF</li>
</ul>

<h3>Canvas Interactions</h3>
<ul>
<li><b>Right-Click Menu</b> - Right-click on canvas for quick actions</li>
<li><b>Multi-Select</b> - Hold Ctrl and click to select multiple items</li>
<li><b>Rubber Band Select</b> - Click and drag on empty area to select multiple items</li>
<li><b>Alt+Drag</b> - Drag selection with Alt key to export to other applications</li>
</ul>

<h3>Tips & Tricks</h3>
<ul>
<li>Images larger than 500px are automatically scaled down on insert</li>
<li>Text editing supports standard text cursor navigation and selection</li>
<li>Scene caching limits memory usage (max 5 pages cached)</li>
<li>All PDF features are preserved when using Save (not Export)</li>
<li>Dark theme preference persists across sessions</li>
</ul>
        """
        
        widget.setHtml(help_text)
        return widget
    
    def create_shortcuts_tab(self):
        """Create the Keyboard Shortcuts tab."""
        widget = QTextEdit()
        widget.setReadOnly(True)
        
        shortcuts_text = """
<h2>Keyboard Shortcuts Reference</h2>

<h3>File Menu</h3>
<table border="1" cellpadding="5" cellspacing="0" width="100%">
<tr><th>Action</th><th>Shortcut</th></tr>
<tr><td>Open PDF</td><td>Ctrl+O</td></tr>
<tr><td>Save</td><td>Ctrl+S</td></tr>
<tr><td>Save As</td><td>Ctrl+Shift+S</td></tr>
<tr><td>Exit</td><td>Alt+F4</td></tr>
</table>

<h3>Edit Menu</h3>
<table border="1" cellpadding="5" cellspacing="0" width="100%">
<tr><th>Action</th><th>Shortcut</th></tr>
<tr><td>Undo</td><td>Ctrl+Z</td></tr>
<tr><td>Redo</td><td>Ctrl+Y</td></tr>
<tr><td>Copy</td><td>Ctrl+C</td></tr>
<tr><td>Paste</td><td>Ctrl+V</td></tr>
<tr><td>Delete</td><td>Delete</td></tr>
<tr><td>Capture Area</td><td>Ctrl+Shift+C</td></tr>
</table>

<h3>Canvas Operations</h3>
<table border="1" cellpadding="5" cellspacing="0" width="100%">
<tr><th>Action</th><th>Shortcut</th></tr>
<tr><td>Rotate 90°</td><td>Ctrl+R</td></tr>
<tr><td>Zoom In</td><td>Ctrl+Mouse Wheel Up</td></tr>
<tr><td>Zoom Out</td><td>Ctrl+Mouse Wheel Down</td></tr>
<tr><td>Multi-Select</td><td>Ctrl+Click</td></tr>
<tr><td>Export Drag</td><td>Alt+Drag</td></tr>
</table>

<h3>Text Editing</h3>
<table border="1" cellpadding="5" cellspacing="0" width="100%">
<tr><th>Action</th><th>Method</th></tr>
<tr><td>Enter Edit Mode</td><td>Double-Click on text</td></tr>
<tr><td>Exit Edit Mode</td><td>Click outside or press Esc</td></tr>
<tr><td>Select All</td><td>Ctrl+A (while editing)</td></tr>
</table>

<h3>Quick Tips</h3>
<ul>
<li>Hold <b>Ctrl</b> while scrolling to zoom in/out</li>
<li>Hold <b>Alt</b> while dragging to export content</li>
<li>Press <b>Delete</b> to remove selected elements</li>
<li><b>Double-click</b> text to edit inline</li>
<li><b>Right-click</b> anywhere for context menu</li>
</ul>
        """
        
        widget.setHtml(shortcuts_text)
        return widget
