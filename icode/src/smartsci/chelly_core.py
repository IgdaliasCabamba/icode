from PyQt5.QtCore import QObject, Qt, pyqtSignal, QThread

from PyQt5.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QPushButton,
    QVBoxLayout,
    QSplitter,
    QFileDialog,
    QGraphicsDropShadowEffect,
    QSizePolicy,
    QWidget,
    QMenu,
    QAction,
)

from PyQt5.Qsci import *
from PyQt5.QtGui import QColor
from pathlib import Path
from .codesmart import Editor, EditorBase
from .codesmart_map import MiniMapPanel
from .codesmart_core import IFile
from functions import filefn, getfn
from . import iconsts, get_unicon
import settings
import mimetypes
from binaryornot.check import is_binary


class BreadcrumbController(QObject):
    on_update_header = pyqtSignal(dict)

    def __init__(self, parent, editor):
        super().__init__()
        self.parent = parent
        self.editor = editor

    def run(self):
        self.make_headers()
        self.editor.on_text_changed.connect(self.text_changed)
        self.editor.on_saved.connect(self.editor_saved)
        self.editor.idocument.on_changed.connect(self.make_headers)

        self.parent.file_watcher.on_file_deleted.connect(self.file_deleted)
        self.parent.file_watcher.on_file_modified.connect(self.file_modified)

    def make_headers(self):
        if self.editor.file_path is None:
            self.on_update_header.emit({
                "text": " Unsaved",
                "widget": "first",
                "last": False
            })
        else:
            widgets = ["second", "third", "fourth", "last"]
            path_levels = getfn.get_path_splited(self.editor.idocument.file)
            while len(path_levels) > len(widgets):
                path_levels.pop(0)

            i = 0
            for path in path_levels:
                if path.replace(" ", "") == "":
                    continue
                if i < len(widgets):
                    self.on_update_header.emit({
                        "text": f" {str(path)}",
                        "widget": widgets[i],
                        "last": False
                    })
                else:
                    self.on_update_header.emit({
                        "text": f" {str(self.editor.idocument.file_name)}",
                        "widget": widgets[i],
                        "last": True,
                    })
                    break
                i += 1
        self.on_update_header.emit({
            "widget": "first",
            "icon": self.editor.idocument.icon,
            "last": False
        })

    def file_deleted(self, file):
        self.on_update_header.emit({
            "text": "D",
            "widget": "info-file",
            "type": "red",
            "last": True
        })

    def file_modified(self, file):
        if filefn.read_file(file) != self.editor.text():
            self.on_update_header.emit({
                "text": "M",
                "widget": "info-file",
                "type": "red",
                "last": True
            })

    def text_changed(self):
        if self.editor.file_path is not None:
            self.on_update_header.emit({
                "text": "M",
                "widget": "info-file",
                "type": "orange",
                "last": True
            })
        else:
            self.on_update_header.emit({
                "text": "U",
                "widget": "info-file",
                "type": "orange",
                "last": True
            })

    def editor_saved(self):
        self.on_update_header.emit({
            "text": "S",
            "widget": "info-file",
            "type": "green",
            "last": True
        })


class Breadcrumbs(QFrame):

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.file_menu = FileMenu(self)
        self.file_menu.save_file.triggered.connect(self.parent.save_file)
        self.file_menu.reload_file.triggered.connect(self.parent.load_file)

        self.setObjectName("breadcrumbs")

        self.hbox = QHBoxLayout(self)
        self.hbox.setSpacing(0)
        self.setLayout(self.hbox)

        self.spacing = QWidget(self)
        self.spacing.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.breadcrumb0 = QPushButton(self)
        self.breadcrumb0.setVisible(False)

        self.breadcrumb1 = QPushButton(self)
        self.breadcrumb1.setVisible(False)

        self.breadcrumb2 = QPushButton(self)
        self.breadcrumb2.setVisible(False)

        self.breadcrumb3 = QPushButton(self)
        self.breadcrumb3.setVisible(False)

        self.breadcrumb4 = QPushButton(self)
        self.breadcrumb4.setVisible(False)

        self.breadcrumb00 = QPushButton(self)
        self.breadcrumb00.setVisible(False)

        self.breadcrumb01 = QPushButton(self)
        self.breadcrumb01.setVisible(False)

        self.breadcrumb02 = QPushButton(self)
        self.breadcrumb02.setVisible(False)

        self.breadcrumb03 = QPushButton(self)
        self.breadcrumb03.setVisible(False)

        self.file_info = QPushButton(self)
        self.file_info.setIcon(self.parent.icons.get_icon("file"))
        self.file_info.setMenu(self.file_menu)
        self.file_info.clicked.connect(lambda: self.file_info.showMenu())

        self.src_ctrl_info = QPushButton(self)
        self.src_ctrl_info.setIcon(
            self.parent.icons.get_icon("source_control"))

        self.warnings_info = QPushButton(self)
        self.warnings_info.setIcon(self.parent.icons.get_icon("warnings"))
        self.warnings_info.setStyleSheet("color:yelllow")

        self.errors_info = QPushButton(self)
        self.errors_info.setIcon(self.parent.icons.get_icon("errors"))
        self.errors_info.setStyleSheet("color:red")

        self.hbox.addWidget(self.breadcrumb0)
        self.hbox.addWidget(self.breadcrumb1)
        self.hbox.addWidget(self.breadcrumb2)
        self.hbox.addWidget(self.breadcrumb3)
        self.hbox.addWidget(self.breadcrumb4)
        self.hbox.addWidget(self.breadcrumb00)
        self.hbox.addWidget(self.breadcrumb01)
        self.hbox.addWidget(self.breadcrumb02)
        self.hbox.addWidget(self.breadcrumb03)
        self.hbox.addWidget(self.spacing)
        self.hbox.addWidget(self.file_info)
        self.hbox.addWidget(self.src_ctrl_info)
        self.hbox.addWidget(self.warnings_info)
        self.hbox.addWidget(self.errors_info)

        self.setFixedHeight(iconsts.BREADCRUMB_FIXED_HEIGHT)
        self.hbox.setContentsMargins(10, 2, 0, 0)

        if self.parent.content_type != "text":
            self.warnings_info.setVisible(False)
            self.errors_info.setVisible(False)


class FileMenu(QMenu):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.reload_file = QAction("Reload File", self)
        self.save_file = QAction("Save File", self)
        self.open_folder = QAction("Open Folder", self)

        self.addAction(self.reload_file)
        self.addAction(self.save_file)
        self.addAction(self.open_folder)


class SourceMenu(QMenu):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.add_file = QAction("Add This File", self)
        self.remove_file = QAction("Remove This File", self)

        self.addAction(self.add_file)
        self.addAction(self.remove_file)


class Div(QSplitter):

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("editor-splitter")
        self.setStyleSheet(
            "QSplitter::handle:horizontal {width: 0px;}QSplitter::handle:vertical {height: 0px;}"
        )
