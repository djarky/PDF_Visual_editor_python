
import unittest
import sys
import os
from unittest.mock import MagicMock

# Mock pygame before importing gameqt
sys.modules['pygame'] = MagicMock()

# Ensure pdf_visual_editor is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from gameqt.menus import QMenuBar, QMenu, QAction
from gameqt.application import QApplication

# Mock QApplication if needed, or rely on headless
if not QApplication.instance():
    try:
        app = QApplication(sys.argv)
    except:
        pass

class TestMenus(unittest.TestCase):
    def test_action_creation(self):
        action = QAction("Test Action")
        # GameQt uses attributes directly
        self.assertEqual(action.text, "Test Action")
        self.assertTrue(action.isEnabled())
        
        action.setEnabled(False)
        self.assertFalse(action.isEnabled())

    def test_menu_creation(self):
        menu = QMenu("File")
        self.assertEqual(menu.text, "File")
        
        action = menu.addAction("New")
        self.assertIsInstance(action, QAction)
        self.assertEqual(action.text, "New")

    def test_menubar_creation(self):
        menubar = QMenuBar()
        menu = menubar.addMenu("Edit")
        self.assertIsInstance(menu, QMenu)
        self.assertEqual(menu.text, "Edit")

if __name__ == '__main__':
    unittest.main()
