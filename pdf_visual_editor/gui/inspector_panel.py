from qt_compat import (QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QHeaderView, 
                       QAbstractItemView, QPushButton, QMenu, QSlider, QStyledItemDelegate, 
                       QStyleOptionViewItem, QLabel, QHBoxLayout, Qt, Signal, QMimeData, 
                       QModelIndex, QIcon, QAction)

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
    deleteKeyPressed = Signal()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Delete:
            self.deleteKeyPressed.emit()
        else:
            super().keyPressEvent(event)

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
    itemChanged = Signal(object, int) # Item, Column
    backgroundOpacityChanged = Signal(float)
    duplicateRequested = Signal(list) # List of QGraphicsItems

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
        
        self.tree.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        
        self.tree.itemChanged.connect(self._on_item_changed)
        self.tree.deleteKeyPressed.connect(self.delete_items)
        
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

        # Shortcuts
        self.join_action = QAction("Join into Folder", self)
        self.join_action.setShortcut("Ctrl+J")
        self.join_action.triggered.connect(self.join_items)
        self.addAction(self.join_action)

    def show_context_menu(self, position):
        """Show context menu on right-click."""
        menu = QMenu(self.tree)
        
        duplicate_action = menu.addAction("Duplicate")
        join_action = menu.addAction("Join into Folder (Ctrl+J)")
        menu.addSeparator()
        create_folder_action = menu.addAction("Create Folder")
        menu.addSeparator()
        delete_action = menu.addAction("Delete")
        
        # Enable/disable based on selection
        has_selection = bool(self.tree.selectedItems())
        duplicate_action.setEnabled(has_selection)
        join_action.setEnabled(has_selection)
        delete_action.setEnabled(has_selection)
        
        action = menu.exec(self.tree.viewport().mapToGlobal(position))
        
        if action == duplicate_action:
            self.duplicate_items()
        elif action == join_action:
            self.join_items()
        elif action == create_folder_action:
            self.create_folder()
        elif action == delete_action:
            self.delete_items()

    def duplicate_items(self):
        """Request duplication of selected items."""
        selected = self.tree.selectedItems()
        if not selected:
            return
        
        items_to_duplicate = []
        for item in selected:
            graphics_item = item.data(0, Qt.ItemDataRole.UserRole + 1)
            if graphics_item:
                items_to_duplicate.append(graphics_item)
        
        if items_to_duplicate:
            self.duplicateRequested.emit(items_to_duplicate)

    def join_items(self):
        """Join selected items into a new folder."""
        selected = self.tree.selectedItems()
        if not selected:
            return

        # Determine parent for the new folder
        # Use the parent of the first selected item
        first_item = selected[0]
        parent = first_item.parent()
        if not parent:
            parent = self.tree.invisibleRootItem()
            # Try to find "Page Content" root if we are at top level
            if parent.childCount() > 0 and parent.child(0).text(0) == "Page Content":
                 parent = parent.child(0)

        # Create new folder
        folder_item = QTreeWidgetItem(parent)
        folder_item.setText(0, "New Folder")
        folder_item.setText(1, "folder")
        folder_item.setCheckState(2, Qt.CheckState.Checked)
        folder_item.setText(3, "1.0")
        folder_item.setFlags(folder_item.flags() | Qt.ItemFlag.ItemIsEditable)
        folder_item.setExpanded(True)
        
        # Move items into folder
        for item in selected:
            # Remove from current parent
            curr_parent = item.parent()
            if curr_parent:
                curr_parent.removeChild(item)
            else:
                self.tree.invisibleRootItem().removeChild(item)
            
            # Add to new folder
            folder_item.addChild(item)

    def add_graphics_item(self, graphics_item):
        """Add a single graphics item to the tree without rebuilding."""
        # Find appropriate folder based on type
        root = self.tree.invisibleRootItem()
        page_content = None
        for i in range(root.childCount()):
            if root.child(i).text(0) == "Page Content":
                page_content = root.child(i)
                break
        
        if not page_content:
            # Should not happen if initialized, but safety check
            return

        target_folder = page_content # Default
        
        # Try to find specific folders
        from qt_compat import QGraphicsTextItem, QGraphicsPixmapItem
        
        folder_name = "⬜ Shapes"
        if isinstance(graphics_item, QGraphicsTextItem):
            folder_name = "📝 Text"
        elif isinstance(graphics_item, QGraphicsPixmapItem):
            folder_name = "🖼️ Images"
            
        for i in range(page_content.childCount()):
            if page_content.child(i).text(0) == folder_name:
                target_folder = page_content.child(i)
                break
        
        # Create item
        tree_item = self._create_tree_item_for_graphics_item(graphics_item)
        target_folder.addChild(tree_item)

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
    
    def populate_from_scene_auto_organize(self, scene):
        """
        Populate inspector with auto-organized folders by element type (PDF import).
        Creates folders for Text, Images, and Shapes.
        """
        from .editor_canvas import ResizablePixmapItem, ResizerHandle
        from qt_compat import QGraphicsTextItem, QGraphicsPixmapItem
        
        self.clear()
        
        root = QTreeWidgetItem(self.tree)
        root.setText(0, "Page Content")
        root.setExpanded(True)
        
        # Create folders for each type
        text_folder = QTreeWidgetItem(root)
        text_folder.setText(0, "📝 Text")
        text_folder.setExpanded(True)
        
        image_folder = QTreeWidgetItem(root)
        image_folder.setText(0, "🖼️ Images")
        image_folder.setExpanded(True)
        
        shape_folder = QTreeWidgetItem(root)
        shape_folder.setText(0, "⬜ Shapes")
        shape_folder.setExpanded(True)
        
        # Sort items into folders
        for item in scene.items():
            if item.zValue() == -100: continue  # Skip background
            if isinstance(item, ResizerHandle): continue
            
            tree_item = self._create_tree_item_for_graphics_item(item)
            
            if isinstance(item, QGraphicsTextItem):
                text_folder.addChild(tree_item)
            elif isinstance(item, QGraphicsPixmapItem):
                image_folder.addChild(tree_item)
            else:
                shape_folder.addChild(tree_item)
    
    def _create_tree_item_for_graphics_item(self, graphics_item):
        """Create a tree widget item for a graphics item."""
        from qt_compat import QGraphicsTextItem, QGraphicsPixmapItem
        
        tree_item = QTreeWidgetItem()
        
        if isinstance(graphics_item, QGraphicsTextItem):
            text = graphics_item.toPlainText()
            tree_item.setText(0, text[:20] if len(text) > 20 else text)
            tree_item.setText(1, "text")
        elif isinstance(graphics_item, QGraphicsPixmapItem):
            tree_item.setText(0, "Image")
            tree_item.setText(1, "image")
        else:
            tree_item.setText(0, "Shape")
            tree_item.setText(1, "shape")
        
        tree_item.setCheckState(2, Qt.CheckState.Checked if graphics_item.isVisible() else Qt.CheckState.Unchecked)
        tree_item.setText(3, str(graphics_item.opacity()))
        tree_item.setFlags(tree_item.flags() | Qt.ItemFlag.ItemIsEditable)
        
        # Link to graphics item
        tree_item.setData(0, Qt.ItemDataRole.UserRole + 1, graphics_item)
        
        return tree_item
    
    def serialize_tree_structure(self):
        """
        Serialize current inspector tree structure for saving in .omar file.
        
        Returns:
            Dictionary with folder structure and hierarchy
        """
        folders = []
        self._serialize_folder_recursive(self.tree.invisibleRootItem(), [], folders)
        
        return {
            "folders": folders,
            "element_count": self._count_elements()
        }
    
    def _serialize_folder_recursive(self, parent_item, parent_path, folders_list):
        """Recursively serialize folder structure."""
        for i in range(parent_item.childCount()):
            item = parent_item.child(i)
            folder_name = item.text(0)
            
            # Check if this is a folder (has children) or an element
            if item.childCount() > 0:
                # This is a folder
                folder_data = {
                    "name": folder_name,
                    "expanded": item.isExpanded(),
                    "parent_path": parent_path.copy(),
                    "items": []
                }
                
                # Process children
                new_path = parent_path + [folder_name]
                for j in range(item.childCount()):
                    child = item.child(j)
                    if child.childCount() == 0:  # Leaf element
                        # Get opacity with fallback to 1.0 if empty or invalid
                        try:
                            opacity = float(child.text(3)) if child.text(3) else 1.0
                        except (ValueError, TypeError):
                            opacity = 1.0
                        
                        folder_data["items"].append({
                            "name": child.text(0),
                            "type": child.text(1),
                            "visible": child.checkState(2) == Qt.CheckState.Checked,
                            "opacity": opacity
                        })
                    else:
                        # Nested folder - recurse
                        self._serialize_folder_recursive(item, new_path, folders_list)
                
                folders_list.append(folder_data)
    
    def _count_elements(self):
        """Count total number of elements in tree."""
        count = 0
        
        def count_recursive(item):
            nonlocal count
            if item.childCount() == 0 and item.parent() is not None:
                count += 1
            for i in range(item.childCount()):
                count_recursive(item.child(i))
        
        count_recursive(self.tree.invisibleRootItem())
        return count
