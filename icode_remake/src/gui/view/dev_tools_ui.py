from PyQt5.QtWidgets import (
    QFrame,
    QListWidget,
    QVBoxLayout,
    QPushButton,
    QTextEdit,
    QListWidget,
    QStackedLayout,
    QFormLayout,
    QLineEdit,
    QComboBox,
)

from PyQt5.QtGui import QColor
from .igui import IListWidgetItem
from core.char_utils import get_unicon
from core.code_api import icode_api


class NotesUi(QFrame):
    def __init__(self, parent):
        super().__init__()
        self.setObjectName("ilabs-notes")
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(2, 2, 2, 2)
        self.setLayout(self.layout)

        self.text_editor = QTextEdit(self)
        self.text_editor.setAcceptRichText(True)
        self.text_editor.setPlaceholderText(
            "Make your notes here, they are automatically saved"
        )
        self.layout.addWidget(self.text_editor)


class TodosUi(QFrame):
    def __init__(self, parent):
        super().__init__()
        self.setObjectName("ilabs-notes")
        self.parent = parent
        self.parent.btn_add_label.clicked.connect(self.go_screen_new)
        self.init_ui()

    def init_ui(self):
        self.layout = QStackedLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.screen_new = QFrame(self)
        self.input_title = QLineEdit(self)
        self.input_desc = QTextEdit(self)
        self.input_desc.setPlaceholderText("Enter description here")
        self.input_line = QLineEdit(self)
        self.label_picker = QComboBox(self)
        self.btn_save = QPushButton("Save", self)
        self.label_picker.addItems(["Bug", "Todo", "Note"])

        self.form_layout = QFormLayout(self.screen_new)
        self.screen_new.setLayout(self.form_layout)

        self.form_layout.addRow("Title:", self.input_title)
        self.form_layout.addRow("Line:", self.input_line)
        self.form_layout.addRow("Label:", self.label_picker)
        self.form_layout.addRow("Desc:", self.input_desc)
        self.form_layout.addRow("", self.btn_save)

        self.display = QListWidget(self)
        self.layout.addWidget(self.display)
        self.layout.addWidget(self.screen_new)

    def go_screen_new(self):
        self.layout.setCurrentWidget(self.screen_new)

    def add_todo(self, line, text, tooltip, type):
        self.layout.setCurrentWidget(self.display)

        title = text
        color_text = QColor(icode_api.get_lexers_frontend()["Label"]["fg"])
        if type == "bug":
            color_text = QColor(icode_api.get_lexers_frontend()["Bug"]["fg"])
            title = f"{get_unicon('nf', 'fa-bug')} {text}"

        elif type == "todo":
            color_text = QColor(icode_api.get_lexers_frontend()["Todo"]["fg"])
            title = f"{get_unicon('nf', 'fa-tasks')} {text}"

        item = IListWidgetItem(
            None, title, tooltip, {"line": line, "note": tooltip, "label": type}
        )
        item.setForeground(color_text)

        self.display.addItem(item)
