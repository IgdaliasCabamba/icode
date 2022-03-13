from PyQt5.QtWidgets import QFrame, QPlainTextEdit, QPushButton, QVBoxLayout, QHBoxLayout, QLineEdit
from PyQt5.QtCore import Qt, QThread, QObject, QProcess

class Debug(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.env = None
        self.editor = None
        self.parent=parent        
        self.setObjectName("debug")
        self.process_debuger = QProcess(self)
        self.process_debuger.readyReadStandardOutput.connect(self.handle_stdout)
        self.process_debuger.readyReadStandardError.connect(self.handle_stderr)
        self.process_debuger.stateChanged.connect(self.handle_state)
        self.process_debuger.finished.connect(self.process_finished)

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
    
    def message(self, text):
        self.output.appendPlainText(text)
    
    def start(self, editor, code, file, interpreter):
        bin = interpreter.executable
        args = ["-m", "pdb", str(file)]
        self.start_process(bin, args)
        
    def start_process(self, bin, args):
        print("starting")
        self.process_debuger.start(bin, args)
    
    def handle_stderr(self):
        data = self.p.readAllStandardError()
        stderr = bytes(data).decode("utf8")
        self.message(stderr)
    
    def handle_stdout(self):
        data = self.process_debuger.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")
        self.message(stdout)
    
    def handle_state(self, state):
        states = {
            QProcess.NotRunning: 'Not running',
            QProcess.Starting: 'Starting',
            QProcess.Running: 'Running',
        }
        state_name = states[state]
        self.message(f"State changed: {state_name}")
    
    def process_finished(self):
        self.message("Process finished.")