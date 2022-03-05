from PyQt5.QtWidgets import QFrame, QVBoxLayout, QTreeWidget
from functions import getfn
from .igui import IStandardItem, QGithubButton

class ConfigUi(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.icons = getfn.get_smartcode_icons("config")
        self.parent = parent
        self.init_ui()
    
    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)