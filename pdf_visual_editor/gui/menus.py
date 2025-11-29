from qt_compat import QMenuBar, QMenu, QAction

class AppMenu(QMenuBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # File Menu
        file_menu = self.addMenu("File")
        self.action_open = QAction("Open PDF...", self)
        self.action_save = QAction("Save", self)
        self.action_save.setShortcut("Ctrl+S")
        self.action_save_as = QAction("Save As...", self)
        self.action_save_as.setShortcut("Ctrl+Shift+S")
        self.menu_recent = self.addMenu("Open Recent") # Placeholder, will be populated by MainWindow
        file_menu.addMenu(self.menu_recent)
        self.action_export = QAction("Export PDF...", self)
        self.action_exit = QAction("Exit", self)
        file_menu.addAction(self.action_open)
        file_menu.addAction(self.action_save)
        file_menu.addAction(self.action_save_as)
        file_menu.addSeparator()
        file_menu.addAction(self.action_export)
        file_menu.addSeparator()
        file_menu.addAction(self.action_exit)
        
        # Edit Menu
        self.menu_edit = self.addMenu("Edit")
        self.action_undo = QAction("Undo", self)
        self.action_undo.setShortcut("Ctrl+Z")
        self.action_redo = QAction("Redo", self)
        self.action_redo.setShortcut("Ctrl+Y")
        self.action_copy = QAction("Copy", self)
        self.action_paste = QAction("Paste", self)
        self.menu_edit.addAction(self.action_undo)
        self.menu_edit.addAction(self.action_redo)
        self.menu_edit.addSeparator()
        self.menu_edit.addAction(self.action_copy)
        self.menu_edit.addAction(self.action_paste)
        
        # Insert Menu
        insert_menu = self.addMenu("Insert")
        self.action_insert_text = QAction("Insert Text", self)
        self.action_insert_image = QAction("Insert Image...", self)
        insert_menu.addAction(self.action_insert_text)
        insert_menu.addAction(self.action_insert_image)
        
        # View Menu
        view_menu = self.addMenu("View")
        self.action_zoom_in = QAction("Zoom In", self)
        self.action_zoom_out = QAction("Zoom Out", self)
        view_menu.addAction(self.action_zoom_in)
        view_menu.addAction(self.action_zoom_out)
        view_menu.addSeparator()
        self.action_history = QAction("History", self)
        self.action_history.setCheckable(True)
        self.action_history.setChecked(False)
        view_menu.addAction(self.action_history)
        view_menu.addSeparator()
        
        # Theme submenu
        theme_menu = view_menu.addMenu("Theme")
        self.action_theme_light = QAction("Light", self)
        self.action_theme_dark = QAction("Dark", self)
        theme_menu.addAction(self.action_theme_light)
        theme_menu.addAction(self.action_theme_dark)
        
        # Help Menu
        help_menu = self.addMenu("Help")
        self.action_about = QAction("About", self)
        help_menu.addAction(self.action_about)
