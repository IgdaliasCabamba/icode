from PyQt5.QtWidgets import QFrame, QPlainTextEdit, QPushButton, QVBoxLayout, QHBoxLayout, QLineEdit
from PyQt5.QtCore import Qt, QThread, QObject, QProcess

class Debug(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent=parent        
        self.setObjectName("debug")

        self.hbox = QHBoxLayout()
        self.btn_next_line = QPushButton("Next")
        self.btn_prev_line = QPushButton("Previous")
        self.btn_jump_to = QPushButton("Jump")
        self.input_line = QLineEdit(self)
        self.input_line.setPlaceholderText("type line")
        self.hbox.addWidget(self.btn_next_line)
        self.hbox.addWidget(self.btn_prev_line)
        self.hbox.addWidget(self.btn_jump_to)
        self.hbox.addWidget(self.input_line)
        
        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)

        self.layout = QVBoxLayout()
        self.layout.addLayout(self.hbox)
        self.layout.addWidget(self.output)
        self.setLayout(self.layout)
    
    def start_process(self):
        print("starting")
        