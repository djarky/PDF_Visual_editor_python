"""
Test suite for Drag & Drop functionality.
Tests file drop events and drag enter/drop event handling.
"""
import sys
import os
import pygame

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from gameqt.application import QApplication, QDragEnterEvent, QDropEvent
from gameqt.core import QMimeData, QUrl
from gameqt.widgets import QMainWindow, QWidget, QLabel
from gameqt.layouts import QVBoxLayout
from gameqt.gui import QColor

class DropZoneWidget(QWidget):
    """A widget that accepts file drops"""
    def __init__(self):
        super().__init__()
        self.dropped_files = []
        self.setAcceptDrops(True)
        self._bg_color = (240, 240, 245)
    
    def dragEnterEvent(self, event):
        """Called when a drag enters the widget"""
        if event.mimeData().hasUrls():
            event.accept()
            self._bg_color = (200, 255, 200)  # Green tint
            print("[DragEnter] File drag detected")
        else:
            event.ignore()
    
    def dropEvent(self, event):
        """Called when files are dropped"""
        mime = event.mimeData()
        if mime.hasUrls():
            self.dropped_files = []
            for url in mime.urls():
                file_path = url.toLocalFile()
                self.dropped_files.append(file_path)
                print(f"[Drop] File dropped: {file_path}")
            
            event.accept()
            self._bg_color = (200, 200, 255)  # Blue tint
        else:
            event.ignore()
    
    def _draw(self, pos):
        if not QApplication._instance or not QApplication._instance._windows: return
        screen = QApplication._instance._windows[0]._screen
        
        # Draw background
        pygame.draw.rect(screen, self._bg_color, (pos.x, pos.y, self._rect.width, self._rect.height))
        pygame.draw.rect(screen, (100, 100, 120), (pos.x, pos.y, self._rect.width, self._rect.height), 2)
        
        # Draw text
        font = pygame.font.SysFont("Arial", 16, bold=True)
        txt = font.render("Drop Zone", True, (80, 80, 90))
        screen.blit(txt, (pos.x + 10, pos.y + 10))
        
        # Draw instructions
        font_small = pygame.font.SysFont("Arial", 12)
        instructions = [
            "Drag files from your file manager",
            "and drop them here to test",
            "",
            "Dropped files:"
        ]
        
        y_offset = 40
        for line in instructions:
            txt = font_small.render(line, True, (60, 60, 70))
            screen.blit(txt, (pos.x + 10, pos.y + y_offset))
            y_offset += 18
        
        # Show dropped files
        for i, file_path in enumerate(self.dropped_files[-5:]):  # Show last 5
            file_name = os.path.basename(file_path)
            txt = font_small.render(f"• {file_name}", True, (0, 100, 0))
            screen.blit(txt, (pos.x + 20, pos.y + y_offset))
            y_offset += 16

class DragDropTestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Drag & Drop Test - GameQt")
        self.resize(500, 400)
        self.setAcceptDrops(True)  # Enable drops on main window
        
        central = QWidget()
        layout = QVBoxLayout(central)
        
        # Title
        title = QLabel()
        title.setText("Drag & Drop Test Suite")
        layout.addWidget(title)
        
        # Instructions
        info = QLabel()
        info.setText("Drag files from your file manager into the drop zone below.")
        layout.addWidget(info)
        
        # Drop zone
        self.drop_zone = DropZoneWidget()
        self.drop_zone._rect.height = 250
        layout.addWidget(self.drop_zone)
        
        # Status
        self.status = QLabel()
        self.status.setText("Ready - Waiting for file drops...")
        layout.addWidget(self.status)
        
        self.setCentralWidget(central)
        central.show()
    
    def dropEvent(self, event):
        """Handle drops on the main window"""
        mime = event.mimeData()
        if mime.hasUrls():
            files = [url.toLocalFile() for url in mime.urls()]
            self.status.setText(f"Dropped {len(files)} file(s) on window")
            event.accept()
            print(f"[MainWindow] Received {len(files)} files")

def test_mimedata_urls():
    """Test QMimeData URL handling"""
    print("\n=== Testing QMimeData URLs ===")
    
    mime = QMimeData()
    urls = [
        QUrl("file:///home/user/document.pdf"),
        QUrl("file:///home/user/image.png")
    ]
    
    mime.setUrls(urls)
    assert mime.hasUrls(), "hasUrls should return True"
    assert len(mime.urls()) == 2, "Should have 2 URLs"
    
    # Test URL conversion
    local_path = mime.urls()[0].toLocalFile()
    assert local_path == "/home/user/document.pdf"
    print(f"✓ URL conversion: {local_path}")
    
    print("=== QMimeData URL Tests Passed ===\n")

def test_drag_events():
    """Test drag event creation and properties"""
    print("\n=== Testing Drag Events ===")
    
    # Create mime data
    mime = QMimeData()
    mime.setUrls([QUrl("file:///test.txt")])
    
    # Test QDragEnterEvent
    drag_enter = QDragEnterEvent((100, 100), mime)
    assert drag_enter.pos() == (100, 100)
    assert drag_enter.mimeData() == mime
    assert not drag_enter.isAccepted(), "Should not be accepted by default"
    
    drag_enter.accept()
    assert drag_enter.isAccepted(), "Should be accepted after accept()"
    print("✓ QDragEnterEvent")
    
    # Test QDropEvent
    drop = QDropEvent((200, 200), mime)
    assert drop.pos() == (200, 200)
    assert drop.position() == (200, 200)  # Compatibility
    assert drop.mimeData() == mime
    
    drop.accept()
    assert drop.isAccepted()
    print("✓ QDropEvent")
    
    print("=== Drag Event Tests Passed ===\n")

def test_widget_drop_acceptance():
    """Test widget setAcceptDrops and acceptDrops"""
    print("\n=== Testing Widget Drop Acceptance ===")
    
    widget = QWidget()
    assert not widget.acceptDrops(), "Should not accept drops by default"
    
    widget.setAcceptDrops(True)
    assert widget.acceptDrops(), "Should accept drops after setAcceptDrops(True)"
    
    widget.setAcceptDrops(False)
    assert not widget.acceptDrops(), "Should not accept drops after setAcceptDrops(False)"
    
    print("✓ Widget drop acceptance")
    print("=== Widget Drop Tests Passed ===\n")

def run_interactive_test():
    """Run interactive drag & drop test with GUI"""
    print("\n=== Starting Interactive Drag & Drop Test ===")
    print("Instructions:")
    print("1. Open your file manager")
    print("2. Drag one or more files")
    print("3. Drop them onto the 'Drop Zone' in the window")
    print("4. The dropped file names will appear in the list")
    print("\nNote: Make sure SDL2 is configured to accept file drops")
    print("Press Ctrl+C or close window to exit\n")
    
    app = QApplication(sys.argv)
    win = DragDropTestWindow()
    win.show()
    return app.exec()

if __name__ == "__main__":
    # Run unit tests first
    test_mimedata_urls()
    test_drag_events()
    test_widget_drop_acceptance()
    
    print("\n" + "="*50)
    print("All unit tests passed!")
    print("="*50)
    
    # Run interactive test
    sys.exit(run_interactive_test())
