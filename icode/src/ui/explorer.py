import pathlib

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QFileDialog,
    QFileSystemModel,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTreeView,
    QVBoxLayout,
    QAbstractItemView,
)

from functions import filefn, getfn

from .igui import HeaderPushButton


class FileExplorer(QFrame):

    on_path_changed = pyqtSignal(str)
    on_file_clicked = pyqtSignal(str)
    on_open_folder_request = pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self._folder = None
        self.is_expanded = False
        self.icons = getfn.get_smartcode_icons("explorer")
        self.init_ui()

    @property
    def folder(self):
        return self._folder

    def init_ui(self):

        self.model = QFileSystemModel(self)
        self.model.setRootPath("")
        self.tree = QTreeView(self)
        self.tree.clicked.connect(self.on_tree_clicked)
        self.tree.setModel(self.model)
        self.tree.header().hide()

        self.tree.setAnimated(True)
        self.tree.setIndentation(20)
        self.tree.setSortingEnabled(False)
        self.tree.setAcceptDrops(True)
        self.tree.setColumnHidden(1, True)
        self.tree.setColumnHidden(2, True)
        self.tree.setColumnHidden(3, True)

        self.btn_open_dir = QPushButton("Open Folder")
        self.btn_open_dir.clicked.connect(lambda: self.on_open_folder_request.emit())
        self.btn_open_dir.setIcon(self.icons.get_icon("open"))
        self.hbox_layout = QHBoxLayout()
        self.hbox_layout.addWidget(self.btn_open_dir)

        self.top_info = QLabel("<small>EXPLORER</small>", self)
        self.top_info.setWordWrap(True)

        self.btn_close_folder = HeaderPushButton(self)
        self.btn_close_folder.setObjectName("explorer-header-button")
        self.btn_close_folder.setIcon(self.icons.get_icon("close"))
        self.btn_close_folder.setVisible(False)

        self.btn_open_folder = HeaderPushButton(self)
        self.btn_open_folder.clicked.connect(lambda: self.on_open_folder_request.emit())
        self.btn_open_folder.setObjectName("explorer-header-button")
        self.btn_open_folder.setIcon(self.icons.get_icon("open"))
        self.btn_open_folder.setVisible(False)

        self.btn_expand_collapse = HeaderPushButton(self)
        self.btn_expand_collapse.clicked.connect(self.expand_collapse)
        self.btn_expand_collapse.setObjectName("explorer-header-button")
        self.btn_expand_collapse.setVisible(False)

        self.header_layout = QHBoxLayout()
        self.header_layout.addWidget(self.top_info)
        self.header_layout.addWidget(self.btn_expand_collapse)
        self.header_layout.addWidget(self.btn_open_folder)
        self.header_layout.addWidget(self.btn_close_folder)

        self.layout = QVBoxLayout(self)
        self.layout.addLayout(self.header_layout)
        self.layout.addLayout(self.hbox_layout)
        self.layout.addWidget(self.tree)
        self.setLayout(self.layout)

    def on_tree_clicked(self, index):
        self.on_file_clicked.emit(self.model.filePath(index))

    def _set_folder(self, path=None):
        if path is None:

            home_dir = self._folder

            if self._folder is None:
                home_dir = str(pathlib.Path.home())

            path = QFileDialog.getExistingDirectory(
                None, "Open Folder", home_dir, QFileDialog.ShowDirsOnly
            )
            if path == "":
                return None

        self._folder = path
        self.tree.setRootIndex(self.model.index(self._folder))
        self.btn_open_folder.setVisible(True)
        self.btn_close_folder.setVisible(True)
        self.btn_expand_collapse.setVisible(True)
        self.btn_open_dir.setVisible(False)
        self.expand()
        self.select_first()

    def open_folder(self, path=None):
        self._set_folder(path)
        self.on_path_changed.emit(self._folder)
        return self._folder

    def goto_folder(self, path) -> None:
        if path is not None and pathlib.Path(path).exists:
            self._set_folder(path)
            return self.folder

    def close_folder(self):
        self.tree.setRootIndex(self.model.index(""))
        self.tree.header().hide()
        self.btn_close_folder.setVisible(False)
        self.btn_open_folder.setVisible(False)
        self.btn_expand_collapse.setVisible(False)
        self.btn_open_dir.setVisible(True)
        self._folder = None

    def expand_collapse(self):
        if self.is_expanded:
            self.collapse()
        else:
            self.expand()

    def expand(self):
        p = pathlib.Path(self.model.rootPath())

        subdirs = [f for f in p.iterdir() if f.is_dir()]
        for directory in subdirs:
            item = self.model.index(directory.name, 0)
            if directory.name not in {".git"} and not directory.name.startswith("."):
                self.tree.expand(item)
        self.is_expanded = True
        self.btn_expand_collapse.setIcon(self.icons.get_icon("collapse"))

    def collapse(self):
        p = pathlib.Path(self.model.rootPath())

        subdirs = [f for f in p.iterdir() if f.is_dir()]
        for directory in subdirs:
            item = self.model.index(directory.name, 0)
            self.tree.collapse(item)
        self.is_expanded = False
        self.btn_expand_collapse.setIcon(self.icons.get_icon("expand"))

    def select_first(self):
        p = pathlib.Path(self.model.rootPath())
        ls = [f for f in p.iterdir()]
        if ls:
            self.tree.setCurrentIndex(self.model.index(ls[0].name, 0))
