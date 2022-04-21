from PyQt5.QtWidgets import (
    QFileSystemModel,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTreeView,
    QVBoxLayout,
)

from functions import getfn
from smartlibs.qtmd import HeaderPushButton


class FileExplorerUi(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.icons = getfn.get_smartcode_icons("explorer")
        self.init_ui()

    def init_ui(self):
        self.model = QFileSystemModel(self)
        self.model.setRootPath("")
        self.tree = QTreeView(self)
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
        self.btn_open_folder.setObjectName("explorer-header-button")
        self.btn_open_folder.setIcon(self.icons.get_icon("open"))
        self.btn_open_folder.setVisible(False)

        self.btn_expand_collapse = HeaderPushButton(self)
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

    def close_folder(self):
        self.tree.setRootIndex(self.model.index(""))
        self.tree.header().hide()
        self.btn_close_folder.setVisible(False)
        self.btn_open_folder.setVisible(False)
        self.btn_expand_collapse.setVisible(False)
        self.btn_open_dir.setVisible(True)
        self._folder = None
