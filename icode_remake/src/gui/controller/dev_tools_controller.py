from PyQt5.QtCore import Qt, pyqtSignal, QThread, QObject
from data import note_file_path, labels_cache
import pathlib
from core import system
from core.char_utils import get_unicon


class NotesCore(QObject):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.editor = parent.view.text_editor

    def run(self):
        self.editor.textChanged.connect(self.save_data)

    def save_data(self):
        self.parent.file.write_text(self.editor.toPlainText())


class NotesController(QObject):
    def __init__(self, application_core, view):
        super().__init__()
        self.application_core = application_core
        self.view = view

        self.file = pathlib.Path(note_file_path)

        self.thread_text = QThread(self)
        self.text_object = NotesCore(self)
        self.text_object.moveToThread(self.thread_text)
        self.thread_text.started.connect(self.run_tasks)
        self.thread_text.start()

        if self.file.exists():
            self.view.text_editor.setText(self.file.read_text())
        else:
            file = open(self.file, "w")
            file.close()

    def run_tasks(self):
        self.text_object.run()


class TodosController(QObject):
    def __init__(self, application_core, view):
        super().__init__()
        self.application_core = application_core
        self.view = view

        self.file_name = None
        self.editor = None
        self.is_showing = False

        self.view.display.currentRowChanged.connect(self.goto_annotation_line)
        self.view.parent.btn_show_hide_labels.clicked.connect(self.show_hide_all)
        self.view.btn_save.clicked.connect(self.new_todo)

        self.update_data()

    def update_data(self):
        self.view.display.clear()
        if self.file_name is not None:
            labels = labels_cache.get_all_from_list(self.file_name)
            if isinstance(labels, list):
                for label in labels:
                    self.view.add_todo(
                        label["line"], label["title"], label["desc"], label["label"]
                    )

    def new_todo(self):
        desc = self.view.input_desc.toPlainText()
        line = self.view.input_line.text()
        title = self.view.input_title.text()
        label = self.view.label_picker.currentText().lower()

        labels_cache.save_to_list(
            {"line": line, "desc": desc, "title": title, "label": label}, self.file_name
        )

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
            item = self.view.display.item(row)
            if hasattr(item, "item_data"):
                line = int(item.item_data["line"])
                note = item.item_data["note"]
                label = item.item_data["label"]
                if label.lower() == "todo":
                    text = f"{get_unicon('nf', 'fa-tasks')} TODO: "
                    style = 210
                elif label.lower() == "bug":
                    text = f"{get_unicon('nf', 'fa-bug')} ISSUE: "
                    style = 202
                else:
                    text = f"{get_unicon('nf', 'fa-sticky_note')} NOTE: "
                    style = 206
                if hasattr(self.editor, "editor"):
                    self.editor.editor.go_to_line(line)
                    self.editor.editor.display_annotation(
                        line, text + note, style, "on_text_changed", 0
                    )

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
                                text = f"{get_unicon('nf', 'fa-tasks')} TODO: "
                                style = 210
                            elif label["label"].lower() == "bug":
                                text = f"{get_unicon('nf', 'fa-bug')} ISSUE: "
                                style = 202
                            else:
                                text = f"{get_unicon('nf', 'fa-sticky_note')} NOTE: "
                                style = 206

                            self.editor.editor.display_annotation(
                                int(label["line"]),
                                text + label["desc"],
                                style,
                                "on_text_changed",
                                0,
                            )

                self.is_showing = True
        except Exception as e:
            print(e)
