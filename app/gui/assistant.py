from PyQt5.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QScrollArea, QLabel, QTextEdit, QGraphicsDropShadowEffect, QSizePolicy
from PyQt5.QtCore import Qt, pyqtSignal, QThread
from PyQt5.QtGui import QColor
import pyperclip as pc
from functions import getfn

from .igui import InputHistory, Animator
from components.april_brain import *
from gui.generic_editor import GenericEditor
    
class Card(QFrame):
    def __init__(self, parent, text:str, title:str, pos:int, type:str="text"):
        super().__init__(parent)
        self.setObjectName("card-message")
        self.parent=parent
        self.text=text
        self.title=title
        self.type = type
        self.pos=pos
        self.init_ui()
    
    def init_ui(self):
        self.layout=QVBoxLayout(self)
        self.setLayout(self.layout)
        
        self.lbl_title=QLabel(self)
        self.layout.addWidget(self.lbl_title)
        self.lbl_title.setText(f"<h4>{self.title}</h4>")
        
        self.editor = self.get_text_editor()
        self.editor.setMinimumHeight(self.msg_size)
        self.layout.addWidget(self.editor)

        self.drop_shadow = QGraphicsDropShadowEffect(self.editor)
        self.drop_shadow.setBlurRadius(10)
        self.drop_shadow.setColor(QColor(30,30,30))

        if self.pos==0:
            self.btn_copy = QPushButton("Copy", self)
            self.btn_copy.setObjectName("btn-copy")
            self.btn_copy.clicked.connect(self.copy_to_clipboard)
            self.btn_copy.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

            self.layout.setAlignment(self.lbl_title, Qt.AlignLeft) 
            self.layout.setAlignment(self.editor, Qt.AlignLeft) 
            self.layout.addWidget(self.btn_copy, Qt.AlignLeft)
            self.drop_shadow.setOffset(-4, -4)
        else:
            self.layout.setAlignment(self.lbl_title, Qt.AlignRight)
            self.layout.setAlignment(self.editor, Qt.AlignRight)    
            self.drop_shadow.setOffset(4, 4)
            self.set_read_only(True)
    
        self.editor.setGraphicsEffect(self.drop_shadow)
    
    def set_read_only(self, arg):
        self.editor.setReadOnly(arg)
    
    def copy_to_clipboard(self):
        wrapper = textwrap.TextWrapper(width=80)
        value= wrapper.fill(text=self.text)

        pc.copy(value)

    @property
    def msg_size(self):
        text_height=len(self.text.splitlines())
        text_height = text_height if text_height >= 2 else 2
        size = text_height*self.editor.font().pointSize()*2
        return size
    
    def get_text_editor(self):
        if self.type == "text":
            content=QTextEdit()
            content.setObjectName("msg")
            content.setText(self.text)
            markdown=content.toMarkdown()
            content.setMarkdown(markdown)
            content.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        elif self.type == "code":
            content = QFrame()
            content.setObjectName("msg")
            vbox = QVBoxLayout()
            vbox.setContentsMargins(5,5,5,5)
            content.setLayout(vbox)
            
            lexer = getfn.get_lexer_from_code(self.text)
            editor = GenericEditor()
            editor.setText(self.text)
            if lexer is not None:
                lexer = lexer()
                editor.set_lexer(lexer)
            
            vbox.addWidget(editor)
            
        return content
        

class AprilFace(QFrame):
    
    on_asked=pyqtSignal(str)

    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("april-ui")
        self.parent=parent
        self.icons = getfn.get_application_icons("assistant")
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

        self.hello_msg=Card(self, hello_msg, "April", 0)
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

        self.vbox.addWidget(Card(self, text, "Me" ,1))
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
            
        self.vbox.addWidget(Card(self, res, "April", 0, type))
        self._work_count -= 1
        if self._work_count < 1:
            self.animation.stop(False)