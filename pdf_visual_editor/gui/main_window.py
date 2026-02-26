
from qt_compat import (QMainWindow, QSplitter, QWidget, QVBoxLayout, QFileDialog, 
                       QMessageBox, QLabel, QTreeWidgetItem, QGraphicsPixmapItem, 
                       QGraphicsItem, QGraphicsRectItem, QGraphicsTextItem, QPixmap, 
                       QTransform, QPen, QColor, QBrush, QUndoStack, Qt, QRectF, 
                       QBuffer, QIODevice, QSettings, QUndoView, QPointF)
from .editor_canvas import EditorCanvas, EditorScene, EditableTextItem, ResizablePixmapItem, ResizerHandle
from .thumbnail_panel import ThumbnailPanel
from .inspector_panel import InspectorPanel
from .menus import AppMenu
from .about_dialog import AboutDialog
from .project_io import ProjectIOMixin
from .page_manager import PageManagerMixin
from .inspector_sync import InspectorSyncMixin
from gui.commands import AddItemCommand, DeleteItemCommand, EditTextCommand
import os
import sys

class MainWindow(QMainWindow, ProjectIOMixin, PageManagerMixin, InspectorSyncMixin):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Visual Editor")
        self.resize(1200, 800)
        
        # State
        self.current_file = None  # Source PDF path or None
        self.current_project_file = None  # Path to .omar file or None
        self.source_pdf_path = None  # Original PDF for .omar projects
        self.is_modified = False  # Track unsaved changes
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
        self.menu_bar.action_save.triggered.connect(self.save_project)
        self.menu_bar.action_save_as.triggered.connect(self.save_project_as)
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
        # Connect Theme Actions
        self.menu_bar.action_theme_light.triggered.connect(lambda: self.toggle_theme("light"))
        self.menu_bar.action_theme_dark.triggered.connect(lambda: self.toggle_theme("dark"))
        self.menu_bar.action_theme_system.triggered.connect(lambda: self.toggle_theme("system"))
        
        # Connect Help Actions
        self.menu_bar.action_about.triggered.connect(self.show_about_dialog)
        
        # Connect View Actions
        self.menu_bar.action_history.toggled.connect(self.toggle_history_panel)
        
        # Main Layout
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.setCentralWidget(main_splitter)
        
        # Left: Editor Canvas
        self.canvas = EditorCanvas(undo_stack=self.undo_stack)
        self.canvas.sceneChanged.connect(self.on_canvas_changed)
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
        
        # History Panel
        self.undo_view = QUndoView(self.undo_stack)
        self.undo_view.setWindowTitle("History")
        self.undo_view.hide() # Hidden by default
        right_splitter.addWidget(self.undo_view)
        
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
        self.inspector_panel.duplicateRequested.connect(self.duplicate_items)
        self.canvas.joinRequested.connect(self.inspector_panel.join_items)
        
        # We also need to connect the canvas selection changed signal.
        # But the scene is created dynamically in load_page.
        # We will connect it there.
        
        # Recent Files
        self.recent_files = []
        self.load_recent_files()

    # ------------------------------------------------------------------
    # Theme
    # ------------------------------------------------------------------

    def load_theme_preference(self):
        """Load saved theme preference."""
        settings = QSettings("Antigravity", "PDFVisualEditor")
        self.current_theme = settings.value("theme", "light", type=str)
        self.apply_theme(self.current_theme)
    
    def apply_theme(self, theme_name: str):
        """Apply a theme by loading its stylesheet."""
        if theme_name == "system":
            self.setStyleSheet("")
            self.current_theme = "system"
            
            # Save preference
            settings = QSettings("Antigravity", "PDFVisualEditor")
            settings.setValue("theme", "system")
            return

        if getattr(sys, 'frozen', False):
            base_dir = sys._MEIPASS
        else:
            base_dir = os.path.join(os.path.dirname(__file__), os.path.pardir)
            
        theme_file = os.path.join(base_dir, "themes", f"{theme_name}_theme.qss")
        try:
            with open(theme_file, 'r') as f:
                stylesheet = f.read()
                self.setStyleSheet(stylesheet)
                self.current_theme = theme_name
                
                # Save preference
                settings = QSettings("Antigravity", "PDFVisualEditor")
                settings.setValue("theme", theme_name)
        except FileNotFoundError:
            print(f"Theme file not found: {theme_file}")
    
    def toggle_theme(self, theme_name: str):
        """Toggle to a specific theme."""
        self.apply_theme(theme_name)

    # ------------------------------------------------------------------
    # Misc UI actions
    # ------------------------------------------------------------------

    def show_about_dialog(self):
        """Show the About dialog."""
        dialog = AboutDialog(self)
        dialog.exec()
    
    def on_canvas_changed(self):
        """Called when canvas scene changes (e.g., paste, delete, capture)."""
        # Refresh the inspector to show updated elements
        if self.canvas and self.canvas.scene:
            self.populate_inspector_from_scene_auto(self.canvas.scene)

    def toggle_capture_mode(self):
        self.canvas.start_capture_mode()
        self.status_label.setText("Capture Mode: Draw a rectangle to capture area.")
        
    def toggle_history_panel(self, checked):
        self.undo_view.setVisible(checked)

    # ------------------------------------------------------------------
    # Insert elements
    # ------------------------------------------------------------------

    def insert_text(self):
        # Add text to center of current view
        item = self.canvas.add_text_element("New Text", 100, 100)
        
        # Add to inspector
        el = {'type': 'text', 'text': 'New Text', 'font_size': 12}
        
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
                
            # Scale down if too big
            if pixmap.width() > 500:
                pixmap = pixmap.scaledToWidth(500, Qt.TransformationMode.SmoothTransformation)
                
            item = ResizablePixmapItem(pixmap)
            item.setPos(100, 100)
            
            if self.undo_stack:
                from gui.commands import AddItemCommand
                cmd = AddItemCommand(self.canvas.scene, item, "Insert Image")
                self.undo_stack.push(cmd)
            else:
                self.canvas.scene.addItem(item)
            
            # Add to inspector (simplified)
            self.populate_inspector_from_scene(self.canvas.scene)

    # ------------------------------------------------------------------
    # Drag and Drop
    # ------------------------------------------------------------------

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
        
        if self.undo_stack:
            from gui.commands import AddItemCommand
            cmd = AddItemCommand(self.canvas.scene, item, "Drop Image")
            self.undo_stack.push(cmd)
        else:
            self.canvas.scene.addItem(item)
        
        # Update inspector
        self.populate_inspector_from_scene(self.canvas.scene)