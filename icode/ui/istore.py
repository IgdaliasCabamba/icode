from PyQt5.QtWidgets import QListWidget, QFrame, QVBoxLayout, QHBoxLayout, QLineEdit, QLabel, QToolBox
from functions import getfn        
from .igui import InputHistory

class ExtensionsUi(QFrame):
    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.parent=parent
        self.setObjectName("extensions")
        self.icons = getfn.get_application_icons("extensions")
        self.init_ui()

    def init_ui(self) -> None:
        self.layout=QVBoxLayout(self)
        self.setLayout(self.layout)

        self.top_info=QLabel("<small>EXTENSIONS</small>")
        self.top_info.setWordWrap(True)
        self.header_layout = QHBoxLayout()
        self.header_layout.addWidget(self.top_info)
        
        self.toolbox = QToolBox(self)

        self.input_name = InputHistory(self)
        self.input_name.setPlaceholderText("Search for Extensions")

        self.installed=QListWidget(self)
        self.toolbox.addItem(self.installed, "INSTALLED")

        self.recommended = QListWidget(self)
        self.toolbox.addItem(self.recommended, "RECOMMENDED")

        self.layout.addLayout(self.header_layout)
        self.layout.addWidget(self.input_name)
        self.layout.addWidget(self.toolbox)
        

        self.toolbox.setItemIcon(0, self.icons.get_icon("installed"))
        self.toolbox.setItemIcon(1, self.icons.get_icon("recommended"))