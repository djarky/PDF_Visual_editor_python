"""
Test suite for QClipboard and QMimeData functionality.
Tests system clipboard integration using pygame.scrap.
"""
import sys
import os
import pygame

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from gameqt.application import QApplication
from gameqt.core import QClipboard, QMimeData, QUrl
from gameqt.widgets import QMainWindow, QWidget, QLabel, QPushButton, QTextEdit
from gameqt.layouts import QVBoxLayout, QHBoxLayout

class ClipboardTestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Clipboard Test - GameQt")
        self.resize(600, 400)
        
        central = QWidget()
        layout = QVBoxLayout(central)
        
        # Instructions
        title = QLabel()
        title.setText("Clipboard Test Suite")
        layout.addWidget(title)
        
        info = QLabel()
        info.setText("Test copying and pasting text between this app and external applications.")
        layout.addWidget(info)
        
        # Text input area
        self.text_edit = QTextEdit()
        self.text_edit.setPlainText("Type some text here, then click 'Copy to Clipboard'")
        layout.addWidget(self.text_edit)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        copy_btn = QPushButton("Copy to Clipboard")
        copy_btn.clicked.connect(self.copy_text)
        btn_layout.addWidget(copy_btn)
        
        paste_btn = QPushButton("Paste from Clipboard")
        paste_btn.clicked.connect(self.paste_text)
        btn_layout.addWidget(paste_btn)
        
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.clear_text)
        btn_layout.addWidget(clear_btn)
        
        layout.addLayout(btn_layout)
        
        # Status label
        self.status = QLabel()
        self.status.setText("Ready")
        layout.addWidget(self.status)
        
        self.setCentralWidget(central)
        central.show()
    
    def copy_text(self):
        text = self.text_edit.toPlainText()
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        self.status.setText(f"Copied {len(text)} characters to clipboard")
        print(f"[Clipboard Test] Copied: {text[:50]}...")
    
    def paste_text(self):
        clipboard = QApplication.clipboard()
        text = clipboard.text()
        self.text_edit.setPlainText(text)
        self.status.setText(f"Pasted {len(text)} characters from clipboard")
        print(f"[Clipboard Test] Pasted: {text[:50]}...")
    
    def clear_text(self):
        self.text_edit.setPlainText("")
        self.status.setText("Cleared")

def test_clipboard_basic():
    """Test basic clipboard text operations"""
    print("\n=== Testing QClipboard Basic Operations ===")
    
    clipboard = QClipboard()
    
    # Test setText and text
    test_text = "Hello, Clipboard!"
    clipboard.setText(test_text)
    retrieved = clipboard.text()
    
    assert retrieved == test_text, f"Expected '{test_text}', got '{retrieved}'"
    print(f"✓ setText/text: '{test_text}'")
    
    # Test with empty string
    clipboard.setText("")
    assert clipboard.text() == "", "Empty string test failed"
    print("✓ Empty string handling")
    
    print("=== QClipboard Basic Tests Passed ===\n")

def test_mimedata():
    """Test QMimeData functionality"""
    print("\n=== Testing QMimeData ===")
    
    mime = QMimeData()
    
    # Test text
    mime.setText("Test text")
    assert mime.hasText(), "hasText should return True"
    assert mime.text() == "Test text", "text() should return set text"
    print("✓ Text data")
    
    # Test URLs
    urls = [QUrl("file:///home/test.pdf"), QUrl("file:///home/image.png")]
    mime.setUrls(urls)
    assert mime.hasUrls(), "hasUrls should return True"
    assert len(mime.urls()) == 2, "Should have 2 URLs"
    print("✓ URL data")
    
    # Test custom data
    mime.setData("application/custom", b"custom data")
    assert mime.data("application/custom") == b"custom data"
    print("✓ Custom data")
    
    print("=== QMimeData Tests Passed ===\n")

def test_qurl():
    """Test QUrl functionality"""
    print("\n=== Testing QUrl ===")
    
    # Test file URL
    url = QUrl("file:///home/user/document.pdf")
    local_path = url.toLocalFile()
    assert local_path == "/home/user/document.pdf", f"Expected '/home/user/document.pdf', got '{local_path}'"
    print(f"✓ File URL conversion: {local_path}")
    
    # Test regular path
    url2 = QUrl("/home/user/file.txt")
    assert url2.toLocalFile() == "/home/user/file.txt"
    print("✓ Regular path handling")
    
    print("=== QUrl Tests Passed ===\n")

def run_interactive_test():
    """Run interactive clipboard test with GUI"""
    print("\n=== Starting Interactive Clipboard Test ===")
    print("Instructions:")
    print("1. Type text in the text area")
    print("2. Click 'Copy to Clipboard'")
    print("3. Open another application (e.g., text editor)")
    print("4. Paste (Ctrl+V) to verify clipboard works")
    print("5. Copy text from another application")
    print("6. Click 'Paste from Clipboard' to verify")
    print("\nPress Ctrl+C or close window to exit\n")
    
    app = QApplication(sys.argv)
    win = ClipboardTestWindow()
    win.show()
    return app.exec()

if __name__ == "__main__":
    # Run unit tests first
    test_clipboard_basic()
    test_mimedata()
    test_qurl()
    
    print("\n" + "="*50)
    print("All unit tests passed!")
    print("="*50)
    
    # Run interactive test
    sys.exit(run_interactive_test())
