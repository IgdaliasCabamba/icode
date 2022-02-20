from PyQt5.QtWidgets import (QFrame, QLabel, QPushButton, QSizePolicy,
                             QTextEdit, QVBoxLayout, QGraphicsDropShadowEffect)

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

from base.april_brain import *

from ui.chelly import GenericEditor
import pyperclip as pc
import textwrap
import commonmark
from functions import getfn

class CardLab(QFrame):
    def __init__(self, parent=None, title:str="Untitled", desc:str="", name_id:str=None):
        super().__init__(parent)
        self.setObjectName("card-lab")
        self.parent = parent
        self.title = title
        self.desc = str(desc)
        self.association = name_id
        self.init_ui()
    
    def init_ui(self):
        self.layout=QVBoxLayout(self)
        self.layout.setContentsMargins(5,5,5,5)
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
        self.drop_shadow.setColor(QColor(30,30,30))
        self.drop_shadow.setOffset(0, 0)
        self.setGraphicsEffect(self.drop_shadow)
        
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
    
    def add_widget(self, widget:object):
        self.content_layout.addWidget(widget)


class CardApril(QFrame):
    def __init__(self, parent, content:object, title:str, pos:int, type:str="text"):
        super().__init__(parent)
        self.icons = getfn.get_smartcode_icons("*")
        self.setObjectName("card-message")
        self.parent=parent
        self.content=content
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
            self.btn_copy.setIcon(self.icons.get_icon("copy"))
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
    def text(self) -> str:    
        return self.content

    @property
    def msg_size(self):
        min_height = 2
        if self.type == "code":
            min_height = 4
            
        text_height=len(self.text.splitlines())
        text_height = text_height if text_height >= min_height else min_height
        size = text_height*self.editor.font().pointSize()*2
        if size > 600:
            return 600
        return size
    
    def get_text_editor(self):
        if self.type == "text":
            content=QTextEdit()
            content.setObjectName("msg")
            content.setText(self.text)
            if self.pos == 0:
                marked_text=content.toHtml()
                content.setHtml(marked_text)
            else:
                marked_text=content.toMarkdown()
                content.setMarkdown(marked_text)
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
            content.setStyleSheet(f"""background:{editor.paper().name()}; border:none""")
        return content
