import sys
import os
import random

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from pdf_visual_editor.gameqt.application import QApplication
from pdf_visual_editor.gameqt.widgets.qwidget import QWidget
from pdf_visual_editor.gameqt.widgets.qlabel import QLabel
from pdf_visual_editor.gameqt.widgets.qpushbutton import QPushButton
from pdf_visual_editor.gameqt.widgets.qscrollarea import QScrollArea
from pdf_visual_editor.gameqt.layouts.box_layout import QVBoxLayout, QHBoxLayout
from pdf_visual_editor.gameqt.gui import QFont, QFontDatabase, QColor

EMOJI_POOL = [
    "🚀", "🌟", "✨", "🔥", "🌈", "🍎", "🍕", "🍔", "🍦", "🎨", 
    "🎸", "🎮", "🕹️", "📱", "💻", "⚡", "❤️", "💎", "👑", "🦄",
    "✅", "❌", "⚠️", "🛑", "🔔", "📢", "💬", "💭", "📁", "📂"
]

def random_emojis(count=5):
    return "".join(random.choices(EMOJI_POOL, k=count))

class StressTestWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Emoji Stress Test 🚀✨🌈")
        self.resize(800, 600)
        
        # Register a custom font to test integration
        font_path = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
        if not os.path.exists(font_path):
            font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        
        self.custom_family = QFontDatabase.addApplicationFont(font_path)
        
        main_layout = QVBoxLayout(self)
        
        scroll = QScrollArea()
        content = QWidget()
        content_layout = QVBoxLayout(content)
        
        # 1. Header with big emojis
        header = QLabel(f"Extreme Emoji Stress Test {random_emojis(10)}")
        header.setFont(QFont(self.custom_family, 24))
        header.setStyleSheet("color: #ffcc00; background-color: #333; border-radius: 10px; border: 2px solid #555")
        content_layout.addWidget(header)
        
        # 2. Add 20 rows of mixed elements
        for i in range(20):
            row_layout = QHBoxLayout()
            
            # Label with random style and emojis
            lbl = QLabel(f"Elt {i}: {random_emojis(3)} Mixed Text {random_emojis(3)}")
            size = random.randint(12, 22)
            lbl.setFont(QFont(self.custom_family, size))
            content_layout.addWidget(lbl)
            
            # Button with emojis
            btn = QPushButton(f"Action {i} {random_emojis(2)}")
            btn.setFont(QFont(self.custom_family, 14))
            content_layout.addWidget(btn)
            
            # Multi-line label
            multi = QLabel(f"Line 1: {random_emojis(5)}\nLine 2: {random_emojis(5)}\nLine 3: {random_emojis(5)}")
            multi.setWordWrap(True)
            multi.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc; margin: 5px")
            content_layout.addWidget(multi)
            
        scroll.setWidget(content)
        main_layout.addWidget(scroll)

def main():
    app = QApplication(sys.argv)
    window = StressTestWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
