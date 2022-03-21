import pyperclip as pc
from functions import getfn
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (QFrame, QGraphicsDropShadowEffect, QHBoxLayout,
                             QLabel, QPushButton, QScrollArea, QSizePolicy,
                             QTextEdit, QVBoxLayout, QMenu, QAction, QActionGroup)

from base.april_brain import *
from .igui import Animator, InputHistory, HeaderPushButton
from .widgets import CardApril
from base.char_utils import get_unicon

class AssistantMenu(QMenu):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        
        group_mode = QActionGroup(self)
        
        self.show_all = QAction("All Response", self)
        self.show_all.setCheckable(True)
        self.addAction(self.show_all)
        
        self.answer_number = QMenu("Number of Answers", self)
        self.addMenu(self.answer_number)
        
        self.less_answers = QAction("1", self)
        self.less_answers.setCheckable(True)
        self.less_answers.setChecked(True)
        self.less_answers.triggered.connect(lambda: self.configure_ans_count(1))
        self.answer_number.addAction(self.less_answers)
        
        self.two_answers = QAction("2", self)
        self.two_answers.setCheckable(True)
        self.two_answers.triggered.connect(lambda: self.configure_ans_count(2))
        self.answer_number.addAction(self.two_answers)
        
        self.normal_answers = QAction("3", self)
        self.normal_answers.setCheckable(True)
        self.normal_answers.triggered.connect(lambda: self.configure_ans_count(3))
        self.answer_number.addAction(self.normal_answers)
        
        self.all_answers = QAction("All", self)
        self.all_answers.setCheckable(True)
        self.all_answers.triggered.connect(lambda: self.configure_ans_count(20))
        self.answer_number.addAction(self.all_answers)
        
        group_mode.addAction(self.less_answers)
        group_mode.addAction(self.two_answers)
        group_mode.addAction(self.normal_answers)
        group_mode.addAction(self.all_answers)
    
    def configure_ans_count(self, val):
        self.parent.settings["answer_count"] = val
    
    def configure_res_type(self, val):
        self.parent.settings["all_response"] = val

class AprilFace(QFrame):
    
    on_asked=pyqtSignal(str, dict)

    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("april-ui")
        self.parent=parent
        self.icons = getfn.get_smartcode_icons("assistant")
        self._work_count = 0
        self.options = AssistantMenu(self)
        self.template = AprilRender()
        self.settings = {
            "all_response":False,
            "answer_count":1
        }
        
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

        self.hello_msg=CardApril(
            self,
            self.template.readme,
            "April "+get_unicon("nf", "mdi-message"),
            0
        )
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
        self.btn_options = HeaderPushButton()
        self.btn_options.setMenu(self.options)
        self.btn_options.setObjectName("assistant-header-button")
        self.btn_options.setIcon(self.icons.get_icon("options"))
        self.btn_options.clicked.connect(lambda: self.btn_options.showMenu())
        
        self.header_layout = QHBoxLayout()
        self.header_layout.addWidget(self.top_info)
        self.header_layout.addWidget(self.animation)
        self.header_layout.addWidget(self.btn_options)
        self.header_layout.setAlignment(self.animation, Qt.AlignLeft)

        self.layout.addLayout(self.header_layout)
        self.layout.addWidget(self.scroll)
        self.layout.addWidget(self.input)
    
    def run(self):
        self.input.setEnabled(True)
        self.brain.run()
    
    def search_answer(self):
        text=self.input.text()

        self.vbox.addWidget(CardApril(self, text, "Me \uf866" ,1))
        self.on_asked.emit(text, self.settings)
        self._work_count += 1
        self.animation.play(True)
        
        return 
    
    def display_result(self, res:str, type:int):
        res=res
        if type in {0,1}:
            self.vbox.addWidget(CardApril(self, res, "April \uf860", 0, "text"))
        elif type == 2:
            for ans in res:
                if isinstance(ans, dict):
                    if "answer" in ans.keys():
                        if ans["answer"] is not None:
                            self.vbox.addWidget(CardApril(self, ans["answer"], "April \uf860", 0, "code"))
        elif type == -1:
            self.vbox.addWidget(CardApril(self, res, "April \uf860", 0, "text"))
                
        self._work_count -= 1
        if self._work_count < 1:
            self.animation.stop(False)