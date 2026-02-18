
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from gameqt import QApplication, QSplitter, QWidget, QVBoxLayout, QHBoxLayout, QLabel, Qt, QColor

def main():
    app = QApplication(sys.argv)
    
    # Create main window
    from gameqt.widgets import QMainWindow
    window = QMainWindow()
    window.setWindowTitle("Splitter Demo")
    window.resize(800, 600)
    
    # Create central widget
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    
    # Main layout
    main_layout = QVBoxLayout(central_widget)
    
    # Horizontal Splitter
    h_splitter = QSplitter(Qt.Orientation.Horizontal)
    
    # Add some widgets to splitter
    w1 = QWidget()
    w1.setStyleSheet("background-color: #FFCCCC; border: 1px solid red;")
    l1 = QVBoxLayout(w1)
    lbl1 = QLabel("Left Panel")
    l1.addWidget(lbl1)
    
    w2 = QWidget()
    w2.setStyleSheet("background-color: #CCFFCC; border: 1px solid green;")
    l2 = QVBoxLayout(w2)
    lbl2 = QLabel("Middle Panel")
    l2.addWidget(lbl2)
    
    w3 = QWidget()
    w3.setStyleSheet("background-color: #CCCCFF; border: 1px solid blue;")
    l3 = QVBoxLayout(w3)
    lbl3 = QLabel("Right Panel")
    l3.addWidget(lbl3)
    
    h_splitter.addWidget(w1)
    h_splitter.addWidget(w2)
    h_splitter.addWidget(w3)
    
    # Set initial sizes
    h_splitter.setSizes([200, 400, 200])
    
    main_layout.addWidget(h_splitter)
    
    window.show()
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
