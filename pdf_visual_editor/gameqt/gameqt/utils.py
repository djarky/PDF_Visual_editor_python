import os
from .core import QObject, Signal
from .gui import QPixmap, QImage
from .widgets import QWidget

class QUndoStack(QObject):
    def __init__(self, parent=None): 
        super().__init__(parent)
        self._stack = []
        self._index = -1
    def push(self, cmd): 
        # Remove any commands after current index
        self._stack = self._stack[:self._index + 1]
        self._stack.append(cmd)
        self._index += 1
        cmd.redo()
    def undo(self): 
        if self._index >= 0:
            self._stack[self._index].undo()
            self._index -= 1
    def redo(self): 
        if self._index < len(self._stack) - 1:
            self._index += 1
            self._stack[self._index].redo()
    def beginMacro(self, text): 
        # Start a macro command (group of commands)
        self._macro_text = text
        self._macro_commands = []
        self._in_macro = True
    def endMacro(self): 
        # End the current macro and push as single command
        if hasattr(self, '_in_macro') and self._in_macro:
            macro_cmd = QUndoCommand(self._macro_text)
            macro_cmd._child_commands = self._macro_commands
            self.push(macro_cmd)
            self._in_macro = False

class QUndoCommand:
    def __init__(self, text=""): 
        self._text = text
        self._child_commands = []
    def redo(self): 
        # Override in subclasses to perform the action
        for cmd in self._child_commands:
            cmd.redo()
    def undo(self): 
        # Override in subclasses to undo the action
        for cmd in reversed(self._child_commands):
            cmd.undo()
    def text(self): 
        return self._text

class QSettings(QObject):
    def __init__(self, organization="GameQt", application="Editor"):
        super().__init__()
        self._path = os.path.expanduser(f"~/.{organization}_{application}.json")
        self._cache = {}
        if os.path.exists(self._path):
            try:
                import json
                with open(self._path, 'r') as f: self._cache = json.load(f)
            except: pass
    def value(self, key, default=None, type=None):
        val = self._cache.get(key, default)
        return val
    def setValue(self, key, val):
        self._cache[key] = val
        try:
            import json
            with open(self._path, 'w') as f: json.dump(self._cache, f)
        except: pass

# QFileDialog and QMessageBox are provided by widgets.py for interactive use.

class QBuffer:
    def __init__(self):
        self._data = bytearray()
        self._pos = 0
    def open(self, m): 
        self._pos = 0
        return True
    def data(self): 
        return bytes(self._data)
    def write(self, data):
        self._data.extend(data)
    def setData(self, data):
        self._data = bytearray(data)

class QIODevice:
    class OpenModeFlag: ReadWrite = 1


class QModelIndex:
    def __init__(self, row=-1, column=-1, internalPointer=None, model=None):
        self._row, self._col, self._ptr, self._model = row, column, internalPointer, model
    def row(self): return self._row
    def column(self): return self._col
    def internalPointer(self): return self._ptr
    def isValid(self): return self._row != -1 and self._col != -1
    def model(self): return self._model

class QPrinter:
    class OutputFormat: PdfFormat = 0; NativeFormat = 1
    def __init__(self):
        self._output_format = QPrinter.OutputFormat.PdfFormat
        self._output_filename = "output.pdf"
    def setOutputFormat(self, f): self._output_format = f
    def setOutputFileName(self, name): self._output_filename = name
    def outputFileName(self): return self._output_filename

class QDrag:
    def __init__(self, parent): 
        self._parent = parent
        self._mime_data = None
    def setMimeData(self, data):
        self._mime_data = data
    def setPixmap(self, pixmap):
        self._pixmap = pixmap
    def setHotSpot(self, hotspot):
        self._hotspot = hotspot
    def exec(self, *args): 
        from .application import QApplication
        app = QApplication.instance()
        if app:
            return app.startDrag(self)
        return 0

from .widgets import QWidget
class QUndoView(QWidget):
    def __init__(self, stack=None, parent=None): 
        super().__init__(parent)
        self._stack = stack
