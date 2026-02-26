"""
ProjectIOMixin — manejo de archivos de proyecto (.omar) y exportación de PDF.

Extraído de MainWindow para mantener una sola responsabilidad por archivo.
Se usa como mixin: class MainWindow(QMainWindow, ProjectIOMixin, ...)
"""

from qt_compat import (QFileDialog, QMessageBox, QBuffer, QIODevice,
                       QSettings, QGraphicsTextItem, QGraphicsPixmapItem)
from export.pdf_writer import PDFWriter
from export.pikepdf_writer import PikePDFWriter
from omar_format import OmarFormat
from pdf_loader import PDFLoader
from layout_analyzer import LayoutAnalyzer
import os


class ProjectIOMixin:
    """Mixin que añade a MainWindow la capacidad de guardar/cargar proyectos y PDFs."""

    # ------------------------------------------------------------------
    # Recent files
    # ------------------------------------------------------------------

    def load_recent_files(self):
        settings = QSettings("Antigravity", "PDFVisualEditor")
        self.recent_files = settings.value("recent_files", [], type=list)
        self.update_recent_menu()

    def add_recent_file(self, file_path):
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
        self.recent_files.insert(0, file_path)
        self.recent_files = self.recent_files[:10]  # Keep last 10

        settings = QSettings("Antigravity", "PDFVisualEditor")
        settings.setValue("recent_files", self.recent_files)
        self.update_recent_menu()

    def update_recent_menu(self):
        self.menu_bar.menu_recent.clear()
        for path in self.recent_files:
            action = self.menu_bar.menu_recent.addAction(path)
            action.triggered.connect(lambda checked, p=path: self.load_file(p))

    # ------------------------------------------------------------------
    # Smart loader
    # ------------------------------------------------------------------

    def load_file(self, file_path):
        """Smart load method that routes to correct loader based on extension."""
        if file_path.lower().endswith('.omar'):
            self.load_project(file_path)
        else:
            self.load_pdf(file_path)

    # ------------------------------------------------------------------
    # Open dialog
    # ------------------------------------------------------------------

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

    # ------------------------------------------------------------------
    # Load PDF
    # ------------------------------------------------------------------

    def load_pdf(self, file_path):
        try:
            if self.pdf_loader:
                self.pdf_loader.close()

            self.current_file = file_path
            self.source_pdf_path = file_path  # Store as source for .omar project
            self.current_project_file = None   # New PDF = unsaved project
            self.is_modified = False

            self.pdf_loader = PDFLoader(file_path)
            self.layout_analyzer = LayoutAnalyzer(file_path)

            self.thumbnail_panel.clear()
            self.inspector_panel.clear()
            self.page_scenes = {}       # Clear scenes
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

    # ------------------------------------------------------------------
    # Load .omar project
    # ------------------------------------------------------------------

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
            print("=" * 80)
            print("ERROR LOADING .OMAR PROJECT:")
            print(error_details)
            print("=" * 80)
            QMessageBox.critical(self, "Error", f"Failed to load project:\n\n{str(e)}\n\nCheck console for details.")

    # ------------------------------------------------------------------
    # Save project
    # ------------------------------------------------------------------

    def save_project(self):
        """Save the current project to .omar file."""
        if not self.pdf_loader:
            QMessageBox.warning(self, "No Project", "No project is currently open.")
            return

        if self.current_project_file:
            self.save_project_to_path(self.current_project_file)
        else:
            self.save_project_as()

    def save_project_as(self):
        """Save the current project to a new .omar file."""
        if not self.pdf_loader:
            QMessageBox.warning(self, "No Project", "No project is currently open.")
            return

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
            project_data = self.gather_project_data()
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

        for page_num in range(self.pdf_loader.get_page_count()):
            page_data = {
                "page_num": page_num,
                "background_opacity": 0.5,
                "elements": [],
                "inspector_tree": None
            }

            if page_num in self.page_scenes:
                scene = self.page_scenes[page_num]
                page_data["elements"] = self._serialize_scene_elements(scene)
                page_data["inspector_tree"] = self.inspector_panel.serialize_tree_structure()
            elif page_num in self.page_elements:
                page_data["elements"] = self.page_elements[page_num]

            pages_data.append(page_data)

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
            if item.zValue() == -100:
                continue  # Skip background
            if isinstance(item, ResizerHandle):
                continue

            element_data = OmarFormat.serialize_graphics_item(item)
            if element_data:
                elements.append(element_data)

        return elements

    # ------------------------------------------------------------------
    # Export PDF
    # ------------------------------------------------------------------

    def save_pdf_to_path(self, output_path: str):
        """Save the PDF with all modifications to the specified path."""
        try:
            writer = PikePDFWriter(self.current_file)

            page_order = self.thumbnail_panel.get_page_order()

            current_pages_data = {}
            for page_num in range(self.pdf_loader.get_page_count()):
                if page_num in self.page_scenes:
                    current_pages_data[page_num] = self.get_elements_from_scene(self.page_scenes[page_num])
                elif page_num in self.page_elements:
                    current_pages_data[page_num] = self.page_elements[page_num]
                else:
                    current_pages_data[page_num] = []

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

                page_order = self.thumbnail_panel.get_page_order()

                current_pages_data = {}
                for page_num in range(self.pdf_loader.get_page_count()):
                    if page_num in self.page_scenes:
                        current_pages_data[page_num] = self.get_elements_from_scene(self.page_scenes[page_num])
                    else:
                        current_pages_data[page_num] = []

                writer.save(current_pages_data, page_order)

                QMessageBox.information(self, "Success", "PDF Exported Successfully!")
            except Exception as e:
                import traceback
                traceback.print_exc()
                QMessageBox.critical(self, "Error", f"Failed to export PDF: {str(e)}")

    def get_elements_from_scene(self, scene):
        """Extract serializable element dicts from a scene (for PDF export)."""
        from .editor_canvas import ResizerHandle

        elements = []
        for item in scene.items():
            if item.zValue() == -100:
                continue  # Skip background
            if not item.isVisible():
                continue
            if isinstance(item, ResizerHandle):
                continue

            scene_rect = item.sceneBoundingRect()
            x = scene_rect.x()
            y = scene_rect.y()
            w = scene_rect.width()
            h = scene_rect.height()

            if isinstance(item, QGraphicsTextItem):
                text = item.toPlainText()
                scale = item.transform().m11()
                font_size = item.font().pointSize() * scale

                elements.append({
                    'type': 'text',
                    'text': text,
                    'x': x,
                    'y': y,
                    'font_size': font_size
                })

            elif isinstance(item, QGraphicsPixmapItem):
                pixmap = item.pixmap()
                buffer = QBuffer()
                buffer.open(QIODevice.OpenModeFlag.ReadWrite)
                pixmap.save(buffer, "PNG")
                image_data = buffer.data().data()

                elements.append({
                    'type': 'image',
                    'image_data': image_data,
                    'x': x,
                    'y': y,
                    'w': w,
                    'h': h
                })

        return elements
