import sys
import os
import pygame

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from pdf_visual_editor.gameqt.application import QApplication
from pdf_visual_editor.gameqt.widgets import QMainWindow, QWidget, QPushButton, QDialog, QMessageBox
from pdf_visual_editor.gameqt.layouts import QVBoxLayout

class DialogTest(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dialog Close Test")
        self.resize(400, 300)
        
        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        btn_qdialog = QPushButton("Open QDialog")
        btn_qdialog.clicked.connect(self.open_qdialog)
        layout.addWidget(btn_qdialog)
        
        btn_qmsg = QPushButton("Open QMessageBox")
        btn_qmsg.clicked.connect(self.open_qmsg)
        layout.addWidget(btn_qmsg)
        
        btn_close_self = QPushButton("Close Main Window")
        btn_close_self.clicked.connect(self.close)
        layout.addWidget(btn_close_self)

    def open_qdialog(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Test QDialog")
        dlg.resize(300, 200)
        dlg.exec()
        print("QDialog closed")

    def open_qmsg(self):
        QMessageBox.information(self, "Test Message", "Try closing me with the [X] button!")
        print("QMessageBox closed")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = DialogTest()
    win.show()
    sys.exit(app.exec())
