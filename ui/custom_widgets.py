from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtCore import Qt


class MessageInput(QTextEdit):
    """Custom text input box, Enter key sends message, Ctrl+Enter adds a line break"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

    def keyPressEvent(self, event):
        # Check if Enter key is pressed
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            # Check if Ctrl key is also pressed
            if event.modifiers() & Qt.ControlModifier:
                # Ctrl+Enter adds a line break
                super().keyPressEvent(event)
            else:
                # Enter alone sends the message
                if self.parent:
                    self.parent.send_message()
        else:
            # Process other keys normally
            super().keyPressEvent(event)