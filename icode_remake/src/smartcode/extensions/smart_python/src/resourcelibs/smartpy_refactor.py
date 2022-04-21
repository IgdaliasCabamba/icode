from PyQt5.QtWidgets import (
    QFrame,
    QFormLayout,
)

from functions import getfn
from smartlibs.qtmd import InputHistory


class Refactor(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("refactor")
        self.init_ui()

    def init_ui(self):
        self.layout = QFormLayout(self)
        self.setLayout(self.layout)

        self.input_find = InputHistory(self)
        self.input_replace = InputHistory(self)

        self.layout.addRow("Find: ", self.input_find)
        self.layout.addRow("Replace: ", self.input_replace)
