from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QHeaderView, QAbstractItemView, QPushButton, QMenu, QSlider, QStyledItemDelegate, QStyleOptionViewItem, QLabel, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal, QMimeData, QModelIndex
from PyQt6.QtGui import QIcon

class OpacitySliderDelegate(QStyledItemDelegate):
    """Custom delegate to display a slider for opacity values."""
    
    def createEditor(self, parent, option, index):
        """Create a slider widget for editing opacity."""
        slider = QSlider(Qt.Orientation.Horizontal, parent)
        slider.setMinimum(0)
        slider.setMaximum(100)
        slider.setSingleStep(1)
        slider.setPageStep(10)
        return slider
    
    def setEditorData(self, editor, index):
        """Load current opacity value into the slider."""
        value = index.data(Qt.ItemDataRole.DisplayRole)
        try:
            # Convert opacity from 0.0-1.0 to 0-100
            opacity = float(value) * 100
            editor.setValue(int(opacity))
        except (ValueError, TypeError):
            editor.setValue(100)
    
    def setModelData(self, editor, model, index):
        """Save the slider value back to the model."""
        # Convert from 0-100 to 0.0-1.0
        opacity = editor.value() / 100.0
        model.setData(index, f"{opacity:.2f}", Qt.ItemDataRole.EditRole)
    
    def updateEditorGeometry(self, editor, option, index):
        """Set the slider geometry to match the cell."""
        editor.setGeometry(option.rect)
    
    def displayText(self, value, locale):
        """Display opacity as percentage."""
        try:
            opacity = float(value) * 100
            return f"{int(opacity)}%"
        except (ValueError, TypeError):
            return "100%"

class InspectorTreeWidget(QTreeWidget):
    def mimeData(self, items):
        # Custom mimeData to avoid serializing QGraphicsItem pointers
        mime = QMimeData()
        mime.setData("application/x-qabstractitemmodeldatalist", b"") 
        return mime

    def dropEvent(self, event):
        # Manual handle of move
        source_items = self.selectedItems()
        if not source_items:
            return
            
        target_item = self.itemAt(event.position().toPoint())
        root = self.invisibleRootItem()
        
        # Determine target index
        if target_item:
            if target_item.parent() is None:
                target_parent = root
                target_index = root.indexOfChild(target_item)
            else:
                target_parent = target_item.parent()
                target_index = target_parent.indexOfChild(target_item)
        else:
            target_parent = root
            target_index = root.childCount()
            
        # Move items
        for item in source_items:
            if item.parent() != target_parent:
                if item.parent():
                    item.parent().removeChild(item)
                else:
                    root.removeChild(item)
                target_parent.insertChild(target_index, item)
            else:
                current_index = target_parent.indexOfChild(item)
                target_parent.takeChild(current_index)
                if current_index < target_index:
                    target_index -= 1
                target_parent.insertChild(target_index, item)
                
        # Update Z-order logic
        page_content = None
        for i in range(root.childCount()):
            if root.child(i).text(0) == "Page Content":
                page_content = root.child(i)
                break
        
        if page_content:
            count = page_content.childCount()
            for i in range(count):
                item = page_content.child(i)
                graphics_item = item.data(0, Qt.ItemDataRole.UserRole + 1)
                if graphics_item:
                    graphics_item.setZValue(count - i)
                    
        event.accept()

class InspectorPanel(QWidget):
    """
    Panel showing a tree view of elements on the current page.
    Supports layers, visibility, and opacity.
    """
    itemChanged = pyqtSignal(object, int) # Item, Column
    backgroundOpacityChanged = pyqtSignal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        
        # Background Opacity Slider
        bg_layout = QHBoxLayout()
        bg_layout.addWidget(QLabel("Background Opacity:"))
        self.bg_slider = QSlider(Qt.Orientation.Horizontal)
        self.bg_slider.setMinimum(0)
        self.bg_slider.setMaximum(100)
        self.bg_slider.setValue(50) # Default
        self.bg_slider.valueChanged.connect(self._on_bg_slider_changed)
        bg_layout.addWidget(self.bg_slider)
        self.bg_label = QLabel("50%")
        bg_layout.addWidget(self.bg_label)
        
        layout.addLayout(bg_layout)
        
        self.tree = InspectorTreeWidget()
        self.tree.setHeaderLabels(["Element", "Type", "Vis", "Opacity"])
        self.tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tree.header().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.tree.header().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        
        self.tree.setDragEnabled(True)
        self.tree.setAcceptDrops(True)
        self.tree.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.tree.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        
        self.tree.itemChanged.connect(self._on_item_changed)
        
        layout.addWidget(self.tree)
        
        # Bottom buttons
        btn_layout = QVBoxLayout()
        self.btn_show_all = QPushButton("Show All")
        self.btn_hide_all = QPushButton("Hide All")
        btn_layout.addWidget(self.btn_show_all)
        btn_layout.addWidget(self.btn_hide_all)
        layout.addLayout(btn_layout)
        
        self.btn_show_all.clicked.connect(lambda: self.set_all_visibility(True))
        self.btn_hide_all.clicked.connect(lambda: self.set_all_visibility(False))
        
        # Set custom delegate for opacity column (column 3)
        opacity_delegate = OpacitySliderDelegate()
        self.tree.setItemDelegateForColumn(3, opacity_delegate)
        
        # Enable context menu
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.show_context_menu)

    def show_context_menu(self, position):
        """Show context menu on right-click."""
        menu = QMenu(self.tree)
        
        copy_action = menu.addAction("Copy")
        paste_action = menu.addAction("Paste")
        menu.addSeparator()
        create_folder_action = menu.addAction("Create Folder")
        menu.addSeparator()
        delete_action = menu.addAction("Delete")
        
        # Enable/disable based on selection
        has_selection = bool(self.tree.selectedItems())
        copy_action.setEnabled(has_selection)
        delete_action.setEnabled(has_selection)
        
        action = menu.exec(self.tree.viewport().mapToGlobal(position))
        
        if action == copy_action:
            self.copy_items()
        elif action == paste_action:
            self.paste_items()
        elif action == create_folder_action:
            self.create_folder()
        elif action == delete_action:
            self.delete_items()

    def copy_items(self):
        """Copy selected items to internal clipboard."""
        selected = self.tree.selectedItems()
        if not selected:
            return
        # Store references
        self.clipboard_items = selected[:]

    def paste_items(self):
        """Paste items from clipboard under current selection or root."""
        if not hasattr(self, 'clipboard_items') or not self.clipboard_items:
            return
        
        # Determine target
        selected = self.tree.selectedItems()
        if selected:
            target = selected[0]
            # If target is a folder, paste as child. Otherwise paste as sibling.
            if target.childCount() > 0 or target.text(1) == "folder":
                parent = target
            else:
                parent = target.parent() if target.parent() else self.tree.invisibleRootItem()
        else:
            # Paste at root
            root = self.tree.topLevelItem(0)
            parent = root if root else self.tree.invisibleRootItem()
        
        # Duplicate items (shallow copy for now)
        for item in self.clipboard_items:
            self.duplicate_tree_item(item, parent)

    def duplicate_tree_item(self, source_item, target_parent):
        """Duplicate a tree item and add to target parent."""
        new_item = QTreeWidgetItem(target_parent)
        for col in range(source_item.columnCount()):
            new_item.setText(col, source_item.text(col))
        new_item.setCheckState(2, source_item.checkState(2))
        new_item.setFlags(source_item.flags())
        
        # Copy user data
        new_item.setData(0, Qt.ItemDataRole.UserRole, source_item.data(0, Qt.ItemDataRole.UserRole))
        
        # Note: Graphics item reference is NOT copied - this creates a duplicate tree entry
        # but not a duplicate graphics item. For actual duplication, MainWindow would need to handle it.

    def create_folder(self):
        """Create a new folder/group in the tree."""
        # Determine where to create
        selected = self.tree.selectedItems()
        if selected:
            parent = selected[0] if (selected[0].childCount() > 0 or selected[0].text(1) == "folder") else selected[0].parent()
            if not parent:
                parent = self.tree.topLevelItem(0)
        else:
            parent = self.tree.topLevelItem(0)
        
        if not parent:
            # No root exists yet, create one
            parent = QTreeWidgetItem(self.tree)
            parent.setText(0, "Page Content")
            parent.setExpanded(True)
        
        # Create folder item
        folder_item = QTreeWidgetItem(parent)
        folder_item.setText(0, "New Folder")
        folder_item.setText(1, "folder")
        folder_item.setCheckState(2, Qt.CheckState.Checked)
        folder_item.setText(3, "1.0")
        folder_item.setFlags(folder_item.flags() | Qt.ItemFlag.ItemIsEditable)
        folder_item.setExpanded(True)

    def delete_items(self):
        """Delete selected items from tree and their graphics items from scene."""
        selected = self.tree.selectedItems()
        for item in selected:
            # Get graphics item and remove from scene
            graphics_item = item.data(0, Qt.ItemDataRole.UserRole + 1)
            if graphics_item and hasattr(graphics_item, 'scene') and graphics_item.scene():
                graphics_item.scene().removeItem(graphics_item)
            
            # Remove from tree
            parent = item.parent()
            if parent:
                parent.removeChild(item)
            else:
                index = self.tree.indexOfTopLevelItem(item)
                if index >= 0:
                    self.tree.takeTopLevelItem(index)

    def set_all_visibility(self, visible: bool):
        root = self.tree.topLevelItem(0)
        if not root: return
        
        state = Qt.CheckState.Checked if visible else Qt.CheckState.Unchecked
        for i in range(root.childCount()):
            item = root.child(i)
            item.setCheckState(2, state)

    def update_elements(self, elements):
        self.tree.clear()
        
        # Create a root folder for "Page Content"
        root = QTreeWidgetItem(self.tree)
        root.setText(0, "Page Content")
        root.setExpanded(True)
        
        for el in elements:
            item = QTreeWidgetItem(root)
            item.setText(0, el.get('text', 'Element')[:20] if el.get('type') == 'text' else 'Image/Rect')
            item.setText(1, el.get('type', 'Unknown'))
            item.setCheckState(2, Qt.CheckState.Checked) # Visibility
            item.setText(3, "1.0") # Opacity
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
            
            # Store reference to actual graphics item (will be linked later)
            item.setData(0, Qt.ItemDataRole.UserRole, el)

    def _on_item_changed(self, item, column):
        self.itemChanged.emit(item, column)

    def clear(self):
        self.tree.clear()

    def _on_bg_slider_changed(self, value):
        opacity = value / 100.0
        self.bg_label.setText(f"{value}%")
        self.backgroundOpacityChanged.emit(opacity)

    def set_background_opacity_value(self, opacity):
        value = int(opacity * 100)
        self.bg_slider.blockSignals(True)
        self.bg_slider.setValue(value)
        self.bg_label.setText(f"{value}%")
        self.bg_slider.blockSignals(False)
