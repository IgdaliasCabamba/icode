from PyQt5.QtWidgets import (
    QFrame, QListWidget, QVBoxLayout,
    QPushButton, QLabel,
    QTextEdit, QHBoxLayout, QListWidget, QStackedLayout, QFormLayout, QLineEdit
    )
    
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QObject
from pathlib import Path
from ..igui import ScrollLabel, IListWidgetItem

class NotesCore(QObject):
    def __init__(self, editor):
        super().__init__()
        self.parent = editor
        self.editor=editor.text_editor
    
    def run(self):
        self.editor.textChanged.connect(self.save_data)
    
    def save_data(self):
        self.parent.file.write_text(self.editor.toPlainText())

class Notes(QFrame):
    def __init__(self, parent, file):
        super().__init__()
        self.setObjectName("ilabs-notes")
        self.parent=parent
        self.file = Path(file)
        self.build()
    
    def build(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(2,2,2,2)
        self.setLayout(self.layout)
        
        self.title_input = QLineEdit(self)
        
        self.text_editor = QTextEdit(self)
        self.thread_text=QThread(self)
        self.text_object=NotesCore(self)
        self.text_object.moveToThread(self.thread_text)
        self.thread_text.started.connect(self.run_tasks)
        self.thread_text.start()
        
        self.text_editor.setAcceptRichText(True)
        self.text_editor.setPlaceholderText("Make your notes here, they are automatically saved")
        
        self.layout.addWidget(self.title_input)
        self.layout.addWidget(self.text_editor)
        
        if self.file.exists():
            self.text_editor.setText(self.file.read_text())
        else:
            file = open(self.file, "w")
            file.close()
    
    def run_tasks(self):
        self.text_object.run()

class Todos(QFrame):
    def __init__(self, parent):
        super().__init__()
        self.setObjectName("ilabs-notes")
        self.parent=parent
        self.parent.btn_add_label.clicked.connect(lambda: self.add_todo("MEU rabo", "YEE", 0))
        self.build()
    
    def build(self):
        self.layout = QStackedLayout(self)
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)
        
        self.form_layout = QFormLayout()
        self.screen_new = QFrame()
        self.screen_new.setLayout(self.form_layout)
        self.form_layout.addRow("Text:", QLineEdit())
        
        self.display=QListWidget(self)
        self.layout.addWidget(self.display)
        self.layout.addWidget(self.screen_new)
        
    def add_todo(self, text, tooltip, type):
        self.layout.setCurrentWidget(self.screen_new)
        #self.display.addItem(IListWidgetItem(None, text, tooltip))
        
        
class Produtivity(QFrame):
    pass