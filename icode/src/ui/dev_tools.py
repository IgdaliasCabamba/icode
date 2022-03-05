from PyQt5.QtWidgets import (QFrame, QListWidget, QVBoxLayout, QPushButton,
                             QLabel, QTextEdit, QHBoxLayout, QListWidget,
                             QStackedLayout, QFormLayout, QLineEdit, QComboBox)

from PyQt5.QtCore import Qt, pyqtSignal, QThread, QObject
from PyQt5.QtGui import QColor
from pathlib import Path
from .igui import ScrollLabel, IListWidgetItem
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
        self.is_showing = False
        self.parent.btn_add_label.clicked.connect(self.go_screen_new)
        self.parent.btn_show_hide_labels.clicked.connect(self.show_hide_all)
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
        if self.file_name is not None:
            labels = labels_cache.get_all_from_list(self.file_name)
            if isinstance(labels, list):
                for label in labels:
                    self.add_todo(label["line"], label["title"], label["desc"], label["label"])

    def add_todo(self, line, text, tooltip, type):
        self.layout.setCurrentWidget(self.display)
        
        title = text
        color_text = QColor("white")
        if type == "bug":
            color_text = QColor("red")
            title = "\uf188"+" "+text
            
        elif type == "todo":
            title = "\uf0ae"+" "+text
            color_text = QColor("blue")
        
        item = IListWidgetItem(None, title, tooltip, {"line": line, "note":tooltip, "label":type})
        item.setForeground(color_text)
            
        self.display.addItem(item)

    def go_screen_new(self):
        self.layout.setCurrentWidget(self.screen_new)

    def new_todo(self):
        desc = self.input_desc.toPlainText()
        line = self.input_line.text()
        title = self.input_title.text()
        label = self.label_picker.currentText().lower()

        labels_cache.save_to_list({
            "line":line,
            "desc": desc,
            "title": title,
            "label": label
        }, self.file_name)
        
        self.update_data()

    def set_data(self, editor: object, file_name: str):
        if file_name is not None:
            self.file_name = str(file_name).replace(system.SYS_SEP, "_")
        else:
            self.file_name = file_name
        
        self.editor = editor
        self.update_data()

    def goto_annotation_line(self, row):
        try:
            item = self.display.item(row)
            if hasattr(item, "item_data"):
                line = int(item.item_data["line"])
                note = item.item_data["note"]
                label = item.item_data["label"]
                if label.lower() == "todo":
                    text = "\uf0ae TODO: "
                    style = 210
                elif label.lower() == "bug":
                    text = "\uf188 ISSUE: "
                    style = 202
                else:
                    text = "\uf249 NOTE: "
                    style = 206
                if hasattr(self.editor, "editor"):
                    self.editor.editor.go_to_line(line)
                    self.editor.editor.display_annotation(line, text+note, style, "on_text_changed", 0)
                        
        except Exception as e:
            print(e)
            
    def show_hide_all(self):
        try:
            if self.is_showing:
                self.is_showing = False
            else:
                if hasattr(self.editor, "editor"):
                    labels = labels_cache.get_all_from_list(self.file_name)        
                    if isinstance(labels, list):
                        for label in labels:    
                            if label["label"].lower() == "todo":
                                text = "\uf0ae TODO: "
                                style = 210
                            elif label["label"].lower() == "bug":
                                text = "\uf188 ISSUE: "
                                style = 202
                            else:
                                text = "\uf249 NOTE: "
                                style = 206
                                
                            self.editor.editor.display_annotation(int(label["line"]), text+label["desc"], style, "on_text_changed", 0)
                                
                self.is_showing = True
        except Exception as e:
            print(e)