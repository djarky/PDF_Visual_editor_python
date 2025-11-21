from PyQt6.QtWidgets import QMainWindow, QSplitter, QWidget, QVBoxLayout, QFileDialog, QMessageBox, QLabel, QTreeWidgetItem, QGraphicsPixmapItem, QGraphicsItem, QGraphicsRectItem, QGraphicsTextItem
from PyQt6.QtGui import QPixmap, QTransform, QPen, QColor, QBrush, QUndoStack
from PyQt6.QtGui import QPixmap, QTransform, QPen, QColor, QBrush
from PyQt6.QtCore import Qt, QRectF, QBuffer, QIODevice
from .editor_canvas import EditorCanvas, EditorScene, EditableTextItem, ResizablePixmapItem, ResizerHandle
from .thumbnail_panel import ThumbnailPanel
from .inspector_panel import InspectorPanel
from .menus import AppMenu
from .about_dialog import AboutDialog
from pdf_loader import PDFLoader
from layout_analyzer import LayoutAnalyzer
from export.pdf_writer import PDFWriter
from export.pikepdf_writer import PikePDFWriter
from utils.geometry import CoordinateConverter
from gui.commands import AddItemCommand, DeleteItemCommand, EditTextCommand
import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Visual Editor")
        self.resize(1200, 800)
        
        # State
        self.current_file = None
        self.pdf_loader = None
        self.layout_analyzer = None
        self.page_scenes = {} # Map page_num -> EditorScene
        self.page_elements = {} # Map page_num -> elements list (for export)
        self.scene_cache_order = [] # Track LRU order
        self.MAX_CACHED_SCENES = 5 # Limit memory usage
        
        # Undo/Redo Stack
        self.undo_stack = QUndoStack(self)
        
        # Theme
        self.current_theme = "light"
        self.load_theme_preference()
        
        # UI Setup
        self.setup_ui()
        
        # Enable Drag and Drop
        self.setAcceptDrops(True)
        
    def setup_ui(self):
        # Menu
        self.menu_bar = AppMenu(self)
        self.setMenuBar(self.menu_bar)
        
        # Connect Menu Actions
        self.menu_bar.action_open.triggered.connect(self.open_pdf_dialog)
        self.menu_bar.action_save.triggered.connect(self.save_pdf)
        self.menu_bar.action_save_as.triggered.connect(self.save_pdf_as)
        self.menu_bar.action_export.triggered.connect(self.export_pdf_dialog)
        self.menu_bar.action_exit.triggered.connect(self.close)
        
        self.menu_bar.action_insert_text.triggered.connect(self.insert_text)
        self.menu_bar.action_insert_image.triggered.connect(self.insert_image)
        
        # Connect Undo/Redo
        self.menu_bar.action_undo.triggered.connect(self.undo_stack.undo)
        self.menu_bar.action_redo.triggered.connect(self.undo_stack.redo)
        
        self.menu_bar.action_copy.triggered.connect(lambda: self.canvas.copy_selection())
        self.menu_bar.action_paste.triggered.connect(lambda: self.canvas.paste_from_clipboard())
        
        # Capture Action (Add to Edit menu or Toolbar)
        # For now, let's add a button or shortcut? 
        # User asked for "drawing a rectangle", implying a mode.
        # Let's add it to the menu for now.
        self.action_capture = self.menu_bar.menu_edit.addAction("Capture Area")
        self.action_capture.setShortcut("Ctrl+Shift+C")
        self.action_capture.triggered.connect(self.toggle_capture_mode)
        
        # Connect Theme Actions
        self.menu_bar.action_theme_light.triggered.connect(lambda: self.toggle_theme("light"))
        self.menu_bar.action_theme_dark.triggered.connect(lambda: self.toggle_theme("dark"))
        
        # Connect Help Actions
        self.menu_bar.action_about.triggered.connect(self.show_about_dialog)
        
        # Main Layout
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.setCentralWidget(main_splitter)
        
        # Left: Editor Canvas
        self.canvas = EditorCanvas()
        main_splitter.addWidget(self.canvas)
        
        # Right: Panels (Splitter Vertical)
        right_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Thumbnail Panel
        self.thumbnail_panel = ThumbnailPanel()
        self.thumbnail_panel.pageSelected.connect(self.load_page)
        right_splitter.addWidget(self.thumbnail_panel)
        
        # Inspector Panel
        self.inspector_panel = InspectorPanel()
        right_splitter.addWidget(self.inspector_panel)
        
        main_splitter.addWidget(right_splitter)
        
        # Set initial sizes
        main_splitter.setSizes([800, 400])
        right_splitter.setSizes([400, 400])
        
        # Status Bar
        self.status_label = QLabel("Ready")
        self.statusBar().addWidget(self.status_label)
        
        # Connect Inspector Signals
        self.inspector_panel.itemChanged.connect(self.on_inspector_item_changed)
        self.inspector_panel.tree.itemSelectionChanged.connect(self.sync_selection_to_canvas)
        self.inspector_panel.backgroundOpacityChanged.connect(self.update_background_opacity)
        
        # We also need to connect the canvas selection changed signal.
        # But the scene is created dynamically in load_page.
        # We will connect it there.
        
        # Recent Files
        self.recent_files = []
        self.load_recent_files()

    def load_recent_files(self):
        from PyQt6.QtCore import QSettings
        settings = QSettings("Antigravity", "PDFVisualEditor")
        self.recent_files = settings.value("recent_files", [], type=list)
        self.update_recent_menu()

    def add_recent_file(self, file_path):
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
        self.recent_files.insert(0, file_path)
        self.recent_files = self.recent_files[:10] # Keep last 10
        
        from PyQt6.QtCore import QSettings
        settings = QSettings("Antigravity", "PDFVisualEditor")
        settings.setValue("recent_files", self.recent_files)
        self.update_recent_menu()

    def update_recent_menu(self):
        self.menu_bar.menu_recent.clear()
        for path in self.recent_files:
            action = self.menu_bar.menu_recent.addAction(path)
            action.triggered.connect(lambda checked, p=path: self.load_pdf(p))
    
    def load_theme_preference(self):
        """Load saved theme preference."""
        from PyQt6.QtCore import QSettings
        settings = QSettings("Antigravity", "PDFVisualEditor")
        self.current_theme = settings.value("theme", "light", type=str)
        self.apply_theme(self.current_theme)
    
    def apply_theme(self, theme_name: str):
        """Apply a theme by loading its stylesheet."""
        import os
        theme_file = os.path.join(os.path.dirname(__file__), os.path.pardir, "themes", f"{theme_name}_theme.qss")
        try:
            with open(theme_file, 'r') as f:
                stylesheet = f.read()
                self.setStyleSheet(stylesheet)
                self.current_theme = theme_name
                
                # Save preference
                from PyQt6.QtCore import QSettings
                settings = QSettings("Antigravity", "PDFVisualEditor")
                settings.setValue("theme", theme_name)
        except FileNotFoundError:
            print(f"Theme file not found: {theme_file}")
    
    def toggle_theme(self, theme_name: str):
        """Toggle to a specific theme."""
        self.apply_theme(theme_name)
    
    def show_about_dialog(self):
        """Show the About dialog."""
        dialog = AboutDialog(self)
        dialog.exec()

    def on_inspector_item_changed(self, item, column):
        # Handle visibility change (Column 2)
        if column == 2:
            visible = item.checkState(2) == Qt.CheckState.Checked
            graphics_item = item.data(0, Qt.ItemDataRole.UserRole + 1)
            if graphics_item:
                graphics_item.setVisible(visible)
        # Handle Opacity change (Column 3)
        elif column == 3:
            try:
                opacity = float(item.text(3))
                graphics_item = item.data(0, Qt.ItemDataRole.UserRole + 1)
                if graphics_item:
                    graphics_item.setOpacity(opacity)
            except ValueError:
                pass # Invalid float

            except ValueError:
                pass # Invalid float

    def update_background_opacity(self, opacity):
        """Update the opacity of the current page background."""
        if hasattr(self.canvas, 'current_page_item') and self.canvas.current_page_item:
            self.canvas.current_page_item.setOpacity(opacity)

    def sync_selection_to_inspector(self):
        """Syncs canvas selection to inspector tree."""
        if self.inspector_panel.tree.signalsBlocked(): return
        
        selected_items = self.canvas.scene.selectedItems()
        
        self.inspector_panel.tree.blockSignals(True)
        self.inspector_panel.tree.clearSelection()
        
        if not selected_items:
            self.inspector_panel.tree.blockSignals(False)
            return
            
        # Map graphics items to tree items
        # We need to iterate the tree to find matches. 
        # Since we don't have a direct map, we search.
        # Optimization: Build a map if performance is bad.
        
        root = self.inspector_panel.tree.topLevelItem(0)
        if root:
            for i in range(root.childCount()):
                tree_item = root.child(i)
                graphics_item = tree_item.data(0, Qt.ItemDataRole.UserRole + 1)
                if graphics_item in selected_items:
                    tree_item.setSelected(True)
                    # Ensure visible
                    self.inspector_panel.tree.scrollToItem(tree_item)
                    
        self.inspector_panel.tree.blockSignals(False)

    def sync_selection_to_canvas(self):
        """Syncs inspector tree selection to canvas."""
        if self.canvas.scene.signalsBlocked(): return
        
        selected_tree_items = self.inspector_panel.tree.selectedItems()
        
        self.canvas.scene.blockSignals(True)
        self.canvas.scene.clearSelection()
        
        for tree_item in selected_tree_items:
            graphics_item = tree_item.data(0, Qt.ItemDataRole.UserRole + 1)
            if graphics_item:
                graphics_item.setSelected(True)
                
        self.canvas.scene.blockSignals(False)

    def toggle_capture_mode(self):
        self.canvas.start_capture_mode()
        self.status_label.setText("Capture Mode: Draw a rectangle to capture area.")
    
    def save_pdf(self):
        """Save the current PDF with modifications."""
        if not self.current_file:
            QMessageBox.warning(self, "No File", "No PDF file is currently open.")
            return
        
        # Save to the same file
        self.save_pdf_to_path(self.current_file)
    
    def save_pdf_as(self):
        """Save the current PDF to a new file."""
        if not self.current_file:
            QMessageBox.warning(self, "No File", "No PDF file is currently open.")
            return
        
        out_path, _ = QFileDialog.getSaveFileName(self, "Save PDF As", "", "PDF Files (*.pdf)")
        if out_path:
            self.save_pdf_to_path(out_path)
            # Update current file to the new path
            self.current_file = out_path
            self.add_recent_file(out_path)
            self.status_label.setText(f"Saved: {out_path}")
    
    def save_pdf_to_path(self, output_path: str):
        """Save the PDF with all modifications to the specified path."""
        try:
            writer = PikePDFWriter(self.current_file)
            
            # Get page order from thumbnail panel
            page_order = self.thumbnail_panel.get_page_order()
            
            # Gather current data from all pages
            current_pages_data = {}
            for page_num in range(self.pdf_loader.get_page_count()):
                if page_num in self.page_scenes:
                    current_pages_data[page_num] = self.get_elements_from_scene(self.page_scenes[page_num])
                elif page_num in self.page_elements:
                    # Use cached elements if page was visited but not currently loaded
                    current_pages_data[page_num] = self.page_elements[page_num]
                else:
                    # Page was never visited, no modifications
                    current_pages_data[page_num] = []
            
            # Save
            writer.save(output_path, current_pages_data, page_order)
            writer.close()
            
            QMessageBox.information(self, "Success", "PDF Saved Successfully!")
            self.status_label.setText(f"Saved: {output_path}")
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Failed to save PDF: {str(e)}")

    def export_pdf_dialog(self):
        if not self.current_file:
            return
            
        out_path, _ = QFileDialog.getSaveFileName(self, "Export PDF", "", "PDF Files (*.pdf)")
        if out_path:
            try:
                writer = PDFWriter(self.current_file, out_path)
                
                # Get page order from thumbnail panel
                page_order = self.thumbnail_panel.get_page_order()
                
                # Gather current data from scenes
                # We need to ensure all pages are loaded or at least we have their data.
                # If a page hasn't been loaded into a scene, we can't edit it easily with this approach.
                # But for MVP, we assume user visited pages or we only save visited pages?
                # Better: Iterate all pages. If scene exists, get from scene. If not, get from initial analysis?
                # Actually, if scene doesn't exist, it means no changes were made to that page (unless we support global changes).
                # So we can just pass empty list for those pages.
                
                current_pages_data = {}
                for page_num in range(self.pdf_loader.get_page_count()):
                    if page_num in self.page_scenes:
                        current_pages_data[page_num] = self.get_elements_from_scene(self.page_scenes[page_num])
                    else:
                        current_pages_data[page_num] = []
                
                # Save
                writer.save(current_pages_data, page_order)
                
                QMessageBox.information(self, "Success", "PDF Exported Successfully!")
            except Exception as e:
                import traceback
                traceback.print_exc()
                QMessageBox.critical(self, "Error", f"Failed to export PDF: {str(e)}")

    def get_elements_from_scene(self, scene):
        elements = []
        for item in scene.items():
            if item.zValue() == -100: continue # Skip background
            if not item.isVisible(): continue
            if isinstance(item, ResizerHandle): continue
            
            # Get geometry
            # We need the bounding rect in scene coordinates
            # But items might be transformed (rotated/scaled).
            # fitz expects simple rects or points.
            # For MVP, we handle position and scale (via bounding rect). Rotation is harder.
            
            # Get scene bounding rect
            scene_rect = item.sceneBoundingRect()
            x = scene_rect.x()
            y = scene_rect.y()
            w = scene_rect.width()
            h = scene_rect.height()
            
            if isinstance(item, QGraphicsTextItem):
                text = item.toPlainText()
                # Font size?
                # We need to estimate effective font size.
                # item.font().pointSize() * scale
                # Scale can be found from transform
                scale = item.transform().m11() # Approx
                font_size = item.font().pointSize() * scale
                
                elements.append({
                    'type': 'text',
                    'text': text,
                    'x': x,
                    'y': y,
                    'font_size': font_size
                })
                
            elif isinstance(item, QGraphicsPixmapItem):
                # We need the image data
                pixmap = item.pixmap()
                buffer = QBuffer()
                buffer.open(QIODevice.OpenModeFlag.ReadWrite)
                pixmap.save(buffer, "PNG")
                image_data = buffer.data().data() # bytes
                
                elements.append({
                    'type': 'image',
                    'image_data': image_data,
                    'x': x,
                    'y': y,
                    'w': w,
                    'h': h
                })
                
        return elements

    def open_pdf_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open PDF", "", "PDF Files (*.pdf)")
        if file_path:
            self.load_pdf(file_path)

    def load_pdf(self, file_path):
        try:
            if self.pdf_loader:
                self.pdf_loader.close()
                
            self.current_file = file_path
            self.pdf_loader = PDFLoader(file_path)
            self.layout_analyzer = LayoutAnalyzer(file_path)
            
            self.thumbnail_panel.clear()
            self.inspector_panel.clear()
            self.page_scenes = {} # Clear scenes
            self.page_elements = {}
            self.scene_cache_order = [] # Reset cache order
            
            # Load Thumbnails
            for i in range(self.pdf_loader.get_page_count()):
                pixmap = self.pdf_loader.get_page_pixmap(i, scale=0.2)
                self.thumbnail_panel.add_page(pixmap, i)
                
            # Load first page
            if self.pdf_loader.get_page_count() > 0:
                self.load_page(0)
                
            self.add_recent_file(file_path)
            self.status_label.setText(f"Loaded: {file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load PDF: {str(e)}")

    def save_scene_to_data(self, page_num):
        """Serialize scene data before evicting from cache."""
        if page_num in self.page_scenes:
            scene = self.page_scenes[page_num]
            self.page_elements[page_num] = self.get_elements_from_scene(scene)

    def load_page(self, page_num):
        if not self.pdf_loader:
            return
            
        # Check if we already have a scene for this page
        if page_num in self.page_scenes:
            # Move to end (mark as recently used)
            if page_num in self.scene_cache_order:
                self.scene_cache_order.remove(page_num)
            self.scene_cache_order.append(page_num)
            
            self.canvas.set_scene(self.page_scenes[page_num])
            self.populate_inspector_from_scene(self.page_scenes[page_num])
            return

        # Check if cache is full - evict LRU page if needed
        if len(self.page_scenes) >= self.MAX_CACHED_SCENES:
            lru_page = self.scene_cache_order.pop(0)
            self.save_scene_to_data(lru_page)
            del self.page_scenes[lru_page]

        # Create new scene
        scene = EditorScene(self.canvas)
        self.page_scenes[page_num] = scene
        self.scene_cache_order.append(page_num)
        self.canvas.set_scene(scene)
        
        # Connect selection signal
        scene.selectionChanged.connect(self.sync_selection_to_inspector)
            
        # Render Page Background
        pixmap = self.pdf_loader.get_page_pixmap(page_num, scale=1.5)
        bg_item = QGraphicsPixmapItem(pixmap)
        bg_item.setZValue(-100)
        bg_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
        bg_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        bg_item.setOpacity(0.5)
        scene.addItem(bg_item)
        scene.setSceneRect(QRectF(pixmap.rect()))
        self.canvas.current_page_item = bg_item # Keep ref
        
        # Update inspector slider
        self.inspector_panel.set_background_opacity_value(0.5)
        
        # Get page height for coordinate conversion
        _, page_height = self.pdf_loader.get_page_size(page_num)
        
        # Check if we have saved element data (previously visited page)
        if page_num in self.page_elements and self.page_elements[page_num]:
            # Restore from saved data
            elements = self.page_elements[page_num]
        else:
            # First visit - analyze layout
            elements = self.layout_analyzer.analyze_page(page_num)
            self.page_elements[page_num] = elements
        
        # Add elements to canvas
        for i, el in enumerate(elements):
                # Convert coordinates using utility
                scale = 1.5
                qt_x, qt_y, w, h = CoordinateConverter.pdf_rect_to_qt_rect(
                    el['bbox'], page_height, scale=scale
                )
                
                x = qt_x
                y = qt_y
                
                item = None
                if el.get('type') == 'text':
                    text_content = el.get('text', '').strip()
                    if text_content:
                        font_size = el.get('font_size', 12) * scale
                        item = EditableTextItem(text_content)
                        item.setPos(x, y)
                        font = item.font()
                        font.setPointSize(int(font_size))
                        item.setFont(font)
                        scene.addItem(item)
                elif el.get('type') == 'image':
                    bbox = el['bbox']
                    try:
                        img_pixmap = self.pdf_loader.get_image_from_rect(page_num, bbox, scale=2.0)
                        item = ResizablePixmapItem(img_pixmap)
                        curr_w = img_pixmap.width()
                        curr_h = img_pixmap.height()
                        target_w = w
                        target_h = h
                        item.setPos(x, y)
                        transform = QTransform()
                        transform.scale(target_w / curr_w, target_h / curr_h)
                        item.setTransform(transform)
                        scene.addItem(item)
                    except Exception as e:
                        print(f"Failed to extract image: {e}")
                        item = QGraphicsRectItem(x, y, w, h)
                        item.setPen(QPen(Qt.GlobalColor.blue))
                        item.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsMovable | QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
                        scene.addItem(item)
                else:
                    # Add generic rect for other elements
                    item = QGraphicsRectItem(x, y, w, h)
                    item.setPen(QPen(Qt.GlobalColor.darkGreen))
                    item.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsMovable | QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
                    scene.addItem(item)
                
                if item:
                    # Store original element data in item
                    item.setData(Qt.ItemDataRole.UserRole, el)
                    item.setData(Qt.ItemDataRole.UserRole + 2, i) # Original Index

        self.populate_inspector_from_scene(scene)

    def populate_inspector_from_scene(self, scene):
        self.inspector_panel.clear()
        # We need to reconstruct the tree from scene items
        # This is a bit reverse of what we did before, but necessary for persistence.
        
        # Create root
        root = QTreeWidgetItem(self.inspector_panel.tree)
        root.setText(0, "Page Content")
        root.setExpanded(True)
        
        for item in scene.items():
            if item.zValue() == -100: continue # Skip background
            if isinstance(item, QGraphicsRectItem) and item.rect().width() == 8: continue # Skip handles (hacky check)
            # Better: check type
            if isinstance(item, ResizerHandle): continue

            tree_item = QTreeWidgetItem(root)
            
            # Try to get original element data
            el = item.data(Qt.ItemDataRole.UserRole)
            
            if isinstance(item, QGraphicsTextItem):
                text = item.toPlainText()
                tree_item.setText(0, text[:20])
                tree_item.setText(1, "text")
            elif isinstance(item, QGraphicsPixmapItem):
                tree_item.setText(0, "Image")
                tree_item.setText(1, "image")
            else:
                tree_item.setText(0, "Element")
                tree_item.setText(1, "rect")
                
            tree_item.setCheckState(2, Qt.CheckState.Checked if item.isVisible() else Qt.CheckState.Unchecked)
            tree_item.setText(3, str(item.opacity()))
            tree_item.setFlags(tree_item.flags() | Qt.ItemFlag.ItemIsEditable)
            
            # Link back
            tree_item.setData(0, Qt.ItemDataRole.UserRole + 1, item)

    def _link_item_to_inspector(self, index, graphics_item):
        # Deprecated by populate_inspector_from_scene
        pass

    def on_inspector_item_changed(self, item, column):
        # Handle visibility change (Column 2)
        if column == 2:
            visible = item.checkState(2) == Qt.CheckState.Checked
            graphics_item = item.data(0, Qt.ItemDataRole.UserRole + 1)
            if graphics_item:
                graphics_item.setVisible(visible)
        # Handle Opacity change (Column 3)
        elif column == 3:
            try:
                opacity = float(item.text(3))
                graphics_item = item.data(0, Qt.ItemDataRole.UserRole + 1)
                if graphics_item:
                    graphics_item.setOpacity(opacity)
            except ValueError:
                pass # Invalid float
                pass # Invalid float

    def insert_text(self):
        # Add text to center of current view
        # We need to find a good position.
        # For now, just add at (100, 100)
        item = self.canvas.add_text_element("New Text", 100, 100)
        
        # Add to inspector
        # We need to create a dummy element dict for it
        el = {'type': 'text', 'text': 'New Text', 'font_size': 12}
        
        # Add to tree
        root = self.inspector_panel.tree.topLevelItem(0)
        if root:
            tree_item = QTreeWidgetItem(root)
            tree_item.setText(0, "New Text")
            tree_item.setText(1, "text")
            tree_item.setCheckState(2, Qt.CheckState.Checked)
            tree_item.setText(3, "1.0")
            tree_item.setFlags(tree_item.flags() | Qt.ItemFlag.ItemIsEditable)
            tree_item.setData(0, Qt.ItemDataRole.UserRole, el)
            tree_item.setData(0, Qt.ItemDataRole.UserRole + 1, item)

    def insert_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Insert Image", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            pixmap = QPixmap(file_path)
            if pixmap.isNull():
                QMessageBox.warning(self, "Error", "Failed to load image.")
                return
                
            # Add to canvas
            # Scale down if too big
            if pixmap.width() > 500:
                pixmap = pixmap.scaledToWidth(500, Qt.TransformationMode.SmoothTransformation)
                
            item = ResizablePixmapItem(pixmap)
            item.setPos(100, 100)
            self.canvas.scene.addItem(item)
            
            # Add to inspector (simplified)
            self.populate_inspector_from_scene(self.canvas.scene)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if not file_path:
                    continue
                    
                ext = os.path.splitext(file_path)[1].lower()
                
                if ext == '.pdf':
                    self.load_pdf(file_path)
                    # Only load the first PDF if multiple dropped
                    break
                    
                elif ext in ['.png', '.jpg', '.jpeg', '.bmp']:
                    # Add image to current canvas
                    if self.canvas and self.canvas.scene:
                        # We want to drop at the mouse position
                        # Map global mouse pos to scene pos
                        # But dropEvent gives us pos in widget coords
                        
                        # Convert drop position to scene coordinates
                        # self.canvas is the view.
                        # We need to map from MainWindow coords to Canvas coords
                        
                        canvas_pos = self.canvas.mapFrom(self, event.position().toPoint())
                        scene_pos = self.canvas.mapToScene(canvas_pos)
                        
                        self.add_image_to_canvas(file_path, scene_pos.x(), scene_pos.y())
                        
    def add_image_to_canvas(self, file_path, x, y):
        pixmap = QPixmap(file_path)
        if pixmap.isNull():
            return
            
        # Scale down if too big
        if pixmap.width() > 500:
            pixmap = pixmap.scaledToWidth(500, Qt.TransformationMode.SmoothTransformation)
            
        item = ResizablePixmapItem(pixmap)
        item.setPos(x, y)
        self.canvas.scene.addItem(item)
        
        # Update inspector
        self.populate_inspector_from_scene(self.canvas.scene)