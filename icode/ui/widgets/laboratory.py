from PyQt5.QtWidgets import QFrame, QLabel, QVBoxLayout, QScrollArea, QGraphicsDropShadowEffect, QScrollArea, QGridLayout, QHBoxLayout, QSizePolicy
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

class Table(QFrame):
    def __init__(self, parent=None, title:str="Untitled"):
        super().__init__(parent)
        self.setObjectName("research-table")
        self.parent = parent
        self.title = title
        self.init_ui()
    
    def init_ui(self):
        self.layout=QVBoxLayout(self)
        self.layout.setContentsMargins(2,2,2,2)
        self.setLayout(self.layout)
        
        self.header_layout = QHBoxLayout()
        self.header_layout.setContentsMargins(5,5,5,0)
        
        self.table_label = QLabel(self)
        self.table_label.setText(f"<h4>{self.title}</h4>")
        self.header_layout.addWidget(self.table_label)
        
        self.scroll=QScrollArea(self)
        self.scroll.setObjectName("scroll-area")
        
        self.content = QFrame(self)
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(2,2,2,2)
        self.content.setLayout(self.content_layout)

        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.content)
        
        self.layout.addLayout(self.header_layout)
        self.layout.addWidget(self.scroll)
        
        self.setStyleSheet("QFrame{background:#333; border-radius:5px}")
        
        self.drop_shadow = QGraphicsDropShadowEffect(self)
        self.drop_shadow.setBlurRadius(10)
        self.drop_shadow.setColor(QColor(30,30,30))
        self.drop_shadow.setOffset(0, 0)
        self.setGraphicsEffect(self.drop_shadow)
    
    def add_widget(self, widget:object):
        self.content_layout.addWidget(widget)
    
    def add_header_widget(self, widget:object):
        self.header_layout.addWidget(widget)

class WorkSpace(QFrame):
    def __init__(self, space_id:str, parent=None):
        super().__init__(parent)
        self.setObjectName("research-space")
        self.parent = parent
        self.space_id = space_id
        self.init_ui()
    
    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)
        
        self.scroll=QScrollArea(self)
        self.scroll.setObjectName("scroll-area")
        
        self.spaces_content = QFrame(self)
        self.tables_manager = QGridLayout()
        self.tables_manager.setContentsMargins(5,5,5,5)
        self.spaces_content.setLayout(self.tables_manager)
        
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.spaces_content)
        
        self.layout.addWidget(self.scroll)
    
    def add_table(self, table:object, row:int, col:int, until_row:int=None, until_col:int=None):
        if until_col is not None and until_row is not None:
            self.tables_manager.addWidget(table, row, col, until_row, until_col)
        else:
            self.tables_manager.addWidget(table, row, col)