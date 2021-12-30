from PyQt5.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QScrollArea,
    QGraphicsDropShadowEffect, QSizePolicy
    )
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor
from pathlib import Path

from functions import getfn
from .igui import ScrollLabel, IListWidgetItem, DoctorStandardItem, IStandardItem
from .widgets import *

class CardLab(QFrame):
    def __init__(self, parent=None, title:str="Untitled", name_id:str=None):
        super().__init__(parent)
        self.setObjectName("card-lab")
        self.parent = parent
        self.title = title
        self.association = name_id
        self.init_ui()
    
    def init_ui(self):
        self.layout=QVBoxLayout(self)
        self.layout.setContentsMargins(5,5,5,5)
        self.setLayout(self.layout)
        
        self.table_label = QLabel(self)
        self.table_label.setText(f"<h4>{self.title}</h4>")
        
        self.content = QFrame(self)
        self.content_layout = QVBoxLayout(self.content)
        self.content.setLayout(self.content_layout)
        
        self.layout.addWidget(self.table_label)
        self.layout.addWidget(self.content)
        
        self.drop_shadow = QGraphicsDropShadowEffect(self)
        self.drop_shadow.setBlurRadius(12)
        self.drop_shadow.setColor(QColor(30,30,30))
        self.drop_shadow.setOffset(0, 0)
        self.setGraphicsEffect(self.drop_shadow)
        
        self.setStyleSheet("QFrame{background:#333; border-radius:5px}")
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        self.setMaximumWidth(400)
    
    def add_widget(self, widget:object):
        self.content_layout.addWidget(widget)

class Labs(QFrame):
    
    on_open_workspace = pyqtSignal(str)

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
        self.layout.addLayout(self.header_layout)
        
        self.btn_notes=QPushButton("Open", self)
        self.btn_notes.setObjectName("btn-get-notes")
        self.btn_notes.clicked.connect(lambda: self.on_open_workspace.emit("inotes"))
        self.new_work_space("Notes and Tasks", "inotes", self.btn_notes)
    
    def new_work_space(self, title:str, name_id:str, widget:object):
        card = CardLab(self, title, name_id)
        card.add_widget(widget)
        self.layout.addWidget(card)
        self.layout.setAlignment(card, Qt.AlignTop)
        return card