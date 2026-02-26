"""
PageManagerMixin — gestión de páginas, escenas y caché LRU.

Extraído de MainWindow para mantener una sola responsabilidad por archivo.
Se usa como mixin: class MainWindow(QMainWindow, ..., PageManagerMixin, ...)
"""

from qt_compat import (QGraphicsPixmapItem, QGraphicsItem, QGraphicsRectItem,
                       QPen, QTransform, QPixmap, Qt, QRectF, QSettings)
from utils.geometry import CoordinateConverter
import os


class PageManagerMixin:
    """Mixin que añade a MainWindow la gestión de páginas del PDF y la caché de escenas."""

    # ------------------------------------------------------------------
    # Window title
    # ------------------------------------------------------------------

    def update_window_title(self):
        """Update window title based on project state."""
        if self.current_project_file:
            project_name = os.path.basename(self.current_project_file)
            modified_marker = "*" if self.is_modified else ""
            self.setWindowTitle(f"{project_name}{modified_marker} - PDF Visual Editor")
        elif self.source_pdf_path:
            self.setWindowTitle("Untitled* - PDF Visual Editor")
        else:
            self.setWindowTitle("PDF Visual Editor")

    # ------------------------------------------------------------------
    # Scene cache helpers
    # ------------------------------------------------------------------

    def save_scene_to_data(self, page_num):
        """Serialize scene data before evicting from cache."""
        if page_num in self.page_scenes:
            scene = self.page_scenes[page_num]
            self.page_elements[page_num] = self.get_elements_from_scene(scene)

    # ------------------------------------------------------------------
    # Load page (standard — from PDF analysis or cache)
    # ------------------------------------------------------------------

    def load_page(self, page_num):
        if not self.pdf_loader:
            return

        # Check if we already have a scene for this page
        if page_num in self.page_scenes:
            if page_num in self.scene_cache_order:
                self.scene_cache_order.remove(page_num)
            self.scene_cache_order.append(page_num)

            self.canvas.set_scene(self.page_scenes[page_num])
            self.populate_inspector_from_scene(self.page_scenes[page_num])
            return

        # Check if cache is full — evict LRU page if needed
        if len(self.page_scenes) >= self.MAX_CACHED_SCENES:
            lru_page = self.scene_cache_order.pop(0)
            self.save_scene_to_data(lru_page)
            del self.page_scenes[lru_page]

        # Lazy import to avoid circular imports
        from .editor_canvas import (EditorScene, EditableTextItem,
                                    ResizablePixmapItem, ResizerHandle)

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
        self.canvas.current_page_item = bg_item  # Keep ref

        # Update inspector slider
        self.inspector_panel.set_background_opacity_value(0.5)

        # Get page height for coordinate conversion
        _, page_height = self.pdf_loader.get_page_size(page_num)

        # Check if we have saved element data (previously visited page)
        if page_num in self.page_elements and self.page_elements[page_num]:
            elements = self.page_elements[page_num]
        else:
            elements = self.layout_analyzer.analyze_page(page_num)
            self.page_elements[page_num] = elements

        # Add elements to canvas
        for i, el in enumerate(elements):
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
                    item.setPos(x, y)
                    transform = QTransform()
                    transform.scale(w / curr_w, h / curr_h)
                    item.setTransform(transform)
                    scene.addItem(item)
                except Exception as e:
                    print(f"Failed to extract image: {e}")
                    item = QGraphicsRectItem(x, y, w, h)
                    item.setPen(QPen(Qt.GlobalColor.blue))
                    item.setFlags(
                        QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
                        QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
                    )
                    scene.addItem(item)
            else:
                item = QGraphicsRectItem(x, y, w, h)
                item.setPen(QPen(Qt.GlobalColor.darkGreen))
                item.setFlags(
                    QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
                    QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
                )
                scene.addItem(item)

            if item:
                item.setData(Qt.ItemDataRole.UserRole, el)
                item.setData(Qt.ItemDataRole.UserRole + 2, i)  # Original Index

        self.populate_inspector_from_scene_auto(scene)

    # ------------------------------------------------------------------
    # Load page from .omar project (preserves structure)
    # ------------------------------------------------------------------

    def load_page_from_project(self, page_num, project_data):
        """Load a page with data from project file (no auto-organization)."""
        if not self.pdf_loader:
            return

        from .editor_canvas import EditorScene

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

        # Populate inspector
        self.populate_inspector_from_scene_auto(scene)

    # ------------------------------------------------------------------
    # Restore serialized elements into a scene
    # ------------------------------------------------------------------

    def _restore_elements_to_scene(self, scene, elements_data):
        """Restore graphics items from serialized element data."""
        from .editor_canvas import EditableTextItem, ResizablePixmapItem
        import base64

        for element_data in elements_data:
            item = None
            element_type = element_data.get("type")

            if element_type == "text":
                text = element_data.get("text", "")
                item = EditableTextItem(text)

                font = item.font()
                font.setFamily(element_data.get("font_family", "Arial"))
                font.setPointSize(int(element_data.get("font_size", 12)))
                font.setBold(element_data.get("font_bold", False))
                font.setItalic(element_data.get("font_italic", False))
                item.setFont(font)

            elif element_type == "image":
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
                width = element_data.get("width", 100)
                height = element_data.get("height", 100)
                item = QGraphicsRectItem(0, 0, width, height)
                item.setPen(QPen(Qt.GlobalColor.blue))
                item.setFlags(
                    QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
                    QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
                )

            if item:
                pos_x = element_data.get("x", 0)
                pos_y = element_data.get("y", 0)
                item.setPos(pos_x, pos_y)

                transform_matrix = element_data.get("transform_matrix", [1, 0, 0, 1, 0, 0])
                if len(transform_matrix) == 6:
                    transform = QTransform(
                        transform_matrix[0], transform_matrix[1],
                        transform_matrix[2], transform_matrix[3],
                        transform_matrix[4], transform_matrix[5]
                    )
                    item.setTransform(transform)

                item.setOpacity(element_data.get("opacity", 1.0))
                item.setVisible(element_data.get("visible", True))
                item.setZValue(element_data.get("z_value", 0))

                scene.addItem(item)
