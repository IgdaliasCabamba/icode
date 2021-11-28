from PyQt5.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel,
    )
from PyQt5.QtCore import Qt
from pathlib import Path

from itertools import zip_longest 

from functions import getfn
from .igui import ScrollLabel, IListWidgetItem, DoctorStandardItem, IStandardItem
from .widgets import *

class Labs(QFrame):

    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("ilabs")
        self.parent=parent
        self.init_ui()
    
    def init_ui(self):
        self.layout=QVBoxLayout(self)
        self.setLayout(self.layout)
        self.layout.setAlignment(Qt.AlignTop)

        self.top_info=QLabel("<small>LABS</small>")
        self.top_info.setWordWrap(True)
        self.header_layout = QHBoxLayout()
        self.header_layout.addWidget(self.top_info)

        self.btn_notes=QPushButton("Show Notes", self)
        self.btn_notes.setObjectName("btn-get-notes")
        self.btn_warnings=QPushButton("Get Warnings", self)
        self.btn_warnings.setObjectName("btn-get-warnings")
        self.btn_tree=QPushButton("Get Tree", self)
        self.btn_tree.setObjectName("btn-get-tree")
        self.btn_analizys=QPushButton("Get Code Analitics", self)
        self.btn_analizys.setObjectName("btn-get-code-analitics")

        self.layout.addLayout(self.header_layout)
        self.layout.addWidget(self.btn_notes)
        self.layout.addWidget(self.btn_tree)
        self.layout.addWidget(self.btn_warnings)
        self.layout.addWidget(self.btn_analizys)