from PyQt5.QtWidgets import QFrame, QLabel, QVBoxLayout, QScrollArea, QGraphicsDropShadowEffect, QScrollArea, QGridLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

class WorkSpace(QFrame):
    def __init__(self, space_id:str, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.space_id = space_id
        self.init_ui()
    
    def init_ui(self):
        self.layout = QGridLayout(self)
        self.setLayout(self.layout)
    
    def add_table(self, table:object, row:int, col:int, until_row:int=None, until_col:int=None):
        if until_col is not None and until_row is not None:
            self.layout.addWidget(table, row, col, until_row, until_col)
        else:
            self.layout.addWidget(table, row, col)

class Table(QFrame):
    def __init__(self, parent=None, title:str="Untitled"):
        super().__init__(parent)
        self.parent = parent
        self.title = title
        self.init_ui()
    
    def init_ui(self):
        self.layout=QVBoxLayout(self)
        self.layout.setContentsMargins(5,5,5,5)
        self.setLayout(self.layout)
        
        self.table_label = QLabel(self)
        self.table_label.setText(f"<h4>{self.title}</h4>")
        
        self.scroll=QScrollArea(self)
        self.scroll.setObjectName("main-area")
        
        self.content = QFrame(self)
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(5,5,5,5)
        self.content.setLayout(self.content_layout)

        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.content)
        
        self.layout.addWidget(self.table_label)
        self.layout.addWidget(self.scroll)
        
        self.setStyleSheet("QFrame{background:#333; border-radius:5px}")
        
        self.drop_shadow = QGraphicsDropShadowEffect(self)
        self.drop_shadow.setBlurRadius(10)
        self.drop_shadow.setColor(QColor(30,30,30))
        self.drop_shadow.setOffset(0, 0)
        self.setGraphicsEffect(self.drop_shadow)
    
    def add_widget(self, widget:object):
        self.content_layout.addWidget(widget)