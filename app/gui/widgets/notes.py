from PyQt5.QtWidgets import (
    QFrame, QListWidget, QVBoxLayout,
    QPushButton, QLabel,
    QTextEdit, QHBoxLayout
    )
    
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QObject
from pathlib import Path

class NotesCore(QObject):
    def __init__(self, editor):
        super().__init__()
        self.editor=editor
    
    def run(self):
        self.editor.textChanged.connect(self.save_data)
    
    def save_data(self):
        self.editor.file.write_text(self.editor.toPlainText())

class Notes(QTextEdit):
    def __init__(self, parent, file):
        super().__init__()
        self.setObjectName("ilabs-notes")
        self.parent=parent
        self.file = Path(file)
        self.build()
    
    def build(self):
        self.thread_text=QThread(self)
        self.text_object=NotesCore(self)
        self.text_object.moveToThread(self.thread_text)
        self.thread_text.started.connect(self.run_tasks)
        self.thread_text.start()

        self.setAcceptRichText(True)
        self.setPlaceholderText("Make your notes here, they are automatically saved")
        
        if self.file.exists():
            self.setText(self.file.read_text())
        else:
            file = open(self.file, "w")
            file.close()
    
    def run_tasks(self):
        self.text_object.run()