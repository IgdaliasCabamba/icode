from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
)

from core.storer import CacheManager
from core.templates import *
from smartlibs.pyqtreactor import *
from functions import getfn

icons = getfn.get_smartcode_icons("index")


class QuickActions(QFrame):

    on_new_clicked = pyqtSignal()
    on_open_file_clicked = pyqtSignal()
    on_open_folder_clicked = pyqtSignal()
    on_show_commands_clicked = pyqtSignal()

    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.setObjectName("quick-actions-panel")
        self.parent = parent
        self.template = IndexRender()

        self.index_events = {
            "#new": self.on_new_clicked,
            "#open-file": self.on_open_file_clicked,
            "#open-folder": self.on_open_folder_clicked,
            "#show-commands": self.on_show_commands_clicked,
        }
        self.init_ui()

    def init_ui(self) -> None:
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setText(self.template.hello_code)
        self.layout.addWidget(self.label)
        self.label.linkActivated.connect(self.option_clicked)

    def option_clicked(self, link):
        try:
            self.index_events[link].emit()
        except KeyError:
            pass


class Index(QFrame):

    on_double_clicked = pyqtSignal()

    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.setObjectName("index")
        self.parent = parent
        self.template = IndexRender()
        self.init_ui()

    def init_ui(self) -> None:
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel(self)
        self.label.setMinimumSize(100, 100)
        self.label.setStyleSheet(self.template.logo)
        self.actions = QuickActions(self)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.actions)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.setFocus()

    def mouseDoubleClickEvent(self, event):
        super().mouseDoubleClickEvent(event)
        self.on_double_clicked.emit()


class WelcomeActions(QFrame):

    on_open_recent_folder = pyqtSignal(str)
    on_new_clicked = pyqtSignal()
    on_open_file_clicked = pyqtSignal()
    on_open_folder_clicked = pyqtSignal()
    on_show_commands_clicked = pyqtSignal()

    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.setObjectName("quick-actions-panel")
        self.parent = parent
        self.template = IndexRender()
        self.init_ui()

        self.index_events = {
            "#new": self.on_new_clicked,
            "#open-file": self.on_open_file_clicked,
            "#open-folder": self.on_open_folder_clicked,
            "#show-commands": self.on_show_commands_clicked,
        }

    def init_ui(self) -> None:
        self.layout = QHBoxLayout(self)
        self.setLayout(self.layout)
        self.layout.setContentsMargins(5, 0, 5, 0)

        self.side_left = QLabel(self)
        self.side_left.setWordWrap(True)
        self.side_left.setAlignment(Qt.AlignLeft)
        self.side_left.setText(self.template.recent_paths)
        self.side_left.setMinimumSize(100, 100)

        self.side_right = QLabel(self)
        self.side_right.setWordWrap(True)
        self.side_right.setAlignment(Qt.AlignLeft)
        self.side_right.setText(self.template.dev_utils)
        self.side_right.setMinimumSize(100, 100)

        self.layout.addWidget(self.side_left)
        self.layout.addWidget(self.side_right)
        self.layout.setAlignment(self.side_left, Qt.AlignLeft | Qt.AlignCenter)
        self.layout.setAlignment(self.side_right,
                                 Qt.AlignRight | Qt.AlignCenter)

        self.side_left.linkActivated.connect(self.option_clicked)

    def option_clicked(self, link):
        if link in self.index_events.keys():
            self.index_events[link].emit()
        else:
            if pathlib.Path(link).is_dir() and pathlib.Path(link).exists:
                self.on_open_recent_folder.emit(link)

    def rebuild(self, paths: list = []):
        self.template.set_paths(paths)
        self.side_left.setText(self.template.recent_paths)


class Welcome(QFrame):

    def __init__(self, parent, folders: list = []) -> None:
        super().__init__(parent)
        self.setObjectName("welcome")
        self.parent = parent
        self.setMouseTracking(True)
        self.folders = folders
        self.icode_message_api = RRequest(self)
        self.init_ui()

    def init_ui(self) -> None:
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)
        self.layout.setContentsMargins(90, 90, 90, 10)
        self.setMinimumSize(100, 100)

        self.actions = WelcomeActions(self)

        self.main_link = QLabel(self)
        self.main_link.setText(
            "<small><a href='icode.com'>icode.io</a></small>")
        self.main_link.setAlignment(Qt.AlignCenter)

        self.show_on_start = QCheckBox("Show welcome page on startup", self)
        self.show_on_start.setChecked(True)

        self.layout.addWidget(self.actions)
        self.layout.addWidget(self.main_link)
        self.layout.addWidget(self.show_on_start)
        self.layout.setAlignment(self.show_on_start, Qt.AlignCenter)
        self.icode_message_api.get_raw(
            "http://igdaliascabamba.github.io/get-icode/api/welcome.html",
            self.show_welcome_message,
        )

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.setFocus()

    def set_last_folders(self, folders: list):
        self.folders = folders
        self.actions.rebuild(self.folders)

    def show_welcome_message(self, text):
        self.main_link.setText(text)
