from typing import Union
from PyQt5.QtCore import pyqtSignal, Qt, QTimer, QPropertyAnimation, QPoint, QEasingCurve
from PyQt5.QtWidgets import (QButtonGroup, QFrame, QGraphicsDropShadowEffect,
                             QLabel, QRadioButton, QTabWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QSizePolicy)
                             
class Notification(QFrame):
    
    on_displayed = pyqtSignal(object)
    
    def __init__(self, parent, title, desc, widgets, time:Union[int, float]):
        super().__init__(parent)
        self.setObjectName("Notification")
        self.parent = parent
        self.title = title
        self.desc = desc
        self.widgets = widgets
        self.timer = QTimer(self)
        self.timer.singleShot(time, lambda:self.on_displayed.emit(self))
        self.init_ui()
    
    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)
        self.setMinimumHeight(90)
        
        self.lbl_title = QLabel(f"<h4>{self.title}</h4>")
        self.lbl_title.setWordWrap(True)
        self.lbl_desc = QLabel(self.desc)
        self.lbl_desc.setWordWrap(True)
        
        self.hbox = QHBoxLayout()
        
        for i in self.widgets:
            self.hbox.addWidget(i)
        
        self.layout.addWidget(self.lbl_title)
        self.layout.addWidget(self.lbl_desc)
        self.layout.addLayout(self.hbox)
        
        self.setVisible(True)
    
    def clear(self):
        self.timer.stop()
        self.close()