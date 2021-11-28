from PyQt5.QtCore import QObject, pyqtSignal, Qt, QSize
from PyQt5.QtWidgets import (
    QFrame, QGridLayout,
    QHBoxLayout, QListWidget,
    QPushButton, QSizePolicy,
    QVBoxLayout, QGraphicsDropShadowEffect,
    QLabel
)
from ..igui import InputHistory
from PyQt5.QtGui import QColor

from functions import getfn

class CloneRepo(QFrame):
    
    focus_out = pyqtSignal(object, object)
    
    def __init__(self, api, parent):
        super().__init__(parent)
        self.api = api
        self._parent = parent
        self.setParent(parent)
        self.setObjectName("editor-widget")
        self.init_ui()
    
    def init_ui(self):

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(self.layout)

        self.input_url = InputHistory(self)
        self.size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.input_url.setSizePolicy(self.size_policy)
        self.input_url.setPlaceholderText("Url to repository")
        self.input_url.setObjectName("child")
        
        self.layout.addWidget(self.input_url)
        
    def run(self):
        self.input_url.setFocus()
        self.setFixedHeight(35)