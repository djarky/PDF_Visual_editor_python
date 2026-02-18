import pygame

class Signal:
    def __init__(self, *args): 
        self._slots = []
        self._blocked = False
    def connect(self, slot): (self._slots.append(slot) if slot not in self._slots else None)
    def disconnect(self, slot): (self._slots.remove(slot) if slot in self._slots else None)
    def emit(self, *args): 
        if self._blocked: return
        for slot in self._slots:
            try:
                slot(*args)
            except TypeError:
                # Fallback: try calling without arguments if calling with args failed
                if args:
                    try:
                        slot()
                        continue
                    except TypeError:
                        pass
                # Fallback: if we had no args but it expects one, try False 
                # (Common for Qt's triggered(bool) signals)
                if not args:
                    try:
                        slot(False)
                        continue
                    except TypeError:
                        pass
                raise

class QObject:
    def __init__(self, parent=None):
        self._parent, self._children = parent, []
        self._signals_blocked = False
        if parent and hasattr(parent, '_children'):
            if self not in parent._children:
                parent._children.append(self)
    def parent(self): return self._parent
    def children(self): return self._children
    def blockSignals(self, b):
        old = self._signals_blocked
        self._signals_blocked = b
        # Apply to all Signals belonging to this object
        for attr in self.__dict__.values():
            if isinstance(attr, Signal):
                attr._blocked = b
        return old
    def signalsBlocked(self): return self._signals_blocked
    def isVisible(self): return getattr(self, '_visible', False)
    def show(self): self.setVisible(True)
    def hide(self): self.setVisible(False)
    def setVisible(self, v): self._visible = v
    def _handle_event(self, event, offset):
        for child in self._children:
            child._handle_event(event, offset)
    def _handle_drop_event(self, event, offset):
        """Default drop event handler for QObjects"""
        for child in self._children:
            if hasattr(child, '_handle_drop_event'):
                if child._handle_drop_event(event, offset):
                    return True
        return False
    def _draw_recursive(self, pos=pygame.Vector2(0,0)):
        if self.isVisible():
            for child in self._children:
                if hasattr(child, '_draw_recursive'):
                    child._draw_recursive(pos)
    def update(self): pass

def pyqtSignal(*args): return Signal(*args)
