from PyQt5.QtCore import QObject, pyqtSignal
import pickle


class IDocument(QObject):

    on_changed = pyqtSignal(dict)

    def __init__(self, editor) -> None:
        super().__init__()
        self.editor = editor
        self.lexer_name = "none"
        self.lexer = None
        self.file = None
        self.first_line_text = ""
        self.name = None
        self.file_name = None
        self.tooltip = None
        self.icon = None

    def set_data(self, data: dict) -> None:
        if "lexer_name" in data.keys():
            self.lexer_name = data["lexer_name"]

        if "name" in data.keys():
            self.name = data["name"]

        if "lexer" in data:
            self.lexer = data["lexer"]

        if "tooltip" in data:
            self.tooltip = data["tooltip"]

        if "icon" in data:
            self.icon = data["icon"]

        if "file" in data:
            self.file = data["file"]

        if "file_name" in data:
            self.file_name = data["file_name"]

        if "first_line" in data:
            self.first_line_text = data["first_line"]

        self.on_changed.emit(self.get_all_data())

    def set_first_line_text(self, title):
        self.first_line_text = title
        self.on_changed.emit(self.get_all_data())

    def set_lexer(self, lexer: object) -> None:
        self.lexer = lexer
        self.on_changed.emit(self.get_all_data())

    def set_lexer_name(self, lexer_name: str) -> None:
        self.lexer_name = lexer_name
        self.on_changed.emit(self.get_all_data())

    def set_file(self, file) -> None:
        self.file = file
        self.on_changed.emit(self.get_all_data())

    def set_file_name(self, file_name) -> None:
        self.file_name = file_name
        self.on_changed.emit(self.get_all_data())

    def set_name(self, name: str) -> None:
        self.name = name
        self.on_changed.emit(self.get_all_data())

    def set_tooltip(self, tooltip: str) -> None:
        self.tooltip = tooltip
        self.on_changed.emit(self.get_all_data())

    def set_icon(self, icon: object) -> None:
        self.icon = icon
        self.on_changed.emit(self.get_all_data())

    def get_all_data(self) -> dict:
        return {
            "editor": self.editor,
            "lexer_name": self.lexer_name,
            "lexer": self.lexer,
            "file": self.file,
            "name": self.name,
            "file_name": self.file_name,
            "tooltip": self.tooltip,
            "icon": self.icon,
            "first_line": self.first_line_text,
        }

    def save_data(self):
        pass
