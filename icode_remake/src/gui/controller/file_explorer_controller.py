from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QFileDialog
import pathlib


class FileExplorerController(QObject):

    on_path_changed = pyqtSignal(str)
    on_file_clicked = pyqtSignal(str)
    on_open_folder_request = pyqtSignal()

    def __init__(self, application_core, view):
        super().__init__()
        self.application_core = application_core
        self.view = view

        self._folder = None
        self.is_expanded = False

        self.view.tree.clicked.connect(self.on_tree_clicked)
        self.view.btn_open_dir.clicked.connect(
            lambda: self.on_open_folder_request.emit()
        )
        self.view.btn_open_folder.clicked.connect(
            lambda: self.on_open_folder_request.emit()
        )
        self.view.btn_expand_collapse.clicked.connect(self.expand_collapse)

    @property
    def folder(self):
        return self._folder

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
        self.view.tree.setRootIndex(self.model.index(self._folder))
        self.view.btn_open_folder.setVisible(True)
        self.view.btn_close_folder.setVisible(True)
        self.view.btn_expand_collapse.setVisible(True)
        self.view.btn_open_dir.setVisible(False)
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

    def on_tree_clicked(self, index):
        self.on_file_clicked.emit(self.view.model.filePath(index))

    def expand_collapse(self):
        if self.is_expanded:
            self.collapse()
        else:
            self.expand()

    def expand(self):
        p = pathlib.Path(self.view.model.rootPath())

        subdirs = [f for f in p.iterdir() if f.is_dir()]
        for directory in subdirs:
            item = self.view.model.index(directory.name, 0)
            if directory.name not in {".git"} and not directory.name.startswith("."):
                self.view.tree.expand(item)
        self.is_expanded = True
        self.view.btn_expand_collapse.setIcon(self.icons.get_icon("collapse"))

    def collapse(self):
        p = pathlib.Path(self.view.model.rootPath())

        subdirs = [f for f in p.iterdir() if f.is_dir()]
        for directory in subdirs:
            item = self.view.model.index(directory.name, 0)
            self.view.tree.collapse(item)
        self.is_expanded = False
        self.view.btn_expand_collapse.setIcon(self.icons.get_icon("expand"))

    def select_first(self):
        p = pathlib.Path(self.model.rootPath())
        ls = [f for f in p.iterdir()]
        if ls:
            self.view.tree.setCurrentIndex(self.model.index(ls[0].name, 0))
