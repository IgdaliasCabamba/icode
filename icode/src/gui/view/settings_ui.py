from PyQt5.QtWidgets import QFrame, QVBoxLayout, QTreeWidget, QLabel, QSplitter
from functions import getfn
from .igui import IStandardItem, IGenericNotebook
from smartlibs.qtmd import QGithubButton


class CodeSettings(QFrame):

    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("settings-page")
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)


class ConfigUi(QFrame):

    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("settings")
        self.icons = getfn.get_smartcode_icons("config")
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        self.notebook = IGenericNotebook(self)
        self.notebook.addTab(QLabel("CODE"), "CODE")
        self.notebook.addTab(QLabel("EXTENSIONS"), "EXTENSIONS")
        self.notebook.addTab(QLabel("APPEARENCE"), "APPEARENCE")
        self.notebook.addTab(QLabel("USER"), "USER")

        self.layout.addWidget(self.notebook)
