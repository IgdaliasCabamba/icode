from PyQt5.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import Qt, pyqtSignal
from .widgets import *


class Labs(QFrame):

    on_open_workspace = pyqtSignal(str)

    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("ilabs")
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)
        self.layout.setAlignment(Qt.AlignTop)

        self.top_info = QLabel("<small>LABS</small>")
        self.top_info.setWordWrap(True)
        self.header_layout = QHBoxLayout()
        self.header_layout.addWidget(self.top_info)
        self.layout.addLayout(self.header_layout)

    def new_work_space(self, title: str, name_id: str, desc: str, widget: object):
        card = CardLab(self, title, desc, name_id)
        card.add_widget(widget)
        self.layout.addWidget(card)
        self.layout.setAlignment(card, Qt.AlignTop)
        return card
