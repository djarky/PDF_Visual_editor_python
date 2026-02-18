
import unittest
import sys
import os
from unittest.mock import MagicMock

# Mock pygame
sys.modules['pygame'] = MagicMock()

# Ensure pdf_visual_editor is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from gameqt.item_views import QListWidget, QListWidgetItem
from gameqt.application import QApplication

if not QApplication.instance():
    try:
        app = QApplication(sys.argv)
    except:
        pass

class TestItemViews(unittest.TestCase):
    def test_list_widget(self):
        list_widget = QListWidget()
        
        item1 = QListWidgetItem("Item 1")
        list_widget.addItem(item1)
        
        self.assertEqual(list_widget.count(), 1)
        self.assertEqual(list_widget.item(0).text(), "Item 1")
        
        list_widget.addItem("Item 2")
        self.assertEqual(list_widget.count(), 2)
        self.assertEqual(list_widget.item(1).text(), "Item 2")

    def test_item_selection(self):
        list_widget = QListWidget()
        item = QListWidgetItem("Selectable")
        list_widget.addItem(item)
        
        item.setSelected(True)
        self.assertTrue(item.isSelected())

if __name__ == '__main__':
    unittest.main()
