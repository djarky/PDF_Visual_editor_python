import sys
import os

# Ensure gameqt is in path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
if os.path.join(project_root, 'pdf_visual_editor') not in sys.path:
     sys.path.insert(0, os.path.join(project_root, 'pdf_visual_editor'))

from gameqt.application import QApplication
from gameqt.widgets import QMainWindow, QWidget, QLabel, QPushButton
from gameqt.layouts import QVBoxLayout, QHBoxLayout
from gameqt.core import Qt
from gameqt.gui import QColor

class TestMissingFeatures(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GameQt Missing Features Test")
        self.resize(900, 700)
        
        central = QWidget()
        self.setCentralWidget(central)
        
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("🔧 Missing Features Implementation Test", central)
        title.setStyleSheet("font-size: 20px; font-weight: bold; background-color: #E3F2FD; padding: 10px;")
        title.show()
        main_layout.addWidget(title)
        
        # 1. Frame Shapes Test
        frame_section = QLabel("1. Frame Shapes (setFrameShape)", central)
        frame_section.setStyleSheet("font-weight: bold; font-size: 14px; margin-top: 10px;")
        frame_section.show()
        main_layout.addWidget(frame_section)
        
        frames_layout = QHBoxLayout()
        
        # NoFrame
        no_frame = QWidget(central)
        no_frame.setFrameShape(Qt.FrameShape.NoFrame)
        no_frame.resize(150, 80)
        lbl_no_frame = QLabel("NoFrame", no_frame)
        lbl_no_frame.setGeometry(10, 30, 130, 20)
        lbl_no_frame.setStyleSheet("background-color: #FFEBEE;")
        lbl_no_frame.show()
        no_frame.show()
        frames_layout.addWidget(no_frame)
        
        # Box
        box_frame = QWidget(central)
        box_frame.setFrameShape(Qt.FrameShape.Box)
        box_frame.resize(150, 80)
        lbl_box = QLabel("Box", box_frame)
        lbl_box.setGeometry(10, 30, 130, 20)
        lbl_box.setStyleSheet("background-color: #E8F5E9;")
        lbl_box.show()
        box_frame.show()
        frames_layout.addWidget(box_frame)
        
        # Panel
        panel_frame = QWidget(central)
        panel_frame.setFrameShape(Qt.FrameShape.Panel)
        panel_frame.resize(150, 80)
        lbl_panel = QLabel("Panel (3D)", panel_frame)
        lbl_panel.setGeometry(10, 30, 130, 20)
        lbl_panel.setStyleSheet("background-color: #FFF3E0;")
        lbl_panel.show()
        panel_frame.show()
        frames_layout.addWidget(panel_frame)
        
        # StyledPanel
        styled_frame = QWidget(central)
        styled_frame.setFrameShape(Qt.FrameShape.StyledPanel)
        styled_frame.resize(150, 80)
        lbl_styled = QLabel("StyledPanel", styled_frame)
        lbl_styled.setGeometry(10, 30, 130, 20)
        lbl_styled.setStyleSheet("background-color: #F3E5F5;")
        lbl_styled.show()
        styled_frame.show()
        frames_layout.addWidget(styled_frame)
        
        main_layout.addLayout(frames_layout)
        
        # 2. Cursor Test
        cursor_section = QLabel("2. Cursor Shapes (setCursor - hover over buttons)", central)
        cursor_section.setStyleSheet("font-weight: bold; font-size: 14px; margin-top: 10px;")
        cursor_section.show()
        main_layout.addWidget(cursor_section)
        
        cursor_layout = QHBoxLayout()
        
        arrow_btn = QPushButton("Arrow Cursor", central)
        arrow_btn.setCursor(Qt.CursorShape.ArrowCursor)
        arrow_btn.show()
        cursor_layout.addWidget(arrow_btn)
        
        cross_btn = QPushButton("Cross Cursor", central)
        cross_btn.setCursor(Qt.CursorShape.CrossCursor)
        cross_btn.show()
        cursor_layout.addWidget(cross_btn)
        
        resize_btn = QPushButton("Resize Cursor", central)
        resize_btn.setCursor(Qt.CursorShape.SizeFDiagCursor)
        resize_btn.show()
        cursor_layout.addWidget(resize_btn)
        
        main_layout.addLayout(cursor_layout)
        
        # 3. Minimum Size Test
        minsize_section = QLabel("3. Minimum Size Enforcement (setMinimumSize)", central)
        minsize_section.setStyleSheet("font-weight: bold; font-size: 14px; margin-top: 10px;")
        minsize_section.show()
        main_layout.addWidget(minsize_section)
        
        minsize_info = QLabel("The button below has setMinimumSize(200, 50) - layout should respect it", central)
        minsize_info.setStyleSheet("font-size: 11px; color: #666;")
        minsize_info.show()
        main_layout.addWidget(minsize_info)
        
        minsize_btn = QPushButton("Minimum Size Button", central)
        minsize_btn.setMinimumSize(200, 50)
        minsize_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        minsize_btn.show()
        main_layout.addWidget(minsize_btn)
        
        # 4. Window Flags Test (informational)
        winflags_section = QLabel("4. Window Flags (setWindowFlags)", central)
        winflags_section.setStyleSheet("font-weight: bold; font-size: 14px; margin-top: 10px;")
        winflags_section.show()
        main_layout.addWidget(winflags_section)
        
        winflags_info = QLabel("Window flags are stored and can be queried with windowFlags(). Dialog type behavior implemented in QDialog.", central)
        winflags_info.setStyleSheet("font-size: 11px; color: #666;")
        winflags_info.show()
        main_layout.addWidget(winflags_info)
        
        # Status
        status = self.statusBar()
        status.showMessage("✅ All missing features implemented and visible")
        
        central.show()

def main():
    app = QApplication(sys.argv)
    win = TestMissingFeatures()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
