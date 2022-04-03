from PyQt5.QtCore import QObject, pyqtSignal, Qt, QSize
from PyQt5.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QListWidget,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QGraphicsDropShadowEffect,
    QLabel,
)
from ..igui import InputHistory

from functions import getfn


class GotoLine(QFrame):

    focus_out = pyqtSignal(object, object)

    def __init__(self, api, parent):
        super().__init__(parent)
        self.api = api
        self._parent = parent
        self.setParent(parent)
        self.setObjectName("editor-widget")
        self.init_ui()

    def init_ui(self):

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(self.layout)

        self.input_edit = InputHistory(self)
        self.input_edit.setPlaceholderText("Goto")
        self.input_edit.setObjectName("child")
        self.input_edit.returnPressed.connect(self.go_anywhere)
        self.input_edit.textChanged.connect(self.live_go_anywhere)

        self.info = QLabel(self)
        self.info.setWordWrap(False)
        self.info.setAlignment(Qt.AlignLeft)
        self.info.setObjectName("child")

        self.layout.addWidget(self.input_edit)
        self.layout.addWidget(self.info)

        self.display_cursor_info()

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        if self.focusWidget() not in self.findChildren(object, "child"):
            self.focus_out.emit(self, event)

    def display_cursor_info(self):
        if self.api.current_editor is not None:
            n_lines = self.api.current_editor.lines()
            current_line, current_char = self.api.current_editor.getCursorPosition()
            self.info.setText(
                f"""
            <small>Current Line: {current_line}, Character{current_char}. Type a line between 1 and {n_lines} to navigate to</small>
            """
            )

    def goto_anywhere(self, text):
        if text.startswith(":") and len(text) > 1:
            href = text.split(":")[1]
            try:
                line = int(href)
                log = self.goto_line(line)
                self.info.setText(log)

            except:
                editor = self.api.get_current_editor()
                if editor is not None:
                    editor.findFirst(href, True, False, True, True)

        elif text.startswith((">", "@", "!")):
            self.api.run_by_id(self, text)

        else:
            self.display_cursor_info()

    def live_go_anywhere(self, text):
        self.goto_anywhere(text)

    def go_anywhere(self):
        editor = self.api.get_current_editor()
        self.goto_anywhere(self.input_edit.text())
        if editor is not None:
            editor.setFocus()

    def goto_line(self, line):
        editor = self.api.get_current_editor()
        if editor is not None:
            n_lines = editor.lines()
            if line > n_lines:
                return f"<small style='color:yellow'>Select a line betwen 0 and {n_lines}<small>"
            editor.go_to_line(line - 1)
            return f"<small>Go to Line: {line}<small>"

    def run(self):
        self.input_edit.setFocus()
        self.input_edit.setText(":")
        self.setFixedHeight(60)
        self.display_cursor_info()
