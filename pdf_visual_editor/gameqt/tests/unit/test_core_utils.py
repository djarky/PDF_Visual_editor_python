import sys
import os

# Ensure gameqt is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from gameqt.core import Qt
from gameqt.utils import QModelIndex, QPrinter, QBuffer

def test_qmodelindex():
    print("Testing QModelIndex...")
    idx = QModelIndex(5, 10, "ptr", "model")
    assert idx.row() == 5
    assert idx.column() == 10
    assert idx.internalPointer() == "ptr"
    assert idx.model() == "model"
    assert idx.isValid()
    
    invalid = QModelIndex()
    assert not invalid.isValid()
    print("✓ QModelIndex passed")

def test_qprinter():
    print("Testing QPrinter...")
    printer = QPrinter()
    printer.setOutputFileName("test_report.pdf")
    assert printer.outputFileName() == "test_report.pdf"
    printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
    print("✓ QPrinter passed")

def test_qbuffer():
    print("Testing QBuffer...")
    buf = QBuffer()
    buf.write(b"GameQt Data")
    assert buf.data() == b"GameQt Data"
    print("✓ QBuffer passed")

def test_item_data_roles():
    print("Testing ItemDataRole constants...")
    assert Qt.ItemDataRole.DisplayRole == 0
    assert Qt.ItemDataRole.UserRole == 1000
    assert hasattr(Qt.ItemDataRole, 'DecorationRole')
    print("✓ ItemDataRole passed")

if __name__ == "__main__":
    try:
        test_qmodelindex()
        test_qprinter()
        test_qbuffer()
        test_item_data_roles()
        print("\nAll Core/Utils tests passed!")
    except Exception as e:
        print(f"Test failed: {e}")
        sys.exit(1)
