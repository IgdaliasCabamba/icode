from PyQt5.QtWidgets import (
    QFrame,
    QLabel,
    QPushButton,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QGraphicsDropShadowEffect,
)

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

import pyperclip
import textwrap
import commonmark
from functions import getfn


class CardLab(QFrame):

    def __init__(self,
                 parent=None,
                 title: str = "Untitled",
                 desc: str = "",
                 name_id: str = None):
        super().__init__(parent)
        self.setObjectName("card-lab")
        self.parent = parent
        self.title = title
        self.desc = str(desc)
        self.association = name_id
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(self.layout)

        self.table_label = QLabel(self)
        self.table_label.setText(f"<h4>{self.title}</h4>")

        self.desc_label = QLabel(self)
        self.desc_label.setText(self.desc)

        self.content = QFrame(self)
        self.content_layout = QVBoxLayout(self.content)
        self.content.setLayout(self.content_layout)

        self.layout.addWidget(self.table_label)
        self.layout.addWidget(self.desc_label)
        self.layout.addWidget(self.content)

        self.drop_shadow = QGraphicsDropShadowEffect(self)
        self.drop_shadow.setBlurRadius(12)
        self.drop_shadow.setColor(QColor(30, 30, 30))
        self.drop_shadow.setOffset(0, 0)
        self.setGraphicsEffect(self.drop_shadow)

        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)

    def add_widget(self, widget: object):
        self.content_layout.addWidget(widget)
