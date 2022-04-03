from PyQt5.QtWidgets import (
    QFrame,
    QListWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QLineEdit,
    QFormLayout,
    QListWidget,
    QHBoxLayout,
)

from PyQt5.QtCore import Qt, pyqtSignal, QThread, QObject
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from pathlib import Path
from functions import getfn
from ui.igui import ScrollLabel, IListWidgetItem, InputHistory


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
