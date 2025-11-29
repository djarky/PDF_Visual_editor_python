
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
from pdf_loader import PDFLoader
from layout_analyzer import LayoutAnalyzer
from export.pdf_writer import PDFWriter
from export.pikepdf_writer import PikePDFWriter
from omar_format import OmarFormat
from utils.geometry import CoordinateConverter
from gui.commands import AddItemCommand, DeleteItemCommand, EditTextCommand
import os

class MainWindow(QMainWindow):
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
        self.menu_bar.action_theme_light.triggered.connect(lambda: self.toggle_theme("light"))
        self.menu_bar.action_theme_dark.triggered.connect(lambda: self.toggle_theme("dark"))
        
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

    def load_recent_files(self):
        settings = QSettings("Antigravity", "PDFVisualEditor")
        self.recent_files = settings.value("recent_files", [], type=list)
        self.update_recent_menu()

    def add_recent_file(self, file_path):
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
        self.recent_files.insert(0, file_path)
        self.recent_files = self.recent_files[:10] # Keep last 10
        
        settings = QSettings("Antigravity", "PDFVisualEditor")
        settings.setValue("recent_files", self.recent_files)
        self.update_recent_menu()

    def update_recent_menu(self):
        self.menu_bar.menu_recent.clear()
        for path in self.recent_files:
            action = self.menu_bar.menu_recent.addAction(path)
            action.triggered.connect(lambda checked, p=path: self.load_file(p))
            
    def load_file(self, file_path):
        """Smart load method that routes to correct loader based on extension."""
        if file_path.lower().endswith('.omar'):
            self.load_project(file_path)
        else:
            self.load_pdf(file_path)
    
    def load_theme_preference(self):
        """Load saved theme preference."""
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
    
    def on_canvas_changed(self):
        """Called when canvas scene changes (e.g., paste, delete, capture)."""
        # Refresh the inspector to show updated elements
        if self.canvas and self.canvas.scene:
            self.populate_inspector_from_scene_auto(self.canvas.scene)

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

    def duplicate_items(self, items):
        """Duplicate the specified graphics items."""
        if not self.canvas or not self.canvas.scene:
            return
            
        # Block signals to prevent full inspector rebuild (preserves custom folders)
        self.canvas.blockSignals(True)
        
        new_items = []
        offset = 20
        
        try:
            for item in items:
                new_item = None
                
                if isinstance(item, QGraphicsTextItem):
                    new_item = EditableTextItem(item.toPlainText())
                    new_item.setFont(item.font())
                    new_item.setDefaultTextColor(item.defaultTextColor())
                elif isinstance(item, QGraphicsPixmapItem):
                    new_item = ResizablePixmapItem(item.pixmap())
                elif isinstance(item, QGraphicsRectItem):
                    new_item = QGraphicsRectItem(item.rect())
                    new_item.setPen(item.pen())
                    new_item.setBrush(item.brush())
                    new_item.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsMovable | 
                                     QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
                
                if new_item:
                    # Copy common properties
                    new_item.setPos(item.pos() + QPointF(offset, offset))
                    new_item.setTransform(item.transform())
                    new_item.setRotation(item.rotation())
                    new_item.setScale(item.scale())
                    new_item.setOpacity(item.opacity())
                    new_item.setZValue(item.zValue() + 0.1)
                    new_item.setVisible(item.isVisible())
                    
                    self.canvas.scene.addItem(new_item)
                    new_items.append(new_item)
                    
                    # Manually add to inspector
                    self.inspector_panel.add_graphics_item(new_item)
            
            # Update selection
            if new_items:
                self.canvas.scene.clearSelection()
                for item in new_items:
                    item.setSelected(True)
                    
        finally:
            self.canvas.blockSignals(False)
            # We do NOT call populate_inspector_from_scene_auto here to preserve structure

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
        
        # Recursive search for items
        def select_recursive(parent_item):
            for i in range(parent_item.childCount()):
                child = parent_item.child(i)
                graphics_item = child.data(0, Qt.ItemDataRole.UserRole + 1)
                if graphics_item in selected_items:
                    child.setSelected(True)
                    # Ensure visible
                    self.inspector_panel.tree.scrollToItem(child)
                
                # Recurse
                select_recursive(child)

        root = self.inspector_panel.tree.invisibleRootItem()
        select_recursive(root)
                    
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
        
    def toggle_history_panel(self, checked):
        self.undo_view.setVisible(checked)
    
    def save_project(self):
        """Save the current project to .omar file."""
        if not self.pdf_loader:
            QMessageBox.warning(self, "No Project", "No project is currently open.")
            return
        
        if self.current_project_file:
            # Save to existing project file
            self.save_project_to_path(self.current_project_file)
        else:
            # No project file yet, prompt for location
            self.save_project_as()
    
    def save_project_as(self):
        """Save the current project to a new .omar file."""
        if not self.pdf_loader:
            QMessageBox.warning(self, "No Project", "No project is currently open.")
            return
        
        # Suggest filesystem based on source PDF
        suggested_name = ""
        if self.source_pdf_path:
            base_name = os.path.splitext(os.path.basename(self.source_pdf_path))[0]
            suggested_name = base_name + ".omar"
        
        out_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Save Project As", 
            suggested_name,
            "OMAR Project Files (*.omar)"
        )
        
        if out_path:
            # Ensure .omar extension
            if not out_path.endswith('.omar'):
                out_path += '.omar'
            
            self.save_project_to_path(out_path)
            self.current_project_file = out_path
            self.is_modified = False
            self.add_recent_file(out_path)
            self.update_window_title()
            self.status_label.setText(f"Saved: {out_path}")
    
    def save_project_to_path(self, output_path: str):
        """Save the project with all modifications to the specified .omar file."""
        try:
            # Gather all project data
            project_data = self.gather_project_data()
            
            # Save using OmarFormat
            OmarFormat.save_project(output_path, project_data)
            
            self.is_modified = False
            self.update_window_title()
            QMessageBox.information(self, "Success", "Project Saved Successfully!")
            self.status_label.setText(f"Saved: {output_path}")
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Failed to save project: {str(e)}")
    
    def gather_project_data(self):
        """Gather all data needed for .omar file."""
        pages_data = []
        
        # Process each page
        for page_num in range(self.pdf_loader.get_page_count()):
            page_data = {
                "page_num": page_num,
                "background_opacity": 0.5,  # Default
                "elements": [],
                "inspector_tree": None
            }
            
            # Get elements from scene if page was visited
            if page_num in self.page_scenes:
                scene = self.page_scenes[page_num]
                page_data["elements"] = self._serialize_scene_elements(scene)
                # Get inspector tree structure
                page_data["inspector_tree"] = self.inspector_panel.serialize_tree_structure()
            elif page_num in self.page_elements:
                # Use cached elements
                page_data["elements"] = self.page_elements[page_num]
            
            pages_data.append(page_data)
        
        # Get page order from thumbnail panel
        page_order = self.thumbnail_panel.get_page_order()
        
        return {
            "source_pdf": {
                "path": self.source_pdf_path or self.current_file,
                "embedded": False,
                "data": None
           },
            "settings": {
                "theme": self.current_theme,
                "current_page": 0  
            },
            "pages": pages_data,
            "page_order": page_order
        }
    
    def _serialize_scene_elements(self, scene):
        """Serialize all elements in a scene."""
        from .editor_canvas import ResizerHandle
        
        elements = []
        for item in scene.items():
            if item.zValue() == -100: continue  # Skip background
            if isinstance(item, ResizerHandle): continue
            
            element_data = OmarFormat.serialize_graphics_item(item)
            if element_data:
                elements.append(element_data)
        
        return elements

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
        """Open file dialog supporting both .omar projects and .pdf files."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Open File", 
            "", 
            "All Supported Files (*.omar *.pdf);;OMAR Projects (*.omar);;PDF Files (*.pdf)"
        )
        if file_path:
            self.load_file(file_path)

    def load_pdf(self, file_path):
        try:
            if self.pdf_loader:
                self.pdf_loader.close()
                
            self.current_file = file_path
            self.source_pdf_path = file_path  # Store as source for .omar project
            self.current_project_file = None  # New PDF = unsaved project
            self.is_modified = False
            
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
            self.update_window_title()
            self.status_label.setText(f"Loaded: {file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load PDF: {str(e)}")
    
    def update_window_title(self):
        """Update window title based on project state."""
        if self.current_project_file:
            # Show .omar project name
            project_name = os.path.basename(self.current_project_file)
            modified_marker = "*" if self.is_modified else ""
            self.setWindowTitle(f"{project_name}{modified_marker} - PDF Visual Editor")
        elif self.source_pdf_path:
            # Unsaved project from PDF
            self.setWindowTitle("Untitled* - PDF Visual Editor")
        else:
            # No project
            self.setWindowTitle("PDF Visual Editor")
    
    def load_project(self, filepath: str):
        """Load a .omar project file."""
        try:
            # Validate this is actually a .omar file
            if not filepath.lower().endswith('.omar'):
                QMessageBox.warning(self, "Invalid File", "Please select a .omar project file.")
                return
            
            # Load project data
            project_data = OmarFormat.load_project(filepath)
            
            # Get source PDF path
            source_pdf = project_data.get("source_pdf", {})
            pdf_path = source_pdf.get("path", "")
            
            # Validate PDF path
            if not pdf_path:
                QMessageBox.warning(
                    self, 
                    "Invalid Project", 
                    "Project file does not contain a valid PDF path."
                )
                return
            
            # Check if PDF exists
            if not os.path.exists(pdf_path):
                response = QMessageBox.question(
                    self, 
                    "PDF Not Found", 
                    f"Source PDF not found:\n{pdf_path}\n\nWould you like to locate it?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if response == QMessageBox.StandardButton.Yes:
                    # Let user browse for PDF
                    new_pdf_path, _ = QFileDialog.getOpenFileName(
                        self, 
                        "Locate Source PDF", 
                        os.path.dirname(pdf_path) if os.path.dirname(pdf_path) else "",
                        "PDF Files (*.pdf)"
                    )
                    if new_pdf_path:
                        pdf_path = new_pdf_path
                    else:
                        return
                else:
                    return
            
            # Load the source PDF first
            if self.pdf_loader:
                self.pdf_loader.close()
            
            self.source_pdf_path = pdf_path
            self.current_file = pdf_path
            self.current_project_file = filepath
            self.is_modified = False
            
            self.pdf_loader = PDFLoader(pdf_path)
            self.layout_analyzer = LayoutAnalyzer(pdf_path)
            
            # Clear UI
            self.thumbnail_panel.clear()
            self.inspector_panel.clear()
            self.page_scenes = {}
            self.page_elements = {}
            self.scene_cache_order = []
            
            # Load thumbnails
            for i in range(self.pdf_loader.get_page_count()):
                pixmap = self.pdf_loader.get_page_pixmap(i, scale=0.2)
                self.thumbnail_panel.add_page(pixmap, i)
            
            # Restore pages data
            pages_data = project_data.get("pages", [])
            for page_data in pages_data:
                page_num = page_data.get("page_num", 0)
                self.page_elements[page_num] = page_data.get("elements", [])
            
            # Load first page
            if self.pdf_loader.get_page_count() > 0:
                self.load_page_from_project(0, project_data)
            
            # Restore settings
            settings = project_data.get("settings", {})
            theme = settings.get("theme", "light")
            if theme != self.current_theme:
                self.apply_theme(theme)
            
            self.add_recent_file(filepath)
            self.update_window_title()
            self.status_label.setText(f"Loaded project: {filepath}")
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print("="*80)
            print("ERROR LOADING .OMAR PROJECT:")
            print(error_details)
            print("="*80)
            QMessageBox.critical(self, "Error", f"Failed to load project:\n\n{str(e)}\n\nCheck console for details.")
    
    def load_page_from_project(self, page_num, project_data):
        """Load a page with data from project file (no auto-organization)."""
        if not self.pdf_loader:
            return
        
        # Create new scene
        scene = EditorScene(self.canvas, undo_stack=self.undo_stack)
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
        
        # Restore background opacity
        pages_data = project_data.get("pages", [])
        bg_opacity = 0.5  # default
        for page_data in pages_data:
            if page_data.get("page_num") == page_num:
                bg_opacity = page_data.get("background_opacity", 0.5)
                break
        
        bg_item.setOpacity(bg_opacity)
        scene.addItem(bg_item)
        scene.setSceneRect(QRectF(pixmap.rect()))
        self.canvas.current_page_item = bg_item
        
        # Update inspector slider
        self.inspector_panel.set_background_opacity_value(bg_opacity)
        
        # Restore elements from project data
        if page_num in self.page_elements:
            self._restore_elements_to_scene(scene, self.page_elements[page_num])
        
        # Populate inspector (will use saved structure if available)
        # For now, use auto-organize - full structure restoration can be added later
        self.populate_inspector_from_scene_auto(scene)
    
    def _restore_elements_to_scene(self, scene, elements_data):
        """Restore graphics items from serialized element data."""
        from .editor_canvas import EditableTextItem, ResizablePixmapItem
        import base64
        
        for element_data in elements_data:
            item = None
            element_type = element_data.get("type")
            
            if element_type == "text":
                # Restore text item
                text = element_data.get("text", "")
                item = EditableTextItem(text)
                
                # Restore font
                font = item.font()
                font.setFamily(element_data.get("font_family", "Arial"))
                font.setPointSize(int(element_data.get("font_size", 12)))
                font.setBold(element_data.get("font_bold", False))
                font.setItalic(element_data.get("font_italic", False))
                item.setFont(font)
                
            elif element_type == "image":
                # Restore image item
                image_data_b64 = element_data.get("image_data", "")
                if image_data_b64:
                    try:
                        image_bytes = base64.b64decode(image_data_b64)
                        pixmap = QPixmap()
                        pixmap.loadFromData(image_bytes)
                        item = ResizablePixmapItem(pixmap)
                    except Exception as e:
                        print(f"Failed to restore image: {e}")
                        continue
            
            elif element_type == "shape":
                # Restore shape/rect
                width = element_data.get("width", 100)
                height = element_data.get("height", 100)
                item = QGraphicsRectItem(0, 0, width, height)
                item.setPen(QPen(Qt.GlobalColor.blue))
                item.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsMovable | 
                             QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
            
            if item:
                # Restore common properties
                pos_x = element_data.get("x", 0)
                pos_y = element_data.get("y", 0)
                item.setPos(pos_x, pos_y)
                
                # Restore transform
                transform_matrix = element_data.get("transform_matrix", [1, 0, 0, 1, 0, 0])
                if len(transform_matrix) == 6:
                    transform = QTransform(
                        transform_matrix[0], transform_matrix[1],
                        transform_matrix[2], transform_matrix[3],
                        transform_matrix[4], transform_matrix[5]
                    )
                    item.setTransform(transform)
                
                # Restore opacity and visibility
                item.setOpacity(element_data.get("opacity", 1.0))
                item.setVisible(element_data.get("visible", True))
                item.setZValue(element_data.get("z_value", 0))
                
                scene.addItem(item)

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
        scene = EditorScene(self.canvas, undo_stack=self.undo_stack)
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


        self.populate_inspector_from_scene_auto(scene)

    def populate_inspector_from_scene_auto(self, scene):
        """Populate inspector with auto-organization (for PDF imports)."""
        self.inspector_panel.populate_from_scene_auto_organize(scene)

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
            
            if self.undo_stack:
                from gui.commands import AddItemCommand
                cmd = AddItemCommand(self.canvas.scene, item, "Insert Image")
                self.undo_stack.push(cmd)
            else:
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
        
        if self.undo_stack:
            from gui.commands import AddItemCommand
            cmd = AddItemCommand(self.canvas.scene, item, "Drop Image")
            self.undo_stack.push(cmd)
        else:
            self.canvas.scene.addItem(item)
        
        # Update inspector
        self.populate_inspector_from_scene(self.canvas.scene)