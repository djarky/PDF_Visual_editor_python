#!/usr/bin/env python3
"""
Part 3: Layouts and Organization - Visual Test
Tests QGridLayout auto-insert and QFormLayout dynamic heights.
"""
import sys
import os

# Setup path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

from gameqt.application import QApplication
from gameqt.widgets import (QMainWindow, QWidget, QLabel, QPushButton, 
                             QLineEdit, QCheckBox, QTextEdit, QComboBox,
                             QSpinBox, QGroupBox, QTabWidget)
from gameqt.layouts import QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout
from gameqt.core import Qt

class LayoutTestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Part 3: Layout Tests")
        self.resize(800, 600)
        
        central = QWidget()
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Header
        header = QLabel(central)
        header.setText("Part 3: Layouts and Organization")
        header.setStyleSheet("font-size: 20px; font-weight: bold;")
        header.show()
        main_layout.addWidget(header)
        
        # Tab widget for different tests
        tabs = QTabWidget(central)
        tabs.resize(780, 500)
        
        # Tab 1: QGridLayout Auto-Insert Test
        grid_tab = self.create_grid_test()
        tabs.addTab(grid_tab, "QGridLayout Auto-Insert")
        
        # Tab 2: QFormLayout Dynamic Heights
        form_tab = self.create_form_test()
        tabs.addTab(form_tab, "QFormLayout Dynamic")
        
        tabs.show()
        main_layout.addWidget(tabs)
        
        self.setCentralWidget(central)
        central.show()
    
    def create_grid_test(self):
        """Test QGridLayout auto-insert functionality."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Info label
        info = QLabel(widget)
        info.setText("QGridLayout with setColumnCount(3) and auto-insert:")
        info.show()
        layout.addWidget(info)
        
        # Grid container
        grid_container = QWidget(widget)
        grid_container.resize(700, 300)
        grid = QGridLayout(grid_container)
        grid.setColumnCount(3)  # 3 columns for auto-insert
        grid.setSpacing(10)
        grid.setContentsMargins(10, 10, 10, 10)
        
        # Add widgets WITHOUT specifying row/col (auto-insert)
        colors = ["#FFB3BA", "#BAFFC9", "#BAE1FF", "#FFFFBA", "#FFD9BA", "#E2BAFF"]
        for i in range(6):
            btn = QPushButton(f"Auto {i+1}", grid_container)
            btn.setStyleSheet(f"background-color: {colors[i]}; padding: 15px;")
            btn.show()
            grid.addWidget(btn)  # No row/col specified!
        
        grid_container.show()
        layout.addWidget(grid_container)
        
        # Custom positions test
        info2 = QLabel(widget)
        info2.setText("QGridLayout with custom row/column sizes:")
        info2.show()
        layout.addWidget(info2)
        
        grid2_container = QWidget(widget)
        grid2_container.resize(700, 150)
        grid2 = QGridLayout(grid2_container)
        grid2.setSpacing(5)
        grid2.setRowMinimumHeight(0, 60)  # First row taller
        grid2.setColumnMinimumWidth(0, 150)  # First column wider
        
        lbl1 = QPushButton("Row 0, Col 0 (tall/wide)", grid2_container)
        lbl1.setStyleSheet("background-color: #98D8C8;")
        lbl1.show()
        grid2.addWidget(lbl1, 0, 0)
        
        lbl2 = QPushButton("Row 0, Col 1", grid2_container)
        lbl2.setStyleSheet("background-color: #F7DC6F;")
        lbl2.show()
        grid2.addWidget(lbl2, 0, 1)
        
        lbl3 = QPushButton("Row 1, Col 0", grid2_container)
        lbl3.setStyleSheet("background-color: #BB8FCE;")
        lbl3.show()
        grid2.addWidget(lbl3, 1, 0)
        
        lbl4 = QPushButton("Row 1, Col 1", grid2_container)
        lbl4.setStyleSheet("background-color: #85C1E9;")
        lbl4.show()
        grid2.addWidget(lbl4, 1, 1)
        
        grid2_container.show()
        layout.addWidget(grid2_container)
        
        widget.show()
        return widget
    
    def create_form_test(self):
        """Test QFormLayout dynamic row heights."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Info label
        info = QLabel(widget)
        info.setText("QFormLayout with dynamic row heights:")
        info.show()
        layout.addWidget(info)
        
        # Form container
        form_container = QWidget(widget)
        form_container.resize(700, 400)
        form = QFormLayout(form_container)
        form.setLabelWidth(150)
        form.setSpacing(8)
        form.setContentsMargins(10, 10, 10, 10)
        
        # Regular field
        name_edit = QLineEdit(form_container)
        name_edit.setPlaceholderText("Enter your name...")
        name_edit.show()
        form.addRow("Name:", name_edit)
        
        # ComboBox (slightly taller)
        combo = QComboBox(form_container)
        combo.addItems(["Option 1", "Option 2", "Option 3"])
        combo.show()
        form.addRow("Choice:", combo)
        
        # SpinBox
        spin = QSpinBox(form_container)
        spin.show()
        form.addRow("Quantity:", spin)
        
        # TextEdit (much taller - auto-detected)
        desc_edit = QTextEdit(form_container)
        desc_edit.setPlainText("This QTextEdit should be taller automatically...")
        desc_edit.show()
        form.addRow("Description:", desc_edit)
        form.setRowMinimumHeight(3, 120)  # Explicit height for description
        
        # Checkbox
        check = QCheckBox("I agree to the terms", form_container)
        check.show()
        form.addRow("Agreement:", check)
        
        # Custom row spacing
        form.setRowSpacing(2, 20)  # Extra space after quantity
        
        form_container.show()
        layout.addWidget(form_container)
        
        widget.show()
        return widget

def main():
    app = QApplication(sys.argv)
    window = LayoutTestWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
