# Imports
import sys
import os
import subprocess
import datetime

# Setup paths
current_dir = os.path.dirname(os.path.abspath(__file__))

from gameqt.application import QApplication
from gameqt.widgets import (QMainWindow, QWidget, QLabel, QPushButton, 
                             QCheckBox, QTabWidget, QScrollArea)
from gameqt.layouts import QVBoxLayout, QHBoxLayout
from gameqt.core import Qt

class TestRunner(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GameQt Test Runner")
        self.resize(900, 700)
        
        central = QWidget(self)
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Header
        header = QLabel(central)
        header.setText("GameQt Test Suite")
        header.setStyleSheet("font-size: 22px; font-weight: bold;")
        main_layout.addWidget(header)
        
        # Discover tests
        demos, units = self.discover_tests()
        
        # Create tab widget
        tabs = QTabWidget(central)
        tabs.resize(870, 550)
        
        # Visual/Graphical Tests Tab with scroll
        demo_scroll = QScrollArea(tabs)
        demo_scroll.setWidgetResizable(True)
        demo_content = QWidget(demo_scroll)
        demo_layout = QVBoxLayout(demo_content)
        demo_layout.setSpacing(6)
        demo_layout.setContentsMargins(10, 10, 10, 10)
        
        demo_info = QLabel(demo_content)
        demo_info.setText("🎨 Visual Tests - Open GUI windows")
        demo_info.setStyleSheet("padding: 8px; border-bottom: 1px solid #2196F3;")
        demo_layout.addWidget(demo_info)
        
        for name, path in demos:
            card = self.create_test_card(name, path, "Demo", demo_content)
            demo_layout.addWidget(card)
        
        demo_layout.addStretch(1)
        demo_scroll.setWidget(demo_content)
        tabs.addTab(demo_scroll, f"Visual ({len(demos)})")
        
        # Console/Unit Tests Tab with scroll
        unit_scroll = QScrollArea(tabs)
        unit_scroll.setWidgetResizable(True)
        unit_content = QWidget(unit_scroll)
        unit_layout = QVBoxLayout(unit_content)
        unit_layout.setSpacing(6)
        unit_layout.setContentsMargins(10, 10, 10, 10)
        
        unit_info = QLabel(unit_content)
        unit_info.setText("⚙️ Console Tests - Check terminal")
        unit_info.setStyleSheet("padding: 8px; border-bottom: 1px solid #FF9800;")
        unit_layout.addWidget(unit_info)
        
        for name, path in units:
            card = self.create_test_card(name, path, "Unit", unit_content)
            unit_layout.addWidget(card)
        
        unit_layout.addStretch(1)
        unit_scroll.setWidget(unit_content)
        tabs.addTab(unit_scroll, f"Console ({len(units)})")
        
        main_layout.addWidget(tabs)
        
        # Footer
        footer_layout = QHBoxLayout()
        
        stats_label = QLabel(central)
        stats_label.setText(f"Total: {len(demos) + len(units)} tests ({len(demos)} visual, {len(units)} console)")
        footer_layout.addWidget(stats_label)
        
        exit_btn = QPushButton("Exit", central)
        exit_btn.clicked.connect(self.close)
        footer_layout.addWidget(exit_btn)
        
        main_layout.addLayout(footer_layout)
        
        self.setCentralWidget(central)

    def discover_tests(self):
        """Scans directories for tests and demos. Returns (demos, units) as separate lists."""
        demos = []
        units = []
        
        # Demos
        demos_dir = os.path.join(current_dir, 'demos')
        if os.path.exists(demos_dir):
            for f in sorted(os.listdir(demos_dir)):
                if f.endswith('.py'):
                    name = f.replace('_', ' ').title().replace('.Py', '')
                    path = os.path.join(demos_dir, f)
                    demos.append((name, path))
        
        # Unit Tests
        unit_dir = os.path.join(current_dir, 'unit')
        if os.path.exists(unit_dir):
             for f in sorted(os.listdir(unit_dir)):
                if f.startswith('test_') and f.endswith('.py'):
                    name = f.replace('_', ' ').title().replace('.Py', '')
                    path = os.path.join(unit_dir, f)
                    units.append((name, path))
                    
        # Custom sort: Put "test_..._partX.py" at the top, then others
        def sort_key(item):
            filename = os.path.basename(item[1]).lower()
            is_prog_test = 'part' in filename or 'phase' in filename
            if is_prog_test:
                # Extract part/phase number if possible for ordering
                try:
                    import re
                    match = re.search(r'(?:part|phase)(\d+)', filename)
                    if match:
                        return (0, int(match.group(1)), filename)
                except:
                    pass
                return (0, 99, filename) # Part test but no number found
            return (1, 0, filename) # Ordinary demo
            
        demos.sort(key=sort_key)
        units.sort(key=sort_key)
        
        return demos, units

    def create_test_card(self, name, path, test_type, parent):
        # Create a horizontal card layout
        card = QWidget(parent)
        card.resize(820, 55)
        
        # border based on type
        border_clr = "#2196F3" if test_type == "Demo" else "#FF9800"
        card.setStyleSheet(f"border: 1px solid {border_clr}; border-radius: 6px; margin: 2px;")
        
        layout = QHBoxLayout(card)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 10, 15, 10)
        
        # Title label
        title = QLabel(card)
        title.setText(name)
        title.setStyleSheet("font-weight: bold; border: none; font-size: 13px;")
        layout.addWidget(title)
        
        # Run button
        run_btn = QPushButton("▶ Run", card)
        run_btn.clicked.connect(lambda: self.run_test(path, name))
        run_btn.setStyleSheet("background-color: #4CAF50; color: white; border: none; padding: 8px 20px; border-radius: 4px; font-size: 13px; min-width: 80px;")
        layout.addWidget(run_btn)
        
        # Pass checkbox
        pass_chk = QCheckBox("✓ Pass", card)
        pass_chk.setStyleSheet("border: none; padding: 5px; font-size: 12px; color: #4CAF50;")
        layout.addWidget(pass_chk)
        
        # Fail checkbox
        fail_chk = QCheckBox("✗ Fail", card)
        fail_chk.setStyleSheet("border: none; padding: 5px; font-size: 12px; color: #F44336;")
        layout.addWidget(fail_chk)
        
        # Skip checkbox
        skip_chk = QCheckBox("⊘ Skip", card)
        skip_chk.setStyleSheet("border: none; padding: 5px; font-size: 12px; color: #FF9800;")
        layout.addWidget(skip_chk)
        
        # Partial/Incomplete checkbox
        partial_chk = QCheckBox("◐ Partial", card)
        partial_chk.setStyleSheet("border: none; padding: 5px; font-size: 12px; color: #2196F3;")
        layout.addWidget(partial_chk)

        # Logic to make them mutually exclusive (4 states)
        def on_pass(s):
            if s == 2: # Checked
                fail_chk.blockSignals(True)
                skip_chk.blockSignals(True)
                partial_chk.blockSignals(True)
                fail_chk.setChecked(False)
                skip_chk.setChecked(False)
                partial_chk.setChecked(False)
                fail_chk.blockSignals(False)
                skip_chk.blockSignals(False)
                partial_chk.blockSignals(False)
                self.log_result(name, "PASS")
            else:
                self.log_result(name, "RESET")

        def on_fail(s):
            if s == 2: # Checked
                pass_chk.blockSignals(True)
                skip_chk.blockSignals(True)
                partial_chk.blockSignals(True)
                pass_chk.setChecked(False)
                skip_chk.setChecked(False)
                partial_chk.setChecked(False)
                pass_chk.blockSignals(False)
                skip_chk.blockSignals(False)
                partial_chk.blockSignals(False)
                self.log_result(name, "FAIL")
            else:
                self.log_result(name, "RESET")
        
        def on_skip(s):
            if s == 2: # Checked
                pass_chk.blockSignals(True)
                fail_chk.blockSignals(True)
                partial_chk.blockSignals(True)
                pass_chk.setChecked(False)
                fail_chk.setChecked(False)
                partial_chk.setChecked(False)
                pass_chk.blockSignals(False)
                fail_chk.blockSignals(False)
                partial_chk.blockSignals(False)
                self.log_result(name, "SKIP")
            else:
                self.log_result(name, "RESET")
        
        def on_partial(s):
            if s == 2: # Checked
                pass_chk.blockSignals(True)
                fail_chk.blockSignals(True)
                skip_chk.blockSignals(True)
                pass_chk.setChecked(False)
                fail_chk.setChecked(False)
                skip_chk.setChecked(False)
                pass_chk.blockSignals(False)
                fail_chk.blockSignals(False)
                skip_chk.blockSignals(False)
                self.log_result(name, "PARTIAL")
            else:
                self.log_result(name, "RESET")

        pass_chk.stateChanged.connect(on_pass)
        fail_chk.stateChanged.connect(on_fail)
        skip_chk.stateChanged.connect(on_skip)
        partial_chk.stateChanged.connect(on_partial)
        
        
        return card

    def run_test(self, path, name=""):
        # Run in a separate process
        print(f"\n{'='*60}")
        print(f"▶ Running: {name or os.path.basename(path)}")
        print(f"{'='*60}")
        # Ensure we use the current interpreter
        subprocess.Popen([sys.executable, path])

    def log_result(self, name, result):
        if result == "RESET": return
        
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {name}: {result}\n"
        print(log_entry.strip())
        
        log_dir = os.path.join(current_dir, 'logs')
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        with open(os.path.join(log_dir, 'test_report.log'), 'a') as f:
            f.write(log_entry)

def main():
    app = QApplication(sys.argv)
    runner = TestRunner()
    runner.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
