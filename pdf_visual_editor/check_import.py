
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath("."))

try:
    from gui.main_window import MainWindow
    print("Successfully imported MainWindow")
except ImportError as e:
    print(f"ImportError: {e}")
except Exception as e:
    print(f"Error: {e}")
