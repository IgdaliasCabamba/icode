from PyQt5.QtWidgets import (QFrame, QListWidget, QVBoxLayout, QPushButton,
                             QLabel, QTextEdit, QHBoxLayout, QListWidget,
                             QStackedLayout, QFormLayout, QLineEdit, QComboBox)

from PyQt5.QtCore import Qt, pyqtSignal, QThread, QObject
from PyQt5.QtGui import QColor
from pathlib import Path
from ..igui import ScrollLabel, IListWidgetItem
from base import memory, system
from data import note_file_path, labels_cache


class NotesCore(QObject):
    def __init__(self, editor):
        super().__init__()
        self.parent = editor
        self.editor = editor.text_editor

    def run(self):
        self.editor.textChanged.connect(self.save_data)

    def save_data(self):
        self.parent.file.write_text(self.editor.toPlainText())


class Notes(QFrame):
    def __init__(self, parent):
        super().__init__()
        self.setObjectName("ilabs-notes")
        self.parent = parent
        self.file = Path(note_file_path)
        self.build()

    def build(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(2, 2, 2, 2)
        self.setLayout(self.layout)

        self.text_editor = QTextEdit(self)
        self.thread_text = QThread(self)
        self.text_object = NotesCore(self)
        self.text_object.moveToThread(self.thread_text)
        self.thread_text.started.connect(self.run_tasks)
        self.thread_text.start()

        self.text_editor.setAcceptRichText(True)
        self.text_editor.setPlaceholderText(
            "Make your notes here, they are automatically saved")

        self.layout.addWidget(self.text_editor)

        if self.file.exists():
            self.text_editor.setText(self.file.read_text())
        else:
            file = open(self.file, "w")
            file.close()

    def run_tasks(self):
        self.text_object.run()


class Todos(QFrame):
    def __init__(self, parent):
        super().__init__()
        self.setObjectName("ilabs-notes")
        self.parent = parent
        self.file_name = None
        self.editor = None
        self.parent.btn_add_label.clicked.connect(self.go_screen_new)
        self.build()

    def build(self):
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
        self.display.currentRowChanged.connect(self.goto_annotation_line)
        self.layout.addWidget(self.display)
        self.layout.addWidget(self.screen_new)

        self.btn_save.clicked.connect(self.new_todo)
        self.update_data()

    def update_data(self):
        self.display.clear()
        labels_cache.beginGroup(self.file_name)
        keys = labels_cache.childKeys()
        for x in keys:
            label = labels_cache.value(x)
            self.add_todo(label["line"], label["title"], label["desc"], label["label"])
        labels_cache.endGroup()

    def add_todo(self, line, text, tooltip, type):
        self.layout.setCurrentWidget(self.display)
        
        title = text
        if type == "bug":
            color_text = QColor("red")
            title = "\uf188"+" "+text
            
        elif type == "todo":
            title = "\uf0ae"+" "+text
            color_text = QColor("blue")
        
        item = IListWidgetItem(None, title, tooltip, {"line": line})
        item.setForeground(color_text)
            
        self.display.addItem(item)

    def go_screen_new(self):
        self.layout.setCurrentWidget(self.screen_new)

    def new_todo(self):
        desc = self.input_desc.toPlainText()
        line = self.input_line.text()
        title = self.input_title.text()
        label = self.label_picker.currentText().lower()
        self.add_todo(line, title, desc, label)

        labels_cache.beginGroup(self.file_name)
        labels_cache.setValue(line, {
            "line":line,
            "desc": desc,
            "title": title,
            "label": label
        })
        labels_cache.endGroup()

    def set_data(self, editor: object, file_name: str):
        self.file_name = file_name.replace(system.SYS_SEP, "_")
        self.editor = editor
        self.update_data()

    def goto_annotation_line(self, row):
        item = self.display.item(row)
        if hasattr(item, "item_data"):
            line = int(item.item_data["line"])
            self.editor.editor.go_to_line(line)
            
