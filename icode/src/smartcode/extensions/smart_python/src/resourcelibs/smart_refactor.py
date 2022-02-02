from PyQt5.QtWidgets import (
    QFrame, QListWidget, QVBoxLayout,
    QPushButton, QLabel,
    QTextEdit, QTreeView,
    QListWidget, QHBoxLayout
    )
    
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QObject
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from pathlib import Path
from functions import getfn
from ui.igui import ScrollLabel, IListWidgetItem, DoctorStandardItem, IStandardItem

class Refactor(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("refactor")
        self.init_ui()
    
    def init_ui(self):
        pass
