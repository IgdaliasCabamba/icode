import pyperclip as pc
from functions import getfn
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (QFrame, QGraphicsDropShadowEffect, QHBoxLayout,
                             QLabel, QPushButton, QScrollArea, QSizePolicy,
                             QTextEdit, QVBoxLayout)

from base.april_brain import *
from .igui import Animator, InputHistory
from .widgets import CardApril

class AprilFace(QFrame):
    
    on_asked=pyqtSignal(str)

    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("april-ui")
        self.parent=parent
        self.icons = getfn.get_smartcode_icons("assistant")
        self._work_count = 0
        
        self.thread=QThread()
        self.brain=Brain(self)
        self.brain.moveToThread(self.thread)
        self.thread.start()
        self.thread.started.connect(self.run)

        self.brain.on_answered.connect(self.display_result)
        self.init_ui()
    
    def init_ui(self):
        self.layout=QVBoxLayout(self)
        self.setLayout(self.layout)

        self.scroll=QScrollArea(self)
        self.scroll.setObjectName("main-area")
        
        self.widget = QFrame(self)
        self.widget.setObjectName("main-frame")
        self.vbox = QVBoxLayout(self.widget)
        self.widget.setLayout(self.vbox)

        self.hello_msg=CardApril(self, hello_msg, "April", 0)
        self.hello_msg.set_read_only(True)

        self.vbox.addWidget(self.hello_msg)

        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.widget)

        self.input = InputHistory(self)
        self.input.setPlaceholderText("...")
        self.input.setEnabled(False)
        self.input.returnPressed.connect(self.search_answer)

        self.top_info=QLabel("<small>APRIL</small>")
        self.top_info.setWordWrap(True)
        self.animation = Animator(self, self.icons.get_path("loading"))
        self.animation.setMaximumHeight(16)
        self.animation.set_scaled_size(64, 16)
        self.animation.stop(False)
        
        self.header_layout = QHBoxLayout()
        self.header_layout.addWidget(self.top_info)
        self.header_layout.addWidget(self.animation)
        self.header_layout.setAlignment(self.animation, Qt.AlignLeft)

        self.layout.addLayout(self.header_layout)
        self.layout.addWidget(self.scroll)
        self.layout.addWidget(self.input)
    
    def run(self):
        self.input.setEnabled(True)
        self.brain.run()
    
    def search_answer(self):
        text=self.input.text()

        self.vbox.addWidget(CardApril(self, text, "Me" ,1))
        self.on_asked.emit(text)
        self._work_count += 1
        self.animation.play(True)
        
        return 
    
    def display_result(self, res:str, type:int):
        res=res
        if type in {0,1}:
            type = "text"
        elif type == 2:
            type = "code"
            
        self.vbox.addWidget(CardApril(self, res, "April", 0, type))
        self._work_count -= 1
        if self._work_count < 1:
            self.animation.stop(False)
