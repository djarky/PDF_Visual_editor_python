"""
EditableTextItem — editable text element with resize handles.
"""

from qt_compat import (QGraphicsTextItem, QGraphicsItem, Qt, QPen, QColor)
from .resizable_mixin import ResizableMixin


class EditableTextItem(QGraphicsTextItem, ResizableMixin):
    def __init__(self, text, parent=None):
        QGraphicsTextItem.__init__(self, text, parent)
        ResizableMixin.__init__(self)
        self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
                      QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
                      QGraphicsItem.GraphicsItemFlag.ItemIsFocusable)
        self.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        self.is_editing = False

    def mouseDoubleClickEvent(self, event):
        if self.textInteractionFlags() == Qt.TextInteractionFlag.NoTextInteraction:
            self.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
            self.setFocus()
            self.is_editing = True
            self.old_text = self.toPlainText()  # Capture old text
            self.setDefaultTextColor(QColor(0, 0, 0))
            cursor = self.textCursor()
            cursor.select(cursor.SelectionType.Document)
            self.setTextCursor(cursor)
            self.update()
        super().mouseDoubleClickEvent(event)

    def focusOutEvent(self, event):
        if self.is_editing:
            self.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
            self.is_editing = False
            cursor = self.textCursor()
            cursor.clearSelection()
            self.setTextCursor(cursor)
            self.update()

            # Check for changes and push undo command
            new_text = self.toPlainText()
            if hasattr(self, 'old_text') and self.old_text != new_text:
                scene = self.scene()
                if scene and hasattr(scene, 'undo_stack') and scene.undo_stack:
                    from gui.commands import EditTextCommand
                    cmd = EditTextCommand(self, self.old_text, new_text)
                    scene.undo_stack.push(cmd)

        super().focusOutEvent(event)

    def keyPressEvent(self, event):
        if self.textInteractionFlags() & Qt.TextInteractionFlag.TextEditorInteraction:
            super().keyPressEvent(event)
        else:
            event.ignore()

    def paint(self, painter, option, widget):
        if self.is_editing:
            painter.save()
            pen = QPen(QColor(0, 120, 215), 2, Qt.PenStyle.SolidLine)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(self.boundingRect().adjusted(1, 1, -1, -1))
            painter.restore()
        super().paint(painter, option, widget)
