from PyQt5.QtWidgets import QFrame, QPlainTextEdit, QPushButton, QVBoxLayout
from PyQt5.QtCore import Qt, QThread, QObject, QProcess

class Debug(QFrame):
    def __init__(self, parent) -> None:
        super().__init__()
        self.setObjectName("debug")
        
        self.btn = QPushButton("Execute")
        self.btn.pressed.connect(self.start_process)
        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.btn)
        self.layout.addWidget(self.output)
        self.setLayout(self.layout)
    
    def start_process(self):
        print("starting")
        